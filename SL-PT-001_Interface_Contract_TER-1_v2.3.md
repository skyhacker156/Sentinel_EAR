# SL-PT-001 | Interface Contract TER-1 v2.3 (candidate)

**Original v2 exposure:** Exactly four supplied attachments: `SL-PT-001_R4.2i_Stage_A_Amendment_Candidate_Claude_2026-11-26(1).md`, `SL-PT-001_Stage_A_Freeze_Record_R4.2i_2026-11-26.txt`, `SL-PT-001_Interface_Contract_TER-1_v1(1).md`, and `sl_pt_001_audit(1).py`. No harness code, external tests, TER output, Claude conversations/packages, credentials or orders were accessed. No repository access during authorship. Computed attachment SHA-256 `4259551121fa3d271074fb13da51fb270ae859b0b516a953752731f20972a51a` (MATCH); freeze record names blob `3549d2275ce3f5490f93802ff9eec1570f2fb48f` (not independently checked).

**v2.1 exposure:** Frozen R4.2i and its amended freeze record, my exact v2 contract and auditor, and `SL-PT-001_Contract_v2_Clarification_Questions_2026-11-26.md` only. Recomputed R4.2i SHA-256 matches the pinned value above. Parent contract SHA-256 `5e563068d6775dcd58f13c5dcf59944eb32552490efea9649bfdda934a9da319`; parent auditor SHA-256 `9ae6be409bc6cd9a85b5b987272c19f31e5fec947f6aaed9262fb662e187db65`. No harness code, external tests, TER output, private harness-author conversations, or repository access. No credentials or orders.

**Status:** Independent pre-TER interface, not an amendment or execution authorization. Normative scope: §§2–7, 8.1/8.1.1, 10, 11, 13, Stage A tests/rows of §§14–16. Stage B excluded. E-1: BOUNDARY_VIOLATION_ATTEMPT is retained test output only, not a record/TER value. E-2: HOLD maps to HOLD; open-order mapping applies only to BUY/EXIT. All serialization decisions not explicitly named in the frozen specification are **CONTRACT CHOICE (CC)**. TER schema tag remains TER-1, not TER-2.

## 1. Encoding and shared types (§§4.3–4.4, 5.1, 10.4–10.5)

Every object below is closed; every listed key is required, including nullable keys. `str` = JSON string; `ns` = signed base-10 integer string, epoch UTC; `intstr` = integer string; `dec` = exact finite decimal string, exponent allowed; `hash` = lowercase 64-character SHA-256 hex; `?` = value or JSON null. Arrays always exist, including `[]`. No JSON numbers or booleans in any TER subtree. **CC:** use decimal strings without a rational slash; all represented Stage A outputs have terminating decimals. Preserve raw numeric token spelling for bar tuples and displayed quote sizes; compare calculated decimal values by exact rational equality. Hashes refer to exact bytes, not decoded/normalized text. `cycle_id` is `["BTC/USD", t_exp_ns]` (CC, tuple from §6.2). `seq` and `declared_slots` are JSON integers, not TER fields; CC: restrict to nonnegative JCS safe integer range (0 to 9007199254740991); all other numeric fields use strings. All enum values are case-sensitive.

## 2. TER object (§10.4)

Names explicitly written in the frozen schema are marked S; other spellings/groupings are CC. All keys below occur exactly once.

| Key | Type | Source/name |
|---|---|---|
| schema | `"TER-1"` | S |
| origin | `SCHEDULED` or `INJECTED` | S |
| manifest_sha256 | hash | S |
| slot_index | intstr? (null for injected) | S/CC null |
| cycle_id | cycle_id? (null for injected) | S/CC tuple |
| invocation_instant | ns? | CC |
| T_d | ns? | CC §6.2 |
| created | ns? | CC §5.3 |
| bars_request | Request? | S |
| quote_request | Request? | S |
| bars_sha256 | hash? | CC |
| bars_headers_sha256 | hash? | CC |
| quote_sha256 | hash? | CC |
| quote_headers_sha256 | hash? | CC |
| completed_bars | Bar[] | CC |
| excluded_bars | Bar[] | CC |
| bar_store_transitions | Transition[] | CC |
| V1, V2, V3, V4, V5, V6, V7, V8, V9, V10, V11, V12a, V12b | Check each | CC flat grouping |
| Q1, Q2, Q3, Q4, Q5 | Check each | CC flat grouping |
| S20_k, S50_k, S20_prev, S50_prev, D_prev, D_k | dec? each | CC |
| signal | `BUY`, `EXIT`, `HOLD` or null | CC |
| mapping | `PROPOSAL`, `HOLD`, `NO_ACTION`, `NO_ACTION (BLOCKED_OPEN_ORDER)` or null | CC §3.3 |
| proposal | Proposal? | CC |
| rule_results | RuleResult[] | CC |
| terminal_state | Terminal | S |
| policy_sha256 | hash | CC |
| displayed_sizes | Sizes? | CC |
| egress_scope | `CLIENT_ALLOWLIST_ONLY` | S |
| t_send, t_recv, D, θ_low, θ_high | ns? each | S (D here is HTTP Date, NOT crossover) |
| lock_clock_at | ns (non-null) | S |
| V12a_evidence | Evidence (non-null) | CC object name; S member names |
| injection | Injection? | CC object name; S member names |
| used_bars | UsedBar[] | CC |

Nested closed shapes (CC except the four Request keys, V12a evidence and injection member names):

- Evidence = `{env_credential_names:str[],config_sha256:hash?,client_allowlist:str[]}`. Only matching names (case-insensitive APCA_ or ALPACA_ prefix), never values. Hash null only if config unreadable; V12a then FAIL. On PASS, hash resolves to raw config artifact, closed `{client_allowlist:["data.alpaca.markets"]}` and exact equality to client-reported list. On FAIL, never retain or read config bytes. Both arrays always present. HARNESS-ATTESTED. A failed config hash is metadata, not an artifact reference.
- Injection = `{plan_sha256:hash,fixture_sha256:hash,intended_rule:str}` (rule code). Null for SCHEDULED; required object for INJECTED.

- Request = `{url:str, sent_at:ns, received_at:ns?, outcome:str}`. `RESPONSE` requires received_at and body/header artifacts; `NO_RESPONSE` requires received_at and both associated hashes null. Never issued = whole object null. `t_send` is bars sent_at even on NO_RESPONSE; `t_recv` is bars received_at. Exactly two request objects; no pagination. Injection quote bytes are fixture-sourced, with quote_request null and quote_headers_sha256 null. **CC-05:** Record the actual client-reported URL, not a reconstructed canonical string. HTTPS host `data.alpaca.markets` with no port, userinfo or fragment; exact paths `/v1beta3/crypto/us/bars` and `/v1beta3/crypto/us/latest/quotes`. Decoded query keys for bars are exactly `symbols=BTC/USD`, `timeframe=5Min`, `start`, `end`, `limit=1000`; for quote exactly `symbols=BTC/USD`. One value per key; no extras. Both `BTC%2FUSD` and `BTC/USD` are accepted, with query parameter order unrestricted. After query decoding, `start` and `end` use `YYYY-MM-DDTHH:MM:SSZ` (UTC whole seconds, uppercase T/Z, no fraction or numeric offset). Start = t_exp − 59 × 300 s; end = T_d. This does not establish wire-level egress.
- Bar = `{t:ns?, o:str?, h:str?, l:str?, c:str?, v:str?, vw:str?, n:str?, zero_volume:str?}`. CC: `zero_volume` = `TRUE` or `FALSE` on parseable v; otherwise null. Numeric members retain original JSON number token spelling, not decoded/reformatted numbers; null if unavailable/malformed. A malformed timestamp with no parseable instant cannot be reliably placed in completed/excluded and is reported from raw bytes. Arrays retain arrival order within each partition; identical duplicates collapse (record note in transitions). Sort separately for computation.
- Tuple = `{o:str,h:str,l:str,c:str,v:str,vw:str,n:str}` (raw tokens). Transition = `{t:ns, event:str, old:Tuple?, new:Tuple?, state:str?, observation_count:intstr?}`. CC event values `BASELINED`, `OBSERVED`, `SOURCE_REVISION`, `CONFIRMED`, `DISAPPEARED`, `DUPLICATE_COLLAPSED`. State `BASELINED`, `PENDING`, `CONFIRMED` or null. Counts refer to currently accepted tuple; on PENDING retain accepted count, confirmation starts new accepted count at 2. A→B→A is another revision (U40); require next same pending tuple to confirm. Duplicate note leaves state/count null; disappearance leaves accepted state/count unchanged. Record duplicate notes in arrival order first, then observations in sorted t order, then disappearances sorted by t (CC). **CC-01:** BASELINED: old=null, new=first tuple; OBSERVED: old=accepted tuple, new=same observed tuple; SOURCE_REVISION: old=accepted tuple if no revision pending, else previous pending tuple, new=observed tuple; CONFIRMED: old=previous accepted tuple (not the pending tuple), new=matching pending tuple now accepted; DISAPPEARED: old=accepted tuple, new=null; DUPLICATE_COLLAPSED: both null. On CONFIRMED count=2; on DISAPPEARED retain accepted state/count; on DUPLICATE_COLLAPSED state/count=null. Invalid sets contribute no transitions; see §9.
- UsedBar = `{t:ns,state:str,observation_count:intstr}` in ascending t order for the actual 51 used bars; otherwise [].
- Check = `{result:str, reason:str?}`; `PASS` or `FAIL` requires null reason; `NOT_EVALUATED` requires one of `V12A_FAILED`, `V12B_FAILED`, `FETCH_FAILED`, `DATA_INVALID`, `NO_PROPOSAL`, `INJECTED`. These values are frozen; shape CC.
- Proposal = `{instrument:str,side:str,order_type:str,L:dec,q:dec,R:dec,rounding_inputs:Rounding}`. **CC-04:** `side` is `BUY` only in a Stage A runtime Proposal (including INJECTION_ABORTED if a proposal exists); order_type `LIMIT`. Scheduled EXIT signal maps to NO_ACTION with proposal=null because the shadow ledger stays flat. Runtime injections are BUY-only (§6.5); EXIT fixture-backed unit tests remain required but are not runtime TERs. Rounding = `{bid:dec,ask:dec,price_increment:dec,qty_increment:dec,min_order_size:dec,f_res:dec,shadow_cash:dec,shadow_reserved:dec,cash_available:dec,budget:dec,shadow_btc:dec,shadow_reserved_btc:dec}`. CC names/grouping for §7/8.1.1 inputs. On live BUY shadow BTC and pre-proposal reservations are zero. No TIF or partial-fill approval fields (Stage B only). No EXIT runtime Proposal representation or fictitious USD R is defined; evaluator-level EXIT fixtures follow the frozen EXIT semantics, outside this TER interface.
- RuleResult = `{rule:str,result:str}`; rule R1–R13 or R15–R16, result `PASS`/`FAIL`; only applicable rules included, numeric code order. R2 limit-only is applicable in A (§7.3, §11.6 D-5); R9/R15 EXIT-only; R6/R7/R8/R12 BUY-only; R14 absent. Runtime proposals are BUY only.
- Sizes = `{bs:str?,as:str?}` (member names S). Each is original JSON number token or null if absent/non-numeric/malformed. Whole object null only if no quote available (not issued, NO_RESPONSE, or injection V12a failure). If response available but both sizes absent: `{ "bs": null, "as": null }`. Record even if Q not evaluated.
- Terminal = `HOLD`, `NO_ACTION`, `REJECTED`, `SHADOW_EXPIRED`, `BOUNDARY_FAIL`, `CYCLE_OVERRUN`, or `NO_DECISION (REASON)` (CC spelling). REASON: `FETCH_FAILED`, `INCOMPLETE_RESPONSE`, `MALFORMED_VALUE`, `DATA_CONFLICT`, `STALE_SERIES`, `DATA_GAP`, `INSUFFICIENT_HISTORY`, `SOURCE_REVISION`, `QUOTE_INVALID`. A scheduled overrun is a separate chain record, not a successful CYCLE. `lock_clock_at` is always present in a TER, including failures and injections; never an append-completion timestamp.

### Presence and precedence (§10.4)

| Path | Requests / artifacts | Checks and decision fields |
|---|---|---|
| V12a fail | neither issued; all response hashes and clock fields null | V12a FAIL; all others NOT_EVALUATED/V12A_FAILED; computed fields, created, sizes null; arrays [] |
| Bars NO_RESPONSE | bars issued, no received_at or hashes; only t_send present; no quote | V12a PASS; all others NOT_EVALUATED/FETCH_FAILED; computed fields null; arrays [] |
| V12b fail | bars response and hashes; no quote | V12a PASS, V12b FAIL; remaining NOT_EVALUATED/V12B_FAILED; computed fields null; arrays [] |
| V1–V11 fail | both issued (quote may have NO_RESPONSE) | V1/V2 both evaluated, V3–V11 NOT_EVALUATED/DATA_INVALID if either fails; otherwise all evaluated; Q NOT_EVALUATED/DATA_INVALID; computed fields null; on V1 or V2 failure, retain evidence-only partitions per §9, but transitions and used_bars [] |
| HOLD / NO_ACTION | both issued | V pass; Q NOT_EVALUATED/NO_PROPOSAL; proposal/created null; rules [] |
| QUOTE_INVALID | both issued | V pass; Q evaluated, at least one fail (all fail on absent quote); proposal/created null; rules [] |
| REJECTED / SHADOW_EXPIRED | both responses | V and Q pass; all applicable rules evaluated; proposal/created present; SHADOW_EXPIRED only if all pass |

For all scheduled paths `injection=null`; V12a evidence and lock_clock_at always present. Quote NO_RESPONSE may occur on V failure or HOLD/NO_ACTION; quote artifact and displayed sizes then null. Clock bounds null when Date cannot parse; if parseable, compute even when V12b fails. For QUOTE_INVALID all Q evaluated; absent quote gives five FAIL. For proposal path REJECTED iff at least one applicable rule fails, SHADOW_EXPIRED iff all pass; lock_clock_at ≥ ceiling only for scheduled SHADOW_EXPIRED. For every scheduled CYCLE lock_clock_at < T_d+300s and chain order before later-slot records (§5.4); timestamps HARNESS-ATTESTED. No completion/durability field.

### Injected terminal paths (§10.4)

All injected paths: origin INJECTED; manifest_sha256 of open run; invocation_instant is founder command instant; T_d from fixture; lock_clock_at and V12a_evidence present; injection object present. slot_index, cycle_id, both requests, bars_sha256, both header hashes, all five clock fields, six computed sums/D fields, signal and mapping null; completed_bars, excluded_bars, bar_store_transitions, used_bars empty. No slot or bar-store credit. Policy hash present. V1–V11 and V12b NOT_EVALUATED/INJECTED except V12a failure.

| Path | Present | Null/empty or unevaluated |
|---|---|---|
| V12a FAIL → BOUNDARY_FAIL | V12a FAIL | quote_sha256, displayed_sizes, created, proposal null; rule_results []; V1–V11, V12b, Q NOT_EVALUATED/V12A_FAILED |
| V12a PASS → NO_DECISION (QUOTE_INVALID) | quote_sha256 = fixture quote bytes SHA-256; displayed_sizes object; Q all evaluated, ≥1 FAIL | created, proposal null; rule_results [] |
| V12a PASS → REJECTED | quote_sha256, sizes, created from fixture, BUY proposal, every applicable rule; Q all PASS | no extra fields; ≥1 FAIL |
| V12a PASS → SHADOW_EXPIRED | same fields, every applicable rule PASS | no scheduled ceiling wait; records at once |

## 3. Global chain and manifest (§§6, 10.1–10.3)

Record envelope exactly `{seq:integer,prev_hash:hash?,type:str,body:object,hash:hash}`; GENESIS seq=0, prev_hash=null (CC); no other null prev_hash. Subsequent prev_hash is preceding record hash, seq increments exactly one. Exact body keys (CC names unless already specified):

| type | body |
|---|---|
| GENESIS | `{experiment_id:str,frozen_set_hashes:HashMap}`; experiment_id `SL-PT-001` |
| RUN_OPEN | `{manifest_sha256:hash}` |
| CYCLE | TER object, origin SCHEDULED |
| CYCLE_OVERRUN | `{slot_index:intstr,old_process_id:intstr}` |
| CONCURRENT_INVOCATION | `{slot_index:intstr,invocation_instant:ns}` |
| OFF_RUN | `{invocation_instant:ns}` (no slot index) |
| INJECTION | TER object, origin INJECTED; proposal and terminal/rule result are inside TER (CC representation of §10.1 content) |
| INJECTION_ABORTED | `{proposal:Proposal?,result:"INJECTION_ABORTED"}` (CC) |
| RUN_STOPPED | `{instant:ns}` |
| RUN_CLOSE | `{invocation_log_sha256:hash,task_xml_sha256:hash}` |

CC: records without manifest hash belong to most recently opened, not superseded run; RUN_CLOSE closes it but later OFF_RUN can belong to it until next RUN_OPEN. Before first RUN_OPEN attribution is unresolved. No concurrent run representation is defined. RUN_STOPPED does not shorten N. The successor/close writes overrun, and the old pid matches the wrapper log only if wrapper PID and harness PID are the same; §6.1 does not establish that identity.

Manifest closed object: `{instrument:str,T_d0:ns,declared_slots:integer,opening_cash:dec,frozen_set_hashes:HashMap,harness_sha256:hash,policy_sha256:hash,task_xml_sha256:hash,wrapper_sha256:hash,prev_chain_head:hash}`. HashMap is object mapping frozen file repository-relative names to exact SHA-256 strings (CC); must contain the named R4.2i path and hash; same map in GENESIS and manifests. T_d0 grid, N≥30, opening cash exactly 500.00 on cent grid; instrument BTC/USD. Raw manifest bytes determine hash. RUN_OPEN must directly follow prev_chain_head. Founder push before T_d0 is separate evidence, not proved by local git timestamps.

Invocation line (CC §6.1): UTF-8 ASCII-compatible `invocation_instant<TAB>process_id<TAB>wrapper_sha256<LF>`; no header; integer strings, lowercase hash. Repeated lines are distinct invocations. Each in-run line matched to one chain record where possible; an overrun is matched by owning slot, because its old harness PID cannot be equated to wrapper PID without evidence. OFF_RUN by instant. The RUN_CLOSE hash covers the complete raw log bytes.

## 4. Policy file (§§4.12, 7.3–7.4, 8.1.1)

CC closed JSON shape below encodes Stage A rules. R2 limit only per §7.3; no Stage B policy controls. Rule entries without a numeric parameter carry stable descriptive identifiers, not executable code. Exact expected values:

```json
{
  "price_increment":{"value":"1","source":"support_table_DOCUMENTED","status":"UNVERIFIED"},
  "qty_increment":{"value":"0.0001","source":"support_table_DOCUMENTED","status":"UNVERIFIED"},
  "min_order_size":{"value":"0.0001","source":"support_table_DOCUMENTED","status":"UNVERIFIED"},
  "f_res":"0.0025","settle_s":"60","W_s":"90","freshness_s":"15",
  "rules":{"R1":"BTC/USD","R2":"LIMIT","R3":"SCHEMA_VALID","R4":"15","R5":"0.01","R6":"CASH_AVAILABLE","R7":"150","R8":"300","R9":"BTC_AVAILABLE","R10":"INCREMENTS_AND_MINIMUM","R11":"ONE_OPEN","R12":"450","R13":"90","R15":"EXIT_LONG","R16":"NO_OPEN_OR_UNRESOLVED"}
}
```

`rules`, `value` and per-rule encodings are CC; the top-level parameter names and source/status values are frozen. All numeric values strings. No inference from precision. File hash is raw SHA-256, recorded in each CYCLE and manifest. **CC-02:** Valid UTF-8 JSON with the exact closed values above and no duplicate keys; key order, insignificant JSON whitespace, indentation and trailing newline are unrestricted. JCS record hashing does not canonicalize policy bytes. Hash the exact chosen bytes; the manifest, CYCLEs and applicable injections/fixtures bind the same hash. Once pinned, even a formatting-only byte change requires a founder record and new version. Policy changes need founder record and new version.

## 5. Layout (§§6.1, 10.1–10.3)

CC: evidence root is `experiments/sl-pt-001/` relative to repository root (explicit auditor override available). Relative paths:

- `chain/events.jsonl` global chain, one complete JSON record per LF-terminated line, no blank lines (CC newline).
- `artifacts/<sha256>` exact bytes of body and headers separately. §4.3 D-8: body = response body bytes after transfer decoding (chunk framing removed); requests send Accept-Encoding: identity; non-identity Content-Encoding fails V1. Header artifact = client-reported `HTTP/<version> <status> <reason>` CRLF, each field `Name: value` CRLF in received order/original case, then CRLF. Status and Date read from artifact. This is NOT a wire capture. Passing V12a config bytes and injected quote bytes also stored by raw hash.
- `chain/invocations/<manifest_sha256>.log` wrapper log.
- `runs/<name>.json` founder manifest; auditor scans recursively and reports duplicates.
- `policy/P-0.2.json` frozen policy version.
- `injections/<name>.json` founder plans; `injections/fixtures/<sha256>.json` founder fixtures.
- Custody is an exception to the evidence root: repository-root `audit-scopes/<id>/` (CC-08; §8 below).
- `chain/tasks/<task_xml_sha256>.xml` (CC location for the preserved XML §6.1; wrapper hash retained in manifest, wrapper source path not specified and not read by auditor).

Artifacts not referenced by any committed record are orphans, not evidence. Git object bytes from audited commit, not working-tree files, are used by the auditor. Symlinks/submodules are not evidence files. Script never accesses network or writes evidence.

## 6. Canonicalization (§10.5)

RFC 8785 JCS: UTF-8, no BOM, no insignificant whitespace, JSON strings escaped per ECMAScript JSON rules, control characters escaped; preserve Unicode (no normalization), reject lone surrogates and duplicate object keys, recursively sort object member names by unsigned UTF-16 code units, preserve array order. TER has no numeric/boolean primitives. Outside TER, this contract admits only safe integer JSON numbers, whose decimal rendering is exactly JCS (no binary arithmetic needed); other numeric primitives are rejected. Record hash = lowercase SHA-256 of canonical UTF-8 bytes of `{seq,prev_hash,type,body}` (omit `hash`, not null). Raw artifact, log, manifest, policy and XML hashes cover their exact raw bytes. JSONL itself need not be canonical for the hash to verify; exact source bytes remain auditable through git.

## 7. Injection plan and fixture (§6.5)

**CC** exact closed plan shape: `{"injections":[{"fixture_sha256":hash,"intended_rule":str},...]}`. Each entry unique by fixture and target, and a countable runtime target belongs to R1/R4/R5/R10/R12/R13. The plan hash is raw file SHA-256. No extra metadata. Commit and push both plan and fixture before its injection record; each fixture filename is its raw SHA-256.

**CC** exact closed fixture shape:

| Key | Type / meaning |
|---|---|
| instrument | str; proposed instrument (R1 fixture may be off allowlist) |
| quote_body_hex | str; lowercase hex of exact fixture quote response body bytes, no separators; same response shape as §4.11, `quotes` keyed by fixture instrument |
| T_d | ns, fixture decision instant |
| created | ns, checkpoint (a), ≥ T_d |
| shadow_cash | dec, nonnegative cents |
| shadow_btc | dec, nonnegative BTC |
| shadow_reserved | dec, nonnegative cents ≤ cash |
| shadow_reserved_btc | dec, nonnegative BTC ≤ held BTC |
| open_authorizations | str[]; open/unresolved authorization or order identifiers (empty for a normally constructed BUY) |
| policy_sha256 | hash, exact policy bytes |

BUY fixed by §6.5; order type LIMIT by construction. A constructed flat BUY requires shadow_btc < min_order_size and no open authorization/order. Fixture cash and reservations provide cash_available; budget, L, q, R, equity, freshness, spread and cutoff recomputed using §7 and §8.1.1. No fixture result/expected outcome field; intended rule lives in plan and TER only. Runtime FAIL cases for R2/R3/R6/R7/R8/R11/R16 and EXIT branches are unit tests, not this interface. The auditor compares every applicable rule and exact failing set, terminal state, rounding inputs, quote sizes and raw artifact hash. Count unique fixtures only (CC: reject both identical bytes and identical decoded objects). INJECTION_ABORTED is not a rejection credit.

## 8. Commit-reveal custody (§11.5)

CC-08 repository-relative path `audit-scopes/<id>/`, not relative to the experimental evidence root (id matches ASCII letters/digits/underscore/hyphen); no added TER or chain fields. Each file is founder-owned, immutable once committed:

- `seed.sha256`: exactly 64 lowercase ASCII hex characters, no newline. SHA-256 of the 64 ASCII seed characters, not the underlying 32 bytes. No manifest list is needed at this stage (later-run hashes may not yet exist). This contract supports one commit-reveal for the entire audited manifest set; any competing seed commitment path in reachable history is invalid.
- `auditor.sha256`: exactly 64 lowercase ASCII hex, no newline; hash of the originally pinned auditor, committed with or before commitment, before any TER; the sole exception for an effective replacement is §12.1.
- `scope.json`: closed `{evidence_commit:str,chain_head:hash,manifests:hash[],population:{count:integer,first_seq:integer?,last_seq:integer?}}`. Commit is full git object ID; manifest list unique and nonempty; count/seq safe nonnegative integers, bounds null iff zero population. Scope commit strictly after the named evidence commit, after last RUN_CLOSE; chain and evidence files frozen at that point. Population covers SCHEDULED CYCLE only (all outcomes, no filtering). Every manifest in the fixed evidence snapshot is audited.
- `seed.txt`: exactly 64 lowercase ASCII hex characters, no newline; strictly later commit. Hash must match commitment. Historical seed at `07f43e0` never reused; historical commit must be available locally to exclude reuse and the historical file remains unchanged in the custody snapshot.

Run: `python sl_pt_001_audit_v2_3.py REPOSITORY --custody-commit COMMIT --scope ID [--reported-counter N]` (optional `--evidence-root experiments/sl-pt-001`). The auditor resolves the evidence commit from scope, not a free CLI seed or evidence override. It checks immutable file introductions in first-parent order, chain append-only prefixes, competing commitments for the fixed run set, pinned evidence tree, eligible population count/first/last, seed hash, and auditor hash. First-parent lineage is a conservative CC; manifests must be present in a strictly earlier local commit than RUN_OPEN, all ancestors are scanned for competing commitment paths in any `audit-scopes` namespace throughout the repository, but omitted histories and remote rewrites cannot be excluded. A separate later audit scope would require a separate interface agreement, not silent seed substitution. The script is read-only and never makes a network request. Local ordering is not proof of actual push order, entropy source, or seed non-disclosure; GitHub push records must separately establish real-world timing before M1-1/M1-6 can be certified. No use of git dates. No fabricated certification.

**Sampling CC:** rank all eligible CYCLE records by `SHA256(b"SL-PT-001/FD-6/v2\0" + seed_ascii + b"\0" + ASCII(seq))`, ascending digest then seq; first five without replacement. No substitution. Replay all CYCLEs in chain order for bar-store history; report selected five and differences. If fewer than five, or custody/population mismatch, M1-6 not met. 

## 9. Audit interpretation and residual limits

- **HARNESS-ATTESTED:** recompute V12a from names, client list and passing config bytes. A FAIL with no visible failing names/list and readable but withheld configuration is indeterminate, not independently verified. No config secret bytes retrieved on FAIL. `lock_clock_at` compared to scheduled boundary, ceiling and chain order. Not append completion, fsync, independent time or host isolation. Qualifying slots conditional on harness observations; §11.1 allows these conditions, unlike v1 strict refusal.
- V2 non-null token fails INCOMPLETE_RESPONSE; never paginate. §4.9/D-6 invalid V1/V2/V3/V4/V9 sets do not update store. CC: malformed unplaceable timestamps omitted from partitions; differing duplicates keep first for partition display but V4 fails; no observations. Identical duplicates note as in v1. Arrival order retained in each partition, sorted for computation. **CC-03:** After V12a and V12b pass, if V1 or V2 fails, still record completed/excluded partitions from a parseable JSON `bars["BTC/USD"]` array, regardless of the validation failure. For each entry with a parseable timestamp keep first occurrence at that instant, in arrival order within each partition; omit unplaceable entries, retain available original numeric tokens (null for missing/malformed members), and flag zero_volume as usual. Completed iff t+360s <= T_d, otherwise excluded. If no parseable target array exists, both partitions are empty. Foreign-symbol data remains in the raw artifact, not mislabeled as BTC/USD. On V1/V2 failure this is evidence-only serialization, not evaluation of V3–V11: bar_store_transitions=[] (including duplicate notes), used_bars=[], and no computed values or store mutation. V12a failure, bars NO_RESPONSE, V12b failure and injections retain their original empty bar collections. This corrects v2 auditor early return, not the frozen spec. Some other malformed partition representations remain underspecified; report differences rather than certify unsupported equivalence. As in v1, CC interpretation of §4.7/§4.11: bars HTTP/JSON failure or any observed wrong symbol map fails V1; a quote transport failure is absent, and other quote HTTP/JSON failures are handled in Q when required; non-identity content encoding fails V1 per D-8. Missing required bars keys maps to INCOMPLETE_RESPONSE. L rounded to zero leaves sizing undefined, reported as unresolved.
- Invocation log and slot classifications follow §11.2 precedence. OFF_RUN never occupies a slot, but is schema/hash checked. All manifest slots count in denominator. Wrapper PID is not automatically old harness PID. §11.4 longest consecutive QUALIFYING streak per manifest, not across manifests; count NO_ACTION by signal. M1-1 local numerical threshold reported separately from push provenance. Founder hand cross-check remains external. No test evidence read; pre-live coverage and full Stage A exit are not certified by this script.
- §2.3 required limitation: "Disconnection from trading is asserted at the HTTP-client level only. Alternate egress paths in the process or host (other libraries, raw sockets, proxies, inherited handles) were not excluded." No G-07, profitability, broker behavior or host isolation claim. Stage A sizing conditional on unverified increments and fees; clock claims conditional on A-CLK/A-CLK2 and data-host UTC accuracy. Completeness relative to GENESIS and pushed history only.

## 10. v1 → v2 change register

| Change | v2 treatment |
|---|---|
| Authority | R4.2i pinned SHA-256; amended freeze E-1/E-2; no Stage B |
| D-1 | no pagination, non-null page token fails V2 |
| D-2 | V12a evidence object, conditional recomputation, passing config artifact only; name-based checked scope |
| D-3 / G7-01 | lock_clock_at always present; append-start boundary/ceiling and chain order; no fsync claim |
| D-4 / G7-02 | injection metadata, plan/fixture shape/layout, BUY-only runtime, separate injected terminal rows, INJECTED reason, exact single-rule attribution and distinct fixture counting, no expiry wait for injection |
| D-4 policy | R6/R7/R8/R12 BUY-only, R9/R15 EXIT-only; runtime reachability corrected; no EXIT injection |
| D-5 | R2 limit-only explicitly Stage A; no conflict with §11.6 |
| D-6 | no store update/disappearance from invalid sets; no downstream uncertainty solely from such invalid set |
| D-7 | commit-reveal immutable scope, local history and population check, superseded seed exclusion, no CLI seed substitution, v2 deterministic sampling domain |
| D-8 | client-reported ordered CRLF headers, transfer-decoded body, Content-Encoding identity check; no wire capture claim |
| G8-01/G8-02 | sizes object even when both members null on available quote; scheduled/injected paths |
| E-3 | leap-second timestamp rejected |
| C-09 | V8 DATA_GAP precedes V10, insufficient history not first failure |
| E-1/E-2 | no boundary-violation record/TER value; HOLD mapping precedence |
| Auditor | local qualifying counters restored under attestation; raw injection replay, custody history checks and report distinctions; stdout only; Python 3.12 stdlib/Fraction |

No other intended changes to v1 chain keys, manifest keys, invocation-line format, policy JSON values or canonicalization. The local auditor requires Git to be installed, but its Python imports use only the standard library. Contract choices are not normative amendments. This artifact and script are pre-evidence deliverables; not independently verified against a harness or TER, nor an FD-5/Stage B authorization.

## 11. v2 → v2.1 clarification register (2026-11-26)

| Choice | Contract change | Auditor change |
|---|---|---|
| CC-01 | Transition old/new explicitly defined | None; matches prior replay |
| CC-02 | Raw policy bytes; layout free before pinning | None |
| CC-03 | Retain evidence-only bar partitions on V1/V2 failure | Reconstruct partitions before early return, without store mutation |
| CC-04 | Runtime proposals BUY only, EXIT unit tests unaffected | Enforce BUY side on runtime proposal schema |
| CC-05 | Decoded URL equivalence, UTC second precision | None |

No other intended semantic or schema changes. TER schema tag stays TER-1; v2 sampling domain stays byte-identical. No seed replacement or resampling. This revised auditor has a new SHA-256; founder must reconcile the auditor hash custody before any TER. If an auditor hash is already immutably committed, do not overwrite it or silently swap auditors; resolve custody under the frozen protocol before using the revised artifact. No authorization for credentials, Stage B or orders.

## 12. v2.1 → v2.2 candidate: synthetic pre-live findings

**Exposure:** frozen R4.2i, amended freeze record, own contract/auditor v2.1, and independently generated synthetic evidence only. No real repository, harness source/tests, actual TERs, credentials or real seed accessed. The founder handoff was read; its implementation/fixture claims were not used as test evidence.

- **CC-06 / U27 (§11.4):** optional `--reported-counter N` supplies the founder-reported harness longest consecutive qualifying streak across the audited run set, as a nonnegative safe integer. This is out-of-band comparison input, not an evidence record or authority for any slot or milestone. If provided, report claimed and recomputed values and `HARNESS_COUNTER_MISMATCH` when unequal. When absent, explicitly report `NOT_SUPPLIED`; no claim that a harness counter was compared. No change to TER, manifest, policy, chain, sampling, or seed.
- **U88 / §11.2 row 1:** a forbidden JSON integer slot_index stays a schema violation. For an already-invalid record, use its integer value only to identify the in-range affected slot for row-1 NON-QUALIFYING classification. Never treat it as a legal TER field or qualifying observation.
- **Custody:** v2.2 is a candidate, NOT the pinned auditor. Its adoption requires a founder-approved custody resolution before any actual TER, with the existing commitment and history preserved and no seed substitution or resampling. This candidate does not authorize editing any existing committed hash.

### 12.1 Optional pre-GENESIS auditor migration (CC-07 as revised by CC-08; requires founder adoption)

For an already-pinned v2.1 scope, the following narrowly scoped exception to the **contract choice** in §8 permits the new script hash to be committed before any TER, as required by frozen §11.5, without replacing the seed commitment or the original auditor pin. It does not change the frozen specification. Direct commitment of v2.3 with the seed remains the default for a fresh synthetic scope.

For an existing scope, preserve `seed.sha256` and `auditor.sha256` byte-for-byte. After their commitment and strictly before GENESIS (an additional conservative constraint), commit a single founder-adopted file `audit-scopes/<id>/auditor-migration.json`, closed JSON object:

```json
{
  "decision": "ADOPT_V2_3_PRE_GENESIS_PRESERVE_SEED",
  "from_sha256": "709137f259d82b709b924ed83789da0172038241b824af2ce2b9c69b18bba6d1",
  "to_sha256": "48629e8a4259ae09169cf4d9be59081e8aff25522306f04c99b89d94d55f0424",
  "seed_sha256": "<existing seed commitment hash, not the seed>"
}
```

Replace the angle-bracket placeholder with the existing 64-character commitment hash only. The migration record must be pushed before GENESIS and all TERs. It is a founder decision, not a script-created authorization or a second seed commitment. The auditor verifies the original pin remains immutable on first-parent history, the old pin equals issued v2.1, the migration is immutable and has no competing version in reachable history, the target equals its own raw script hash, and the seed commitment equals the preserved existing commitment. It rejects absent, late, changed or mismatched migration. It reports the original/effective hashes, mode and migration commit. No new seed, no new scope for the same manifests, no seed reveal, no resampling, no edits to the old pin. The first-parent, remote push timing and founder-authority limitations remain. This proposed migration is not adopted merely by delivery of this candidate.

**Historical seed limitation:** the local lookup of abbreviated `07f43e0` is Git-name resolution, not independent verification that the intended historical object was resolved. The synthetic test repositories use a local tag with this name and a synthetic seed file, explicitly not the historical object. Before any real run the founder must verify that the real resolved full commit ID has prefix `07f43e0`, that it is in the intended ancestry and that the original seed artifact is unchanged. Do not print its contents. No claim that synthetic custody proves real custody.

## 13. v2.3 candidate: repository-root custody correction (CC-08)

**Exposure:** frozen R4.2i, freeze record, own v2.2 artifacts and synthetic test generator, founder-reported read-only Git path listing and the founder's proposed Script I. No real repository access, real seed, harness source/tests or real TER. Founder output indicates the original commitment is at repository-root `audit-scopes/stage-a/`, not under `experiments/sl-pt-001/`. The v2.2 candidate was not adopted according to the supplied state; verify this before adoption.

- The sole custody namespace is repository-root `audit-scopes/<id>/`: `seed.sha256`, `auditor.sha256`, `auditor-migration.json`, `scope.json`, `seed.txt`. All five are addressed by absolute repository-relative paths in Git snapshots; `--evidence-root` continues to affect experimental evidence only. There is no alternate custody-root option or fallback.
- Any other ordinary committed `seed.sha256` under any directory component named `audit-scopes` anywhere in reachable Git history is a competing commitment, including the previously specified nested evidence-root path. No relocation, duplication or fresh commitment is permitted. The selected original commitment, migration and pin immutability checks retain their existing scope and chronology.
- For the actual experiment, use the default evidence root `experiments/sl-pt-001`, scope `stage-a`, and the original repository-root commitments. A sole pre-GENESIS migration directly from the pinned v2.1 to v2.3 uses the closed JSON object in §12.1 with the v2.3 decision token and effective hash. v2.2 is an unadopted candidate, not an intermediate pin; if any migration already exists, stop rather than replace it.
- The auditor reports `custody_path` and `evidence_root` alongside the existing migration metadata. Sampling domain, seed, TER schema, reconstruction, slot classification and evidence population are unchanged. No new normative requirement, no permission to start live cycles. The historical seed reference and remote push limitations remain. Keep the auditor source outside the shared repository under Founder Decision v5; commit its hash, not its source.
