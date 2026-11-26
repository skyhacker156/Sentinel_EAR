"""Strike 1b completion tests (frozen R4.2i, FD-5 v2): the full cycle from raw D-8 artifacts.
V12a (§6.4 step 1, D-2, U116), V12b ordering (§5.6), V1/V2 (§4.7, D-1, D-8, U13, U94, U95, U111a/b), transport
(U112, U113), bar store and V11 (§4.9, D-6, U31, U35, U36, U39, U40, U84, U85, U115), displayed sizes (G8-01),
full BUY -> SHADOW_EXPIRED, replay determinism (U9 form)."""
import copy
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
CFG = b'{"client_allowlist":["data.alpaca.markets"]}'
V12A_OK = V.boundary_check(["PATH", "HOME"], CFG, ["data.alpaca.markets"])
DAYS = ["Thu", "Fri", "Sat", "Sun", "Mon", "Tue", "Wed"]
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def imf(ns):
    iso = FX.iso(ns - ns % NS)
    y, mo, d = iso[:4], int(iso[5:7]), iso[8:10]
    return f"{DAYS[(ns // (86400 * NS)) % 7]}, {d} {MON[mo - 1]} {y} {iso[11:19]} GMT"


def bars_body(bars, token="null", symbol="BTC/USD", raw=None):
    if raw is not None:
        return raw
    rows = []
    for b in bars:
        parts = [f'"t":"{b["t"]}"' if isinstance(b["t"], str) else f'"t":{b["t"]}']
        parts += [f'"{k}":{b[k]}' for k in ("o", "h", "l", "c", "v", "vw", "n")]
        rows.append("{" + ",".join(parts) + "}")
    return ('{"bars":{"%s":[%s]},"next_page_token":%s}' % (symbol, ",".join(rows), token)).encode()


T_SEND = FX.T_D + 1 * NS // 10
T_RECV = FX.T_D + 3 * NS // 10


def hdr(status=200, date_ns=None, extra=()):
    fields = [("Date", imf(date_ns if date_ns is not None else T_RECV)), ("Content-Type", "application/json")]
    return V.build_header_artifact("1.1", status, "OK" if status == 200 else "ERR", fields + list(extra))


def quote_body(bp="90004.25", ap="90004.75", bs="0.5", as_="0.4", t_ns=None, symbol="BTC/USD", omit=()):
    q = {"bp": bp, "ap": ap, "bs": bs, "as": as_}
    parts = [f'"{k}":{v}' for k, v in q.items() if k not in omit]
    if "t" not in omit:
        parts.append(f'"t":"{FX.iso(t_ns if t_ns is not None else C - 2 * NS)}"')
    return ('{"quotes":{"%s":{%s}}}' % (symbol, ",".join(parts))).encode()


C = FX.T_D + 5 * NS


def cycle(bars=None, last="5", body=None, bh=None, qh="default", qb="default", v12a=V12A_OK, store=None,
          ledger=None, T_d=FX.T_D, t_send=T_SEND, t_recv=T_RECV):
    bars = bars if bars is not None else FX.bars(last)
    store = {} if store is None else store
    return D.run_cycle(v12a, bh if bh is not None else hdr(), body if body is not None else bars_body(bars),
                       t_send, t_recv, hdr() if qh == "default" else qh,
                       quote_body() if qb == "default" else qb, T_d, C, ledger or D.ShadowLedger(), store)


class BoundaryV12a(unittest.TestCase):
    def test_U116_env_credential_name_recorded_not_value(self):
        r, ev, store_cfg = V.boundary_check(["PATH", "apca_api_key_id", "ALPACA_SECRET"], CFG, ["data.alpaca.markets"])
        self.assertEqual((r, store_cfg), ("FAIL", False))
        self.assertEqual(ev["env_credential_names"], ["ALPACA_SECRET", "apca_api_key_id"])
        self.assertNotIn("value", str(ev).lower())

    def test_U116_config_extra_key_allowlist_mismatch_missing_config(self):
        cases = [(b'{"client_allowlist":["data.alpaca.markets"],"key":"x"}', ["data.alpaca.markets"]),
                 (b'{"client_allowlist":["data.alpaca.markets","api.alpaca.markets"]}', ["data.alpaca.markets"]),
                 (CFG, ["data.alpaca.markets", "paper-api.alpaca.markets"]),
                 (b'{"client_allowlist":["data.alpaca.markets"],"client_allowlist":["x"]}', ["data.alpaca.markets"]),
                 (None, ["data.alpaca.markets"]), (b"not json", ["data.alpaca.markets"])]
        for cfg, client in cases:
            with self.subTest(cfg=cfg, client=client):
                r, ev, store_cfg = V.boundary_check([], cfg, client)
                self.assertEqual((r, store_cfg), ("FAIL", False))
        self.assertIsNone(V.boundary_check([], None, ["data.alpaca.markets"])[1]["config_sha256"])

    def test_V12a_pass_and_cycle_BOUNDARY_FAIL_with_no_fetch(self):
        self.assertEqual(V12A_OK[0], "PASS")
        self.assertTrue(V12A_OK[2])
        out = cycle(v12a=V.boundary_check(["APCA_API_SECRET_KEY"], CFG, ["data.alpaca.markets"]))
        self.assertEqual((out["terminal"], out["reason"]), ("BOUNDARY_FAIL", "V12A_FAILED"))
        self.assertEqual(set(out["V"].values()), {"NOT_EVALUATED"})


class TransportAndClock(unittest.TestCase):
    def test_U112_bars_no_response(self):
        out = D.run_cycle(V12A_OK, None, None, T_SEND, T_RECV, None, None, FX.T_D, C, D.ShadowLedger(), {})
        self.assertEqual(out["terminal"], "NO_DECISION (FETCH_FAILED)")
        self.assertEqual(out["V12b"], "NOT_EVALUATED")

    def test_V12b_fail_is_BOUNDARY_FAIL_before_V1(self):
        out = cycle(bh=hdr(date_ns=T_RECV + 5 * NS), body=b"{not json")      # bad clock and bad body
        self.assertEqual((out["terminal"], out["reason"]), ("BOUNDARY_FAIL", "V12B_FAILED"))
        self.assertEqual(out["V"]["V1"], "NOT_EVALUATED")                     # V12b runs before V1 (§5.6)

    def test_U113a_quote_no_response_HOLD(self):
        out = cycle(last="0", qh=None, qb=None)
        self.assertEqual(out["terminal"], "HOLD")
        self.assertIsNone(out["displayed_sizes"])

    def test_U113b_quote_no_response_BUY_QUOTE_INVALID_all_Q_fail(self):
        out = cycle(last="5", qh=None, qb=None)
        self.assertEqual(out["terminal"], "NO_DECISION (QUOTE_INVALID)")
        self.assertEqual(set(out["Q"].values()), {"FAIL"})


class V1V2(unittest.TestCase):
    def assertNoDecision(self, out, sub):
        self.assertEqual(out["terminal"], f"NO_DECISION ({sub})")
        self.assertEqual({out["V"][c] for c in ("V3", "V4", "V5", "V6", "V7", "V8", "V9", "V10", "V11")},
                         {"NOT_EVALUATED"})                                   # U111a/b: DATA_INVALID

    def test_U111a_V1_http_encoding_json_symbol_FETCH_FAILED(self):
        good = FX.bars("5")
        for kw in (dict(bh=hdr(status=500)), dict(bh=hdr(extra=[("Content-Encoding", "gzip")])),
                   dict(body=b'{"bars":'), dict(body=bars_body(good, symbol="ETH/USD")),
                   dict(body=bars_body(good).replace(b'"BTC/USD":[', b'"BTC/USD":[],"ETH/USD":[')),
                   dict(body=bars_body(good).replace(b'"next_page_token":null', b'"next_page_token":NaN')),
                   dict(body=bars_body(good).replace(b'{"bars"', b'{"next_page_token":null,"bars"'))):
            with self.subTest(kw=list(kw)):
                self.assertNoDecision(cycle(**kw), "FETCH_FAILED")

    def test_V1_identity_encoding_is_allowed(self):
        self.assertEqual(cycle(last="0", bh=hdr(extra=[("Content-Encoding", "identity")]))["terminal"], "HOLD")

    def test_U95_quote_wrong_symbol_fails_V1(self):
        self.assertNoDecision(cycle(qb=quote_body(symbol="ETH/USD")), "FETCH_FAILED")

    def test_U94_missing_page_token_key_and_bar_field_INCOMPLETE(self):
        good = FX.bars("5")
        no_key = bars_body(good).replace(b',"next_page_token":null', b"")
        no_field = bars_body(good).replace(b',"vw":90000', b"", 1)
        for body in (no_key, no_field):
            with self.subTest():
                self.assertNoDecision(cycle(body=body), "INCOMPLETE_RESPONSE")

    def test_U13_page_token_not_null_INCOMPLETE_no_second_request(self):
        for tok in ('""', '"abc"', "0"):
            with self.subTest(tok=tok):
                out = cycle(body=bars_body(FX.bars("5"), token=tok))
                self.assertEqual(out["V"]["V2"], "FAIL")
                self.assertNoDecision(out, "INCOMPLETE_RESPONSE")

    def test_V9_json_string_where_number_required_MALFORMED(self):
        body = bars_body(FX.bars("5")).replace(b'"c":90005', b'"c":"90005"')
        self.assertEqual(cycle(body=body)["terminal"], "NO_DECISION (MALFORMED_VALUE)")

    def test_token_text_preserved_from_body(self):
        b = V.check_bars_response(hdr(), bars_body(FX.bars("5")).replace(b'"c":90005', b'"c":9.0005e4'))
        self.assertIn("9.0005e4", [r["c"] for r in b["bars"]])


class BarStore(unittest.TestCase):
    def test_U115b_bare_NaN_body_is_V1_not_V9(self):
        body = bars_body(FX.bars("0")).replace(b'"c":90000', b'"c":NaN', 1)
        self.assertEqual(cycle(body=body)["terminal"], "NO_DECISION (FETCH_FAILED)")

    T_D2 = FX.T_D + 300 * NS

    def revise(self, bars, t_ns, c):
        out = copy.deepcopy(bars)
        for b in out:
            if X.parse_rfc3339_ns(b["t"]) == t_ns:
                b.update(c=c, o=c, h=c, l=c, vw=c)
        return out

    def test_U35_first_cycle_all_BASELINED(self):
        store = {}
        out = cycle(last="0", store=store)
        self.assertEqual(out["terminal"], "HOLD")
        self.assertEqual({s["state"] for s in store.values()}, {"BASELINED"})
        self.assertEqual({s["count"] for s in store.values()}, {1})
        self.assertEqual(len(store), 51)                                        # forming bar never stored

    def test_U39_revision_pending_then_confirmed_next_slot(self):
        store = {}
        cycle(last="0", store=store)
        t = FX.T_EXP - 10 * 300 * NS
        rev = self.revise(FX.bars("0"), t, "90001")
        out = cycle(bars=rev, store=store)
        self.assertEqual(out["terminal"], "NO_DECISION (SOURCE_REVISION)")      # U31 inside the window
        self.assertEqual(store[t]["state"], "PENDING")
        out = cycle(bars=rev, store=store)
        self.assertEqual(store[t]["state"], "CONFIRMED")
        self.assertEqual(store[t]["count"], 2)
        self.assertNotEqual(out["terminal"], "NO_DECISION (SOURCE_REVISION)")

    def test_U40_A_B_A_is_two_revisions(self):
        store = {}
        t = FX.T_EXP - 3 * 300 * NS
        a = FX.bars("0")
        cycle(bars=a, store=store)
        ev1 = cycle(bars=self.revise(a, t, "90007"), store=store)["transitions"]
        ev2 = cycle(bars=a, store=store)["transitions"]
        revs = [e for e in ev1 + ev2 if e["event"] == "SOURCE_REVISION" and e["t"] == t]
        self.assertEqual(len(revs), 2)
        self.assertEqual(store[t]["state"], "PENDING")

    def test_U85_token_text_change_is_a_revision(self):
        store = {}
        t = FX.T_EXP - 300 * NS
        cycle(last="0", store=store)
        self.assertEqual(cycle(bars=self.revise(FX.bars("0"), t, "90000.0"), store=store)["terminal"],
                         "NO_DECISION (SOURCE_REVISION)")

    def test_U31_revision_outside_window_recorded_only(self):
        store = {}
        old = FX.T_EXP - 55 * 300 * NS                                          # inside request range, outside window
        bars = FX.bars("0", count=56)
        cycle(bars=bars, store=store)
        out = cycle(bars=self.revise(bars, old, "1"), store=store)
        self.assertEqual(out["terminal"], "HOLD")
        self.assertIn("SOURCE_REVISION", [e["event"] for e in out["transitions"]])

    def test_U84_disappearance_in_window_DATA_GAP_and_note(self):
        store = {}
        cycle(last="0", store=store)
        t = FX.T_EXP - 20 * 300 * NS
        bars = [b for b in FX.bars("0") if X.parse_rfc3339_ns(b["t"]) != t]
        out = cycle(bars=bars, store=store)
        self.assertEqual(out["terminal"], "NO_DECISION (DATA_GAP)")
        self.assertIn({"t": t, "event": "DISAPPEARED"}, out["transitions"])
        self.assertEqual(store[t]["state"], "BASELINED")                        # state unchanged

    def test_U115_V9_failing_response_not_admitted(self):
        store = {}
        cycle(last="0", store=store)
        before = copy.deepcopy(store)
        # correction (run 7): a bare NaN is not JSON (V1 FETCH_FAILED); a valid JSON body failing V9 needs c <= 0.
        bad = self.revise(FX.bars("0"), FX.T_EXP - 2 * 300 * NS, "-1")
        out = cycle(bars=bad, store=store)
        self.assertEqual(out["terminal"], "NO_DECISION (MALFORMED_VALUE)")
        self.assertEqual(out["transitions"], [])
        self.assertEqual(store, before)                                         # no observation, D-6

    def test_U36_detection_against_slot_1_after_a_NO_DECISION_slot(self):
        store = {}
        cycle(last="0", store=store)                                            # slot 1 baselines
        stale = [b for b in FX.bars("0") if X.parse_rfc3339_ns(b["t"]) != FX.T_EXP]
        self.assertEqual(cycle(bars=stale, store=store)["terminal"], "NO_DECISION (STALE_SERIES)")   # slot 2
        t = FX.T_EXP - 5 * 300 * NS
        self.assertEqual(cycle(bars=self.revise(FX.bars("0"), t, "1"), store=store)["terminal"],
                         "NO_DECISION (SOURCE_REVISION)")                       # slot 3 detects vs slot 1


class DisplayedSizes(unittest.TestCase):
    def test_G8_01_rule(self):
        q = V.check_quote_response(hdr(), quote_body())["quote"]
        self.assertEqual(V.displayed_sizes(q), {"bs": "0.5", "as": "0.4"})
        q = V.check_quote_response(hdr(), quote_body(omit=("bs",)))["quote"]
        self.assertEqual(V.displayed_sizes(q), {"bs": None, "as": "0.4"})
        q = V.check_quote_response(hdr(), quote_body(omit=("bs", "as")))["quote"]
        self.assertEqual(V.displayed_sizes(q), {"bs": None, "as": None})
        q = V.check_quote_response(hdr(), quote_body(bs='"big"'))["quote"]
        self.assertEqual(V.displayed_sizes(q), {"bs": None, "as": "0.4"})
        q = V.check_quote_response(hdr(), quote_body(bs="-1"))["quote"]
        self.assertEqual(V.displayed_sizes(q)["bs"], "-1")                      # evidence kept; Q4 fails
        self.assertIsNone(V.displayed_sizes(V.check_quote_response(None, None)["quote"]))

    def test_G8_01_recorded_even_when_Q_not_evaluated(self):
        out = cycle(last="0")
        self.assertEqual(out["displayed_sizes"], {"bs": "0.5", "as": "0.4"})
        self.assertEqual(set(out["Q"].values()), {"NOT_EVALUATED"})


class SpecFixesF1F2(unittest.TestCase):
    """Fixes F-1 and F-2 (2026-11-26), each asserting R4.2i text: §4.3 D-8 and §10.4 G8-01."""

    def test_F1_quote_non_identity_content_encoding_fails_V1(self):
        out = cycle(qh=hdr(extra=[("Content-Encoding", "gzip")]))
        self.assertEqual(out["V"]["V1"], "FAIL")
        self.assertEqual(out["terminal"], "NO_DECISION (FETCH_FAILED)")
        self.assertEqual(out["V"]["V3"], "NOT_EVALUATED")

    def test_F2_unusable_but_received_quote_gives_null_members(self):
        for kw in (dict(qh=hdr(status=500)), dict(qb=b"{not json"), dict(qb=b'{"quotes":[]}'),
                   dict(qh=b"garbage")):
            with self.subTest(kw=list(kw)):
                out = cycle(last="0", **kw)
                self.assertEqual(out["displayed_sizes"], {"bs": None, "as": None})
                self.assertEqual(out["terminal"], "HOLD")

    def test_F2_unusable_quote_on_BUY_is_QUOTE_INVALID(self):
        out = cycle(last="5", qh=hdr(status=500))
        self.assertEqual(out["terminal"], "NO_DECISION (QUOTE_INVALID)")
        self.assertEqual(set(out["Q"].values()), {"FAIL"})

    def test_F2_no_response_still_null_object(self):
        self.assertIsNone(cycle(last="0", qh=None, qb=None)["displayed_sizes"])


class FullCycle(unittest.TestCase):
    def test_full_BUY_SHADOW_EXPIRED_from_raw_artifacts(self):
        out = cycle(last="5")
        self.assertEqual((out["signal"], out["mapping"], out["terminal"]), (D.BUY, D.PROPOSAL, "SHADOW_EXPIRED"))
        self.assertEqual(list(out["rules"]), D.BUY_RULES)
        self.assertEqual((out["proposal"]["L"], out["proposal"]["q"]), (F(90004), F("0.0016")))
        self.assertEqual(out["V12a"], "PASS")
        self.assertEqual(out["V12b"], "PASS")

    def test_U9_replay_identical(self):
        a = cycle(last="5", store={})
        b = cycle(last="5", store={})
        self.assertEqual(repr(a), repr(b))


if __name__ == "__main__":
    unittest.main()
