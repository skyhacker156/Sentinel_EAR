"""SL-PT-001 Stage A harness: data validation (Strike 1b-pre portion).

Implements ONLY requirements whose text is unchanged between frozen R4.2c and candidate R4.2g
(row-level comparison, COMPUTED): §4.7 rows V3-V10 and V12b plus the evaluation rule, §4.10, §4.11 (Q1-Q5),
§5.6 (V12b predicate). Authority: FD-5 (5252322), unchanged requirements only.

DEFERRED to the amended freeze (their governing text changes in R4.2g):
  V1 (D-8 adds the Content-Encoding rule via §4.3), V2 (D-1), V11 and the bar-store fold (D-6), V12a (D-2).
Inputs are therefore bar and quote objects whose values are still JSON number TOKEN TEXT (strings), as V1
would hand them over. Nothing here reads a clock, a file or the network.
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
            "deferred": ["V1", "V2", "V11", "V12a"]}


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
