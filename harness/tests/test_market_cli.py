"""Strike 4 tests: keyless client (§2.2, §4.2, §4.3 D-8, §5.6, CC-05), V12a on real observations (§6.4 step 1),
command line (policy pre-flight §7.4 / CC-02, GENESIS, invoke end to end through the real client over a FAKE
connection). No test opens a socket: every connection is a local fake. Governing text: R4.2i, contract v2.1."""
import io
import os
import shutil
import sys
import tempfile
import unittest
from urllib.parse import parse_qsl, urlsplit

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sl_pt_001 import cli as CLI         # noqa: E402
from sl_pt_001 import controller as C    # noqa: E402
from sl_pt_001 import evidence as E      # noqa: E402
from sl_pt_001 import exact as X         # noqa: E402
from sl_pt_001 import market as M        # noqa: E402
import test_controller as TCTL           # noqa: E402
import test_cycle_r42i as TC             # noqa: E402

NS = X.NS
T0 = TCTL.T0


class FakeResp:
    def __init__(self, status=200, reason="OK", headers=None, body=b"{}", version=11):
        self.status, self.reason, self.version, self._h, self._b = status, reason, version, headers or [], body

    def getheaders(self):
        return list(self._h)

    def read(self):
        return self._b


class FakeConn:
    """Records what the client sends; serves bars or quote bodies by path. Never touches the network."""

    def __init__(self, clock, log, serve, fail=None):
        self.clock, self.log, self.serve, self.fail = clock, log, serve, fail
        self.headers, self.target = [], None

    def putrequest(self, method, target, skip_accept_encoding=False):
        self.log.append(("putrequest", method, target, skip_accept_encoding))
        self.target = target

    def putheader(self, name, value):
        self.headers.append((name, value))

    def endheaders(self):
        self.log.append(("endheaders", self.clock()))
        if self.fail == "send":
            raise ConnectionResetError("reset")
        self.clock.t += NS // 10

    def getresponse(self):
        if self.fail == "recv":
            raise TimeoutError("timed out")
        return self.serve(self.target, self.clock())

    def close(self):
        self.log.append(("close",))


def serve_market(T_d_of_target):
    def serve(target, now):
        hdrs = [("Date", TC.imf(now)), ("Content-Type", "application/json"), ("X-Request-ID", "abc")]
        if target.startswith(M.BARS_PATH):
            q = dict(parse_qsl(urlsplit(target).query))
            T_d = X.parse_rfc3339_ns(q["end"])
            return FakeResp(headers=hdrs, body=TC.bars_body(TCTL.bars_for(T_d)))
        return FakeResp(headers=hdrs, body=TC.quote_body(t_ns=now - NS))
    return serve


def client(clock, fail=None):
    log, conns = [], []

    def connect(host, timeout):
        log.append(("connect", host, timeout))
        c = FakeConn(clock, log, serve_market(None), fail)
        conns.append(c)
        return c
    return M.Client(clock=clock, connect=connect), log, conns


class Requests(unittest.TestCase):
    def test_CC05_bars_url_exact_keys_and_instants(self):
        T_d = T0
        target = M.bars_target(T_d)
        q = parse_qsl(urlsplit(target).query, keep_blank_values=True)
        self.assertEqual([k for k, _ in q], ["symbols", "timeframe", "start", "end", "limit"])
        d = dict(q)
        self.assertEqual((d["symbols"], d["timeframe"], d["limit"]), ("BTC/USD", "5Min", "1000"))
        self.assertEqual(X.parse_rfc3339_ns(d["end"]), T_d)
        self.assertEqual(X.parse_rfc3339_ns(d["start"]), X.t_exp_ns(T_d) - 59 * 300 * NS)
        for k in ("start", "end"):
            self.assertRegex(d[k], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        self.assertEqual(urlsplit(target).path, "/v1beta3/crypto/us/bars")
        self.assertEqual(M.quote_target(), "/v1beta3/crypto/us/latest/quotes?symbols=BTC%2FUSD")
        with self.assertRaises(ValueError):
            M.utc_seconds(T_d + 1)

    def test_refused_before_network_io(self):
        clk = TCTL.Clock(T0)
        cl, log, _ = client(clk)
        for host, target in (("api.alpaca.markets", M.quote_target()), ("paper-api.alpaca.markets", "/v2/orders"),
                             ("data.alpaca.markets", "/v2/orders"), ("data.alpaca.markets", "/v1beta3/crypto/us/trades"),
                             ("data.alpaca.markets.evil", M.quote_target())):
            with self.subTest(host=host, target=target):
                with self.assertRaises(M.RefusedRequest):
                    cl.get(host, target)
        self.assertEqual(log, [])                                      # no connection was ever made

    def test_D8_headers_identity_no_auth_and_artifact_order(self):
        clk = TCTL.Clock(T0 + NS)
        cl, log, conns = client(clk)
        r = cl.fetch_quote()
        sent = dict(conns[0].headers)
        self.assertEqual(sent["Accept-Encoding"], "identity")
        self.assertTrue(log[1][3])                                     # http.client's default Accept-Encoding skipped
        names = [n.lower() for n, _ in conns[0].headers]
        self.assertFalse(any("auth" in n or n.startswith(("apca", "alpaca")) for n in names))
        self.assertEqual(r["header"].split(b"\r\n")[0], b"HTTP/1.1 200 OK")
        self.assertEqual([ln.split(b":")[0] for ln in r["header"].split(b"\r\n")[1:4]],
                         [b"Date", b"Content-Type", b"X-Request-ID"])  # received order, original case
        self.assertEqual(r["url"], "https://data.alpaca.markets" + M.quote_target())

    def test_5_6_t_send_before_send_t_recv_at_headers(self):
        clk = TCTL.Clock(T0 + NS)
        cl, log, _ = client(clk)
        r = cl.fetch_bars(T0)
        end_at = [e for e in log if e[0] == "endheaders"][0][1]
        self.assertEqual(r["sent"], end_at)
        self.assertEqual(r["recv"], end_at + NS // 10)

    def test_transport_failure_is_no_response(self):
        for fail in ("send", "recv"):
            with self.subTest(fail=fail):
                clk = TCTL.Clock(T0 + NS)
                cl, log, _ = client(clk, fail)
                r = cl.fetch_bars(T0)
                self.assertEqual((r["header"], r["body"], r["recv"]), (None, None, None))
                self.assertIsNotNone(r["sent"])
                self.assertEqual(log[-1], ("close",))


class BoundaryObservations(unittest.TestCase):
    def test_env_names_only_and_config_file(self):
        cl = M.Client()
        r, ev, cfg = CLI.boundary(cl, {"PATH": "x", "APCA_API_SECRET_KEY": "secret-value"})
        self.assertEqual((r, cfg, ev["env_credential_names"]), ("FAIL", None, ["APCA_API_SECRET_KEY"]))
        self.assertNotIn("secret-value", repr(ev))
        r, ev, cfg = CLI.boundary(cl, {"PATH": "x"})
        self.assertEqual((r, cfg), ("PASS", TC.CFG))                   # harness/config.json
        r, ev, cfg = CLI.boundary(cl, {"PATH": "x"}, config_path=os.path.join(tempfile.mkdtemp(), "none.json"))
        self.assertEqual((r, ev["config_sha256"], cfg), ("FAIL", None, None))


class CommandLine(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.root = os.path.join(self.repo, "experiments", "sl-pt-001")
        os.makedirs(self.root)
        self.out = io.StringIO()

    def cli(self, *args, clock=None, client=None, environ=None):
        return CLI.main(["cli", *args], clock=clock or TCTL.Clock(T0), client=client,
                        environ={"PATH": "x"} if environ is None else environ, out=self.out)

    def test_write_policy_once_and_never_rewritten(self):
        self.assertEqual(self.cli("write-policy", self.root), 0)
        p = os.path.join(self.root, "policy", "P-0.2.json")
        with open(p, "rb") as fh:
            self.assertEqual(fh.read(), E.policy_bytes())
        self.assertEqual(self.cli("write-policy", self.root), 0)
        with open(p, "ab") as fh:
            fh.write(b"\n")
        self.assertEqual(self.cli("write-policy", self.root), 4)

    def test_genesis_requires_the_pinned_spec_file(self):
        self.assertEqual(self.cli("genesis", self.root), 4)            # no spec file in this repo
        spec_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", *E.SPEC_PATH.split("/"))
        if not os.path.exists(spec_src):
            self.skipTest("R4.2i not present beside this harness tree")
        dst = os.path.join(self.repo, *E.SPEC_PATH.split("/"))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(spec_src, dst)
        self.assertEqual(self.cli("genesis", self.root), 0)
        self.assertEqual(self.cli("genesis", self.root), 4)            # written once

    def setup_run(self):
        self.cli("write-policy", self.root)
        clk = TCTL.Clock(T0 - 10 * NS)
        g = C.Harness(self.root, clk).genesis({E.SPEC_PATH: E.SPEC_SHA256})
        mpath = os.path.join(self.root, "runs", "run-1.json")
        os.makedirs(os.path.dirname(mpath))
        with open(mpath, "wb") as fh:
            fh.write(TCTL.manifest(g["hash"]))
        return mpath

    def test_invoke_end_to_end_through_the_real_client(self):
        mpath = self.setup_run()
        clk = TCTL.Clock(T0 + NS)
        cl, log, _ = client(clk)
        self.assertEqual(self.cli("invoke", self.root, mpath, str(T0 + NS), clock=clk, client=cl), 0)
        recs = E.read_chain(self.root)
        self.assertEqual([r["type"] for r in recs], ["GENESIS", "RUN_OPEN", "CYCLE"])
        t = recs[-1]["body"]
        self.assertEqual((t["terminal_state"], t["V12b"]["result"]), ("HOLD", "PASS"))
        self.assertEqual(t["bars_request"]["url"], "https://data.alpaca.markets" + M.bars_target(T0))
        self.assertEqual([e[1] for e in log if e[0] == "connect"], ["data.alpaca.markets"] * 2)

    def test_invoke_V12a_fail_makes_no_connection(self):
        mpath = self.setup_run()
        clk = TCTL.Clock(T0 + NS)
        cl, log, _ = client(clk)
        self.assertEqual(self.cli("invoke", self.root, mpath, str(T0 + NS), clock=clk, client=cl,
                                  environ={"ALPACA_KEY": "v"}), 0)
        self.assertEqual(E.read_chain(self.root)[-1]["body"]["terminal_state"], "BOUNDARY_FAIL")
        self.assertEqual(log, [])

    def test_invoke_refuses_on_policy_mismatch_and_writes_nothing(self):
        mpath = self.setup_run()
        p = os.path.join(self.root, "policy", "P-0.2.json")
        with open(p, "ab") as fh:
            fh.write(b" ")                                             # still valid JSON, different hash
        n = len(E.read_chain(self.root))
        clk = TCTL.Clock(T0 + NS)
        cl, log, _ = client(clk)
        self.assertEqual(self.cli("invoke", self.root, mpath, str(T0 + NS), clock=clk, client=cl), 4)
        self.assertEqual((len(E.read_chain(self.root)), log), (n, []))

    def test_usage(self):
        self.assertEqual(self.cli("invoke", self.root), 2)


if __name__ == "__main__":
    unittest.main()
