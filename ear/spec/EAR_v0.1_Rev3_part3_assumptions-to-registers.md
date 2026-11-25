SPECIFICATION ONLY / NOT IMPLEMENTED / NOT VERIFIED
Exposure Accounting Reference Model v0.1, Revision 3 (frozen). Part 3 of 3. Full-file SHA-256: 9a2c3be747fa9acbe4513e77f4122712f1970aa17109beb52acffbe051702b0a
---PART-BODY-START---
### 2.11 Assumptions and their classification [R to state, not to resolve here]

Classes: **M** mathematically required, **E** environmental hypothesis, **I** implementation requirement, **O** operational dependency, **D** deferred. A broker-environment hypothesis is never to be read as a mathematical fact.

| ID | Assumption | Class | Failure could cause permission that would otherwise be denied |
|---|---|---|---|
| A-1 | Single instrument | M (scope) | low: foreign ids are quarantined |
| A-2 | **Input contract:** where broker_seq is present it is one monotone sequence per account, and a watermark W means the snapshot contains exactly the executions with broker_seq <= W (absent sequence numbers mean unknown timing). Not established for any real broker | **E** | yes |
| A-3 | The store provides atomic compare-and-set | I | yes |
| A-4 | An independent clock exists | O | yes |
| A-5 | The future adapter submits only with a live reservation token | O | yes |
| A-6 | W1 to W7 (section 2.3), hypotheses about the modeled broker environment | **E** | yes |
| A-7 | The state keeper's ledger is honest and complete as given (trust mechanism open, D05, D23, D24) | O | yes |
| A-8 | Q_MAX, L, TTL, K, D_max and the staleness and wait limits are configuration, pinned by hash and identified like TierConfig | I | low |
| A-9 | The pure functions receive the as_of time as an explicit input from the independent clock; at commit the same function is called again with the commit time | I | low |
| A-10 | The master version id and content hash are supplied as evidence | I | low (fails closed) |
| A-11 | Events carry stable event ids (otherwise the hash of canonical content). **Idempotency by event ID does not establish economic-execution uniqueness**; a duplicate economic execution under a different id is uncovered | **E** | yes (V56) |
| **A-12** | **Event delivery is complete between snapshots, except for unreported fills of known working orders (W4).** Snapshot freshness and decision age do **not** establish it; no formula covers its failure; a later snapshot can only reveal a failure after the fact | **E** | **yes** |
| A-13 | Integers only; no floating-point quantity enters accounting | M | none |

### 2.12 Instrument identity and master: the v0.1 minimum [R/H as marked]

The full master-governance requirements of the addendum are broader than this model needs. v0.1 keeps only what the accounting decision depends on.
- [R] **Canonical identity.** Every order, execution and snapshot carries an instrument id. A symbol or alias is not authority-bearing identity. An id that is not the model's canonical instrument id is quarantined (D13): an execution or event with such an id is T2-U (UNBOUNDED until resolved); a snapshot with such an id is rejected and logged.
- [R] **Master version pinned.** Each evaluation records the master version id and content hash in force. They are opaque inputs to v0.1 and are part of the item hash and of the commit check (I5).
- [R] **Semantic master change (class B), modeled as one event type, E24.** Class B means a change to the tradable flag, validity end, alias or symbol mapping, lot size, multiplier, currency or price increment. Effects, in one revision step: every AUTHORIZED-not-submitted order expires (T05) and its reservation is released, to be re-proposed under the new version; every working order stays as sent, flagged, and is not reinterpreted (R is kept); position status becomes UNKNOWN until the broker reconciles under the new version, so increases and reductions are blocked (R_MASTER_CHANGE); if lot size, multiplier or currency changed, quantities are not comparable across the change and remain unknown until the broker confirms them. Class A (metadata only): record the new version, no accounting effect. This answers RQ11: a semantic change releases unsubmitted authorizations and blocks activity until reconciliation; it never silently reinterprets a working order.
- [H] Retroactive corrections create a new version marked as a correction; history is never edited; effective-time lookups are as of the decision time on the independent clock.
- **Deferred or excluded** (2.13): provenance chain and founder-authorized change workflow in detail, audit-history mechanics, multiplier, notional, price-band and risk implications (G-04), corporate-action flags (excluded by the envelope), master ownership, review frequency and maximum age (OPEN, D25).

### 2.13 Change log: disposition of each addendum provision

| Addendum provision (section: item) | Disposition | Note |
|---|---|---|
| 1: Five evidence properties | Incorporated | 2.8 |
| 1: Failure states and reason codes | Incorporated, modified | Property-prefixed; INTEGRITY.MISMATCH vs POSITION.MISMATCH; quantified vs structural Consistency failures (D19) |
| 1: NO_INDEPENDENT_EVIDENCE rule | Incorporated | Not tolerated for reductions (D06); other tolerance OPEN (D24) |
| 1: State-keeper compromise, key management | Incorporated as OPEN | A-7 stated; D05, D23 |
| 2.1 E1 envelope, E7 log integrity, E8 originators: Event identity, hash-chained log, rejection of unauthorized sources | Incorporated | 2.2, 2.6.3, IB1 |
| 2.1: E2 idempotency | Incorporated, modified | A conflict is a structural evidence failure, not a position MISMATCH status |
| 2.1: E3 determinism | Modified | Canonical order is the log position, not broker_seq or receipt time (D20, F-7) |
| 2.1: E4 out-of-order, E5 gaps | Incorporated | Pending items, GAP status |
| 2.1: E6 corrections | Incorporated, modified | A correction naming an unknown original makes the band UNBOUNDED (V31), not just status UNKNOWN |
| 2.2 definitions and seven statuses | Modified | Consolidated in 2.2 and 2.6.2 with bounded/unbounded per status |
| 2.3 snapshot comparison a to f | Incorporated | Case table in 2.6.2 |
| 2.3 case c (snapshot ahead) | Modified | UNBOUNDED, D18 (F-4) |
| 3.1 transitions T01 to T22 | Incorporated | Accounting-effect column added (2.6.1) |
| 3.1 IB1 to IB4, T22 | Modified | IB3: execution held as a pending item, not applied (F-8). IB4: structural evidence failure, not position MISMATCH |
| 3.1 terminal-transition rule | Incorporated, clarified | As-of net_cum_at (RQ8) |
| 3.2 history versus net_cum | Incorporated | I7, V30 |
| 4 UNKNOWN classification and blocks | Incorporated, modified | Block matrix 2.7; reductions during quantified MISMATCH (D19) |
| 4 human override | Deferred | D11: none in v0.1 |
| 5.1 K1/K2/K3 | Modified | Formally mapped (2.4.1); K3 side-aware (RQ1) |
| 5.2 max formulas and explanation | **Excluded: SUPERSEDED (D14)** | Historical only; the oracle and model never use them (except as a test-only variant to demonstrate the failure, Appendix A and 5.1) |
| 5.2 A = max(0, A_raw); deny-not-clip; reduction needs bounded band | Incorporated | 2.4 |
| 5.3 OVER_RESERVED | Incorporated | I3, I8 |
| 5.3 "state-keeper may cancel working sells" | Excluded | Authority to cancel is outside v0.1 (D10 amended, G-07) |
| 5.4 atomic reservation and CAS | Incorporated, extended | Decision age and revision coverage (2.9, F-6) |
| 5.5 invariants I1 to I5 | Modified | Reconciled into I1a to I9 (2.5); original I4 not retained unconditionally |
| 5.5 worked examples 1 to 6, 8 to 10 | Incorporated | As vectors V01 to V16 |
| 5.5 worked example 7 | **Superseded (D14)** | V08a, V08b |
| 6 master provenance, versioning, change authorization, effective time, audit | Incorporated minimally, rest deferred | 2.12; D25 |
| 6 class A and class B master changes | Incorporated minimally | E24, V35 |
| 6 indirect effects (multiplier, notional, price bands, corporate actions) | Excluded | G-04 and the envelope |
| OPEN items (master ownership, review frequency, maximum age; timeouts; wait limit) | Deferred | D07, D08, D25 |

### 2.14 Reconciliation register (RQ1 to RQ12)

Each entry: the conflict or ambiguity, the competing interpretations, the recommended resolution, safety and availability consequences, whether founder approval is required, whether it blocks implementation. "Approval" means explicit approval of the recommended default.

| RQ | Conflict or ambiguity | Interpretations | Resolution | Safety / availability | Approval; blocks implementation |
|---|---|---|---|---|---|
| RQ1 | How K1/K2/K3 map to the six quantities | Copy K1/K2/K3 directly; map formally | Formal mapping (2.4.1). K3 is side-aware: Q3_buy to F_max, Q3_sell to F_min, Q3_unk to both (the addendum used the absolute quantity on both bounds) | Soundness unchanged (hand-derived); a buy orphan no longer reduces A, so more availability than the symmetric form | No (flagged for challenge); no |
| RQ2 | When is a discrepancy additional uncertainty and when an alternative explanation of an orphan | Alternative (max); additional (sum) | Sum rule always in v0.1: no relationship is inferred; it is established only by applying the orphan, after which d recomputes (D01). H-LINK deferred | Sound; over-denial classes G1 and G2 | Already decided (D01); no |
| RQ3 | How V08a and V08b differ, and which evidence selects the treatment | Treat differently; same formula | The formula is the same. The evidence (broker_seq > W or <= W or absent) selects only the oracle's world set and the gap class; V25 (no sequence) enumerates both | V08a tight, V08b a measured gap of 5 | No; no |
| RQ4 | Orphan side unknown | Count against one side; both | Q3_unk on both bounds (V12) | Sound; costs reducible quantity on the high side | No; no |
| RQ5 | Execution received without a resolvable order identity | Drop; hold as orphan; guess an association | Orphan item by event_id (T1, T1u, T2 or T2-U); never dropped; if it later resolves to a known order the order's R and the orphan overlap until applied (conservative) | Sound; temporary over-denial | No; no |
| RQ6 | Does every unresolved item block increases; which also block reductions | Addendum text (evidence failure denies reductions) versus its own K1 band and D01 (MISMATCH bounded, reductions used) | Every unresolved item blocks increases; the block matrix of 2.7 says which also block reductions. A quantified MISMATCH does not block reductions; structural conflicts do (D19) | Permits reductions during a bounded mismatch (false-permission risk measured by the oracle); alternative denies them (availability loss) | **Yes (D19); yes** |
| RQ7 | Are the addendum's seven statuses consistent with bounded/unbounded | Addendum bounds AWAITING-BEHIND by F_b; model says unbounded | AWAITING-BEHIND, AWAITING-UNVERIFIED, GAP, UNKNOWN are UNBOUNDED (2.6.2). Trusting the snapshot here is unsound under W1 (F-4) | Safe; reductions UNRESOLVED during the wait | **Yes (D18); yes** |
| RQ8 | Terminal-transition cumulative-quantity rule versus busts and corrections after confirmation | Compare with latest net_cum; compare as-of the event | As-of: net_cum_at(order, the event's broker_seq). Later busts and corrections are T21 events and do not falsify the earlier report | Avoids false conflicts on valid history | No; no |
| RQ9 | Deterministic replay with absent or inconsistent sequence numbers | Receipt order; broker_seq order; log position | Log position is canonical; broker_seq is only for gaps and watermarks; inconsistent sequences are conflicts (2.6.3) | Replay reproducible; no claim of order-invariance for non-commuting events | **Yes (D20); yes** |
| RQ10 | Does the revision counter cover all accounting-relevant changes | Counter only; counter plus item hash plus time check | Coverage list, item hash as a second check, and a maximum decision age (2.9, F-6) | Closes the time-staleness gap; adds a parameter | **Yes (D21); yes** |
| RQ11 | Does a master change always invalidate an authorization | Always release; sometimes; never | Class B: release every unsubmitted authorization, keep working orders as sent, block until reconciled; class A: no effect (2.12, E24, V35) | Safe; blocks activity until reconciliation | **Yes (D22); yes, for E24 only** |
| RQ12 | Which addendum requirements are beyond the approved envelope | Keep all; exclude and defer | Excluded or deferred: full master governance, multiplier and notional logic, corporate-action flags, key-management mechanics, human override, authority to cancel, protective intervention. The model treats the master version and signature fields as opaque evidence, so excluding them does not weaken the accounting | No effect on the accounting claims | **Yes (D22 confirms the exclusions); yes** |

---

## 3. Decision register (Deliverable B)

### 3.1 Decisions already taken (founder, 2026-11-22)

| ID | Decision | Outcome | Where |
|---|---|---|---|
| D01 | Discrepancy plus orphan | **APPROVED:** sum rule normative; H-LINK not adopted | 2.4, Appendix A |
| D02 | World model W1 to W6 | **APPROVED WITH ADDITIONS** (dispatch 2026-11-22, item 1, as read by Claude): clarification (2.3, W1 to W7) and Revision 3 additions (A-12, A-2 as input contract, 2.2 definitions). A hypothesis about the modeled environment, not a fact about any broker | 2.2, 2.3, 2.11 |
| D03 | Reservation TTL | Approved default: fixed TTL on the independent clock, value a parameter | 2.9 |
| D04 | One revision counter | Approved default: single counter | 2.9 |
| D05 | State-keeper trust and authenticity | Approved default: state A-7 plainly; decide before any broker contact | 2.8 |
| D06 | NO_INDEPENDENT_EVIDENCE for reductions | Approved default: not tolerated | 2.8 |
| D07 | Snapshot staleness limit | Approved default: parameter, no value here | 2.6.2 |
| D08 | Wait limit, reconciliation interval, UNKNOWN timeout | Approved default: parameters, no values here | 2.6.1, 2.6.2 |
| D09 | Commit retry bound | Approved default: K = 3, DENY on exhaustion | 2.9 |
| D10 | Authority for cancellation | **AMENDED:** events only; no authority implied; G-07 | 2.6 |
| D11 | Human override | Approved default: none in v0.1 | 2.13 |
| D12 | Q_MAX and malformed quantities | Approved default: reject outside [1, Q_MAX] | 2.1 |
| D13 | Foreign instrument id | Approved default: quarantine | 2.12 |
| D14 | Addendum 5.2 and example 7 | **APPROVED and done:** marked SUPERSEDED, history preserved | addendum |
| D15 | DENIED state | Approved default: confirmed | 2.6.1 |
| D16 | UNRESOLVED distinct from DENY | Approved default: distinct, both non-authorizing | 2.4 |

### 3.2 Decisions D02 and D17 to D22 (recorded per founder dispatch 2026-11-22, item 1)

GPT's dispositions are technical review positions. The approval column records the founder dispatch of 2026-11-22, item 1, as read by Claude; it is open to founder correction. Founder approval is not verification. "Closing evidence" is what would close the item.

| ID | Decision | GPT provisional | Claude position (Revision 3) | Founder approval | Closing evidence |
|---|---|---|---|---|---|
| D02 | World model, with additions | accept with additions | Accept with additions: A-12 named; A-2 an input contract; 2.2 definitions (unsequenced executions, F_d(W) by event seq) | Approved (dispatch 2026-11-22, item 1, as read by Claude) | Reviewer counterexample attempts against W1 to W7; before any broker contact, a separate study of an actual broker's semantics |
| D17 | U_unknown and A_unknown identically zero | accept with modification | Accept with modification: inventory 2.4.2 normative; zero-assertion test | Approved (dispatch 2026-11-22, item 1, as read by Claude) | The inventory reviewed by GPT and Gemini; the test written |
| D18 | Snapshot ahead of events, or no watermark with a busy ledger: UNBOUNDED | accept | Accept as proposed | Approved (dispatch 2026-11-22, item 1, as read by Claude) | Oracle run on AWAITING-BEHIND ledgers (no numeric bound reported) |
| D19 | Reductions allowed within A during a quantified MISMATCH | conditionally accept as a specification candidate, not an established safety property | Conditionally accepted; five preconditions (I2); rollback to blocking reductions if the oracle finds any false permission on a MISMATCH ledger; **zero false permissions in the declared test space cannot establish safety against conditions excluded from W1 to W7** | **Approved only as a conditional specification candidate** (dispatch 2026-11-22, item 1); not an established safety property | Executed oracle run, then independent review; the world model is not thereby validated |
| D20 | Replay order is log append position | accept with explicit limits | Accept with the limits listed in 2.6.3 | Approved (dispatch 2026-11-22, item 1, as read by Claude) | Replay and idempotency tests (5.6); the non-commuting vector V49 |
| D21 | Maximum decision age D_max | accept with commit-time freshness revalidation | Accept with revalidation at commit (2.9, I5): snapshot age re-checked against S_lim at commit; S_lim not extended by D_max. Value of D_max OPEN | Approved (dispatch 2026-11-22, item 1, as read by Claude) | V44; interleaving tests; value chosen when parameters are set |
| D22 | Minimal master change handling (E24) and the RQ12 exclusions | accept within the existing scope | Accept within scope | Approved (dispatch 2026-11-22, item 1, as read by Claude) | V35; no governance process added |

### 3.3 Deferred OPEN decisions (do not block the v0.1 reference model)

| ID | Decision | Options | Recommendation | Consequences | Blocks implementation | Founder approval |
|---|---|---|---|---|---|---|
| D23 | Signing-key holder, rotation, revocation, response to suspected compromise | Not decided | Decide before any broker contact; hypothesis: authority holds only a verification key, fail closed on suspected compromise | v0.1 states A-7 instead | No (blocks any broker contact) | Yes, later |
| D24 | Independent evidence required for any future live use; whether NO_INDEPENDENT_EVIDENCE is tolerated outside reductions in a first replay | Not decided | Require a second read-only channel for live use | v0.1 cannot test common-mode failure | No | Yes, later |
| D25 | Master owner, review frequency, maximum master age | Not decided | Owner = founder; frequency and age after the first replay | Not needed for a single fixed instrument | No | Yes, later |

## 4. Executable-model plan (Deliverable C). Not implemented.

Small and bounded. Pure Python, standard library only, no network, no broker adapter, no clock or randomness inside pure functions, no import from `sentinel_core*`.

**Module boundaries**
- `exposure_model/types.py`: frozen dataclasses with exact-type validation (no bool as int, no floats): `Order`, `Execution`, `SnapshotEvidence`, `OrderEvent`, `Proposal`, `Config` (L, Q_MAX, TTL, K, D_max, staleness and wait limits; pinned by hash), `Ledger`, `Decision`, `Reservation`.
- `exposure_model/log.py`: the append-only, hash-chained event log and canonical serialization (sorted keys, integers only, UTF-8). `apply_event(ledger, log_entry) -> Ledger` is pure and implements 2.6 (lifecycle, idempotency, pending items, orphan items, statuses).
- `exposure_model/accounting.py`: `derive(ledger, config, as_of) -> Accounting` (F_d, F_d(W), d, F_min, F_max, B, S, U, A_raw, A, status, BOUNDED, flags, evidence results). One formula set, the one in 2.4.
- `exposure_model/authority.py`: `evaluate(ledger, proposal, config, as_of) -> Decision`; no caller-supplied derived values, no mutation, no reservation.
- `exposure_model/store.py`: the only stateful module: `read()`, `commit(decision)` (which re-calls the pure `evaluate` with as_of = commit time, 2.9), `apply(log_entry)`, serialized, with the compare-and-set of 2.9, in-memory only, a deterministic scheduler for tests (no threads).

**Immutable data structures.** Tuples and frozen dataclasses; the item list is a canonical, sorted tuple; item_hash = SHA-256 of its canonical serialization plus master version and configuration hash.

**Event and execution ledger representation.** Orders keyed by order_id with the append-only lifecycle history and a derived net_cum; executions keyed by exec_id with kind NEW, CORRECT or BUST and reference; orphan and pending items keyed by event_id; snapshot evidence keyed by snapshot_id; every entry carries its log position, raw_hash and, if present, broker_seq.

**Failure and reason-code representation.** An enumeration of the reason codes of 2.9 and the evidence codes of 2.8; a Decision carries the full list of applicable codes, never a single "error".

**Test organization**
- `tests/test_vectors.py`: frozen vectors V01 to V56 loaded from data files, with their hand derivations.
- `tests/test_events.py`: every event and transition (E01 to E24, T01 to T22), duplicates, conflicts, malformed input.
- `tests/test_snapshots.py`: the seven snapshot cases and statuses.
- `tests/test_invariants.py`: I1a to I9 against the oracle.
- `tests/test_replay.py`: idempotency, double-replay hash equality, duplicate injection.
- `tests/test_commit.py`: CAS interleavings and the concurrency scenarios.
- `tests/test_enumeration.py`: consumes the oracle's output.
Separate package `exposure_oracle/` (5.1) shares no code with `exposure_model/`.

---

## 5. Verification plan with an independently structured oracle (Deliverable D)

"Independently structured" here means separately written and separately checkable, not that a second model agrees. Until an external author writes or re-derives it, the oracle is an **independently structured reference oracle**, not independent verification. Same-author work is labelled same-author.

### 5.1 Oracle construction
Separate package `exposure_oracle/`, written from the world model (2.3) and importing nothing from `exposure_model/`. It reads only the raw ledger items (orders with qty and net_cum, executions, the snapshot with F_b and W, orphan and ambiguous items with side, quantity and broker_seq). It does not use the formulas of 2.4 and does not call any model function.
For each ledger it enumerates worlds as the product of:
1. the snapshot class: W1-T or W1-F (when status is RECONCILED, AWAITING or MISMATCH; for GAP, UNKNOWN, AWAITING-BEHIND, AWAITING-UNVERIFIED or any T2-U item it reports UNBOUNDED and enumerates nothing);
2. for each T1u item: side buy or sell; for each T2 item: did not occur, occurred as buy, occurred as sell;
3. for each occurred orphan item with no broker_seq: timing T3 or T4 (fixed when broker_seq is known);
4. for each working order: unreported fill x in [0, R], placed before or after W.
For each world it computes P by the world values in 2.3, then U_w and A_w. U_oracle = max over worlds of U_w; A_oracle = min over worlds of A_w. The model is **sound** on a ledger iff U >= U_oracle and A_raw <= A_oracle. The gaps U - U_oracle and A_oracle - A_raw are reported per ledger and attributed to class G1 (T3 item counted twice), G2 (unreported fill at or before W counted twice), G3 (known-side orphan not credited against the opposite bound), or UNEXPLAINED. Any UNEXPLAINED gap, and any soundness violation, is a counterexample and is reported with its minimal reproduction.
**Safeguards (C-11).** (1) The world semantics (2.3) are frozen before the oracle is written; (2) the oracle derives from raw ledger facts, never from model-derived fields; (3) it imports no model type, formula, helper or normalizer; (4) it uses a distinct ledger representation (raw-fact JSON); (5) it enumerates admissible worlds directly; (6) hand-derived examples include ones neither implementation generated, authored by a reviewer where possible; (7) GPT and Gemini challenge the oracle's assumptions and expected results; (8) counterexamples and failed tests are preserved permanently; (9) the oracle's source hash is recorded before it sees any model output; (10) where feasible a reviewer derives a small oracle from the specification without seeing this one.
**Three separate comparisons (C-11).** (a) *Bound soundness*, bounded cases only: U >= U_oracle and A_raw <= A_oracle, on the raw numbers, A_raw of any sign. (b) *Decision soundness*: ALLOW of an increase Q implies U_oracle + Q <= L; ALLOW of a reduction Q implies 1 <= Q <= A_oracle, so with A_oracle < 0 nothing may be allowed. **False permission is a violation of (b).** (c) *Flag soundness*: A_oracle < 0 implies OVER_RESERVED is raised; a ledger the oracle reports UNBOUNDED must resolve to UNRESOLVED or DENY in the model. Excessive conservatism (the model denies what the oracle would allow, or U exceeds U_oracle) is availability cost, classified G1, G2 or UNEXPLAINED, and is never counted as a safety defect; it is reported separately. Negative A_raw is a diagnostic, never an available quantity.
Hand-calculated vectors (V01 to V56) are the second, formula-free anchor.
**Expected results, HYPOTHESIZED, not executed:** the sum rule is sound on every enumerated ledger; all gaps fall in G1, G2 or G3; the previously proposed max rule (Appendix A, as a test-only variant) fails soundness at V08a-type states.
**Same-author caution:** the oracle is separate in structure and has no shared code, but if I write it, it is not independently authored. It is labelled same-author until an independent reviewer writes or re-derives it.

### 5.2 Bounded exhaustive enumeration (exact bounds declared before running)
- Position F_d in 0..4 (5 values).
- One buy slot and one sell slot, each absent or a working order with qty 1..3. Valid (state, net_cum) combinations per slot: q=1: 5; q=2: 8; q=3: 11 (AUTHORIZED, SUBMITTED, ACKNOWLEDGED need net_cum=0; PARTIALLY_FILLED needs net_cum in 1..q-1; CANCEL_PENDING and UNKNOWN net_cum in 0..q-1). 24 plus absent = 25 per slot, 625 order combinations.
- Position status: bounded statuses RECONCILED, AWAITING, and MISMATCH with d in {-2,-1,+1,+2} (6 values); unbounded statuses GAP, UNKNOWN, AWAITING-BEHIND and AWAITING-UNVERIFIED (4 values).
- Orphan configurations (at most one item):
  - bounded statuses: none (1); T1 side {buy,sell} x qty {1,2} x timing {T3,T4,unknown} (12); T1u qty {1,2} x 3 timings (6); T2 parseable qty {1,2} x 3 timings (6); T2-U (1). Total 26.
  - unbounded statuses (timing is irrelevant): none (1); T1 (4); T1u (2); T2 (2); T2-U (1). Total 10.
- Ledger states, **generated (Cartesian product, an upper bound, not a count of valid cases)**: bounded 625 x 5 (F_d) x 6 (statuses) x 26 = 487,500; unbounded 625 x 5 x 4 x 10 = 125,000. **Total generated 612,500.** A written validity predicate, declared before the run, removes inconsistent combinations (for example a MISMATCH d impossible for the chosen F_d, or a timing label for an orphan with no sequence evidence); each removal carries a reason code. (AWAITING has the same formulas as RECONCILED; it is included to test status dispatch.)
- Proposals: side {buy, sell} x qty 1..4 = 8, giving 4,900,000 cases per exposure-limit value, and **14,700,000** across L in {4, 6, 8}. These are arithmetic counts, to be confirmed when executed.
- Second variant: two buy slots and no sell slot, and the reverse, to reach same-side combinations.
- Event sequences (C-01): single order, all sequences of length 1 to 4 over the **11** event types named here: E04, E05, E06, E07, E08, E09, E12, E13, E14, E16, E17. The count is 11 + 11^2 + 11^3 + 11^4 = 11 + 121 + 1,331 + 14,641 = **16,104** sequences, before parameter choices and before the validity filter (EXECUTED arithmetic, Python integers; 14,641 is the length-four count alone). No twelfth event is added: E11 (status UNKNOWN) and E15 (execution out of order) are existing events not in this list; they are exercised by the UNKNOWN order states and the GAP status of the ledger enumeration instead, and are recorded as declared exclusions from the sequence enumeration. At most one applied execution with no broker_seq is generated per ledger (a declared bound).
- World enumeration per ledger is at most a few hundred worlds. If the full run is not feasible in the available time, any sampling must be declared **before** running and the result is then not called exhaustive.
- **Counts kept separate (C-01):** generated states; valid states; excluded states (with reasons); evaluated proposals (valid states x proposals x L); distinct event sequences (after removing duplicates and invalid prefixes); CAS schedules (interleavings per scenario times scenarios); test executions after deduplication (identical canonical ledger and proposal hash removed). A Cartesian-product bound is never presented as the number of valid or meaningful cases.
- **Coverage report columns (C-02):** false permissions; false denials of legitimate reductions; false denials of legitimate increases; correct denials; unbounded outcomes; structural evidence failures; invariant violations; oracle disagreements; excluded combinations; generation bias; duplicate or redundant cases; runtime and resource consumption.
- Reported on completion: total states and cases, invariants checked, counterexamples (with minimal reproduction), excluded combinations (more than one orphan, more than two orders, quantities > 3, negative positions, multiple instruments, more than one snapshot), generation bias (small quantities, single orphan, no interleaved busts), whether every transition class (E01 to E23) and every uncertainty class (2.7 rows, T1 to T4) was reached.
- Safety and availability measured separately: false permission (must be 0 for soundness), false denial of a legitimate reduction, false denial of a legitimate increase, correct denial when evidence is insufficient. "Legitimate" is defined by the oracle's worlds. The G1 and G2 gaps are reported as availability cost, not as defects (D01). A model that denies everything fails the availability metrics.
- What it can establish: "exhaustive over the declared finite state space and assumptions". It does not prove the architecture or the system safe. **Zero false permissions in the declared space cannot establish safety against conditions excluded from W1 to W7** (requirement C): undelivered events, duplicate economic executions, wrong-side association, a false state keeper. A model that denies everything fails the availability metrics.

### 5.3 Property-based and generative tests
Random ledgers beyond the enumeration bounds (larger quantities, more orders, up to 6 events) with a fixed seed recorded; checked against the oracle where world enumeration is tractable, and against invariants I1a to I9 elsewhere. Shrinking to a minimal counterexample on failure.

### 5.4 Concurrency and CAS simulation
Deterministic scheduler, no threads: each proposer is a sequence (read, evaluate, commit), each broker event is one step. All interleavings are enumerated; for two proposers (3 steps each) plus one broker event: 7!/(3! 3! 1!) = **140** schedules, for each scenario in dispatch section 8 (two sells of 60; two buys; buy and sell; fill, cancel confirmation or UNKNOWN between evaluation and commit; stale replay; duplicate commit; reservation expiry; release after reject or cancel; partial fill then cancel; commit failure after a valid decision). Check I2 and I5 after every schedule: total committed sell reservations never exceed A at their commit revision.

### 5.5 Frozen vectors, reproduction, artifacts
Frozen vectors V01 to V56 stored as data with hand derivations. Reproduction: one command, fixed seeds, pinned Python version, hash of the spec, model, oracle and config printed on every run. Preserve: spec hash, source hashes, bounds file, full result JSON, counterexample list, interleaving traces, environment (Python version, OS). A reviewer reproducing the run is labelled "reproduced", never "independently verified" unless the reviewer wrote the oracle without seeing the model.

### 5.6 Replay, idempotency, serialization, counterexamples, reproduction, evidence

- **Replay and idempotency.** For every enumerated event sequence and every generated log: (a) fold the log twice and compare the SHA-256 of the canonical serialization of the ledger and of every decision; (b) inject a duplicate of each event at every position and check the ledger is unchanged; (c) re-serialize and re-parse the log and check equality. Order-invariance is tested only for sets of non-conflicting executions and is reported as limited.
- **Same-id conflict and malformed input.** Every event type with a conflicting duplicate, a malformed field, an out-of-range quantity, a wrong instrument, and a missing sequence number must yield the codes and statuses of 2.6 and 2.8, never an exception and never a pass.
- **Counterexample reporting.** Every failed invariant, soundness violation or UNEXPLAINED gap is written with the minimal ledger or event sequence that reproduces it, the oracle's worlds that expose it, and the model's values. A run with zero counterexamples is reported as "none found in the declared state space", never as a proof.
- **Reproduction.** One command, fixed seeds, pinned Python version, printing the SHA-256 of the specification, the model and oracle sources, the vector files, the configuration and the bounds file.
- **Evidence artifacts to preserve.** The specification hash; source hashes; frozen vectors with derivations; the bounds file; full result JSON; counterexample list; interleaving traces; replay hashes; environment (Python version, OS); the reviewer's reproduction record.
- **What this could establish.** Over the declared finite state space and the world model W1 to W7: soundness of the sum rule against the oracle; the measured over-denial (G1, G2, G3); that I1a to I9 hold in the enumerated cases; that decisions are deterministic and idempotent; that no concurrency interleaving in the declared set over-reserves.
- **What it could not.** Truth or completeness of broker data; the world model's fit to any real broker; behavior outside the bounds; implementation correctness of anything other than this model; trading or financial performance; independence, unless a reviewer writes or re-derives the oracle without seeing the model.

---

## 6. Residual-risk register (explicit)

| Class | ID | Risk |
|---|---|---|
| Mathematical | M-1 | The sum rule and the soundness derivations (2.3, 2.4.1) are one-author hand derivations; soundness is relative to W1 to W7; tightness is measured, not asserted; G1, G2 and G3 over-denial is accepted (D01, widen-only principle) |
| Mathematical | M-2 | D19 is a specification candidate: its safety rests on the world model and on five preconditions; zero false permissions in a declared test space does not extend to excluded conditions |
| Mathematical | M-3 | The interval construction for unsequenced applied executions (2.2) is exact over the modeled inclusion choices only; it is a Revision 3 addition and has had no independent review |
| Environmental | E-1 | **A-12:** event delivery complete between snapshots. Snapshot freshness and decision age do not establish it. No formula covers its failure |
| Environmental | E-2 | **A-11:** a duplicate economic execution under a different id is uncovered; false permission is possible before the next reconciliation (V56): reductions after a duplicated buy, increases after a duplicated sell |
| Environmental | E-3 | A-2 (watermark semantics) and A-6 (W1 to W7) are hypotheses about the modeled environment; whether any real broker satisfies them is unvalidated |
| Environmental | E-4 | Wrong-side or wrong-instrument association of an applied execution (outside W6): visible only at the next snapshot |
| Environmental | E-5 | Broker-initiated position changes, and corporate actions, are outside the envelope and not represented |
| Implementation | I-1 | Same author for specification, planned model and planned oracle until an external author is found |
| Implementation | I-2 | Exhaustive-run feasibility is unknown until timed; any sampling must be declared in advance |
| Implementation | I-3 | The commit-time re-evaluation (2.9) must use the same pure function; a separate freshness path would be an unreviewed second decision |
| Operational | O-1 | **A-7:** the state keeper's ledger is trusted. D05, D23 and D24 are blockers for any broker contact or live-use claim |
| Operational | O-2 | A-5: the adapter must submit only with a live reservation token; the window before an unreserved order is detected is a residual risk |
| Operational | O-3 | A-4 and A-9: clock integrity |
| Scope | S-1 | G-04 (limit L), G-06 (protective intervention for the UNBOUNDED case) and G-07 (cancellation and override authority) remain open and outside v0.1 |

## 7. Stop/go recommendation (Deliverable E)

**Status: FROZEN FOR HOSTILE REVIEW.** D02 and D17 to D22 are recorded (3.2; D19 only as a conditional candidate). Every rule needed to build a small reference model and an independently structured oracle is stated: equations, worlds and their limits, statuses, lifecycle effects, the uncertainty inventory, events, the block matrix, reason codes, invariants, and 56 hand vectors.

**NO-GO for implementation.** The independent challenge of Revision 3 is not done; no claim has been executed or independently reviewed; the founder has not authorized the bounded executable reference model. The detail of the specification is not a reason to implement.

**Exact implementation boundary if later approved:** `exposure_model/` (types, log, accounting, authority, in-memory store) and a separately structured `exposure_oracle/`, pure Python standard library, deterministic scheduler, no broker adapter, no network, no clock or randomness inside pure functions, no change to `sentinel_core*`, parameter values (TTL, K, D_max, S_lim, limits) as test parameters only, and the enumeration bounds of 5.2 declared before any run.

## 8. Sequence and next action
1. Decisions D02 and D17 to D22 recorded (3.2).
2. Revision 3 frozen; its full-file SHA-256 is published with the review packet.
3. Targeted hostile-review packet for GPT and Gemini (independent reviews; blind oracle exercise first).
4. Challenge of the mathematical assumptions, oracle design, uncertainty inventory and counterexamples, before any code.
5. Only after that review: the founder decides whether to authorize the bounded executable reference model.
Nothing is implemented, and no broker, paper, live, strategy, P&L or crypto work is authorized, at any step above.

---

## 9. Counterexample register (permanent; nothing is deleted)

| ID | Counterexample or defect | Source | Resolved by |
|---|---|---|---|
| F-1 | Unconditional max rule undercounts (V08a: the max rule gives A_raw 45; the oracle minimum is 40) | Claude (addendum) | D14 sum rule |
| F-2 | I1a and I1b not exact inside a MISMATCH | Claude | Weakened to inequalities (2.5) |
| F-3 | Position >= 0 after authorization fails with busts | Claude | I8 |
| F-4 | AWAITING-BEHIND bounded by F_b is unsound | Claude | D18: UNBOUNDED |
| F-5 | Addendum contradictory about reductions during mismatch | Claude | D19 |
| F-6 | Revision counter does not cover time | Claude | D21, 2.9 |
| F-7 | Replay order not deterministic | Claude | D20, 2.6.3 |
| F-8 | Late execution after a terminal state | Claude | Pending item plus UNKNOWN (T22) |
| N-1 | Enumeration arithmetic: 20,736 is 12^4; the sum is 22,620 for 12 types; the list names 11 types; 16,104 for 11 | GPT, plus Claude | 5.2 (C-01) |
| N-2 | Applied execution without broker_seq under a watermark | Claude | 2.2, V51 |
| N-3 | Direction-unknown discrepancy not representable | Claude | 2.2, V53, V54 |
| N-4 | Event delivery completeness unstated | Claude | A-12, 2.3 limits |
| N-5 | Duplicate economic execution under a different id (false permission for reductions after a duplicated buy; for increases after a duplicated sell) | Claude | Documented as uncovered: A-11, V56 |
| N-6 | F_d(W) must be defined by event broker_seq | Claude | 2.2 |
| N-7 | Oracle comparison needed three checks | GPT, refined by Claude | 5.1 |
| N-8 | A later snapshot "covering" a GAP; effective freshness S_lim plus D_max | Claude | 2.6.3, 2.9 |
| N-9 | Unknown-side working order with known remaining quantity had no row | GPT requirement F | 2.7, 2.4.2 |
| N-10 | The two-interpretation formula for unsequenced executions is exact for one such execution only | Claude, while implementing requirement D | 2.2 (all inclusion choices; same result for n = 1) |
| N-11 | The claim that all bound gaps fall in G1 or G2 (and that C2 and C3 are "tight") is wrong: a known-side orphan is not credited against the opposite bound (G3). Found while preparing blind oracle cases | Claude | 2.3, 2.4 (widen-only principle), 2.4.1, 5.1 |

---

## Status ledger (what is what)
- **Defined:** the rules of section 2 with founder decisions D01, D03 to D16 applied (D02 and D17 to D22 pending founder approval).
- **Proposed:** the reconciliation resolutions RQ1 to RQ12, the Revision 3 additions, the oracle design, the enumeration bounds, the soundness derivations.
- **Unknown:** whether the world model fits any real broker; soundness and tightness results; actual counts; whether any invariant fails; the values of the parameters.
- **Executed or verified:** nothing in this assignment except integer arithmetic of counts (5.2). Findings F-1 to F-8 and the case table of 2.4.1 are hand-derived hypotheses by one author. Agreement among GPT, Gemini and Claude is not independent verification.

## Appendix A. H-LINK (NOT ADOPTED; historical record of a possible future refinement)
Idea: an orphan with broker_seq <= W, known side and quantity, whose signed value equals the discrepancy d, could be linked to d by a recorded link item, after which the pair would count once (a max instead of a sum for that pair). It would tighten V08b from 40 to 45 at the cost of link-evidence rules. The founder decision D01 does not adopt it into v0.1; it must not complicate v0.1. It may be revisited after the v0.1 results show how large the G1 gap actually is. The previously proposed unconditional max rule remains rejected as unsound (F-1) and appears only as a test-only variant to demonstrate the failure.
