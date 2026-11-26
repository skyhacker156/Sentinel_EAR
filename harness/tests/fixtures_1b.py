"""Deterministic local fixtures for Strike 1b-pre tests. Never live data. Token text throughout."""
from sl_pt_001 import exact as X

NS = X.NS
T_D = X.parse_rfc3339_ns("2026-11-26T10:01:00Z")      # (T_d - 60 s) on the 300 s grid
T_EXP = X.t_exp_ns(T_D)                                 # 09:55:00Z


def iso(ns):
    s, frac = divmod(ns, NS)
    days, rem = divmod(s, 86400)
    # civil from days (inverse of exact._days_from_civil), exact integers
    z = days + 719468
    era = (z if z >= 0 else z - 146096) // 146097
    doe = z - era * 146097
    yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
    y = yoe + era * 400
    doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
    mp = (5 * doy + 2) // 153
    d = doy - (153 * mp + 2) // 5 + 1
    m = mp + 3 if mp < 10 else mp - 9
    y += m <= 2
    hh, rem = divmod(rem, 3600)
    mm, ss = divmod(rem, 60)
    out = f"{y:04d}-{m:02d}-{d:02d}T{hh:02d}:{mm:02d}:{ss:02d}"
    return out + (f".{frac:09d}" if frac else "") + "Z"


def bar(t_ns, c, v="1.5", n="3"):
    return {"t": iso(t_ns), "o": c, "h": c, "l": c, "c": c, "v": v, "vw": c, "n": n}


def bars(last_delta="0", base="90000", count=51, with_forming=True):
    """`count` completed bars ending at t_exp, oldest first; closes all `base` except the newest,
    which is base + last_delta. Then D(k-1) = 0 and D(k) = 3 * last_delta (DERIVED). Plus one forming bar."""
    b0 = X.parse_number_token(base)
    out = []
    for j in range(count - 1, -1, -1):
        t = T_EXP - 300 * NS * j
        c = base if j else X.to_decimal_string(b0 + X.parse_number_token(last_delta))
        out.append(bar(t, c))
    if with_forming:
        out.append(bar(T_EXP + 300 * NS, base))          # 10:00 bar: not completed at T_d = 10:01 (U17)
    return out


def quote(bid="90004.25", ask="90004.75", t_ns=None, bs="0.5", as_="0.4"):
    return {"bp": bid, "ap": ask, "bs": bs, "as": as_, "t": iso(t_ns if t_ns is not None else T_D + 3 * NS)}
