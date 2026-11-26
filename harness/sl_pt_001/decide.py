"""SL-PT-001 Stage A harness: signal and signal-to-action mapping (Strike 1a portion of decide.py).

Governing text (frozen R4.2c; byte-identical in candidate R4.2f, COMPUTED): §3.1, §3.2, §3.3, §3.4.
Also relied on, unchanged: §11.1 (HOLD / NO_ACTION qualifying conditions), used to settle §3.3 row precedence.
Not in this increment: proposal sizing (§8.1.1) and policy P-0.2 (§7.3), whose sections changed in R4.2f.

Exactness: every input is a fractions.Fraction (exact.parse_number_token). No binary floating point (§5.1).
Quote independence (§3.4, U18): no function here accepts any quote field.
"""
from fractions import Fraction

WINDOW = 51                       # k-50 ... k (§3.1)

BUY, EXIT, HOLD = "BUY", "EXIT", "HOLD"
PROPOSAL = "PROPOSAL"
NO_ACTION = "NO_ACTION"
NO_ACTION_BLOCKED = "NO_ACTION (BLOCKED_OPEN_ORDER)"   # TER-1 contract v1 spelling (CONTRACT CHOICE)


def indicators(closes):
    """S20 and S50 at k and k-1, and D(k-1), D(k) (§3.1).

    `closes` are the exact closes of the 51 consecutive completed candles k-50 ... k, oldest first.
    D(k) = 5*S20(k) - 2*S50(k); sign(D) = sign(SMA20 - SMA50) because SMA20 - SMA50 = D/100 (DERIVED).
    """
    closes = list(closes)
    if len(closes) != WINDOW:
        raise ValueError(f"exactly {WINDOW} closes are required (k-50 ... k); got {len(closes)}")
    for c in closes:
        if not isinstance(c, Fraction):
            raise TypeError("closes must be exact Fractions")
    k = WINDOW - 1
    S20_k = sum(closes[k - 19:k + 1], Fraction(0))
    S50_k = sum(closes[k - 49:k + 1], Fraction(0))
    S20_prev = sum(closes[k - 20:k], Fraction(0))
    S50_prev = sum(closes[k - 50:k], Fraction(0))
    return {
        "S20_k": S20_k, "S50_k": S50_k, "S20_prev": S20_prev, "S50_prev": S50_prev,
        "D_prev": 5 * S20_prev - 2 * S50_prev,
        "D_k": 5 * S20_k - 2 * S50_k,
    }


def crossover(D_prev, D_k):
    """FD-2, literal (§3.2): BUY iff D(k-1) <= 0 and D(k) > 0; EXIT iff D(k-1) >= 0 and D(k) < 0; else HOLD."""
    if D_prev <= 0 and D_k > 0:
        return BUY
    if D_prev >= 0 and D_k < 0:
        return EXIT
    return HOLD


def is_flat(held_btc, min_order_size):
    """Flat := held BTC < min_order_size (§3.3). min_order_size comes from the policy file (UNVERIFIED)."""
    return Fraction(held_btc) < Fraction(min_order_size)


def mapping(signal, held_btc, min_order_size, open_or_unresolved):
    """Signal-to-action mapping (§3.3).

    Row precedence (DERIVED from §11.1, not chosen here): a HOLD signal always maps to HOLD. §11.1 qualifies
    NO_ACTION only with signal in {BUY, EXIT}, so mapping a HOLD signal to NO_ACTION (BLOCKED_OPEN_ORDER)
    would make a correct cycle non-qualifying. The 'any signal' blocked row therefore applies to BUY and EXIT.
    In Stage A no order or authorization is ever open (R16 vacuous), so that row is reachable only in tests.
    """
    if signal not in (BUY, EXIT, HOLD):
        raise ValueError(f"unknown signal: {signal!r}")
    if signal == HOLD:
        return HOLD
    if open_or_unresolved:
        return NO_ACTION_BLOCKED
    flat = is_flat(held_btc, min_order_size)
    if signal == BUY:
        return PROPOSAL if flat else NO_ACTION       # BUY while long: NO_ACTION (CF-2)
    return NO_ACTION if flat else PROPOSAL           # EXIT while flat: NO_ACTION (CF-2)


def decide_signal(closes):
    """Indicators plus signal for one window. Returns the indicator dict with 'signal' added."""
    out = indicators(closes)
    out["signal"] = crossover(out["D_prev"], out["D_k"])
    return out
