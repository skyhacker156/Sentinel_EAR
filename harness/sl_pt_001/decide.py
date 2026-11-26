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
# Strike 1b: proposal construction, policy P-0.2, Stage A shadow ledger, disposition, full cycle.
# Governing text: frozen R4.2i (freeze 5ec5d1b), FD-5 v2. §6.4 steps 1-7, §7.1-7.3, §8.1, §8.1.1, §11.1.
# Commit timing (lock_clock_at, the ceiling wait) and TER serialization are Strike 2/3, not here.
# ======================================================================================================
from . import exact as X  # noqa: E402
from . import validate as V  # noqa: E402

POLICY = {                                     # §7.3, §7.4, §8.1.1; increments DOCUMENTED, status UNVERIFIED
    "instrument": "BTC/USD",
    "price_increment": Fraction(1), "qty_increment": Fraction(1, 10000), "min_order_size": Fraction(1, 10000),
    "f_res": Fraction(25, 10000), "freshness_s": 15, "W_s": 90,
    "R5_band": Fraction(1, 100), "R7_cap": Fraction(150), "R8_cap": Fraction(300), "R12_floor": Fraction(450),
}

# Applicability: R9 and R15 apply to EXIT only; R6, R7, R8 and R12 do not apply to EXIT (§8.1.1 R4.2i row);
# R14 is Stage B. Lists are in numeric rule order.
BUY_RULES = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R10", "R11", "R12", "R13", "R16"]
EXIT_RULES = ["R1", "R2", "R3", "R4", "R5", "R9", "R10", "R11", "R13", "R15", "R16"]


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
    q_exit = floor_qty(shadow BTC - shadow_reserved_btc); no R and no budget (§8.1.1 R4.2i row)."""
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


def schema_valid(p):
    """R3 (R4.2i): every field present with its type. Value bounds belong to R4-R13 (q = 0 is schema-valid)."""
    side = p.get("side")
    if side not in ("BUY", "EXIT"):
        return False
    need = {"instrument": str, "side": str, "order_type": str, "L": Fraction, "q": Fraction, "rounding_inputs": dict}
    if side == "BUY":
        need["R"] = Fraction
    if any(not isinstance(p.get(k), t) for k, t in need.items()):
        return False
    return side == "BUY" or "R" not in p


def rule_predicates(p, quote, created_ns, T_d_ns, ledger, policy=POLICY):
    """Every Stage A rule predicate (§7.3). True = PASS. `quote`: exact bid, ask, t of the checkpoint-(a) quote.
    Fail-closed (correction, run 5): a predicate whose input is missing or of the wrong type is FAIL, never an
    exception, so a malformed proposal is REJECTED with R3 (and any rule that reads the malformed field)."""
    bid, ask, qt = quote["bid"], quote["ask"], quote["t"]
    mid = (bid + ask) * Fraction(1, 2)

    def num(k):
        v = p[k]
        if not isinstance(v, Fraction):
            raise TypeError(k)
        return v

    preds = {
        "R1": lambda: p["instrument"] == policy["instrument"],
        "R2": lambda: p["order_type"] == "LIMIT",                      # Stage A part of R2 (§7.3, §11.6)
        "R3": lambda: schema_valid(p),
        "R4": lambda: 0 <= created_ns - qt <= policy["freshness_s"] * X.NS,   # §5.4: a quote dated after c fails
        "R5": lambda: abs(num("L") - mid) <= policy["R5_band"] * mid,
        "R6": lambda: num("R") <= ledger.cash_available,
        "R7": lambda: num("R") <= policy["R7_cap"],
        "R8": lambda: ledger.btc * bid + num("R") <= policy["R8_cap"],
        "R9": lambda: num("q") <= ledger.btc - ledger.reserved_btc,
        "R10": lambda: (num("q") >= policy["min_order_size"] and _on_grid(num("q"), policy["qty_increment"])
                        and _on_grid(num("L"), policy["price_increment"])),
        "R11": lambda: not ledger.open_or_unresolved,
        "R12": lambda: not (ledger.cash + ledger.btc * bid < policy["R12_floor"]),
        "R13": lambda: X.cutoff_passed(T_d_ns, created_ns, policy["W_s"]),
        "R15": lambda: not (ledger.btc < policy["min_order_size"]),    # EXIT only while long
        "R16": lambda: not ledger.open_or_unresolved,                  # FD-3
    }
    out = {}
    for r, f in preds.items():
        try:
            out[r] = bool(f())
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            out[r] = False
    return out


def evaluate(p, quote, created_ns, T_d_ns, ledger, policy=POLICY):
    """§7.1 step 4: EVERY applicable rule for the proposal's side, each recorded with its code."""
    side = p.get("side")
    if side == "BUY":
        rules = BUY_RULES
    elif side == "EXIT":
        rules = EXIT_RULES
    else:                                    # invalid side (R3 fails): evaluate every Stage A rule, skip none
        rules = sorted(set(BUY_RULES) | set(EXIT_RULES), key=lambda c: int(c[1:]))
    pred = rule_predicates(p, quote, created_ns, T_d_ns, ledger, policy)
    return {r: ("PASS" if pred[r] else "FAIL") for r in rules}


def disposition(rule_results):
    """§7.1 step 5: any FAIL -> REJECTED with all failing codes; all PASS -> SHADOW_EXPIRED (Stage A).
    The commit of SHADOW_EXPIRED happens at the ceiling (lock_clock_at >= ceiling): that timing is Strike 3."""
    failing = [r for r, v in rule_results.items() if v == "FAIL"]
    if failing:
        return {"terminal": "REJECTED", "failing": failing}
    return {"terminal": "SHADOW_EXPIRED", "failing": []}


def _propose(out, signal, quote_tokens, quote_checks, created_ns, T_d_ns, ledger, policy):
    out["Q"] = quote_checks
    if any(v == "FAIL" for v in quote_checks.values()):
        out["terminal"] = "NO_DECISION (QUOTE_INVALID)"
        return out
    qv = V.quote_values(quote_tokens)
    out["created"] = created_ns                                        # checkpoint (a), §5.3
    p = construct(signal, qv["bid"], qv["ask"], ledger, policy)
    out["proposal"] = p
    out["rules"] = evaluate(p, qv, created_ns, T_d_ns, ledger, policy)
    out.update(disposition(out["rules"]))
    if out["terminal"] == "SHADOW_EXPIRED":                            # §8.1.1: reserve only if every rule passes,
        ledger.reserve(p)                                              # release at SHADOW_EXPIRED, same cycle
        out["reserved"] = {"usd": ledger.reserved_usd, "btc": ledger.reserved_btc}
        ledger.release()
    return out


def shadow_decision(validation, quote_tokens, quote_checks, created_ns, T_d_ns, ledger, closes=None,
                    policy=POLICY):
    """Fixture path from already-validated bars (V3-V10 output): signal -> mapping -> Q -> proposal -> policy."""
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
    return _propose(out, sig["signal"], quote_tokens, quote_checks, created_ns, T_d_ns, ledger, policy)


V_ALL = ["V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9", "V10", "V11"]


def run_cycle(v12a, bars_header, bars_body, t_send_ns, t_recv_ns, quote_header, quote_body, T_d_ns, created_ns,
              ledger, store, policy=POLICY):
    """One Stage A cycle, §6.4 steps 1-7, from SUPPLIED observations and raw artifacts (no I/O here).
    `v12a` is boundary_check output (result, evidence, store_flag), or the string "FAIL" for a bare failure.
    `bars_header`/`bars_body` are the D-8 artifacts, or None/None if the bars request got no HTTP response.
    `store` is the bar store (validate.fold), mutated only by an admitted response (D-6).
    Returns a dict with every check result, the signal path and the terminal state."""
    out = {"V": {c: "NOT_EVALUATED" for c in V_ALL}, "V12a": None, "V12b": "NOT_EVALUATED",
           "Q": {q: "NOT_EVALUATED" for q in ("Q1", "Q2", "Q3", "Q4", "Q5")}, "transitions": []}
    v12a_result = v12a if isinstance(v12a, str) else v12a[0]
    out["V12a"] = v12a_result
    if v12a_result != "PASS":                                          # step 1: no fetch
        out["reason"] = "V12A_FAILED"
        out["terminal"] = "BOUNDARY_FAIL"
        return out
    if bars_header is None and bars_body is None:                      # step 2: no HTTP response (U112)
        out["reason"] = "FETCH_FAILED"
        out["terminal"] = "NO_DECISION (FETCH_FAILED)"
        return out
    try:                                                               # step 3: V12b before V1 (§5.6)
        _, fields = V.parse_header_artifact(bars_header)
        date = V.header_value(fields, "Date")
    except ValueError:
        date = None
    out["V12b"], out["D"], out["theta_low"], out["theta_high"] = V.clock_check(date, t_send_ns, t_recv_ns)
    if out["V12b"] != "PASS":
        out["reason"] = "V12B_FAILED"
        out["terminal"] = "BOUNDARY_FAIL"
        return out
    q = V.check_quote_response(quote_header, quote_body)               # step 4: quote fetched
    out["displayed_sizes"] = V.displayed_sizes(q["quote"])
    b = V.check_bars_response(bars_header, bars_body)                  # step 5: V1 ... V11
    v1 = "PASS" if b["V1"] == "PASS" and q["V1_quote"] == "PASS" else "FAIL"
    out["V"]["V1"], out["V"]["V2"] = v1, b["V2"]
    if v1 == "FAIL" or b["V2"] != "PASS":
        out["reason"] = "DATA_INVALID"                                 # V3-V11 NOT_EVALUATED (DATA_INVALID)
        if v1 == "FAIL":                                               # first failing check decides (§4.7)
            sub = b["subreason"] if b["V1"] == "FAIL" else "FETCH_FAILED"  # quote symbol failure (U95)
        else:
            sub = "INCOMPLETE_RESPONSE"                                # V2 (D-1)
        out["terminal"] = f"NO_DECISION ({sub})"
        return out
    val = V.validate_bars(b["bars"], T_d_ns)
    if V.admitted(b, val):
        out["transitions"] = V.fold(store, val, V.request_start_ns(T_d_ns), T_d_ns)
    v11 = V.check_V11(store, T_d_ns)
    out["V"].update(val["results"])
    out["V"]["V11"] = v11
    first = next((c for c in V_ALL[2:] if out["V"][c] == "FAIL"), None)
    if first is not None:
        sub = "SOURCE_REVISION" if first == "V11" else V.SUBREASON[first]
        out["terminal"] = f"NO_DECISION ({sub})"
        return out
    closes = V.window_closes(val)                                      # step 6
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
    return _propose(out, sig["signal"], q["quote"], V.validate_quote(q["quote"]), created_ns, T_d_ns,
                    ledger, policy)                                    # step 7
