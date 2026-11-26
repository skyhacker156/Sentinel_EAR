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


# ======================================================================================================
# Strike 1b-pre: proposal construction, policy predicates, Stage A shadow ledger, disposition.
# Governing text, unchanged row by row between frozen R4.2c and candidate R4.2g (COMPUTED):
#   §7.1, §7.2, §7.3 rows R1, R2, R4-R16 (not R3), §8.1, §8.1.1 rows (not the inserted EXIT-applicability row),
#   §3.3, §5.3, §5.4 rows used here (freshness, cutoff), §11.1 rows HOLD / NO_ACTION / REJECTED.
# DEFERRED to the amended freeze: R3 (redefined in R4.2g), the EXIT rule-applicability set (new row in
#   §8.1.1), and the SHADOW_EXPIRED condition (§11.1 row changed). Policy values: §7.3 and §7.4 text.
# ======================================================================================================
from . import exact as X  # noqa: E402

PENDING_FREEZE = "PENDING_FREEZE"


class PendingFreeze(Exception):
    """A disposition that needs requirements not yet frozen (R3; EXIT applicability; SHADOW_EXPIRED)."""


POLICY = {                                     # §7.3, §7.4, §8.1.1; increments DOCUMENTED, status UNVERIFIED
    "instrument": "BTC/USD",
    "price_increment": Fraction(1), "qty_increment": Fraction(1, 10000), "min_order_size": Fraction(1, 10000),
    "f_res": Fraction(25, 10000), "freshness_s": 15, "W_s": 90,
    "R5_band": Fraction(1, 100), "R7_cap": Fraction(150), "R8_cap": Fraction(300), "R12_floor": Fraction(450),
}

# BUY applicability DERIVED from unchanged rule rows: R9 (q_exit) and R15 (EXIT only while long) are EXIT
# rules by content; R12 says "reject BUY"; R14 is Stage B. R3 is applicable but deferred (redefined).
BUY_RULES = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R10", "R11", "R12", "R13", "R16"]


class ShadowLedger:
    """Stage A shadow ledger (§8.1, §8.1.1). Cash and BTC never change; no fills are simulated.
    A reservation exists only between 'every rule passes at checkpoint (a)' and SHADOW_EXPIRED in the same
    cycle, so it never crosses a slot. Fixture-backed ledgers (btc > 0, open authorization) are for tests."""

    def __init__(self, cash=Fraction(500), btc=Fraction(0), open_or_unresolved=False):
        cash = Fraction(cash)
        if (cash * 100).denominator != 1:
            raise ValueError("shadow cash must be an exact multiple of $0.01 (§8.1.1)")
        self.cash, self.btc, self.open_or_unresolved = cash, Fraction(btc), open_or_unresolved
        self.reserved_usd = Fraction(0)
        self.reserved_btc = Fraction(0)

    @property
    def cash_available(self):
        return self.cash - self.reserved_usd

    def reserve(self, proposal):
        if self.reserved_usd or self.reserved_btc:
            raise RuntimeError("a reservation already exists; reservations never cross a slot (§8.1)")
        if proposal["side"] == "BUY":
            self.reserved_usd = proposal["R"]
        else:
            self.reserved_btc = proposal["q"]

    def release(self):
        self.reserved_usd = Fraction(0)
        self.reserved_btc = Fraction(0)


def construct(side, bid, ask, ledger, policy=POLICY):
    """§7.1 step 3 with §7.2 and §8.1.1. BUY: L = ask rounded down; budget = min($150, cash_available);
    q = floor_qty(budget / (L (1 + f_res))); R = ceil_cent(q L (1 + f_res)). EXIT: L = bid rounded up;
    q_exit = floor_qty(shadow BTC - shadow_reserved_btc). No repricing or resizing afterwards (§7.2)."""
    L = X.round_limit(Fraction(ask) if side == "BUY" else Fraction(bid), side, policy["price_increment"])
    p = {"instrument": policy["instrument"], "side": side, "order_type": "LIMIT", "L": L,
         "rounding_inputs": {"bid": Fraction(bid), "ask": Fraction(ask),
                             "price_increment": policy["price_increment"],
                             "qty_increment": policy["qty_increment"], "min_order_size": policy["min_order_size"],
                             "f_res": policy["f_res"], "shadow_cash": ledger.cash,
                             "shadow_reserved": ledger.reserved_usd, "cash_available": ledger.cash_available,
                             "shadow_btc": ledger.btc, "shadow_reserved_btc": ledger.reserved_btc}}
    if side == "BUY":
        if L <= 0:
            raise ValueError("L must be > 0 (§8.1.1 assumes L > 0)")
        budget = min(policy["R7_cap"], ledger.cash_available)
        q = X.floor_to(budget / (L * (1 + policy["f_res"])), policy["qty_increment"])
        p.update(q=q, R=X.ceil_cent(q * L * (1 + policy["f_res"])))
        p["rounding_inputs"]["budget"] = budget
    elif side == "EXIT":
        p["q"] = X.floor_to(ledger.btc - ledger.reserved_btc, policy["qty_increment"])
    else:
        raise ValueError(f"side must be BUY or EXIT: {side!r}")
    return p


def _on_grid(x, inc):
    return (Fraction(x) / inc).denominator == 1


def rule_predicates(p, quote, created_ns, T_d_ns, ledger, policy=POLICY):
    """Every rule predicate whose §7.3 row is unchanged (all but R3). True = PASS.
    `quote` holds exact bid, ask and t of the checkpoint-(a) quote (validate.quote_values)."""
    bid, ask, qt = quote["bid"], quote["ask"], quote["t"]
    mid = (bid + ask) * Fraction(1, 2)
    R = p.get("R", Fraction(0))
    return {
        "R1": p["instrument"] == policy["instrument"],
        "R2": p["order_type"] == "LIMIT",                              # Stage A part of R2 (§7.3: "A: limit")
        "R4": 0 <= created_ns - qt <= policy["freshness_s"] * X.NS,    # §5.4: a quote dated after c fails
        "R5": abs(p["L"] - mid) <= policy["R5_band"] * mid,
        "R6": R <= ledger.cash_available,
        "R7": R <= policy["R7_cap"],
        "R8": ledger.btc * bid + R <= policy["R8_cap"],
        "R9": p["q"] <= ledger.btc - ledger.reserved_btc,
        "R10": p["q"] >= policy["min_order_size"] and _on_grid(p["q"], policy["qty_increment"])
               and _on_grid(p["L"], policy["price_increment"]),
        "R11": not ledger.open_or_unresolved,
        "R12": not (ledger.cash + ledger.btc * bid < policy["R12_floor"]),
        "R13": X.cutoff_passed(T_d_ns, created_ns, policy["W_s"]),
        "R15": not (ledger.btc < policy["min_order_size"]),            # EXIT only while long
        "R16": not ledger.open_or_unresolved,                          # FD-3
    }


def evaluate_buy(p, quote, created_ns, T_d_ns, ledger, policy=POLICY):
    """§7.1 step 4 for a BUY: EVERY applicable rule evaluated and recorded (not the first rejection).
    R3 is reported as PENDING_FREEZE."""
    if p["side"] != "BUY":
        raise PendingFreeze("EXIT rule applicability is new text in R4.2g (§8.1.1); evaluated after the freeze")
    pred = rule_predicates(p, quote, created_ns, T_d_ns, ledger, policy)
    return {r: (PENDING_FREEZE if r == "R3" else ("PASS" if pred[r] else "FAIL")) for r in BUY_RULES}


def disposition(rule_results):
    """§7.1 step 5: any FAIL -> REJECTED (all failing codes); all PASS -> SHADOW_EXPIRED at the ceiling.
    REJECTED needs only one FAIL, so it is decidable now (the failing set may still gain R3 after the freeze).
    An all-pass result needs R3 and the amended SHADOW_EXPIRED condition: PendingFreeze."""
    failing = [r for r, v in rule_results.items() if v == "FAIL"]
    if failing:
        return {"terminal": "REJECTED", "failing": failing,
                "failing_set_complete": PENDING_FREEZE not in rule_results.values()}
    raise PendingFreeze("all evaluated rules pass; R3 and the SHADOW_EXPIRED condition await the freeze")


def shadow_decision(validation, quote_tokens, quote_checks, created_ns, T_d_ns, ledger, closes=None,
                    policy=POLICY):
    """Integrated fixture path (§6.4 steps 5-7, §7.1): validation -> signal -> mapping -> proposal -> policy
    -> disposition. `validation` is validate.validate_bars output; `quote_checks` is validate.validate_quote."""
    out = {"V": validation["results"]}
    if validation["first_failure"] is not None:
        out["terminal"] = f"NO_DECISION ({validation['subreason']})"
        return out
    sig = decide_signal(closes)
    out.update(sig)
    m = mapping(sig["signal"], ledger.btc, policy["min_order_size"], ledger.open_or_unresolved)
    out["mapping"] = m
    if m == HOLD:
        out["terminal"] = "HOLD"
        return out
    if m != PROPOSAL:
        out["terminal"] = "NO_ACTION"
        return out
    out["Q"] = quote_checks
    if any(v == "FAIL" for v in quote_checks.values()):
        out["terminal"] = "NO_DECISION (QUOTE_INVALID)"
        return out
    from .validate import quote_values
    qv = quote_values(quote_tokens)
    p = construct(sig["signal"], qv["bid"], qv["ask"], ledger, policy)
    out["proposal"] = p
    rules = evaluate_buy(p, qv, created_ns, T_d_ns, ledger, policy)
    out["rules"] = rules
    out.update(disposition(rules))
    return out
