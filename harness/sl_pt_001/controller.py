"""SL-PT-001 Stage A harness: cycle controller (Strike 3).

Governing text: frozen R4.2i §6.1-6.5, §5.3-5.4, §8.1, §10.1-10.4, §11.4; TER-1 contract v2.1 (CC-01..CC-05).
Post-exposure work (founder decision v5): every rule cites R4.2i or the contract, never auditor behaviour.

- One OS exclusive APPEND LOCK (chain/append.lock) guards every chain append and every token change (§6.3).
- The RUN LOCK TOKEN (chain/run_token.json) records (manifest, slot index or INJECTION, process id, acquired_at). It is
  harness state, not evidence; every decision about it is also visible in the chain records it produces.
- lock_clock_at is read while holding the append lock; a CYCLE append is refused unless lock_clock_at < T_d(i+1)
  (and >= the ceiling for SHADOW_EXPIRED). Write, flush and fsync happen before the lock is released (§6.4 step 8).
- The bar store is rebuilt from the chain each time (§4.9: "the deterministic fold of every CYCLE record").
I/O to the market is NOT here: a `fetch` callable is supplied (Strike 4 provides the real keyless client).
"""
import json
import os
from fractions import Fraction

from . import decide as D
from . import evidence as E
from . import exact as X
from . import validate as V

NS = X.NS


def bars_clock_ok(bars_header, t_send, t_recv):
    """V12b on the bars response (§5.6), the same predicate run_cycle applies; gates the quote fetch."""
    try:
        _, fields = V.parse_header_artifact(bars_header)
        date = V.header_value(fields, "Date")
    except (ValueError, TypeError, AttributeError):
        date = None
    return V.clock_check(date, t_send, t_recv)[0] == "PASS"


class Refused(Exception):
    """An append or token change refused by §6.3 / §6.4 (the process exits; nothing is written)."""


# --------------------------------------------------------------------------------------- append lock (§6.3)
class AppendLock:
    """OS exclusive lock on chain/append.lock; blocks until acquired. Released by the OS if the process dies."""

    def __init__(self, evidence_root):
        d = os.path.join(evidence_root, "chain")
        os.makedirs(d, exist_ok=True)
        self.path = os.path.join(d, "append.lock")
        self.fh = None

    def __enter__(self):
        self.fh = open(self.path, "a+b")
        if os.name == "nt":
            import msvcrt
            self.fh.seek(0)
            while True:
                try:
                    msvcrt.locking(self.fh.fileno(), msvcrt.LK_LOCK, 1)
                    break
                except OSError:
                    continue
        else:
            import fcntl
            fcntl.flock(self.fh.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, *exc):
        try:
            if os.name == "nt":
                import msvcrt
                self.fh.seek(0)
                msvcrt.locking(self.fh.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.fh.fileno(), fcntl.LOCK_UN)
        finally:
            self.fh.close()
        return False


def _token_path(root):
    return os.path.join(root, "chain", "run_token.json")


def read_token(root):
    p = _token_path(root)
    if not os.path.exists(p):
        return None
    with open(p, "rb") as fh:
        return json.loads(fh.read().decode("utf-8"))


def write_token(root, token):
    """Only ever called while holding the append lock."""
    p = _token_path(root)
    tmp = p + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(json.dumps(token, sort_keys=True).encode("utf-8"))
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, p)


# ----------------------------------------------------------------------------------------- chain queries
def _cycles(records, mh, slot):
    return [r for r in records if r["type"] == "CYCLE" and r["body"]["manifest_sha256"] == mh
            and r["body"]["slot_index"] == str(slot)]


def run_state(records, mh):
    """(opened, closed) for manifest mh, from the chain."""
    opened = closed = False
    for r in records:
        if r["type"] == "RUN_OPEN":
            if r["body"]["manifest_sha256"] == mh:
                opened, closed = True, False
            elif opened and not closed:
                opened = False                                         # a later run opened: mh is not current
        elif r["type"] == "RUN_CLOSE" and opened:
            closed = True
    return opened, closed


def rebuild_store(records):
    """§4.9: the bar store is the deterministic fold of every CYCLE record's transitions, in chain order.
    Injections never enter the store (§6.5, R4.2f D-4)."""
    store = {}
    for r in records:
        if r["type"] != "CYCLE":
            continue
        for e in r["body"]["bar_store_transitions"]:
            t, ev = int(e["t"]), e["event"]
            tup = tuple(e["new"][f] for f in E.BAR_FIELDS) if e["new"] else None
            if ev in ("BASELINED", "CONFIRMED"):
                store[t] = {"tuple": tup, "state": e["state"], "count": int(e["observation_count"]), "pending": None}
            elif ev == "OBSERVED":
                store[t]["count"] = int(e["observation_count"])
            elif ev == "SOURCE_REVISION":
                store[t]["pending"], store[t]["state"] = tup, "PENDING"
    return store


# --------------------------------------------------------------------------------------- harness process
class Harness:
    """One harness process. `clock` returns integer ns (UTC wall clock, §5.6); `sleep` takes seconds as a Fraction."""

    def __init__(self, evidence_root, clock, sleep=None, pid=None):
        self.root, self.clock = evidence_root, clock
        self.sleep = sleep or (lambda s: None)
        self.pid = os.getpid() if pid is None else pid

    # -- records written by the harness on the founder's command
    def genesis(self, frozen_set_hashes):
        with AppendLock(self.root):
            return E.append_record(self.root, "GENESIS", {"experiment_id": "SL-PT-001",
                                                          "frozen_set_hashes": frozen_set_hashes})

    def run_stopped(self, manifest_raw):
        m, mh = E.validate_manifest(manifest_raw)
        with AppendLock(self.root):
            if run_state(E.read_chain(self.root), mh) != (True, False):
                raise Refused("RUN_STOPPED needs an open run")
            return E.append_record(self.root, "RUN_STOPPED", {"instant": str(self.clock())})

    def run_close(self, manifest_raw, invocation_log_bytes, task_xml_bytes):
        """§10.1 RUN_CLOSE after T_d(N); first a CYCLE_OVERRUN if slot N-1 holds the token without a terminal."""
        m, mh = E.validate_manifest(manifest_raw)
        T0, N = int(m["T_d0"]), m["declared_slots"]
        with AppendLock(self.root):
            if self.clock() < X.T_d(T0, N):
                raise Refused("RUN_CLOSE only after T_d(N)")
            recs = E.read_chain(self.root)
            if run_state(recs, mh) != (True, False):
                raise Refused("RUN_CLOSE needs an open run")
            tok = read_token(self.root)
            if tok and tok["manifest"] == mh and tok["kind"] == "SLOT" and tok["slot"] == N - 1 \
                    and not _cycles(recs, mh, N - 1):
                E.append_record(self.root, "CYCLE_OVERRUN", {"slot_index": str(N - 1), "old_process_id": str(tok["pid"])})
            write_token(self.root, None)
            return E.append_record(self.root, "RUN_CLOSE", {
                "invocation_log_sha256": E.sha256_hex(invocation_log_bytes),
                "task_xml_sha256": E.sha256_hex(task_xml_bytes)})

    # -- one scheduled invocation (§6.2-6.4)
    def invoke(self, manifest_raw, invocation_ns, boundary, fetch_bars, fetch_quote):
        """`boundary()` -> (result, evidence, config_bytes): V12a on this process's own observations (§6.4 step 1).
        `fetch_bars(T_d)` -> {url, sent, recv, header, body}; header/body None and recv None when no HTTP response.
        `fetch_quote()` -> the same shape; called only after V12b passes (§6.4 steps 3-4).
        Returns the record written (CYCLE or an anomaly record); raises Refused when §6.3/§6.4 forbid the append."""
        m, mh = E.validate_manifest(manifest_raw)
        T0, N = int(m["T_d0"]), m["declared_slots"]
        j = X.owning_slot(invocation_ns, T0, N)
        with AppendLock(self.root):
            recs = E.read_chain(self.root)
            if not recs:
                raise Refused("no GENESIS: the chain must exist before a run")
            if j is None:                                              # §6.2: OFF_RUN, nothing else
                return E.append_record(self.root, "OFF_RUN", {"invocation_instant": str(invocation_ns)})
            opened, closed = run_state(recs, mh)
            if closed:
                raise Refused("the run is closed")
            if not opened:                                             # RUN_OPEN at the first invocation (§10.1)
                if recs[-1]["hash"] != m["prev_chain_head"]:
                    raise Refused("RUN_OPEN must directly follow the manifest's prev_chain_head")
                E.append_record(self.root, "RUN_OPEN", {"manifest_sha256": mh})
                recs = E.read_chain(self.root)
            tok = read_token(self.root)
            dup = {"slot_index": str(j), "invocation_instant": str(invocation_ns)}
            if _cycles(recs, mh, j):                                    # CYCLE already exists (replay protection)
                return E.append_record(self.root, "CONCURRENT_INVOCATION", dup)
            if tok and tok["kind"] == "SLOT" and tok["manifest"] == mh and tok["slot"] == j:
                return E.append_record(self.root, "CONCURRENT_INVOCATION", dup)       # same slot already running
            if tok and tok["kind"] == "INJECTION":                     # a slot invocation aborts an injection
                E.append_record(self.root, "INJECTION_ABORTED", {"proposal": None, "result": "INJECTION_ABORTED"})
            elif tok and tok["kind"] == "SLOT" and tok["manifest"] == mh and tok["slot"] < j \
                    and not _cycles(recs, mh, tok["slot"]):            # overrun, written by the successor
                E.append_record(self.root, "CYCLE_OVERRUN",
                                {"slot_index": str(tok["slot"]), "old_process_id": str(tok["pid"])})
            token = {"kind": "SLOT", "manifest": mh, "slot": j, "pid": self.pid, "acquired_at": str(self.clock())}
            write_token(self.root, token)
            store = rebuild_store(E.read_chain(self.root))
        return self._cycle(m, mh, j, invocation_ns, token, store, boundary, fetch_bars, fetch_quote)

    def _request(self, f):
        got = f["header"] is not None or f["body"] is not None
        req = {"url": f["url"], "sent_at": str(f["sent"]), "received_at": str(f["recv"]) if got else None,
               "outcome": "RESPONSE" if got else "NO_RESPONSE"}
        hashes = (E.put_artifact(self.root, f["body"]), E.put_artifact(self.root, f["header"])) if got else (None, None)
        return req, hashes                                             # artifacts stored BEFORE parsing (§4.3)

    def _cycle(self, m, mh, j, invocation_ns, token, store, boundary, fetch_bars, fetch_quote):
        T_d = X.T_d(int(m["T_d0"]), j)
        res, evid, cfg = boundary()                                    # step 1
        ctx = {"manifest_sha256": mh, "slot_index": j, "invocation_instant": invocation_ns, "T_d": T_d,
               "policy_sha256": m["policy_sha256"], "V12a_evidence": evid, "bars_request": None,
               "quote_request": None, "bars_sha256": None, "bars_headers_sha256": None, "quote_sha256": None,
               "quote_headers_sha256": None}
        bh = bb = qh = qb = t_send = t_recv = None
        if res == "PASS":
            E.put_artifact(self.root, cfg)                             # passing V12a config bytes (contract §6)
            fb = fetch_bars(T_d)                                       # step 2
            bh, bb, t_send, t_recv = fb["header"], fb["body"], fb["sent"], fb["recv"]
            ctx["bars_request"], (ctx["bars_sha256"], ctx["bars_headers_sha256"]) = self._request(fb)
            if ctx["bars_request"]["outcome"] == "RESPONSE" and bars_clock_ok(bh, t_send, t_recv):
                fq = fetch_quote()                                     # step 4, only after V12b passes
                qh, qb = fq["header"], fq["body"]
                ctx["quote_request"], (ctx["quote_sha256"], ctx["quote_headers_sha256"]) = self._request(fq)
        created = self.clock()                                         # checkpoint (a) (§5.3)
        ledger = D.ShadowLedger(cash=X.parse_number_token(m["opening_cash"]))   # Stage A: no fills (§8.1)
        cyc = D.run_cycle((res, evid, res == "PASS"), bh, bb, t_send, t_recv, qh, qb, T_d, created, ledger, store)
        if cyc["terminal"] == "SHADOW_EXPIRED":                         # §5.3: recorded at the ceiling
            while self.clock() < X.ceiling(T_d):
                self.sleep(Fraction(X.ceiling(T_d) - self.clock(), NS))
        with AppendLock(self.root):                                    # step 8
            lock_clock_at = self.clock()
            if read_token(self.root) != token:
                raise Refused("run token lost: the append is refused (§6.3; U83)")
            if lock_clock_at >= X.T_d(T_d, 1):
                raise Refused("append not begun before T_d(i+1): overrun (§6.4 step 8; U117a)")
            if cyc["terminal"] == "SHADOW_EXPIRED" and lock_clock_at < X.ceiling(T_d):
                raise Refused("SHADOW_EXPIRED before the ceiling (U117b)")
            ctx["lock_clock_at"] = lock_clock_at
            rec = E.append_record(self.root, "CYCLE", E.build_scheduled_ter(ctx, cyc, store))
            write_token(self.root, None)                               # the terminal releases the token
            return rec

    # -- founder-commanded injection (§6.5, §11.4)
    def inject(self, manifest_raw, plan_bytes, fixture_bytes, intended_rule, command_ns, boundary):
        """Run one BUY fixture as an INJECTION. Plan and fixture must be committed and pushed BEFORE this (founder);
        the auditor checks that from history. Here: shape, plan membership, timing, token, and the TER."""
        m, mh = E.validate_manifest(manifest_raw)
        T0, N = int(m["T_d0"]), m["declared_slots"]
        fh = E.sha256_hex(fixture_bytes)
        plan = V.parse_json_tokens(plan_bytes)
        E._closed(plan, ["injections"], "plan")
        if sum(1 for e in plan["injections"] if e == {"fixture_sha256": fh, "intended_rule": intended_rule}) != 1:
            raise Refused("the plan does not name this fixture with this intended rule exactly once")
        fx = parse_fixture(fixture_bytes)
        if fx["policy_sha256"] != m["policy_sha256"]:
            raise Refused("fixture policy hash differs from the manifest's")
        with AppendLock(self.root):
            recs = E.read_chain(self.root)
            if run_state(recs, mh) != (True, False):
                raise Refused("injections run only while a run is open (§6.5)")
            nxt = X.T_d(T0, (command_ns - T0) // (300 * NS) + 1) if command_ns >= T0 else T0
            if nxt - command_ns < 30 * NS:
                raise Refused("an injection may not start within 30 s of the next T_d (§6.5)")
            tok = read_token(self.root)
            if tok and tok["kind"] == "SLOT" and tok["manifest"] == mh and not _cycles(recs, mh, tok["slot"]):
                raise Refused("a slot cycle is in progress")
            token = {"kind": "INJECTION", "manifest": mh, "slot": None, "pid": self.pid, "acquired_at": str(self.clock())}
            write_token(self.root, token)
        v12a = boundary()
        if v12a[0] == "PASS":
            E.put_artifact(self.root, v12a[2])
        res = run_injection(fx, v12a)
        q_hash = E.put_artifact(self.root, fx["quote_bytes"]) if v12a[0] == "PASS" else None
        with AppendLock(self.root):
            lock_clock_at = self.clock()
            if read_token(self.root) != token:
                raise Refused("injection aborted by a slot invocation (§6.3 row 5)")
            ter = E.build_injected_ter({"manifest_sha256": mh, "invocation_instant": command_ns, "T_d": fx["T_d"],
                                        "policy_sha256": m["policy_sha256"], "V12a_evidence": v12a[1],
                                        "lock_clock_at": lock_clock_at, "quote_sha256": q_hash,
                                        "injection": {"plan_sha256": E.sha256_hex(plan_bytes), "fixture_sha256": fh,
                                                      "intended_rule": intended_rule}}, res)
            rec = E.append_record(self.root, "INJECTION", ter)
            write_token(self.root, None)
            return rec


FIXTURE_KEYS = ["instrument", "quote_body_hex", "T_d", "created", "shadow_cash", "shadow_btc", "shadow_reserved",
                "shadow_reserved_btc", "open_authorizations", "policy_sha256"]           # contract v2 §7


def parse_fixture(raw):
    f = V.parse_json_tokens(raw)
    E._closed(f, FIXTURE_KEYS, "fixture")
    for k in ("T_d", "created"):
        E._ns(f[k])
    for k in ("shadow_cash", "shadow_btc", "shadow_reserved", "shadow_reserved_btc"):
        E._dec(f[k])
    E._hash(f["policy_sha256"])
    if not isinstance(f["open_authorizations"], list) or int(f["created"]) < int(f["T_d"]):
        raise Refused("fixture shape")
    hexs = f["quote_body_hex"]
    if not (isinstance(hexs, str) and len(hexs) % 2 == 0 and all(c in "0123456789abcdef" for c in hexs)):
        raise Refused("quote_body_hex must be lowercase hex")
    cash, btc = X.parse_number_token(f["shadow_cash"]), X.parse_number_token(f["shadow_btc"])
    res, res_btc = X.parse_number_token(f["shadow_reserved"]), X.parse_number_token(f["shadow_reserved_btc"])
    if not (cash >= 0 and 0 <= res <= cash and 0 <= res_btc <= btc and (cash * 100).denominator == 1
            and (res * 100).denominator == 1):
        raise Refused("fixture ledger (contract v2 §7)")
    if not (btc < Fraction(1, 10000) and not f["open_authorizations"]):
        raise Refused("a runtime injection is a normally constructed flat BUY (contract v2 §7)")
    return {"instrument": f["instrument"], "quote_bytes": bytes.fromhex(hexs), "T_d": int(f["T_d"]),
            "created": int(f["created"]), "cash": cash, "btc": btc, "reserved": res, "reserved_btc": res_btc,
            "policy_sha256": f["policy_sha256"]}


def run_injection(fx, v12a):
    """The injected decision path (§6.5; contract v2 §2 injected rows): V12a, then Q on the fixture quote (keyed by the
    fixture instrument), then a normally constructed BUY, every applicable rule, disposition at once."""
    out = {"V12a": v12a[0], "displayed_sizes": None, "Q": None, "proposal": None, "rules": None, "created": None}
    if v12a[0] != "PASS":
        out["terminal"] = "BOUNDARY_FAIL"
        return out
    try:
        doc = V.parse_json_tokens(fx["quote_bytes"])
        q = doc["quotes"][fx["instrument"]]
        quote = {k: V._numeric_or_marker(q[k]) for k in ("bp", "ap", "bs", "as") if k in q}
        if "t" in q:
            quote["t"] = q["t"] if isinstance(q["t"], str) and not isinstance(q["t"], V.NumTok) else V.NonNumeric(q["t"])
    except (ValueError, TypeError, KeyError, AttributeError):
        quote = None
    out["displayed_sizes"] = V.displayed_sizes(quote, True)
    out["Q"] = V.validate_quote(quote)
    if any(v == "FAIL" for v in out["Q"].values()):
        out["terminal"] = "NO_DECISION (QUOTE_INVALID)"
        return out
    lg = D.ShadowLedger(cash=fx["cash"], btc=fx["btc"])
    lg.reserved_usd, lg.reserved_btc = fx["reserved"], fx["reserved_btc"]
    qv = V.quote_values(quote)
    policy = dict(D.POLICY, instrument="BTC/USD")
    p = D.construct("BUY", qv["bid"], qv["ask"], lg, policy)
    p["instrument"] = fx["instrument"]                                 # R1 fixture may be off the allowlist
    out["created"] = fx["created"]
    out["proposal"] = p
    out["rules"] = D.evaluate(p, qv, fx["created"], fx["T_d"], lg, policy)
    out.update(D.disposition(out["rules"]))                           # SHADOW_EXPIRED recorded at once (no ceiling)
    return out
