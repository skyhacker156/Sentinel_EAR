"""SL-PT-001 CL-03: exact-arithmetic feasibility check of Stage A BUY injection fixtures.
Author: Claude (harness author). Inputs: R4.2c sections 3.3, 5.3, 5.4, 7.2, 7.3, 8.1.1 and policy values only.
NOT the harness, NOT the FD-6 auditor. Standard library only; Fraction only (no float).
Usage: py -3.12 -I sl_pt_001_cl03_fixture_check.py
"""
from fractions import Fraction as F
import math

PRICE_INC, QTY_INC, MIN_Q, F_RES = F(1), F("0.0001"), F("0.0001"), F("0.0025")
S = 10**9  # ns per second

def floor_to(x, inc): return F(math.floor(x / inc)) * inc
def ceil_cent(x): return F(math.ceil(x * 100), 100)

def evaluate(fx):
    """BUY at checkpoint (a). Returns (q, R, {rule: PASS/FAIL}) for rules applicable to a Stage A BUY."""
    bid, ask = F(fx["bid"]), F(fx["ask"])
    cash, btc, reserved = F(fx["cash"]), F(fx["btc"]), F(0)  # reservations never cross a slot (8.1)
    L = floor_to(ask, PRICE_INC)                          # 7.2 BUY: ask rounded down
    cash_avail = cash - reserved
    budget = min(F(150), cash_avail)
    q = floor_to(budget / (L * (1 + F_RES)), QTY_INC)    # 8.1.1
    R = ceil_cent(q * L * (1 + F_RES))
    mid = (bid + ask) / 2
    Td, created, qt = fx["T_d"], fx["created"], fx["quote_t"]
    r = {
        "R1": fx.get("instrument", "BTC/USD") == "BTC/USD",
        "R4": 0 <= created - qt <= 15 * S,
        "R5": abs(L - mid) <= F("0.01") * mid,
        "R6": R <= cash_avail,
        "R7": R <= 150,
        "R8": btc * bid + R <= 300,
        "R10": q >= MIN_Q and (q / QTY_INC).denominator == 1 and (L / PRICE_INC).denominator == 1,
        "R12": not (cash + btc * bid < 450),
        "R13": Td + 120 * S - created >= 90 * S,
    }
    flat = btc < MIN_Q  # 3.3
    return flat, q, R, {k: ("PASS" if v else "FAIL") for k, v in r.items()}

Td = 1_795_000_000 * S
base = dict(bid="90000.25", ask="90000.75", cash="500.00", btc="0", T_d=Td, created=Td + 5 * S, quote_t=Td + 2 * S)
FIXTURES = {
    "R4":  dict(base, quote_t=Td + 5 * S - 16 * S),        # quote 16 s old at (a)
    "R5":  dict(base, bid="90000", ask="92000"),            # L = 92000, mid 91000: 1000 > 910
    "R10": dict(base, bid="2000000", ask="2000000"),        # q floors to 0 < 0.0001
    "R12": dict(base, cash="400.00"),                       # equity 400 < 450
    "R13": dict(base, created=Td + 31 * S, quote_t=Td + 26 * S),  # T_d+120-created = 89 s < 90
    "R1":  dict(base, instrument="ETH/USD"),                # only if the fixture may set instrument
}

ok = True
for intended, fx in FIXTURES.items():
    flat, q, R, res = evaluate(fx)
    fails = sorted(k for k, v in res.items() if v == "FAIL")
    single = flat and fails == [intended]
    ok &= single
    print(f"{intended:4} flat={flat} q={q} R={R} fails={fails} -> {'SINGLE-RULE OK' if single else 'NOT SINGLE'}")

# Unreachability by construction (DERIVED, spot-checked here over a price grid):
print("\nR6/R7: R <= budget <= min(150, cash_available) by construction; R8 while flat:")
worst = F(0)
for L in [F(p) for p in (1, 100, 10_000, 90_000, 1_000_000, 1_495_000, 1_496_000, 1_496_258)]:
    q = floor_to(F(150) / (L * (1 + F_RES)), QTY_INC)
    if q < MIN_Q:
        continue
    R = ceil_cent(q * L * (1 + F_RES))
    btc_max_flat = MIN_Q - F(1, 10**12)          # just below min_order_size
    exposure = btc_max_flat * L + R
    worst = max(worst, exposure)
    assert R <= 150
print(f"max (flat BTC x bid + R) over grid with q >= min: {worst.numerator // worst.denominator} + {worst - worst.numerator // worst.denominator} (exact) -> R8 FAIL reachable while flat: {worst > 300}")
print("\nRESULT:", "ALL FIVE+ INTENDED-RULE FIXTURES CONSTRUCTIBLE" if ok else "SOME FIXTURE FAILS")
