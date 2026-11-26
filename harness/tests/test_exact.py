"""Strike 1a tests: exact values, rounding points, instants, completed candles, slot identity.
Test names carry the R4.2c §14 test ID they execute (or EXACT-/TIME- for supporting checks)."""
import os
import random
import sys
import unittest
from fractions import Fraction as F

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from sl_pt_001 import exact as X  # noqa: E402

NS = X.NS


def iso(text):
    return X.parse_rfc3339_ns(text)


class NumberTokens(unittest.TestCase):
    def test_EXACT_valid_tokens(self):
        cases = {"0": F(0), "-0": F(0), "60000.25": F(6000025, 100), "6.0001e4": F(60001),
                 "1E-2": F("0.01"), "-0.5e-3": F(-5, 10000), "123": F(123), "0.0": F(0), "0e0": F(0)}
        for tok, want in cases.items():
            with self.subTest(tok=tok):
                self.assertEqual(X.parse_number_token(tok), want)
                self.assertIsInstance(X.parse_number_token(tok), F)

    def test_U87_malformed_tokens(self):
        for tok in ["NaN", "nan", "Infinity", "-Infinity", "inf", "+1", "01", ".5", "1.", "1e", "1e+",
                    "0x10", "1_000", " 1", "1 ", "", "--1", "1.2.3", "١٢"]:
            with self.subTest(tok=tok):
                with self.assertRaises(X.MalformedValue):
                    X.parse_number_token(tok)
        with self.assertRaises(X.MalformedValue):
            X.parse_number_token(1.5)                      # a non-token (already-decoded number) is refused

    def test_U87_long_mantissa_and_extreme_exponents_are_exact(self):
        long = "123456789012345678901234567890.123456789012345678901234567890"
        value = X.parse_number_token(long)
        # correction (run 1): canonical output drops the trailing zero; compare exact values, then the canonical form
        self.assertEqual(X.parse_number_token(X.to_decimal_string(value)), value)
        self.assertEqual(X.to_decimal_string(value), long.rstrip("0"))
        self.assertEqual(X.parse_number_token("1e400"), F(10) ** 400)          # a double would overflow
        self.assertEqual(X.parse_number_token("1e-400"), F(1, 10 ** 400))      # a double would underflow
        self.assertNotEqual(X.parse_number_token("1e-400"), 0)

    def test_U24_zero_volume_by_exact_value(self):
        for tok in ["0", "0.0", "0e0", "-0"]:
            with self.subTest(tok=tok):
                self.assertTrue(X.is_zero_volume(tok))
        self.assertFalse(X.is_zero_volume("0.00000001"))

    def test_U25_exact_sums_where_binary_sums_differ(self):
        toks = ["0.1", "0.2", "0.3", "1e-1", "2E-1"]
        exact_sum = sum((X.parse_number_token(t) for t in toks), F(0))
        self.assertEqual(exact_sum, F(9, 10))
        self.assertEqual(X.to_decimal_string(exact_sum), "0.9")


class RoundingPoints(unittest.TestCase):
    def test_EXACT_floor_q_to_quantity_increment(self):
        inc = F("0.0001")
        self.assertEqual(X.floor_to(F("0.00169999"), inc), F("0.0016"))
        self.assertEqual(X.floor_to(F("0.0016"), inc), F("0.0016"))
        self.assertEqual(X.floor_to(F("0.00009999"), inc), 0)

    def test_EXACT_limit_conservative_rounding(self):
        one = F(1)
        self.assertEqual(X.round_limit(F("90000.75"), "BUY", one), F(90000))   # BUY rounds down
        self.assertEqual(X.round_limit(F("90000.25"), "EXIT", one), F(90001))  # EXIT rounds up
        self.assertEqual(X.round_limit(F(90000), "BUY", one), F(90000))
        self.assertEqual(X.round_limit(F(90000), "EXIT", one), F(90000))
        with self.assertRaises(ValueError):
            X.round_limit(F(1), "SELL", one)

    def test_EXACT_ceil_cent(self):
        self.assertEqual(X.ceil_cent(F("144.3601")), F("144.37"))
        self.assertEqual(X.ceil_cent(F("144.36")), F("144.36"))

    def test_EXACT_display_8dp_round_half_even(self):
        self.assertEqual(X.display_8dp(F("0.000000005")), "0.00000000")      # half -> even (0)
        self.assertEqual(X.display_8dp(F("0.000000015")), "0.00000002")      # half -> even (2)
        self.assertEqual(X.display_8dp(F("0.0000000151")), "0.00000002")
        self.assertEqual(X.display_8dp(F("-0.000000015")), "-0.00000002")
        self.assertEqual(X.display_8dp(F(1, 3)), "0.33333333")

    def test_EXACT_decimal_string_refuses_non_terminating(self):
        self.assertEqual(X.to_decimal_string(F("-12.500")), "-12.5")
        with self.assertRaises(ValueError):
            X.to_decimal_string(F(1, 3))


class Instants(unittest.TestCase):
    def test_TIME_rfc3339_exact(self):
        self.assertEqual(iso("1970-01-01T00:00:00Z"), 0)
        self.assertEqual(iso("2000-01-01T00:00:00Z"), 946684800 * NS)
        self.assertEqual(iso("2000-01-01T01:00:00+01:00"), 946684800 * NS)
        self.assertEqual(iso("1999-12-31T19:00:00-05:00"), 946684800 * NS)
        self.assertEqual(iso("2026-11-26T03:13:19.7553616Z") % NS, 755361600)     # probe form, 7 digits
        self.assertEqual(iso("2026-11-26T03:13:19.123456789Z") % NS, 123456789)   # 9 digits kept
        self.assertEqual(iso("2024-02-29T00:00:00z"), iso("2024-02-29T00:00:00Z"))

    def test_TIME_rfc3339_malformed(self):
        for t in ["2026-11-26T03:13:19.1234567891Z",   # 10 fractional digits
                  "2026-11-26T03:13:19",               # no zone designator
                  "2026-11-26 03:13:19Z", "2023-02-29T00:00:00Z", "2026-13-01T00:00:00Z",
                  "2026-11-26T24:00:00Z", "2026-11-26T03:13:60Z",   # leap second: fail-closed reading
                  "2026-11-26T03:13:19.Z", "2026-11-26T03:13:19+0100", "garbage", ""]:
            with self.subTest(t=t):
                with self.assertRaises(X.MalformedValue):
                    iso(t)


T_D_1001 = iso("2026-11-26T10:01:00Z")


class CompletedCandles(unittest.TestCase):
    def test_U5_late_invocation_keeps_slot_and_rule(self):
        T_d0 = T_D_1001
        x = iso("2026-11-26T10:05:30Z")
        self.assertEqual(X.owning_slot(x, T_d0, 30), 0)                     # same slot, T_d = 10:01
        self.assertFalse(X.is_completed(iso("2026-11-26T10:00:00Z"), X.T_d(T_d0, 0)))
        self.assertEqual(X.t_exp_ns(T_D_1001), iso("2026-11-26T09:55:00Z"))
        self.assertTrue(X.is_completed(iso("2026-11-26T09:55:00Z"), T_D_1001))

    def test_U17_bar_past_settle_is_excluded(self):
        t = iso("2026-11-26T09:55:00Z") + 1                                    # t + 360 s > T_d by 1 ns
        self.assertFalse(X.is_completed(t, T_D_1001))

    def test_U78_boundary_inclusive_then_one_ns_earlier(self):
        t = T_D_1001 - 360 * NS
        self.assertTrue(X.is_completed(t, T_D_1001))                          # t + 360 s = T_d: included
        self.assertFalse(X.is_completed(t, T_D_1001 - 1))                     # T_d one ns earlier: excluded

    def test_U89_end_labelled_bars_never_used_before_close(self):
        # Under end-labelling a bar labelled t closes at t; under start-labelling at t + 300 s.
        # Every bar the rule accepts has closed under BOTH readings, settle included (conservative).
        for offset_s in range(-3600, 3600, 300):
            t = T_D_1001 - 360 * NS + offset_s * NS
            if X.is_completed(t, T_D_1001):
                self.assertLessEqual(t + 300 * NS, T_D_1001 - 60 * NS)       # start-labelled close + settle
                self.assertLessEqual(t, T_D_1001 - 60 * NS)                   # end-labelled close + settle


class SlotIdentity(unittest.TestCase):
    def test_U52_invocation_exactly_at_next_T_d(self):
        T_d0 = T_D_1001
        self.assertEqual(X.owning_slot(X.T_d(T_d0, 1), T_d0, 30), 1)
        self.assertEqual(X.owning_slot(X.T_d(T_d0, 1) - 1, T_d0, 30), 0)

    def test_TIME_off_run_and_grid(self):
        T_d0 = T_D_1001
        self.assertIsNone(X.owning_slot(T_d0 - 1, T_d0, 30))                  # before T_d0
        self.assertIsNone(X.owning_slot(X.T_d(T_d0, 30), T_d0, 30))           # at T_d(N)
        self.assertEqual(X.owning_slot(X.T_d(T_d0, 30) - 1, T_d0, 30), 29)
        self.assertTrue(X.valid_T_d0(T_d0))
        self.assertFalse(X.valid_T_d0(iso("2026-11-26T10:00:00Z")))
        with self.assertRaises(ValueError):
            X.owning_slot(T_d0, T_d0 + NS, 30)
        self.assertEqual(X.cycle_id(T_d0, 2), ("BTC/USD", X.T_d(T_d0, 2) - 360 * NS))

    def test_U53_property_slot_anchored_clocks(self):
        seed = 20261126
        rng = random.Random(seed)
        print(f"\n[U53] property seed recorded: {seed}")
        T = T_D_1001
        for _ in range(20000):
            created = T + rng.randrange(0, 300 * NS)
            dl = X.approval_deadline(T, created)
            self.assertEqual(dl, T + 120 * NS)                                 # invariant 1
            if dl >= created:
                issued = created + rng.randrange(0, dl - created + 1)
                exp = X.expires_at(T, issued)
                self.assertEqual(exp, issued + 60 * NS)                        # invariant 2
                self.assertLessEqual(exp, T + 180 * NS)
                self.assertLess(exp, X.T_d(T, 1))
            if X.cutoff_passed(T, created):
                self.assertGreaterEqual(dl - created, 90 * NS)                 # invariant 3
            self.assertLess(X.ceiling(T), X.T_d(T, 1))                         # invariant 4

    def test_U53_cutoff_boundaries(self):
        T = T_D_1001
        self.assertTrue(X.cutoff_passed(T, T + 30 * NS))                      # exactly 90 s left: passes
        self.assertFalse(X.cutoff_passed(T, T + 30 * NS + 1))


if __name__ == "__main__":
    unittest.main()
