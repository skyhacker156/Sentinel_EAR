"""SL-PT-001 Stage A keyless, read-only market-data client (Strike 4).

Governing text: frozen R4.2i §2.2 (allowlisted host, no credential, no submit path), §2.3 Branch C (client-level only),
§4.2 (pinned requests), §4.3 D-8 (artifacts), §5.6 (t_send, t_recv); TER-1 contract v2.1 CC-05 (URLs).

- Only GET to https://data.alpaca.markets on the two pinned paths. Any other host, path or method is refused BEFORE any
  network I/O (§2.2). No authentication header is ever sent; the client has no credential parameter.
- http.client: no proxy lookup, no redirect following, chunked framing removed, no decompression. Accept-Encoding:
  identity is sent; a non-identity Content-Encoding fails V1 downstream (D-8).
- t_send: wall clock immediately before sending; t_recv: wall clock at receipt of the response headers (§5.6).
- Any transport failure = NO_RESPONSE (header and body None). One request each; never a further page (D-1).
Limitation carried by every Stage A result (§2.3, verbatim): "Disconnection from trading is asserted at the HTTP-client
level only. Alternate egress paths in the process or host (other libraries, raw sockets, proxies, inherited handles)
were not excluded."
"""
import http.client
import ssl
import time

from . import exact as X
from . import validate as V

HOST = "data.alpaca.markets"
BARS_PATH = "/v1beta3/crypto/us/bars"
QUOTE_PATH = "/v1beta3/crypto/us/latest/quotes"
PATHS = (BARS_PATH, QUOTE_PATH)
TIMEOUT_S = 10


class RefusedRequest(Exception):
    """A request outside the allowlist or the pinned paths; raised before any network I/O."""


def utc_seconds(ns):
    """CC-05: YYYY-MM-DDTHH:MM:SSZ, UTC whole seconds. Refuses a non-whole-second instant."""
    if ns % X.NS:
        raise ValueError("request instants are whole seconds")
    return _iso(ns)


def _iso(ns):
    s = ns // X.NS
    days, rem = divmod(s, 86400)
    z = days + 719468
    era = (z if z >= 0 else z - 146096) // 146097
    doe = z - era * 146097
    yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
    doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
    mp = (5 * doy + 2) // 153
    d = doy - (153 * mp + 2) // 5 + 1
    m = mp + 3 if mp < 10 else mp - 9
    y = yoe + era * 400 + (m <= 2)
    hh, rem = divmod(rem, 3600)
    mm, ss = divmod(rem, 60)
    return f"{y:04d}-{m:02d}-{d:02d}T{hh:02d}:{mm:02d}:{ss:02d}Z"


def bars_target(T_d_ns):
    """§4.2 / CC-05: symbols, timeframe, start = t_exp - 59 x 300 s, end = T_d, limit = 1000. Nothing else."""
    start = V.request_start_ns(T_d_ns)
    q = f"symbols=BTC%2FUSD&timeframe=5Min&start={utc_seconds(start)}&end={utc_seconds(T_d_ns)}&limit=1000"
    return f"{BARS_PATH}?{q}"


def quote_target():
    return f"{QUOTE_PATH}?symbols=BTC%2FUSD"


class Client:
    """The harness HTTP client. `allowlist` is what V12a reads as the client-reported allowlist (§6.4 step 1).
    `connect(host, timeout)` is injectable for tests; production uses http.client.HTTPSConnection."""

    def __init__(self, clock=time.time_ns, connect=None):
        self.allowlist = [HOST]
        self.clock = clock
        self._connect = connect or (lambda host, timeout: http.client.HTTPSConnection(
            host, 443, timeout=timeout, context=ssl.create_default_context()))

    def get(self, host, target):
        """One GET. Returns {url, sent, recv, header, body}; header/body/recv None when no HTTP response."""
        path = target.split("?", 1)[0]
        if host not in self.allowlist or host != HOST or path not in PATHS:
            raise RefusedRequest(f"refused before network I/O: {host}{path}")   # §2.2
        url = f"https://{host}{target}"
        conn = self._connect(host, TIMEOUT_S)
        sent = None
        try:
            conn.putrequest("GET", target, skip_accept_encoding=True)
            conn.putheader("Accept", "application/json")
            conn.putheader("Accept-Encoding", "identity")
            conn.putheader("User-Agent", "SL-PT-001-StageA/1")
            sent = self.clock()                                        # immediately before sending (§5.6)
            conn.endheaders()
            resp = conn.getresponse()
            recv = self.clock()                                        # response headers received (§5.6)
            version = {10: "1.0", 11: "1.1"}.get(resp.version, str(resp.version))
            header = V.build_header_artifact(version, resp.status, resp.reason, resp.getheaders())
            body = resp.read()                                         # chunked framing removed; not decompressed
            return {"url": url, "sent": sent, "recv": recv, "header": header, "body": body}
        except (OSError, http.client.HTTPException, ValueError):
            return {"url": url, "sent": sent if sent is not None else self.clock(), "recv": None,
                    "header": None, "body": None}
        finally:
            conn.close()

    def fetch_bars(self, T_d_ns):
        return self.get(HOST, bars_target(T_d_ns))

    def fetch_quote(self):
        return self.get(HOST, quote_target())
