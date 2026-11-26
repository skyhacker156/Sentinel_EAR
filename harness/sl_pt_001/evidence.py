"""SL-PT-001 Stage A harness: evidence infrastructure (Strike 2).

Governing text: frozen R4.2i §10.1-10.5, §4.3 (artifacts), §7.4 (policy file), §10.3 (manifest); TER-1 interface
contract v2 (SHA-256 5e563068..., committed b5ed809) §§1-6 for every key name, type and layout choice.
Post-exposure work (founder decision v5): every rule below cites R4.2i or contract v2, never auditor behaviour.
Where contract v2 is silent, the choice is marked CONTRACT GAP and listed in the Strike 2 report.

Scope: canonical JSON (RFC 8785, restricted domain), record hashing, chain append and verification, content-
addressed artifacts, the policy file, manifest validation, TER-1 assembly and closed-schema self-check.
NOT here (Strike 3): the append lock and run token, lock_clock_at sampling, fsync timing, the scheduler.
"""
import hashlib
import os

from . import exact as X

SAFE_MAX = 9007199254740991
NUMS = ["S20_k", "S50_k", "S20_prev", "S50_prev", "D_prev", "D_k"]
CLOCK = ["t_send", "t_recv", "D", "θ_low", "θ_high"]
ART = ["bars_sha256", "bars_headers_sha256", "quote_sha256", "quote_headers_sha256"]
ARRAYS = ["completed_bars", "excluded_bars", "bar_store_transitions", "rule_results", "used_bars"]
V_CHECKS = ["V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9", "V10", "V11", "V12a", "V12b"]
Q_CHECKS = ["Q1", "Q2", "Q3", "Q4", "Q5"]
BAR_FIELDS = ("o", "h", "l", "c", "v", "vw", "n")
ROUNDING = ["bid", "ask", "price_increment", "qty_increment", "min_order_size", "f_res", "shadow_cash",
            "shadow_reserved", "cash_available", "budget", "shadow_btc", "shadow_reserved_btc"]
TER_KEYS = (["schema", "origin", "manifest_sha256", "slot_index", "cycle_id", "invocation_instant", "T_d", "created",
             "bars_request", "quote_request"] + ART + ["completed_bars", "excluded_bars", "bar_store_transitions"]
            + V_CHECKS + Q_CHECKS + NUMS + ["signal", "mapping", "proposal", "rule_results", "terminal_state",
            "policy_sha256", "displayed_sizes", "egress_scope"] + CLOCK
            + ["lock_clock_at", "V12a_evidence", "injection", "used_bars"])                  # contract v2 §2
REASONS = {"V12A_FAILED", "V12B_FAILED", "FETCH_FAILED", "DATA_INVALID", "NO_PROPOSAL", "INJECTED"}
NO_DECISION = ["FETCH_FAILED", "INCOMPLETE_RESPONSE", "MALFORMED_VALUE", "DATA_CONFLICT", "STALE_SERIES",
               "DATA_GAP", "INSUFFICIENT_HISTORY", "SOURCE_REVISION", "QUOTE_INVALID"]
TERMINALS = {"HOLD", "NO_ACTION", "REJECTED", "SHADOW_EXPIRED", "BOUNDARY_FAIL", "CYCLE_OVERRUN"} | {
    f"NO_DECISION ({r})" for r in NO_DECISION}
MAPPINGS = {None, "PROPOSAL", "HOLD", "NO_ACTION", "NO_ACTION (BLOCKED_OPEN_ORDER)"}
EVENTS = {"BASELINED", "OBSERVED", "SOURCE_REVISION", "CONFIRMED", "DISAPPEARED", "DUPLICATE_COLLAPSED"}
RECORD_BODIES = {                                                                            # contract v2 §3
    "GENESIS": ["experiment_id", "frozen_set_hashes"], "RUN_OPEN": ["manifest_sha256"],
    "CYCLE_OVERRUN": ["slot_index", "old_process_id"], "CONCURRENT_INVOCATION": ["slot_index", "invocation_instant"],
    "OFF_RUN": ["invocation_instant"], "INJECTION_ABORTED": ["proposal", "result"], "RUN_STOPPED": ["instant"],
    "RUN_CLOSE": ["invocation_log_sha256", "task_xml_sha256"]}
MANIFEST_KEYS = ["instrument", "T_d0", "declared_slots", "opening_cash", "frozen_set_hashes", "harness_sha256",
                 "policy_sha256", "task_xml_sha256", "wrapper_sha256", "prev_chain_head"]       # contract v2 §3
SPEC_PATH = "experiments/sl-pt-001/SL-PT-001_R4.2i_Stage_A_Amendment_Candidate_Claude_2026-11-26.md"
SPEC_SHA256 = "4259551121fa3d271074fb13da51fb270ae859b0b516a953752731f20972a51a"


class EvidenceError(ValueError):
    """Schema, integrity or custody failure. Raised before anything is written."""


def sha256_hex(b):
    return hashlib.sha256(b).hexdigest()


# ----------------------------------------------------------------------------- RFC 8785 JCS (contract v2 §6)
def _jcs_string(s):
    out = ['"']
    for ch in s:
        o = ord(ch)
        if 0xD800 <= o <= 0xDFFF:
            raise EvidenceError("lone surrogate in string")
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif o < 0x20:
            out.append({8: "\\b", 9: "\\t", 10: "\\n", 12: "\\f", 13: "\\r"}.get(o, "\\u%04x" % o))
        else:
            out.append(ch)                                     # no Unicode escaping or normalization
    out.append('"')
    return "".join(out)


def jcs(value):
    """Canonical JSON text (RFC 8785) over the contract's domain: null, strings, safe non-negative JSON
    integers (outside TERs only), arrays and objects. Booleans and non-integer numbers are refused (§10.4, §10.5)."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        raise EvidenceError("JSON booleans are not admitted")
    if isinstance(value, str):
        return _jcs_string(value)
    if isinstance(value, int):
        if not 0 <= value <= SAFE_MAX:
            raise EvidenceError("integer outside the safe non-negative range")
        return str(value)
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(jcs(v) for v in value) + "]"
    if isinstance(value, dict):
        for k in value:
            if not isinstance(k, str):
                raise EvidenceError("object key is not a string")
        keys = sorted(value, key=lambda k: k.encode("utf-16-be"))         # unsigned UTF-16 code units
        return "{" + ",".join(_jcs_string(k) + ":" + jcs(value[k]) for k in keys) + "}"
    raise EvidenceError(f"unsupported JSON value: {type(value).__name__}")


def jcs_bytes(value):
    return jcs(value).encode("utf-8")


def record_hash(seq, prev_hash, rtype, body):
    """§10.1: SHA-256 of the canonical serialization of the record without `hash` (contract v2 §6)."""
    return sha256_hex(jcs_bytes({"seq": seq, "prev_hash": prev_hash, "type": rtype, "body": body}))


# ------------------------------------------------------------------------------------- scalar validators
def _hash(x, nullable=False):
    if x is None and nullable:
        return
    if not (isinstance(x, str) and len(x) == 64 and all(c in "0123456789abcdef" for c in x)):
        raise EvidenceError(f"not a lowercase SHA-256: {x!r}")


def _ns(x, nullable=False):
    if x is None and nullable:
        return
    if not (isinstance(x, str) and (x.lstrip("-").isdigit()) and x == str(int(x))):
        raise EvidenceError(f"not an integer string: {x!r}")


def _dec(x, nullable=False):
    if x is None and nullable:
        return
    try:
        X.parse_number_token(x)
    except X.MalformedValue:
        raise EvidenceError(f"not an exact decimal string: {x!r}")


def _closed(obj, keys, what):
    if not isinstance(obj, dict) or set(obj) != set(keys):
        raise EvidenceError(f"{what}: closed key set differs: {sorted(set(obj) ^ set(keys)) if isinstance(obj, dict) else obj!r}")


def _no_numbers(x, path="TER"):
    """§10.4: null is the only non-string scalar in a TER; no JSON numbers or booleans (U88)."""
    if isinstance(x, dict):
        for k, v in x.items():
            _no_numbers(v, f"{path}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            _no_numbers(v, f"{path}[{i}]")
    elif not (x is None or isinstance(x, str)):
        raise EvidenceError(f"{path}: non-string scalar {x!r} (U88)")


def dec_str(x):
    """Exact decimal string of a Fraction (contract v2 §1: no rational slash; terminating decimals only)."""
    return X.to_decimal_string(x)


# ----------------------------------------------------------------------------- artifacts (§10.2, §4.3)
def put_artifact(evidence_root, data):
    """Store raw bytes at artifacts/<sha256>. Idempotent; an existing file with different bytes is an integrity
    failure. Returns the hash. Caller stores BEFORE parsing (§4.3 item 1)."""
    h = sha256_hex(data)
    d = os.path.join(evidence_root, "artifacts")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, h)
    if os.path.exists(p):
        with open(p, "rb") as fh:
            if fh.read() != data:
                raise EvidenceError(f"artifact {h} exists with different bytes")
        return h
    tmp = p + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, p)
    return h


def read_artifact(evidence_root, h):
    _hash(h)
    with open(os.path.join(evidence_root, "artifacts", h), "rb") as fh:
        data = fh.read()
    if sha256_hex(data) != h:
        raise EvidenceError(f"artifact {h} does not hash to its name")
    return data


# ------------------------------------------------------------------------------ policy file (§7.4)
POLICY_DOC = {                                                     # contract v2 §4, exact expected values
    "price_increment": {"value": "1", "source": "support_table_DOCUMENTED", "status": "UNVERIFIED"},
    "qty_increment": {"value": "0.0001", "source": "support_table_DOCUMENTED", "status": "UNVERIFIED"},
    "min_order_size": {"value": "0.0001", "source": "support_table_DOCUMENTED", "status": "UNVERIFIED"},
    "f_res": "0.0025", "settle_s": "60", "W_s": "90", "freshness_s": "15",
    "rules": {"R1": "BTC/USD", "R2": "LIMIT", "R3": "SCHEMA_VALID", "R4": "15", "R5": "0.01", "R6": "CASH_AVAILABLE",
              "R7": "150", "R8": "300", "R9": "BTC_AVAILABLE", "R10": "INCREMENTS_AND_MINIMUM", "R11": "ONE_OPEN",
              "R12": "450", "R13": "90", "R15": "EXIT_LONG", "R16": "NO_OPEN_OR_UNRESOLVED"}}


def policy_bytes():
    """The P-0.2 policy file bytes. Contract v2.1 CC-02: any valid layout is acceptable provided the same raw-byte
    hash is used everywhere and the bytes never change once pinned; the harness writes JCS bytes, no trailing newline."""
    return jcs_bytes(POLICY_DOC)


def check_policy_matches_harness(decide_policy):
    """The harness's in-code policy constants must equal the policy file (§7.4: one policy, one hash)."""
    from fractions import Fraction as F
    p = POLICY_DOC
    want = {"price_increment": F(p["price_increment"]["value"]), "qty_increment": F(p["qty_increment"]["value"]),
            "min_order_size": F(p["min_order_size"]["value"]), "f_res": F(p["f_res"]),
            "freshness_s": int(p["freshness_s"]), "W_s": int(p["W_s"]), "R5_band": F(p["rules"]["R5"]),
            "R7_cap": F(p["rules"]["R7"]), "R8_cap": F(p["rules"]["R8"]), "R12_floor": F(p["rules"]["R12"]),
            "instrument": p["rules"]["R1"]}
    diff = {k: (decide_policy.get(k), v) for k, v in want.items() if decide_policy.get(k) != v}
    if diff or X.SETTLE_S != int(p["settle_s"]):
        raise EvidenceError(f"harness policy constants differ from the policy file: {diff}")


# --------------------------------------------------------------------------- manifest (§10.3, contract §3)
def validate_manifest(raw):
    """Parse and validate a founder manifest. Returns (manifest, sha256 of raw bytes) (§10.3; U42; U72)."""
    from . import validate as Vd
    try:
        m = Vd.parse_json_tokens(raw)
    except ValueError as exc:
        raise EvidenceError(f"manifest is not strict JSON: {exc}")
    _closed(m, MANIFEST_KEYS, "manifest")
    if m["instrument"] != "BTC/USD":
        raise EvidenceError("manifest instrument")
    _ns(m["T_d0"])
    if not X.valid_T_d0(int(m["T_d0"])):
        raise EvidenceError("T_d0 off the decision grid")
    n = m["declared_slots"]
    if not (isinstance(n, Vd.NumTok) and str(n).isdigit() and 30 <= int(n) <= SAFE_MAX):
        raise EvidenceError("declared_slots must be a JSON integer >= 30 (U42)")
    if not (isinstance(m["opening_cash"], str) and not isinstance(m["opening_cash"], Vd.NumTok)):
        raise EvidenceError("opening_cash must be a decimal string")
    if X.parse_number_token(m["opening_cash"]) != 500:
        raise EvidenceError("opening_cash must be 500.00")
    fs = m["frozen_set_hashes"]
    if not isinstance(fs, dict) or fs.get(SPEC_PATH) != SPEC_SHA256:
        raise EvidenceError("frozen_set_hashes must map the R4.2i path to its SHA-256")
    for v in fs.values():
        _hash(v)
    for k in ("harness_sha256", "policy_sha256", "task_xml_sha256", "wrapper_sha256", "prev_chain_head"):
        _hash(m[k])
    m = dict(m, declared_slots=int(n))
    return m, sha256_hex(raw)


# ------------------------------------------------------------------------------ chain (§10.1, §11.3 step 1)
def chain_path(evidence_root):
    return os.path.join(evidence_root, "chain", "events.jsonl")


def read_chain(evidence_root):
    """Parse and verify the whole chain from GENESIS: contiguous seq, prev_hash, hash and record schema
    (U43, U70, U114). Returns the list of records. Raises EvidenceError on the first failure."""
    from . import validate as Vd
    p = chain_path(evidence_root)
    if not os.path.exists(p):
        return []
    with open(p, "rb") as fh:
        data = fh.read()
    if data and not data.endswith(b"\n"):
        raise EvidenceError("chain does not end with LF")
    records, prev = [], None
    for i, line in enumerate(data.split(b"\n")[:-1] if data else []):
        if not line or line.endswith(b"\r"):
            raise EvidenceError(f"line {i + 1}: blank or CRLF line")
        try:
            r = Vd.parse_json_tokens(line)
        except ValueError as exc:
            raise EvidenceError(f"line {i + 1}: not strict JSON: {exc}")
        _closed(r, ["seq", "prev_hash", "type", "body", "hash"], f"line {i + 1} envelope")
        if not (isinstance(r["seq"], Vd.NumTok) and str(r["seq"]) == str(i)):
            raise EvidenceError(f"line {i + 1}: seq is not {i}")
        seq = int(r["seq"])
        if (i == 0) != (r["type"] == "GENESIS") or (i == 0 and r["prev_hash"] is not None) or (i > 0 and r["prev_hash"] != prev):
            raise EvidenceError(f"line {i + 1}: GENESIS position or prev_hash mismatch")
        body = _untoken(r["body"])
        validate_body(r["type"], body)
        if record_hash(seq, r["prev_hash"], r["type"], body) != r["hash"]:
            raise EvidenceError(f"line {i + 1}: record hash mismatch")
        records.append({"seq": seq, "prev_hash": r["prev_hash"], "type": r["type"], "body": body, "hash": r["hash"]})
        prev = r["hash"]
    return records


def _untoken(x):
    """Bodies never contain JSON numbers except the contract's safe integers (none inside TERs)."""
    from . import validate as Vd
    if isinstance(x, dict):
        return {k: _untoken(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_untoken(v) for v in x]
    if isinstance(x, Vd.NumTok):
        if not str(x).isdigit():
            raise EvidenceError("non-integer JSON number in a chain body")
        return int(x)
    if isinstance(x, bool):
        raise EvidenceError("JSON boolean in a chain body")
    return x


def append_record(evidence_root, rtype, body):
    """Append one record after verifying the existing chain (§10.1). Returns the record.
    The append lock, run token and lock_clock_at gate wrap this call in Strike 3 (§6.3, §6.4 step 8).
    Write, flush and fsync happen here; the caller releases the lock only after this returns."""
    validate_body(rtype, body)
    records = read_chain(evidence_root)
    seq = len(records)
    if (seq == 0) != (rtype == "GENESIS"):
        raise EvidenceError("GENESIS must be the first and only first record")
    prev = records[-1]["hash"] if records else None
    rec = {"seq": seq, "prev_hash": prev, "type": rtype, "body": body,
           "hash": record_hash(seq, prev, rtype, body)}
    line = jcs_bytes(rec) + b"\n"
    os.makedirs(os.path.dirname(chain_path(evidence_root)), exist_ok=True)
    with open(chain_path(evidence_root), "ab") as fh:
        fh.write(line)
        fh.flush()
        os.fsync(fh.fileno())
    return rec


def validate_body(rtype, body):
    if rtype in ("CYCLE", "INJECTION"):
        validate_ter(body)
        if body["origin"] != ("SCHEDULED" if rtype == "CYCLE" else "INJECTED"):
            raise EvidenceError("record type and TER origin disagree")
        return
    if rtype not in RECORD_BODIES:
        raise EvidenceError(f"unknown record type {rtype!r}")
    _closed(body, RECORD_BODIES[rtype], rtype)
    for k, v in body.items():
        if k.endswith("sha256"):
            _hash(v)
        elif k in ("slot_index", "old_process_id", "invocation_instant", "instant"):
            _ns(v)
    if rtype == "GENESIS":
        if body["experiment_id"] != "SL-PT-001" or not isinstance(body["frozen_set_hashes"], dict):
            raise EvidenceError("GENESIS body")
        if body["frozen_set_hashes"].get(SPEC_PATH) != SPEC_SHA256:
            raise EvidenceError("GENESIS frozen_set_hashes must pin R4.2i")
        for v in body["frozen_set_hashes"].values():
            _hash(v)
    if rtype == "INJECTION_ABORTED" and body["result"] != "INJECTION_ABORTED":
        raise EvidenceError("INJECTION_ABORTED result")


# ------------------------------------------------------------------------------- TER-1 closed schema
def _check(c, name):
    _closed(c, ["result", "reason"], name)
    if c["result"] in ("PASS", "FAIL"):
        if c["reason"] is not None:
            raise EvidenceError(f"{name}: PASS/FAIL carries a reason")
    elif c["result"] == "NOT_EVALUATED":
        if c["reason"] not in REASONS:
            raise EvidenceError(f"{name}: NOT_EVALUATED reason {c['reason']!r}")
    else:
        raise EvidenceError(f"{name}: result {c['result']!r}")


def _tuple(t, name):
    _closed(t, list(BAR_FIELDS), name)
    for v in t.values():
        _dec(v)


def validate_ter(t):
    """Closed TER-1 schema (contract v2 §2; §10.4; U67, U88) plus the presence rules this harness relies on.
    A failure here stops the append: the harness never writes a TER it cannot validate."""
    _closed(t, TER_KEYS, "TER")
    _no_numbers(t)
    if t["schema"] != "TER-1" or t["origin"] not in ("SCHEDULED", "INJECTED") or t["egress_scope"] != "CLIENT_ALLOWLIST_ONLY":
        raise EvidenceError("TER identity fields")
    if t["terminal_state"] not in TERMINALS or t["signal"] not in (None, "BUY", "EXIT", "HOLD") or t["mapping"] not in MAPPINGS:
        raise EvidenceError("TER enum fields")
    _hash(t["manifest_sha256"])
    _hash(t["policy_sha256"])
    for k in ART:
        _hash(t[k], nullable=True)
    for k in CLOCK + ["slot_index", "invocation_instant", "T_d", "created"]:
        _ns(t[k], nullable=True)
    _ns(t["lock_clock_at"])
    for k in NUMS:
        _dec(t[k], nullable=True)
    for k in V_CHECKS + Q_CHECKS:
        _check(t[k], k)
    ev = t["V12a_evidence"]
    _closed(ev, ["env_credential_names", "config_sha256", "client_allowlist"], "V12a_evidence")
    _hash(ev["config_sha256"], nullable=True)
    if not (isinstance(ev["env_credential_names"], list) and isinstance(ev["client_allowlist"], list)):
        raise EvidenceError("V12a_evidence arrays")
    if ev["config_sha256"] is None and t["V12a"]["result"] != "FAIL":
        raise EvidenceError("unreadable config must fail V12a")
    if t["origin"] == "SCHEDULED":
        if t["injection"] is not None or t["slot_index"] is None or t["cycle_id"] is None:
            raise EvidenceError("scheduled identity")
        cid = t["cycle_id"]
        if not (isinstance(cid, list) and len(cid) == 2 and cid[0] == "BTC/USD"):
            raise EvidenceError("cycle_id shape")
        _ns(cid[1])
    else:
        inj = t["injection"]
        _closed(inj, ["plan_sha256", "fixture_sha256", "intended_rule"], "injection")
        _hash(inj["plan_sha256"])
        _hash(inj["fixture_sha256"])
        if t["slot_index"] is not None or t["cycle_id"] is not None:
            raise EvidenceError("an injection occupies no slot")
    for k in ("bars_request", "quote_request"):
        r = t[k]
        if r is not None:
            _closed(r, ["url", "sent_at", "received_at", "outcome"], k)
            _ns(r["sent_at"])
            if r["outcome"] == "RESPONSE":
                _ns(r["received_at"])
            elif r["outcome"] == "NO_RESPONSE":
                if r["received_at"] is not None:
                    raise EvidenceError(f"{k}: NO_RESPONSE with received_at")
            else:
                raise EvidenceError(f"{k}: outcome")
    for k in ARRAYS:
        if not isinstance(t[k], list):
            raise EvidenceError(f"{k} must be an array")
    for b in t["completed_bars"] + t["excluded_bars"]:
        _closed(b, ["t", *BAR_FIELDS, "zero_volume"], "Bar")
        _ns(b["t"], nullable=True)
        for f in BAR_FIELDS:
            _dec(b[f], nullable=True)
        if b["zero_volume"] not in (None, "TRUE", "FALSE"):
            raise EvidenceError("zero_volume")
    for e in t["bar_store_transitions"]:
        _closed(e, ["t", "event", "old", "new", "state", "observation_count"], "Transition")
        _ns(e["t"])
        if e["event"] not in EVENTS or e["state"] not in (None, "BASELINED", "PENDING", "CONFIRMED"):
            raise EvidenceError("Transition enums")
        for k in ("old", "new"):
            if e[k] is not None:
                _tuple(e[k], f"Transition.{k}")
        _ns(e["observation_count"], nullable=True)
    for u in t["used_bars"]:
        _closed(u, ["t", "state", "observation_count"], "UsedBar")
    if t["used_bars"] and len(t["used_bars"]) != 51:
        raise EvidenceError("used_bars must be empty or exactly 51")
    seen = []
    for r in t["rule_results"]:
        _closed(r, ["rule", "result"], "RuleResult")
        if r["result"] not in ("PASS", "FAIL") or r["rule"] in seen:
            raise EvidenceError("RuleResult")
        seen.append(r["rule"])
    if seen != sorted(seen, key=lambda c: int(c[1:])):
        raise EvidenceError("rule_results must be in numeric code order")
    if t["proposal"] is not None:
        p = t["proposal"]
        _closed(p, ["instrument", "side", "order_type", "L", "q", "R", "rounding_inputs"], "Proposal")
        for k in ("L", "q", "R"):
            _dec(p[k])
        _closed(p["rounding_inputs"], ROUNDING, "Rounding")
        for v in p["rounding_inputs"].values():
            _dec(v)
    s = t["displayed_sizes"]
    if s is not None:
        _closed(s, ["bs", "as"], "displayed_sizes")
        for v in s.values():
            _dec(v, nullable=True)
    _presence(t)


def _presence(t):
    """Presence and precedence rows of §10.4 / contract v2 for the paths the harness produces."""
    term = t["terminal_state"]
    v12a, v12b = t["V12a"]["result"], t["V12b"]["result"]
    empty_decision = all(t[k] is None for k in NUMS + ["signal", "mapping", "proposal", "created"]) and \
        not t["rule_results"] and not t["used_bars"]
    if t["origin"] == "INJECTED":
        _presence_injected(t)
        return
    if v12a == "FAIL":
        ok = (term == "BOUNDARY_FAIL" and t["bars_request"] is None and t["quote_request"] is None and empty_decision
              and all(t[k] is None for k in ART + CLOCK) and all(not t[k] for k in ARRAYS) and t["displayed_sizes"] is None)
    elif t["bars_request"] is not None and t["bars_request"]["outcome"] == "NO_RESPONSE":
        ok = (term == "NO_DECISION (FETCH_FAILED)" and t["quote_request"] is None and empty_decision
              and all(t[k] is None for k in ART + CLOCK[1:]) and t["t_send"] == t["bars_request"]["sent_at"])
    elif v12b == "FAIL":
        ok = term == "BOUNDARY_FAIL" and t["quote_request"] is None and empty_decision and all(not t[k] for k in ARRAYS)
    elif term.startswith("NO_DECISION") and term != "NO_DECISION (QUOTE_INVALID)":
        ok = empty_decision and all(t[q]["reason"] == "DATA_INVALID" for q in Q_CHECKS)
    elif term in ("HOLD", "NO_ACTION"):
        ok = (t["proposal"] is None and t["created"] is None and not t["rule_results"] and len(t["used_bars"]) == 51
              and all(t[q]["reason"] == "NO_PROPOSAL" for q in Q_CHECKS))
    elif term == "NO_DECISION (QUOTE_INVALID)":
        ok = (t["proposal"] is None and t["created"] is None and not t["rule_results"]
              and any(t[q]["result"] == "FAIL" for q in Q_CHECKS) and all(t[q]["result"] != "NOT_EVALUATED" for q in Q_CHECKS))
    elif term in ("REJECTED", "SHADOW_EXPIRED"):
        fails = [r for r in t["rule_results"] if r["result"] == "FAIL"]
        ok = (t["proposal"] is not None and t["created"] is not None and bool(t["rule_results"])
              and all(t[q]["result"] == "PASS" for q in Q_CHECKS) and (bool(fails) == (term == "REJECTED")))
    else:
        ok = False
    if not ok:
        raise EvidenceError(f"TER presence rules violated for terminal path {term!r}")
    got_quote = t["quote_request"] is not None and t["quote_request"]["outcome"] == "RESPONSE"
    if (t["displayed_sizes"] is not None) != got_quote:
        raise EvidenceError("displayed_sizes must be present iff a quote response was received (§10.4 G8-01)")


# ----------------------------------------------------------------------------- TER-1 assembly (contract v2 §2)
def _s(x):
    return None if x is None else str(x)


def _tuple_obj(tup):
    return None if tup is None else dict(zip(BAR_FIELDS, tup))


def _bar_view(b):
    """contract v2 §2 Bar: token text kept; NonNumeric -> null; zero_volume TRUE/FALSE on a parseable v."""
    def tok(v):
        return v if isinstance(v, str) else None
    out = {"t": None}
    try:
        out["t"] = str(X.parse_rfc3339_ns(b.get("t")))
    except (X.MalformedValue, TypeError):
        pass
    out.update({f: tok(b.get(f)) for f in BAR_FIELDS})
    try:
        out["zero_volume"] = "TRUE" if X.parse_number_token(b.get("v")) == 0 else "FALSE"
    except (X.MalformedValue, TypeError):
        out["zero_volume"] = None
    return out


def bar_partitions(bars_parsed, T_d_ns):
    """completed_bars / excluded_bars in ARRIVAL order (contract v2 §2): unplaceable timestamps omitted, an identical
    duplicate collapses, a differing duplicate keeps the first for display (V4 fails separately) (contract v2 §9)."""
    seen, completed, excluded = {}, [], []
    for b in bars_parsed:
        view = _bar_view(b)
        if view["t"] is None:
            continue
        t = int(view["t"])
        if t in seen:
            continue
        seen[t] = True
        (completed if X.is_completed(t, T_d_ns) else excluded).append(view)
    return completed, excluded


def transitions(events, store):
    """contract v2 §2 Transition objects from validate.fold events and the store AFTER the fold.
    Contract v2.1 CC-01: BASELINED null/A; OBSERVED A/A; SOURCE_REVISION A/B, or B/C while already pending;
    CONFIRMED A/B (old = previously accepted, new = newly accepted); DISAPPEARED A/null; DUPLICATE_COLLAPSED null/null.
    state/observation_count are the store values after the event; null for DUPLICATE_COLLAPSED (contract v2)."""
    out = []
    for e in events:
        t, ev = e["t"], e["event"]
        st = store.get(t)
        rec = {"t": str(t), "event": ev, "old": None, "new": None, "state": None, "observation_count": None}
        if ev != "DUPLICATE_COLLAPSED":
            rec["state"], rec["observation_count"] = st["state"], str(st["count"])
        if ev == "BASELINED":
            rec["new"] = _tuple_obj(e["new"])
        elif ev == "OBSERVED":
            rec["old"] = rec["new"] = _tuple_obj(st["tuple"])
        elif ev == "SOURCE_REVISION":
            rec["old"], rec["new"] = _tuple_obj(e["old"]), _tuple_obj(e["new"])
        elif ev == "CONFIRMED":
            rec["old"], rec["new"] = _tuple_obj(e["old"]), _tuple_obj(e["new"])          # CC-01: old = previously accepted
        elif ev == "DISAPPEARED":
            rec["old"] = _tuple_obj(st["tuple"])
        out.append(rec)
    return out


def _chk(result, reason=None):
    return {"result": result, "reason": None} if result in ("PASS", "FAIL") else {"result": "NOT_EVALUATED", "reason": reason}


def build_scheduled_ter(ctx, cyc, store):
    """Assemble a SCHEDULED TER-1 object from run_cycle output `cyc` and the cycle context `ctx`:
      manifest_sha256, slot_index, invocation_instant, T_d, bars_request, quote_request (contract Request objects or
      None), bars_sha256, bars_headers_sha256, quote_sha256, quote_headers_sha256, policy_sha256, V12a_evidence,
      lock_clock_at. Validates the result (validate_ter) before returning it."""
    term = cyc["terminal"]
    T_d = ctx["T_d"]
    v12a, v12b = cyc["V12a"], cyc["V12b"]
    if v12a != "PASS":
        path_reason = "V12A_FAILED"
    elif ctx["bars_request"] is not None and ctx["bars_request"]["outcome"] == "NO_RESPONSE":
        path_reason = "FETCH_FAILED"
    elif v12b != "PASS":
        path_reason = "V12B_FAILED"
    else:
        path_reason = None
    V = {}
    for c in ["V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9", "V10", "V11"]:
        r = cyc["V"][c]
        if r == "NOT_EVALUATED":
            V[c] = _chk(r, path_reason or "DATA_INVALID")
        else:
            V[c] = _chk(r)
    V["V12a"] = _chk(v12a, None)
    V["V12b"] = _chk(v12b, path_reason) if v12b == "NOT_EVALUATED" else _chk(v12b)
    if path_reason:
        q_reason = path_reason
    elif any(V[c]["result"] == "FAIL" for c in ["V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9", "V10", "V11"]):
        q_reason = "DATA_INVALID"
    else:
        q_reason = "NO_PROPOSAL"
    Q = {q: _chk(cyc["Q"][q], q_reason) for q in Q_CHECKS}

    parsed = cyc.get("bars_parsed") or []
    completed, excluded = (bar_partitions(parsed, T_d) if path_reason is None else ([], []))
    signal_path = "signal" in cyc
    t_exp = X.t_exp_ns(T_d)
    used = ([{"t": str(t), "state": store[t]["state"], "observation_count": str(store[t]["count"])}
             for t in sorted(t_exp - 300 * X.NS * j for j in range(51))] if signal_path else [])
    p = cyc.get("proposal")
    proposal = None
    if p is not None:
        if "R" not in p:
            raise EvidenceError("an EXIT proposal is not representable in a Stage A TER (contract v2: R required)")
        proposal = {"instrument": p["instrument"], "side": p["side"], "order_type": p["order_type"],
                    "L": dec_str(p["L"]), "q": dec_str(p["q"]), "R": dec_str(p["R"]),
                    "rounding_inputs": {k: dec_str(p["rounding_inputs"][k]) for k in ROUNDING}}
    br = ctx["bars_request"]
    ter = {
        "schema": "TER-1", "origin": "SCHEDULED", "manifest_sha256": ctx["manifest_sha256"],
        "slot_index": str(ctx["slot_index"]), "cycle_id": ["BTC/USD", str(t_exp)],
        "invocation_instant": str(ctx["invocation_instant"]), "T_d": str(T_d),
        "created": _s(cyc.get("created")),
        "bars_request": br, "quote_request": ctx["quote_request"],
        "bars_sha256": ctx["bars_sha256"], "bars_headers_sha256": ctx["bars_headers_sha256"],
        "quote_sha256": ctx["quote_sha256"], "quote_headers_sha256": ctx["quote_headers_sha256"],
        "completed_bars": completed, "excluded_bars": excluded,
        "bar_store_transitions": transitions(cyc.get("transitions", []), store),
        **V, **Q,
        **{k: (dec_str(cyc[k]) if signal_path else None) for k in NUMS},
        "signal": cyc.get("signal"), "mapping": cyc.get("mapping"), "proposal": proposal,
        "rule_results": [{"rule": r, "result": v} for r, v in (cyc.get("rules") or {}).items()],
        "terminal_state": term, "policy_sha256": ctx["policy_sha256"],
        "displayed_sizes": cyc.get("displayed_sizes"), "egress_scope": "CLIENT_ALLOWLIST_ONLY",
        "t_send": br["sent_at"] if br else None, "t_recv": br["received_at"] if br else None,
        "D": _s(cyc.get("D")), "θ_low": _s(cyc.get("theta_low")), "θ_high": _s(cyc.get("theta_high")),
        "lock_clock_at": str(ctx["lock_clock_at"]), "V12a_evidence": ctx["V12a_evidence"], "injection": None,
        "used_bars": used,
    }
    validate_ter(ter)
    return ter


# ------------------------------------------------------------------ injected TERs (contract v2 §2 injected rows)
INJ_NULL = (["slot_index", "cycle_id", "bars_request", "quote_request", "bars_sha256", "bars_headers_sha256",
             "quote_headers_sha256"] + CLOCK + NUMS + ["signal", "mapping"])
INJ_EMPTY = ["completed_bars", "excluded_bars", "bar_store_transitions", "used_bars"]


def _presence_injected(t):
    """Contract v2 §2 'Injected terminal paths' (§10.4): one row per path; anything else is refused."""
    term, v12a = t["terminal_state"], t["V12a"]["result"]
    ok = all(t[k] is None for k in INJ_NULL) and all(t[k] == [] for k in INJ_EMPTY) and t["injection"] is not None
    na = "V12A_FAILED" if v12a == "FAIL" else "INJECTED"
    ok = ok and all(t[c] == {"result": "NOT_EVALUATED", "reason": na} for c in V_CHECKS if c != "V12a")
    if v12a == "FAIL":
        ok = (ok and term == "BOUNDARY_FAIL" and t["quote_sha256"] is None and t["displayed_sizes"] is None
              and t["created"] is None and t["proposal"] is None and not t["rule_results"]
              and all(t[q] == {"result": "NOT_EVALUATED", "reason": "V12A_FAILED"} for q in Q_CHECKS))
    elif term == "NO_DECISION (QUOTE_INVALID)":
        ok = (ok and t["quote_sha256"] is not None and t["displayed_sizes"] is not None and t["created"] is None
              and t["proposal"] is None and not t["rule_results"]
              and all(t[q]["result"] in ("PASS", "FAIL") for q in Q_CHECKS)
              and any(t[q]["result"] == "FAIL" for q in Q_CHECKS))
    elif term in ("REJECTED", "SHADOW_EXPIRED"):
        fails = [r for r in t["rule_results"] if r["result"] == "FAIL"]
        ok = (ok and t["quote_sha256"] is not None and t["displayed_sizes"] is not None and t["created"] is not None
              and t["proposal"] is not None and t["proposal"]["side"] == "BUY" and bool(t["rule_results"])
              and all(t[q]["result"] == "PASS" for q in Q_CHECKS) and bool(fails) == (term == "REJECTED"))
    else:
        ok = False
    if not ok:
        raise EvidenceError(f"injected TER presence rules violated for terminal path {term!r}")


def build_injected_ter(ctx, res):
    """Assemble an INJECTED TER-1 from controller.run_injection output `res` and `ctx`: manifest_sha256,
    invocation_instant (founder command instant), T_d (fixture), policy_sha256, V12a_evidence, lock_clock_at,
    quote_sha256 (raw fixture quote bytes, stored as an artifact) and injection {plan_sha256, fixture_sha256,
    intended_rule}. BUY only (contract v2 §7; CC-04). Validated before return."""
    v12a = res["V12a"]
    na = "V12A_FAILED" if v12a != "PASS" else "INJECTED"
    V = {c: _chk("NOT_EVALUATED", na) for c in V_CHECKS if c != "V12a"}
    V["V12a"] = _chk(v12a)
    Q = ({q: _chk("NOT_EVALUATED", "V12A_FAILED") for q in Q_CHECKS} if v12a != "PASS"
         else {q: _chk(res["Q"][q]) for q in Q_CHECKS})
    p = res.get("proposal")
    proposal = None
    if p is not None:
        if p["side"] != "BUY" or "R" not in p:
            raise EvidenceError("a Stage A injection is BUY-only (contract v2 §7; CC-04)")
        proposal = {"instrument": p["instrument"], "side": p["side"], "order_type": p["order_type"],
                    "L": dec_str(p["L"]), "q": dec_str(p["q"]), "R": dec_str(p["R"]),
                    "rounding_inputs": {k: dec_str(p["rounding_inputs"][k]) for k in ROUNDING}}
    ter = {k: None for k in TER_KEYS}
    ter.update({
        "schema": "TER-1", "origin": "INJECTED", "manifest_sha256": ctx["manifest_sha256"],
        "invocation_instant": str(ctx["invocation_instant"]), "T_d": str(ctx["T_d"]), "created": _s(res.get("created")),
        "quote_sha256": ctx["quote_sha256"], "completed_bars": [], "excluded_bars": [], "bar_store_transitions": [],
        "used_bars": [], **V, **Q, "proposal": proposal,
        "rule_results": [{"rule": r, "result": v} for r, v in (res.get("rules") or {}).items()],
        "terminal_state": res["terminal"], "policy_sha256": ctx["policy_sha256"],
        "displayed_sizes": res.get("displayed_sizes"), "egress_scope": "CLIENT_ALLOWLIST_ONLY",
        "lock_clock_at": str(ctx["lock_clock_at"]), "V12a_evidence": ctx["V12a_evidence"],
        "injection": dict(ctx["injection"])})
    validate_ter(ter)
    return ter
