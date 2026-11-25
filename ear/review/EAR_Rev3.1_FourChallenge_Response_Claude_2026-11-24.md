# EAR v0.1 Rev 3.1: Response to the Four-Point Targeted Hostile Challenge

SPECIFICATION REVIEW ONLY. Rev 3.1 (`dd9d87f7…`, commit d4c9e66) stays frozen. Rev 3.2 drafting is not authorized. No reference model, oracle execution, broker, paper or live work.
Reviewer: Claude (Specification Lead / ARBITER). Date: 2026-11-24.
This responds to the dispatch "Four-point targeted hostile challenge" (GPT, with Gemini corroboration). It builds on the review (`39c224a3…`) and the counter-review response (`e53d96ef…`), cited below as "R1" and "R2".

Labels:
- **DERIVED**: follows from stated definitions and assumptions.
- **COMPUTED**: integer arithmetic executed by a throwaway Python script that evaluates the Rev 3.1 section 2.4 formulas on the stated values. Not an oracle and not a test; it is reported only to rule out arithmetic slips.
- **ASSUMED**: rests on an explicit assumption.
- **CONDITIONAL**: holds only if the named preconditions hold.
- **UNVERIFIED**: not demonstrated by execution, independent review or external evidence.

Gemini's agreement with GPT is corroboration that these questions are worth asking. It is not verification of anything below.

---

## 0. Correction to R2 (left visible)

**R2's CX-28 was wrong as stated.** R2 said that applying a late pre-bootstrap event (#480, a sell of 10, already included in snapshot S0 at W0 = 500) understates U and creates an increase false permission. That ignored the F_d(W) comparison.

Because #480 has broker_seq ≤ W, it enters F_d(W):
- F_d(W) = 90 against F_b = 100, so d = +10 and the status is MISMATCH.
- F_max = 90 + 10 = 100, which equals the true position. U is correct, not understated.
- F_min = 90, so A is conservative.
- Increases are blocked by the MISMATCH.
(COMPUTED: d 10, U 100, A_raw 90, true P 100.)

**The real defect is availability, not safety.** Every later snapshot reports the true 100 against F_d(W′) = 90, so the MISMATCH never clears (DERIVED).

The SEQ_CONTRACT rule for s ≤ W0 is still recommended, but for a different reason, given in Challenge 4, case 1: it keeps a sequence reset from silently disabling gap detection. Double counting is not the reason.

---

## Challenge 1: R-07′ multiplicity and exit

**Disposition: accept. R-07′'s exit rule is withdrawn.** Neither cum_qty nor an execution list can establish the multiplicity of *deliveries*. The broker knows which executions occurred; it does not know which ones the model received.

### Definitions and assumptions

- R-07′ applies only to deliveries that have **no broker-unique id and no broker_seq** (DERIVED from A-2′ and A-11):
  - Same broker_seq with the same identity and payload is an idempotent duplicate (R-03′ case 2). The sequence number establishes identity.
  - Same broker_seq or same event_id with a different payload is a conflicting delivery: structural CONFLICT (Rev 3.1 lines 417 and 523).
  - Different broker_seq with identical payload means distinct executions under the contract. If it is really a resend, that is an A-11 violation (V56).
- **Genuinely distinct executions with identical observable payloads**, unsequenced and id-less, cannot be told apart from duplicates. This is exactly the multiplicity item, m ∈ {1..k}. The held state is conservative (R2 section 3.2, DERIVED).

### Counterexample C1-a (naive exit)

Setup:
- Our working sell order O9, quantity 50. Start: F_d = 100, L = 150, RECONCILED, no buys.
- E1: sell 10, broker id X1, applied. F_d = 90, R = 40.
- D1: sell 10, no id, no sequence number, applied. F_d = 80, R = 30.
- D2: content identical to D1, held as a T2 sell copy (R-07′ associated case): Q3_sell = 10.

**Held state (COMPUTED).**
- Model: U = 80, A_raw = 70 − 30 = 40. Increases are blocked by the item.
- World (i), D2 genuine: true P = 70, R = 20, so true U = 70 and A = 50.
- World (ii), D2 a duplicate: true P = 80, R = 30, so true U = 80 and A = 50.
- Model U ≥ both and A_raw ≤ both: **conservative.**

**Broker order status: cum_qty = 30.**
- **Naive exit N1** (compare cum_qty with the copies only, ignoring the baseline): 30 ≠ 20 and 30 ≠ 10. No consistent m; inconclusive.
- **Naive exit N2** (cum_qty minus applied net_cum, attributed to the held copy): 30 − 20 = 10, so it sets m = 2 and applies D2. F_d = 70, R = 20, U = 70, A_raw = 50. The increase block lifts.
- But cum_qty = 30 is also consistent with **world (ii′)**: D2 is a duplicate and a third fill X (sell 10, never delivered) occurred. N2's attribution is wrong. The quantity happens to be right at this moment, because D2 stands in for X.
- **X is later delivered** (with id X3, or id-less but distinguishable) and applied: F_d = 60, R = 10, model U = 60. The truth is still P = 70, R = 20, U = 70.
- **A buy of 90 passes the model check, U + Q = 150 ≤ L, and is ALLOWED. The true U + Q = 160 > L. False permission of 10** (COMPUTED).
- The mirror case, with buys, gives a reduction false permission (DERIVED).

**Why this happens (DERIVED).** cum_qty conserves *quantity per order at an unstated point in time*. It does not attribute that quantity to particular deliveries, and it does not mark which later deliveries are already inside it. Once a later delivery is matched against nothing, it double counts.

### What evidence actually makes an exit valid

1. **Minimum broker response:** an authoritative **per-order execution list** with:
   - (a) a broker-unique execution id for every execution on the order;
   - (b) each execution's side and quantity, and its current corrected version;
   - (c) a per-order watermark: "complete through" a broker sequence number, or the order being terminal.
2. **Baseline and interval:** the list replaces the order's *entire* execution set as of its watermark. It is not a delta from our net_cum.
3. **Exit (R-07″), in one revision step:**
   - (a) every applied or held execution on that order with no id is dismissed and superseded;
   - (b) the listed executions become the order's applied set, so net_cum = the list total and R = qty − net_cum;
   - (c) applied executions that carry ids are matched by id, and an unlisted id is a CONFLICT;
   - (d) corrections and busts are reflected only through the list's current versions.
   This avoids double counting (DERIVED), because no quantity enters from both the old set and the list.
4. **After the exit:** a later delivery for that order is applied only if its id is in the list and new since the watermark, or above the watermark. An id-less later delivery is held as T2 until the order is terminal and its terminal cum_qty reconciles (Rev 3.1 terminal rule, line 486).
5. **Unassociated items (no order):** no per-order list exists. The item leaves only by an authoritative execution-level response with ids for that exact execution. Otherwise it stays held. That is conservative, at an indefinite availability cost.

With this evidence, C1-a resolves correctly: the list is {X1, Xa, X3}, total 30, and X3's later delivery matches by id and is idempotent (DERIVED).

**Answer to the question.** No: R-07′ cannot establish exact multiplicity from the proposed evidence. Any exit needs a **stronger identity and reconciliation contract**: broker execution ids plus a per-order watermark. Recommended alternative for v0.1 (**FD-8**): declare deliveries with no id and no sequence number **out of contract**. Hold them as a structural failure, UNBOUNDED on the affected side, until per-order list reconciliation. This removes the multiplicity item from the bounded model altogether.

**Remaining dependency:** whether any real broker provides per-order execution lists with watermarks (UNVERIFIED).
**Baseline:** a Rev 3.2 candidate only; it modifies 2.4.1 item 6, 2.4.2, A-11 and 5.1.

---

## Challenge 2: R-15 symmetric suspension and reactivation

**Disposition: accept.** R-15 was one-sided and reactivated on A_raw alone. It is replaced by R-15′.

### Definitions and assumptions

Rev 3.1 flags only A_raw < 0 (OVER_RESERVED, I3). **There is no flag for U > L** (verified by reading I3, I8 and 2.9). The increase side therefore has no analogue to detect a breach.

### Case A: buy-fill bust with an outstanding sell reservation (COMPUTED)

- **Initial:** a buy of 100 on B1, FILLED and applied from 0, so F_d = 100, RECONCILED. Sell reservation P1 (sell 100) ACTIVE: S = 100, A_raw = 0.
- **Authorization basis:** a sell of 100 was allowed because 100 ≤ A = 100.
- **Bust:** E14 / T21 busts B1, so F_d = 0. Then F_min = 0, A_raw = 0 − 100 = −100, and OVER_RESERVED is raised.
- **Unsafe:** every ACTIVE sell reservation. Here, P1.

### Case B: sell-fill bust with an outstanding buy reservation (COMPUTED)

- **Initial:** L = 150. Position 150, then sell fill S1 of 50 applied, so F_d = 100, RECONCILED. Buy reservation P2 (buy 50) ACTIVE: B = 50, U = 150 ≤ L.
- **Bust:** S1 is busted, so F_d = 150 and U = 150 + 50 = **200 > L**. **Rev 3.1 raises nothing**: no flag and no block. P2 can be consumed.
- **Unsafe:** every ACTIVE buy reservation.
- The limit L is a G-04 test parameter, so this is a *policy-limit* breach. Case A is a long-only *envelope* breach.

### R-15′ (replaces R-15)

> **Continuing-safety predicate.** For each ACTIVE reservation r, let Π(r, ρ) be the complete authorization predicate of 2.4 and 2.9 (R-12′) for r's proposal at revision ρ, with r's own quantity already in B or S and every other ACTIVE reservation counted. It includes:
> BOUNDED; no structural evidence failure, including SEQ_CONTRACT, D26/D27 holds and CONFLICT; evidence profile acceptable (Consistency CORROBORATED, Freshness FRESH at the evaluation time, fixtures acceptable); not OVER_RESERVED; not OVER_LIMIT (new flag: U > L); and the side-specific blocks of 2.7. For a buy, that means no increase-blocking item (UNKNOWN order, orphan, MISMATCH, pending item); for a sell, A_raw ≥ 0.
>
> **Suspension.** In the **same revision step** that applies any event or snapshot, and at every reservation-expiry tick:
> - every ACTIVE r with ¬Π(r, ρ) becomes **SUSPENDED**;
> - it is recorded in the log and the item hash, and stays counted in B or S.
> The suspension set is **all** failing reservations, never a chosen subset. The alternative, suspending the newest first until the breach clears, is a policy choice (FD-9).
>
> **Consumption.** `consume` requires state ACTIVE **and** re-evaluates Π at its own linearization point (R-12″).
>
> **Reactivation.** SUSPENDED → ACTIVE only at a revision where Π(r, ρ) holds in full, evaluated as for a fresh commit. Otherwise r stays SUSPENDED until its expires_at (R-12′, bounded by evidence freshness), then becomes EXPIRED and its quantity is released.

### Reactivation counterexample: A_raw ≥ 0 while Π fails (COMPUTED and DERIVED)

- Start from Case A after the bust: F_d = 0, S = 100 with P1 SUSPENDED.
- We also have a working buy O3 of 100, previously submitted.
- O3 fills 100, sequenced and contiguous: F_d = 100, B = 0, so **A_raw = 100 − 100 = 0 ≥ 0**.
- In the meantime the accepted snapshot has aged past S_lim. The status is UNKNOWN (stale), so the band is UNBOUNDED.
- **Naive reactivation** (on A_raw ≥ 0) makes P1 consumable, and a sell of 100 goes out against a position that no accepted snapshot corroborates.
- **Under R-15′**, Π fails on BOUNDED and Freshness, so P1 **stays SUSPENDED**.
- The same holds for each of: a GAP, AWAITING-BEHIND, SEQ_CONTRACT, an unresolved D26 correction, or a new UNKNOWN order (that one blocks buys only). In each, A_raw can be ≥ 0 while Π fails (DERIVED).

### Consumed or later stages (unchanged from R2 section 8, both directions)

- **Consumed but not transmitted:** the order is SUBMITTED. The model cannot recall it. The adapter re-check is an acceptance test (R-16), not a v0.1 guarantee.
- **Accepted, not executed:** detection only. Cancellation authority is G-07.
- **Executed:** irreversible.
  - Case A: a short position. The next snapshot is negative (V54), giving UNRESOLVED.
  - Case B: U above L. The new OVER_LIMIT flag blocks further increases. No containment (G-06).
- **Bound (DERIVED):** a single bust can push past the limit by at most the busted quantity, plus whatever executes from reservations consumed *before* the bust's revision.

**Answer.** Yes. R-15′ is symmetric. It suspends every reservation whose continuing safety is not established, atomically in the revision that changes the evidence, and it requires complete re-authorization (Π) to reactivate.

**Remaining:** FD-9 (all-failing versus newest-first). An interaction: under FD-3 "permanent MISMATCH", every ACTIVE buy would be suspended permanently (DERIVED).
**Baseline:** a Rev 3.2 candidate. It adds the OVER_LIMIT flag to I3 and I8, the SUSPENDED state to 2.9, and updates the reservation lifecycle.

---

## Challenge 3: R-12′ linearization and D_max

**Disposition: partially accept.**
- Under R2's intended reading, `decision.as_of` meant the as_of of the **original** decision passed to `commit`, not the new evaluation at t_L. Under that reading the check is not vacuous. But R2 did not say so, and "outcome ALLOW" in the same rule referred to the new evaluation. The text invites the tautology. **Accept** that it must be rewritten.
- **The deeper point is accepted too:** once Π is re-evaluated inside the critical section at t_L on the same revision, **D_max has no exposure-safety function** (DERIVED, below).

### Definitions (R-12″)

- **t_eval**: the as_of of the decision D that is passed to `commit`. It is set when D is created, outside the critical section, and is immutable.
- **t_L**: the time read from the independent clock **inside** the store's serialized critical section, after the lock is acquired and before the append. This is the linearization point L: the instant the reservation and the AUTHORIZED order are appended and the revision advances.
- **E_L = evaluate(ledger at the current revision, proposal, config, as_of = t_L)**: computed inside the critical section. D is never altered.
- **Evidence freshness** (snapshot age against S_lim, and every Freshness check) uses **t_L**.
- **Decision-to-commit age**, if retained, is **t_L − t_eval**, with t_eval read from D, never from E_L.

**Required structure:** evaluation outside the critical section, then full re-evaluation inside it.
- The outside evaluation is advisory only. Authority comes solely from E_L at L.
- `consume` follows the same pattern, with its own t_L.

### Counterexample C3-a (COMPUTED)

Timestamps:
- D_max = 5 s, S_lim = 60 s; the snapshot is received at t = −10 s.
- D is evaluated at t_eval = 0. No event arrives. The critical section runs at t_L = 8.

| Interpretation | Check | Result |
|---|---|---|
| Intended (R-12″) | t_L − t_eval = 8 − 0 = 8 > 5 | **refuse** (R_DECISION_STALE) |
| Naive (as_of reassigned to t_L) | t_L − t_L = 0 ≤ 5 | pass |
| Freshness, both | snapshot age at t_L = 18 s < 60 | fresh |

**What the difference protects (DERIVED).** In C3-a:
- the revision and item hash are unchanged;
- E_L returns ALLOW at t_L;
- the evidence is fresh at t_L.
So the ledger, the bounds and the evidence are identical to what an immediate commit at t_L would see. Committing would be exposure-safe, and refusing protects nothing that 2.4 accounts for. The only thing D_max still limits is the age of the *proposer's intent*: the market context behind the proposal. Market data is G-05 and out of scope.

**Answer.**
- D_max is **not** an independent exposure-safety constraint under R-12″.
- Recommendation (**FD-10**): either
  - (a) **withdraw D_max** as a safety rule and amend D21 to "commit-time re-evaluation at t_L, with freshness against S_lim at t_L"; or
  - (b) keep it, explicitly labelled a **non-safety intent-age policy** (t_L − t_eval ≤ D_max), evaluated as above. Under that label it cannot collapse, because t_eval is sourced only from D.
- Either way, V44 must be restated. Its "snapshot older than S_lim at commit" half survives; its D_max half becomes policy.

### How external events are represented

- **Reference model (ASSUMED, by construction):**
  - a deterministic scheduler; time is an explicit input that advances only between steps;
  - every broker event or snapshot is one step;
  - steps may interleave between t_eval and lock acquisition, but never inside the critical section;
  - an event that "arrives during" authorization is ordered either before L (so E_L sees it) or after L (so it is a later revision, and R-15′ applies to the new reservation).
- **Production (UNVERIFIED):** this requires a store with serializable appends and a clock read inside the transaction. Events received during the transaction are queued until after it commits. That is a strengthened A-3 and A-4 obligation. The model shows these semantics are coherent; it does not show any real store provides them.

**Baseline:** a Rev 3.2 candidate (2.9 commit steps, I5, D21, V44).

---

## Challenge 4: R-01′ / R-03′ transitions

**Disposition: partially accept.** The combined system is coherent **only with two additions**:
- (i) a **mandatory** stream-epoch id, with event_id stable across epochs; and
- (ii) a rule that a new-epoch snapshot is **compared, not adopted**.

Without the epoch id, a renumbering that restarts at H+1 hides lost events, giving a false permission (C4-R below). The CX-28 correction (section 0) also changes the justification for case 1.

### Contract additions (A-2″, a Rev 3.2 candidate)

1. Every sequenced message carries (epoch, broker_seq). Epochs are totally ordered, and every event of epoch e precedes every event of e′ > e.
2. event_id is stable across epochs, so a re-sent historical event keeps its id.
3. The ledger has an **opening item** at bootstrap: position F_b(S0) with broker_seq W0 in epoch e0. Rev 3.1 never defines bootstrap (verified by reading 2.2 and 2.6.2). Without this item, F_d(W) is undefined.
4. For a snapshot in epoch e′, F_d(W′) = all applied events of earlier epochs, plus events of e′ with seq ≤ W′.

### Transition table

H, M and G as in R1 and R2: H = highest contiguous received number, M = highest received number, G = recorded holes. W is the accepted snapshot watermark. "Auth?" means whether authorization is possible.

| # | Prior | Incoming | Disposition | Affects position? | H / M / W after | Status | Auth? |
|---|---|---|---|---|---|---|---|
| 1 | e, W0 = 500, H = M = 505, W = 500 | event (e, s = 480), unseen id | **SEQ_CONTRACT** (not applied) | no | unchanged | UNBOUNDED (structural) | no |
| 2 | H = 505 | (e, 505), same id and payload | idempotent | no | unchanged | unchanged | unchanged |
| 3 | H = 505 | (e, 505), different id or payload | CONFLICT | no | unchanged | UNBOUNDED | no |
| 4 | H = 505, M = 507, G = {506} | (e, 506) | applied; buffered 507 then applied | yes | H = M = 507 | recomputed | if BOUNDED |
| 5 | H = M = 505 | (e, 508) | buffered | no (until applied) | H = 505, M = 508, G = {506, 507} | GAP | no |
| 6 | H = 505, W0 = 500 | (e, 1), (e, 2) … same epoch label | s ≤ W0 gives SEQ_CONTRACT; s in (W0, H] gives CONFLICT | no | unchanged | UNBOUNDED | no |
| 6′ | H = 505 | **same-epoch renumbering that restarts at 506** after the old 506 was lost | indistinguishable from normal continuation | yes, wrongly | H = 506 | as if contiguous | **yes: false permission (C4-R)** unless A-2″ (1) holds |
| 7 | W = 500 in e | snapshot (e, W′ = 7), newer received_at | with a broker-side as_of older than the accepted snapshot: **REPLAY, corroboration only** (recorded, no state change, never replaces d). With a newer broker as_of or none: **SEQ_CONTRACT** | no | unchanged | REPLAY: unchanged. SEQ_CONTRACT: UNBOUNDED | REPLAY: unchanged. SEQ_CONTRACT: no |
| 8 | e: H = 501, M = 503, G = {502} | first message of e′ > e | e frozen; e′ messages buffered pending bootstrap | no | e: H_e = 501, M_e = 503, G_e = {502}; e′: none | UNKNOWN, and UNBOUNDED while G_e ≠ ∅ | no |
| 9 | as 8, or G_e = ∅ | accepted snapshot (e′, W0′) | **compared, not adopted**: d = F_b′ − F_d(all e events + e′ events ≤ W0′) | via d | e′: W0′ becomes its bootstrap | G_e ≠ ∅: still UNBOUNDED (a snapshot never clears a hole). G_e = ∅: RECONCILED or MISMATCH | only if G_e = ∅ and BOUNDED |
| 10 | any | delivered execution with no broker_seq | applied if associated (otherwise an orphan with T3/T4 enumerated); no effect on H or M | yes | H / M unchanged | MISMATCH if any inclusion choice gives d ≠ 0 | reductions by A (D19); increases blocked |

**Case 1, justification (DERIVED).**
- *Applying* the event: if it is a genuine old event already in S0, the result is a bounded but permanent MISMATCH (section 0). If it is a reset event, the result is a bounded MISMATCH **that hides the reset**. Gap detection is then disabled for the old numbering, a later tail loss is invisible, and D19 still allows reductions.
- *Ignoring* the event: if it is a reset event, a real execution is dropped (omission).
- So only failing closed is safe in both readings.

**A late tail event from an old epoch.** An event (e, s) with s > M_e that arrives after e′ has begun is a legitimate late event of e. Under A-2″ (1) it is ordered before e′: it is applied, and d against the e′ snapshot is recomputed. That is coherent, and it is impossible without the epoch label (DERIVED).

### Required counterexamples

- **A. Pre-bootstrap double counting.**
  - S0: W0 = 500, F_b = 100, opening item 100. #480 (a sell of 10, inside S0) arrives.
  - Rev 3.1: applied, giving F_d = 90, F_d(W) = 90 and d = +10, so MISMATCH with U = 100 and A_raw = 90. Conservative but permanent (COMPUTED).
  - R-03″: SEQ_CONTRACT, so UNBOUNDED until reconciled. Safe, and it does not hide a reset.
- **B. Epoch transition with unresolved holes.**
  - e: H = 501, M = 503, G_e = {502}, where #502 was an external sell of 50 and was never delivered.
  - e′ begins; snapshot (e′, W0′) with F_b′ = 50 while F_d = 100.
  - The comparison gives d = −50, so F_min = 50 (COMPUTED). But G_e ≠ ∅, so the status stays **UNBOUNDED** (DERIVED: under W1-F nothing bounds #502, the same reasoning as F-4 and V48).
  - **A new epoch cannot restore boundedness without resolving the old epoch's holes.** Once #502 arrives (as e, 502), or an authoritative execution list covers it, G_e = ∅ and the status becomes MISMATCH or RECONCILED.
- **C. Lower-watermark snapshot.**
  - Accepted (e, W = 500); then (e, W′ = 7) arrives later.
  - It is not corroboration of the current state, because it describes an earlier point.
  - It is not a rebase, because rebasing is unsound under W1-F (R2, answer D).
  - It is corroboration of the *past* only if a broker-side as_of proves it older. Otherwise it is evidence of a renumbering, so SEQ_CONTRACT.
  - A new epoch is declared only by an epoch id, never inferred from a lower watermark.
- **D. Unsequenced delivered execution.**
  - RECONCILED at W = 100, F_b = F_d = 100. A sell of 10 for a known working order is delivered with no broker_seq and applied, so F_d = 90.
  - Inclusion choices give d ∈ {+10, 0}, so d_plus = 10, d_minus = 0, F_max = 100, F_min = 90 (COMPUTED). True P ∈ {90, 100}, so both bounds hold.
  - The status is MISMATCH; increases are blocked and reductions are limited by A = 90 − S.
  - H and M are unchanged. The contiguous sequence says nothing about this event, and the model never infers completeness from it (DERIVED). Permanent MISMATCH: FD-3, CX-21.
- **C4-R. Same-epoch renumbering that restarts at H+1** (the remaining false-permission path).
  - H = 503, F = 100, RECONCILED, no orders.
  - The broker's original #504 (an external sell of 50) is lost. The session resets without an epoch change, and the new numbering restarts at 504 with an acknowledgement for another order.
  - The model sees 504 as contiguous: no GAP, A = 100, so a sell of 80 is ALLOWED against a true position of 50, an **oversell of 30** (COMPUTED).
  - This is an A-2 contract violation that **no rule can detect** without the epoch id. With A-2″ (1), the new session is (e′, 504), which leads to case 8, then case 9 with d = −50 (DERIVED).
  - Even with epochs, the lost (e, 504) is a *tail* loss of e, so only the e′ snapshot's d reveals it. This is A-12 territory, made visible by the mandatory re-comparison.

**Answer.** With A-2″ (a mandatory epoch id, cross-epoch stable ids, an opening item and the epoch ordering) and R-03″ (the table above), the system is coherent across bootstrap, gaps, resets and epochs. Within that contract I found **no path to double counting, omission or false permission** (DERIVED, not executed).

What remains outside the contract:
- A-12 tail loss;
- an unlabelled renumbering (C4-R), which violates A-2″ and is undetectable by construction;
- re-sends under new ids (A-11);
- common mode (W1).

**Baseline:** a Rev 3.2 candidate (2.2 bootstrap, A-2, 2.6, 2.6.2, 2.6.3).

---

## Cross-check: are the four corrections consistent with each other? (DERIVED)

- **R-15′ with R-03″:** SEQ_CONTRACT and UNKNOWN make the band UNBOUNDED, so Π fails and every reservation is suspended in the same revision. Consistent.
- **R-15′ with R-12″:** suspension is computed in the event-apply step, and consume and commit re-evaluate Π at their own t_L. Both run inside store serialization. Consistent.
- **R-07″ with R-15′:** a per-order list exit is a revision step, so Π is re-evaluated. Consistent.
- **R-07″ with A-2″:** the multiplicity problem exists only for unsequenced, id-less deliveries. FD-8 (out of contract) removes it.
- **One tension:** FD-3 "permanent MISMATCH" combined with R-15′ means unsequenced executions permanently suspend buy reservations. That makes FD-3 effectively "unsequenced executions are out of contract for increases".
- **One editorial consequence:** V44 and D21 must change together with R-12″ (FD-10).

---

## Final disposition

| Challenge | Resolved? | Evidence level | Remaining blocker |
|---|---|---|---|
| R-07′ multiplicity | **Exit withdrawn.** Replaced by R-07″ (per-order execution list with ids and a watermark), or by FD-8 (id-less unsequenced deliveries out of contract) | DERIVED; counterexample COMPUTED | FD-8; broker capability UNVERIFIED |
| R-15 symmetry / reactivation | **Yes, as R-15′** (adds OVER_LIMIT, the SUSPENDED state, a complete Π for reactivation) | DERIVED; ledgers COMPUTED | FD-9 (suspension scope) |
| R-12′ / D_max | **Yes, as R-12″.** D_max shown to have no exposure-safety role; withdraw or relabel | DERIVED; timestamps COMPUTED | FD-10 (withdraw vs policy); production atomicity UNVERIFIED |
| R-01′ / R-03′ transitions | **Yes, conditional on A-2″** (mandatory epoch, stable ids, opening item, compare-not-adopt). CX-28 corrected | DERIVED; values COMPUTED | FD-2″ (epoch mandatory); broker epoch semantics UNVERIFIED |

1. **Does any challenge still permit a concrete false-authorization path?** Inside the proposed Rev 3.2 contracts: none found (DERIVED, not executed). Two paths survive *outside* them, both undetectable by construction and so recorded as contract boundaries:
   - C4-R, an unlabelled renumbering, which violates A-2″;
   - C1-a's later-delivery double count, which arises if a naive exit is ever used, or if FD-8 is rejected without R-07″.
   A-12 (CX-01), A-11 (V56) and W1 common mode remain documented limitations.
2. **Are the four corrections consistent with each other?** Yes, with the FD-3 / R-15′ interaction noted (DERIVED).
3. **Is there sufficient basis to authorize controlled Rev 3.2 drafting?** **Yes, once FD-2″, FD-8, FD-9 and FD-10 are decided.** The open items are now governance choices, not unresolved technical questions. "Drafting" means a candidate text for hostile review, not a freeze. That recommendation is the reviewer's position; the decision is the founder's.
4. **What stays NO-GO regardless?**
   - any reference implementation or oracle execution before Rev 3.2 is frozen, counter-reviewed and the 5.7 prerequisites are met;
   - any broker contact: A-2″, A-11, A-12 and A-7 are unvalidated, and D23 and D24 are undecided;
   - paper and live trading;
   - any claim that the model, the oracle or this review is verified. Everything above is hand derivation plus throwaway arithmetic by a single author, cross-checked only by other models.

**New founder decisions:**
- **FD-8:** id-less unsequenced deliveries out of contract (recommended), or R-07″ per-order list reconciliation.
- **FD-9:** R-15′ suspends all failing reservations (recommended), or newest first.
- **FD-10:** withdraw D_max as a safety rule (recommended), or keep it as a labelled intent-age policy.
- **FD-2″:** a mandatory epoch id with cross-epoch stable event ids (this replaces FD-2′'s options, because option (b) is now required).

Still open from R2: FD-1′, FD-3, FD-4′, FD-5, FD-6 and FD-7. FD-6 becomes moot under FD-8.

*Agreement among Claude, GPT and Gemini is not independent verification. Nothing here was executed except hashing and the throwaway arithmetic marked COMPUTED.*
