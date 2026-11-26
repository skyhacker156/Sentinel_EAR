"""SL-PT-001 Stage A harness: data validation.

Governing text: frozen R4.2i (freeze 5ec5d1b), FD-5 v2. §4.3, §4.4, §4.7 (V1-V12b), §4.9 (bar store, D-6),
§4.10, §4.11 (Q1-Q5), §5.6 (V12b), §6.4 step 1 (V12a, D-2), §10.4 displayed sizes (G8-01).
History: V3-V10, Q1-Q5 and the V12b predicate were built first (Strike 1b-pre) against requirements unchanged
between R4.2c and R4.2i; V1, V2, the bar store, V11, V12a and displayed sizes were added after the freeze.
Nothing here reads a clock, a file, the environment or the network: every observation is supplied by the caller.
"""
import re

from . import exact as X

NS = X.NS
WINDOW = 51
V_ORDER = ["V3", "V4", "V5", "V6", "V7", "V8", "V9", "V10"]           # V11 deferred (D-6)
SUBREASON = {"V3": "MALFORMED_VALUE", "V4": "DATA_CONFLICT", "V7": "STALE_SERIES", "V8": "DATA_GAP",
             "V9": "MALFORMED_VALUE", "V10": "INSUFFICIENT_HISTORY"}  # V5, V6 never fail (§4.7)
BAR_FIELDS = ("o", "h", "l", "c", "v", "vw", "n")


def _num(tok):
    return X.parse_number_token(tok)


def validate_bars(bars, T_d_ns):
    """V3-V10 on one bars response that has passed V1 and V2 (§4.7 rule: all evaluated, all failures recorded).

    `bars`: list of dicts in ARRIVAL order, each with key 't' (RFC-3339 text) and keys o, h, l, c, v, vw, n
    holding JSON number token text. Returns a dict with per-check PASS/FAIL, the first-failure NO_DECISION
    sub-reason (or None), and the partitions needed downstream.

    IMPLEMENTATION READINGS (flagged, fail-closed; R4.2c is not explicit, GPT contract v1 §7.6 notes the same):
      - checks V4-V10 are evaluated over the bars whose 't' parses; a V3 failure already decides the sub-reason;
      - V4 "byte-identical" duplicates are compared as identical token text for t and all seven fields;
      - V9 applies to every bar in the response, not only to completed bars (§4.10: any malformed value).
    """
    res = {}
    parsed, bad_t = [], False
    for b in bars:
        try:
            t = X.parse_rfc3339_ns(b["t"])
        except (X.MalformedValue, KeyError, TypeError):
            bad_t = True
            continue
        if t % (300 * NS) != 0:
            bad_t = True
        parsed.append((t, b))
    res["V3"] = "FAIL" if bad_t else "PASS"

    # V4: t unique; byte-identical duplicates collapse with a note; differing duplicates fail.
    by_t, notes, conflict = {}, [], False
    for t, b in parsed:
        key = (b.get("t"),) + tuple(b.get(f) for f in BAR_FIELDS)
        if t in by_t:
            if by_t[t][1] == key:
                notes.append(("DUPLICATE_COLLAPSED", t))
            else:
                conflict = True
        else:
            by_t[t] = (b, key)
    res["V4"] = "FAIL" if conflict else "PASS"

    # V5: arrival order kept by the caller; sorted copy for computation. Never fails.
    ordered = sorted(((t, bk[0]) for t, bk in by_t.items()), key=lambda x: x[0])
    res["V5"] = "PASS"

    # V6: non-completed bars excluded (§4.6). Never fails.
    completed = [(t, b) for t, b in ordered if X.is_completed(t, T_d_ns)]
    excluded = [(t, b) for t, b in ordered if not X.is_completed(t, T_d_ns)]
    res["V6"] = "PASS"

    # V7: newest completed bar has t = t_exp.
    t_exp = X.t_exp_ns(T_d_ns)
    res["V7"] = "PASS" if completed and completed[-1][0] == t_exp else "FAIL"

    # V8: every 300 s step in [t_exp - 250 min, t_exp] has a bar (51 bars).
    have = {t for t, _ in completed}
    steps = [t_exp - 300 * NS * j for j in range(WINDOW)]
    res["V8"] = "PASS" if all(s in have for s in steps) else "FAIL"

    # V9: numeric validity: finite; o, h, l, c, vw > 0; v >= 0; n >= 0 and an integer.
    v9 = True
    for b in bars:
        try:
            vals = {f: _num(b[f]) for f in BAR_FIELDS}
        except (X.MalformedValue, KeyError, TypeError):
            v9 = False
            continue
        if not all(vals[f] > 0 for f in ("o", "h", "l", "c", "vw")):
            v9 = False
        if vals["v"] < 0 or vals["n"] < 0 or vals["n"].denominator != 1:
            v9 = False
    res["V9"] = "PASS" if v9 else "FAIL"

    # V10: at least 51 completed candles.
    res["V10"] = "PASS" if len(completed) >= WINDOW else "FAIL"

    first = next((c for c in V_ORDER if res[c] == "FAIL"), None)
    window = []
    if first is None:
        window = [(t, b) for t, b in completed if t in set(steps)]
    return {"results": res, "first_failure": first,
            "subreason": SUBREASON.get(first) if first else None,
            "completed": completed, "excluded": excluded, "duplicate_notes": notes, "window": window,
            "evaluated_elsewhere": ["V1", "V2", "V11", "V12a"]}   # check_bars_response, check_V11, boundary_check


def window_closes(validation):
    """Exact closes of the 51-bar window, oldest first, only when V3-V10 all passed."""
    if validation["first_failure"] is not None:
        raise ValueError("no signal input: a V check failed")
    w = validation["window"]
    if len(w) != WINDOW:
        raise ValueError("window is not exactly 51 bars")
    return [_num(b["c"]) for _, b in w]


# ---------------------------------------------------------------------------------------- quote (§4.11)
def validate_quote(quote):
    """Q1-Q5 (§4.11). `quote` is a dict of token text (bp, ap, bs, as, t) or None when absent.
    An absent quote fails every Q check (§4.11 outcomes; §10.4 QUOTE_INVALID row). All checks are evaluated."""
    if quote is None:
        return {q: "FAIL" for q in ("Q1", "Q2", "Q3", "Q4", "Q5")}

    def val(k):
        try:
            return _num(quote[k])
        except (X.MalformedValue, KeyError, TypeError):
            return None
    bp, ap, bs, as_ = val("bp"), val("ap"), val("bs"), val("as")
    try:
        X.parse_rfc3339_ns(quote["t"])
        q5 = True
    except (X.MalformedValue, KeyError, TypeError):
        q5 = False
    return {
        "Q1": "PASS" if bp is not None and bp > 0 else "FAIL",
        "Q2": "PASS" if ap is not None and ap > 0 else "FAIL",
        "Q3": "PASS" if bp is not None and ap is not None and ap >= bp else "FAIL",
        "Q4": "PASS" if bs is not None and as_ is not None and bs >= 0 and as_ >= 0 else "FAIL",
        "Q5": "PASS" if q5 else "FAIL",
    }


def quote_values(quote):
    """Exact bid, ask and instant of a quote that passed Q1-Q5."""
    return {"bid": _num(quote["bp"]), "ask": _num(quote["ap"]), "t": X.parse_rfc3339_ns(quote["t"])}


# ------------------------------------------------------------------------------- V12b predicate (§5.6)
_IMF = re.compile(r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun), (\d{2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) "
                  r"(\d{4}) (\d{2}):(\d{2}):(\d{2}) GMT\Z")
_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
_DAYS = ["Thu", "Fri", "Sat", "Sun", "Mon", "Tue", "Wed"]          # 1970-01-01 was a Thursday


def parse_imf_fixdate_ns(text):
    """RFC 7231 IMF-fixdate -> integer ns (whole seconds). Strict: a weekday inconsistent with the date fails."""
    m = _IMF.match(text or "")
    if not m:
        raise X.MalformedValue(f"not IMF-fixdate: {text!r}")
    wd, dd, mon, yyyy, hh, mi, ss = m.groups()
    iso = f"{yyyy}-{_MONTHS.index(mon) + 1:02d}-{dd}T{hh}:{mi}:{ss}Z"
    ns = X.parse_rfc3339_ns(iso)
    if _DAYS[(ns // (86400 * NS)) % 7] != wd:
        raise X.MalformedValue(f"weekday does not match date: {text!r}")
    return ns


def clock_check(date_header, t_send_ns, t_recv_ns):
    """V12b (§5.6): PASS iff all four conditions hold. Returns (result, D, theta_low, theta_high)."""
    try:
        D = parse_imf_fixdate_ns(date_header)
    except X.MalformedValue:
        return "FAIL", None, None, None                                   # condition 1
    theta_low = D - t_recv_ns
    theta_high = D + 1 * NS - t_send_ns
    ok = (t_recv_ns >= t_send_ns                                          # condition 2
          and t_recv_ns - t_send_ns < 3 * NS                              # condition 3
          and theta_low >= -2 * NS and theta_high <= 2 * NS)              # condition 4
    return ("PASS" if ok else "FAIL"), D, theta_low, theta_high


# ======================================================================================================
# Strike 1b completion under FD-5 v2 (governing text: frozen R4.2i, freeze 5ec5d1b).
#   §4.3 item 1 (D-8 artifacts), §4.7 V1 and V2 (D-1), §4.9 bar store with the D-6 admission rule, V11,
#   §6.4 step 1 V12a (D-2), §10.4 displayed sizes (G8-01).
# TER serialization and event-name spellings follow GPT's interface contract, which is not yet at v2:
# names used below that the contract fixes are PROVISIONAL (contract v1 spelling) until v2 is committed.
# ======================================================================================================
import hashlib
import json

SYMBOL = "BTC/USD"


class NumTok(str):
    """Token text of a JSON number, as it appeared in the body."""


class NonNumeric:
    """A JSON value that is not a number where a number is required (§4.10). parse_number_token refuses it."""
    __slots__ = ("value",)

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return isinstance(other, NonNumeric) and repr(self.value) == repr(other.value)

    def __repr__(self):
        return f"NonNumeric({self.value!r})"


def _reject_constant(name):
    raise ValueError(f"non-JSON constant {name}")


def _no_duplicate_keys(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate object key")
    return dict(pairs)


def parse_json_tokens(body_bytes):
    """Strict JSON with number token text preserved (§4.3 items 2-4). NaN/Infinity and duplicate keys are not
    well-formed JSON here (IMPLEMENTATION READING, fail-closed). Raises ValueError on any failure."""
    text = body_bytes.decode("utf-8")                                  # UnicodeDecodeError is a ValueError
    return json.loads(text, parse_float=NumTok, parse_int=NumTok, parse_constant=_reject_constant,
                      object_pairs_hook=_no_duplicate_keys)


def _numeric_or_marker(v):
    return str(v) if isinstance(v, NumTok) else NonNumeric(v)


# --------------------------------------------------------------------------------- header artifact (D-8)
def build_header_artifact(version, status, reason, fields):
    """§4.3 D-8: 'HTTP/<version> <status> <reason>' CRLF, each 'Name: value' CRLF in received order, then CRLF.
    The client's report, not a wire capture."""
    lines = [f"HTTP/{version} {status} {reason}"] + [f"{n}: {v}" for n, v in fields]
    return ("\r\n".join(lines) + "\r\n\r\n").encode("latin-1")


def parse_header_artifact(raw):
    """Inverse of build_header_artifact. Returns (status:int, fields:list[(name, value)]). Raises ValueError."""
    text = raw.decode("latin-1")
    if not text.endswith("\r\n\r\n"):
        raise ValueError("header artifact must end with CRLF CRLF")
    lines = text[:-4].split("\r\n")
    m = re.fullmatch(r"HTTP/(\d(?:\.\d)?) (\d{3}) ?(.*)", lines[0])
    if not m:
        raise ValueError("bad status line")
    fields = []
    for line in lines[1:]:
        name, sep, value = line.partition(": ")
        if not sep or not name:
            raise ValueError(f"bad header line: {line!r}")
        fields.append((name, value))
    return int(m.group(2)), fields


def header_value(fields, name):
    """Last value of a header, matched case-insensitively; None if absent."""
    vals = [v for n, v in fields if n.lower() == name.lower()]
    return vals[-1] if vals else None


# ------------------------------------------------------------------------------------------ V1 and V2
def check_bars_response(header_raw, body_raw):
    """V1 and V2 on the bars response (§4.7; D-1; D-8).

    V1: HTTP 200; no Content-Encoding other than identity; well-formed JSON; response key next_page_token
    present; symbol key exactly BTC/USD with no other symbol; every bar has t, o, h, l, c, v, n, vw.
    Sub-reason mapping (follows contract v1 CONTRACT CHOICE, to be re-checked at v2): HTTP / encoding / JSON /
    symbol -> FETCH_FAILED; a missing required key -> INCOMPLETE_RESPONSE.
    V2: next_page_token is JSON null; any other value, including "", fails (INCOMPLETE_RESPONSE). No further
    page is ever fetched.
    Returns dict(V1, V2, subreason, bars) where bars hold token text (str) or NonNumeric markers, in arrival order.
    """
    out = {"V1": "FAIL", "V2": "NOT_EVALUATED", "subreason": "FETCH_FAILED", "bars": []}
    try:
        status, fields = parse_header_artifact(header_raw)
    except ValueError:
        return out
    enc = header_value(fields, "Content-Encoding")
    if status != 200 or (enc is not None and enc.strip().lower() != "identity"):
        return out
    try:
        doc = parse_json_tokens(body_raw)
    except ValueError:
        return out
    if not isinstance(doc, dict) or not isinstance(doc.get("bars"), dict):
        out["subreason"] = "INCOMPLETE_RESPONSE" if isinstance(doc, dict) else "FETCH_FAILED"
        return out
    if set(doc["bars"]) != {SYMBOL}:
        return out                                                     # wrong or extra symbol (U95)
    if "next_page_token" not in doc or not isinstance(doc["bars"][SYMBOL], list):
        out["subreason"] = "INCOMPLETE_RESPONSE"                      # U94: key absent
        return out
    bars = []
    for b in doc["bars"][SYMBOL]:
        if not isinstance(b, dict) or not all(k in b for k in ("t",) + BAR_FIELDS):
            out["subreason"] = "INCOMPLETE_RESPONSE"
            return out
        row = {"t": b["t"] if isinstance(b["t"], str) and not isinstance(b["t"], NumTok) else NonNumeric(b["t"])}
        row.update({f: _numeric_or_marker(b[f]) for f in BAR_FIELDS})
        bars.append(row)
    out.update(V1="PASS", subreason=None, bars=bars)
    if doc["next_page_token"] is not None:
        out.update(V2="FAIL", subreason="INCOMPLETE_RESPONSE")         # U13; D-1
    else:
        out["V2"] = "PASS"
    return out


def check_quote_response(header_raw, body_raw):
    """The quote response (§4.11; U95; U113; §4.3 D-8; §10.4 G8-01).
    - no response (both None): the quote is absent and no response is available; V1 is not failed (U113);
    - a Content-Encoding other than identity fails V1 (§4.3 D-8: "a response with any Content-Encoding other than
      identity fails V1"). [Fix F-1, 2026-11-26: the earlier code treated this as an absent quote.]
    - a quote that parses and is keyed by any symbol other than exactly BTC/USD fails V1 (U95);
    - a non-200 status, an unparseable header artifact or malformed JSON leave the quote ABSENT (Q1-Q5 all FAIL if a
      proposal is built, §4.11), but a response WAS received, so displayed sizes are {bs: null, as: null}
      (§10.4 G8-01: the object is null only when no quote is available). [Fix F-2, 2026-11-26.]
    Both fixes cite R4.2i text; they were found while checking the harness against contract v2 and the spec."""
    if header_raw is None and body_raw is None:
        return {"V1_quote": "PASS", "quote": None, "available": False}
    absent = {"V1_quote": "PASS", "quote": None, "available": True}
    try:
        status, fields = parse_header_artifact(header_raw)
    except (ValueError, TypeError, AttributeError):
        return absent
    enc = header_value(fields, "Content-Encoding")
    if enc is not None and enc.strip().lower() != "identity":
        return {"V1_quote": "FAIL", "quote": None, "available": True}          # F-1 (D-8)
    if status != 200:
        return absent
    try:
        doc = parse_json_tokens(body_raw)
    except (ValueError, TypeError, AttributeError):
        return absent
    quotes = doc.get("quotes") if isinstance(doc, dict) else None
    if not isinstance(quotes, dict):
        return absent
    if set(quotes) != {SYMBOL}:
        return {"V1_quote": "FAIL", "quote": None, "available": True}          # U95
    q = quotes[SYMBOL]
    if not isinstance(q, dict):
        return absent
    row = {k: _numeric_or_marker(q[k]) for k in ("bp", "ap", "bs", "as") if k in q}
    if "t" in q:
        row["t"] = q["t"] if isinstance(q["t"], str) and not isinstance(q["t"], NumTok) else NonNumeric(q["t"])
    return {"V1_quote": "PASS", "quote": row, "available": True}


def displayed_sizes(quote, available=None):
    """§10.4 G8-01: {bs, as}, each the token text when the key holds a JSON number token, else None.
    None as a whole ONLY when no quote is available (request never issued, NO_RESPONSE, injected V12a FAIL).
    `available` defaults to (quote is not None); pass it explicitly when a response arrived but was unusable (F-2)."""
    if available is None:
        available = quote is not None
    if not available:
        return None
    quote = quote or {}
    return {k: (quote[k] if isinstance(quote.get(k), str) else None) for k in ("bs", "as")}


# ------------------------------------------------------------------------- bar store and V11 (§4.9, D-6)
def bar_tuple(b):
    return tuple(b[f] for f in BAR_FIELDS)


def admitted(v1v2, v):
    """D-6: a bars response contributes observations only if V1, V2, V3, V4 and V9 all pass."""
    return (v1v2["V1"] == "PASS" and v1v2["V2"] == "PASS"
            and all(v["results"][c] == "PASS" for c in ("V3", "V4", "V9")))


def fold(store, v, request_start_ns, T_d_ns):
    """Apply one admitted cycle's observations to the store (§4.9 table). Returns the transition events.
    `store`: dict t_ns -> {"tuple", "state", "count", "pending"}; mutated in place.
    Event spellings (BASELINED, OBSERVED, SOURCE_REVISION, CONFIRMED, DISAPPEARED, DUPLICATE_COLLAPSED) are
    contract v1 CONTRACT CHOICES, PROVISIONAL until v2. Order: duplicate notes in arrival order, then
    observations in ascending t, then disappearances in ascending t (contract v1)."""
    events = [{"t": t, "event": "DUPLICATE_COLLAPSED"} for _, t in v["duplicate_notes"]]
    seen = set()
    for t, b in v["completed"]:
        seen.add(t)
        new = bar_tuple(b)
        cur = store.get(t)
        if cur is None:
            store[t] = {"tuple": new, "state": "BASELINED", "count": 1, "pending": None}
            events.append({"t": t, "event": "BASELINED", "new": new})
        elif cur["state"] == "PENDING":
            if new == cur["pending"]:
                cur.update(tuple=new, state="CONFIRMED", count=2, pending=None)
                events.append({"t": t, "event": "CONFIRMED", "new": new})
            else:                                                      # differs from pending (incl. A->B->A, U40)
                events.append({"t": t, "event": "SOURCE_REVISION", "old": cur["pending"], "new": new})
                cur["pending"] = new
        elif new == cur["tuple"]:
            cur["count"] += 1
            events.append({"t": t, "event": "OBSERVED"})
        else:
            events.append({"t": t, "event": "SOURCE_REVISION", "old": cur["tuple"], "new": new})
            cur.update(state="PENDING", pending=new)
    for t in sorted(store):
        if t not in seen and request_start_ns <= t and X.is_completed(t, T_d_ns) and store[t]["state"] != "PENDING":
            events.append({"t": t, "event": "DISAPPEARED"})            # accepted bar absent inside the range
    return events


def check_V11(store, T_d_ns):
    """V11: any PENDING bar inside the current 51-bar window [t_exp - 250 min, t_exp] -> FAIL (SOURCE_REVISION).
    The window is the 51 grid steps themselves, whether or not every bar arrived (V8 covers absences)."""
    t_exp = X.t_exp_ns(T_d_ns)
    steps = {t_exp - 300 * NS * j for j in range(WINDOW)}
    return "FAIL" if any(store.get(t, {}).get("state") == "PENDING" for t in steps) else "PASS"


def request_start_ns(T_d_ns):
    """§4.2: start = t_exp - 59 x 300 s."""
    return X.t_exp_ns(T_d_ns) - 59 * 300 * NS


# --------------------------------------------------------------------------------- V12a (§6.4 step 1, D-2)
ALLOWLIST = ["data.alpaca.markets"]


def boundary_check(env_names, config_bytes, client_allowlist):
    """V12a on SUPPLIED observations (the caller reads the process environment, the config file and the client
    object; this function reads nothing). Credential = an env name beginning APCA_ or ALPACA_ (case-insensitive),
    or any config key other than client_allowlist. Values are never taken or recorded.
    Returns (result, evidence, store_config_bytes). Evidence is HARNESS-ATTESTED (§11.1, U-I3)."""
    matched = sorted(n for n in env_names if n.upper().startswith(("APCA_", "ALPACA_")))
    config_sha = hashlib.sha256(config_bytes).hexdigest() if config_bytes is not None else None
    ok = not matched and config_bytes is not None and list(client_allowlist) == ALLOWLIST
    if ok:
        try:
            cfg = parse_json_tokens(config_bytes)
            ok = isinstance(cfg, dict) and set(cfg) == {"client_allowlist"} and cfg["client_allowlist"] == ALLOWLIST
        except ValueError:
            ok = False
    evidence = {"env_credential_names": matched, "config_sha256": config_sha,
                "client_allowlist": list(client_allowlist)}
    return ("PASS" if ok else "FAIL"), evidence, ok                    # config bytes stored only on PASS
