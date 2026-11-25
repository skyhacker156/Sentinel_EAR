# Sentinel Exposure Accounting Reference Model v0.1 Specification

**SPECIFICATION ONLY / NOT IMPLEMENTED / NOT VERIFIED**

Date: 2026-11-23. **Revision 3.1** (supersedes Revision 3, SHA-256 9a2c3be747fa9acbe4513e77f4122712f1970aa17109beb52acffbe051702b0a). Revision 3.1 incorporates the accepted outcomes of the GPT (two passes) and Gemini hostile reviews of Revision 3: candidates R31-01 to R31-11, gaps G-A to G-E, and founder decisions D26 and D27 (2026-11-23). Revision 3's own header follows as history. Date: 2026-11-22. **Revision 3.** Incorporates changes C-01 to C-15 of the Rev 2 reconciliation package and the six additional requirements (A to F) of GPT's Rev 3 preparation dispatch into Revision 2 (SHA-256 7d9573e42f7d8d0fe502b6bdc936b0a3933b536c838f7272de5e500802346e2c). From: Claude (ARBITER / Specification Lead).
**Revision 3.1 is FROZEN for targeted final review. Its SHA-256 is computed by program from the delivered bytes, published with the delivery, and not embedded in this file (a file cannot contain its own hash). Freezing is not authorization to implement the reference model. Implementation remains NO-GO.**
**History: Revision 3 was frozen for hostile review. Its SHA-256 was published in the review packet and in the chat, and is not embedded in this file (a file cannot contain its own hash). The pre-freeze Revision 3 draft had hash 0eb476236b6510f2a2508fc401a8469310d9d4501362123c8298a2c282e22230; the frozen Revision 3 superseded it (decisions recorded; G3 added). Freezing is not authorization to implement the reference model.**
Status of every rule: **[R]** REQUIRED or **[H]** HYPOTHESIS; unresolved decisions are marked **OPEN**. Founder decisions already applied: D01 approved (sum rule); D14 approved (addendum 5.2 and example 7 superseded); D10 amended; D03 to D09, D11 to D13, D15, D16 approved as proposed. **Founder dispatch of 2026-11-22, item 1 ("Resolve D02 and D17-D22 explicitly, preserving the conditional status of D19"), is recorded in 3.2 as approval of the positions on which Claude and GPT agree: D02 with additions, D17 with modification, D18, D20 with limits, D21 with commit-time revalidation, D22. D19 is approved only as a conditional specification candidate and never as an established safety property.** This is Claude's reading of that dispatch and is open to founder correction. Founder approval is not technical verification; GPT's dispositions are review positions, not approval. D23 to D25 remain deferred and OPEN. **Founder decisions of 2026-11-23: D26 (a CORRECT that changes side, order association or instrument: Option A, structural evidence failure and UNBOUNDED) and D27 (the five-requirement correction contract) are applied in 2.2, 2.4.2, 2.6 and 3.2.1, and drafting of this revision was authorized; these are Claude's readings of the founder's messages, open to correction, and are not verification.** Nothing here has been executed.
Untouched: frozen v0.3, v0.3.1, v0.3.2, candidate v0.3.3 and their verification record. This model does not describe, and is not enforced by, the existing authority core.
Crypto observation, crypto-specific accounting, brokers, paper and live orders, strategy or P&L experiments, and G-04 to G-07 remain out of scope and appear nowhere in this specification except as named dependencies.

### Revision 3.1 change log (exact sections)
| Item | Change | Where |
|---|---|---|
| R31-01' | W1-T and W1-F are the only snapshot-world classes the model admits, exhaustive only within W1 to W7 and the envelope; not a taxonomy of real snapshot failures | 2.3 (limits) |
| R31-02 | Worked G3 examples from blind cases B2 and B5 | 2.4.1 |
| R31-03' | A-12 failure can invalidate both bounds and reduction permission in every status, including RECONCILED; an assumptions-in-force notice that is a label, not evidence | 2.3 (limits), I2, 2.9, 2.11 |
| R31-04' | Correction and bust rows distinguish F_d from F_d(W); stale, incomplete and identity-changing corrections | 2.2, 2.4.2, E13, T21 |
| R31-05' | More than one unsequenced applied execution: static-grid note and vector V57 with all five D19 preconditions stated | 5.2, 2.10 |
| R31-06A | Evaluation is internal and non-authorizing; the only public operation returns a committed reservation or a refusal; diagnostics never returned | 2.9, 2.6.1 (T02, T03), 4 |
| R31-06B (G-A) | Reservation bound to a canonical proposal hash; same proposal_id with a different hash is a CONFLICT; single consumption with exact payload equality; accounting consequence of an unknown submission outcome; adapter and G-07 boundary recorded as OPEN | 2.9, 2.2, 2.6.1 (T04), V58 |
| R31-07' | Snapshot replacement rule: strictly greater accepted watermark, contiguity, recomputation, only the prior discrepancy item replaced | 2.4, 2.6.2, V62 |
| R31-08 | Oracle domain: integer unreported fills, every placement, full Cartesian product | 5.1, 5.2 |
| R31-09' | Pre-enumeration prerequisites: validity predicate and exclusion ledger, test-obligation matrix, separate spaces, oracle-domain report, adversarial authority tests | 5.7 |
| R31-10 | Five separate claim levels and a reporting format | 5.5, status ledger |
| R31-11 | T22 re-reservation plus held execution labelled a possible over-denial | 2.6.1 |
| G-C, D26 | CORRECT that changes side, order association or instrument: Option A | 2.2, 2.4.1, 2.4.2, 2.6 (E13), 2.6.1 (T21), 2.8, 3.2.1, V59 |
| G-D, D27 | Correction contract: reference, completeness, prior version, replacement quantity, no silent application | 2.2, 2.4.2, 2.6 (E13), 2.11 (A-14), 3.2.1, V49, V60, V61 |
| G-E | CAS scenarios declare steps, precedence and admissible interleavings; counts are generated, not asserted | 5.4, 5.7 |
| Registers | N-12 to N-18; residual risks M-4, O-4, V-1; status ledger corrected (D02, D17 to D22 recorded) | 6, 9, status ledger |
| Unchanged | The equations of 2.4, the sum rule (D01), the world model W1 to W7 (apart from the added limit statements), the statuses, D19 (still a conditional candidate with its rollback), D14 to D22 | |

Reviewer errors found in the reviews of Revision 3 (Gemini's B2 A_raw, B5 gap class and n = 2 signs) are recorded in the adjudication documents, not in this specification. Nothing in Revision 3.1 has been executed. G-A to G-E are labels of gaps found in review, not the program gates G-01 to G-07.

### Revision 3 change log (exact sections)
| Item | Change | Where |
|---|---|---|
| C-01 | Event-sequence enumeration uses the 11 named event types; sum for lengths 1 to 4 is 16,104; generated, valid, excluded, evaluated and deduplicated counts kept separate | 5.2 |
| C-02 | Coverage-report columns: false permission, false denial, unbounded, structural, violations, disagreements, exclusions, generation bias, duplicates, resources | 5.2, 5.6 |
| C-03 | Applied execution without broker_seq: both watermark interpretations enumerated | 2.2, 2.6.2, V51 |
| C-04 | F_d(W) defined over events by their own broker_seq | 2.2, 2.6.2 |
| C-05 | A later snapshot never clears a GAP | 2.6.3, 2.6.2, V47, V48 |
| C-06 | Input contract for snapshot quantity and discrepancy magnitude | 2.2, 2.6.2, V53, V54 |
| C-07 | A-2 restated as an input contract; **A-12** added; every assumption classified | 2.11, 2.3 (limits) |
| C-08 | Freshness at commit (see requirement E) | 2.9, I5 |
| C-09 | Normative uncertainty inventory and zero-assertion test | 2.4.2, 2.4 |
| C-10 | D19 preconditions added to I2 | 2.5 (I2) |
| C-11 | Oracle renamed "independently structured reference oracle"; safeguards; three comparisons | 5.1 |
| C-12 | Vectors V46 to V56 | 2.10 |
| C-13 | D20 limits listed | 2.6.3 |
| C-14 | State-keeper trust limitation in the executive verdict | 1, 2.8 |
| C-15 | Decision register updated | 3.1, 3.2 |
| A | A-12 limitation: snapshot freshness and decision age do not establish event-delivery completeness | 1, 2.3 (limits), 2.11, 3.2 |
| B | "Idempotency by event ID does not establish economic-execution uniqueness"; duplicate economic executions under different ids documented as uncovered | 2.6.3, I6, 2.11 (A-11), V56 |
| C | Zero false permissions in the declared oracle test space cannot establish safety against conditions excluded from W1 to W7 | I2, 3.2 (D19), 5.2 |
| D | Interval construction for unsequenced applied executions (generalized from two interpretations to all subsets; identical when there is one such execution) | 2.2, V51 |
| E | Snapshot age re-checked at commit; S_lim not extended by D_max | 2.9, I5, V44 |
| F | Known remaining quantity with unknown order side affects both bounds; unknown quantity remains UNBOUNDED | 2.7, 2.4.2, 2.3 (W3) |
| Enumeration | 11 types; 16,104; no twelfth event invented | 5.2 |
| Registers | Decision register; counterexample register; residual-risk register | 3, after 8, 6 |
| Freeze | Decisions recorded; **gap class G3 and the widen-only principle added** after preparing the blind oracle cases (N-11); frozen for hostile review | header, 2.3, 2.4, 2.4.1, 3, 5.1, 7, 9 |

### Revision 2 change log (retained as history)
1. **Addendum Revision 1 integrated** (evidence model 2.8, snapshot rules and statuses 2.6.2, lifecycle T01 to T22 with accounting effects 2.6.1, master minimum 2.12) with a provision-by-provision disposition (incorporated, modified, deferred, excluded) in 2.13.
2. **K1/K2/K3 formally mapped** to F_min, F_max, B, S, U_unknown, A_unknown (2.4.1). The seven required reconciliation items are answered there.
3. **Conflicts between the addendum and the model found and resolved or registered** (2.14, RQ1 to RQ12). Five findings (F-4 to F-8, below) change behavior.
4. **Invariants reconciled** into one set I1a to I9 (2.5). Each has the seven required fields. The addendum's unconditional I4 is not retained.
5. **Vectors** extended to V01 to V45 with position bounds, U, A_raw, A, decisions and reason codes (2.10).
6. **Enumeration** recomputed for the seven position statuses: 612,500 ledger states (5.2).
7. **Plan and verification** now include the event ledger representation, canonical serialization, replay and idempotency tests (4, 5.6).
Unchanged from Revision 1: the sum rule (2.4), the world model W1 to W7 (2.3), findings F-1 to F-3.

---

## 1. Executive verdict

**Revision 3 additions (limitations that must be read first).**
- **Trust in the state keeper (A-7).** The model establishes properties of the ledger it *receives*. It cannot establish that the ledger is truthful and complete if the state keeper is compromised or wrong. D23 (key custody) and D24 (independent evidence) block any broker contact and any live-use claim.
- **A-12 (environmental hypothesis).** Snapshot freshness (D07) and decision age (D21) bound how *old* the evidence is. They do **not** establish that event delivery was complete. The model must not be read as protecting against undelivered events merely because a snapshot is fresh.
- **Economic-execution uniqueness.** Idempotency by event ID does not establish economic-execution uniqueness (2.6.3). A duplicate economic execution under a different id is an uncovered environmental failure and may create false permission until the next reconciliation.
- **D19 is a specification candidate, conditional on the world model.** Zero false permissions in the declared oracle test space cannot establish safety against conditions excluded from W1 to W7.
- **Same-author status.** Specification, planned model and planned oracle share one author until an external author is found.

**Revision 3.1 additions (read with the limitations above).**
- **Authority interface.** An evaluation is internal and is never permission. The only artifact whose existence means authority is a *committed reservation*, created by a successful atomic commit and bound to a canonical hash of the exact proposal (2.9). The diagnostic values (F_min, F_max, B, S, U, A_raw, A) are never returned to proposers or adapters.
- **Corrections.** A CORRECT replaces a named prior version of an execution (D27). A CORRECT that changes side, order association or instrument is a structural failure and the affected exposure is UNBOUNDED (D26). Cost: availability.
- **Boundary of this model.** It specifies the accounting result of an unknown submission outcome. The broker retry protocol, client order ids, non-forgeable submission capabilities and recovery after a lost acknowledgement are adapter and G-07 matters and are not designed here (2.9, OPEN).
- **What the reviews of Revision 3 did and did not show.** Two hostile reviewers hand-derived selected vectors and found no arithmetic false permission inside W1 to W7. That is a second hand derivation, not verification; the oracle, enumeration and independent reproduction have not been executed.

**The addendum and the model can form one coherent, testable specification, but not by mechanical merge. Reconciliation found five conflicts that change authority behavior. Each has a recommended default and needs your approval (D17 to D22).**

1. **F-4 (RQ7). The addendum's treatment of a snapshot that is ahead of our events is unsound under the world model.** Its item ledger uses the broker position as a bound in AWAITING-BEHIND. But if the snapshot is false (W1-F) and executions up to its watermark have not arrived, nothing bounds the true position. Resolution: AWAITING-BEHIND, like GAP, is UNBOUNDED. Cost: reductions are UNRESOLVED during the wait. Decision D18.
2. **F-5 (RQ6). The addendum contradicts itself on reductions during a position mismatch.** Its consistency check lists a position-versus-snapshot disagreement as INCONSISTENT, and section 4 denies reductions on any evidence failure, yet its item ledger bounds a MISMATCH and the sum rule (D01) assumes the bound is used. Resolution: a *quantified* mismatch (known discrepancy d, contiguous events) blocks increases but not reductions within A; *structural* conflicts (same id with different content, cumulative-quantity conflicts, overfills) block both. Decision D19.
3. **F-6 (RQ10). The revision counter does not cover the passage of time.** A snapshot fresh at evaluation can be stale at commit with no ledger change. Resolution: the decision records its as_of time and the commit rejects a decision older than a maximum age. Decision D21 (the value stays a parameter).
4. **F-7 (RQ9). "Order by receipt time when sequence numbers are absent" is not deterministic on replay unless the receipt order is itself recorded.** Resolution: the canonical order is the append position in the hash-chained log; broker sequence numbers are used for gaps and watermark comparison only. Decision D20.
5. **F-8. A late execution after a terminal state:** the addendum says apply it to the position and set the order UNKNOWN (IB3); this model holds it as a pending item until reconciliation. There is no decision-level difference, because the conflict blocks reductions either way. Registered, no approval needed (RQ8).

Two further reconciliations concern wording, not behavior:
- **Equation notation (D17).** Your dispatch restates the equations with U_unknown and A_unknown. They are kept as notation with both identically zero. A separate additive term would count the same uncertainty twice.
- **"The same quantity cannot be counted twice."** This holds at the level of item identity (invariant I6, universal in the model). It does not hold across *different* items that might be the same real-world quantity, such as a discrepancy and an orphan with an unproven relationship. D01 requires counting both. The over-denial this causes is the measured gap G1/G2, not a defect.

**What this specification establishes if its tests pass:** the rules are internally consistent and sound relative to the stated world model, over a declared finite state space. **What it cannot establish:** that broker data is truthful, that an implementation enforces the model, that the world model is complete, that a previously authorized reduction stays safe if the world model is violated, or anything about trading performance.

**Stop/go (section 7):** REVISION 3.1 FROZEN FOR TARGETED FINAL REVIEW. **NO-GO for implementation** until the targeted final review of Revision 3.1 and the pre-enumeration prerequisites (5.7) are complete and the founder decides whether to authorize the bounded executable reference model.

---

## 2. Normative specification (Deliverable A)

### 2.1 Scope and exclusions [R]

In scope: long-only, one instrument, one venue, one account, regular session, whole units, buy and sell orders, no modify/replace orders (cancel and new proposal only).
Excluded: short selling, options, futures, margin, leverage, corporate actions, symbol changes, rolls, broker adapter, any live or paper connection, G-04 risk limits (the exposure limit L is a test parameter only), G-05 market data, G-06 protective intervention, G-07 authorization design.
Quantities: integers in [1, Q_MAX] for orders and executions; Q_MAX is a configuration value (decision D12). Quantities outside range, non-integer, boolean or non-numeric are malformed.

Beyond the approved envelope, and therefore excluded or deferred although present in the addendum: full instrument-master governance, multiplier, notional and price-band logic, corporate-action flags, key-management mechanics, human override, authority to cancel (2.13, RQ12).

### 2.2 State definitions [R]

**Observed evidence (inputs, never recomputed):**
- Order event: event_id, order_id, type, broker_seq (optional), cum_qty (required on every terminal event), raw_hash, received_at (independent clock).
- Execution: exec_id, order_id or null, instrument, side or null, qty or null, broker_seq (optional), kind in {NEW, CORRECT, BUST}, ref_exec_id for CORRECT/BUST, raw_hash, received_at. **A CORRECT additionally carries, in full: the identity it asserts (instrument, side, order_id), prior_version and prior_qty (the exact version of the referenced execution it replaces), and qty (the replacement quantity) (D27).**
- Snapshot: snapshot_id, instrument, qty, watermark W (the broker sequence number it is current through; optional), raw_hash, received_at. **Input contract (C-06):** qty is a signed integer. In this long-only envelope a negative or out-of-range qty is an envelope violation: structural Consistency failure, UNRESOLVED (V54). A source that reports only the *magnitude* of a discrepancy and not its direction is represented by d_plus = d_minus = the magnitude; a source that gives neither is malformed.
- Proposal: proposal_id, side, qty, instrument. The configured account identifier (one fixed account in v0.1, 2.1) is part of the proposal's identity: **proposal_hash** = SHA-256 of the canonical serialization (2.6.3) of (instrument, account, side, qty, proposal_id) (G-A, 2.9).
- Master version id and content hash in force (opaque inputs to v0.1, 2.12).
- Internal records: reservation commits, with the evaluation that produced them.

**Event log.** The ledger's source of truth is an append-only, hash-chained sequence of every accepted evidence item, in append order (the *log position*). Replay is a pure fold over the log in log-position order (2.6.3). Raw payloads and their hashes are retained.

**Execution versions and corrections (D26, D27) [R].** Each applied execution has a current *version*: version 0 is the NEW report and each applied CORRECT creates the next version. A version is (version number, qty, side, order_id, instrument). A CORRECT is applied to the current version only if every check below passes; failing (1), (2) or (3) leaves it unapplied and the band UNBOUNDED, failing (4) or the range check of (5) is a structural conflict; all outcomes block, none narrows.
1. *Reference.* ref_exec_id names an applied execution; otherwise the CORRECT is held pending with its effect unknown, T2-U (E13, V31, V55).
2. *Completeness.* The CORRECT carries instrument, side, order_id, prior_version, prior_qty and qty, each of the right type; a CORRECT missing or malforming any of them is not applied to any version and is treated as an orphan of unknown quantity, T2-U (2.6, V61). Nothing is silently applied to the current version.
3. *Identity.* instrument, side and order_id equal the referenced execution's current values; otherwise **D26** applies (below).
4. *Prior version.* prior_version equals the execution's current version number and prior_qty equals its current qty; otherwise structural conflict (V49). A resent correction under a new event id therefore conflicts instead of being applied twice.
5. *Replacement.* qty is the replacement value, not an adjustment: the effect on F_d and net_cum is qty - prior_qty, at the CORRECT's own broker_seq, and the version number rises by one. net_cum must stay in [0, order qty] and must not exceed the broker's cumulative quantity (E13), else structural conflict.
**D26 (identity-changing correction, Option A).** A CORRECT may change only the quantity of an execution. A CORRECT whose instrument, side or order association differs from the referenced execution's current values is a structural evidence failure and is **not applied**. The CORRECT and its referenced execution are held as a pending item whose effect is unknown: the band is UNBOUNDED (T2-U), increases and reductions are blocked (UNRESOLVED / DENY), and no quantity is transferred between orders or instruments. The item leaves only by the two transitions of 2.4.1 item 6 (application on an authoritative broker response that establishes the corrected execution's instrument, side, order association and quantity, or authoritative dismissal). A CORRECT naming a non-canonical instrument is also quarantined under D13 (2.12). Cost: availability; a legitimate identity correction blocks until the broker resolves it. Options B (reversal plus replacement) and C (enumerating both interpretations) are not adopted in v0.1.

**Derived state (recomputable from the log, model version and configuration):**
- **net_cum(order)** = the sum, over that order's applied NEW executions, of each execution's current-version quantity (replaced by each applied CORRECT, D27), with a BUST removing its execution's current quantity. **net_cum_at(order, s)** is the same using only executions with broker_seq <= s. The lifecycle history is a separate append-only record, never rewritten.
- **R(order)** = qty - net_cum for orders whose lifecycle state is in WORKING = {AUTHORIZED, SUBMITTED, ACKNOWLEDGED, PARTIALLY_FILLED, CANCEL_PENDING, UNKNOWN}; R = 0 for PROPOSED, DENIED, FILLED, CANCELED, REJECTED, EXPIRED. A bust does not resurrect a terminal order.
- **F_d** = position reconstructed from applied executions (buy +q, sell -q). **F_d(W)** = the signed sum of applied execution *events* whose own broker_seq <= W (C-04). A CORRECT or BUST is an event with its own broker_seq: a correction numbered above W is not in F_d(W) even if it refers to an execution numbered at or below W, so a late correction does not create a spurious discrepancy. **Unsequenced applied executions (C-03, requirement D):** an applied execution with no broker_seq has unknown timing relative to W. Let the unsequenced applied executions have signed quantities s_1..s_n and let F_base be the signed sum of the sequenced applied executions with broker_seq <= W. Each unsequenced execution is independently either inside or outside F_d(W), so d = F_b - (F_base + sum of the included s_j) takes values d_k over all 2^n inclusion choices. Then **d_plus = max(0, max_k d_k)** and **d_minus = max(0, -min_k d_k)**. For n = 1 this is exactly d_plus = max(0, d_1, d_2) and d_minus = max(0, -d_1, -d_2) with d_1, d_2 the discrepancy under the two interpretations. For n > 1 the extremes are reached by including all unsequenced sells or all unsequenced buys, so the computation is linear: max d = F_b - F_base - (sum of the negative s_j), min d = F_b - F_base - (sum of the positive s_j). The status is MISMATCH if any d_k is not 0. **F_b** = quantity in the latest accepted snapshot, at its watermark W. d = F_b - F_d(W); d_plus = max(0, d); d_minus = max(0, -d).
- **B** = sum of R over working buy orders. **S** = sum of R over working sell orders.
- **Position status** (exactly one of seven, table in 2.6.2): RECONCILED, AWAITING, MISMATCH, AWAITING-BEHIND, AWAITING-UNVERIFIED, GAP, UNKNOWN. Position MISMATCH and the integrity failure MISMATCH are different things; reason codes are always written with their property prefix (2.8).
- **Position-band items**, each counted once by identity:
  - the discrepancy item d (only in MISMATCH);
  - orphan items, keyed by event_id, classified once under 2.3 as T1, T1u or T2: Q3_buy (known buy), Q3_sell (known sell), Q3_unk (side unknown, or ambiguous, with parseable quantity);
  - pending items: events awaiting a prerequisite (an out-of-order execution, a CORRECT or BUST naming an unknown original). A pending item whose effect is known is treated as an orphan; one whose effect is unknown is T2-U.
- **BOUNDED** is true iff the status is RECONCILED, AWAITING or MISMATCH, no T2-U item exists, and no structural evidence failure exists (2.8). Otherwise **UNBOUNDED**.

### 2.3 World model (D02 clarification) [H]

**These are hypotheses about the modeled broker environment, not established facts about any real broker or all brokers.** They are the explicitly bounded assumptions of the challenge baseline. The formulas (2.4) and the oracle (5.1) are both defined against exactly this section, and no other.

**Objects.** W = watermark of the latest accepted snapshot. P_W = the true position at W. P = the true current position. An execution is *applied* (in the ledger, so in F_d) or *unapplied*. *Occurred* means it really took place at the broker. d = F_b - F_d(W), so F_d + d = F_b + (F_d - F_d(W)).

**Classification of unapplied items (each item is classified once; the treatments are not interchangeable).**

| Treatment | Item | Did it occur? | Effect on position in a world | Formula term | What the oracle enumerates |
|---|---|---|---|---|---|
| T1 | **Known execution that occurred but cannot be associated with an order:** well-formed execution report, known side and quantity, order unknown or unassociable. | **Yes, in every world** (W2). An execution report asserts occurrence; a false report is outside the model. | buy +q, sell -q | Q3_buy, Q3_sell | occurred only; timing per T3/T4 |
| T1u | As T1 but side unknown. | Yes, in every world. | +q or -q, chosen by the world (W3) | Q3_unk | occurred only; side buy or sell; timing per T3/T4 |
| T2 | **Ambiguous event that may not represent an execution:** unclassifiable type, or malformed with a parseable quantity. | **Unknown: the world decides.** | none if it did not occur; otherwise as T1u | Q3_unk | three options: did not occur, occurred as buy, occurred as sell; timing per T3/T4 when occurred |
| T2-U | Ambiguous event with unparseable or unknown quantity; or unknown instrument (D13). | Unknown | unbounded | none: band UNBOUNDED (UNRESOLVED for reductions, DENY for increases) | not enumerated; the oracle reports UNBOUNDED |

**Timing, for any occurred T1, T1u or T2 item:**

| Treatment | Timing | Meaning |
|---|---|---|
| T3 | **Already reflected in the snapshot** | broker_seq <= W: if the snapshot is truthful, F_b already contains it. |
| T4 | **Not reflected in the snapshot** | broker_seq > W: F_b does not contain it, so it adds to the position after W. |
| (unknown) | No usable broker_seq | The oracle enumerates both T3 and T4. |

**Assumptions.**
- **W1 (snapshot; identifies the complete true position at W, not a baseline).** Exactly one of two world classes holds when the status is RECONCILED or MISMATCH:
  - **W1-T, snapshot truthful:** P_W = F_b. Every occurred execution with broker_seq <= W, applied or not, is already inside F_b. Any part of d not explained by evidenced items is attributed to executions the broker has and we lack evidence for (net effect d, all with broker_seq <= W).
  - **W1-F, snapshot false:** P_W = F_d(W) + signed sum of occurred unapplied executions with broker_seq <= W (d is not used).
  A failure of both our reconstruction and the snapshot without any evidence is a common-mode failure and out of scope. W1 is not "a baseline to which orphans are then added": orphans are added after W in W1-T (T4 only) and in full in W1-F, as the world values below state.
- **W2 (occurrence).** T1 and T1u items occurred. T2 items may or may not have occurred. No other unapplied executions are modeled, with two exceptions: unreported fills of working orders (W4), and, under W1-T only, the executions implied by d (all with broker_seq <= W). No unevidenced execution after W is modeled (a missing sequence number is a GAP and makes the band UNBOUNDED).
- **W3 (side).** An unknown side (T1u, occurred T2) is chosen by the world, whichever way is worse for the bound being tested. The same holds for a working order of unknown side with a known remaining quantity R (requirement F): the world chooses the side per bound, so the order contributes R to both B and S (2.7, 2.4.2). An unknown quantity is not bounded by any world: UNBOUNDED.
- **W4 (unreported fills).** Each working order, including UNKNOWN ones, may have filled x in [0, R] without a report, placed before or after W, and may fill any amount of the rest in future.
- **W5 (cancel-pending).** A CANCEL_PENDING order may still fill any amount in [0, R] until a confirmation with a consistent cum_qty is accepted.
- **W6 (applied events).** Applied events are true. A later BUST or CORRECT is a new event, not a world.
- **W7 (current position).** P = P_W + signed applied executions with broker_seq > W + signed occurred unapplied executions placed after W (+ unreported fills per W4).

**World values.**
```
W1-T :  P = F_d + d + sum( signed occurred orphan items with timing T4 ) + unreported fills placed after W
W1-F :  P = F_d      + sum( signed occurred orphan items, any timing )    + unreported fills (any placement)
U_w   = P + sum( remaining buy quantity R - x over working buys )
A_w   = P - sum( remaining sell quantity R - x over working sells )
```
A world is enumerated whenever its choices (occurrence, side, timing, x) respect the evidence: timing is fixed when broker_seq is known, enumerated when it is not.

**Soundness of the sum rule against these worlds (hand derivation, not executed).**
- Upper side. In W1-T, U_w <= F_d + d + (buy items) + (unknown-side items as buys) + B: unreported buy fills move quantity from remaining to position and cancel in U_w. In W1-F, U_w <= F_d + (buy items) + (unknown-side items as buys) + B. Since d <= d_plus, and the W1-F bound has no d term, both are <= F_d + d_plus + Q3_buy + Q3_unk + B = U.
- Lower side, symmetric: A_w >= F_d - d_minus - Q3_sell - Q3_unk - S = A_raw.
- **Where the sum rule is deliberately not tight (D01; not weakened for availability):** G1, a T3 item (already in F_b) is counted in d and again in Q3; G2, an unreported fill placed at or before W is counted in d and again in R. **G3, a known-side orphan (T1) that occurred in every world is not credited against the opposite bound** (a sell orphan of q does not lower F_max; a buy orphan does not raise F_min), by the widen-only principle of 2.4; the oracle's maximum or minimum over worlds is tighter by q on that side. Outside G1, G2 and G3 the bounds are expected to coincide with the oracle. *Found in preparing the blind cases (N-11): the earlier statement that gaps fall only in G1 and G2 was wrong.*

**Limits of this world model [R to state; requirement A, C].**
- W1 to W7 and A-2 are hypotheses about the *modeled* environment. A-2 is an **input contract of the reference model**: events and snapshots supplied to it are assumed to carry one monotone broker_seq per account, and a snapshot watermark W is assumed to mean the snapshot contains exactly the executions with broker_seq <= W. That a real broker's data satisfies this contract is **not established** by this specification and must be shown separately before any broker contact.
- **Scope of the W1 classes (R31-01').** W1-T and W1-F are the only snapshot-world classes this model admits, and they are exhaustive only within W1 to W7 and the stated instrument, account, venue, session and quantity envelope. This is not a claim that every real broker snapshot failure, position change or evidence failure belongs to either class: an external adjustment, a corporate action, a transfer, an incorrect instrument mapping or a compromised reporting source lies outside both and is handled, if at all, by the structural-failure and UNBOUNDED rules, not by a third world.
- W2 and W6 depend on **A-12**: event delivery is complete between snapshots, except for unreported fills of known working orders (W4). **Snapshot freshness and decision age do not establish A-12.** A fresh snapshot with d = 0 shows only that the broker position equalled the ledger position at W. A dropped bust, a dropped execution for an unknown order, an undelivered correction, a wrong-side association or a duplicate economic execution after W is not represented by any world, and no formula covers it. It can be detected afterwards, at a later snapshot, as a discrepancy. This is detection after the fact, not protection. **A failure of A-12 can invalidate both bounds and reduction permission in every position status, including RECONCILED (R31-03'); D19 covers only the quantified discrepancy d, not missing, undelivered, duplicated, misattributed or otherwise unrepresented executions. A later accepted snapshot can reveal such a failure; it cannot make A-12 true for the interval before it.**
- No statement in this specification that a bound is "sound" extends beyond W1 to W7. A result of zero false permissions in a test space is a result about that space and those worlds.

**What this resolves for D02.** (1) A known occurred execution that cannot be associated (T1) is treated as having occurred in every world. (2) An ambiguous event (T2) is a different class: its occurrence is a choice of the world. (3) An execution already reflected in the snapshot (T3) sits inside P_W in W1-T and is added in W1-F. (4) An execution not reflected (T4) is added on top of the snapshot in both classes. The formula adds every orphan to the band regardless of timing, and the oracle enumerates exactly the worlds above, so they describe the same set of possibilities.

### 2.4 Formal equations [R]. Section 2.4 is the sole normative calculation.

```
F_max = F_d + d_plus + Q3_buy + Q3_unk
F_min = F_d - d_minus - Q3_sell - Q3_unk

U      = F_max + B + U_unknown      (U_unknown is identically 0, D17)
A_raw  = F_min - S - A_unknown      (A_unknown is identically 0, D17)
A      = max(0, A_raw)
OVER_RESERVED  iff  A_raw < 0           (A_raw preserved for diagnostics)
```
- **Widen-only principle [R].** An unreconciled item (orphan, pending item, discrepancy, unknown order) may widen a bound; it may never narrow one. A known-side orphan therefore moves only the bound its side widens (Q3_buy raises F_max, Q3_sell lowers F_min) and takes **no credit** against the opposite bound, even though every world in which it occurred would allow it (gap G3). Only *application* (evidence that moves the item into F_d, 2.4.1 item 6) can end an overlap or take credit. **A bound may narrow only by evidence that replaces the item** (R31-07'): application of an execution to F_d, authoritative dismissal of an item (2.4.1 item 6), or a newer accepted snapshot that replaces the discrepancy item d under the rule of 2.6.2. Each such replacement is one revision step. No timeout, belief, strategy output or state-keeper assertion qualifies, and a snapshot replacement dismisses no other item.
- **Zero-assertion test (C-09).** The model carries a test that U_unknown and A_unknown are identically zero and that every item class of the inventory (2.4.2) has exactly one home. A nonzero value in v0.1 is a specification violation.
- U_unknown and A_unknown from the dispatch are **identically 0 by construction (D17, 2.4.1)**. Their job is done by (a) the band items above and (b) counting UNKNOWN working orders in B or S at full R. Keeping separate additive U_unknown/A_unknown terms is what would permit double counting, so they are removed. This is a deliberate deviation from the starting hypothesis, flagged here, not silent.
- Once-only mechanism: every uncertain quantity has one identity (order_id for order reservations, snapshot_id for the discrepancy, event_id for orphans) and appears in exactly one term. An applied execution is in F_d and never also in an orphan or in R. The discrepancy d is recomputed from F_d(W) at each comparison, so applying an execution shrinks it automatically and cannot be counted twice.
- Sum rule [R, D01 approved]: discrepancy and unlinked orphan quantities are added conservatively, never max'ed. No linking of an orphan to the discrepancy exists in v0.1 (Appendix A records the idea as a possible future refinement only).
- Decisions:
  - Increase Q: ALLOW iff BOUNDED, no block (2.7), and U + Q <= L. L is a test parameter (G-04 dependency).
  - Reduction Q (sell): ALLOW iff BOUNDED, no structural evidence failure (2.8), and Q <= A. A reduction larger than A is DENIED, never clipped (clipping alters the authorized order). In long-only scope, selling beyond A risks going short and is also treated as an increase-class violation.
  - **UNRESOLVED** when the quantity cannot be computed (UNBOUNDED or evidence failure). **DENY** when it can be computed and a constraint or block applies. Neither authorizes anything.
  - Proposals with side not in {buy, sell}, quantity out of range, or instrument != the model instrument are DENY with a malformed or foreign-instrument code.
  - Proposed orders do not need to match any exposure-increasing/decreasing classification beyond side: buy = increase, sell = reduction.

### 2.4.1 Reconciliation of the addendum item ledger with the six quantities [R]

Section 2.4 is the single normative source. The dispatch's notation `U = F_max + B + U_unknown` and `A_raw = F_min - S - A_unknown` is retained with **U_unknown and A_unknown identically zero (D17)**: all uncertainty is already inside F_max and F_min, and a separate nonnegative additive term would count it twice. A nonzero value in v0.1 is a specification violation.

**Formal mapping (the addendum's K1/K2/K3 is not copied; it is mapped):**

| Addendum item | What it is | Model quantity and rule |
|---|---|---|
| K1 position F_d | Applied executions | F_d, the centre of both bounds |
| K1 broker position F_b and MISMATCH delta | Snapshot at W versus F_d(W) | d_plus raises F_max; d_minus lowers F_min. Defined only in MISMATCH with contiguous events. In AWAITING-BEHIND, AWAITING-UNVERIFIED, GAP, UNKNOWN the band is UNBOUNDED (changed from the addendum, which used F_b as a bound for AWAITING-BEHIND: F-4, D18). |
| K2 reservations, buy side | R of working buys, including UNKNOWN and AUTHORIZED | B |
| K2 reservations, sell side | R of working sells, including UNKNOWN and AUTHORIZED | S |
| K3 orphan quantity Q3 | Unapplied, unmatched execution or event | Q3_buy raises F_max; Q3_sell lowers F_min; Q3_unk does both. The addendum used the absolute quantity on both bounds; the side-aware form is a sound refinement (hand-derived, flagged for challenge, RQ1). Unknown quantity or unknown instrument: UNBOUNDED. |
| U_unknown, A_unknown | none | identically 0 (D17) |

**Answers to the seven required items.**

1. **How position discrepancies enter the bounds.** d = F_b - F_d(W) is computed only at the snapshot's own watermark with contiguous events. It widens F_max by d_plus and F_min by d_minus. It is one item, identified by snapshot_id, and is recomputed at every comparison, so applying an execution shrinks it automatically.
2. **How orphans and unresolved executions enter.** Each is one item, keyed by event_id, in exactly one of Q3_buy, Q3_sell, Q3_unk, or it makes the band UNBOUNDED. It is added to the discrepancy, never max'ed against it (D01).
3. **When an orphan is additional uncertainty and when it is an explanation already represented in the discrepancy.** In v0.1 the relationship is never inferred: an unapplied orphan is always treated as additional uncertainty, even if it could explain d. The relationship becomes established only by *application*: once the orphan is matched and applied it is in F_d, and d recomputes without it. A recorded link between an orphan and d (H-LINK) is not adopted (D01, Appendix A). V08a and V08b show the two evidence situations; the formula is identical for both.
4. **No double counting.** At the level of item identity (I6): every order_id contributes one R, every exec_id one applied or pending entry, every event_id one orphan entry; an applied execution is never also an orphan or a reservation. Across *different* items that might be one real-world quantity (a discrepancy and an unlinked orphan; an unreported fill already inside d and also inside R), both are counted. That conservative overlap is D01's rule, bounded and measured as gaps G1 and G2.
5. **No quantity disappears.** An item leaves Q3 only by the two recorded transitions below. Delay, replay, duplication, unmatched identity or correction do not remove it: duplicates are idempotent by event_id, replays recompute from the log, and no timeout, belief, strategy or state-keeper assertion alone clears an item.
6. **How an item moves into the applied ledger.**

| From | To | Trigger | Accounting in ONE revision step |
|---|---|---|---|
| Orphan or pending item (T1, T1u, T2) | Applied | Association evidence: the order id resolves, or an authoritative broker response establishes order, side and quantity; no contradiction | The item leaves Q3, enters the execution ledger, F_d changes by the signed quantity; if an order is known its net_cum rises and R falls by the same amount |
| Orphan T2 | Dismissed | Authoritative broker response establishes it is not an execution, or duplicates an applied one | The item leaves Q3; evidence retained |
| Identity-changing or incomplete CORRECT held under D26 or D27 | Applied or Dismissed | An authoritative broker response establishes the corrected execution's instrument, side, order association and quantity (application), or establishes that the correction is not valid (dismissal) | Application: one revision step replaces the held items with the corrected execution. Dismissal: the held correction leaves and the original execution stays at its current version; evidence retained |
| Any | Any other exit | none exists | Timeouts, internal belief, the strategy and a state-keeper assertion cannot clear an item |

There is no instant at which the quantity is in neither place or in both: the move is one revision step, and the evaluation at the new revision sees only the new state.

7. **The sum rule is conservative in each relevant case** (hand derivation against the worlds of 2.3, not executed):

| Case | Items | Exact extremes over the worlds | Sum-rule bound | Relation |
|---|---|---|---|---|
| C1 | discrepancy only | F_max = F_d + d_plus, F_min = F_d - d_minus | same | tight |
| C2 | orphan with known side, not reflected (T4), no discrepancy | one-sided by side | Q3_buy to F_max, Q3_sell to F_min | tight for the bound the side widens; the opposite bound takes no credit (gap G3) |
| C3 | discrepancy plus an unrelated orphan (V08a) | both additive | sum | tight for A_raw; F_max takes no credit for the sell orphan (gap G3) |
| C4 | discrepancy plus an orphan already in the snapshot (T3, V08b, V23) | orphan inside d | d and Q3 both counted | conservative, gap G1 |
| C5 | orphan of unknown side | +/- q | Q3_unk on both bounds | tight |
| C6 | ambiguous event, parseable quantity | includes a world where it did not occur | Q3_unk on both bounds | conservative by the not-occurred world, which never loosens a bound |
| C7 | unknown quantity or unknown instrument | no bound | UNBOUNDED | no optimistic authorization possible |
| C8 | unknown working order | fills conserve R plus position | full R in B or S | tight |
| C9 | unreported fill at or before W | inside d and in R | both counted | conservative, gap G2 |
| C10 | snapshot ahead of received events | W1-F unbounded | UNBOUNDED | conservative (F-4) |
| C11 | late execution after terminal status | contradicts terminal cum | pending item plus structural evidence failure: UNRESOLVED | conservative |
| C12 | bust or correction of an applied execution, identity unchanged, prior version current | new evidence | recompute; OVER_RESERVED if A_raw < 0 | detection, not prevention (I8) |
| C13 | correction that changes side, order association or instrument (D26) | no admitted world represents it | UNBOUNDED; increases and reductions blocked | structural; no optimistic authorization possible (V59) |

**Worked examples for the two evidence situations (V08a, V08b).** Common setup: F_d = 70, F_b = 65 at the same W (d = -5, MISMATCH), working sell 20, one orphan sell of 5.
- *V08a, orphan known to be after W (T4).* Formula: F_min = 70 - 5 - 5 = 60, A_raw = 60 - 20 = 40. Worlds: W1-T gives P = 70 - 5 - 5 = 60 (A_w = 40); W1-F gives P = 70 - 5 = 65 (A_w = 45). Oracle minimum 40 equals the formula: tight.
- *V08b, orphan with broker_seq <= W (T3, possibly already in the snapshot).* The formula is unchanged: 40. Worlds: W1-T has the orphan inside F_b, so P = 65 (A_w = 45); W1-F gives P = 70 - 5 = 65 (A_w = 45). Oracle minimum 45: the formula is conservative by 5 (gap G1).
- The formula cannot tell the two apart without trusting a link between the orphan and d, which v0.1 does not do (D01). The sequence evidence only labels the oracle's world set and the gap class. With no sequence number (V25) both timings are enumerated and the oracle minimum is 40.

**Worked G3 examples (R31-02; from the blind oracle cases B2 and B5; hand-derived, not executed).**
- *B2 (G3 in the upper bound).* F_d = 50; snapshot F_b = 45 at W (d = -5, MISMATCH); working sell R = 10; one known sell execution of 3 that occurred with broker_seq > W (T4). Model: d_plus = 0, d_minus = 5, Q3_sell = 3, so F_max = 50, F_min = 50 - 5 - 3 = 42, U = 50, A_raw = 42 - 10 = 32. Worlds: W1-T gives P = 45 - 3 = 42; W1-F gives P = 50 - 3 = 47. Oracle: U_oracle = 47, A_oracle = 42 - 10 = 32. Gaps: U by 3, class G3 (the sell orphan does not lower F_max); A by 0.
- *B5 (G1 in the upper bound, G3 in the lower bound).* F_d = 100; snapshot F_b = 104 at W (d = +4, MISMATCH); working buy 6 and working sell 20; one known buy execution of 4 that occurred with broker_seq <= W (T3). Model: d_plus = 4, d_minus = 0, Q3_buy = 4, so F_max = 108, F_min = 100, B = 6, U = 114, A_raw = 100 - 20 = 80. Worlds: W1-T has the orphan inside F_b, P = 104; W1-F adds it, P = 104. Oracle: U_oracle = 104 + 6 = 110, A_oracle = 104 - 20 = 84. Gaps: U by 4, class G1 (the T3 buy is counted in d and in Q3_buy); A by 4, class G3 (the buy orphan does not raise F_min).

### 2.4.2 Uncertainty inventory [R] (C-09, D17 modification)

Every uncertainty has exactly one home: a **term** of 2.4, **UNBOUNDED**, or a **block** with no quantity. "Exactly one" is by item identity; overlap between *different* items that may be one real quantity is the sum rule (D01, gaps G1 and G2). A new item class may not be added without a row here.

| Uncertainty | Home | F_min | F_max | B / S | Bounded? | Affects authority |
|---|---|---|---|---|---|---|
| Unknown buy execution (T1 buy) | Q3_buy | none | + q | none | bounded | increases blocked; U up |
| Unknown sell execution (T1 sell) | Q3_sell | - q | none | none | bounded | A down |
| Unknown execution side, known quantity (T1u) | Q3_unk | - q | + q | none | bounded | both |
| Unknown execution quantity | T2-U | UNB | UNB | n/a | **unbounded** | increases DENY, reductions UNRESOLVED |
| Unassociated execution | T1 or T1u by side | as above | as above | none | bounded | as above |
| Working order, unknown identity but known side and remaining quantity | UNKNOWN order | none | none | full R in B (buy) or S (sell) | bounded | increases blocked |
| **Working order of unknown side, known remaining quantity (requirement F)** | UNKNOWN order | none | none | **full R in both B and S** | bounded | increases blocked; A down |
| Order with unknown remaining quantity | T2-U | UNB | UNB | n/a | **unbounded** | as T2-U |
| Correction or bust of a known applied execution, identity unchanged, prior version current (D27) | applied at its own broker_seq: moves F_d, and F_d(W) only if that seq <= W | by effect | by effect | B or S change only for a working order whose net_cum changes (R = qty - net_cum); a terminal order keeps R = 0 (I7) | bounded | by revision; may raise OVER_RESERVED |
| Correction whose prior version or prior quantity does not match the current version (D27) | structural evidence failure | n/a | n/a | R kept | n/a | both blocked (UNRESOLVED) |
| Correction that changes side, order association or instrument (D26) | T2-U: held pending, not applied | UNB | UNB | n/a | **unbounded** | as T2-U |
| Correction missing prior_version, prior_qty or another required field (malformed, D27) | T2-U: orphan of unknown quantity | UNB | UNB | n/a | **unbounded** | as T2-U |
| Pending correction or bust, original unknown | T2-U | UNB | UNB | n/a | **unbounded** | as T2-U |
| Snapshot ahead of received events | AWAITING-BEHIND | UNB | UNB | n/a | **unbounded** (D18) | as T2-U |
| Missing sequence | GAP | UNB | UNB | n/a | **unbounded** | as T2-U; a later snapshot never clears it |
| Unverified snapshot (no watermark, ledger not quiescent) | AWAITING-UNVERIFIED | UNB | UNB | n/a | **unbounded** | as T2-U |
| Position mismatch (quantified, signed or magnitude-only) | d (d_plus, d_minus, 2.2) | - d_minus | + d_plus | none | bounded | increases blocked; reductions by A (D19, conditional) |
| Applied execution with no broker_seq | d over all inclusion choices (2.2) | - d_minus | + d_plus | none | bounded | as the mismatch |
| Duplicate event id, identical content | idempotent: no change | none | none | none | n/a | none |
| Duplicate event id, conflicting content | structural evidence failure (block) | n/a | n/a | R kept | n/a | both blocked (UNRESOLVED) |
| Instrument identity uncertainty | D13 quarantine: T2-U | UNB | UNB | n/a | **unbounded** | as T2-U |
| *Not represented by any row (A-12, A-11, 2.3):* undelivered events; duplicate economic execution under a different id; wrong-side association | **no home** | | | | | **uncovered environmental failure** |

Answers: (1) each row is one home; (2) an item leaves a home only by apply or authoritative dismissal (2.4.1 item 6); (3) matching an orphan is application in one revision step, never a bare reduction of uncertainty; (4) an item is in one of K1, K2, K3 by identity (I6); (5) a correction moves F_d through the log by its own broker_seq, and an unknown-original correction is UNBOUNDED until the original arrives.

### 2.5 Invariants I1a to I9 [R as requirements; every claim about them is HYPOTHESIZED until executed]

One reconciled set. Each invariant states: statement, preconditions, scope of universality, required assumptions, a counterexample attempt, known limitations, and an independently specified test. Notation: a ledger is Lambda; "fill q on order o" is one NEW execution of q units on o with 1 <= q <= R(o). "Within the model" means given the stated assumptions (A-1 to A-11, W1 to W7). None of these is claimed proven universally; bounded enumeration is not proof.

**I1a Buy-fill conservation.**
- *Statement.* Part 1: if the status is RECONCILED or AWAITING, or the fill's broker_seq > W, then a buy fill of q gives F_d' = F_d + q, B' = B - q, **U' = U**, A_raw' = A_raw + q. Part 2: in any BOUNDED status, U' <= U and A_raw' >= A_raw.
- *Preconditions.* The fill is consistent; no other change; BOUNDED before and after.
- *Scope.* Part 1 conditional (status or sequence); Part 2 universal within the model over bounded ledgers.
- *Assumptions.* W1 to W7, A-2.
- *Counterexample attempt.* All bounded ledgers x all buy fills; V05; V17, where a fill already inside the snapshot lowers U from 125 to 120.
- *Limitations.* "U unchanged" is false for a late fill inside a MISMATCH; the dispatch wording "must not increase U" holds.
- *Independent test.* The oracle computes U_oracle and A_oracle before and after the fill from the raw items and checks the monotone relations; frozen hand vectors V05, V17.

**I1b Sell-fill conservation.**
- *Statement.* Part 1 (same preconditions as I1a): F_d' = F_d - q, S' = S - q, **A_raw' = A_raw**, U' = U - q. Part 2: A_raw' >= A_raw and U' <= U.
- *Preconditions, scope, assumptions, limitations.* As I1a.
- *Counterexample attempt.* All bounded ledgers x all sell fills; V06; V15 (fill-first branch).
- *Independent test.* As I1a, plus V06 and V15.

**I2 No over-reduction at the committed revision.**
- *Statement.* If a reduction of Q is committed at revision R, then Q <= A(R), BOUNDED(R), and no structural evidence failure exists at R. After the commit S rises by Q, so a second reduction is judged against A(R) - Q.
- *Preconditions.* I5 holds (evaluation and commit on the same revision, with freshness re-validated at commit). **For a reduction while the status is a quantified MISMATCH (D19, C-10) all five hold:** (1) d is a signed integer or magnitude-only value (2.2) from a snapshot with a valid watermark and contiguous events through W (not GAP, AWAITING-BEHIND, AWAITING-UNVERIFIED); (2) no structural evidence failure and no pending correction or bust; (3) unsequenced applied executions are handled by the interval construction of 2.2; (4) the snapshot is within its staleness limit **at evaluation and again at commit** and the decision age is within D_max (2.9); (5) the reduction is judged against A, never clipped, and never exceeds the position in the long-only envelope. If any fails, reductions are DENY or UNRESOLVED.
- *Scope.* Universal within the model (it follows from the decision function and I5).
- *Assumptions.* W1 to W7, A-3.
- *Counterexample attempt.* Sells of A and A+1; two concurrent sells (V14); sell after a partial fill (V43).
- *Limitations.* Concerns authorization at commit; says nothing about later evidence (I8) or broker outcomes. **Failure of A-12 (an unreported, undelivered, duplicated, misattributed or otherwise unrepresented execution) can invalidate both bounds and reduction permission in every position status, including RECONCILED; D19 addresses only the quantified discrepancy d (R31-03').** **D19 is a specification candidate, conditional on the world model.** Zero false permissions in the declared oracle test space cannot establish safety against conditions excluded from W1 to W7 (A-11, A-12, wrong-side association, duplicate economic executions). The pre-declared rollback applies: if the oracle run finds any false permission on a MISMATCH ledger, reductions during a quantified MISMATCH are blocked (D19 option b).
- *Independent test.* ALLOW implies Q <= A_oracle (the oracle's minimum over worlds), checked on every enumerated case; CAS interleavings (5.4).

**I3 Nonnegative authorization quantity; over-reservation detection.**
- *Statement.* A >= 0 always; OVER_RESERVED is raised iff A_raw < 0; A_raw is preserved for diagnostics; while OVER_RESERVED, every increase and every reduction is DENY.
- *Preconditions.* None.
- *Scope.* Universal by definition; the test target is flag correctness.
- *Assumptions.* None beyond the sum rule.
- *Counterexample attempt.* V04 (supplied ledger), V16 (bust).
- *Limitations.* Detection, not prevention; the model does not say who clears it (D10).
- *Independent test.* Whenever A_oracle < 0 the flag must be raised (no false negative); false positives caused by G1, G2 and G3 are counted and reported as availability cost.

**I4 Conservative uncertainty and no redundant counting (soundness).**
- *Statement.* For every ledger with BOUNDED status, for every world w consistent with the evidence under W1 to W7: U >= max over w of (P_w + remaining buys_w) and A_raw <= min over w of (P_w - remaining sells_w). Each uncertain item appears in exactly one term (set equality of item ids and terms). Tightness is measured, not asserted: the gap to the oracle is classified G1, G2 or UNEXPLAINED.
- *Preconditions.* BOUNDED; the world model of 2.3.
- *Scope.* Conditional on W1 to W7. **Not unconditional**: a later bust, correction or new evidence that violates W1 to W7 invalidates the bound (I8).
- *Assumptions.* W1 to W7, A-2, A-7.
- *Counterexample attempt.* Exhaustive enumeration (5.2). The unconditional max rule is expected to fail at V08a-type states; it is run only as a test-only variant.
- *Limitations.* Soundness is relative to the world model, not to any real broker; G1, G2 and G3 over-denial is accepted (D01, widen-only principle).
- *Independent test.* The oracle of 5.1, which shares no code and no formulas with the model.

**I5 Revision integrity and decision age.**
- *Statement.* A commit succeeds only if all hold: outcome = ALLOW; decision.ledger_revision = store.revision; decision.item_hash = hash(store items); configuration hash and master version equal; proposal_id has no committed reservation; (commit time - decision.as_of) <= D_max (D21); and **the pure evaluation re-run at the commit time on the store's current ledger (as_of = commit time) again returns ALLOW for the same proposal**, so snapshot age and every other freshness check are re-validated at commit. D_max does not extend S_lim: a snapshot older than S_lim at commit time fails regardless of D_max. Otherwise nothing changes.
- *Preconditions.* Atomic compare-and-set in the store.
- *Scope.* Universal within the model.
- *Assumptions.* A-3, A-4.
- *Counterexample attempt.* Stale replay; duplicate commit; intervening fill, cancel or UNKNOWN; snapshot ageing past the limit with no ledger change (V44).
- *Limitations.* A store that lies or is not atomic defeats it; D_max is a parameter (OPEN value).
- *Independent test.* Exhaustive interleaving enumeration (140 schedules per scenario) and a separate stale-replay test.

**I6 Every item counted exactly once, by identity.**
- *Statement.* Each order_id contributes at most one R; an AUTHORIZED order is the reservation and is not counted again at submission; each exec_id is applied at most once; each event_id is in exactly one of {applied, orphan or pending, dismissed}; every move between those classes happens in one revision step. Overlap between different items is permitted (sum rule) and is not a violation of I6.
- *Preconditions.* Event ids are stable (A-2).
- *Scope.* Universal within the model.
- *Counterexample attempt.* Duplicate injection at every position of every enumerated event sequence; replay; V19, V26.
- *Limitations.* If the broker issues non-unique ids the model reports a conflict (V27), it cannot repair them. **Idempotency by event ID does not establish economic-execution uniqueness.** One real execution re-sent under a different event id is applied twice, overstating F_d by its quantity (V56); it is not detected until a later snapshot shows the discrepancy. This is an uncovered environmental failure (A-11).
- *Independent test.* A partition check on item ids, written without calling the model's accounting.

**I7 Lifecycle history versus net execution.**
- *Statement.* The lifecycle history is append-only (each ledger's history is a prefix of its successor's). For a terminal order R = 0 regardless of net_cum. BUST and CORRECT change net_cum and F_d but never the lifecycle state and never R of a terminal order. net_cum must stay in [0, qty], else structural conflict. A transition into a terminal state requires the broker cumulative quantity to equal net_cum_at(order, seq of that event) with every execution up to that sequence applied.
- *Preconditions.* broker_seq present on the terminal event, else the rule is checked in quiescent state only.
- *Scope.* Universal within the model.
- *Counterexample attempt.* Bust after FILLED (V30); correction after CANCELED; late execution (V32).
- *Limitations.* The as-of rule means a later bust does not retroactively falsify the terminal report; the bust is its own event (T21).
- *Independent test.* Sequence enumeration with a separately written history checker.

**I8 Behavior after busts, corrections and new evidence (safety is conditional).**
- *Statement.* A reduction authorized at revision R **remains position-safe** at a later revision R' iff BOUNDED(R') and F_min(R') - S(R') >= 0, evaluated with W1 to W7 at R'. If new evidence makes A_raw(R') < 0, OVER_RESERVED is raised in the same revision in which the evidence is applied, and every increase and reduction is DENY until cleared.
- *Preconditions.* Evidence is applied through the log.
- *Scope.* Detection universal within the model. Safety is conditional on W1 to W7 continuing to hold.
- *Counterexample attempt.* Busts and orphans after authorization over all enumerated sequences; V16.
- *Limitations.* The model cannot recall an order already at the broker, and cannot guarantee any broker-side outcome. Who may cancel to clear OVER_RESERVED is not decided here (D10, G-07).
- *Independent test.* After every event of every enumerated sequence: A_oracle < 0 implies the flag.

**I9 Idempotency and deterministic replay.**
- *Statement.* Applying an identical event twice equals applying it once. Folding a fixed log in log-position order gives byte-identical ledgers and decisions. No clock reading, randomness or unordered iteration appears in a pure function.
- *Preconditions.* Canonical serialization (sorted keys, integers only, no floats); the as_of time is an explicit input.
- *Scope.* Universal within the model for a fixed log. Arrival-order invariance is **not** claimed for non-commuting events.
- *Counterexample attempt.* Duplicate injection; two independent replays; log re-serialization.
- *Limitations.* Does not show that two different logs of the same real-world history agree.
- *Independent test.* Replay hash equality, written outside the model package.

**Safety scope, separated.**
1. *Safety under the model's stated assumptions:* I2, I4 and I5 together: a committed reduction never exceeds the oracle's conservative availability at its revision.
2. *Behavior when new evidence invalidates those assumptions:* I8: detect and raise OVER_RESERVED; block; do not claim the earlier authorization was wrong, or that the position is safe.
3. *What the model cannot guarantee:* broker-side outcomes (a sell filling after we believe it cancelled, a broker rejecting a reduction, a bust that arrives later), the truth of broker evidence, or a safe exit under evidence failure.

### 2.6 Event and transition semantics [R]

Generic handling of malformed, duplicate, stale and conflicting events (item 8 of the dispatch). Exceptions are in the table.
- **Duplicate** (same event_id, identical canonical payload): idempotent no-op; no revision change; duplicate count recorded.
- **Same event_id, different payload:** CONFLICT evidence failure. Affected order treated as UNKNOWN (R kept at qty - net_cum). Blocks increases; reductions UNRESOLVED until an authoritative broker response resolves it.
- **Out of order (broker_seq beyond next expected):** not applied; buffered as evidence; position status GAP (UNBOUNDED).
- **Stale (broker_seq below the applied watermark, event_id unseen):** applied only if consistent with the order's recorded cum_qty and state; otherwise CONFLICT.
- **Malformed (schema, type, range, instrument):** not applied; raw evidence retained; treated as an orphan of unknown quantity (UNBOUNDED) until resolved by a broker query.

Columns: dF = changes F_d; dB, dS = changes B, S; band = changes uncertainty items; blk = blocks increases; red = can permit a reduction; ev = evidence retained (all events retain raw_hash, event_id, broker_seq, received_at; table lists only the extra).

| # | Event | dF | dB | dS | band | blk | red | Extra evidence / exceptions |
|---|---|---|---|---|---|---|---|---|
| E01 | Proposal created | no | no | no | no | no | n/a | Proposal record. Not a reservation. |
| E02 | Authorization committed (CAS) | no | +qty if buy | +qty if sell | no | no | yes (by A) | Decision hash, revision. Order becomes AUTHORIZED; counted once from this moment. |
| E03 | Order submitted (adapter reports) | no | no | no | no | no | yes | Requires live reservation token (A-5). Submit without a live reservation: order later appears as unknown order (E20). |
| E04 | Acknowledged | no | no | no | no | no | yes | Duplicate ack is a no-op; ack contradicting state is CONFLICT. |
| E05 | Partial fill (NEW exec) | yes (signed q) | -q if buy | -q if sell | no | no | yes | net_cum updated. q > R(o) is CONFLICT (overfill). |
| E06 | Full fill | yes | R to 0 | R to 0 | no | no | yes | Order FILLED (terminal). net_cum must equal qty else CONFLICT. |
| E07 | Cancel requested | no | no | no | no | no | yes | State CANCEL_PENDING; R unchanged (may still fill). Recorded as an event only: the model does not decide or imply who may issue a cancellation (D10, G-07). |
| E08 | Cancel confirmed | no | -R if buy | -R if sell | no | no | yes | Terminal. R is released only if the required broker evidence is present and cum_qty equals net_cum, all executions up to the event being applied; otherwise CONFLICT and the order stays working with R kept. Arithmetic effect only; no judgment that the cancellation is risk-reducing. |
| E09 | Rejected | no | -R | -R | no | no | yes | Terminal. cum_qty must be 0 for a never-filled order, else CONFLICT. |
| E10a | Broker expiry | no | -R | -R | no | no | yes | Terminal, cum_qty required as for E08. |
| E10b | Reservation expiry (internal) | no | -qty | -qty | no | no | yes | Only for AUTHORIZED never submitted. A later broker event for that order_id is T22 (order UNKNOWN, R re-reserved). |
| E11 | Order status UNKNOWN | no | R kept | R kept | no | **yes** | by A if BOUNDED | Order counted as working until broker-resolved (T20). |
| E12 | Duplicate execution report | no | no | no | no | no | n/a | No-op. Same exec_id different payload: CONFLICT. |
| E13 | Corrected execution | yes (qty - prior_qty) | adjusts via net_cum | adjusts | no | no | by A | A CORRECT replaces the quantity of the named version (D27, 2.2): reference, completeness and prior_version and prior_qty must match, else T2-U or structural conflict as in 2.2 (V49, V61). If the new net_cum is outside [0, qty] or exceeds broker cum: CONFLICT. Applies to terminal orders too (T21). A CORRECT that changes side, order association or instrument is not applied: structural evidence failure, band UNBOUNDED, increases and reductions blocked (D26, V59). A CORRECT or BUST naming an unknown original is held pending: effect unknown, band UNBOUNDED until the original arrives or the broker resolves it (V31). |
| E14 | Busted / reversed execution | yes (-old) | none (terminal R stays 0; working order R rises) | same | no | no | by A | May produce OVER_RESERVED. Does not resurrect a terminal order. |
| E15 | Execution out of order | no (not applied) | no | no | GAP | **yes** | no (UNRESOLVED) | Buffered until the gap fills. |
| E16 | Execution after cancel request | yes | -q (buy) | -q (sell) | no | no | yes | Normal fill on CANCEL_PENDING; R after the fill continues until confirmation. |
| E17 | New execution after terminal status | not applied | no | no | pending item by side (Q3) | **yes** | no (UNRESOLVED) | T22: order UNKNOWN with R = qty - net_cum (re-reserved); structural evidence failure (conflicts with the terminal cum_qty). The execution moves to F_d only on authoritative reconciliation (V32). Modified from the addendum's IB3 (F-8). |
| E18 | Duplicate ack / cancel confirm | no | no | no | no | no | n/a | No-op if identical and state-consistent; otherwise CONFLICT. |
| E19 | Conflicting broker events | no | R kept | R kept | evidence failure | **yes** | no (UNRESOLVED) | Order frozen as UNKNOWN. |
| E20 | Unknown order identity | no | no | no | orphan (Q3 by side) | **yes** | by A if qty and side known | Orphan keyed by event_id. |
| E21 | Unknown execution side or quantity | no | no | no | side unknown: Q3_unk; qty unknown: UNBOUNDED | **yes** | side unknown: by A; qty unknown: no | |
| E22 | Execution not associable | no | no | no | as E20 | **yes** | as E20 | |
| E23 | Broker snapshot received | no | no | no | recomputes d, status | by status | by status | snapshot_id, W, F_b. Cases in 2.6.2. Older W than the last accepted: REPLAY, ignored with record. |
| E24 | Master semantic change (class B) | no | released if AUTHORIZED unsubmitted | released if AUTHORIZED unsubmitted | status UNKNOWN until reconciled | **yes** | **no** (R_MASTER_CHANGE) | Master version and hash; effects in 2.12, V35. |

**Cancellation semantics (D10 amended) [R].** The model represents a cancellation request (E07) and a broker-confirmed cancellation (E08, and unsolicited broker cancellations) as events. It does not decide, imply or enforce who has authority to issue a cancellation command; that question is outside v0.1 and reserved for G-07. A confirmation removes the remaining working-order reservation only when the required broker evidence and cumulative-quantity checks are satisfied. The model does not classify cancellation of a working sell as inherently risk-reducing: its only effect in the model is the arithmetic change to S (or B). OVER_RESERVED clears when A_raw >= 0 by whatever evidenced events occur; the model does not say who must act.

### 2.6.1 Order lifecycle with accounting effects [R]

States: PROPOSED, AUTHORIZED, SUBMITTED, ACKNOWLEDGED, PARTIALLY_FILLED, FILLED, CANCEL_PENDING, CANCELED, REJECTED, EXPIRED, UNKNOWN, DENIED. Terminal: FILLED, CANCELED, REJECTED, EXPIRED, DENIED. The table is exhaustive: a transition not listed is invalid. Evidence codes: EV-eval (evaluation record), EV-msg (broker message id and raw hash), EV-req (our outgoing request hash), EV-clk (independent clock reading), EV-rec (reconciliation result). Each transition is one revision step. R is the remaining reserved quantity of 2.2.

| ID | From to | Trigger and evidence | Accounting effect (F_d; B or S; band) | If invalid |
|---|---|---|---|---|
| T01 | none to PROPOSED | Strategy proposal (intent only); proposal hash | none; not in the ledger | IB1 |
| T02 | PROPOSED to AUTHORIZED | Internal evaluation ALLOW and successful commit (2.9); EV-eval | **R reserved**: B or S rises by qty; revision + 1 | stays PROPOSED, then T03 |
| T03 | PROPOSED to DENIED | Internal evaluation DENY or UNRESOLVED, returned as a Refusal (2.9); EV-eval with codes | none | n/a |
| T04 | AUTHORIZED to SUBMITTED | Our submit, consuming a live reservation (ACTIVE to CONSUMED, exact payload equality, 2.9); EV-req, EV-clk | none (same order id, counted once) | IB2 |
| T05 | AUTHORIZED to EXPIRED | TTL (EV-clk), or master class-B change (2.12) | R released; revision + 1 | n/a |
| T06 | SUBMITTED to ACKNOWLEDGED | Broker ack; EV-msg | none | IB1 |
| T07 | SUBMITTED to REJECTED | Broker reject; net cum = 0 | R released | IB4 |
| T08 | SUBMITTED to PARTIALLY_FILLED or FILLED | Fill before ack | F_d +/- q; R -q (I1) | IB3/IB4 |
| T09 | ACKNOWLEDGED to PARTIALLY_FILLED | Execution | F_d +/- q; R -q | IB3/IB4 |
| T10 | ACKNOWLEDGED or PARTIALLY_FILLED to FILLED | Execution completes the order | F_d +/- q; R = 0 | IB3/IB4 |
| T11 | PARTIALLY_FILLED to PARTIALLY_FILLED | Further partial execution | F_d +/- q; R -q | IB3/IB4 |
| T12 | SUBMITTED, ACKNOWLEDGED or PARTIALLY_FILLED to CANCEL_PENDING | Cancel request recorded as an event (D10: the model does not decide who may issue it); EV-req | none; R kept in full | IB2 |
| T13 | CANCEL_PENDING to CANCEL_PENDING | Execution before confirmation | F_d +/- q; R -q | IB3/IB4 |
| T14 | CANCEL_PENDING to FILLED | Execution completes the order | F_d +/- q; R = 0 | IB3/IB4 |
| T15 | CANCEL_PENDING to CANCELED | Broker confirmation; **terminal rule** | R released | IB4 |
| T16 | CANCEL_PENDING to ACKNOWLEDGED or PARTIALLY_FILLED | Broker rejects the cancel | none | IB1 |
| T17 | working to EXPIRED | Broker time-in-force expiry; terminal rule | R released | IB4 |
| T18 | working to CANCELED (unsolicited: halt, broker limit) | Broker; terminal rule; alarm | R released | IB4 |
| T19 | working to UNKNOWN | No confirmation within the limit (value OPEN, D08), disconnect, contradictory reports | none; R kept; **blocks increases** | n/a |
| T20 | UNKNOWN to resolved state | Authoritative broker order-status response only; executions reconciled | R per the resolved state | stays UNKNOWN |
| T21 | terminal to the same state, attributes updated | BUST, or a CORRECT that keeps identity and satisfies the D27 contract, referencing a known execution | F_d and net_cum adjust (F_d(W) only if the event's own seq <= W); **R stays 0**; lifecycle state not rewritten; may raise OVER_RESERVED. A stale prior version is a structural conflict; an identity-changing CORRECT is held under D26 (UNBOUNDED) | IB4 |
| T22 | CANCELED, REJECTED or EXPIRED to UNKNOWN | An event arrives for a dead order | order UNKNOWN with **R = qty - net_cum (re-reserved)**. If the event is an execution: it is held as a pending item (by side) and a structural evidence failure is raised (modified from the addendum's IB3, F-8). **Possible over-denial (R31-11):** the re-reserved remainder and the held execution may be the same real quantity and both are counted; that is conservative overlap in the sense of D01, not exact accounting. If it is any other report: UNKNOWN only, no failure. | IB3 |

Invalid-transition classes (from the addendum, reconciled): **IB1** reject the event, state unchanged, log (malformed or unauthorized originators land here, E8). **IB2** block our own action, state unchanged, alarm. **IB3** event contradicts a terminal state: order UNKNOWN, any execution held as a pending item (not applied to F_d until reconciled). **IB4** data conflict: order UNKNOWN and a *structural* evidence failure (INCONSISTENT); the addendum set the position status to MISMATCH here, which is different from a snapshot mismatch and is not used (2.6.2).
No transition leaves a terminal state except T21 (attributes only) and T22 (anomaly).

**Terminal-transition rule [R].** A transition into a terminal state (T05 excepted, T07, T14, T15, T17, T18) requires that every execution up to the event has been applied and that the broker-reported cumulative quantity equals **net_cum_at(order, the event's broker_seq)**, i.e. the net quantity as of that event, not the latest net_cum. If an execution below that sequence is missing, the check fails closed (IB4). A later BUST or CORRECT is a separate event (T21): it changes net_cum and F_d, and does not retroactively falsify the earlier terminal report. This is the same principle as comparing a snapshot at its own watermark (RQ8).

### 2.6.2 Position status and snapshot rules [R]

A snapshot is compared with F_d(W) at the snapshot's own watermark, never with the latest derived position.

| Status | Definition | Bounded? | Blocks increases | Reductions |
|---|---|---|---|---|
| RECONCILED | contiguous through W; F_d(W) = F_b | yes | no | by A |
| AWAITING | executions applied after the latest snapshot, no gap, F_d(W) = F_b | yes | no | by A |
| MISMATCH | contiguous through W; F_d(W) != F_b under at least one inclusion choice of 2.2; d_plus and d_minus recorded | yes, by d | **yes** | by A (**D19**, conditional; preconditions in I2) |
| AWAITING-BEHIND | snapshot watermark above the highest applied sequence | **no** (D18) | yes | UNRESOLVED |
| AWAITING-UNVERIFIED | no watermark and the ledger is not quiescent | **no** | yes | UNRESOLVED |
| GAP | a sequence number missing at or below W | **no** | yes | UNRESOLVED |
| UNKNOWN | no snapshot, stale beyond the limit (D07), or conflicting snapshots | **no** | yes | UNRESOLVED |

AWAITING-BEHIND becomes GAP when the wait limit passes (value OPEN, D08). Quiescent means no working, authorized or unknown orders and no pending events.

| Snapshot case | Outcome |
|---|---|
| Valid watermark | Compare F_d(W) with F_b: RECONCILED, or MISMATCH with d recorded (case 1) |
| Gap at or below W | GAP; no comparison is made (it would produce a false MISMATCH) |
| Ahead of the highest applied sequence | AWAITING-BEHIND (F-4) |
| Stale or replayed (W below the latest accepted watermark) | Rejected; Freshness REPLAY; prior state kept |
| Equal watermark, different content | Conflict: Consistency INCONSISTENT (structural); both snapshots retained; status UNKNOWN until the broker resolves it |
| No watermark | Compared only if the ledger is quiescent; otherwise AWAITING-UNVERIFIED. No tolerance is invented. |
| Instrument id differs from the canonical id | Rejected (IB1) and logged; prior state kept |
| Snapshot quantity not a signed integer, or negative in the long-only envelope | Structural Consistency failure: UNRESOLVED (V54) |
| Discrepancy supplied as magnitude only | d_plus = d_minus = magnitude (2.2, V53) |
| Applied execution without broker_seq | d over all inclusion choices (2.2, V51) |
Time-only `as_of` is not used for comparison. Freshness and wait limits are parameters in the register (D07, D08), not values here.

**Snapshot replacement rule (R31-07') [R].** A snapshot replaces the prior discrepancy item d only if all hold: (1) it is accepted under every rule of this section and of 2.8 (canonical instrument; integrity, provenance, authenticity, consistency and freshness acceptable; no structural failure); (2) its watermark W' is **strictly greater** than the prior accepted watermark (a later timestamp alone is never enough; an equal watermark with identical content is idempotent and with different content is a conflict); (3) events are contiguous through W' (no GAP, not AWAITING-BEHIND). The discrepancy is then **recomputed** as d' = F_b' - F_d(W') from the new snapshot and the applied events whose own broker_seq <= W'. A newer snapshot that still disagrees yields a new MISMATCH, not RECONCILED (V62). Only the prior discrepancy item is replaced: no orphan, pending item, pending correction or bust, unknown order, structural failure or GAP leaves because a snapshot arrived, unless it has satisfied its own resolution rule (2.4.1 item 6, 2.6.3, T20). Executions applied with broker_seq between W and W' enter F_d(W') and so change d' through the same recomputation. **A newer accepted snapshot does not establish A-12 for the interval it covers:** it can reveal an earlier failure as a discrepancy; it cannot make the event stream complete after the fact.

### 2.6.3 Event ordering, idempotency and deterministic replay [R]
- **Canonical order is the log position.** Every accepted event is appended to the hash-chained log; the ledger is a pure fold over the log in that order (D20, F-7). broker_seq is used for gap detection and for watermark and as-of comparison, never to reorder the log.
- **Identity and economic uniqueness (requirement B).** **Idempotency by event ID does not establish economic-execution uniqueness.** The same real-world execution delivered under a different event id or exec_id is, to the model, a second execution; the model cannot detect it (V56). It is documented as an uncovered environmental failure that may create false permission before reconciliation: a duplicated buy overstates F_d (false permission for reductions), a duplicated sell understates it (false permission for increases). A later snapshot shows it as a discrepancy. event_id is broker-unique; if the broker supplies none, the hash of the canonical content. Identical event_id and identical content: apply once, count the duplicate (counters are outside the item hash). Same event_id, different content: structural conflict.
- **Sequence inconsistencies.** A broker_seq below the applied watermark with an unseen event_id is applied only if consistent with the order's recorded state, else a conflict. The same broker_seq with different event_id or content is a conflict.
- **Absent sequence numbers.** Events without broker_seq are ordered by log position, carry unknown timing (both T3 and T4 enumerated), and cannot establish a watermark.
- **Determinism.** Canonical serialization: sorted keys, integers only, no floats, UTF-8; the as_of time is an explicit input; no clock, randomness or unordered iteration in pure functions. Replaying the same log twice must give byte-identical ledgers and decisions.
- **Out of order.** Position is a sum, so arrival order does not change F_d for non-conflicting sets; an event whose prerequisite has not arrived is held as pending and applied in dependency order. This is **not** claimed for conflicting or state-dependent events.
- **Reconnection (C-05).** A missing sequence is GAP until the missing event arrives, or the broker gives an explicit authoritative resolution of that specific sequence. **A later snapshot never clears a GAP:** it does not supply the order-level accounting (net_cum, R) of the missing execution, and no comparison is made under GAP (V48). Resent events fall under idempotency.

**Limits of replay order (D20, C-13) [R].** The log-position order establishes a deterministic *processing* order only. It does not establish that the resulting state equals the state under any other arrival order; it does not establish that two logs of the same real-world history agree; non-commuting events (for example two corrections of one execution) give outcomes that depend on log position (V49); and it says nothing about economic uniqueness or completeness of delivery (A-11, A-12). Order-invariance is claimed only for sets of non-conflicting executions.

### 2.7 UNKNOWN semantics [R]

| Case | Effect on F_min / F_max | B | S | Blocks | Reduction allowed? |
|---|---|---|---|---|---|
| Unknown increase order | none | + full R | none | all increases | yes, by A, if BOUNDED |
| Unknown reduction order | F_min not lowered (not treated as having reduced) | none | + full R | all increases | yes, by A, if BOUNDED |
| Unknown working order of unknown side, known remaining quantity R (requirement F) | none | + full R | + full R | all increases | yes, by A, if BOUNDED |
| Unknown execution, known side and qty | buy: F_max + q; sell: F_min - q | none | none | all increases | yes, by A, if BOUNDED |
| Unknown execution side, known qty | F_max + q and F_min - q | none | none | all increases | yes, by A |
| Unknown quantity | UNBOUNDED | n/a | n/a | all increases | **no** (UNRESOLVED) |
| Unknown instrument | quarantined; treated as orphan of unknown side and quantity until resolved; UNBOUNDED | n/a | n/a | all activity | **no** |
| Unknown broker position (no or stale snapshot) | status UNKNOWN: UNBOUNDED | n/a | n/a | all increases | **no** (NO_INDEPENDENT_EVIDENCE is not tolerated for reductions, D06 approved) |
| Unknown sequence or watermark | status GAP: UNBOUNDED | n/a | n/a | all increases | **no** |

- Orphan and ambiguous items follow the treatments T1, T1u, T2, T2-U of section 2.3.
- An unknown increase is never treated as unable to fill. An unknown reduction is never treated as already executed. An unknown execution is neither discarded nor applied twice (event_id idempotency).
- Resume: each unknown item is resolved only by an authoritative broker response; then position status RECONCILED or AWAITING at a watermark not earlier than the resolution; then the evaluation shows no unknown item and no evidence failure. Timeouts, internal belief and the strategy never clear an item.
- A reduction during uncertainty is permitted only when the band is BOUNDED, with quantity limited by A. This is not a safe-exit guarantee; whether any exit is possible when the band is UNBOUNDED is the separate protective-intervention problem (G-06) and is out of scope.

**What blocks what [R].** Every unresolved item blocks increases. Only some also block reductions. "Structural evidence failure" means a conflict that cannot be quantified (2.8).

| Condition | Blocks increases | Blocks reductions |
|---|---|---|
| UNKNOWN order | yes | no (limited by A) |
| Orphan or pending item with known quantity (T1, T1u, T2) | yes | no (limited by A) |
| T2-U: unknown quantity, unknown instrument, correction naming an unknown original | yes | **yes** (UNBOUNDED; UNRESOLVED) |
| Position MISMATCH with known d | yes | no (limited by A, D19) |
| AWAITING-BEHIND, AWAITING-UNVERIFIED, GAP, UNKNOWN | yes | **yes** (UNBOUNDED; UNRESOLVED) |
| Structural evidence failure | yes | **yes** (UNRESOLVED) |
| OVER_RESERVED | yes | yes (A = 0) |
| Master class-B change pending reconciliation | yes | **yes** (status UNKNOWN until reconciled) |

When no reduction can be authorized (any "yes" in the last column), the model returns UNRESOLVED or DENY; it does not promise a safe exit. Protective intervention is the separate G-06 problem and is not solved here.

### 2.8 Evidence and trust model [R]

Five separate properties, never collapsed into one "verified" flag. A failed or unavailable check is never a pass.

| Property | Question | Established by | What it does NOT establish |
|---|---|---|---|
| Integrity | Unchanged since it was made? | hash of canonical bytes compared with a hash obtained through a trusted channel | who made it; that it is true |
| Provenance | Where from, how derived? | metadata: source, request, raw-payload hash, state-keeper version | only a claim by whoever wrote it |
| Authenticity | Did the claimed party produce it? | signature or MAC with that party's key | that the key holder is uncompromised; that the broker told the truth |
| Consistency | Does it agree with independent evidence and its own invariants? | cross-checks between position, snapshot and executions; fills never exceed order quantity | agreement of sources that share a failure (common mode) |
| Freshness | Recent enough, and not a replay? | independent clock; sequence and watermark monotonicity | content truth; a valid signed record can be stale |

Exactly one result per property, recorded in every evaluation. Only the first state is acceptable.

| Property | Acceptable | Failure states (distinct reason codes, written with the property prefix) |
|---|---|---|
| Integrity | MATCH | INTEGRITY.MISMATCH, HASH_MISSING, NO_TRUSTED_REFERENCE |
| Provenance | COMPLETE (fields present and well-typed; completeness, not truth) | INCOMPLETE, MALFORMED |
| Authenticity | VERIFIED | INVALID_SIGNATURE, SIGNATURE_MISSING, KEY_UNKNOWN, KEY_REVOKED |
| Consistency | CONSISTENT | INCONSISTENT, NO_INDEPENDENT_EVIDENCE |
| Freshness | FRESH | STALE, REPLAY, FROM_FUTURE, CLOCK_UNAVAILABLE |

- **Name collision resolved.** The addendum uses MISMATCH for both an integrity failure and a position status. Here they are INTEGRITY.MISMATCH and POSITION.MISMATCH.
- **Two kinds of Consistency failure (D19).** A *quantified* position mismatch (known d, contiguous events) is carried in the bounds and is a failure for increases only. A *structural* inconsistency (same id with different content, cumulative-quantity conflict, overfill, a correction whose prior version is stale (D27), an identity-changing correction (D26), conflicting snapshots at one watermark) cannot be quantified and blocks increases and reductions.
- Any failure state blocks increases. The state-keeper cannot override a failure state. An unavailable check (for example CLOCK_UNAVAILABLE) is a failure state.
- NO_INDEPENDENT_EVIDENCE (one source, no second channel) is not tolerated for reductions (D06 approved). Whether it may be tolerated in a first replay for any other purpose, and what independent evidence any future live use requires, remain **OPEN** (D24).
- **Integrity is not truth.** A hash, a signature or a valid provenance record establishes at most integrity, provenance or authenticity of what the state-keeper reports. It does not establish that the broker's reported state is true. The raw broker payload and its hash are retained so the chain reaches the broker's own message.
- **State-keeper trust limitation (C-14).** Stated in the executive verdict and here: if the state keeper is compromised or wrong, no property of this model holds. D23 and D24 are blockers for any broker contact or live-use claim.
- **State-keeper compromise (OPEN, D05, D23).** When the state-keeper is the only evidence source, the model *can* establish: the derived values are a reproducible function of the ledger; the ledger is internally consistent; changes to a log are detectable if a reference hash is held outside the state-keeper; replay is deterministic. It *cannot* establish: that any event is true or complete, that no event was omitted or fabricated, or that signed state is honest; there is no independent consistency check (NO_INDEPENDENT_EVIDENCE). v0.1 therefore states assumption A-7 plainly (the ledger is honest and complete as given) and does not remove it.
- **Key management (OPEN, D23).** Who holds signing keys, how they are rotated and revoked, and what happens on suspected compromise are not decided and not mandated here. Hypothesis [H]: the authority holds only a verification key; the strategy never holds a signing key; on suspected compromise the system fails closed (denies increases). These are labelled hypotheses, not implementation assumptions of v0.1.

- **Observed versus derived.** Observed evidence (2.2) is never recomputed. Every derived value is a pure function of (log, configuration, model version, as_of) and is reproducible; each evaluation record stores the item hash, ledger revision, configuration hash, master version, model version and references to every item used.

### 2.9 Reservation and compare-and-set semantics [R]

**Pure function** `evaluate(ledger_snapshot, proposal, config) -> Decision`. It never mutates, never reserves, and accepts no derived quantity from the caller. Decision fields (an internal evaluation record, R31-06A): proposal_hash, outcome (ALLOW, DENY, UNRESOLVED), derived values (F_min, F_max, B, S, U, A_raw, A, status, flags), failure codes, ledger_revision, item_hash, model_version, config_hash, evidence references, explanation.

**Commit layer** `commit(decision, store)`:
1. read revision R, items;
2. evaluate against exactly R;
3. **re-validate freshness (requirement E):** call the pure `evaluate` again with as_of = the commit time on the store's current ledger; proceed only if it returns ALLOW for the same proposal; this re-checks snapshot age against S_lim (D07) and every other freshness check at commit time, using the same pure function, so the commit layer decides nothing itself;
4. in one atomic step: if store.revision == decision.ledger_revision and item_hash matches and outcome == ALLOW and the decision's proposal_hash equals the hash of the proposal being committed and no reservation exists for proposal_id (the handling of an existing reservation for the same proposal_id is under *Reservation binding*, below) and (commit time - decision.as_of) <= D_max: append the reservation and the AUTHORIZED order (one record, counted once) and set revision = R + 1;
5. otherwise change nothing; if the revision moved, re-evaluate from step 1 (retry bound K, decision D09; exhausting K ends in DENY).

The commit layer never decides permissibility; it commits only a decision the pure function returned for the exact revision. A stale decision never becomes authority. Applying a broker event uses the same serializer and advances the revision.

**Minimum reservation record:** reservation_id (= order_id), proposal_id, proposal_hash, instrument, account, side, qty, evaluated_revision, committed_revision, decision hash, assumptions_in_force (below), created_at and expires_at (independent clock), state in {ACTIVE, CONSUMED (submitted), RELEASED (reject, cancel, fill complete), EXPIRED}.
**Lifecycle relation:** commit creates AUTHORIZED (reserves B or S). Submit consumes the token. Reject, cancel confirmation or expiry releases it. A fill reduces R through net_cum. An order that reaches the broker without a live reservation is detected as an unknown order and then counted (the window before detection is a residual risk, section 6).
**Valid evaluation versus committed reservation:** a Decision is an evaluation record only. Authority exists only when a reservation commit succeeds.
**Evaluation is internal and non-authorizing (R31-06A) [R].** The pure function `evaluate` and its Decision, including an outcome ALLOW and every derived value, are internal to the authority orchestration. They are stored in the evaluation record for audit and are **never returned to a proposer, strategy, caller or adapter as permission to act.** The only public operation is `authorize(proposal)`, which returns exactly one of: (a) a **CommittedReservation**, created only by a successful atomic commit (steps 1 to 5 above), carrying reservation_id, proposal_hash, the evaluated and committed revisions, the decision hash and the assumptions-in-force notice; or (b) a **Refusal**: a kind (DENY, UNRESOLVED, CONFLICT or COMMIT_FAILED) and reason codes, **and nothing else**. No object with outcome ALLOW leaves the orchestration other than a CommittedReservation. The diagnostic values F_min, F_max, B, S, U, A_raw and A are non-authoritative: no field of any returned object is a permitted quantity, the only quantity that can be authorized is the proposal's own Q and only by a successful commit, and no operation accepts A, A_raw or any derived value as input. No reservation, capability or permission is inferred from an evaluation result, including one whose outcome is ALLOW.
**Required behaviours:** duplicate commit of the same proposal (same proposal_id and proposal_hash) returns the existing reservation record in its current state with no second one; a repeated proposal_id with a different proposal_hash is a CONFLICT (R_PROPOSAL_CONFLICT); commit failure after a valid decision leaves no reservation and no authority; serializer or store unavailable means DENY.

**Reservation binding and proposal identity (G-A) [R].** proposal_id alone is never proposal identity. A reservation retains the proposal_hash it was committed against. A repeated proposal_id with an **identical** proposal_hash is a duplicate commit and returns the existing reservation record in its current state (ACTIVE, CONSUMED, RELEASED or EXPIRED; a record that is not ACTIVE confers no authority). A repeated proposal_id with a **different** proposal_hash is a CONFLICT: reason R_PROPOSAL_CONFLICT, refusal kind CONFLICT; the existing reservation is not returned, modified or consumed, and the new proposal is not committed under that id (V58).
**Consumption, payload binding and unknown submission outcome [R, model side].** A reservation is used for submission only through `consume(reservation_id, order_payload)`, one atomic compare-and-set on the store. It succeeds iff the reservation is ACTIVE and unexpired (independent clock) and the outgoing order's instrument, account, side and quantity equal the reserved proposal's exactly, checked at the moment of consumption and not when the token is first presented; it moves the state ACTIVE to CONSUMED (T04). A second consume of the same reservation, or one with any differing payload field, fails and changes nothing. If the adapter reports that the outcome of a submission is unknown (no acknowledgement or rejection, a disconnect, a lost response), the reservation stays CONSUMED, the order is SUBMITTED and then UNKNOWN under T19, R is kept at qty - net_cum, increases are blocked, and the model never releases R because time passed. A resend is not a second use of the same reservation (it would fail); it would need a new proposal and a new commit.
**Assumptions in force (R31-03') [R].** Every CommittedReservation carries the fixed notice: this result depends on A-2, A-6 (W1 to W7), A-7, A-11 and A-12 (2.11). The notice records hypotheses. **It is not evidence that any of them holds, has been verified, is continuously satisfied or is protected against failure**, and it must not be presented as a validation result.
**Boundary with the future adapter and G-07 (OPEN, not designed here).** Non-forgeable submission capabilities, broker client-order identifiers and the retry protocol, recovery of broker state after a lost acknowledgement, and broker-side duplicate-submission prevention belong to adapter and authorization design (G-07, D23, D24), not to v0.1. This model specifies only their accounting consequence (above) and requires that none of them accept a diagnostic value as authority. A committed reservation alone is **not** a complete broker submission authorization. The acceptance list for that future work is the adversarial tests of 5.7 (pre-commit ALLOW leakage, token replay, double consumption, proposal mutation, concurrent submission, timeout after submit, reservation expiry, proposal_id reuse).

**Revision coverage and time (F-6, D21) [R].**
- The revision counter increases on every change to the derived ledger: each log append that changes an item (applied event, new or resolved orphan or pending item, status change, OVER_RESERVED change), each reservation made, released or expired, each master version change, each configuration change. Duplicates that change nothing do not increase it. As a second line of defense every decision also records the **item hash** (items, master version, configuration hash), so a change the counter missed still fails the commit check.
- Passage of time is not a ledger change. The pure function takes an explicit **as_of** time from the independent clock; freshness is evaluated at as_of. The decision records as_of, and the commit rejects a decision when (commit time - as_of) exceeds **D_max** (parameter, value OPEN, D21). Without this a snapshot fresh at evaluation could be stale at commit with the revision unchanged. **Freshness is re-validated at commit (step 3 of the commit layer); S_lim is not extended by D_max.** D_max is an additional cap on the age of the *decision*, not an allowance on the age of the *snapshot*.
- Reservation expiry (TTL, D03) is itself an event recorded in the log at an independent-clock time (T05), so it is covered by the counter.

**Reason codes [R].** Decision reasons: R_BLOCK_UNKNOWN_ORDER, R_BLOCK_ORPHAN, R_BLOCK_STATUS, R_BLOCK_PENDING_REFERENCE, R_UNBOUNDED, R_EVIDENCE_FAILURE, R_OVER_RESERVED, R_EXCEEDS_A, R_EXCEEDS_LIMIT, R_MASTER_CHANGE, R_MALFORMED_PROPOSAL, R_FOREIGN_INSTRUMENT. Commit reasons: R_STALE_REVISION, R_DECISION_STALE, R_DUPLICATE, R_PROPOSAL_CONFLICT, R_STORE_UNAVAILABLE. Evidence codes are those of 2.8. A decision lists every applicable code.

### 2.10 Frozen numerical vectors (hand-calculated; not executed)

Unless stated: RECONCILED, single instrument, long-only, exposure limit L = 150. "Probe" decisions are a reduction (sell 10) and an increase (buy 10). Bounds are F_min and F_max of 2.4. "n/a" = UNBOUNDED, no bounds or values are computed. Codes use the reason-code set of 2.9. Where a vector exercises the oracle gap classes, the hand-derived oracle value is given and labelled.

| ID | Setup | F_min | F_max | U | A_raw | A | Probe: sell 10 / buy 10 | Codes |
|---|---|---|---|---|---|---|---|---|
| V01 | F=100, working sell 60 | 100 | 100 | 100 | 40 | 40 | ALLOW / ALLOW | none |
| V02 | F=100, working buy 20 | 100 | 100 | 120 | 100 | 100 | ALLOW / ALLOW | none |
| V03 | F=100, working buy 20 and sell 30 | 100 | 100 | 120 | 70 | 70 | ALLOW / ALLOW | none |
| V04 | F=100, working sell 120 (supplied ledger, not reachable by the authority) | 100 | 100 | 100 | -20 | 0 | DENY / DENY | R_OVER_RESERVED |
| V05 | F=100, working buy 20, fill 5: F=105, B=15 | 105 | 105 | 120 | 105 | 105 | ALLOW / ALLOW | none |
| V06 | F=100, working sell 30, fill 10: F=90, S=20 | 90 | 90 | 90 | 70 | 70 | ALLOW / ALLOW | none |
| V07 | Discrepancy, no orphan: F_d=70, F_b=65 at the same W (d=-5), MISMATCH, working sell 20 | 65 | 70 | 70 | 45 | 45 | ALLOW / DENY | R_BLOCK_STATUS |
| V08a | V07 plus orphan sell 5 (T1) known to be after W (T4) | 60 | 70 | 70 | 40 | 40 | ALLOW / DENY | R_BLOCK_STATUS, R_BLOCK_ORPHAN. Oracle A=40: tight |
| V08b | V07 plus orphan sell 5 (T1) with broker_seq <= W (T3, may already be in the snapshot) | 60 | 70 | 70 | 40 | 40 | ALLOW / DENY | same. Hand-derived oracle A=45: gap 5, class G1, accepted (D01) |
| V09 | withdrawn (it exercised H-LINK, not adopted) | | | | | | | |
| V10 | F=100, UNKNOWN sell 30, UNKNOWN buy 20 | 100 | 100 | 120 | 70 | 70 | ALLOW / DENY | R_BLOCK_UNKNOWN_ORDER |
| V11 | Orphan with no discrepancy: F=100, orphan buy 7 (T1) | 100 | 107 | 107 | 100 | 100 | ALLOW / DENY | R_BLOCK_ORPHAN |
| V12 | F=100, orphan of unknown side, quantity 7 (T1u) | 93 | 107 | 107 | 93 | 93 | ALLOW / DENY | R_BLOCK_ORPHAN |
| V13 | F=100, orphan of unknown quantity (T2-U) | n/a | n/a | n/a | n/a | n/a | UNRESOLVED / DENY | R_UNBOUNDED, R_BLOCK_ORPHAN |
| V14 | F=100, revision 7, two sell proposals of 60 evaluated on revision 7 | | | | | | first commits (revision 8, S=60); second fails the revision check, re-evaluates: A=40, 60 > 40, DENY; one reservation exists | R_STALE_REVISION, R_EXCEEDS_A |
| V15 | F=100, sell 60 CANCEL_PENDING | 100 | 100 | 100 | 40 | 40 | ALLOW / ALLOW | none. Fill first: F=40, S=0, A_raw=40. Cancel first (cum 0): F=100, A=100 |
| V16 | F=100, working sells 60 and 40; an earlier buy of 30 is busted: F=70 | 70 | 70 | 70 | -30 | 0 | DENY / DENY | R_OVER_RESERVED |
| V17 | Discrepancy d=+5: F_d=100, F_b=105, working buy 20 | 100 | 105 | 125 | 100 | 100 | ALLOW / DENY | R_BLOCK_STATUS. After applying the explaining 5-unit fill: F=105, B=15, RECONCILED: U=120, A_raw=105 (U falls, A_raw rises; I1 part 2) |
| V18 | F=100, working buy 20 | 100 | 100 | 120 | 100 | 100 | buy 30 ALLOW (U=150); buy 31 DENY | R_EXCEEDS_LIMIT |
| V19 | Duplicate execution report, identical content | no change | | | | | no change, no revision change | none |
| V20 | F=100, working buy 20, fill 8, cancel confirmed with cum 8 | 108 | 108 | 108 | 108 | 108 | ALLOW / ALLOW | none |
| V21 | F=100, sell 101 proposed | 100 | 100 | 100 | 100 | 100 | DENY (not clipped) | R_EXCEEDS_A |
| V22 | F=100, ambiguous event (T2), quantity 7 parseable | 93 | 107 | 107 | 93 | 93 | ALLOW / DENY | R_BLOCK_ORPHAN. Oracle also enumerates the "did not occur" world; bounds unchanged |
| V23 | F_d=100, F_b=105 (d=+5), orphan buy 5 (T1) with broker_seq <= W (T3) | 100 | 110 | 110 | 100 | 100 | ALLOW / DENY | R_BLOCK_STATUS, R_BLOCK_ORPHAN. Hand-derived oracle U=105: gap 5, class G1 |
| V24 | As V23, orphan has broker_seq > W (T4) | 100 | 110 | 110 | 100 | 100 | ALLOW / DENY | same. Hand-derived oracle U=110: tight |
| V25 | Relationship unproven: F_d=70, F_b=65, orphan sell 5 with no broker_seq, working sell 20 | 60 | 70 | 70 | 40 | 40 | ALLOW / DENY | R_BLOCK_STATUS, R_BLOCK_ORPHAN. Oracle A=min(40 for T4, 45 for T3)=40 |
| V26 | Duplicate delivery of exec E1 (buy 10 of a buy 20): F=100, R=10 | 100 | 100 | 110 | 100 | 100 | ALLOW / ALLOW | none. Second delivery: no change, duplicate counter 1, revision unchanged |
| V27 | Same event_id, conflicting content: E1 applied (buy 10); E1 arrives again with quantity 12 | | | | | | UNRESOLVED / DENY | R_EVIDENCE_FAILURE (Consistency INCONSISTENT), R_BLOCK_UNKNOWN_ORDER. Order UNKNOWN; bounds diagnostic only |
| V28 | Gap below the watermark: events 501 and 503 applied, 502 missing, snapshot W=503 | n/a | n/a | n/a | n/a | n/a | UNRESOLVED / DENY | R_UNBOUNDED, R_BLOCK_STATUS (GAP). When 502 arrives and F_d(503)=F_b: RECONCILED |
| V29 | Snapshot ahead: highest applied 502, snapshot qty 65 at W=504, F_d(502)=70 | n/a | n/a | n/a | n/a | n/a | UNRESOLVED / DENY | R_UNBOUNDED, R_BLOCK_STATUS (AWAITING-BEHIND, D18). After 503 and 504 arrive and F_d(504)=65: RECONCILED |
| V30 | Bust after a terminal state: buy 100 FILLED by E1 from F=0; E1 busted | 0 | 0 | 0 | 0 | 0 | DENY / ALLOW | R_EXCEEDS_A. History keeps FILLED plus a BUST record; net_cum=0; R=0 (no resurrection); F_d=0 |
| V31 | Correction naming an unknown execution X99 | n/a | n/a | n/a | n/a | n/a | UNRESOLVED / DENY | R_UNBOUNDED, R_BLOCK_PENDING_REFERENCE. Held pending until X99 arrives or the broker resolves it |
| V32 | Late fill after cancellation: F=100, sell 60 CANCELED (cum 0, confirmed); then execution sell 5 for that order arrives | 95 | 100 | 100 | 35 | 35 | UNRESOLVED / DENY | R_EVIDENCE_FAILURE, R_BLOCK_UNKNOWN_ORDER (bounds diagnostic). Order UNKNOWN with R=60, execution pending. After authoritative resolution (CANCELED, cum 5): F=95, R=0, A=95 |
| V33 | Reservation expiry: F=100, sell 60 AUTHORIZED (S=60, A=40); TTL passes | 100 | 100 | 100 | 100 | 100 | ALLOW / ALLOW | none. T05 releases R; revision + 1 |
| V34 | Late broker ack for the expired order of V33 | 100 | 100 | 100 | 40 | 40 | ALLOW / DENY | R_BLOCK_UNKNOWN_ORDER. T22: order UNKNOWN, R=60 re-reserved, no evidence failure |
| V35 | Master semantic change (class B, symbol mapping): F=100, sell 60 AUTHORIZED unsubmitted, sell 20 working at the broker | n/a | n/a | n/a | n/a | n/a | UNRESOLVED / DENY | R_MASTER_CHANGE, R_UNBOUNDED. The authorized sell expires (S: 80 to 20); status UNKNOWN until reconciled under the new version. After: F=100, A=80, ALLOW / ALLOW |
| V36 | Two simultaneous buys of 30 on the same revision, F=100 | | | | | | first commits (B=30, U=130); second fails the check, re-evaluates: U+30=160 > 150: DENY | R_STALE_REVISION, R_EXCEEDS_LIMIT |
| V37 | Buy 30 and sell 60 evaluated concurrently, F=100 | | | | | | one commits; the other retries and is ALLOW either way (buy first: A_raw=100; sell first: U=130). Cost: one retry, not a denial (D04) | R_STALE_REVISION on the retried one |
| V38 | Normal AWAITING: S0 qty 100 at W=500; E501 buy 20, E502 sell 50 applied: F_d=70, no new snapshot | 70 | 70 | 70 | 70 | 70 | ALLOW / ALLOW | none. Snapshot qty 70 at W=502 then gives RECONCILED |
| V39 | Intervening fill: F=100, working sell 30 (A=70); sell 60 evaluated on revision 7 (ALLOW); the sell 30 fills (F=70, S=0, revision 8) before the commit | 70 | 70 | 70 | 70 | 70 | commit rejected; re-evaluated on revision 8: A=70, ALLOW, new decision bound to revision 8 | R_STALE_REVISION |
| V40 | UNKNOWN event between evaluation and commit: buy 30 evaluated ALLOW on revision 7; an UNKNOWN order appears (revision 8) | | | | | | commit rejected; re-evaluated: DENY | R_STALE_REVISION, R_BLOCK_UNKNOWN_ORDER |
| V41 | Duplicate commit of the same decision | | | | | | second attempt returns the existing reservation; no second reservation; revision advanced once | R_DUPLICATE |
| V42 | Commit failure after a valid decision: store unavailable | | | | | | no reservation and no authority; the order may not be submitted | R_STORE_UNAVAILABLE |
| V43 | Partial fill then cancellation: F=100, sell 60 working; fill 20; cancel confirmed with cum 20 | 80 | 80 | 80 | 80 | 80 | after the fill: F=80, S=40, A_raw=40 (unchanged, I1b); after the cancel: S=0 | none |
| V44 | Decision age and commit-time freshness: evaluation with a snapshot younger than S_lim; at commit time the snapshot is older than S_lim (or the decision older than D_max), with no ledger change | | | | | | commit rejected: the re-evaluation at commit time returns STALE or D_max is exceeded; **a snapshot older than S_lim fails even when the decision age is within D_max** | R_DECISION_STALE |
| V45 | Release after confirmed rejection: F=100, buy 20 AUTHORIZED, SUBMITTED, REJECTED (cum 0) | 100 | 100 | 100 | 100 | 100 | ALLOW / ALLOW | none. B back to 0 |
| V46 | V01 base plus an earlier applied sell of 5 (seq 90 <= W) and a committed reduction of 40 (S = 100, A_raw was 0); a correction (own seq 110 > W) raises the sold amount to 7: F = 98, F_d(100) unchanged, d = 0 | 98 | 98 | 98 | -2 | 0 | DENY / DENY | R_OVER_RESERVED. Prior authorization invalidated in effect (I8); no new authorization possible; who cancels is G-07 |
| V47 | S0 qty 100 at W = 500; E501 buy 20, E503 sell 50 applied, E502 (buy 10) missing; snapshot W = 503, F_b = 80. Then E502 arrives | before: n/a; after: 80 | 80 | 80 | 80 | 80 | before: UNRESOLVED / DENY; after: ALLOW / ALLOW | before: R_UNBOUNDED, R_BLOCK_STATUS (GAP); after: none |
| V48 | As V47 before E502 arrives, and a later snapshot W = 510, F_b = 80 arrives while sequence 502 is still missing | n/a | n/a | n/a | n/a | n/a | UNRESOLVED / DENY | R_UNBOUNDED, R_BLOCK_STATUS (GAP persists; a later snapshot never clears it) |
| V49 | Execution E1 (buy 5) applied; correction C1 (prior_version 0, prior_qty 5, replacement 4, seq 201) and C2 (prior_version 0, prior_qty 5, replacement 3, seq 202), each valid alone. Log order C1, C2 | n/a | n/a | n/a | n/a | n/a | UNRESOLVED / DENY | R_EVIDENCE_FAILURE (C2 names a prior version that is no longer current after C1: structural conflict, D27). Reversed log order applies C2 and conflicts C1: outcomes depend on log position, by design (D20) |
| V50 | Reconnect resends E3 to E5, already applied | unchanged | unchanged | unchanged | unchanged | unchanged | unchanged | none. No revision change; duplicate counters only |
| V51 | F_base = 95 (all seq <= W = 100); one applied buy of 5 with no broker_seq (F_d = 100); snapshot W = 100, F_b = 100; no orders. Interpretations: inside F_d(W): d_1 = 0; outside: d_2 = +5 | 100 | 105 | 105 | 100 | 100 | ALLOW / DENY | R_BLOCK_STATUS (MISMATCH; d_plus = max(0, 0, 5) = 5, d_minus = max(0, 0, -5) = 0) |
| V52 | Proposals with qty True, 1.0, "1", -0, 10^30 (above Q_MAX), NaN, side "BUY " | n/a | n/a | n/a | n/a | n/a | DENY for every one; never ALLOW; no exception escapes | R_MALFORMED_PROPOSAL |
| V53 | F_d = 70; discrepancy supplied as magnitude 5 only; working sell 20 | 65 | 75 | 75 | 45 | 45 | ALLOW / DENY | R_BLOCK_STATUS (d_plus = d_minus = 5) |
| V54 | Snapshot with qty -3 in the long-only envelope | n/a | n/a | n/a | n/a | n/a | UNRESOLVED / DENY | R_EVIDENCE_FAILURE (Consistency INCONSISTENT: envelope violation) |
| V55 | Bust naming an unknown original X77 | n/a | n/a | n/a | n/a | n/a | UNRESOLVED / DENY | R_UNBOUNDED, R_BLOCK_PENDING_REFERENCE |
| V56 | **Uncovered failure, documented limitation.** True position 100 after buy E1 of 10; the broker re-sends E1 under a different event id and exec_id; both applied: F_d = 110; working sell 60 | 110 | 110 | 110 | 50 | 50 | The model ALLOWs sell 50. True A = 100 - 60 = 40, so **false permission of 10 units** | none: not detected (A-11, A-12). A later snapshot F_b = 100 gives d = -10: F_min = 100, A_raw = 40. A known limitation, never a passing result |
| V57 | **D19 preconditions stated (R31-05').** F_base = 100 (sequenced applied executions, broker_seq <= W); two applied executions with no broker_seq, s_1 = +4 and s_2 = -2, so F_d = 102; snapshot W, F_b = 100; no orders. The four inclusion choices give d = {0, -4, +2, -2}, so d_plus = 2 and d_minus = 4. All five D19 preconditions hold: valid watermark and contiguous events through W; no structural evidence failure and no pending correction or bust; unsequenced executions handled by the 2.2 interval; snapshot fresh at evaluation and again at commit and decision age within D_max; long-only, sell within A | 98 | 104 | 104 | 98 | 98 | ALLOW / DENY | R_BLOCK_STATUS (the buy is blocked by the MISMATCH status, not by the limit: 104 + 10 <= 150). Cross-check under W1-T, P = F_b + the excluded unsequenced executions: 102, 98, 104, 100, so the minimum 98 and the maximum 104 equal F_min and F_max |
| V58 | **Proposal identity (G-A).** F = 100, no orders. Proposal P-17 (buy 10) is committed: reservation ACTIVE, B = 10. P-17 then arrives again with identical content, and again as a sell of 10 (a different proposal_hash) | 100 | 100 | 110 | 100 | 100 | P-17 buy 10 again: the existing reservation is returned, no second one. P-17 sell 10: refused, CONFLICT | R_DUPLICATE (same hash). R_PROPOSAL_CONFLICT (different hash): the existing reservation is not returned, modified or consumed |
| V59 | **Identity-changing correction (D26, Option A).** V01 base (F = 100, working sell 60); execution E1 (buy 10, order O1) applied. A CORRECT for E1 (prior_version 0, prior_qty 10, qty 10) restates side = sell. The same result if it restates order O2, or a non-canonical instrument | n/a | n/a | n/a | n/a | n/a | UNRESOLVED / DENY | R_UNBOUNDED, R_EVIDENCE_FAILURE, R_BLOCK_PENDING_REFERENCE (the CORRECT is not applied; E1 stays at version 0; held pending; increases and reductions blocked until an authoritative broker response) |
| V60 | **Valid correction (D27).** F_d = 100 including E1 (buy 10, version 0, broker_seq 90 <= W = 100); snapshot W = 100, F_b = 100; no orders. CORRECT C1 (own broker_seq 110 > W) restates instrument, side and order unchanged, prior_version 0, prior_qty 10, replacement qty 8 | 98 | 98 | 98 | 98 | 98 | ALLOW / ALLOW | none. The effect is 8 - 10 = -2 on F_d (F_d = 98); F_d(100) = 100 is unchanged because C1's own seq is above W, so d = 0 and the status is AWAITING; E1 is now version 1 with qty 8 |
| V61 | **Incomplete correction (D27).** As V60 but the CORRECT omits prior_version and prior_qty | n/a | n/a | n/a | n/a | n/a | UNRESOLVED / DENY | R_UNBOUNDED, R_BLOCK_ORPHAN (malformed: not applied to the current version, held as an orphan of unknown quantity; nothing is silently applied) |
| V62 | **Newer snapshot, still mismatched (R31-07').** V07 base (F_d = 70, F_b = 65 at W = 100, d = -5, MISMATCH, working sell 20). A later snapshot arrives: W' = 110, F_b' = 60, events contiguous through 110, no execution applied (F_d(110) = 70), no orphan present | 60 | 70 | 70 | 40 | 40 | ALLOW / DENY | R_BLOCK_STATUS. d' = 60 - 70 = -10 replaces d = -5 (it is not added to it): d_minus = 10, F_min = 70 - 10 = 60, A_raw = 60 - 20 = 40. The status stays MISMATCH: a newer accepted snapshot is not a reconciled one, and an unapplied orphan, had one existed, would remain an item |

Vectors V46 to V56 were added in Revision 3. Hand-derived, not executed; V56 records a failure the model cannot prevent. Vectors V57 to V62 were added in Revision 3.1 (V57 the unsequenced interval with n = 2 and the D19 preconditions; V58 G-A; V59 D26; V60 and V61 D27; V62 R31-07'); V49 was restated with the D27 fields. All hand-derived, not executed.

### 2.11 Assumptions and their classification [R to state, not to resolve here]

Classes: **M** mathematically required, **E** environmental hypothesis, **I** implementation requirement, **O** operational dependency, **D** deferred. A broker-environment hypothesis is never to be read as a mathematical fact.

| ID | Assumption | Class | Failure could cause permission that would otherwise be denied |
|---|---|---|---|
| A-1 | Single instrument | M (scope) | low: foreign ids are quarantined |
| A-2 | **Input contract:** where broker_seq is present it is one monotone sequence per account, and a watermark W means the snapshot contains exactly the executions with broker_seq <= W (absent sequence numbers mean unknown timing). Not established for any real broker | **E** | yes |
| A-3 | The store provides atomic compare-and-set | I | yes |
| A-4 | An independent clock exists | O | yes |
| A-5 | The future adapter submits only with a live reservation token, consumed against the exact reserved payload (2.9) | O | yes |
| A-6 | W1 to W7 (section 2.3), hypotheses about the modeled broker environment | **E** | yes |
| A-7 | The state keeper's ledger is honest and complete as given (trust mechanism open, D05, D23, D24) | O | yes |
| A-8 | Q_MAX, L, TTL, K, D_max and the staleness and wait limits are configuration, pinned by hash and identified like TierConfig | I | low |
| A-9 | The pure functions receive the as_of time as an explicit input from the independent clock; at commit the same function is called again with the commit time | I | low |
| A-10 | The master version id and content hash are supplied as evidence | I | low (fails closed) |
| A-11 | Events carry stable event ids (otherwise the hash of canonical content). **Idempotency by event ID does not establish economic-execution uniqueness**; a duplicate economic execution under a different id is uncovered | **E** | yes (V56) |
| **A-12** | **Event delivery is complete between snapshots, except for unreported fills of known working orders (W4).** Snapshot freshness and decision age do **not** establish it; no formula covers its failure; a later snapshot can only reveal a failure after the fact; a failure can invalidate reduction permission in every status, including RECONCILED (R31-03') | **E** | **yes** |
| A-13 | Integers only; no floating-point quantity enters accounting | M | none |
| A-14 | CORRECT events supply instrument, side, order association, prior_version, prior_qty and qty (input contract, D27). An incomplete or identity-changing correction is not applied and is UNBOUNDED (D26) | **E** (input contract) | no (fails closed; availability cost) |

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

### 3.2.1 Decisions D26 and D27 (founder, 2026-11-23)

Both arose from the GPT hostile reviews of Revision 3 (gaps G-C and G-D). The founder's words were "i accept the recommendation" (Option A for G-C) and "i approve the 5 requirements" (G-D); the approval column records them as Claude's reading, open to founder correction. Founder approval is not verification.

| ID | Decision | Position | Founder approval | Closing evidence |
|---|---|---|---|---|
| D26 | CORRECT that changes side, order association or instrument | Option A: structural evidence failure; not applied; held pending; band UNBOUNDED; increases and reductions blocked until authoritative resolution; no quantity transferred between orders or instruments. Options B (reversal plus replacement) and C (enumerate both interpretations) are not adopted in v0.1 and are future research items after executed evidence | Approved (2026-11-23, as read by Claude) | V59; an oracle run showing UNBOUNDED for such ledgers; the availability cost measured |
| D27 | Correction contract | A CORRECT (1) references an existing execution; (2) identifies the exact prior version replaced (prior_version, prior_qty); (3) supplies the replacement quantity; (4) a stale or mismatched prior version is a structural conflict; (5) no ambiguous correction is silently applied to the current version (an incomplete one is malformed, T2-U). A side, order or instrument change goes to D26 | Approved (2026-11-23, as read by Claude) | V49, V60, V61; replay tests of non-commuting corrections |

### 3.3 Deferred OPEN decisions (do not block the v0.1 reference model)

| ID | Decision | Options | Recommendation | Consequences | Blocks implementation | Founder approval |
|---|---|---|---|---|---|---|
| D23 | Signing-key holder, rotation, revocation, response to suspected compromise | Not decided | Decide before any broker contact; hypothesis: authority holds only a verification key, fail closed on suspected compromise | v0.1 states A-7 instead | No (blocks any broker contact) | Yes, later |
| D24 | Independent evidence required for any future live use; whether NO_INDEPENDENT_EVIDENCE is tolerated outside reductions in a first replay | Not decided | Require a second read-only channel for live use | v0.1 cannot test common-mode failure | No | Yes, later |
| D25 | Master owner, review frequency, maximum master age | Not decided | Owner = founder; frequency and age after the first replay | Not needed for a single fixed instrument | No | Yes, later |

## 4. Executable-model plan (Deliverable C). Not implemented.

Small and bounded. Pure Python, standard library only, no network, no broker adapter, no clock or randomness inside pure functions, no import from `sentinel_core*`.

**Module boundaries**
- `exposure_model/types.py`: frozen dataclasses with exact-type validation (no bool as int, no floats): `Order`, `Execution`, `SnapshotEvidence`, `OrderEvent`, `Proposal`, `Config` (L, Q_MAX, TTL, K, D_max, staleness and wait limits; pinned by hash), `Ledger`, `Decision` (an internal evaluation record), `Reservation`, `CommittedReservation`, `Refusal`.
- `exposure_model/log.py`: the append-only, hash-chained event log and canonical serialization (sorted keys, integers only, UTF-8). `apply_event(ledger, log_entry) -> Ledger` is pure and implements 2.6 (lifecycle, idempotency, pending items, orphan items, statuses).
- `exposure_model/accounting.py`: `derive(ledger, config, as_of) -> Accounting` (F_d, F_d(W), d, F_min, F_max, B, S, U, A_raw, A, status, BOUNDED, flags, evidence results). One formula set, the one in 2.4.
- `exposure_model/authority.py`: `evaluate(ledger, proposal, config, as_of) -> Decision`; no caller-supplied derived values, no mutation, no reservation. Internal: not exported to callers or the adapter (2.9).
- `exposure_model/store.py`: the only stateful module: `read()`, `commit(decision)` (which re-calls the pure `evaluate` with as_of = commit time, 2.9), `apply(log_entry)`, serialized, with the compare-and-set of 2.9, in-memory only, a deterministic scheduler for tests (no threads). The public operations are `authorize(proposal) -> CommittedReservation | Refusal` and `consume(reservation_id, order_payload)` (2.9); no operation returns a Decision or a diagnostic value.

**Immutable data structures.** Tuples and frozen dataclasses; the item list is a canonical, sorted tuple; item_hash = SHA-256 of its canonical serialization plus master version and configuration hash.

**Event and execution ledger representation.** Orders keyed by order_id with the append-only lifecycle history and a derived net_cum; executions keyed by exec_id with kind NEW, CORRECT or BUST and reference; orphan and pending items keyed by event_id; snapshot evidence keyed by snapshot_id; every entry carries its log position, raw_hash and, if present, broker_seq.

**Failure and reason-code representation.** An enumeration of the reason codes of 2.9 and the evidence codes of 2.8; a Decision carries the full list of applicable codes, never a single "error".

**Test organization**
- `tests/test_vectors.py`: frozen vectors V01 to V62 loaded from data files, with their hand derivations.
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
4. for each working order with remaining quantity R: every **integer** unreported fill x in {0, 1, ..., R} (A-13), each with every placement permitted by W4 (before W or after W). Choices for distinct working orders are independent and are combined as the **full Cartesian product**; no sampling or independence shortcut may stand in for it in a run described as exhaustive over the declared domain (R31-08).
For each world it computes P by the world values in 2.3, then U_w and A_w. U_oracle = max over worlds of U_w; A_oracle = min over worlds of A_w. The model is **sound** on a ledger iff U >= U_oracle and A_raw <= A_oracle. The gaps U - U_oracle and A_oracle - A_raw are reported per ledger and attributed to class G1 (T3 item counted twice), G2 (unreported fill at or before W counted twice), G3 (known-side orphan not credited against the opposite bound), or UNEXPLAINED. Any UNEXPLAINED gap, and any soundness violation, is a counterexample and is reported with its minimal reproduction.
**Safeguards (C-11).** (1) The world semantics (2.3) are frozen before the oracle is written; (2) the oracle derives from raw ledger facts, never from model-derived fields; (3) it imports no model type, formula, helper or normalizer; (4) it uses a distinct ledger representation (raw-fact JSON); (5) it enumerates admissible worlds directly; (6) hand-derived examples include ones neither implementation generated, authored by a reviewer where possible; (7) GPT and Gemini challenge the oracle's assumptions and expected results; (8) counterexamples and failed tests are preserved permanently; (9) the oracle's source hash is recorded before it sees any model output; (10) where feasible a reviewer derives a small oracle from the specification without seeing this one.
**Three separate comparisons (C-11).** (a) *Bound soundness*, bounded cases only: U >= U_oracle and A_raw <= A_oracle, on the raw numbers, A_raw of any sign. (b) *Decision soundness*: ALLOW of an increase Q implies U_oracle + Q <= L; ALLOW of a reduction Q implies 1 <= Q <= A_oracle, so with A_oracle < 0 nothing may be allowed. **False permission is a violation of (b).** (c) *Flag soundness*: A_oracle < 0 implies OVER_RESERVED is raised; a ledger the oracle reports UNBOUNDED must resolve to UNRESOLVED or DENY in the model. Excessive conservatism (the model denies what the oracle would allow, or U exceeds U_oracle) is availability cost, classified G1, G2 or UNEXPLAINED, and is never counted as a safety defect; it is reported separately. Negative A_raw is a diagnostic, never an available quantity.
Hand-calculated vectors (V01 to V62) are the second, formula-free anchor.
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
- Event sequences (C-01): single order, all sequences of length 1 to 4 over the **11** event types named here: E04, E05, E06, E07, E08, E09, E12, E13, E14, E16, E17. The count is 11 + 11^2 + 11^3 + 11^4 = 11 + 121 + 1,331 + 14,641 = **16,104** sequences, before parameter choices and before the validity filter (EXECUTED arithmetic, Python integers; 14,641 is the length-four count alone). No twelfth event is added: E11 (status UNKNOWN) and E15 (execution out of order) are existing events not in this list; they are exercised by the UNKNOWN order states and the GAP status of the ledger enumeration instead, and are recorded as declared exclusions from the sequence enumeration. At most one applied execution with no broker_seq is generated per ledger (a declared bound). **The static grid therefore does not cover more than one unsequenced applied execution (R31-05'); that case is covered by V57 and by the generative tests of 5.3, and the grid's other declared limits (at most one orphan, at most two orders) are listed among its excluded combinations.**
- World enumeration per ledger is at most a few hundred worlds; the number is the integer product of 5.1 and is reported (5.7). If the full run is not feasible in the available time, any sampling must be declared **before** running and the result is then not called exhaustive.
- **Counts kept separate (C-01):** generated states; valid states; excluded states (with reasons); evaluated proposals (valid states x proposals x L); distinct event sequences (after removing duplicates and invalid prefixes); CAS schedules (interleavings per scenario times scenarios); test executions after deduplication (identical canonical ledger and proposal hash removed). A Cartesian-product bound is never presented as the number of valid or meaningful cases.
- **Coverage report columns (C-02):** false permissions; false denials of legitimate reductions; false denials of legitimate increases; correct denials; unbounded outcomes; structural evidence failures; invariant violations; oracle disagreements; excluded combinations; generation bias; duplicate or redundant cases; runtime and resource consumption.
- Reported on completion: total states and cases, invariants checked, counterexamples (with minimal reproduction), excluded combinations (more than one orphan, more than two orders, quantities > 3, negative positions, multiple instruments, more than one snapshot), generation bias (small quantities, single orphan, no interleaved busts), whether every transition class (E01 to E23) and every uncertainty class (2.7 rows, T1 to T4) was reached.
- Safety and availability measured separately: false permission (must be 0 for soundness), false denial of a legitimate reduction, false denial of a legitimate increase, correct denial when evidence is insufficient. "Legitimate" is defined by the oracle's worlds. The G1 and G2 gaps are reported as availability cost, not as defects (D01). A model that denies everything fails the availability metrics.
- What it can establish: "exhaustive over the declared finite state space and assumptions". It does not prove the architecture or the system safe. **Zero false permissions in the declared space cannot establish safety against conditions excluded from W1 to W7** (requirement C): undelivered events, duplicate economic executions, wrong-side association, a false state keeper. A model that denies everything fails the availability metrics.

### 5.3 Property-based and generative tests
Random ledgers beyond the enumeration bounds (larger quantities, more orders, up to 6 events) with a fixed seed recorded; checked against the oracle where world enumeration is tractable, and against invariants I1a to I9 elsewhere. Shrinking to a minimal counterexample on failure.

### 5.4 Concurrency and CAS simulation
Deterministic scheduler, no threads: each proposer is a sequence (read, evaluate, commit), each broker event is one step. All interleavings are enumerated; **Every scenario declares its own steps, precedence constraints and admissible interleavings, and its schedule count is generated from those declarations by the scheduler, never asserted from a formula or inferred from the number of steps (G-E).** Examples of integer arithmetic (EXECUTED): two proposers of three steps each plus one independent broker event give 7!/(3! 3! 1!) = 140 schedules; with two independent broker events, 8!/(3! 3! 1! 1!) = 1,120; when the second event must follow the first (a partial fill and then its cancel confirmation), 8!/(3! 3! 2!) = 560. The scenarios of dispatch section 8, each with its own declaration (two sells of 60; two buys; buy and sell; fill, cancel confirmation or UNKNOWN between evaluation and commit; stale replay; duplicate commit; reservation expiry; release after reject or cancel; partial fill then cancel; commit failure after a valid decision). Check I2 and I5 after every schedule: total committed sell reservations never exceed A at their commit revision.

### 5.5 Frozen vectors, reproduction, artifacts
Frozen vectors V01 to V62 stored as data with hand derivations. Reproduction: one command, fixed seeds, pinned Python version, hash of the spec, model, oracle and config printed on every run. Preserve: spec hash, source hashes, bounds file, full result JSON, counterexample list, interleaving traces, environment (Python version, OS). A reviewer reproducing the run is labelled "reproduced", never "independently verified" unless the reviewer wrote the oracle without seeing the model.

**Reporting format and claim levels (R31-10) [R].** Every report of a run, a review or a reproduction states five claims separately and never collapses them into one label such as "verified": (1) *specification consistency* (the equations and definitions cohere); (2) *hand-vector agreement* (independent readers derive the same values for selected examples); (3) *oracle correctness* (the oracle enumerates and evaluates all declared worlds correctly); (4) *model soundness* (model bounds and decisions agree with the oracle over the declared test space); (5) *external validity* (the declared world model describes a real broker environment). In Revision 3.1 only claims 1 and 2 have any support, and both rest on hand derivations by reviewers and one author; claims 3, 4 and 5 are not established.

### 5.6 Replay, idempotency, serialization, counterexamples, reproduction, evidence

- **Replay and idempotency.** For every enumerated event sequence and every generated log: (a) fold the log twice and compare the SHA-256 of the canonical serialization of the ledger and of every decision; (b) inject a duplicate of each event at every position and check the ledger is unchanged; (c) re-serialize and re-parse the log and check equality. Order-invariance is tested only for sets of non-conflicting executions and is reported as limited.
- **Same-id conflict and malformed input.** Every event type with a conflicting duplicate, a malformed field, an out-of-range quantity, a wrong instrument, and a missing sequence number must yield the codes and statuses of 2.6 and 2.8, never an exception and never a pass.
- **Counterexample reporting.** Every failed invariant, soundness violation or UNEXPLAINED gap is written with the minimal ledger or event sequence that reproduces it, the oracle's worlds that expose it, and the model's values. A run with zero counterexamples is reported as "none found in the declared state space", never as a proof.
- **Reproduction.** One command, fixed seeds, pinned Python version, printing the SHA-256 of the specification, the model and oracle sources, the vector files, the configuration and the bounds file.
- **Evidence artifacts to preserve.** The specification hash; source hashes; frozen vectors with derivations; the bounds file; full result JSON; counterexample list; interleaving traces; replay hashes; environment (Python version, OS); the reviewer's reproduction record.
- **What this could establish.** Over the declared finite state space and the world model W1 to W7: soundness of the sum rule against the oracle; the measured over-denial (G1, G2, G3); that I1a to I9 hold in the enumerated cases; that decisions are deterministic and idempotent; that no concurrency interleaving in the declared set over-reserves.
- **What it could not.** Truth or completeness of broker data; the world model's fit to any real broker; behavior outside the bounds; implementation correctness of anything other than this model; trading or financial performance; independence, unless a reviewer writes or re-derives the oracle without seeing the model.

### 5.7 Pre-enumeration prerequisites [R] (R31-09', G-E)

None of these is authorization to code. They are the minimum specification and plan maturity required before the founder is asked whether to authorize the bounded executable reference model.
1. **One controlled revision.** The amendments are applied together (this revision) and survive the targeted final review.
2. **Correction semantics frozen.** D26 and D27 as specified (2.2, 2.6, V49, V59 to V61); no event class whose meaning the model and the oracle would both have to guess.
3. **Oracle domain and validity predicate frozen before any run.** The oracle domain is 5.1 (R31-08). The validity predicate decides, for every generated candidate, whether it is a valid ledger state and, if not, which rule excludes it (malformed input, unreachable state, conflicting history, declared envelope exclusion). Every exclusion is counted and reported with its reason, so the harness cannot silently filter difficult cases.
4. **Test-obligation matrix.** A table mapping each obligation to its test family and to the evidence that the test *reaches and exercises* it (a test that merely references a transition does not count): each event E01 to E24; each lifecycle transition T01 to T22, including invalid and late transitions; each row of the uncertainty inventory (2.4.2); each block condition (increases and reductions tested separately); each invariant I1a to I9 (assertion and counterexample report); each oracle world choice (worlds generated, evaluated, excluded and compared); each registered failure F, N and V; each structural evidence failure (code, state, permission behavior); each CAS scenario.
5. **Three spaces reported separately:** ledger and world space; event and replay space; concurrency and schedule space. A count in one says nothing about coverage in another.
6. **CAS schedule-construction rules** (5.4): per scenario, the declared steps and precedence and the constructed, executed and excluded schedule counts with reasons.
7. **Oracle-domain report for every run:** per-order fill domain, placements, Cartesian product size, worlds generated, evaluated and excluded (with reasons), and whether the model's bounds were compared with the oracle for every valid ledger. A run that samples the product is called sampled, not exhaustive.
8. **Adversarial authority tests** as the acceptance list for the adapter boundary (2.9): pre-commit ALLOW leakage, token replay, double consumption, proposal mutation, concurrent submission, timeout after submit, reservation expiry, proposal_id reuse with different content (V58).
9. **Targeted review of the test plan** against the final specification, by a reviewer other than its author where one exists.

---

## 6. Residual-risk register (explicit)

| Class | ID | Risk |
|---|---|---|
| Mathematical | M-1 | The sum rule and the soundness derivations (2.3, 2.4.1) are one-author hand derivations; soundness is relative to W1 to W7; tightness is measured, not asserted; G1, G2 and G3 over-denial is accepted (D01, widen-only principle) |
| Mathematical | M-2 | D19 is a specification candidate: its safety rests on the world model and on five preconditions; zero false permissions in a declared test space does not extend to excluded conditions |
| Mathematical | M-3 | The interval construction for unsequenced applied executions (2.2) is exact over the modeled inclusion choices only; it is a Revision 3 addition and has had no independent review |
| Mathematical | M-4 | The Revision 3.1 additions (the correction contract D26 and D27, the snapshot replacement rule of 2.6.2, the proposal binding and consumption rules of 2.9) are one-author hand derivations and have had no independent review beyond the adjudicated hand reviews of Revision 3 |
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
| Operational | O-4 | The adapter and G-07 boundary (2.9): non-forgeable capabilities, client order ids, the retry protocol and recovery after a lost acknowledgement are not designed; the model specifies only the accounting consequence of an unknown submission; a committed reservation alone is not a complete broker submission authorization |
| Scope | S-1 | G-04 (limit L), G-06 (protective intervention for the UNBOUNDED case) and G-07 (cancellation and override authority) remain open and outside v0.1 |
| Validation | V-1 | No model, oracle, enumeration, CAS suite or independent reproduction exists; the pre-enumeration prerequisites of 5.7 are not yet produced |

## 7. Stop/go recommendation (Deliverable E)

**Status: REVISION 3.1 FROZEN FOR TARGETED FINAL REVIEW** (Revision 3 was frozen for hostile review; the reviews of it are adjudicated and incorporated here). D02 and D17 to D22 are recorded (3.2; D19 only as a conditional candidate). Every rule needed to build a small reference model and an independently structured oracle is stated: equations, worlds and their limits, statuses, lifecycle effects, the uncertainty inventory, events, the block matrix, reason codes, invariants, and 56 hand vectors.

**NO-GO for implementation.** The targeted final review of Revision 3.1 is not done; no claim has been executed or independently reviewed (the reviews of Revision 3 were hand-derived); the founder has not authorized the bounded executable reference model. The detail of the specification is not a reason to implement.

**Exact implementation boundary if later approved:** `exposure_model/` (types, log, accounting, authority, in-memory store) and a separately structured `exposure_oracle/`, pure Python standard library, deterministic scheduler, no broker adapter, no network, no clock or randomness inside pure functions, no change to `sentinel_core*`, parameter values (TTL, K, D_max, S_lim, limits) as test parameters only, and the enumeration bounds of 5.2 declared before any run.

## 8. Sequence and next action
1. Decisions D02 and D17 to D22 recorded (3.2); D26 and D27 recorded (3.2.1).
2. Revision 3 frozen and reviewed (Gemini; GPT, two passes); the reviews adjudicated.
3. Revision 3.1 drafted and frozen; its full-file SHA-256 is computed from the delivered bytes and published with the delivery.
4. Targeted final review of the complete Revision 3.1 file, sent as the actual file text.
5. Pre-enumeration prerequisites (5.7) produced and reviewed.
6. Only after that: the founder decides whether to authorize the bounded executable reference model.
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
| N-12 | Commit keyed by proposal_id alone: a reused id with different content could return an existing reservation (G-A) | GPT (review of Revision 3), confirmed by Claude | 2.9, 2.2, V58 |
| N-13 | An evaluation outcome ALLOW is visible to callers before commit and could be read as permission; diagnostics returned alongside DENY and UNRESOLVED (G-B, FND-08) | Gemini, GPT | 2.9 (R31-06A), 4 |
| N-14 | A CORRECT that changes side, order association or instrument was unspecified; E13 covered quantity only (G-C) | Claude, GPT | D26, 2.2, 2.4.2, E13, V59 |
| N-15 | Correction payload and version semantics appeared only in the V49 setup; no normative prior-version contract (G-D) | GPT | D27, 2.2, E13, V49, V60, V61 |
| N-16 | The CAS schedule count 140 was stated for every scenario; scenarios with several or ordered broker events have different counts (G-E; 1,120 against 560) | GPT, Claude | 5.4, 5.7 |
| N-17 | The oracle domain for unreported fills did not state integer values or the full product (GPT-04) | GPT | 5.1, R31-08 |
| N-18 | "A newer accepted snapshot replaces the discrepancy" was imprecise on watermark, acceptance, contiguity and non-dismissal of other items (GPT-03) | GPT | 2.6.2, 2.4, V62 |

---

## Status ledger (what is what)
- **Defined:** the rules of section 2 with founder decisions D01, D03 to D16 applied (D02 and D17 to D22 recorded as approved in 3.2; D26 and D27 in 3.2.1).
- **Proposed:** the reconciliation resolutions RQ1 to RQ12, the Revision 3 and Revision 3.1 additions, the oracle design, the enumeration bounds, the soundness derivations.
- **Unknown:** whether the world model fits any real broker; soundness and tightness results; actual counts; whether any invariant fails; the values of the parameters.
- **Executed or verified:** nothing in this assignment except integer arithmetic of counts (5.2). Findings F-1 to F-8 and the case table of 2.4.1 are hand-derived hypotheses by one author. Agreement among GPT, Gemini and Claude is not independent verification.
- **Claim levels (R31-10):** specification consistency and hand-vector agreement have limited, hand-derived support; oracle correctness, model soundness and external validity are not established.

## Appendix A. H-LINK (NOT ADOPTED; historical record of a possible future refinement)
Idea: an orphan with broker_seq <= W, known side and quantity, whose signed value equals the discrepancy d, could be linked to d by a recorded link item, after which the pair would count once (a max instead of a sum for that pair). It would tighten V08b from 40 to 45 at the cost of link-evidence rules. The founder decision D01 does not adopt it into v0.1; it must not complicate v0.1. It may be revisited after the v0.1 results show how large the G1 gap actually is. The previously proposed unconditional max rule remains rejected as unsound (F-1) and appears only as a test-only variant to demonstrate the failure.
