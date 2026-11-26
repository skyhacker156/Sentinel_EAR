"""Strike 1a tests: indicators, FD-2 crossover, signal-to-action mapping, quote independence, determinism."""
import inspect
import json
import os
import subprocess
import sys
import unittest
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from sl_pt_001 import decide as D  # noqa: E402
from sl_pt_001 import exact as X   # noqa: E402

MIN_Q = F("0.0001")


def closes_with_last(x, base="100"):
    """51 closes: 50 at base, the newest at base + x. Then D(k-1) = 0 and D(k) = 3x (DERIVED)."""
    b = X.parse_number_token(base)
    return [b] * 50 + [b + x]


class Crossover(unittest.TestCase):
    def test_U1_minus4_to_minus1_hold(self):
        self.assertEqual(D.crossover(F(-4), F(-1)), D.HOLD)

    def test_U2_minus3_to_plus2_buy(self):
        self.assertEqual(D.crossover(F(-3), F(2)), D.BUY)

    def test_U3_plus3_to_minus2_exit(self):
        self.assertEqual(D.crossover(F(3), F(-2)), D.EXIT)

    def test_U4a_minus1_to_0_hold(self):
        self.assertEqual(D.crossover(F(-1), F(0)), D.HOLD)

    def test_U4b_0_to_plus1_buy(self):
        self.assertEqual(D.crossover(F(0), F(1)), D.BUY)

    def test_U4c_plus1_0_plus1_buy_at_third_step(self):
        seq = [F(1), F(0), F(1)]
        self.assertEqual([D.crossover(a, b) for a, b in zip(seq, seq[1:])], [D.HOLD, D.BUY])

    def test_U4d_minus1_0_minus1_exit_at_third_step(self):
        seq = [F(-1), F(0), F(-1)]
        self.assertEqual([D.crossover(a, b) for a, b in zip(seq, seq[1:])], [D.HOLD, D.EXIT])

    def test_EC3_EC4(self):
        seq = [F(-1), F(0), F(1)]
        self.assertEqual([D.crossover(a, b) for a, b in zip(seq, seq[1:])], [D.HOLD, D.BUY])
        self.assertEqual(D.crossover(F(0), F(0)), D.HOLD)

    def test_FD2_exhaustive_and_exclusive_on_sign_grid(self):
        for a in (F(-1), F(0), F(1)):
            for b in (F(-1), F(0), F(1)):
                s = D.crossover(a, b)
                buy = a <= 0 < b
                exit_ = a >= 0 > b
                self.assertFalse(buy and exit_)
                self.assertEqual(s, D.BUY if buy else D.EXIT if exit_ else D.HOLD)


class Indicators(unittest.TestCase):
    def test_EXACT_indicator_values(self):
        out = D.indicators(closes_with_last(F(1)))
        self.assertEqual(out["S20_k"], F(2001))
        self.assertEqual(out["S50_k"], F(5001))
        self.assertEqual(out["S20_prev"], F(2000))
        self.assertEqual(out["S50_prev"], F(5000))
        self.assertEqual(out["D_prev"], 0)
        self.assertEqual(out["D_k"], F(3))
        self.assertEqual((out["S20_k"] / 20 - out["S50_k"] / 50) * 100, out["D_k"])   # D = 100*(SMA20 - SMA50)

    def test_EXACT_end_to_end_signals(self):
        self.assertEqual(D.decide_signal(closes_with_last(F("0.01")))["signal"], D.BUY)
        self.assertEqual(D.decide_signal(closes_with_last(F("-0.01")))["signal"], D.EXIT)
        self.assertEqual(D.decide_signal(closes_with_last(F(0)))["signal"], D.HOLD)

    def test_U4e_exact_equality_where_binary_arithmetic_differs(self):
        tok = "1.1"     # correction (run 1): "0.1" gave float D = 0 too, so it did not establish the premise
        closes = [X.parse_number_token(tok)] * 51
        out = D.decide_signal(closes)
        self.assertEqual(out["D_prev"], 0)
        self.assertEqual(out["D_k"], 0)
        self.assertEqual(out["signal"], D.HOLD)
        # Premise check only (test code, never harness code): the binary-float route does NOT give 0.
        fs20 = sum([float(tok)] * 20)
        fs50 = sum([float(tok)] * 50)
        self.assertNotEqual(5 * fs20 - 2 * fs50, 0.0)

    def test_U11_history_precondition(self):
        for n in (50, 52, 0):
            with self.subTest(n=n):
                with self.assertRaises(ValueError):
                    D.indicators([F(100)] * n)
        with self.assertRaises(TypeError):
            D.indicators([100] * 51)                                # ints, not exact token values

    def test_U18_quote_independence(self):
        for fn in (D.indicators, D.crossover, D.decide_signal):
            names = [p.lower() for p in inspect.signature(fn).parameters]
            self.assertFalse(any(k in n for n in names for k in ("quote", "bid", "ask", "bp", "ap")), fn)
        c = closes_with_last(F("0.37"))
        self.assertEqual(D.decide_signal(c), D.decide_signal(list(c)))


class Mapping(unittest.TestCase):
    def test_EXACT_mapping_table(self):
        flat, long_ = F(0), F("0.0001")                             # long at exactly min_order_size
        cases = [
            (D.BUY, flat, False, D.PROPOSAL), (D.BUY, long_, False, D.NO_ACTION),
            (D.EXIT, long_, False, D.PROPOSAL), (D.EXIT, flat, False, D.NO_ACTION),
            (D.HOLD, flat, False, D.HOLD), (D.HOLD, long_, False, D.HOLD),
            (D.BUY, flat, True, D.NO_ACTION_BLOCKED), (D.EXIT, long_, True, D.NO_ACTION_BLOCKED),
            (D.HOLD, flat, True, D.HOLD),                            # HOLD precedence, DERIVED from §11.1
        ]
        for sig, btc, open_, want in cases:
            with self.subTest(sig=sig, btc=btc, open_=open_):
                self.assertEqual(D.mapping(sig, btc, MIN_Q, open_), want)
        with self.assertRaises(ValueError):
            D.mapping("SELL", flat, MIN_Q, False)

    def test_U14_flat_boundary(self):
        self.assertTrue(D.is_flat(F("0.00009999"), MIN_Q))
        self.assertFalse(D.is_flat(F("0.0001"), MIN_Q))
        self.assertEqual(D.mapping(D.BUY, F("0.0001"), MIN_Q, False), D.NO_ACTION)   # BUY while long
        self.assertEqual(D.mapping(D.EXIT, F(0), MIN_Q, False), D.NO_ACTION)         # EXIT while flat


DIGEST_SCRIPT = r"""
import hashlib, json, sys
sys.path.insert(0, sys.argv[1])
from fractions import Fraction as F
from sl_pt_001 import decide as D, exact as X
rows = []
for i in range(60):
    toks = [f"{90000 + ((j * 7919 + i * 104729) % 977)}.{(j * i) % 100:02d}" for j in range(51)]
    out = D.decide_signal([X.parse_number_token(t) for t in toks])
    rows.append({k: (X.to_decimal_string(v) if isinstance(v, F) else v) for k, v in out.items()})
rows.append(X.parse_rfc3339_ns("2026-11-26T10:01:00.5-05:00"))
print(hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest())
"""


class Determinism(unittest.TestCase):
    def test_U10_identical_across_runs_processes_locale_timezone(self):
        pkg = os.path.join(HERE, "..")
        envs = [{}, {"TZ": "Asia/Tokyo", "LC_ALL": "de_DE.UTF-8", "LANG": "de_DE.UTF-8"},
                {"TZ": "America/New_York", "PYTHONHASHSEED": "12345"}, {"TZ": "UTC", "PYTHONHASHSEED": "0"}]
        digests = set()
        for extra in envs:
            env = dict(os.environ, **extra)
            out = subprocess.run([sys.executable, "-I", "-c", DIGEST_SCRIPT, pkg],
                                 capture_output=True, text=True, env=env, check=True)
            digests.add(out.stdout.strip())
        self.assertEqual(len(digests), 1, digests)
        # 100 in-process repeats of one window
        c = closes_with_last(F("0.5"))
        first = json.dumps({k: str(v) for k, v in D.decide_signal(c).items()})
        for _ in range(100):
            self.assertEqual(json.dumps({k: str(v) for k, v in D.decide_signal(c).items()}), first)
        print(f"\n[U10] cross-process digest: {digests.pop()}")


if __name__ == "__main__":
    unittest.main()
