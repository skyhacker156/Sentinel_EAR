# SL-PT-001 | Interface Contract TER-1 v1

**Exposure:** Only the three supplied files: `SL-PT-001_R4.2c_Stage_A_Review_Candidate_Claude_2026-11-26.md`, `SL-PT-001_Stage_A_Freeze_Record_2026-11-26.txt`, `SL-PT-001_Stage_A_Freeze_Record_Correction_2026-11-26.txt`. No harness code, tests, TER output, Claude conversations, credentials or orders were accessed. No repository access. The specification SHA-256 was computed from the attachment before any task work: `9d417fb5b22147eec6785816b239ad6b76215ea5f18e662432dc7e9cfb283d76` (MATCH); named git blob `316d08c046dd7e1ea4a61be980c037b1c62037d5`.

**Status:** independent, pre-TER interface proposal; not a change to the freeze or authorization to build or execute. Normative scope: §§2–7, 8.1/8.1.1, 10, 11, 13, Stage A tests/rows of §§14–16. Stage B draft is not used. The correction changes review attribution only. All serialization decisions not explicit in the frozen specification are **CONTRACT CHOICE** (CC). A choice cannot supply evidence that the frozen schema does not retain.

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
| used_bars | UsedBar[] | CC |

Nested closed shapes (CC except the four Request keys):

- Request = `{url:str, sent_at:ns, received_at:ns?, outcome:str}`. `RESPONSE` requires received_at and body/header artifacts; `NO_RESPONSE` requires received_at and both associated hashes null. Never issued = whole object null. `t_send` is bars sent_at even on NO_RESPONSE; `t_recv` is bars received_at. The two request objects cannot represent per-page requests; see §7 below.
- Bar = `{t:ns?, o:str?, h:str?, l:str?, c:str?, v:str?, vw:str?, n:str?, zero_volume:str?}`. CC: `zero_volume` = `TRUE` or `FALSE` on parseable v; otherwise null. Numeric members retain original JSON number token spelling, not decoded/reformatted numbers; null if unavailable/malformed. A malformed timestamp with no parseable instant cannot be reliably placed in completed/excluded and is reported from raw bytes. Arrays retain arrival order within each partition; identical duplicates collapse (record note in transitions). Sort separately for computation.
- Tuple = `{o:str,h:str,l:str,c:str,v:str,vw:str,n:str}` (raw tokens). Transition = `{t:ns, event:str, old:Tuple?, new:Tuple?, state:str?, observation_count:intstr?}`. CC event values `BASELINED`, `OBSERVED`, `SOURCE_REVISION`, `CONFIRMED`, `DISAPPEARED`, `DUPLICATE_COLLAPSED`. State `BASELINED`, `PENDING`, `CONFIRMED` or null. Counts refer to currently accepted tuple; on PENDING retain accepted count, confirmation starts new accepted count at 2. A→B→A is another revision (U40); require next same pending tuple to confirm. Duplicate note leaves state/count null; disappearance leaves accepted state/count unchanged. Record duplicate notes in arrival order first, then observations in sorted t order, then disappearances sorted by t (CC). For malformed/ambiguous sets the fold is not fully specified; see §7.
- UsedBar = `{t:ns,state:str,observation_count:intstr}` in ascending t order for the actual 51 used bars; otherwise [].
- Check = `{result:str, reason:str?}`; `PASS` or `FAIL` requires null reason; `NOT_EVALUATED` requires one of `V12A_FAILED`, `V12B_FAILED`, `FETCH_FAILED`, `DATA_INVALID`, `NO_PROPOSAL`. These values are frozen; shape CC.
- Proposal = `{instrument:str,side:str,order_type:str,L:dec,q:dec,R:dec,rounding_inputs:Rounding}`. `BUY` or `EXIT`; order_type `LIMIT`. Rounding = `{bid:dec,ask:dec,price_increment:dec,qty_increment:dec,min_order_size:dec,f_res:dec,shadow_cash:dec,shadow_reserved:dec,cash_available:dec,budget:dec,shadow_btc:dec,shadow_reserved_btc:dec}`. CC names/grouping for §7/8.1.1 inputs. On live BUY shadow BTC and pre-proposal reservations are zero. No TIF or partial-fill approval fields (Stage B only). EXIT reservation in fixture has no independently specified USD R convention; not invented here.
- RuleResult = `{rule:str,result:str}`; rule R1–R13 or R15–R16, result `PASS`/`FAIL`; only applicable rules included, numeric code order. CC: R2 limit-only included for §7.3 despite §11.6 saying R2 is B-only; R9/R15 EXIT-only, R12 BUY-only, R14 absent. This is an explicit conflict, not a silent resolution.
- Sizes = `{bs:str?,as:str?}`, original quote token text where available. Null when neither available.
- Terminal = `HOLD`, `NO_ACTION`, `REJECTED`, `SHADOW_EXPIRED`, `BOUNDARY_FAIL`, `CYCLE_OVERRUN`, or `NO_DECISION (REASON)` (CC spelling). REASON: `FETCH_FAILED`, `INCOMPLETE_RESPONSE`, `MALFORMED_VALUE`, `DATA_CONFLICT`, `STALE_SERIES`, `DATA_GAP`, `INSUFFICIENT_HISTORY`, `SOURCE_REVISION`, `QUOTE_INVALID`. A scheduled overrun is a separate chain record, not a successful CYCLE.

### Presence and precedence (§10.4)

| Path | Requests / artifacts | Checks and decision fields |
|---|---|---|
| V12a fail | neither issued; all hashes and clock fields null | V12a FAIL; all others NOT_EVALUATED/V12A_FAILED; computed fields, created, sizes null; arrays [] |
| Bars NO_RESPONSE | bars issued, no received_at or hashes; only t_send present; no quote | V12a PASS; all others NOT_EVALUATED/FETCH_FAILED; computed fields null; arrays [] |
| V12b fail | bars response and hashes; no quote | V12a PASS, V12b FAIL; remaining NOT_EVALUATED/V12B_FAILED; computed fields null; arrays [] |
| V1–V11 fail | both issued (quote may have NO_RESPONSE) | V1/V2 both evaluated, V3–V11 NOT_EVALUATED/DATA_INVALID if either fails; otherwise all evaluated; Q NOT_EVALUATED/DATA_INVALID; computed fields null |
| HOLD / NO_ACTION | both issued | V pass; Q NOT_EVALUATED/NO_PROPOSAL; proposal/created null; rules [] |
| QUOTE_INVALID | both issued | V pass; Q evaluated, at least one fail (all fail on absent quote); proposal/created null; rules [] |
| REJECTED / SHADOW_EXPIRED | both responses | V and Q pass; all applicable rules evaluated; proposal/created present; SHADOW_EXPIRED only if all pass |

Displayed sizes may exist even when Q not evaluated, when the quote was retained. Clock bounds null when Date cannot parse; if parseable, compute even if clock check fails. No additional TER key for append time, V12a evidence or intended injection rule exists.

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

Manifest closed object: `{instrument:str,T_d0:ns,declared_slots:integer,opening_cash:dec,frozen_set_hashes:HashMap,harness_sha256:hash,policy_sha256:hash,task_xml_sha256:hash,wrapper_sha256:hash,prev_chain_head:hash}`. HashMap is object mapping frozen file repository-relative names to exact SHA-256 strings (CC); must contain the named R4.2c path and hash; same map in GENESIS and manifests. T_d0 grid, N≥30, opening cash exactly 500.00 on cent grid; instrument BTC/USD. Raw manifest bytes determine hash. RUN_OPEN must directly follow prev_chain_head. Founder push before T_d0 is separate evidence, not proved by local git timestamps.

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

`rules`, `value` and per-rule encodings are CC; the top-level parameter names and source/status values are frozen. All numeric values strings. No inference from precision. File hash is raw SHA-256, recorded in each CYCLE and manifest. Policy changes need founder record and new version.

## 5. Layout (§§6.1, 10.1–10.3)

CC: evidence root is `experiments/sl-pt-001/` relative to repository root (explicit auditor override available). Relative paths:

- `chain/events.jsonl` global chain, one complete JSON record per LF-terminated line, no blank lines (CC newline).
- `artifacts/<sha256>` exact bytes of body and headers separately. CC headers are exact HTTP status line and header block, CRLF-separated, terminating CRLF CRLF; must include status line to reconstruct V1 and Date to reconstruct V12b. No normalization. If the HTTP client cannot retain this representation, the evidence format needs founder resolution; a JSON header mapping alone cannot prove exact response bytes/status.
- `chain/invocations/<manifest_sha256>.log` wrapper log.
- `runs/<name>.json` founder manifest; auditor scans recursively and reports duplicates.
- `policy/P-0.2.json` frozen policy version.
- `chain/tasks/<task_xml_sha256>.xml` (CC location for the preserved XML §6.1; wrapper hash retained in manifest, wrapper source path not specified and not read by auditor).

Artifacts not referenced by any committed record are orphans, not evidence. Git object bytes from audited commit, not working-tree files, are used by the auditor. Symlinks/submodules are not evidence files. Script never accesses network or writes evidence.

## 6. Canonicalization (§10.5)

RFC 8785 JCS: UTF-8, no BOM, no insignificant whitespace, JSON strings escaped per ECMAScript JSON rules, control characters escaped; preserve Unicode (no normalization), reject lone surrogates and duplicate object keys, recursively sort object member names by unsigned UTF-16 code units, preserve array order. TER has no numeric/boolean primitives. Outside TER, this contract admits only safe integer JSON numbers, whose decimal rendering is exactly JCS (no binary arithmetic needed); other numeric primitives are rejected. Record hash = lowercase SHA-256 of canonical UTF-8 bytes of `{seq,prev_hash,type,body}` (omit `hash`, not null). Raw artifact, log, manifest, policy and XML hashes cover their exact raw bytes. JSONL itself need not be canonical for the hash to verify; exact source bytes remain auditable through git.

## 7. Frozen evidence gaps and auditor treatment (not new fields)

1. **V12a:** only its result and egress marker are retained. Actual environment/config check and exact client allowlist are not retained as raw artifacts. URL checks can contradict but cannot independently prove V12a. All otherwise qualifying slots remain **NON-QUALIFYING (unverified)** in the strict report; a separately labeled conditional classification shows the result if the missing boundary and timing facts were supplied. No TER assertion upgrades the strict result.
2. **Commit timing:** no CYCLE append instant or independent append timestamp is defined; SHADOW_EXPIRED at the ceiling and all commits before next slot cannot be independently established. Git dates are self-asserted. No new TER field invented.
3. **Injection intent:** §10.1 retains proposal/result but not committed intended rule, fixture ledger, injection command/time or provenance. Five rejected results are not proof of five intended-rule rejections. M1-1 remains not established; reported injection counts are not certified. EXIT fixtures cannot be fully reconstructed from this schema.
4. **Pagination:** V2 allows complete pagination, but exactly two request objects plus single response/hash pairs cannot represent ordered page requests/responses. First page with non-null token is not reconstructible as a complete set; report INCOMPLETE_RESPONSE or unresolved pagination, never certify. A new format decision is needed for successful multi-page cycles.
5. **Revision edge cases:** §4.9/U40 imply a return to accepted tuple while pending is another revision; invalid/ambiguous bar sets have no fully specified observation rule. CC: do not fold bars when V1/V2 or V3/V4/V9 fail; mark downstream store provenance uncertain if that decision can matter. V7/V8/V10 failures do not prevent folding valid observations. V5/V6 are deterministic transformations. V1 wrong quote symbol (U95) is treated as failure if a quote response exists, but quote NO_RESPONSE does not fail V1 (U113). Quote HTTP/JSON failure otherwise handled in Q when proposal required. V1 vs V2 subreason: HTTP/JSON/symbol → FETCH_FAILED; missing required keys → INCOMPLETE_RESPONSE (CC).
6. **Malformed arrays:** exact recording of unparseable timestamps or non-numeric tokens and V3–V11 evaluation on malformed sets is not fully specified. Auditor reports ambiguity instead of claiming equivalence. R3 checks the constructed Stage A shape; an L rounded to zero has no defined sizing result (§8.1.1 assumes L>0), so report unresolved rather than invent a zero-division rule.
7. **External completeness:** git HEAD does not prove GitHub push timing or that no unpushed/rewritten history exists, nor actual wrapper/task behavior. The seed is passed as exact UTF-8 text; its pre-run commit/push is not independently proved by this interface. Optional seed path checks committed bytes only. The hand cross-check of one manifest is founder work. FD-6 common-mode risk remains.

**Sampling CC:** rank every committed CYCLE with origin SCHEDULED by `SHA256(b"SL-PT-001/FD-6/v1\\0" + seed_utf8 + b"\\0" + ASCII(seq))`, ascending digest then seq; take first five without replacement, including failures and duplicates; no outcome filtering. If fewer than five, report shortfall. Global raw replay for all CYCLE records is required for bar-store history and slot audit; the selected five are separately enumerated with detailed differences. Do not substitute another cycle after selection.

**Required claim limit (§2.3):** "Disconnection from trading is asserted at the HTTP-client level only. Alternate egress paths in the process or host (other libraries, raw sockets, proxies, inherited handles) were not excluded." No G-07, profitability, broker behavior or host isolation claim. Stage A sizing remains CONDITIONAL on unverified venue increments and fees; clock claims conditional on A-CLK/A-CLK2 and unverified host UTC accuracy.
