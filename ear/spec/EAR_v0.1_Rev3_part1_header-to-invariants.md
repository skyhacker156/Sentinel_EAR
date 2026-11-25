SPECIFICATION ONLY / NOT IMPLEMENTED / NOT VERIFIED
Exposure Accounting Reference Model v0.1, Revision 3 (frozen). Part 1 of 3. Full-file SHA-256: 9a2c3be747fa9acbe4513e77f4122712f1970aa17109beb52acffbe051702b0a
---PART-BODY-START---
# Sentinel Exposure Accounting Reference Model v0.1 Specification

**SPECIFICATION ONLY / NOT IMPLEMENTED / NOT VERIFIED**

Date: 2026-11-22. **Revision 3.** Incorporates changes C-01 to C-15 of the Rev 2 reconciliation package and the six additional requirements (A to F) of GPT's Rev 3 preparation dispatch into Revision 2 (SHA-256 7d9573e42f7d8d0fe502b6bdc936b0a3933b536c838f7272de5e500802346e2c). From: Claude (ARBITER / Specification Lead).
**Revision 3 is FROZEN for hostile review. Its SHA-256 is published in the review packet and in the chat, and is not embedded in this file (a file cannot contain its own hash). The pre-freeze Revision 3 draft had hash 0eb476236b6510f2a2508fc401a8469310d9d4501362123c8298a2c282e22230; this file supersedes it (decisions recorded; G3 added). Freezing is not authorization to implement the reference model.**
Status of every rule: **[R]** REQUIRED or **[H]** HYPOTHESIS; unresolved decisions are marked **OPEN**. Founder decisions already applied: D01 approved (sum rule); D14 approved (addendum 5.2 and example 7 superseded); D10 amended; D03 to D09, D11 to D13, D15, D16 approved as proposed. **Founder dispatch of 2026-11-22, item 1 ("Resolve D02 and D17-D22 explicitly, preserving the conditional status of D19"), is recorded in 3.2 as approval of the positions on which Claude and GPT agree: D02 with additions, D17 with modification, D18, D20 with limits, D21 with commit-time revalidation, D22. D19 is approved only as a conditional specification candidate and never as an established safety property.** This is Claude's reading of that dispatch and is open to founder correction. Founder approval is not technical verification; GPT's dispositions are review positions, not approval. D23 to D25 remain deferred and OPEN. Nothing here has been executed.
Untouched: frozen v0.3, v0.3.1, v0.3.2, candidate v0.3.3 and their verification record. This model does not describe, and is not enforced by, the existing authority core.
Crypto observation, crypto-specific accounting, brokers, paper and live orders, strategy or P&L experiments, and G-04 to G-07 remain out of scope and appear nowhere in this specification except as named dependencies.

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

**Stop/go (section 7):** FROZEN FOR HOSTILE REVIEW. **NO-GO for implementation** until the independent challenge of Revision 3 is complete and the founder decides whether to authorize the bounded executable reference model.

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
- Execution: exec_id, order_id or null, instrument, side or null, qty or null, broker_seq (optional), kind in {NEW, CORRECT, BUST}, ref_exec_id for CORRECT/BUST, raw_hash, received_at.
- Snapshot: snapshot_id, instrument, qty, watermark W (the broker sequence number it is current through; optional), raw_hash, received_at. **Input contract (C-06):** qty is a signed integer. In this long-only envelope a negative or out-of-range qty is an envelope violation: structural Consistency failure, UNRESOLVED (V54). A source that reports only the *magnitude* of a discrepancy and not its direction is represented by d_plus = d_minus = the magnitude; a source that gives neither is malformed.
- Proposal: proposal_id, side, qty, instrument.
- Master version id and content hash in force (opaque inputs to v0.1, 2.12).
- Internal records: reservation commits, with the evaluation that produced them.

**Event log.** The ledger's source of truth is an append-only, hash-chained sequence of every accepted evidence item, in append order (the *log position*). Replay is a pure fold over the log in log-position order (2.6.3). Raw payloads and their hashes are retained.

**Derived state (recomputable from the log, model version and configuration):**
- **net_cum(order)** = sum of NEW execution quantities, adjusted by CORRECT, minus BUST, for that order. **net_cum_at(order, s)** is the same using only executions with broker_seq <= s. The lifecycle history is a separate append-only record, never rewritten.
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
- W2 and W6 depend on **A-12**: event delivery is complete between snapshots, except for unreported fills of known working orders (W4). **Snapshot freshness and decision age do not establish A-12.** A fresh snapshot with d = 0 shows only that the broker position equalled the ledger position at W. A dropped bust, a dropped execution for an unknown order, an undelivered correction, a wrong-side association or a duplicate economic execution after W is not represented by any world, and no formula covers it. It can be detected afterwards, at a later snapshot, as a discrepancy. This is detection after the fact, not protection.
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
- **Widen-only principle [R].** An unreconciled item (orphan, pending item, discrepancy, unknown order) may widen a bound; it may never narrow one. A known-side orphan therefore moves only the bound its side widens (Q3_buy raises F_max, Q3_sell lowers F_min) and takes **no credit** against the opposite bound, even though every world in which it occurred would allow it (gap G3). Only *application* (evidence that moves the item into F_d, 2.4.1 item 6) can end an overlap or take credit.
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
| C12 | bust or correction of an applied execution | new evidence | recompute; OVER_RESERVED if A_raw < 0 | detection, not prevention (I8) |

**Worked examples for the two evidence situations (V08a, V08b).** Common setup: F_d = 70, F_b = 65 at the same W (d = -5, MISMATCH), working sell 20, one orphan sell of 5.
- *V08a, orphan known to be after W (T4).* Formula: F_min = 70 - 5 - 5 = 60, A_raw = 60 - 20 = 40. Worlds: W1-T gives P = 70 - 5 - 5 = 60 (A_w = 40); W1-F gives P = 70 - 5 = 65 (A_w = 45). Oracle minimum 40 equals the formula: tight.
- *V08b, orphan with broker_seq <= W (T3, possibly already in the snapshot).* The formula is unchanged: 40. Worlds: W1-T has the orphan inside F_b, so P = 65 (A_w = 45); W1-F gives P = 70 - 5 = 65 (A_w = 45). Oracle minimum 45: the formula is conservative by 5 (gap G1).
- The formula cannot tell the two apart without trusting a link between the orphan and d, which v0.1 does not do (D01). The sequence evidence only labels the oracle's world set and the gap class. With no sequence number (V25) both timings are enumerated and the oracle minimum is 40.

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
| Pending correction or bust, original known | applied by own broker_seq | by effect | by effect | by effect | bounded | by revision |
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
- *Limitations.* Concerns authorization at commit; says nothing about later evidence (I8) or broker outcomes. **D19 is a specification candidate, conditional on the world model.** Zero false permissions in the declared oracle test space cannot establish safety against conditions excluded from W1 to W7 (A-11, A-12, wrong-side association, duplicate economic executions). The pre-declared rollback applies: if the oracle run finds any false permission on a MISMATCH ledger, reductions during a quantified MISMATCH are blocked (D19 option b).
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

