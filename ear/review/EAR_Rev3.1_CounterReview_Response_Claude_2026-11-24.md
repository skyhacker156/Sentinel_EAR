# EAR v0.1 Rev 3.1: Response to GPT's Independent Counter-Review

SPECIFICATION ANALYSIS ONLY. Rev 3.1 (`dd9d87f7…`, commit d4c9e66) stays frozen and unmodified. No implementation, broker contact, paper or live trading is authorized. Nothing here is a frozen revision; every proposal below is a Rev 3.2 *candidate* for founder review.

Reviewer: Claude (Specification Lead / ARBITER). Date: 2026-11-24. Responds to the founder-relayed GPT dispatch of the same date.
It builds on `EAR_Rev3.1_Review_Claude_2026-11-24.md` (SHA-256 39c224a3…), cited below as "the review". Line numbers refer to the Rev 3.1 file.
Labels: **verified** (checked by hashing, arithmetic or reading the text), **derived** (hand derivation, not executed), **computed** (a throwaway brute-force check of one hand example: not the oracle, not retained, not a test), **assumed**, **conditional**, **unverified**.

---

## 1. Disposition of GPT's findings

| GPT finding | Disposition | Reasoning |
|---|---|---|
| Rev 3.1 is NO-GO | **Accept** | Same conclusion. |
| R-01 silently conflicts with A-12 | **Accept** | The clause "every message that consumes a sequence number is delivered to the model" is a delivery-completeness assumption. It would quietly shrink A-12, so it is withdrawn (section 2). |
| R-07's "conservative on both bounds" is unproven and wrong in some cases | **Partially accept, and replace R-07** | Counting each delivery *as an orphan* is conservative on both bounds; proof in section 3 (derived and computed). But R-07 was **incomplete and unsafe at the exit transition**: under the Rev 3.1 rule "the order id resolves" (2.4.1 item 6, line 256), every copy is *applied*. Applied duplicates give false permission in **both** directions (computed). The claim also relied, unstated, on the widen-only principle. R-07 is withdrawn and replaced by R-07′. |
| R-03 needs a formal transition table | **Accept** | Table in section 4. Building it exposed a further defect: an old event below the bootstrap watermark is double-counted under the Rev 3.1 stale rule, whichever interpretation is taken (CX-28). |
| R-02 conflates accepted, corroborating and independent evidence | **Accept** | A same-broker snapshot is *corroboration*, not independent evidence. Terminology and profile revised (section 5). |
| R-06: a copied status function is not an independent oracle | **Agree** | Design in section 6. |
| R-12's epsilon has no operational meaning | **Accept** | Replaced with a defined linearization point (section 7). This also exposed that a reservation can outlive the freshness of its evidence (CX-25). |
| CX-12 needs lifecycle treatment | **Partially accept** | The economic limitation stands, but one part of it can be closed inside v0.1: an ACTIVE reservation survives OVER_RESERVED and can still be consumed (CX-26). New R-15 (section 8). |

New counterexamples in this response: CX-23 (hole above W), CX-24 (stale at the atomic step), CX-25 (reservation outlives its evidence), CX-26 (consume after OVER_RESERVED), CX-27 (duplicate applied at exit), CX-28 (pre-bootstrap event double-counted).

---

## 2. R-01 revised: reconciling A-2 with A-12

### 2.1 Event taxonomy

"In contract" means inside the declared A-2 / W1–W7 / envelope contract. "Undetected" means no rule of Rev 3.1 or R-01′ can notice the event.

| # | Category | Contract | Detectable? | Affects exposure? | Governing assumption | Authorization consequence |
|---|---|---|---|---|---|---|
| 1 | Sequenced and delivered | in | n/a | yes | A-2′ | Applied in sequence. Normal rules. |
| 2a | Sequenced, not delivered, **a higher number later observed** (a later event, or a snapshot with W above it) | in (delivery failure) | **yes**: a hole at H+1 | yes | A-2′ (detection) | GAP or AWAITING-BEHIND, so UNBOUNDED: increases DENY, reductions UNRESOLVED |
| 2b | Sequenced, not delivered, **above every observed number** (tail) | in (delivery failure) | **no**, until a higher number is observed | yes | **A-12 (tail form)** | Normal permissions continue. **False permission possible in any status, including RECONCILED** (CX-01) |
| 3 | Unsequenced and delivered | in (A-2 allows absent numbers) | its timing is unknown | yes | A-2′, 2.2 interval | Interval treatment and T3/T4 enumeration. Usually MISMATCH (CX-21) |
| 4 | Unsequenced, not delivered | out | **no** sequence detection. A later snapshot shows it only as d, and only if it occurred at or before that snapshot's W | yes | **A-12** | False permission possible until the next snapshot |
| 5 | Outside the declared sequence scope: other instruments' events, admin messages, broker adjustments, transfers, corporate actions | out (2.1 envelope, E-5), apart from coverage handling (R-08) | events that consume numbers: as 2a or 2b. Position changes outside the sequence: only as d at a later snapshot | sometimes | 2.1, E-5, **A-12**, R-08 | If they consume numbers: GAP until resolved (R-08). If they don't: undetected until d appears |
| 6 | Omitted by both the event stream and the snapshot | out (W1 common mode) | **no** | yes | W1 common-mode clause, A-7, D24 | Undetectable in v0.1. False permission possible |

### 2.2 Answers

**A. Did R-01 make sequenced delivery completeness an explicit assumption?** As drafted in the review, **yes**, and that was the error: it would have moved category 2b out of A-12 by assumption. **Withdrawn.** R-01′ (below) assumes how the broker *numbers* messages and how coverage works. It assumes nothing about *delivery*.

**B. Is A-12 limited to unsequenced or out-of-contract events?** **No.** Under R-01′, A-12 still governs categories 2b, 4, 5 (where no number is consumed) and 6. What R-01′ adds is *detection* for category 2a only. A-12 is not weakened. It is now partly explained: a missing sequenced event is detectable exactly when some higher number has been observed.

**C. Can the sequence be contiguous through W while an economically relevant event is absent?** **Yes**, in four ways (derived):
- (i) a tail loss above every observed number, category 2b (for example W = H = M = 100 and event 101, an external sell, never delivered);
- (ii) any category-4 or category-5 event;
- (iii) category 6;
- (iv) a W1-F snapshot (the broker's snapshot is false) whose watermark is still exact for the events it claims.
"Contiguous through W" is therefore a property of what was *received*, never of what *occurred*.

**D. Can an accepted snapshot rebase over missing numbers?** **No.** Rev 3.1 is right here (line 527, V48), and R-01′ keeps that.
- *Reason (derived):* a rebase accepts F_b as the true position at W, which is the W1-T world. The world model also admits W1-F (the snapshot is false), and in W1-F a missing event at or below W leaves the true position unbounded. That is exactly F-4 / D18.
- A snapshot also does not supply net_cum or R for the missing execution's order.
- So clearing a hole requires either the missing event itself, or a sequence-resolution item (R-08) from an authoritative broker response that names that exact number and classifies it (non-economic, foreign instrument, or an execution whose content is then supplied).

**E. Does the proposed H handle out-of-order buffering and a snapshot with W > H?** **Only partly, and fixing it exposes a Rev 3.1 inconsistency.**
- Define H over *received* numbers. Buffered events are received but not applied, and are applied in sequence order when the hole fills.
- Define M as the highest received number.
- *The inconsistency:* 2.6 (line 418) puts the status to GAP for **any** out-of-order arrival, while the 2.6.2 table (line 499) defines GAP as a number missing "at or below W". If the hole lies above W (H ≥ W, M > H+1), the two disagree.
- *CX-23:* under the narrow 2.6.2 reading, a buffered external sell (an orphan) above the hole is neither applied nor counted. F_min is too high, A is too high, and a **false permission** results (derived). Buffered events also have no row in the 2.4.2 inventory, which violates D17's "exactly one home".
- *Resolution in R-01′:* any recorded hole (H < M) means GAP. A snapshot with W > H and no received number above H means AWAITING-BEHIND.

### 2.3 R-01′: proposed contract text

**Replaces** the A-2 row of 2.11 (line 708) and the A-2 sentence in 2.3 limits (line 200). **Adds** definitions to 2.2. **Supersedes** the GAP rows of 2.6 (line 418) and 2.6.2 (line 499).

> **A-2′ (input contract, E).**
> (a) *Numbering:* where present, broker_seq is drawn from one contiguous integer sequence per (account, stream epoch). Each sequenced message's number is exactly its predecessor's plus one, as numbered at the source.
> (b) *Coverage:* the contract names the message classes that consume numbers. A number consumed by a class outside the model's scope is still a number of this sequence and must be resolved (R-08).
> (c) *Watermark exactness:* as in Rev 3.1.
> (d) *No delivery assumption:* delivery to the model is **not** assumed. A missing number is detected only once a higher number, or a snapshot watermark above it, is observed. Loss of events above every observed number is governed by A-12.
> Not established for any real broker.
>
> **Definitions.**
> - *W0:* the watermark of the bootstrap snapshot.
> - *Received:* appended to the log, whether or not applied.
> - *H:* the largest h ≥ W0 such that every number in (W0, h] has been received.
> - *M:* the largest received number (W0 if none).
> - *Hole:* any number in (H, M] not received.
> - Buffered events (received, number > H+1) are applied in number order, each in one revision step, when every hole below them has been filled.
>
> **Status rule (replaces the GAP rows).**
> - **GAP** iff H < M (at least one recorded hole), wherever it lies relative to W.
> - Otherwise **AWAITING-BEHIND** iff the accepted snapshot has W > H.
> - Otherwise "contiguous through W" holds (W ≤ H = M), and RECONCILED, AWAITING or MISMATCH follow from 2.6.2.
>
> **Inventory row (2.4.2).** Buffered event: home GAP; band UNBOUNDED.
>
> **A-12 (restated, not weakened).** Event delivery is complete between snapshots for:
> - (i) sequenced events numbered above M;
> - (ii) unsequenced events;
> - (iii) position changes that consume no sequence number.
> This holds except for unreported fills of known working orders (W4). It is not established by freshness, monotonicity, contiguity through W, or reconciliation. Its failure can invalidate both bounds and reduction permission in every status, including RECONCILED.

*Behavioural consequence:* CX-02 and CX-23 fail closed. CX-01 remains a documented limitation (unchanged). *Tests:* the raw-fact sequence patterns of R-06; CX-02, CX-10 and CX-23 as frozen vectors; V28, V29, V47 and V48 re-derived under H and M. *Alters the frozen baseline:* yes.

---

## 3. R-07: mathematical reassessment

### 3.1 The two cases

Common setup: F_d = 100, a working sell of 60 (S = 60), no buys, no discrepancy, L = 150. One genuine execution of quantity 10 is delivered twice, with no broker-unique id. All rows are **computed**, and agree with hand derivation.

| Case | Treatment of the second copy | Model U | Model A_raw | True U | True A | U conservative? | A conservative? |
|---|---|---|---|---|---|---|---|
| A: duplicate **buy**, both counted as orphans (Q3_buy = 20) | orphan | 120 | 40 | 110 | 50 | yes | yes |
| B: duplicate **sell**, both counted as orphans (Q3_sell = 20) | orphan | 100 | 20 | 90 | 30 | yes | yes |
| A: duplicate buy, both **applied** to F_d (F_d = 120) | applied | 120 | **60** | 110 | 50 | yes | **no: reduction false permission of 10** |
| B: duplicate sell, both **applied** (F_d = 80) | applied | **80** | 20 | 90 | 30 | **no: increase false permission of 10** | yes |

For case A as orphans, F_min takes no credit for the buy orphans (G3), so A_raw = 100 - 60 = 40 against a true 50. For case B as orphans, F_max takes no credit for the sell orphans, so U = 100 against a true 90.

### 3.2 Proof: counting as orphans is conservative (derived; holds only if (P1) to (P3) hold)

Let D_b and D_s be the multisets of *delivered* unassociated buy and sell executions, and O_b and O_s the multisets that *occurred*.
- **(P1), from A-12:** every occurred execution is delivered at least once, so O_b ⊆ D_b and O_s ⊆ D_s.
- **(P2), widen-only (2.4):** Q3_buy enters only F_max and Q3_sell only F_min; neither takes credit on the opposite bound.
- **(P3):** no copy leaves Q3 except by the exit rule of R-07′ (below).

Then ΣO_b ≤ ΣD_b and ΣO_s ≤ ΣD_s. In every admitted world:
- P_w ≤ F_d + d_plus + ΣO_b + Q3_unk ≤ F_d + d_plus + ΣD_b + Q3_unk = F_max;
- P_w ≥ F_d − d_minus − ΣO_s − Q3_unk ≥ F_min (symmetrically).
B and S are unaffected, so U ≥ U_true and A_raw ≤ A_true. **Counting cannot create false permission. Applying can.**

Note on increases: any orphan blocks increases (2.7). So case B's increase risk arises only after the copies leave Q3, which is exactly the exit problem.

### 3.3 Where the risk actually lies: exit and association (CX-27)

Rev 3.1 2.4.1 item 6 (line 256) lets an orphan move into F_d on "association evidence: **the order id resolves**, or an authoritative broker response establishes order, side and quantity". The first trigger applies each copy independently.
- *CX-27:* two copies of an external sell of 10 for order O9. The broker later acknowledges O9 (quantity 50). Both copies apply: net_cum = 20, F_d = 80, while the truth is net_cum 10 and position 90. U is understated by 10, so after T20 resolves O9 the increase block lifts and a buy is permitted 10 units beyond L (derived; the "applied" row in 3.1).
- The mirror case, a duplicate buy, gives a reduction false permission of 10. That is V56's shape, reached *inside* the spec's own exit rule rather than through an environmental failure.

### 3.4 R-07′ (replaces R-07)

> **Multiplicity-uncertain item (new inventory row in 2.4.2).**
> - *Trigger:* k ≥ 2 deliveries with identical canonical economic content (instrument, side, quantity, order reference, broker_seq if any) and no broker-unique id.
> - *Representation:* **one item** with occurrence multiplicity m ∈ {1, …, k}. (The case m = 0 is excluded by the reading of T1 that a report asserts occurrence.)
> - *Bounds:* the item widens its own side by **k·q**. Buy: F_max + k·q. Sell: F_min − k·q. Unknown side: both. No credit on the opposite side (widen-only). It blocks increases, like any orphan.
>
> **Exit (replaces the first trigger of 2.4.1 item 6 for this item).** The item moves into F_d only on an authoritative broker response that establishes the **exact multiplicity m**: an execution list, or an order status with a cum_qty consistent with exactly m copies. In one revision step:
> - m copies are applied;
> - k − m are dismissed, with evidence retained.
> "The order id resolves" alone is **not** sufficient for this item.
>
> **Associated executions** (the order is known) with no broker-unique id: a content-identical later delivery is **not applied and not discarded**. It is held as a T2 item of known side: it may or may not have occurred, it widens its own side by q, and it leaves only under the same exact-multiplicity exit.
> Alternative for FD-6: treat it as a structural conflict that blocks both sides. That is also conservative, at a higher availability cost.

*Proof for the associated case (derived).* Take a known working order, and a second copy held as T2.
- If the copy was genuine: the true net_cum is higher by q and the true R lower by q. For a buy, true U is unchanged while model U is F_max + q + B, which is larger; true A is F_d + q − S while model A_raw is F_d − S, which is smaller. For a sell, the same holds with the signs reversed.
- If the copy was not genuine: the model equals the truth plus a widening term.
- **Conservative in all four cases.**

*Oracle obligation:* the oracle enumerates m ∈ {1..k} for the multiplicity item and {occurred, not} for the associated T2 copy. Treating a copy as T1 would put a non-existent execution into every world.
*Tests:* both cases from section 3.1, CX-27, and k = 3 with exact-multiplicity exits m = 1, 2 and 3.
*Alters the frozen baseline:* yes (2.4.1, 2.4.2, A-11, 5.1).

---

## 4. R-03′: sequence transitions

Notation: W0 = bootstrap watermark; H and M as in R-01′; G = recorded holes; e = current epoch. "SEQ_CONTRACT" is a new structural evidence failure (2.8): it blocks increases and reductions (UNBOUNDED), and reason R_EVIDENCE_FAILURE carries the evidence code CONSISTENCY.SEQ_CONTRACT.

| # | Case | Initial | Incoming | Resulting H / G | Status | Applied? | Bounds change? | Authorization possible? | Evidence to restore |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Fills a recorded hole | W0 = 100, H = 100, G = {101}, buffered 102–103 | #101, unseen id, epoch e | H = 103, G = ∅ | recomputed (RECONCILED, AWAITING or MISMATCH) | yes; then 102 and 103 in order | yes | yes, if BOUNDED | none beyond the event |
| 2 | Same number, same identity and payload | H = 105 | #103 again, same event_id and payload | unchanged | unchanged | no (idempotent) | no | unchanged | none |
| 3 | Same number, conflicting id or payload | H = 105 | #103, different event_id or payload | unchanged | structural CONFLICT (Rev 3.1 line 523) | no | → UNBOUNDED | no | authoritative broker resolution of #103 |
| 4 | Unseen event, number ≤ H | H = 105 | #s ≤ H, unseen id | — | if W0 < s ≤ H, this is case 3 (every number in (W0, H] was received). If s ≤ W0: **SEQ_CONTRACT** | **no** | → UNBOUNDED | no | authoritative reconciliation: broker execution list for the range plus an accepted snapshot in the current epoch |
| 5 | Out of order above H+1 | H = 105, M = 105 | #108 | H = 105, M = 108, G = {106, 107} | **GAP** | buffered | → UNBOUNDED | no | case 1 for each hole, or a sequence resolution (R-08) |
| 6 | Sequence reset in the same epoch label | H = 503, W0 = 500 | #1, #2, … | — | the first event is case 4 (s ≤ W0) → **SEQ_CONTRACT** | no | → UNBOUNDED | no | as case 8, with the new epoch declared by the broker |
| 7 | Snapshot with newer received_at but lower watermark | accepted W = 500 | snapshot W′ = 7, received later | unchanged | Rev 3.1: rejected as REPLAY, prior state kept (unsafe under a reset, CX-04). **Proposed (FD-2):** (a) SEQ_CONTRACT → UNBOUNDED; or (b) add a broker-side as_of/epoch to the snapshot schema, so that REPLAY applies only to a snapshot older at the source | no | (a) → UNBOUNDED | (a) no | (a) as case 8 |
| 8 | New stream epoch (explicit) | epoch e, H = 503, G possibly non-empty | first message of e′ | H and G of e are frozen; e′ has none until a bootstrap | **UNKNOWN** | e′ events buffered | → UNBOUNDED | no | (i) an accepted snapshot of e′ (its W becomes W0′); (ii) resolution of every hole of e, by the missing events or an authoritative execution list covering (H_e, M_e]; (iii) T20 resolution of every UNKNOWN order. Without (ii), permanently UNBOUNDED: the honest cost (answer D) |

**SEQ_CONTRACT predicate.** A message in epoch e with number s is a sequence-contract failure iff one of the following holds:
- s ≤ W0_e;
- a snapshot arrives with W′ < the accepted W, under FD-2 option (a);
- an epoch arrives that the contract does not declare.

A number s ∈ G **is a hole fill, never a failure.** An s in (W0, H] with a new id is a CONFLICT (case 3), as Rev 3.1 already says.

**CX-28 (pre-bootstrap double count, derived).** Ledger bootstrapped from S0 (W0 = 500, F_d := F_b = 100). A genuine old execution #480 (a sell of 10) arrives late. Under Rev 3.1 line 419 it is "below the applied watermark, unseen, applied if consistent", so F_d becomes 90. But by watermark exactness S0 already contained #480, so the true position is 100.
- The applied sell **understates** F_d. U is too low, and an increase false permission follows once increases are otherwise open.
- A late old *buy* overstates F_d and gives a reduction false permission.
- **Rev 3.1's stale rule is unsafe even without a reset.** Case 4 closes it.

---

## 5. R-02′: evidence terminology and profile

**Three distinct concepts.** Each goes into 2.8 as a definition.

| Term | Meaning | Is it in v0.1? |
|---|---|---|
| **Accepted snapshot** | A snapshot that passes every rule of 2.6.2 and the snapshot-replacement rule | Yes |
| **Corroboration** | A second representation of the broker's state *from the same source*: an accepted snapshot compared with the execution stream at the snapshot's own W. Agreement shows the broker's reports are internally consistent, not that they are true; both share every broker-side and channel failure (W1 common mode) | **Yes: the only cross-check v0.1 has** |
| **Independent evidence** | A source whose failure modes are independent of the broker's: a second read-only channel, clearing or custodian records | **No** (D24) |

**What v0.1 needs:** corroboration for reductions. Independence is a live-use requirement (D24) and is never claimed in v0.1.

**Proposed changes.**
- **Consistency results:** CORROBORATED (acceptable), UNCORROBORATED (no accepted snapshot to compare: failure), INCONSISTENT (structural: failure).
- **D06 restated:** "UNCORROBORATED is not tolerated for reductions."
- **NO_INDEPENDENT_EVIDENCE** stops being a Consistency failure state. It becomes a fixed **limitation flag**, recorded in every v0.1 Decision and in the assumptions-in-force notice. It always reads "no independent evidence", which makes the absence of independence visible without making v0.1 unable to authorize anything. Whether any live use may tolerate it is D24.

**Evidence-property inputs (reference model).** Each of the five properties is either *computed by the model from explicit inputs*, or *supplied as a synthetic fixture*. No fixture value ever reads as real-world assurance.

| Property | v0.1 reference model | Recorded as |
|---|---|---|
| Integrity | synthetic fixture | FIXTURE_PASS or a named failure fixture; **never MATCH** |
| Provenance | synthetic fixture | FIXTURE_PASS or a failure fixture; never COMPLETE |
| Authenticity | synthetic fixture (D23 undecided; no keys exist) | FIXTURE_PASS or a failure fixture; **never VERIFIED** |
| Consistency | **computed** (snapshot comparison, structural checks) | CORROBORATED, UNCORROBORATED or INCONSISTENT |
| Freshness | **computed** from as_of, received_at, S_lim and the REPLAY rules | FRESH, STALE, REPLAY, FROM_FUTURE or CLOCK_UNAVAILABLE |

How the gating works:
- **Rule:** FIXTURE_PASS is acceptable *for gating in the reference model only*.
- **Labelling:** every Decision and CommittedReservation carries `evidence_profile = SYNTHETIC_FIXTURE`. Any report that aggregates results must print that profile beside every ALLOW count.
- **Hard boundary:** a run using SYNTHETIC_FIXTURE can never support claim level 5 (external validity, R31-10).
- **Fixture failures are enumerated:** each failure fixture × {increase, reduction} must yield DENY or UNRESOLVED.

**Reconciling with the vectors (derived).** Under this profile, with the three fixtures at FIXTURE_PASS and the computed Consistency and Freshness, no vector V01–V62 changes outcome:
- every ALLOW vector has an accepted snapshot (default RECONCILED; or AWAITING or MISMATCH), so it is CORROBORATED and FRESH;
- vectors with status UNKNOWN or UNBOUNDED (V13, V28, V29, V31, V35, V47-before, V48, V54, V55, V59, V61) already refuse;
- V52 is a malformed-proposal refusal, independent of evidence.
- *Caveat:* the vectors need an explicit `evidence_profile` column. Today their evidence results are implicit (**verified** by reading 2.10).

---

## 6. R-06′: independent status derivation

**Agree with GPT.** A function that reuses or transcribes the model's status logic shares its errors. CX-02 is exactly such an error: a monotone-only GAP that both copies would share.

**Design.**
1. **Inputs are raw facts only.** The generator emits raw-fact JSON:
   - events with event_id, payload, broker_seq or null, epoch and log position;
   - snapshots with W or null, F_b, received_at and epoch;
   - the bootstrap W0;
   - lifecycle events for quiescence;
   - corrections and busts with their D27 fields;
   - terminal events with cum_qty.
   **No status, H, M, d or BOUNDED field appears in the input.**
2. **Separate derivation.** The status checker lives in `exposure_oracle/status/`. It is written from 2.6.2, R-01′ and R-03′ text only, with its own parser and data types. It imports nothing from `exposure_model/` and no shared helper library (enforced by an AST import-ban test that fails the build).
3. **Separate generator.** The grid generator is a third component that knows nothing about either derivation. Raw-fact dimensions replace the status dimension of 5.2 (line 892):
   - sequence pattern ∈ {contiguous, one hole below W, one hole above W, tail beyond M, duplicate number with the same id, duplicate number with a different id, pre-W0 number, epoch change};
   - snapshot W relative to H and M ∈ {below, equal, above};
   - quiescent ∈ {yes, no};
   - unsequenced applied executions ∈ {0, 1, 2}.
4. **Source hashes first.** The checker's source hash is recorded before it sees any model output.
5. **Detection power is demonstrated, not assumed.** A mutation suite injects known status bugs into a *copy* of the model:
   - monotone-only GAP (CX-02);
   - the narrow "at or below W" GAP (CX-23);
   - the stale rule applying a pre-W0 number (CX-28);
   - REPLAY-ignore of a lower watermark (CX-04).
   The comparison must flag every mutant on at least one generated case. A mutant that survives means the comparison is too weak.
6. **Labelling.** If Claude writes both the model and the checker, the checker is **same-author, structurally separated**. Independence requires a second author to write it from the text alone (the review's section 7 list applies).

---

## 7. R-12′: the commit linearization point

**Definition.** The linearization point L of `authorize` is the single atomic step of the store in which the reservation and the AUTHORIZED order are appended and the revision advances. Its timestamp t_L is read from the independent clock **inside** the store's serialized critical section, after the lock is acquired and before the append.

**Rule (replaces commit steps 3 and 4, 2.9 lines 605–606).** Inside the critical section, with no interleaving possible:
1. Read t_L.
2. Run the pure `evaluate(ledger at the current revision, proposal, config, as_of = t_L)`.
3. Require all of: outcome ALLOW; the current revision equals decision.ledger_revision; item hash matches; proposal_hash matches; no existing reservation; t_L − decision.as_of ≤ D_max.
4. If any check fails, append nothing, release the lock, and refuse (or retry from step 1 of 2.9 up to K).
5. If all pass, append with committed_at = t_L.

Freshness is decided at t_L. No epsilon is needed, because the check and the append are one logical step at one logical time. Physical time between the clock read and the append is not observable to any other operation (serialized). In the reference model, time is an explicit scheduler input that advances only *between* steps, so t_L is exact.

**If the operation completes after the evidence expires:** in this definition the operation "completes" at L. If the snapshot is stale at t_L, the commit is refused (R_DECISION_STALE). Re-evaluation is required on every retry. No previous evaluation is ever reused.

**CX-24 (stale between check and commit).** S_lim = 10 s; the snapshot is received at t = 0.
- Evaluation at 9.90 s: ALLOW. Rev 3.1 step 3 at 9.95 s: fresh. The store's atomic step executes at 10.05 s.
- Rev 3.1 leaves open which time step 4 uses, so the commit may succeed on stale evidence.
- R-12′: t_L = 10.05 s, the snapshot is 10.05 s old > S_lim, so it is **refused**.

**CX-25 (reservation outlives its evidence).** Committed at t_L = 9.95 s, TTL = 30 s; consume at 25 s.
- Rev 3.1 `consume` checks only ACTIVE and unexpired (line 618), so it succeeds on a snapshot 25 s old.
- **Proposed:** expires_at = min(t_L + TTL, snapshot.received_at + S_lim), so consume at 25 s fails.
- Alternative (FD-7): `consume` re-runs the freshness check at its own linearization point. That is stricter, and it creates the "authorized but unconsumable" state at the same frequency.

---

## 8. CX-12: later bust across the authorization lifecycle

Setup (derived): F = 100 after the buy fill B1 of 100 was applied (order FILLED), RECONCILED. A sell reservation of 100 was committed: S = 100, A_raw = 0. Then B1 is busted (E14, T21): F_d = 0 and A_raw = −100, so OVER_RESERVED is raised in the same revision (I8).

| Stage when the bust arrives | Rev 3.1 behaviour | What v0.1 can promise | Proposed |
|---|---|---|---|
| 1. After evaluation, before commit | The revision moved, so commit is refused and re-evaluation gives DENY (I5) | **No authorization** | none needed |
| 2. Committed, reservation ACTIVE, not consumed | OVER_RESERVED raised, but **`consume` does not check it** (line 618): the adapter can consume and submit an oversell (**CX-26**) | Today: nothing | **R-15:** OVER_RESERVED moves every ACTIVE reservation on the sell side to SUSPENDED, in the same revision step; `consume` requires ACTIVE (not SUSPENDED); a SUSPENDED reservation is released when A_raw ≥ 0 is re-evaluated, or it expires. Now: **no consumption** |
| 3. Consumed, not yet transmitted | Order SUBMITTED at consume (T04). The model cannot recall it (I8) | **Nothing.** Whether the adapter checks again before transmitting is the adapter/G-07 boundary (2.9 line 620) | Record this explicitly as an adapter acceptance test (5.7 item 8): "OVER_RESERVED between consume and transmit" |
| 4. Accepted by the broker, not executed | The model records E07/E08 if a cancel happens; authority to cancel is G-07 (D10) | Detection; no new authorization; R stays reserved | none in v0.1 |
| 5. Executed | Position goes short; the next snapshot gives a negative F_b, a structural failure (V54), and everything is UNRESOLVED | Detection only. Containment is G-06 (out of scope) | none in v0.1 |

**What v0.1 promises:**
- OVER_RESERVED is raised in the same revision as the bust;
- no new authorization while it holds;
- **with R-15**, no consumption of an outstanding reservation while it holds.

**What it does not promise:** recall of a consumed order, cancellation, containment, or recovery from an executed oversell.

**Operational bound (derived).** If A_raw ≥ 0 before the bust and the bust removes a buy of quantity q_b, then afterwards A_raw ≥ −q_b. Hence:
- the worst-case short created by one bust is at most q_b, plus any later reductions, which R-15 prevents;
- for several busts, the bound is the sum of the busted buy quantities;
- operationally, the exposure of an accepted limitation is "up to the quantity of not-yet-final buy fills against which reductions were committed".

That is why FD-4 still matters: the alternative is to keep fills younger than a bust window out of A, which needs a new parameter and is a research item.

---

## 9. Revised oracle obligations and D19 findings

**Unknown-side working order, enumeration (derived and computed).** Each world takes a side s ∈ {buy, sell}, a fill x ∈ {0..R} and a placement. Contribution to U_w:
- buy world: x + (R − x) = R;
- sell world: −x;
- so the maximum is R.
Contribution to A_w:
- buy world: +x;
- sell world: −x − (R − x) = −R;
- so the minimum is −R.
The model puts R in both B and S, so it is **tight on both bounds.** 5.1 step 2 must add the side choice (R-05).

**n > 1 unsequenced executions plus an unknown-side order plus MISMATCH plus a T1u orphan.**
- *Separability (derived).* Within one snapshot class, P_w is a sum of terms each depending on a different, independent world choice (inclusion choices for unsequenced executions, orphan side, order side and fill). So the maximum (or minimum) over the product space equals the sum of the per-term extremes. The only shared choice is the class W1-T vs W1-F, handled by taking the maximum over the two. Both extremes in W1-T reproduce F_d + max d and F_d + min d (2.2 interval), and W1-F contributes d = 0, which d_plus and d_minus already include through max(0, ·).
- *Worked example (computed, plus derived by hand).* F_base = 50, unsequenced s = (+4, −1), F_b = 50, a T1u orphan of 2 with seq > W, an unknown-side order R = 5.
  - Inclusion choices give d ∈ {0, −4, +1, −3}, so d_plus = 1 and d_minus = 4.
  - Model: F_max = 53 + 1 + 2 = 56, F_min = 53 − 4 − 2 = 47, U = 61, A_raw = 42.
  - Brute force over all worlds: U_oracle = 61, A_oracle = 42. **Sound and tight.**
  - This is outside the static grid and must enter the generative tests (5.3) with a declared bound.

**Multi-orphan combinations:** the same separability holds. Each orphan's occurrence, side and timing are independent per class (derived). Note, though, that G1 overlap can occur once per T3 orphan.

**Negative-snapshot path:** the validity predicate (line 896) must route F_b < 0 to the V54 structural path, not exclude it (R-13).

**G3 classification:** R-04 unchanged. B2 and B5 are frozen G3 vectors.

**Status derivation:** R-06′.

**D26/D27 payload obligations:**
- an identity change (side, order, instrument) × the referenced execution {working order, terminal order};
- a stale prior_version;
- a prior_qty mismatch;
- each required field missing in turn;
- two corrections in both log orders (V49);
- a CORRECT numbered above W versus at or below W (F_d versus F_d(W)).

**Multiplicity items (R-07′):** m ∈ {1..k} for k ∈ {2, 3}; the associated T2 copy ∈ {occurred, not}.

**D19's five preconditions (I2, line 342).**

| # | Precondition | Character | Finding |
|---|---|---|---|
| 1 | Valid watermark, contiguous through W, not GAP, AWAITING-BEHIND or AWAITING-UNVERIFIED | **Substantive.** It defines when MISMATCH is BOUNDED | Depends on R-01′ (H, M). Under the narrow Rev 3.1 GAP definition it can appear satisfied while a hole above W hides an orphan (CX-23) |
| 2 | No structural failure, no pending correction or bust | **Substantive** | Already implied by BOUNDED (2.2 line 148) and the reduction rule; independently testable |
| 3 | Unsequenced executions handled by the interval | **Circular.** It *is* the definition of d (2.2) | Not a precondition. It can only fail through an implementation defect, so it is testable by mutation only |
| 4 | Fresh at evaluation and at commit; within D_max | **Redundant.** I5 / R-12′ apply to every commit | Not specific to D19 |
| 5 | Judged against A, never clipped, never above the position | **Restates the decision rule.** Q ≤ A ≤ F_min | Not independent |

**Finding (derived):** D19 reduces to "a quantified MISMATCH is a BOUNDED status, evaluated by the general reduction rule", subject to preconditions 1 and 2. Sufficiency inside W1–W7 follows from the sum-rule soundness (review section 6) and the separability argument above. **No in-model false permission found** (derived, not executed). D19 stays **conditional**. Its rollback trigger stands. **R-17:** restate D19 with two preconditions and record 3, 4 and 5 as consequences, so that no test pretends to exercise them as conditions.

---

## 10. Updated revision candidate list

All alter the frozen baseline. All are Rev 3.2 candidates for founder review.

| ID | Severity | Change | Status vs the review |
|---|---|---|---|
| R-01′ | Blocking | A-2′ numbering and coverage without a delivery assumption; definitions of W0, H, M and hole; GAP iff H < M; buffered-event inventory row; A-12 restated with its scope | **Revised** (delivery clause withdrawn; CX-23 added) |
| R-02′ | Blocking | Accepted, corroboration and independent defined; Consistency values; D06 restated; NO_INDEPENDENT_EVIDENCE becomes a limitation flag; SYNTHETIC_FIXTURE profile; evidence column in the vectors | **Revised** |
| R-03′ | Blocking | Transition table; SEQ_CONTRACT predicate; pre-W0 events never applied (CX-28); epoch handling | **Revised** (stale rule found unsafe even without a reset) |
| R-04 | Major | Add G3 to every gap classification | unchanged |
| R-05 | Major | Unknown-side order in the oracle domain and grid | unchanged (now derived as tight) |
| R-06′ | Major | Raw-fact grid; separate status checker; import ban; mutation-based detection-power test | **Revised** |
| R-07′ | Major | Multiplicity-uncertain item; exact-multiplicity exit; associated copy as T2 of known side | **Replaces R-07** |
| R-08 | Major | Coverage classes and the sequence-resolution evidence item | unchanged |
| R-09 | Minor | net_cum_at over events by their own number | unchanged |
| R-10 | Minor | Unsequenced executions (FD-3) | unchanged |
| R-11 | Minor | Master version on snapshots | unchanged |
| R-12′ | Major (raised from minor) | Linearization point t_L; evaluation inside the critical section; expires_at bounded by evidence freshness | **Revised** (CX-24, CX-25) |
| R-13 | Minor | Editorial fixes; V54 routing; D26/D27 obligations | unchanged |
| R-14 | Info | Limitation vectors V63 (CX-01), V64 (CX-12), V65 (CX-08), plus V66 (CX-27) | extended |
| **R-15** | **Major** | OVER_RESERVED suspends ACTIVE reservations on the affected side; `consume` refuses SUSPENDED | **New** (CX-26) |
| **R-16** | Minor | Adapter acceptance test: OVER_RESERVED between consume and transmit (5.7 item 8) | **New** |
| **R-17** | Minor | D19 restated with two substantive preconditions | **New** |

---

## 11. Remaining founder decisions

- **FD-1′:** adopt the corroboration terminology and the SYNTHETIC_FIXTURE profile (R-02′). This replaces the earlier choice between (a) and (b).
- **FD-2′:** a lower-watermark snapshot with a newer receipt time: (a) SEQ_CONTRACT, or (b) a schema change adding a broker-side as_of/epoch (R-03′ case 7). Also: accept that unresolved holes from an old epoch keep the ledger UNBOUNDED until an authoritative execution list is supplied (case 8).
- **FD-3:** unsequenced executions are out of contract, or permanent MISMATCH is the stated cost (R-10).
- **FD-4′:** later busts. Accept the limitation with R-15, plus the operational bound of section 8 (recommended for v0.1); or schedule a fill-finality haircut as research.
- **FD-5:** authorize a single controlled Rev 3.2 drafting pass containing R-01′ to R-08, R-12′ and R-15, with R-09 to R-17 included or deferred.
- **FD-6 (new):** an associated content-identical copy is held as T2 of known side (recommended), or treated as a structural conflict.
- **FD-7 (new):** reservation expiry bounded by evidence freshness (recommended), or a freshness re-check at `consume`.

---

## 12. Updated implementation-readiness verdict

**NO-GO for a bounded reference implementation of Rev 3.1. Unchanged.**

The counter-review made the correction set stronger, and in doing so surfaced six further defects:
- three are in-spec false-permission paths: CX-23, CX-27 and CX-28;
- one is a commit-time ambiguity: CX-24;
- two are lifecycle gaps: CX-25 and CX-26.

All are closed by R-01′, R-03′, R-07′, R-12′ and R-15 as proposed (derived).

**Path to CONDITIONAL GO:**
1. FD-1′, FD-2′, FD-3, FD-6 and FD-7 decided;
2. a controlled Rev 3.2 candidate drafted with the set above (FD-5);
3. an adversarial counter-review of *that candidate*, in which GPT should attack R-07′'s exit rule and R-03′'s SEQ_CONTRACT predicate first;
4. the 5.7 prerequisites, including the R-06′ mutation suite.

Separately, by dimension:

| Dimension | Assessment |
|---|---|
| Coherence | Rev 3.1 inconsistent at A-2/GAP, 2.6 versus 2.6.2, 2.8 versus the vectors, the stale rule, and the G3 classification (verified by reading) |
| Soundness within the model | Sum rule, D19, unknown-side orders and separability hold (derived); in-spec exit and sequence rules do not (CX-23, CX-27, CX-28; derived) |
| Assumption adequacy | A-12 now scoped explicitly, not weakened; A-2′ separates numbering from delivery |
| Counterexample coverage | CX-01 to CX-28 (derived) |
| Oracle adequacy | Design gaps identified with fixes; nothing executed (unverified) |
| Independent verification readiness | Not ready; same author throughout |
| Operational realism | A-2′ contiguity, epochs, broker-unique ids, D27 prior_version: all unvalidated for any broker (unverified) |

*Agreement between this response and GPT's review is not independent verification. The only things executed here were hashing, integer arithmetic, and the throwaway brute-force checks marked "computed".*
