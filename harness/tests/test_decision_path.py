"""Strike 1b tests (R4.2i frozen, FD-5 v2): proposal construction (§7.2, §8.1.1), policy P-0.2 (§7.3), shadow ledger
(§8.1), disposition (§7.1 step 5) and the integrated fixture path (§6.4 steps 5-7).
FREEZE UPDATE (R4.2i, 5ec5d1b): cases that expected PendingFreeze (R3, EXIT applicability, SHADOW_EXPIRED) now
assert the frozen R4.2i outcome. Each such change is marked "freeze update"; no expected FAIL was removed.

Three kinds of case are kept apart, as the dispatch requires:
  PATH : normal construction from fixture inputs through the integrated path;
  INJ  : a runtime-injection-style BUY fixture (normal construction, constructed ledger/quote/time);
  EVAL : direct evaluator-level fixture (a constructed proposal or ledger the normal path cannot reach).
"""
import os
import sys
import unittest
from fractions import Fraction as F

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sl_pt_001 import decide as D      # noqa: E402
from sl_pt_001 import exact as X       # noqa: E402
from sl_pt_001 import validate as V    # noqa: E402
import fixtures_1b as FX               # noqa: E402

NS = X.NS
C = FX.T_D + 5 * NS                    # checkpoint (a) instant used by default (U44)


def path(last_delta="5", base="90000", quote=None, created=C, ledger=None, bars=None):
    bs = bars if bars is not None else FX.bars(last_delta, base)
    val = V.validate_bars(bs, FX.T_D)
    q = quote if quote is not None else FX.quote(t_ns=created - 2 * NS)
    closes = V.window_closes(val) if val["first_failure"] is None else None
    return D.shadow_decision(val, q, V.validate_quote(q), created, FX.T_D, ledger or D.ShadowLedger(), closes)


def failing(rules):
    return [r for r, v in rules.items() if v == "FAIL"]


class IntegratedPath(unittest.TestCase):
    def test_PATH_valid_BUY_SHADOW_EXPIRED_reserve_then_release(self):
        out = path("5")                                               # freeze update: was PendingFreeze
        self.assertEqual((out["terminal"], out["failing"]), ("SHADOW_EXPIRED", []))
        self.assertEqual(out["reserved"]["usd"], out["proposal"]["R"])  # reserved at (a) only on all-pass
        val = V.validate_bars(FX.bars("5"), FX.T_D)
        sig = D.decide_signal(V.window_closes(val))
        self.assertEqual((sig["D_prev"], sig["D_k"], sig["signal"]), (0, F(15), D.BUY))
        qv = V.quote_values(FX.quote(t_ns=C - 2 * NS))
        p = D.construct("BUY", qv["bid"], qv["ask"], D.ShadowLedger())
        L = F(90004)                                                   # ask 90004.75 rounded down (§7.2)
        q = X.floor_to(F(150) / (L * F("1.0025")), F("0.0001"))
        self.assertEqual((p["L"], p["q"], p["R"]), (L, q, X.ceil_cent(q * L * F("1.0025"))))
        self.assertEqual(p["q"], F("0.0016"))
        rules = D.evaluate(p, qv, C, FX.T_D, D.ShadowLedger())
        self.assertEqual(failing(rules), [])
        self.assertEqual(rules["R3"], "PASS")                         # freeze update: R3 now evaluated
        self.assertEqual(list(rules), D.BUY_RULES)                    # complete applicable set, numeric order

    def test_PATH_HOLD(self):
        out = path("0")
        self.assertEqual((out["signal"], out["mapping"], out["terminal"]), (D.HOLD, D.HOLD, "HOLD"))
        self.assertNotIn("proposal", out)

    def test_PATH_EXIT_while_flat_NO_ACTION(self):
        out = path("-5")
        self.assertEqual((out["signal"], out["terminal"]), (D.EXIT, "NO_ACTION"))

    def test_PATH_BUY_while_long_NO_ACTION_fixture_ledger(self):
        out = path("5", ledger=D.ShadowLedger(btc=F("0.01")))
        self.assertEqual((out["signal"], out["terminal"]), (D.BUY, "NO_ACTION"))

    def test_PATH_U8b_stale_quote_REJECTED_R4(self):
        out = path("5", quote=FX.quote(t_ns=C - 16 * NS))
        self.assertEqual((out["terminal"], out["failing"]), ("REJECTED", ["R4"]))
        self.assertNotIn("reserved", out)                             # no reservation when a rule fails

    def test_PATH_U81_insufficient_quantity_REJECTED_R10(self):
        out = path("5", base="2000000", quote=FX.quote("2000004", "2000005", t_ns=C - 2 * NS))
        self.assertEqual(out["proposal"]["q"], 0)
        self.assertEqual((out["terminal"], out["failing"]), ("REJECTED", ["R10"]))

    def test_PATH_U46_authorization_window_REJECTED_R13(self):
        created = FX.T_D + 30 * NS + 1
        out = path("5", created=created, quote=FX.quote(t_ns=created - 2 * NS))
        self.assertEqual((out["terminal"], out["failing"]), ("REJECTED", ["R13"]))

    def test_PATH_U45_cutoff_inclusive_passes(self):
        created = FX.T_D + 30 * NS
        out = path("5", created=created, quote=FX.quote(t_ns=created - 2 * NS))   # freeze update
        self.assertEqual(out["terminal"], "SHADOW_EXPIRED")

    def test_PATH_U47_created_late_REJECTED_R13(self):
        created = FX.T_D + 250 * NS
        out = path("5", created=created, quote=FX.quote(t_ns=created - 2 * NS))
        self.assertIn("R13", out["failing"])

    def test_PATH_invalid_data_NO_DECISION(self):
        gap = FX.bars("5")
        del gap[20]
        nan = FX.bars("5")
        nan[3] = dict(nan[3], c="NaN")
        dup = FX.bars("5")
        dup.insert(9, dict(dup[9], c="1"))
        for bs, want in ((gap, "NO_DECISION (DATA_GAP)"), (nan, "NO_DECISION (MALFORMED_VALUE)"),
                         (dup, "NO_DECISION (DATA_CONFLICT)"), (FX.bars("5", count=50), "NO_DECISION (DATA_GAP)")):
            with self.subTest(want=want):
                out = path(bars=bs)
                self.assertEqual(out["terminal"], want)
                self.assertNotIn("signal", out)

    def test_PATH_U80_invalid_quote_on_BUY_NO_DECISION_QUOTE_INVALID(self):
        out = path("5", quote=FX.quote(bid="0", t_ns=C - 2 * NS))
        self.assertEqual(out["terminal"], "NO_DECISION (QUOTE_INVALID)")
        self.assertNotIn("proposal", out)

    def test_PATH_U80_stale_but_valid_quote_REJECTED_not_QUOTE_INVALID(self):
        out = path("5", quote=FX.quote(t_ns=C - 60 * NS))
        self.assertEqual(out["terminal"], "REJECTED")

    def test_PATH_quote_not_validated_on_HOLD(self):
        out = path("0", quote=FX.quote(bid="0"))                     # §4.11: validated only for a proposal
        self.assertEqual(out["terminal"], "HOLD")
        self.assertNotIn("Q", out)

    def test_PATH_U18_quote_does_not_change_signal(self):
        a = path("0", quote=FX.quote("1", "2"))
        b = path("0", quote=FX.quote("99999", "100000"))
        self.assertEqual({k: a[k] for k in ("S20_k", "S50_k", "D_k", "signal")},
                         {k: b[k] for k in ("S20_k", "S50_k", "D_k", "signal")})


QV = {"bid": F("90004.25"), "ask": F("90004.75"), "t": C - 2 * NS}


def buy(ledger=None, **override):
    ledger = ledger or D.ShadowLedger()
    p = D.construct("BUY", QV["bid"], QV["ask"], ledger)
    p.update(override)
    return p, D.evaluate(p, QV, C, FX.T_D, ledger)


class Policy(unittest.TestCase):
    def test_INJ_R5_limit_far_from_mid(self):                       # X7
        qv = {"bid": F(90000), "ask": F(92000), "t": C - 2 * NS}
        lg = D.ShadowLedger()
        p = D.construct("BUY", qv["bid"], qv["ask"], lg)
        self.assertEqual(failing(D.evaluate(p, qv, C, FX.T_D, lg)), ["R5"])

    def test_INJ_R12_equity_below_450(self):
        self.assertEqual(failing(buy(D.ShadowLedger(cash=F("400.00")))[1]), ["R12"])

    def test_EVAL_X5_R12_equity_449(self):
        self.assertEqual(failing(buy(D.ShadowLedger(cash=F("449.00")))[1]), ["R12"])

    def test_EVAL_R8_exposure_limit_BUY_with_long_ledger(self):
        # Unreachable by the normal path (BUY while long maps to NO_ACTION); evaluator-level, as allowed.
        self.assertEqual(failing(buy(D.ShadowLedger(btc=F("0.01")))[1]), ["R8"])

    def test_EVAL_R8_with_R10_flat_G6_03(self):
        qv = {"bid": F(4000000), "ask": F(4000000), "t": C - 2 * NS}
        lg = D.ShadowLedger(btc=F("0.00009"))
        p = D.construct("BUY", qv["bid"], qv["ask"], lg)
        self.assertEqual(failing(D.evaluate(p, qv, C, FX.T_D, lg)), ["R8", "R10"])

    def test_EVAL_X4_R7_R_150_01(self):
        self.assertEqual(failing(buy(R=F("150.01"))[1]), ["R7"])

    def test_EVAL_R6_R_above_cash_available(self):
        lg = D.ShadowLedger()
        lg.reserved_usd = F(400)                                     # constructed state, test only
        p = D.construct("BUY", QV["bid"], QV["ask"], lg)
        p["R"] = F(120)
        self.assertEqual(failing(D.evaluate(p, QV, C, FX.T_D, lg)), ["R6"])

    def test_EVAL_X2_R1_unsupported_instrument(self):
        self.assertEqual(failing(buy(instrument="ETH/USD")[1]), ["R1"])

    def test_EVAL_R2_not_limit(self):
        self.assertEqual(failing(buy(order_type="MARKET")[1]), ["R2"])

    def test_EVAL_R11_R16_open_authorization(self):
        self.assertEqual(failing(buy(D.ShadowLedger(open_or_unresolved=True))[1]), ["R11", "R16"])

    def test_EVAL_EXIT_rules_X6_R9_R15(self):
        # freeze update: EXIT applicability is now frozen (R4.2i §8.1.1): R6, R7, R8, R12 do not apply.
        lg = D.ShadowLedger(btc=F("0.01"))
        p = D.construct("EXIT", QV["bid"], QV["ask"], lg)
        self.assertEqual((p["L"], p["q"]), (F(90005), F("0.01")))      # bid rounded UP; q_exit = held
        self.assertNotIn("R", p)                                       # EXIT has no R
        rules = D.evaluate(p, QV, C, FX.T_D, lg)
        self.assertEqual(list(rules), D.EXIT_RULES)
        self.assertEqual(failing(rules), [])                           # normal EXIT while long passes
        self.assertEqual(failing(D.evaluate(dict(p, q=F("0.02")), QV, C, FX.T_D, lg)), ["R9"])   # X6
        flat = D.ShadowLedger()
        pf = D.construct("EXIT", QV["bid"], QV["ask"], flat)
        self.assertEqual(failing(D.evaluate(pf, QV, C, FX.T_D, flat)), ["R10", "R15"])        # U121, G6-02

    def test_EVAL_X1_R3_malformed_proposal(self):
        # correction (run 5): exact failing sets; a malformed field fails R3 and every rule that reads it.
        p, _ = buy()
        cases = [({k: v for k, v in p.items() if k != "rounding_inputs"}, ["R3"]),       # U121 R3 case
                 (dict(p, L="90004"), ["R3", "R5", "R10"]),                           # L of the wrong type
                 ({k: v for k, v in p.items() if k != "R"}, ["R3", "R6", "R7", "R8"]),  # BUY without R
                 (dict(p, side="SELL"), ["R3", "R9", "R15"])]   # correction (run 6): every rule evaluated
        for broken, want in cases:
            with self.subTest(want=want):
                self.assertEqual(failing(D.evaluate(broken, QV, C, FX.T_D, D.ShadowLedger())), want)

    def test_EVAL_R3_q_zero_is_schema_valid(self):
        self.assertEqual(failing(buy(q=F(0), R=F(0))[1]), ["R10"])      # value bounds are R10's, not R3's

    def test_U28_freshness_boundaries(self):
        lg = D.ShadowLedger()
        for qt, want in ((C + 1, "FAIL"), (C - 15 * NS, "PASS"), (C - 15 * NS - 1, "FAIL"), (C, "PASS")):
            with self.subTest(age_ns=C - qt):
                qv = dict(QV, t=qt)
                p = D.construct("BUY", qv["bid"], qv["ask"], lg)
                self.assertEqual(D.evaluate(p, qv, C, FX.T_D, lg)["R4"], want)

    def test_U33_budget_divisible_and_one_cent_short(self):
        L, f = F(60000), F("1.0025")
        for cash in (F("150.00") , F("149.99")):
            with self.subTest(cash=cash):
                lg = D.ShadowLedger(cash=cash)
                p = D.construct("BUY", F(60000), F(60000), lg)
                self.assertEqual(p["q"], X.floor_to(min(F(150), cash) / (L * f), F("0.0001")))
                self.assertLessEqual(p["R"], min(F(150), cash))

    def test_U82_cash_available_below_150(self):
        lg = D.ShadowLedger(cash=F("100.00"))
        p = D.construct("BUY", QV["bid"], QV["ask"], lg)
        self.assertEqual(p["rounding_inputs"]["budget"], F(100))
        self.assertLessEqual(p["R"], F(100))

    def test_DERIVED_R_le_budget_by_construction(self):
        for ask in ("1", "99.99", "60000.01", "90004.75", "1496259", "3000000"):
            for cash in ("500.00", "150.00", "0.01", "37.42"):
                lg = D.ShadowLedger(cash=F(cash))
                p = D.construct("BUY", F(ask), F(ask), lg)
                self.assertLessEqual(p["R"], p["rounding_inputs"]["budget"])
                self.assertEqual((p["R"] * 100).denominator, 1)
                self.assertEqual((p["q"] / F("0.0001")).denominator, 1)


class Ledger(unittest.TestCase):
    def test_LEDGER_reservation_lifecycle_same_cycle(self):
        lg = D.ShadowLedger()
        p = D.construct("BUY", QV["bid"], QV["ask"], lg)
        lg.reserve(p)
        self.assertEqual((lg.reserved_usd, lg.cash_available), (p["R"], F(500) - p["R"]))
        with self.assertRaises(RuntimeError):
            lg.reserve(p)                                            # never two reservations
        lg.release()                                                 # SHADOW_EXPIRED in the same cycle
        self.assertEqual((lg.reserved_usd, lg.reserved_btc, lg.cash, lg.btc), (0, 0, F(500), 0))

    def test_LEDGER_no_fill_path_cash_and_btc_never_change(self):
        lg = D.ShadowLedger()
        self.assertFalse(any(hasattr(lg, a) for a in ("fill", "apply_fill", "submit", "settle")))
        self.assertEqual((lg.cash, lg.btc), (F(500), 0))

    def test_LEDGER_cash_on_cent_grid(self):
        with self.assertRaises(ValueError):
            D.ShadowLedger(cash=F("500.001"))

    def test_DISPOSITION_rules(self):
        self.assertEqual(D.disposition({"R1": "FAIL", "R3": "PASS", "R4": "FAIL"}),
                         {"terminal": "REJECTED", "failing": ["R1", "R4"]})
        self.assertEqual(D.disposition({"R1": "PASS", "R3": "PASS"}), {"terminal": "SHADOW_EXPIRED", "failing": []})


if __name__ == "__main__":
    unittest.main()
