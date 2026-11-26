"""Strike 3 tests: cycle controller (§6.2-6.5, §10.1), run token table (§6.3), lock_clock_at gate (§6.4 step 8),
bar store rebuilt from the chain (§4.9), injection runner (§6.5, contract v2 §7, CC-04).
Ids: U19, U73-U77 (harness side: the records the auditor classifies), U83, U91, U117(a)(b)(c), U118 (harness side),
U108 injected rows. Governing text: R4.2i and TER-1 contract v2.1; never auditor behaviour (decision v5)."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sl_pt_001 import controller as C   # noqa: E402
from sl_pt_001 import evidence as E     # noqa: E402
from sl_pt_001 import exact as X        # noqa: E402
from sl_pt_001 import validate as V     # noqa: E402
import fixtures_1b as FX                # noqa: E402
import test_cycle_r42i as TC            # noqa: E402

NS = X.NS
SLOT = 300 * NS
T0 = FX.T_D
CFG = TC.CFG
GEN_HASHES = {E.SPEC_PATH: E.SPEC_SHA256}
POLICY_SHA = E.sha256_hex(E.policy_bytes())
BARS_URL = ("https://data.alpaca.markets/v1beta3/crypto/us/bars?symbols=BTC%2FUSD&timeframe=5Min"
            "&start=S&end=E&limit=60&sort=asc")
QUOTE_URL = "https://data.alpaca.markets/v1beta3/crypto/us/latest/quotes?symbols=BTC%2FUSD"


class Clock:
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.t += int(s * NS) + 1


def ok_boundary():
    r, ev, _ = V.boundary_check(["PATH"], CFG, ["data.alpaca.markets"])
    return r, ev, CFG


def bad_boundary():
    r, ev, _ = V.boundary_check(["APCA_API_KEY_ID"], CFG, ["data.alpaca.markets"])
    return r, ev, None


def bars_for(T_d, last="0"):
    """FX.bars shifted to decision instant T_d (51 completed bars ending at t_exp, plus a forming bar)."""
    t_exp = X.t_exp_ns(T_d)
    out = [FX.bar(t_exp - SLOT * j, "90000") for j in range(50, 0, -1)]
    out.append(FX.bar(t_exp, X.to_decimal_string(90000 + X.parse_number_token(last))))
    out.append(FX.bar(t_exp + SLOT, "90000"))
    return out


class Market:
    """Deterministic local market: fetches advance the clock like real I/O would. Never live data."""

    def __init__(self, clock, last="0", bars_fail=False, quote_fail=False, compute_s=0):
        self.clock, self.last, self.bars_fail, self.quote_fail, self.compute_s = clock, last, bars_fail, quote_fail, compute_s
        self.quote_calls = 0

    def bars(self, T_d):
        sent = self.clock()
        self.clock.t += 2 * NS // 10
        recv = self.clock()
        if self.bars_fail:
            return {"url": BARS_URL, "sent": sent, "recv": None, "header": None, "body": None}
        h = V.build_header_artifact("1.1", 200, "OK", [("Date", TC.imf(recv)), ("Content-Type", "application/json")])
        return {"url": BARS_URL, "sent": sent, "recv": recv, "header": h, "body": TC.bars_body(bars_for(T_d, self.last))}

    def quote(self):
        self.quote_calls += 1
        sent = self.clock()
        self.clock.t += NS // 10
        recv = self.clock()
        self.clock.t += self.compute_s * NS
        if self.quote_fail:
            return {"url": QUOTE_URL, "sent": sent, "recv": None, "header": None, "body": None}
        h = V.build_header_artifact("1.1", 200, "OK", [("Date", TC.imf(recv)), ("Content-Type", "application/json")])
        return {"url": QUOTE_URL, "sent": sent, "recv": recv, "header": h, "body": TC.quote_body(t_ns=sent - NS)}


def manifest(prev, N=30):
    return E.jcs_bytes({"instrument": "BTC/USD", "T_d0": str(T0), "declared_slots": N, "opening_cash": "500.00",
                        "frozen_set_hashes": GEN_HASHES, "harness_sha256": "1" * 64, "policy_sha256": POLICY_SHA,
                        "task_xml_sha256": "2" * 64, "wrapper_sha256": "3" * 64, "prev_chain_head": prev})


class Base(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.clock = Clock(T0 - 10 * NS)
        self.h = C.Harness(self.root, self.clock, self.clock.sleep, pid=1111)
        g = self.h.genesis(GEN_HASHES)
        self.m = manifest(g["hash"])
        self.mh = E.sha256_hex(self.m)

    def types(self):
        return [r["type"] for r in E.read_chain(self.root)]

    def run_slot(self, j, mk=None, h=None, offset=NS // 20):
        self.clock.t = X.T_d(T0, j) + offset
        mk = mk or Market(self.clock)
        return (h or self.h).invoke(self.m, self.clock(), ok_boundary, mk.bars, mk.quote)


class RunLifecycle(Base):
    def test_run_open_then_cycle_then_close(self):
        r = self.run_slot(0)
        self.assertEqual(self.types(), ["GENESIS", "RUN_OPEN", "CYCLE"])
        self.assertEqual(r["body"]["terminal_state"], "HOLD")
        self.assertEqual(r["body"]["slot_index"], "0")
        self.assertIsNone(C.read_token(self.root))
        with self.assertRaises(C.Refused):                             # RUN_CLOSE only after T_d(N)
            self.h.run_close(self.m, b"log", b"xml")
        self.clock.t = X.T_d(T0, 30)
        self.h.run_close(self.m, b"log", b"xml")
        self.assertEqual(self.types()[-1], "RUN_CLOSE")
        with self.assertRaises(C.Refused):                             # nothing after close
            self.run_slot(1)

    def test_run_open_must_follow_prev_chain_head(self):
        self.h.invoke(self.m, T0 - 400 * NS, ok_boundary, None, None)  # OFF_RUN moves the head
        self.clock.t = T0
        with self.assertRaises(C.Refused):
            self.h.invoke(self.m, T0, ok_boundary, Market(self.clock).bars, Market(self.clock).quote)

    def test_off_run_invocation_writes_only_OFF_RUN(self):
        self.h.invoke(self.m, T0 - 1, ok_boundary, None, None)
        self.assertEqual(self.types(), ["GENESIS", "OFF_RUN"])

    def test_artifacts_stored_including_passing_config(self):
        r = self.run_slot(0)
        b = r["body"]
        for k in ("bars_sha256", "bars_headers_sha256", "quote_sha256", "quote_headers_sha256"):
            self.assertIsNotNone(E.read_artifact(self.root, b[k]))
        self.assertEqual(E.read_artifact(self.root, b["V12a_evidence"]["config_sha256"]), CFG)

    def test_V12a_fail_no_fetch_and_config_not_stored(self):
        self.clock.t = T0 + NS
        called = []
        r = self.h.invoke(self.m, self.clock(), bad_boundary, lambda T: called.append(1), lambda: called.append(2))
        self.assertEqual((r["body"]["terminal_state"], called), ("BOUNDARY_FAIL", []))
        self.assertFalse(os.path.exists(os.path.join(self.root, "artifacts", E.sha256_hex(CFG))))

    def test_quote_not_fetched_when_bars_get_no_response(self):
        mk = Market(self.clock, bars_fail=True)
        r = self.run_slot(0, mk)
        self.assertEqual((r["body"]["terminal_state"], mk.quote_calls), ("NO_DECISION (FETCH_FAILED)", 0))

    def test_shadow_expired_waits_for_ceiling(self):
        r = self.run_slot(0, Market(self.clock, last="5"))
        b = r["body"]
        self.assertEqual(b["terminal_state"], "SHADOW_EXPIRED")
        self.assertGreaterEqual(int(b["lock_clock_at"]), X.ceiling(T0))
        self.assertLess(int(b["lock_clock_at"]), X.T_d(T0, 1))

    def test_store_rebuilt_from_chain_counts_observations(self):
        self.run_slot(0)
        self.run_slot(1)
        store = C.rebuild_store(E.read_chain(self.root))
        t = X.t_exp_ns(T0)
        self.assertEqual(store[t]["count"], 2)                         # observed by slot 0 and slot 1
        used = {u["t"]: u for u in E.read_chain(self.root)[-1]["body"]["used_bars"]}
        self.assertEqual(used[str(t)]["observation_count"], "2")


class TokenTable(Base):
    """§6.3 token table rows; U74 duplicate wake; U19/U83/U117(a) overrun; U91 injection abort."""

    def test_U74_duplicate_after_completion(self):
        self.run_slot(0)
        self.run_slot(0, offset=10 * NS)
        self.assertEqual(self.types()[-1], "CONCURRENT_INVOCATION")
        self.assertEqual(sum(1 for t in self.types() if t == "CYCLE"), 1)

    def test_U74_second_invocation_while_running(self):
        with C.AppendLock(self.root):
            E.append_record(self.root, "RUN_OPEN", {"manifest_sha256": self.mh})
            C.write_token(self.root, {"kind": "SLOT", "manifest": self.mh, "slot": 0, "pid": 7, "acquired_at": "1"})
        self.run_slot(0, offset=20 * NS)
        self.assertEqual(self.types()[-1], "CONCURRENT_INVOCATION")
        self.assertEqual(C.read_token(self.root)["pid"], 7)            # the running cycle keeps its token

    def test_U19_U83_overrun_successor_writes_and_old_append_refused(self):
        slow = C.Harness(self.root, self.clock, self.clock.sleep, pid=2222)
        self.clock.t = T0 + NS // 20
        m = self.m
        # the old process takes the token for slot 0, then stalls: drive its steps by hand
        with C.AppendLock(self.root):
            E.append_record(self.root, "RUN_OPEN", {"manifest_sha256": self.mh})
            old_tok = {"kind": "SLOT", "manifest": self.mh, "slot": 0, "pid": 2222, "acquired_at": str(self.clock())}
            C.write_token(self.root, old_tok)
        self.run_slot(1)                                               # successor at slot 1
        self.assertEqual(self.types()[2:], ["CYCLE_OVERRUN", "CYCLE"])
        ov = E.read_chain(self.root)[2]["body"]
        self.assertEqual(ov, {"slot_index": "0", "old_process_id": "2222"})
        store = C.rebuild_store(E.read_chain(self.root))
        with self.assertRaises(C.Refused):                             # U83: old process append refused
            slow._cycle(E.validate_manifest(m)[0], self.mh, 0, T0, old_tok, store, ok_boundary,
                        Market(self.clock).bars, Market(self.clock).quote)
        self.assertEqual(self.types()[-1], "CYCLE")

    def test_U83_lost_token_refused_even_inside_the_slot(self):
        mk = Market(self.clock)
        real = mk.quote

        def quote_then_takeover():
            out = real()
            with C.AppendLock(self.root):                              # another holder replaced the token
                C.write_token(self.root, {"kind": "SLOT", "manifest": self.mh, "slot": 0, "pid": 99, "acquired_at": "1"})
            return out
        self.clock.t = T0 + NS
        with self.assertRaises(C.Refused):
            self.h.invoke(self.m, self.clock(), ok_boundary, mk.bars, quote_then_takeover)
        self.assertNotIn("CYCLE", self.types())

    def test_U117b_shadow_expired_refused_if_clock_reads_before_ceiling(self):
        clk = self.clock
        state = {"n": 0}

        def sleep(s):                                                 # wake at the ceiling, then the clock steps back
            clk.t = X.ceiling(T0)
            state["n"] = 2

        def clock():
            if state["n"]:
                state["n"] -= 1
                return clk.t - (NS if state["n"] == 0 else 0)
            return clk.t
        h = C.Harness(self.root, clock, sleep, pid=3)
        self.clock.t = T0 + NS
        mk = Market(self.clock, last="5")
        with self.assertRaises(C.Refused):
            h.invoke(self.m, self.clock(), ok_boundary, mk.bars, mk.quote)

    def test_U117a_append_at_or_after_next_boundary_refused(self):
        mk = Market(self.clock, compute_s=300)                         # computation runs past T_d(1)
        with self.assertRaises(C.Refused):
            self.run_slot(0, mk)
        self.assertNotIn("CYCLE", self.types())
        self.assertEqual(C.read_token(self.root)["slot"], 0)           # token kept: the successor sees no terminal
        self.run_slot(1)
        self.assertEqual(self.types()[-2:], ["CYCLE_OVERRUN", "CYCLE"])

    def test_U117c_append_begun_in_slot_is_not_an_overrun(self):
        self.clock.t = X.T_d(T0, 1) - NS                               # lock_clock_at < T_d(1)
        mk = Market(self.clock)
        self.h.invoke(self.m, X.T_d(T0, 0) + 200 * NS, ok_boundary, mk.bars, mk.quote)
        self.run_slot(1)
        self.assertNotIn("CYCLE_OVERRUN", self.types())

    def test_overrun_of_last_slot_written_at_run_close(self):
        with C.AppendLock(self.root):
            E.append_record(self.root, "RUN_OPEN", {"manifest_sha256": self.mh})
            C.write_token(self.root, {"kind": "SLOT", "manifest": self.mh, "slot": 29, "pid": 9, "acquired_at": "1"})
        self.clock.t = X.T_d(T0, 30)
        self.h.run_close(self.m, b"log", b"xml")
        self.assertEqual(self.types()[-2:], ["CYCLE_OVERRUN", "RUN_CLOSE"])

    def test_U73_U75_U76_missed_slots_leave_no_record(self):
        self.run_slot(0)
        self.run_slot(3, offset=250 * NS)                              # sleep/restart: resumes late in slot 3
        cyc = [r["body"]["slot_index"] for r in E.read_chain(self.root) if r["type"] == "CYCLE"]
        self.assertEqual(cyc, ["0", "3"])                              # slots 1, 2: no record (auditor: MISSING)

    def test_U77_every_invocation_leaves_a_record(self):
        self.run_slot(0)
        n = len(self.types())
        self.run_slot(0, offset=30 * NS)
        self.h.invoke(self.m, T0 - 1, ok_boundary, None, None)
        self.assertEqual(len(self.types()), n + 2)                    # duplicate -> anomaly, off-run -> OFF_RUN


# ------------------------------------------------------------------------------------------ injections
def fixture(bid="90004.25", ask="90004.75", instrument="BTC/USD", created_off=3 * NS, quote_age=NS, cash="500.00",
            quote_raw=None, T_d=None):
    T_d = T_d if T_d is not None else T0 - 3 * SLOT
    created = T_d + created_off
    qb = quote_raw if quote_raw is not None else (
        '{"quotes":{"%s":{"bp":%s,"ap":%s,"bs":0.5,"as":0.4,"t":"%s"}}}' % (instrument, bid, ask,
                                                                            FX.iso(created - quote_age))).encode()
    return E.jcs_bytes({"instrument": instrument, "quote_body_hex": qb.hex(), "T_d": str(T_d), "created": str(created),
                        "shadow_cash": cash, "shadow_btc": "0", "shadow_reserved": "0.00", "shadow_reserved_btc": "0",
                        "open_authorizations": [], "policy_sha256": POLICY_SHA})


def plan(*entries):
    return E.jcs_bytes({"injections": [{"fixture_sha256": E.sha256_hex(f), "intended_rule": r} for f, r in entries]})


class Injections(Base):
    def setUp(self):
        super().setUp()
        self.run_slot(0)                                              # run open
        self.clock.t = T0 + 100 * NS

    def inject(self, fx, rule, boundary=ok_boundary, pl=None):
        return self.h.inject(self.m, pl or plan((fx, rule)), fx, rule, self.clock(), boundary)

    def test_U108_injected_rows(self):
        cases = [(fixture(), "R13", ok_boundary, "SHADOW_EXPIRED"),
                 (fixture(instrument="ETH/USD"), "R1", ok_boundary, "REJECTED"),
                 (fixture(quote_age=60 * NS), "R4", ok_boundary, "REJECTED"),
                 (fixture(created_off=95 * NS), "R13", ok_boundary, "REJECTED"),
                 (fixture(bid="90010", ask="90000"), "R5", ok_boundary, "NO_DECISION (QUOTE_INVALID)"),
                 (fixture(quote_raw=b'{"quotes":{"BTC/USD":{"bp":1,"ap":2,"t":"2026-11-26T09:46:00Z"}}}'),
                  "R5", ok_boundary, "NO_DECISION (QUOTE_INVALID)"),
                 (fixture(), "R13", bad_boundary, "BOUNDARY_FAIL")]
        for fx, rule, b, term in cases:
            with self.subTest(term=term, rule=rule):
                rec = self.inject(fx, rule, b)
                t = rec["body"]
                self.assertEqual((rec["type"], t["terminal_state"], t["origin"]), ("INJECTION", term, "INJECTED"))
                self.assertEqual(t["injection"]["fixture_sha256"], E.sha256_hex(fx))
                if b is ok_boundary:
                    self.assertEqual(E.read_artifact(self.root, t["quote_sha256"]), bytes.fromhex(
                        V.parse_json_tokens(fx)["quote_body_hex"]))
                    self.assertEqual(t["V3"], {"result": "NOT_EVALUATED", "reason": "INJECTED"})
                else:
                    self.assertIsNone(t["quote_sha256"])
                self.assertIsNone(C.read_token(self.root))
                self.clock.t += NS
        sizes = [r["body"]["displayed_sizes"] for r in E.read_chain(self.root) if r["type"] == "INJECTION"]
        self.assertEqual(sizes[5], {"bs": None, "as": None})           # both sizes absent: object, members null
        self.assertIsNone(sizes[6])

    def test_U118_second_rule_also_fails_is_recorded_whole(self):
        rec = self.inject(fixture(instrument="ETH/USD", quote_age=60 * NS), "R1")
        fails = [r["rule"] for r in rec["body"]["rule_results"] if r["result"] == "FAIL"]
        self.assertEqual(fails, ["R1", "R4"])                          # every applicable rule, exact failing set

    def test_plan_membership_and_fixture_shape(self):
        fx = fixture()
        with self.assertRaises(C.Refused):
            self.h.inject(self.m, plan((fx, "R4")), fx, "R13", self.clock(), ok_boundary)
        bad = fx.replace(b'"shadow_btc":"0"', b'"shadow_btc":"0.5"')
        with self.assertRaises(C.Refused):                            # not a flat BUY
            self.h.inject(self.m, plan((bad, "R13")), bad, "R13", self.clock(), ok_boundary)
        extra = fx[:-1] + b',"expected":"PASS"}'
        with self.assertRaises(E.EvidenceError):                     # closed shape: no expected-outcome field
            self.h.inject(self.m, plan((extra, "R13")), extra, "R13", self.clock(), ok_boundary)

    def test_injection_not_within_30s_of_next_T_d(self):
        self.clock.t = X.T_d(T0, 1) - 20 * NS
        with self.assertRaises(C.Refused):
            self.inject(fixture(), "R13")

    def test_injections_never_enter_the_store(self):
        before = C.rebuild_store(E.read_chain(self.root))
        self.inject(fixture(), "R13")
        self.assertEqual(C.rebuild_store(E.read_chain(self.root)), before)

    def test_U91_slot_invocation_aborts_injection(self):
        with C.AppendLock(self.root):
            C.write_token(self.root, {"kind": "INJECTION", "manifest": self.mh, "slot": None, "pid": 5, "acquired_at": "1"})
        self.run_slot(1)
        self.assertEqual(self.types()[-2:], ["INJECTION_ABORTED", "CYCLE"])
        self.assertEqual(E.read_chain(self.root)[-1]["body"]["slot_index"], "1")   # slot unaffected

    def test_injection_requires_open_run(self):
        self.clock.t = X.T_d(T0, 30)
        self.h.run_close(self.m, b"log", b"xml")
        with self.assertRaises(C.Refused):
            self.inject(fixture(), "R13")


class Wrapper(unittest.TestCase):
    def test_invocation_log_line_then_start(self):
        from sl_pt_001 import wrapper as W
        root = tempfile.mkdtemp()
        mpath = os.path.join(root, "manifest.json")
        with open(mpath, "wb") as fh:
            fh.write(b"{}")
        seen = []
        rc = W.main(["wrapper.py", root, mpath], start=lambda cmd: seen.append(cmd) or 0)
        msha = E.sha256_hex(b"{}")
        with open(os.path.join(root, "chain", "invocations", msha + ".log"), "rb") as fh:
            line = fh.read()
        inst, pid, wsha = line.rstrip(b"\n").split(b"\t")
        self.assertEqual((rc, line.count(b"\n"), int(pid), wsha.decode()), (0, 1, os.getpid(), W.wrapper_sha256()))
        self.assertEqual(seen[0][-1], inst.decode())                   # the harness gets the logged instant
        self.assertNotIn("-I", seen[0])


class InjectedSchema(unittest.TestCase):
    def test_injected_presence_refuses_scheduled_fields(self):
        res = C.run_injection(C.parse_fixture(fixture()), ok_boundary())
        ctx = {"manifest_sha256": "a" * 64, "invocation_instant": 1, "T_d": T0, "policy_sha256": POLICY_SHA,
               "V12a_evidence": ok_boundary()[1], "lock_clock_at": 2, "quote_sha256": "b" * 64,
               "injection": {"plan_sha256": "c" * 64, "fixture_sha256": "d" * 64, "intended_rule": "R13"}}
        ter = E.build_injected_ter(ctx, res)
        for k, v in (("slot_index", "0"), ("used_bars", [{"t": "1", "state": "BASELINED", "observation_count": "1"}] * 51),
                     ("V3", {"result": "PASS", "reason": None})):
            with self.subTest(k=k):
                with self.assertRaises(E.EvidenceError):
                    E.validate_ter(dict(ter, **{k: v}))


if __name__ == "__main__":
    unittest.main()
