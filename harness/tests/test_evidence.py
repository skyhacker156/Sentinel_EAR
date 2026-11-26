"""Strike 2 tests: RFC 8785 JCS, record hash, chain append/verify (U43, U70, U114), artifacts, policy file, manifest
(U42, U72), TER-1 closed schema (U67, U88), one TER per scheduled terminal path (U108 scheduled part), replay (U9).
Governing text: R4.2i §10 and TER-1 contract v2."""
import copy
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sl_pt_001 import decide as D       # noqa: E402
from sl_pt_001 import evidence as E     # noqa: E402
from sl_pt_001 import exact as X        # noqa: E402
from sl_pt_001 import validate as V     # noqa: E402
import fixtures_1b as FX                # noqa: E402
import test_cycle_r42i as TC            # noqa: E402

NS = X.NS
H0 = "0" * 64
GEN = {"experiment_id": "SL-PT-001", "frozen_set_hashes": {E.SPEC_PATH: E.SPEC_SHA256}}


class JCS(unittest.TestCase):
    def test_RFC8785_key_order_utf16(self):
        obj = {"€": "a", "\r": "b", "1": "c", "\U0001F600": "d", "\u0080": "e", "ö": "f", "דּ": "g"}
        out = E.jcs(obj)
        order = [k for k in ["\r", "1", "\u0080", "ö", "€", "\U0001F600", "דּ"]]
        self.assertEqual([out.index(E._jcs_string(k)) for k in order], sorted(out.index(E._jcs_string(k)) for k in order))

    def test_escapes_and_unicode_passthrough(self):
        self.assertEqual(E.jcs("a\"b\\c\b\f\n\r\t\x01\x1f/€θ"), '"a\\"b\\\\c\\b\\f\\n\\r\\t\\u0001\\u001f/€θ"')
        self.assertEqual(E.jcs({"b": [None, "x"], "a": {}}), '{"a":{},"b":[null,"x"]}')
        self.assertEqual(E.jcs(9007199254740991), "9007199254740991")

    def test_refused_values(self):
        for bad in (True, False, 1.5, -1, 9007199254740992, "\ud800", {1: "x"}, b"x"):
            with self.subTest(bad=bad):
                with self.assertRaises(E.EvidenceError):
                    E.jcs(bad)


class Chain(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def test_genesis_append_verify(self):
        g = E.append_record(self.root, "GENESIS", GEN)
        self.assertEqual((g["seq"], g["prev_hash"]), (0, None))
        r = E.append_record(self.root, "OFF_RUN", {"invocation_instant": "123"})
        self.assertEqual(r["prev_hash"], g["hash"])
        recs = E.read_chain(self.root)
        self.assertEqual([x["hash"] for x in recs], [g["hash"], r["hash"]])
        with open(E.chain_path(self.root), "rb") as fh:
            self.assertTrue(fh.read().endswith(b"\n"))

    def test_genesis_rules(self):
        with self.assertRaises(E.EvidenceError):
            E.append_record(self.root, "OFF_RUN", {"invocation_instant": "1"})       # not GENESIS first
        E.append_record(self.root, "GENESIS", GEN)
        with self.assertRaises(E.EvidenceError):
            E.append_record(self.root, "GENESIS", GEN)                              # only once
        with self.assertRaises(E.EvidenceError):
            E.append_record(tempfile.mkdtemp(), "GENESIS", {"experiment_id": "SL-PT-001", "frozen_set_hashes": {}})

    def test_U70_one_byte_altered_breaks_chain(self):
        E.append_record(self.root, "GENESIS", GEN)
        E.append_record(self.root, "OFF_RUN", {"invocation_instant": "123"})
        p = E.chain_path(self.root)
        data = bytearray(open(p, "rb").read())
        data[data.index(b"123")] = ord("9")
        open(p, "wb").write(bytes(data))
        with self.assertRaises(E.EvidenceError):
            E.read_chain(self.root)

    def test_U43_record_removed_reported(self):
        E.append_record(self.root, "GENESIS", GEN)
        for i in range(3):
            E.append_record(self.root, "OFF_RUN", {"invocation_instant": str(i)})
        p = E.chain_path(self.root)
        lines = open(p, "rb").read().split(b"\n")
        open(p, "wb").write(b"\n".join(lines[:2] + lines[3:]))
        with self.assertRaises(E.EvidenceError):
            E.read_chain(self.root)

    def test_U114_off_run_unknown_field_and_crlf(self):
        E.append_record(self.root, "GENESIS", GEN)
        with self.assertRaises(E.EvidenceError):
            E.append_record(self.root, "OFF_RUN", {"invocation_instant": "1", "extra": "x"})
        p = E.chain_path(self.root)
        open(p, "ab").write(b'{"x":1}\r\n')
        with self.assertRaises(E.EvidenceError):
            E.read_chain(self.root)

    def test_unknown_record_type_refused(self):
        E.append_record(self.root, "GENESIS", GEN)
        with self.assertRaises(E.EvidenceError):
            E.append_record(self.root, "BOUNDARY_VIOLATION_ATTEMPT", {})               # E-1


class Artifacts(unittest.TestCase):
    def test_content_addressed_idempotent_and_collision(self):
        root = tempfile.mkdtemp()
        h = E.put_artifact(root, b"abc")
        self.assertEqual(h, E.sha256_hex(b"abc"))
        self.assertEqual(E.put_artifact(root, b"abc"), h)
        self.assertEqual(E.read_artifact(root, h), b"abc")
        open(os.path.join(root, "artifacts", h), "wb").write(b"tampered")
        with self.assertRaises(E.EvidenceError):
            E.read_artifact(root, h)
        with self.assertRaises(E.EvidenceError):
            E.put_artifact(root, b"abc")


class PolicyAndManifest(unittest.TestCase):
    def test_policy_file_bytes_and_harness_constants(self):
        b = E.policy_bytes()
        self.assertEqual(b, E.policy_bytes())
        self.assertEqual(V.parse_json_tokens(b)["rules"]["R12"], "450")
        E.check_policy_matches_harness(D.POLICY)
        with self.assertRaises(E.EvidenceError):
            E.check_policy_matches_harness(dict(D.POLICY, R7_cap=F(151)))

    def manifest(self, **kw):
        m = {"instrument": "BTC/USD", "T_d0": str(FX.T_D), "declared_slots": 30, "opening_cash": "500.00",
             "frozen_set_hashes": {E.SPEC_PATH: E.SPEC_SHA256}, "harness_sha256": H0, "policy_sha256": H0,
             "task_xml_sha256": H0, "wrapper_sha256": H0, "prev_chain_head": H0}
        m.update(kw)
        return E.jcs_bytes(m)

    def test_valid_manifest(self):
        m, h = E.validate_manifest(self.manifest())
        self.assertEqual((m["declared_slots"], h), (30, E.sha256_hex(self.manifest())))

    def test_U42_U72_and_schema(self):
        for kw in (dict(declared_slots=29), dict(opening_cash="499.99"), dict(T_d0=str(FX.T_D + NS)),
                   dict(frozen_set_hashes={}), dict(instrument="ETH/USD"), dict(extra="x")):
            with self.subTest(kw=list(kw)):
                with self.assertRaises(E.EvidenceError):
                    E.validate_manifest(self.manifest(**kw))
        _, h1 = E.validate_manifest(self.manifest())
        _, h2 = E.validate_manifest(self.manifest(declared_slots=31))                 # U72: edited = new hash
        self.assertNotEqual(h1, h2)


from fractions import Fraction as F  # noqa: E402

CFG = TC.CFG
EVID = V.boundary_check(["PATH"], CFG, ["data.alpaca.markets"])


def scheduled(root, store, v12a=EVID, bars=None, last="5", bh=None, body=None, qh="default", qb="default",
              bars_no_response=False, quote_no_response=False, ledger=None):
    """Run one cycle on raw artifacts, store them, and build its TER. Mirrors §6.4 order: artifacts first."""
    T_d = FX.T_D
    bars = bars if bars is not None else FX.bars(last)
    bh = None if bars_no_response else (bh if bh is not None else TC.hdr())
    body = None if bars_no_response else (body if body is not None else TC.bars_body(bars))
    qh = None if (quote_no_response or bars_no_response) else (TC.hdr() if qh == "default" else qh)
    qb = None if (quote_no_response or bars_no_response) else (TC.quote_body() if qb == "default" else qb)
    cyc = D.run_cycle(v12a, bh, body, TC.T_SEND, TC.T_RECV, qh, qb, T_d, TC.C, ledger or D.ShadowLedger(), store)
    ctx = {"manifest_sha256": H0, "slot_index": 0, "invocation_instant": T_d + 50_000_000, "T_d": T_d,
           "policy_sha256": E.sha256_hex(E.policy_bytes()), "V12a_evidence": v12a[1], "lock_clock_at": T_d + 2 * NS,
           "bars_request": None, "quote_request": None, "bars_sha256": None, "bars_headers_sha256": None,
           "quote_sha256": None, "quote_headers_sha256": None}
    if v12a[0] == "PASS":
        url = "https://data.alpaca.markets/v1beta3/crypto/us/bars"
        if bars_no_response:
            ctx["bars_request"] = {"url": url, "sent_at": str(TC.T_SEND), "received_at": None, "outcome": "NO_RESPONSE"}
        else:
            ctx["bars_request"] = {"url": url, "sent_at": str(TC.T_SEND), "received_at": str(TC.T_RECV), "outcome": "RESPONSE"}
            ctx["bars_sha256"], ctx["bars_headers_sha256"] = E.put_artifact(root, body), E.put_artifact(root, bh)
            if cyc["V12b"] == "PASS":
                qurl = "https://data.alpaca.markets/v1beta3/crypto/us/latest/quotes"
                if quote_no_response:
                    ctx["quote_request"] = {"url": qurl, "sent_at": str(TC.T_RECV + 1), "received_at": None, "outcome": "NO_RESPONSE"}
                else:
                    ctx["quote_request"] = {"url": qurl, "sent_at": str(TC.T_RECV + 1), "received_at": str(TC.T_RECV + 2), "outcome": "RESPONSE"}
                    ctx["quote_sha256"], ctx["quote_headers_sha256"] = E.put_artifact(root, qb), E.put_artifact(root, qh)
    return E.build_scheduled_ter(ctx, cyc, store), cyc


class TERPaths(unittest.TestCase):
    """U108 (scheduled part): one TER per scheduled terminal-path row, each validated, appended and re-verified."""

    def setUp(self):
        self.root = tempfile.mkdtemp()
        E.append_record(self.root, "GENESIS", GEN)

    def roundtrip(self, ter, term):
        self.assertEqual(ter["terminal_state"], term)
        E.append_record(self.root, "CYCLE", ter)
        self.assertEqual(E.read_chain(self.root)[-1]["body"], ter)
        return ter

    def test_U108_every_scheduled_path(self):
        bad_v12a = V.boundary_check(["APCA_API_KEY_ID"], CFG, ["data.alpaca.markets"])
        cases = [
            ("V12a FAIL", dict(v12a=bad_v12a), "BOUNDARY_FAIL"),
            ("bars NO_RESPONSE", dict(bars_no_response=True), "NO_DECISION (FETCH_FAILED)"),
            ("V12b FAIL", dict(bh=TC.hdr(date_ns=TC.T_RECV + 5 * NS)), "BOUNDARY_FAIL"),
            ("V1 FAIL", dict(bh=TC.hdr(status=500)), "NO_DECISION (FETCH_FAILED)"),
            ("V8 FAIL", dict(bars=FX.bars("5", count=50)), "NO_DECISION (DATA_GAP)"),
            ("HOLD", dict(last="0"), "HOLD"),
            ("NO_ACTION", dict(last="-5"), "NO_ACTION"),
            ("QUOTE_INVALID", dict(qh=TC.hdr(status=500)), "NO_DECISION (QUOTE_INVALID)"),
            ("QUOTE_INVALID no response", dict(quote_no_response=True), "NO_DECISION (QUOTE_INVALID)"),
            ("REJECTED", dict(qb=TC.quote_body(t_ns=TC.C - 16 * NS)), "REJECTED"),
            ("SHADOW_EXPIRED", dict(), "SHADOW_EXPIRED"),
            ("one size absent", dict(qb=TC.quote_body(omit=("bs",))), "NO_DECISION (QUOTE_INVALID)"),
            ("both sizes absent", dict(qb=TC.quote_body(omit=("bs", "as"))), "NO_DECISION (QUOTE_INVALID)"),
        ]
        for name, kw, term in cases:
            with self.subTest(path=name):
                ter, _ = scheduled(self.root, {}, **kw)
                self.roundtrip(ter, term)
        self.assertEqual(len(E.read_chain(self.root)), 1 + len(cases))

    def test_path_details(self):
        ter, _ = scheduled(self.root, {}, v12a=V.boundary_check(["APCA_X"], CFG, ["data.alpaca.markets"]))
        self.assertEqual(ter["V3"], {"result": "NOT_EVALUATED", "reason": "V12A_FAILED"})
        self.assertEqual(ter["V12a_evidence"]["env_credential_names"], ["APCA_X"])
        ter, _ = scheduled(self.root, {}, bars_no_response=True)
        self.assertEqual((ter["t_send"], ter["t_recv"], ter["V12b"]["reason"]), (str(TC.T_SEND), None, "FETCH_FAILED"))
        ter, _ = scheduled(self.root, {}, bh=TC.hdr(status=500))
        self.assertEqual((ter["V3"]["reason"], ter["Q1"]["reason"]), ("DATA_INVALID", "DATA_INVALID"))
        ter, _ = scheduled(self.root, {}, last="0")
        self.assertEqual((ter["Q1"]["reason"], len(ter["used_bars"]), len(ter["completed_bars"]),
                          len(ter["excluded_bars"])), ("NO_PROPOSAL", 51, 51, 1))
        self.assertEqual(ter["bar_store_transitions"][0]["event"], "BASELINED")
        ter, _ = scheduled(self.root, {}, qb=TC.quote_body(omit=("bs", "as")))
        self.assertEqual(ter["displayed_sizes"], {"bs": None, "as": None})
        ter, _ = scheduled(self.root, {})
        self.assertEqual([r["rule"] for r in ter["rule_results"]], D.BUY_RULES)
        self.assertEqual((ter["proposal"]["L"], ter["proposal"]["q"]), ("90004", "0.0016"))

    def test_transition_shapes_revision_and_confirm(self):
        store = {}
        t = FX.T_EXP - 4 * 300 * NS
        scheduled(self.root, store, last="0")
        rev = copy.deepcopy(FX.bars("0"))
        for b in rev:
            if X.parse_rfc3339_ns(b["t"]) == t:
                b.update(c="90001")
        ter, _ = scheduled(self.root, store, bars=rev)
        ev = [e for e in ter["bar_store_transitions"] if e["t"] == str(t)][0]
        self.assertEqual((ev["event"], ev["state"], ev["observation_count"], ev["old"]["c"], ev["new"]["c"]),
                         ("SOURCE_REVISION", "PENDING", "1", "90000", "90001"))
        self.assertEqual(ter["terminal_state"], "NO_DECISION (SOURCE_REVISION)")
        ter, _ = scheduled(self.root, store, bars=rev)
        ev = [e for e in ter["bar_store_transitions"] if e["t"] == str(t)][0]
        self.assertEqual((ev["event"], ev["state"], ev["observation_count"]), ("CONFIRMED", "CONFIRMED", "2"))
        self.assertEqual((ev["old"]["c"], ev["new"]["c"]), ("90000", "90001"))      # CC-01: old = previously accepted

    def test_CC03_partitions_kept_when_V1_or_V2_fails(self):
        for kw, n in ((dict(body=TC.bars_body(FX.bars("5"), token='"abc"')), 51),      # V2 fails
                      (dict(qb=TC.quote_body(symbol="ETH/USD")), 51),                  # quote symbol V1 fail
                      (dict(body=b"{not json"), 0)):                                  # unparseable: []
            with self.subTest(n=n):
                ter, _ = scheduled(self.root, {}, **kw)
                self.assertEqual(len(ter["completed_bars"]), n)
                self.assertEqual(ter["bar_store_transitions"], [])
                self.assertEqual(ter["V3"]["reason"], "DATA_INVALID")

    def test_U9_replay_byte_identical_TER(self):
        a, _ = scheduled(tempfile.mkdtemp(), {})
        b, _ = scheduled(tempfile.mkdtemp(), {})
        self.assertEqual(E.jcs_bytes(a), E.jcs_bytes(b))


class TERSchema(unittest.TestCase):
    def setUp(self):
        self.ter, _ = scheduled(tempfile.mkdtemp(), {})

    def test_U67_unknown_or_missing_field(self):
        with self.assertRaises(E.EvidenceError):
            E.validate_ter(dict(self.ter, extra=None))
        t = dict(self.ter)
        del t["used_bars"]
        with self.assertRaises(E.EvidenceError):
            E.validate_ter(t)

    def test_U88_json_number_anywhere(self):
        for path in (("slot_index",), ("proposal", "q"), ("rule_results",)):
            with self.subTest(path=path):
                t = copy.deepcopy(self.ter)
                if path == ("rule_results",):
                    t["rule_results"][0]["result"] = 1
                elif len(path) == 2:
                    t["proposal"]["q"] = 0.0016
                else:
                    t["slot_index"] = 0
                with self.assertRaises(E.EvidenceError):
                    E.validate_ter(t)

    def test_U88_numbers_only_the_general_guard_can_see(self):
        # Mutation finding (2026-11-26): with the general no-numbers guard disabled, the earlier U88 cases still
        # failed through field-specific checks. These cases sit where no field-specific check looks.
        for mutate in (lambda t: t["V12a_evidence"]["client_allowlist"].append(1),
                       lambda t: t["V12a_evidence"]["env_credential_names"].append(2),
                       lambda t: t["V12a_evidence"].__setitem__("client_allowlist", [True])):
            with self.subTest():
                t = copy.deepcopy(self.ter)
                mutate(t)
                with self.assertRaises(E.EvidenceError):
                    E.validate_ter(t)

    def test_presence_violations_refused(self):
        bad = [dict(self.ter, terminal_state="HOLD"),                      # proposal path labelled HOLD
               dict(self.ter, displayed_sizes=None),                       # G8-01: response but no sizes
               dict(self.ter, rule_results=list(reversed(self.ter["rule_results"])))]   # numeric order
        for t in bad:
            with self.assertRaises(E.EvidenceError):
                E.validate_ter(t)


if __name__ == "__main__":
    unittest.main()
