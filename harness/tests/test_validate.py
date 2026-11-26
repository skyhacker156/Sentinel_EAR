"""Strike 1b-pre tests: V3-V10 (§4.7), Q1-Q5 (§4.11), V12b (§5.6). V1, V2, V11, V12a deferred to the freeze."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sl_pt_001 import exact as X       # noqa: E402
from sl_pt_001 import validate as V    # noqa: E402
import fixtures_1b as FX               # noqa: E402

NS = X.NS


def run(bs):
    return V.validate_bars(bs, FX.T_D)


class FixtureSanity(unittest.TestCase):
    def test_FIXTURE_iso_round_trip(self):
        for ns in (0, FX.T_D, FX.T_EXP, FX.T_D + 123456789, 951782400 * NS):
            self.assertEqual(X.parse_rfc3339_ns(FX.iso(ns)), ns)


class BarValidation(unittest.TestCase):
    def test_VALID_51_bars_all_pass_and_window(self):
        v = run(FX.bars())
        self.assertIsNone(v["first_failure"], v["results"])
        self.assertTrue(all(r == "PASS" for r in v["results"].values()))
        self.assertEqual(len(V.window_closes(v)), 51)
        self.assertEqual(v["deferred"], ["V1", "V2", "V11", "V12a"])

    def test_U17_forming_bar_excluded_and_recorded(self):
        v = run(FX.bars())
        self.assertEqual([t for t, _ in v["excluded"]], [FX.T_EXP + 300 * NS])

    def test_U6_one_bar_absent_in_window_DATA_GAP(self):
        bs = FX.bars()
        del bs[20]
        v = run(bs)
        self.assertEqual(v["results"]["V8"], "FAIL")
        self.assertEqual(v["subreason"], "DATA_GAP")

    def test_U8a_newest_completed_10_min_old_STALE_SERIES(self):
        bs = [b for b in FX.bars() if X.parse_rfc3339_ns(b["t"]) < FX.T_EXP - 300 * NS]   # drop t_exp bar
        v = run(bs)
        self.assertEqual(v["results"]["V7"], "FAIL")
        self.assertEqual(v["subreason"], "STALE_SERIES")

    def test_U7a_identical_duplicate_collapses_with_note(self):
        bs = FX.bars()
        bs.insert(10, dict(bs[10]))
        v = run(bs)
        self.assertIsNone(v["first_failure"])
        self.assertEqual(len(v["duplicate_notes"]), 1)

    def test_U7b_differing_duplicate_DATA_CONFLICT(self):
        bs = FX.bars()
        d = dict(bs[10])
        d["c"] = "90000.01"
        bs.insert(11, d)
        v = run(bs)
        self.assertEqual(v["results"]["V4"], "FAIL")
        self.assertEqual(v["subreason"], "DATA_CONFLICT")

    def test_U85_token_text_difference_is_a_difference(self):
        bs = FX.bars()
        d = dict(bs[10])
        d["c"] = d["c"] + ".0"                                   # same value, different token text
        bs.insert(11, d)
        self.assertEqual(run(bs)["results"]["V4"], "FAIL")       # not byte-identical -> differing duplicate

    def test_U12_reverse_order_sorted_same_result(self):
        a, b = run(FX.bars()), run(list(reversed(FX.bars())))
        self.assertEqual(a["results"], b["results"])
        self.assertEqual(V.window_closes(a), V.window_closes(b))

    def test_V3_offgrid_and_unparseable_t_MALFORMED(self):
        for mutate in ("2026-11-26T09:52:30Z", "2026-11-26T09:55:00", "garbage"):
            with self.subTest(t=mutate):
                bs = FX.bars()
                bs[5] = dict(bs[5], t=mutate)
                v = run(bs)
                self.assertEqual(v["results"]["V3"], "FAIL")
                self.assertEqual(v["subreason"], "MALFORMED_VALUE")

    def test_V9_numeric_validity_MALFORMED(self):
        for field, tok in (("c", "NaN"), ("o", "0"), ("vw", "-1"), ("v", "-0.1"), ("n", "2.5"), ("n", "-1"),
                           ("h", "Infinity"), ("l", "abc")):
            with self.subTest(field=field, tok=tok):
                bs = FX.bars()
                bs[7] = dict(bs[7], **{field: tok})
                v = run(bs)
                self.assertEqual(v["results"]["V9"], "FAIL")
                self.assertEqual(v["subreason"], "MALFORMED_VALUE")

    def test_V9_accepts_exponent_and_zero_volume(self):
        bs = FX.bars()
        bs[3] = dict(bs[3], v="0", n="0")
        bs[4] = dict(bs[4], c="9.0000e4", o="9e4", h="9e4", l="9e4", vw="9e4")
        self.assertIsNone(run(bs)["first_failure"])

    def test_U24_zero_volume_bar_retained_in_window(self):
        bs = FX.bars()
        bs[30] = dict(bs[30], v="0e0")
        v = run(bs)
        self.assertIsNone(v["first_failure"])
        self.assertIn("0e0", [b["v"] for _, b in v["window"]])

    def test_U111c_non_short_circuit_all_failures_recorded(self):
        bs = FX.bars()
        bs[2] = dict(bs[2], c="NaN")                              # V9
        bs = bs[:-2] + bs[-1:]                                    # drop t_exp bar: V7, V8, V10
        v = run(bs)
        r = v["results"]
        self.assertEqual((r["V7"], r["V8"], r["V9"], r["V10"]), ("FAIL", "FAIL", "FAIL", "FAIL"))
        self.assertEqual(v["first_failure"], "V7")
        self.assertEqual(v["subreason"], "STALE_SERIES")

    def test_U11_CONFLICT_50_bars_first_failure_is_V8_not_V10(self):
        # Frozen R4.2c U11 expects INSUFFICIENT_HISTORY. With 50 completed bars ending at t_exp, one of the
        # 51 required steps is missing, so V8 FAILS too, and V8 precedes V10 in §4.7: the first-failure rule
        # gives DATA_GAP. Fewer than 51 completed bars ALWAYS fails V8 (DERIVED), so V10 can never be the first
        # failure. Recorded as finding C-09; this test asserts §4.7's rule, not U11's expected sub-reason.
        v = run(FX.bars(count=50))
        self.assertEqual(v["results"]["V10"], "FAIL")
        self.assertEqual(v["results"]["V8"], "FAIL")
        self.assertEqual(v["subreason"], "DATA_GAP")

    def test_window_refused_on_failure(self):
        with self.assertRaises(ValueError):
            V.window_closes(run(FX.bars(count=50)))


class QuoteValidation(unittest.TestCase):
    def test_U80_each_Q_check_failing(self):
        cases = {"Q1": dict(bid="0"), "Q2": dict(ask="-1"), "Q3": dict(bid="90005", ask="90004"),
                 "Q4": dict(bs="-0.1"), "Q5": None}
        for q, kw in cases.items():
            with self.subTest(q=q):
                quote = FX.quote(**kw) if kw is not None else dict(FX.quote(), t="not-a-time")
                res = V.validate_quote(quote)
                self.assertEqual(res[q], "FAIL")
                # correction (run 3): a negative ask also fails Q3 (ask >= bid, bid > 0). The exact failing
                # set is asserted per case; nothing is loosened.
                want = {"Q1": ["Q1"], "Q2": ["Q2", "Q3"], "Q3": ["Q3"], "Q4": ["Q4"], "Q5": ["Q5"]}[q]
                self.assertEqual([k for k, v in res.items() if v == "FAIL"], want)

    def test_U80_missing_or_malformed_fields_and_absent_quote(self):
        q = FX.quote()
        del q["as"]
        self.assertEqual(V.validate_quote(q)["Q4"], "FAIL")
        self.assertEqual(V.validate_quote(dict(FX.quote(), bp="NaN"))["Q1"], "FAIL")
        self.assertEqual(set(V.validate_quote(None).values()), {"FAIL"})          # absent quote (U113b)
        self.assertEqual(set(V.validate_quote(FX.quote()).values()), {"PASS"})


class ClockCheck(unittest.TestCase):
    D = "Thu, 26 Nov 2026 10:01:02 GMT"

    def test_U79_theta_boundaries(self):
        Dns = V.parse_imf_fixdate_ns(self.D)
        # t_recv - t_send = 1 s. theta_high = D + 1 s - t_send; theta_low = D - t_recv.
        ok, *_ = V.clock_check(self.D, Dns - 1 * NS, Dns)                     # theta_high = +2 s exactly
        self.assertEqual(ok, "PASS")
        ok, *_ = V.clock_check(self.D, Dns - 1 * NS - 1, Dns - 1)            # theta_high = +2 s + 1 ns
        self.assertEqual(ok, "FAIL")
        ok, *_ = V.clock_check(self.D, Dns + 1 * NS, Dns + 2 * NS)           # theta_low = -2 s exactly
        self.assertEqual(ok, "PASS")
        ok, *_ = V.clock_check(self.D, Dns + 1 * NS + 1, Dns + 2 * NS + 1)   # theta_low = -2 s - 1 ns
        self.assertEqual(ok, "FAIL")

    def test_V12b_conditions_1_to_3(self):
        Dns = V.parse_imf_fixdate_ns(self.D)
        self.assertEqual(V.clock_check(None, Dns, Dns)[0], "FAIL")                       # 1: absent
        self.assertEqual(V.clock_check("Wed, 26 Nov 2026 10:01:02 GMT", Dns, Dns)[0], "FAIL")   # 1: weekday
        self.assertEqual(V.clock_check(self.D, Dns, Dns - 1)[0], "FAIL")                 # 2: negative RTT
        self.assertEqual(V.clock_check(self.D, Dns - 1 * NS, Dns + 2 * NS)[0], "FAIL")   # 3: RTT = 3 s
        r, d, lo, hi = V.clock_check(self.D, Dns, Dns + NS // 2)
        self.assertEqual((r, d, lo, hi), ("PASS", Dns, -(NS // 2), NS))

    def test_V12b_probe_date_parses(self):
        self.assertEqual(V.parse_imf_fixdate_ns("Thu, 26 Nov 2026 03:13:20 GMT"),
                         X.parse_rfc3339_ns("2026-11-26T03:13:20Z"))


if __name__ == "__main__":
    unittest.main()
