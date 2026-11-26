"""SL-PT-001 CL-03 v2: exact-arithmetic check of (A) runtime BUY injection fixtures and
(B) evaluator-level unit-test cases (U121), over EVERY Stage A rule applicable to the side.
Author: Claude (harness author). Inputs: R4.2f sections 3.3, 5.3, 5.4, 7.2, 7.3, 8.1.1 and policy values.
NOT the harness and NOT the FD-6 auditor. Standard library only; Fraction only, no binary floating point.
Supersedes v1 (sl_pt_001_cl03_fixture_check.py), which checked only R1, R4-R8, R10, R12, R13 and
skipped the q < min_order_size region in its R8 bound (GPT G6-03).
Usage: py -3.12 -I sl_pt_001_cl03_fixture_check_v2.py      exit code 0 iff every expectation holds.
"""
from fractions import Fraction as F
import math, sys

PRICE_INC, QTY_INC, MIN_Q, F_RES = F(1), F("0.0001"), F("0.0001"), F("0.0025")
S = 10**9
BUY_RULES = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R10", "R11", "R12", "R13", "R16"]
EXIT_RULES = ["R1", "R2", "R3", "R4", "R5", "R9", "R10", "R11", "R13", "R15", "R16"]  # R6 R7 R8 R12 n/a (8.1.1)
FIELDS = ["instrument", "side", "order_type", "L", "q", "rounding_inputs"]  # + "R" for BUY

def floor_to(x, inc): return F(math.floor(x / inc)) * inc
def ceil_to(x, inc): return F(math.ceil(x / inc)) * inc
def ceil_cent(x): return F(math.ceil(x * 100), 100)
def on_grid(x, inc): return (x / inc).denominator == 1

def construct(side, quote, ledger):
    """Normal construction (7.2, 8.1.1)."""
    bid, ask = quote["bid"], quote["ask"]
    if side == "BUY":
        L = floor_to(ask, PRICE_INC)
        budget = min(F(150), ledger["cash"] - ledger["res_usd"])
        q = floor_to(budget / (L * (1 + F_RES)), QTY_INC)
        return dict(instrument="BTC/USD", side="BUY", order_type="LIMIT", L=L, q=q,
                    R=ceil_cent(q * L * (1 + F_RES)), rounding_inputs={})
    L = ceil_to(bid, PRICE_INC)
    q = floor_to(ledger["btc"] - ledger["res_btc"], QTY_INC)
    return dict(instrument="BTC/USD", side="EXIT", order_type="LIMIT", L=L, q=q, rounding_inputs={})

def evaluate(p, quote, ledger, Td, created):
    """Every rule applicable to p['side'] (7.3 as amended). Returns sorted list of FAIL codes."""
    bid, ask, qt = quote["bid"], quote["ask"], quote["t"]
    cash, res_usd, btc, res_btc, open_auth = (ledger[k] for k in ("cash", "res_usd", "btc", "res_btc", "open_auth"))
    side = p.get("side", "BUY")
    need = FIELDS + (["R"] if side == "BUY" else [])
    schema_ok = all(k in p for k in need)
    L, q, R = p.get("L", F(0)), p.get("q", F(0)), p.get("R", F(0))
    mid = (bid + ask) / 2
    r = {
        "R1": p.get("instrument") == "BTC/USD",
        "R2": p.get("order_type") == "LIMIT",
        "R3": schema_ok,
        "R4": 0 <= created - qt <= 15 * S,
        "R5": abs(L - mid) <= F("0.01") * mid,
        "R6": R <= cash - res_usd,
        "R7": R <= 150,
        "R8": btc * bid + R <= 300,
        "R9": q <= btc - res_btc,
        "R10": q >= MIN_Q and on_grid(q, QTY_INC) and on_grid(L, PRICE_INC),
        "R11": not open_auth,
        "R12": not (cash + btc * bid < 450),
        "R13": Td + 120 * S - created >= 90 * S,
        "R15": btc >= MIN_Q,       # EXIT only while long (3.3: flat := held BTC < min_order_size)
        "R16": not open_auth,      # FD-3: no proposal while an order or authorization is open/unresolved
    }
    rules = BUY_RULES if side == "BUY" else EXIT_RULES
    return sorted((k for k in rules if not r[k]), key=lambda c: int(c[1:]))

Td = 1_795_000_000 * S
Q = dict(bid=F("90000.25"), ask=F("90000.75"), t=Td + 2 * S)
FLAT = dict(cash=F(500), res_usd=F(0), btc=F(0), res_btc=F(0), open_auth=False)
LONG = dict(FLAT, btc=F("0.01"))
C = Td + 5 * S

CASES = []
def case(name, kind, side, expect, quote=Q, ledger=FLAT, created=C, mutate=None):
    CASES.append((name, kind, side, expect, quote, ledger, created, mutate))

# (A) runtime BUY injections: normal construction from fixture inputs, flat ledger
case("INJ R4 stale quote",      "injection", "BUY", ["R4"],  quote=dict(Q, t=C - 16 * S))
case("INJ R5 L far from mid",   "injection", "BUY", ["R5"],  quote=dict(Q, bid=F(90000), ask=F(92000)))
case("INJ R10 q floors to 0",   "injection", "BUY", ["R10"], quote=dict(Q, bid=F(2000000), ask=F(2000000)))
case("INJ R12 equity < 450",    "injection", "BUY", ["R12"], ledger=dict(FLAT, cash=F(400)))
case("INJ R13 cutoff",          "injection", "BUY", ["R13"], created=Td + 31 * S, quote=dict(Q, t=Td + 26 * S))
case("INJ R1 instrument (needs fixture field)", "injection", "BUY", ["R1"], mutate=dict(instrument="ETH/USD"))
# GPT G6-03 counterexample: flat, held 0.00009 BTC at $4,000,000 -> q = 0 -> R8 and R10 fail together
case("G6-03 R8 with R10 (flat)", "injection", "BUY", ["R8", "R10"],
     quote=dict(Q, bid=F(4000000), ask=F(4000000)), ledger=dict(FLAT, btc=F("0.00009")))

# (B) U121 evaluator-level cases: directly constructed proposal and/or ledger
case("U121 R2 not LIMIT",       "unit", "BUY", ["R2"],  mutate=dict(order_type="MARKET"))
case("U121 R3 field missing",   "unit", "BUY", ["R3"],  mutate=dict(_drop="rounding_inputs"))
case("U121 R6 R > cash_avail",  "unit", "BUY", ["R6"],  ledger=dict(FLAT, res_usd=F(400)), mutate=dict(R=F(120)))
case("U121 R7 R > 150",         "unit", "BUY", ["R7"],  mutate=dict(R=F(160)))
case("U121 R8 BUY while long",  "unit", "BUY", ["R8"],  ledger=LONG)
case("U121 R11+R16 open auth",  "unit", "BUY", ["R11", "R16"], ledger=dict(FLAT, open_auth=True))
case("U121 R9 q_exit > held",   "unit", "EXIT", ["R9"], ledger=LONG, mutate=dict(q=F("0.02")))
case("U121 R15 EXIT while flat","unit", "EXIT", ["R10", "R15"])            # G6-02: q_exit = 0
case("U121 EXIT pass (long)",   "unit", "EXIT", [], ledger=LONG)
case("U121 BUY pass (flat)",    "unit", "BUY", [])

ok = True
for name, kind, side, expect, quote, ledger, created, mutate in CASES:
    p = construct(side, quote, ledger)
    for k, v in (mutate or {}).items():
        if k == "_drop":
            p.pop(v)
        else:
            p[k] = v
    got = evaluate(p, quote, ledger, Td, created)
    flat = ledger["btc"] < MIN_Q
    good = got == expect
    ok &= good
    print(f"{'OK ' if good else 'BAD'} {kind:9} {side:4} flat={str(flat):5} q={p.get('q')} fails={got} expected={expect}  {name}")

# (C) R8 bound for a NORMALLY CONSTRUCTED flat BUY that passes R10 (DERIVED; exact over a grid)
worst = F(0)
for L in [F(p) for p in (1, 100, 90000, 1_000_000, 1_495_000, 1_496_000, 1_496_258, 1_496_259, 4_000_000)]:
    q = floor_to(F(150) / (L * (1 + F_RES)), QTY_INC)
    if q < MIN_Q:
        continue  # R10 fails; R8 may then fail too (G6-03) -- not a sole-R8 case
    exposure = (MIN_Q - F(1, 10**12)) * L + ceil_cent(q * L * (1 + F_RES))
    worst = max(worst, exposure)
sole_r8 = worst > 300
print(f"\nmax flat exposure with q >= min (exact): {worst}  -> sole-R8 failure reachable: {sole_r8}")
ok &= not sole_r8
print("RESULT:", "ALL EXPECTATIONS HOLD" if ok else "EXPECTATION FAILURE")
sys.exit(0 if ok else 1)
