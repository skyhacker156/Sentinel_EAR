"""SL-PT-001 Stage A harness: exact values and instants.

Governing text (frozen R4.2c; byte-identical in candidate R4.2f, COMPUTED): §4.3 items 2-3, §4.4, §4.6, §4.8,
§4.10, §5.1, §5.2, §5.3, §6.2. Strike 1a under FD-5 (5252322).

Rules kept by this module:
- Every numeric value is an exact rational (fractions.Fraction) built from the original JSON number token text.
  No binary floating point and no decimal module are used anywhere (§4.3 item 2, §5.1).
- Every instant is an integer number of nanoseconds since the Unix epoch, UTC (§4.4). No clock is read here.
- The only rounding points are the named ones (§5.1): floor_q, round_limit, ceil_cent, display_8dp.
"""
from fractions import Fraction
import math
import re

NS = 1_000_000_000
BAR_S = 300                      # 5Min bars
SETTLE_S = 60                    # settle, accepted RC-25c (§4.6)
W_S = 90                         # cutoff W, founder (§5.3)


class MalformedValue(ValueError):
    """A token that §4.10 / §4.4 classifies as malformed."""


# --------------------------------------------------------------------------------------------------- numbers
# JSON number grammar (RFC 8259 §6). Anything else, including NaN / Infinity / '+1' / '01' / '.5', is malformed.
_JSON_NUMBER = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.([0-9]+))?(?:[eE]([+-]?[0-9]+))?\Z")


def parse_number_token(token):
    """Exact rational from the original JSON number token text (§4.3 items 2-3; §4.10)."""
    if not isinstance(token, str):
        raise MalformedValue(f"not token text: {type(token).__name__}")
    m = _JSON_NUMBER.match(token)
    if not m:
        raise MalformedValue(f"not a finite JSON number token: {token!r}")
    frac = m.group(1) or ""
    exp = int(m.group(2) or "0")
    mantissa_text = token.split("e")[0].split("E")[0]
    negative = mantissa_text.startswith("-")
    digits = mantissa_text.lstrip("-").replace(".", "")
    value = Fraction(int(digits), 10 ** len(frac))
    if exp >= 0:
        value *= 10 ** exp
    else:
        value /= 10 ** (-exp)
    return -value if negative else value


def is_zero_volume(v_token):
    """§4.8: zero_volume iff the exact value of v = 0 (covers 0, 0.0, 0e0, -0). No text matching."""
    return parse_number_token(v_token) == 0


# ------------------------------------------------------------------------------------------ rounding points
def _check_increment(inc):
    if not isinstance(inc, Fraction) or inc <= 0:
        raise ValueError("increment must be a positive Fraction")


def floor_to(x, inc):
    """Floor x to a multiple of inc (q: floor to the quantity increment, §5.1)."""
    _check_increment(inc)
    return math.floor(Fraction(x) / inc) * inc


def ceil_to(x, inc):
    _check_increment(inc)
    return math.ceil(Fraction(x) / inc) * inc


def round_limit(price, side, price_increment):
    """L to the price increment, conservatively: BUY down, EXIT up (§5.1, §7.2)."""
    if side == "BUY":
        return floor_to(price, price_increment)
    if side == "EXIT":
        return ceil_to(price, price_increment)
    raise ValueError(f"side must be BUY or EXIT: {side!r}")


def ceil_cent(x):
    """R: ceil to the cent (§5.1)."""
    return ceil_to(x, Fraction(1, 100))


def display_8dp(x):
    """Display value: 8 dp, round-half-even. DISPLAY ONLY; never an input to any decision (§5.1)."""
    x = Fraction(x)
    scaled = x * 10 ** 8
    q, r = divmod(scaled.numerator, scaled.denominator)          # floor division, exact
    twice = 2 * r
    if twice > scaled.denominator or (twice == scaled.denominator and q % 2 == 1):
        q += 1
    sign = "-" if q < 0 else ""
    q = abs(q)
    return f"{sign}{q // 10**8}.{q % 10**8:08d}"


def to_decimal_string(x):
    """Exact decimal string of a terminating rational (TER numerics are strings, §10.4). Raises if non-terminating."""
    x = Fraction(x)
    d = x.denominator
    twos = fives = 0
    while d % 2 == 0:
        d //= 2
        twos += 1
    while d % 5 == 0:
        d //= 5
        fives += 1
    if d != 1:
        raise ValueError(f"non-terminating decimal: {x}")
    places = max(twos, fives)
    n = abs(x.numerator) * (10 ** places // x.denominator)
    sign = "-" if x < 0 else ""
    if places == 0:
        return f"{sign}{n}"
    return f"{sign}{n // 10**places}.{n % 10**places:0{places}d}"


# --------------------------------------------------------------------------------------------------- instants
_RFC3339 = re.compile(
    r"(\d{4})-(\d{2})-(\d{2})[Tt](\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?(?:([Zz])|([+-])(\d{2}):(\d{2}))\Z")


def _days_from_civil(y, m, d):
    """Days since 1970-01-01 for a proleptic Gregorian date (exact integer arithmetic)."""
    y -= m <= 2
    era = (y if y >= 0 else y - 399) // 400
    yoe = y - era * 400
    doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


def _days_in_month(y, m):
    if m == 2:
        return 29 if (y % 4 == 0 and y % 100 != 0) or y % 400 == 0 else 28
    return 30 if m in (4, 6, 9, 11) else 31


def parse_rfc3339_ns(text):
    """Exact RFC-3339 -> integer ns since the epoch, UTC (§4.4).

    Malformed: missing zone designator, more than 9 fractional digits, any parse failure.
    IMPLEMENTATION READING (flagged for review): a leap second (second = 60) has no POSIX-epoch ns value,
    so it is treated as malformed (fail-closed). R4.2c is silent on it.
    """
    if not isinstance(text, str):
        raise MalformedValue("timestamp is not a string")
    m = _RFC3339.match(text)
    if not m:
        raise MalformedValue(f"not RFC-3339 with a zone designator: {text!r}")
    y, mo, d, hh, mi, ss = (int(g) for g in m.groups()[:6])
    frac = m.group(7) or ""
    if len(frac) > 9:
        raise MalformedValue(f"more than 9 fractional digits: {text!r}")
    if not (1 <= mo <= 12 and 1 <= d <= _days_in_month(y, mo) and hh <= 23 and mi <= 59 and ss <= 59):
        raise MalformedValue(f"field out of range: {text!r}")
    offset_s = 0
    if m.group(9):
        oh, om = int(m.group(10)), int(m.group(11))
        if oh > 23 or om > 59:
            raise MalformedValue(f"zone offset out of range: {text!r}")
        offset_s = (oh * 3600 + om * 60) * (1 if m.group(9) == "+" else -1)
    seconds = _days_from_civil(y, mo, d) * 86400 + hh * 3600 + mi * 60 + ss - offset_s
    return seconds * NS + int(frac.ljust(9, "0") or "0")


# ---------------------------------------------------------------------------------- completed candles (§4.6)
def is_completed(t_ns, T_d_ns, settle_s=SETTLE_S):
    """A bar with start t is completed iff t + 300 s + settle <= T_d (§4.6, §5.4)."""
    return t_ns + (BAR_S + settle_s) * NS <= T_d_ns


def t_exp_ns(T_d_ns, settle_s=SETTLE_S):
    """Expected newest completed bar: floor_300s(T_d - settle) - 300 s (§4.6)."""
    x = T_d_ns - settle_s * NS
    return x - (x % (BAR_S * NS)) - BAR_S * NS


# ------------------------------------------------------------------------------------- slot identity (§6.2)
def valid_T_d0(T_d0_ns, settle_s=SETTLE_S):
    """(T_d0 - settle) mod 300 s = 0, so T_d is a candle close + settle (§6.2)."""
    return (T_d0_ns - settle_s * NS) % (BAR_S * NS) == 0


def T_d(T_d0_ns, i):
    """T_d(i) = T_d0 + 300 s * i (§6.2)."""
    return T_d0_ns + BAR_S * NS * i


def owning_slot(x_ns, T_d0_ns, N):
    """Slot i iff T_d(i) <= x < T_d(i+1); None (OFF_RUN) before T_d0 or at/after T_d(N) (§6.2)."""
    if not valid_T_d0(T_d0_ns):
        raise ValueError("T_d0 is off the decision grid")
    if x_ns < T_d0_ns or x_ns >= T_d(T_d0_ns, N):
        return None
    return (x_ns - T_d0_ns) // (BAR_S * NS)


def cycle_id(T_d0_ns, i, settle_s=SETTLE_S):
    """cycle_id(i) = (BTC/USD, t_exp(i)), t_exp(i) = T_d(i) - settle - 300 s (§6.2)."""
    return ("BTC/USD", T_d(T_d0_ns, i) - settle_s * NS - BAR_S * NS)


# ------------------------------------------------------------------------------ slot-anchored clocks (§5.3)
def cutoff_passed(T_d_ns, created_ns, W_s=W_S):
    """The proposal proceeds only if T_d + 120 s - created >= W (§5.3, §5.4)."""
    return T_d_ns + 120 * NS - created_ns >= W_s * NS


def approval_deadline(T_d_ns, created_ns):
    return min(created_ns + 120 * NS, T_d_ns + 120 * NS)


def expires_at(T_d_ns, issued_ns):
    return min(issued_ns + 60 * NS, T_d_ns + 180 * NS)


def ceiling(T_d_ns):
    return T_d_ns + 180 * NS
