"""Pre-live gate closure tests (§11.6): the harness-side §14 Stage-A rows not yet executed under their own ids, and an
explicit pass AND fail case for every Stage A rule (R1-R13, R15, R16; R2 = limit-order check).
Governing text: frozen R4.2i §14 rows as written; contract v2.1/v2.2 serialization. No new requirement is introduced."""
import os
import sys
import tempfile
import unittest
from fractions import Fraction as F

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sl_pt_001 import controller as C   # noqa: E402
from sl_pt_001 import decide as D       # noqa: E402
from sl_pt_001 import evidence as E     # noqa: E402
from sl_pt_001 import exact as X        # noqa: E402
from sl_pt_001 import validate as V     # noqa: E402
import fixtures_1b as FX                # noqa: E402
import test_controller as T             # noqa: E402

NS = X.NS
T0 = T.T0


class Section14Rows(T.Base):
    def test_U15_invocation_at_T_d_plus_200s_same_cycle_id_R13(self):
        r = self.run_slot(0, T.Market(self.clock, last="5"), offset=200 * NS)
        b = r["body"]
        self.assertEqual(b["cycle_id"], ["BTC/USD", str(X.t_exp_ns(T0))])
        self.assertEqual(b["terminal_state"], "REJECTED")
        self.assertEqual([x["rule"] for x in b["rule_results"] if x["result"] == "FAIL"], ["R13"])

    def test_U96_order_V12a_bars_V12b_quote_and_no_quote_after_V12b_fail(self):
        calls = []
        mk = T.Market(self.clock)

        def boundary():
            calls.append("V12a")
            return T.ok_boundary()

        def bars(T_d):
            calls.append("bars")
            return mk.bars(T_d)

        def quote():
            calls.append("quote")
            return mk.quote()
        self.clock.t = T0 + NS
        self.h.invoke(self.m, self.clock(), boundary, bars, quote)
        self.assertEqual(calls, ["V12a", "bars", "quote"])

        def bad_bars(T_d):                                             # Date 10 s ahead: V12b fails
            calls.append("bars")
            f = mk.bars(T_d)
            f["header"] = V.build_header_artifact("1.1", 200, "OK", [("Date", T.TC.imf(f["recv"] + 10 * NS))])
            return f
        calls.clear()
        self.clock.t = X.T_d(T0, 1) + NS
        r = self.h.invoke(self.m, self.clock(), boundary, bad_bars, quote)
        self.assertEqual((calls, r["body"]["terminal_state"]), (["V12a", "bars"], "BOUNDARY_FAIL"))
        self.assertIsNone(r["body"]["quote_request"])

    def test_U99_crash_before_append_leaves_no_CYCLE_orphans_kept(self):
        """Harness side of U99 for each pre-append boundary: a process dying there leaves no CYCLE record, its
        stored artifacts remain (orphans), and the chain still verifies. The classification (INCOMPLETE) is the
        auditor's (§11.2); the successor's CYCLE_OVERRUN under §6.3 row 3 is recorded as finding F-3."""
        mk = T.Market(self.clock)

        def die(*_):
            raise SystemExit("crash")
        for name, kw in (("before bars", dict(fetch_bars=die)), ("after bars stored", dict(fetch_quote=die))):
            with self.subTest(point=name):
                root = tempfile.mkdtemp()
                h = C.Harness(root, self.clock, self.clock.sleep, pid=1)
                g = h.genesis(T.GEN_HASHES)
                m = T.manifest(g["hash"])
                self.clock.t = T0 + NS
                args = dict(fetch_bars=mk.bars, fetch_quote=mk.quote)
                args.update(kw)
                with self.assertRaises(SystemExit):
                    h.invoke(m, self.clock(), T.ok_boundary, args["fetch_bars"], args["fetch_quote"])
                recs = E.read_chain(root)
                self.assertEqual([r["type"] for r in recs], ["GENESIS", "RUN_OPEN"])
                arts = os.listdir(os.path.join(root, "artifacts")) if os.path.isdir(os.path.join(root, "artifacts")) else []
                self.assertEqual(len(arts) > 1, name == "after bars stored")   # config + bars body/header kept

    def test_U102_last_slot_token_at_RUN_CLOSE(self):
        with C.AppendLock(self.root):
            E.append_record(self.root, "RUN_OPEN", {"manifest_sha256": self.mh})
            C.write_token(self.root, {"kind": "SLOT", "manifest": self.mh, "slot": 29, "pid": 4, "acquired_at": "1"})
        self.clock.t = X.T_d(T0, 30)
        self.h.run_close(self.m, b"log", b"xml")
        self.assertEqual(self.types()[-2:], ["CYCLE_OVERRUN", "RUN_CLOSE"])

    def test_U104_shadow_expired_delayed_past_next_boundary(self):
        clk = self.clock

        def oversleep(s):
            clk.t = X.T_d(T0, 1) + NS                                  # wakes after T_d(1)
        h = C.Harness(self.root, clk, oversleep, pid=5)
        mk = T.Market(clk, last="5")
        clk.t = T0 + NS
        with self.assertRaises(C.Refused):
            h.invoke(self.m, clk(), T.ok_boundary, mk.bars, mk.quote)
        self.run_slot(1)
        self.assertEqual(self.types()[-2:], ["CYCLE_OVERRUN", "CYCLE"])


class Section14Pure(unittest.TestCase):
    def test_U97_clock_masking_plus_4s_with_2s_transit(self):
        t_send, t_recv = 0, 2 * NS
        D_ns = (t_send + 1 * NS) + 4 * NS                              # server stamps mid-flight, +4 s offset
        r, D_, lo, hi = V.clock_check(T.TC.imf(D_ns + 1_700_000_000 * NS),
                                      t_send + 1_700_000_000 * NS, t_recv + 1_700_000_000 * NS)
        self.assertEqual(r, "FAIL")
        self.assertGreater(hi, 2 * NS)

    def test_U98_round_trip_boundaries(self):
        base = 1_700_000_000 * NS
        Dh = T.TC.imf(base)
        self.assertEqual(V.clock_check(Dh, base - NS, base + 2 * NS - 1)[0], "PASS")
        self.assertEqual(V.clock_check(Dh, base - NS, base + 2 * NS)[0], "FAIL")       # exactly 3 s: condition 3
        self.assertEqual(V.clock_check(Dh, base - NS, base + 2 * NS + 1)[0], "FAIL")

    def test_U106_t_recv_before_t_send(self):
        base = 1_700_000_000 * NS
        self.assertEqual(V.clock_check(T.TC.imf(base), base, base - 1)[0], "FAIL")

    def test_U107_Date_absent_or_unparseable(self):
        base = 1_700_000_000 * NS
        for d in (None, "", "Tue, 14 Nov 2023 22:13:20 UTC", "2023-11-14T22:13:20Z", "Tue, 31 Nov 2023 22:13:20 GMT"):
            with self.subTest(d=d):
                self.assertEqual(V.clock_check(d, base, base + NS)[0], "FAIL")

    def test_U101_A_B_C_D_pending_throughout(self):
        store = {}
        tuples = ["90000", "90001", "90002", "90003"]
        T_d = FX.T_D
        for i, c in enumerate(tuples):
            bars = T.bars_for(T_d)
            bars[50] = FX.bar(X.t_exp_ns(T_d), c)
            v = V.validate_bars(V.check_bars_response(T.TC.hdr(), T.TC.bars_body(bars))["bars"], T_d)
            V.fold(store, v, V.request_start_ns(T_d), T_d)
            if i:
                self.assertEqual(store[X.t_exp_ns(T_d)]["state"], "PENDING")
                self.assertEqual(V.check_V11(store, T_d), "FAIL")      # NO_DECISION (SOURCE_REVISION)

    def test_U105_sizing_vectors(self):
        cases = [("59850", F(150), "0.0025", "150.00"), ("59850", F(14999, 100), "0.0024", "144.00"),
                 ("60663.76", F(150), "0.0024", "145.96"), ("100000", F(150), "0.0014", "140.35")]
        for ask, cash, q, R in cases:
            with self.subTest(ask=ask, cash=cash):
                p = D.construct("BUY", X.parse_number_token(ask) - 1, X.parse_number_token(ask), D.ShadowLedger(cash=cash))
                self.assertEqual((p["q"], p["R"]), (X.parse_number_token(q), X.parse_number_token(R)))

    def test_U110_EXIT_fixture_reservation(self):
        lg = D.ShadowLedger(cash=F(500), btc=F(3, 1000))
        bid, ask = F(90000), F(90001)
        qt = {"bp": "90000", "ap": "90001", "bs": "1", "as": "1", "t": FX.iso(FX.T_D + 3 * NS)}
        out = D._propose({}, "EXIT", qt, V.validate_quote(qt), FX.T_D + 5 * NS, FX.T_D, lg, D.POLICY)
        self.assertEqual(out["terminal"], "SHADOW_EXPIRED")
        self.assertEqual(out["reserved"]["btc"], out["proposal"]["q"])
        self.assertEqual(out["proposal"]["q"], F(3, 1000))
        self.assertEqual((lg.reserved_btc, lg.reserved_usd), (0, 0))   # released at SHADOW_EXPIRED

    def test_U119_R2_not_limit(self):
        lg = D.ShadowLedger()
        p = D.construct("BUY", F(90000), F(90001), lg)
        p["order_type"] = "MARKET"
        q = {"bid": F(90000), "ask": F(90001), "t": FX.T_D}
        self.assertEqual(D.disposition(D.evaluate(p, q, FX.T_D + NS, FX.T_D, lg)),
                         {"terminal": "REJECTED", "failing": ["R2"]})

    def test_U122_leap_second_malformed_and_9_fraction_digits_exact(self):
        with self.assertRaises(X.MalformedValue):
            X.parse_rfc3339_ns("2016-12-31T23:59:60Z")
        self.assertEqual(X.parse_rfc3339_ns("2016-12-31T23:59:59.999999999Z"),
                         X.parse_rfc3339_ns("2017-01-01T00:00:00Z") - 1)


class Section14More(unittest.TestCase):
    def test_U44_created_T_d_plus_5s_proposal_and_deadline(self):
        lg = D.ShadowLedger()
        qt = {"bp": "90000", "ap": "90001", "bs": "1", "as": "1", "t": FX.iso(FX.T_D + 3 * NS)}
        out = D._propose({}, "BUY", qt, V.validate_quote(qt), FX.T_D + 5 * NS, FX.T_D, lg, D.POLICY)
        self.assertIsNotNone(out["proposal"])
        self.assertEqual(X.approval_deadline(FX.T_D, FX.T_D + 5 * NS), FX.T_D + 120 * NS)

    def test_U100_baselined_changed_same_changed_confirmed(self):
        store, T_d, t = {}, FX.T_D, X.t_exp_ns(FX.T_D)
        seen = []
        for c in ("90000", "90005", "90005"):
            bars = T.bars_for(T_d)
            bars[50] = FX.bar(t, c)
            v = V.validate_bars(V.check_bars_response(T.TC.hdr(), T.TC.bars_body(bars))["bars"], T_d)
            V.fold(store, v, V.request_start_ns(T_d), T_d)
            seen.append((store[t]["state"], store[t]["count"], V.check_V11(store, T_d)))
        self.assertEqual(seen, [("BASELINED", 1, "PASS"), ("PENDING", 1, "FAIL"), ("CONFIRMED", 2, "PASS")])

    def test_U121_evaluator_exact_failing_sets(self):
        BID, ASK = F(90000), F(90001)
        q = {"bid": BID, "ask": ASK, "t": FX.T_D + 2 * NS}
        c = FX.T_D + 5 * NS

        def failing(p, lg):
            return [k for k, v in D.evaluate(p, q, c, FX.T_D, lg).items() if v == "FAIL"]
        flat, long_ = D.ShadowLedger(), D.ShadowLedger(btc=F(3, 1000))
        buy = D.construct("BUY", BID, ASK, flat)
        ex = D.construct("EXIT", BID, ASK, long_)
        self.assertEqual(failing(dict(buy, order_type="MARKET"), flat), ["R2"])
        self.assertEqual(failing({k: v for k, v in buy.items() if k != "rounding_inputs"}, flat), ["R3"])
        lg6 = D.ShadowLedger()
        lg6.reserved_usd = F(400)
        self.assertEqual(failing(dict(buy, R=F(101)), lg6), ["R6"])
        self.assertEqual(failing(dict(buy, R=F(15001, 100)), flat), ["R7"])
        self.assertEqual(failing(D.construct("BUY", BID, ASK, D.ShadowLedger(btc=F(2, 1000))),
                                 D.ShadowLedger(btc=F(2, 1000))), ["R8"])
        oa = D.ShadowLedger(open_or_unresolved=True)
        self.assertEqual(failing(buy, oa), ["R11", "R16"])
        self.assertEqual(failing(dict(ex, q=F(4, 1000)), long_), ["R9"])
        self.assertEqual(failing(D.construct("EXIT", BID, ASK, flat), flat), ["R10", "R15"])
        self.assertEqual((failing(ex, long_), failing(buy, flat)), ([], []))


class XSeries(unittest.TestCase):
    """§14 X-series Stage-A rows on the harness side (X1, X2, X4, X5, X6 are test_decision_path EVAL_X*;
    X10 is test_purity; X11 is auditor-only). E-1: for X8/X10 'recorded' means retained test output."""

    def test_X3_previous_cycle_snapshot_REJECTED_R4(self):
        lg = D.ShadowLedger()
        p = D.construct("BUY", F(90000), F(90001), lg)
        prev = {"bid": F(90000), "ask": F(90001), "t": FX.T_D - 300 * NS + 3 * NS}       # last cycle's quote
        res = D.evaluate(p, prev, FX.T_D + 5 * NS, FX.T_D, lg)
        self.assertEqual([k for k, v in res.items() if v == "FAIL"], ["R4"])

    def test_X7_limit_1_5pct_off_mid_REJECTED_R5(self):
        lg = D.ShadowLedger()
        p = D.construct("BUY", F(90000), F(90001), lg)
        p["L"] = F(90000) * F(1015, 1000)
        res = D.evaluate(p, {"bid": F(90000), "ask": F(90001), "t": FX.T_D + 2 * NS}, FX.T_D + 5 * NS, FX.T_D, lg)
        self.assertEqual([k for k, v in res.items() if v == "FAIL"], ["R5"])

    def test_X8_trading_host_refused_before_network_io(self):
        from sl_pt_001 import market as M
        opened = []
        cl = M.Client(connect=lambda h, t: opened.append(h))
        for host, target in (("paper-api.alpaca.markets", "/v2/orders"), ("api.alpaca.markets", "/v2/orders")):
            with self.assertRaises(M.RefusedRequest):
                cl.get(host, target)
        self.assertEqual(opened, [])
        print("\n[X8] BOUNDARY_VIOLATION_ATTEMPT (retained test output, E-1): trading-host requests refused before I/O")

    def test_X9_credential_in_env_or_config_BOUNDARY_FAIL(self):
        from sl_pt_001 import cli as CLI
        from sl_pt_001 import market as M
        r1 = CLI.boundary(M.Client(), {"PATH": "x", "APCA_API_KEY_ID": "k"})[0]
        d = tempfile.mkdtemp()
        cfgp = os.path.join(d, "config.json")
        with open(cfgp, "wb") as fh:
            fh.write(b'{"client_allowlist":["data.alpaca.markets"],"api_key":"k"}')
        r2 = CLI.boundary(M.Client(), {"PATH": "x"}, config_path=cfgp)[0]
        self.assertEqual((r1, r2), ("FAIL", "FAIL"))


class RuleMatrix(unittest.TestCase):
    """§11.6: an EXECUTED pass case and fail case for every Stage A rule. Pass = a valid proposal with the rule PASS;
    fail = a one-field change making that rule FAIL. Each fail case asserts the exact failing set."""
    BID, ASK = F(90000), F(90001)

    def quote(self, t=None):
        return {"bid": self.BID, "ask": self.ASK, "t": FX.T_D + 2 * NS if t is None else t}

    def run_rules(self, side="BUY", ledger=None, change=None, created=None, quote=None):
        lg = ledger or (D.ShadowLedger() if side == "BUY" else D.ShadowLedger(btc=F(3, 1000)))
        p = D.construct(side, self.BID, self.ASK, lg)
        if change:
            change(p, lg)
        res = D.evaluate(p, quote or self.quote(), created or FX.T_D + 5 * NS, FX.T_D, lg)
        return res

    def test_every_rule_pass_and_fail(self):
        def setp(k, v):
            return lambda p, lg: p.__setitem__(k, v)

        def reserve_400_then_R_101(p, lg):
            lg.reserved_usd = F(400)
            p["R"] = F(101)

        def open_auth(p, lg):
            lg.open_or_unresolved = True
        fails = {
            "R1": (dict(change=setp("instrument", "ETH/USD")), ["R1"]),
            "R2": (dict(change=setp("order_type", "MARKET")), ["R2"]),
            "R3": (dict(change=setp("L", "90001")), None),              # malformed field: R3 plus rules reading L
            "R4": (dict(quote=self.quote(t=FX.T_D - 20 * NS)), ["R4"]),
            "R5": (dict(change=setp("L", F(93000))), ["R5"]),
            "R6": (dict(change=reserve_400_then_R_101), ["R6"]),          # cash_available 100 < R, equity 500
            "R7": (dict(change=setp("R", F(15001, 100))), ["R7"]),
            "R8": (dict(ledger=D.ShadowLedger(btc=F(2, 1000)), change=None), None),
            "R10": (dict(change=setp("q", F(1, 100000))), ["R10"]),
            "R11": (dict(change=open_auth), ["R11", "R16"]),
            "R12": (dict(ledger=D.ShadowLedger(cash=F(44999, 100))), ["R12"]),
            "R13": (dict(created=FX.T_D + 91 * NS, quote=self.quote(t=FX.T_D + 89 * NS)), ["R13"]),
            "R16": (dict(change=open_auth), ["R11", "R16"]),
            "R9": (dict(side="EXIT", change=setp("q", F(4, 1000))), ["R9"]),
            "R15": (dict(side="EXIT", ledger=D.ShadowLedger(btc=F(0))), None),
        }
        base_buy, base_exit = self.run_rules("BUY"), self.run_rules("EXIT")
        for r in D.BUY_RULES:
            self.assertEqual(base_buy[r], "PASS", r)                    # pass case for every BUY rule
        for r in D.EXIT_RULES:
            self.assertEqual(base_exit[r], "PASS", r)                   # pass case for R9, R15 (and EXIT set)
        for rule, (kw, exact) in fails.items():
            with self.subTest(rule=rule):
                res = self.run_rules(**kw)
                failing = [k for k, v in res.items() if v == "FAIL"]
                self.assertIn(rule, failing)
                if exact is not None:
                    self.assertEqual(failing, exact)
        self.assertEqual(sorted(set(fails), key=lambda c: int(c[1:])),
                         ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11", "R12", "R13", "R15", "R16"])


class PreliveInjectionFiles(unittest.TestCase):
    """The six committed fixtures and the plan (harness/prelive/injections): closed shapes, plan membership, file name =
    raw SHA-256, policy hash = P-0.2 bytes, and each fixture REJECTED on exactly its intended rule on replay (U118 d)."""
    DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "prelive", "injections")

    def test_plan_and_six_fixtures(self):
        with open(os.path.join(self.DIR, "plan-stage-a.json"), "rb") as fh:
            plan = V.parse_json_tokens(fh.read())
        E._closed(plan, ["injections"], "plan")
        rules = [e["intended_rule"] for e in plan["injections"]]
        self.assertEqual(rules, ["R1", "R4", "R5", "R10", "R12", "R13"])
        names = sorted(os.listdir(os.path.join(self.DIR, "fixtures")))
        self.assertEqual(names, sorted(e["fixture_sha256"] + ".json" for e in plan["injections"]))
        decoded = []
        for e in plan["injections"]:
            with open(os.path.join(self.DIR, "fixtures", e["fixture_sha256"] + ".json"), "rb") as fh:
                raw = fh.read()
            self.assertEqual(E.sha256_hex(raw), e["fixture_sha256"])
            fx = C.parse_fixture(raw)
            self.assertEqual(fx["policy_sha256"], E.sha256_hex(E.policy_bytes()))
            res = C.run_injection(fx, T.ok_boundary())
            self.assertEqual((res["terminal"], [k for k, v in res["rules"].items() if v == "FAIL"]),
                             ("REJECTED", [e["intended_rule"]]))
            decoded.append(V.parse_json_tokens(raw))
        self.assertEqual(len({E.jcs(d) for d in decoded}), 6)          # distinct decoded objects (contract §7)


if __name__ == "__main__":
    unittest.main()
