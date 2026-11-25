# EAR v0.1: Final Clarification Pass. Response and Rev 3.2 Candidate Amendments

SPECIFICATION REVIEW ONLY. Rev 3.1 (`dd9d87f7…`, commit d4c9e66) stays frozen and unmodified. This document is **candidate** Rev 3.2 language for hostile review. It is not a freeze and does not authorize implementation, oracle execution, broker contact, paper or live trading.
Reviewer: Claude (Specification Lead / ARBITER). Prepared 2026-11-24 (ET) in response to the dispatch dated 2026-11-25.
Prior documents: R1, the review (`39c224a3…`); R2, the counter-review response (`e53d96ef…`); R3, the four-challenge response (`1aef01e9…`).

**Labels.**
- **DERIVED**: follows from stated definitions and assumptions.
- **COMPUTED**: integer arithmetic run in a throwaway Python script on hand-specified ledgers using the Rev 3.1 section 2.4 formulas. It establishes arithmetic only, not model correctness.
- **ASSUMED**, **CONDITIONAL**, **UNVERIFIED**: as before.

No oracle exists or was run. The transition tables are hand-derived.

---

## Deliverable 1. Four-point technical response

### Challenge A: R-07″ reconciliation and global execution identity

**Disposition.** Resolved by one rule: an execution has exactly **one accounting identity**, its broker execution id, held in a single **execution registry**. Stream deliveries and reconciliation-list entries are two ways of reporting the same registry entry. **Neither one adds quantity on its own.** Quantity enters F_d only through the registry entry's current version (DERIVED).

**Answers to the eight questions.**

1. **Sequence domain.** The candidate requires (A-11″, R-07″) that each list entry carries its execution's **global key** (epoch, broker_seq), and that the list watermark is a global key (e, W_o). Same domain.
   - If a broker cannot supply this, the list is **reduced-capability**. Its new executions are treated as *unsequenced* applied executions (2.2 interval, so usually MISMATCH and increases blocked), and absence conflicts cannot be detected (question 7).
   - No contract failure is declared, because identity still works. Only timing and completeness checks are lost (DERIVED).
2. **Execution-id scope.** Required to be **unique per account, across orders and epochs** (A-11″).
   - Ids unique only per order are acceptable only through the composite key (order_id, exec_id), and only for executions whose order is known.
   - An execution of an unknown order whose id is not account-unique has no usable identity. It is held as T2-U (UNBOUNDED).
3. **Stream first, list later.** The list entry's id is found in the registry. Same version means no-op. A higher list version is applied as a replacement under the D27 rules. A lower list version is stale if W_o is below the key of the correction already applied, and a **CONFLICT** if W_o is at or above it.
4. **List first, stream later.** The stream delivery's exec_id is found in the registry. Same version means idempotent, with no quantity change. Message identity (event_id) is separate from accounting identity (exec_id), so a new event_id does not create a new execution.
5. **Corrections and busts.** A CORRECT or BUST acts on the registry entry named by ref_exec_id and replaces its current version (D27). Whether it arrives by stream or appears as the list's current version, it is the same version transition, keyed by (exec_id, version). A version already present is never applied twice.
6. **An id in the list not seen before.** Inserted into the registry as applied, at its global key, in one revision step. If its key falls inside a recorded hole, it fills that number. If the key exceeds M, it raises M, which can create new holes and therefore GAP.
7. **An applied id missing from a list that claims completeness.** If the execution's key is ≤ W_o, this is a **structural CONFLICT** for that order: UNBOUNDED, both sides blocked, until an authoritative resolution. If its key is > W_o, no conflict, because the list was not complete that far.
8. **A later stream event relative to W_o.** If key > W_o, it is a normal new delivery. If key ≤ W_o and its id is in the list, idempotent. If key ≤ W_o and its id is not in the list, **CONFLICT** (the list claimed completeness).

**Counterexample A-1 (COMPUTED). Every step.**

Setup:
- Bootstrap opening item 100 at (e0, 500).
- Our working buy O1, quantity 50. No sells.
- L = 200. Snapshot S0 at W0 = 500.

| Step | Evidence | Registry (O1) | F_d | net_cum | R = B | U | A_raw | H / M | Status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | stream (e0, 501) NEW X1 buy 10 | X1 v0: 10 | 110 | 10 | 40 | 150 | 110 | 501 / 501 | AWAITING |
| 2 | list for O1, complete through (e0, 505): X1 v0 at 501, X2 v0 at 503, X3 v0 at 505 | X1 matched (no-op); X2 and X3 inserted | 130 | 30 | 20 | 150 | 130 | 501 / 505 | **GAP** (holes 502, 504) |
| 3 | stream (e0, 502) other order's ack; (e0, 503) X2; (e0, 504) ack; (e0, 505) X3 | X2 and X3 found by id: **idempotent** | 130 | 30 | 20 | 150 | 130 | 505 / 505 | AWAITING |
| 4 | stream (e0, 506) CORRECT X2, prior_version 0, prior_qty 10, qty 6 | X2 v1: 6 | 126 | 26 | 24 | 150 | 126 | 506 / 506 | AWAITING |
| 5 | stream (e0, 507) BUST X3 | X3 v1: busted (0) | 116 | 16 | 34 | 150 | 116 | 507 / 507 | AWAITING; snapshot (e0, 507) with F_b = 116 → RECONCILED |

What the table shows:
- **No execution is added twice.** In step 3, X2 and X3 arrive by the second path and change nothing.
- **None is omitted.** X2 and X3 are counted from step 2.
- **None is treated as new by mistake.** Matching is by id, not by event_id.
- **The list does not falsely bound the state.** Step 2 reveals numbers 502 and 504, so the status is GAP until they arrive.
- U stays at 150 throughout. Fills and corrections on a known working buy move quantity between F_d and R, and U is invariant to that (I1a).

**Variants (DERIVED).**
- (a) A list for O1 complete through (e0, 505) **without X1** → CONFLICT on O1 → UNBOUNDED.
- (b) A later list showing X2 v0 with W_o ≥ 506 → CONFLICT, because the list contradicts a correction it should already contain.
- (c) A later list showing X2 v0 with W_o = 505 → the entry is stale and is ignored for X2. The registry keeps v1.

**Acceptance criterion: met (DERIVED)**, *conditional on A-11″* (account-unique, stable execution ids and global keys on list entries). Without A-11″, the reduced-capability rule in question 1 applies.

---

### Challenge B: R-15′ reservation accounting and lifecycle

**Disposition.** Resolved. The commitment is carried by **one accounting object, the order's remaining quantity R**, which already exists in Rev 3.1 (2.2: R for AUTHORIZED, …, UNKNOWN). Reservation states are **capabilities attached to that order and never accounting terms**.
- So a change of lifecycle state cannot change B or S (DERIVED).
- The proposed invariant is adopted as stated, with that mechanism.
- **Consequence: FD-9 is moot.** Since suspension never removes quantity, every reservation on the affected side fails Π identically (Π uses the aggregate). There is no subset to choose.

**Lifecycle and accounting.**

| Reservation state | Order state | Counted in B or S | Capability | Leaves by |
|---|---|---|---|---|
| ACTIVE | AUTHORIZED | **yes**, R = qty | may be consumed | consume → CONSUMED; ¬Π → SUSPENDED; expiry → EXPIRED; release → RELEASED |
| SUSPENDED | AUTHORIZED | **yes**, R = qty (unchanged) | none | Π holds at a revision → ACTIVE; expiry → EXPIRED; release → RELEASED |
| CONSUMED | SUBMITTED, then ACKNOWLEDGED, PARTIALLY_FILLED or CANCEL_PENDING (or UNKNOWN) | **yes**, R = qty − net_cum, the same order record | none (spent) | order terminal → RELEASED (R = 0) |
| EXPIRED (terminal) | AUTHORIZED → EXPIRED (T05) | no: R released in the same revision step | none | — |
| RELEASED (terminal) | FILLED, CANCELED, REJECTED or broker EXPIRED; or withdrawn before consume | no: R = 0 | none | — |

What the table establishes:
- **AUTHORIZED → SUBMITTED is the same order id, so R is unchanged** (T04). There is no double count and no gap.
- Partial fills move quantity from R into F_d (I1a, I1b).
- Cancel confirmation and rejection release R under the terminal rules.
- **New: `release(reservation_id)`**, the proposer withdrawing its own unconsumed reservation, is allowed in ACTIVE or SUSPENDED. It can only reduce committed exposure, so it can never weaken safety (DERIVED).

**Π, stated so the candidate is counted exactly once (R-15″).** For an unexpired reservation r on order o_r at revision ρ, *every* unexpired reservation, ACTIVE or SUSPENDED, and every working order is already inside B(ρ) and S(ρ) through its R. Then:
- **buy r:** U(ρ) = F_max(ρ) + B(ρ) ≤ L. This is the same as U(ρ) − R(o_r) + Q_r ≤ L, i.e. the fresh-commit test with r excluded and then added once, because R(o_r) = Q_r for an unconsumed reservation;
- **sell r:** A_raw(ρ) = F_min(ρ) − S(ρ) ≥ 0, the same as Q_r ≤ A computed with r excluded;
- **and every other predicate:** BOUNDED; no structural failure (including SEQ_CONTRACT, CONFLICT and the D26/D27 holds); Consistency CORROBORATED; Freshness FRESH at the evaluation time; not OVER_RESERVED; not OVER_LIMIT; and the side blocks of 2.7.

Because Π is a test on the aggregate, it cannot leave out another SUSPENDED reservation or count r twice (DERIVED).

**Counterexample B-1 (COMPUTED).** L = 150; buy reservations r1 = 30 and r2 = 30.
- Reading of the dispatch: "current upper exposure 100" is taken as F_max **after** the correction. Before it, F_max = 90, so both reservations were valid when committed. A sell fill of 10 is busted, raising F_max from 90 to 100.

| Step | F_max | B | U | Π(r1), Π(r2) | Result |
|---|---|---|---|---|---|
| Before the correction, both ACTIVE | 90 | 60 | **150** ≤ L | both hold | — |
| Correction applied | 100 | 60 | **160** > L | both fail | OVER_LIMIT raised; both SUSPENDED **in the same revision** |
| After suspension | 100 | **60** (unchanged) | **160** | both fail | suspension released nothing |
| *Naive: suspension releases quantity* | 100 | 0 | 100 | would hold | wrong |
| *Naive: reactivate r1, counting only ACTIVE others* | 100 | 30 | 130 | "holds" | wrong |
| *Naive: then reactivate r2 the same way* | 100 | 60 | 160 > L | — | **limit breached by 10** |
| r2 expires (or is released) | 100 | 30 | 130 ≤ L | Π(r1): limit holds; then BOUNDED, fresh, no increase block, no OVER_LIMIT are checked | if all hold, r1 → ACTIVE; otherwise it stays SUSPENDED |

**Mirror case, reductions (COMPUTED).** Sell reservations of 60 and 60.
- Before: F_min = 120, so A_raw = 0.
- A buy fill of 20 is busted: F_min = 100, A_raw = −20, OVER_RESERVED, and both are SUSPENDED (still counted, so A_raw stays −20).
- Neither can reactivate.
- One expires: S = 60 and A_raw = 40, so Π for the other passes the arithmetic part. It reactivates only if every other predicate holds.

**Acceptance criterion: met (DERIVED).**

---

### Challenge C: R-12″ and external chronology

**Disposition.** Accepted as a **limitation that cannot be closed inside the model**, plus one finding.
- R-12″ serializes Sentinel's *internal* decisions. It says nothing about when broker events occur.
- **Finding:** Rev 3.1 never states the assumption this case actually rests on, **account exclusivity**: all executions on the account come from orders the model knows about. This is proposed as A-15 (ASSUMED, new).

**The nine events, and which timestamps exist.**

| # | Event | Timestamp | Authoritative for | Missing, delayed or untrusted? |
|---|---|---|---|---|
| 1 | External execution occurs | broker execution time (in the payload, if any) | nothing in the model; a broker claim | may be missing; broker clock; never used to order authorization |
| 2 | Broker publishes the notification | broker send time, if any | nothing in the model | as 1 |
| 3 | Sentinel receives it | received_at (independent clock, A-4) | receipt only | delayed relative to 1 by an unknown, unbounded latency |
| 4 | Applied to the ledger | log position, revision | the processing order (D20) | — |
| 5 | Authorization evaluated | t_eval (independent clock) | the age of the decision | — |
| 6 | Authorization committed | t_L (inside the critical section) | the commit instant and freshness | — |
| 7 | Order submitted | EV-req, EV-clk at consume | our action | — |
| 8 | Broker accepts | broker ack time / EV-msg | a broker claim, received later | delayed |
| 9 | Later execution, correction or bust | as 1 to 4 | as 1 to 4 | as 1 to 3 |

Only times on Sentinel's clock (3 to 7) are authoritative within the model, and only for *Sentinel's* events. **Broker-side times are evidence claims.** They are never used to order or authorize anything (DERIVED from 2.8 and A-4).

**Counterexample C-1 (COMPUTED).** Start: F_d = 100, RECONCILED, a fresh snapshot, no working orders.

| Time | Event | Reconstructed | Actual external |
|---|---|---|---|
| 10:00:00.100 | broker executes an **external** sell of 40 (no known order); notification delayed | F_d = 100, A = 100 | P = 60 |
| .200 | Sentinel evaluates a sell of 80 | A = 100 → ALLOW | — |
| .250 | commit at t_L: revision unchanged, fresh → **committed**, S = 80 | A_raw = 20 | actual A = 60 − 80 = **−20** |
| .300 | notification arrives: orphan T1 sell of 40 | F_min = 100 − 40 = 60; S = 80; A_raw = 60 − 80 = **−20** → OVER_RESERVED | P = 60 |

1. **Reconstructed position at commit: 100. Actual: 60.**
2. **Does the current model permit it? Yes.** It is correct given everything Sentinel had *received*.
3. **Does the later notification detect it? Yes, at .300**, and only if it is delivered at all (A-12).
4. **Can the reservation be suspended?** Yes, if it is still unconsumed: R-15″ suspends it in the .300 revision.
5. **What if it was consumed or submitted before .300?** It cannot be recalled (I8). If accepted but not executed, only detection is possible; cancellation is G-07. If executed, the true position is 100 − 40 − 80 = **−20**, a short in the long-only envelope. The next snapshot is negative (V54), giving UNRESOLVED. Containment is G-06.

**Contrast C-2 (COMPUTED).** The delayed execution is a fill of **our own** working sell of 60.
- Model: A = 100 − 60 = 40, so a sell of 30 is ALLOWed.
- Truth: P = 40, R = 0, so true A = 40 ≥ 30. **Safe:** W4 covers unreported fills of known working orders, at any delay.

**Analysis.**
- **R-12″ guarantees:**
  - every commit is decided on exactly the evidence received by t_L;
  - the evidence is fresh at t_L;
  - no internal event interleaves inside the commit.
- **It cannot guarantee** that every external execution before t_L was received by t_L.
- **Which assumption covers this?** W2 ("no unevidenced execution after W is modeled") and A-12. As worded, A-12 is about *completeness* between snapshots, not *timeliness* at the decision.
  - The candidate restates A-12 as **A-12″: complete as of evaluation time**. That is unachievable with nonzero latency for any execution outside a known working order.
  - So the real requirement is **A-15 (account exclusivity)**. Under A-15 every execution is a fill of a known working order, W4 covers every delay, and C-1 is excluded by assumption, not by mechanism.
- **External mechanisms that would strengthen this (all UNVERIFIED; none is claimed to exist):**
  - a broker-side pre-trade position or no-short check, which would turn C-1 into a broker reject;
  - a broker "position barrier" or high-water sequence query at commit, which narrows the window but cannot close it;
  - a dedicated sub-account that only EAR can trade, which is the operational form of A-15.
- **Without any such mechanism, the model must:**
  - state A-15 as an environmental assumption;
  - record C-1 as a documented limitation (vector V67);
  - on detecting a violation (any execution for an unknown order), apply FD-11: either (a) the existing bounded orphan treatment, or (b) treat it as an **exclusivity violation**, a structural failure that blocks both sides until reconciled. Under (b), once one external execution is seen, further undelivered ones are assumed possible.

**Acceptance criterion: met by statement, not by mechanism.** The candidate text (A-12″, A-15, the 2.9 note) says explicitly that internal serialization does not establish external completeness. It separates *correct reconstruction of received evidence* from *complete reconstruction of what occurred*.

---

### Challenge D: A-2″ bootstrap and cross-epoch reconstruction

**Disposition.** Resolved, with an explicit reconstruction equation. Two clarifications follow from it:
- (i) Only the **bootstrap** epoch uses a watermark baseline (W0). A later epoch's numbers are all deltas, so its holes start at its first number, not at its snapshot watermark.
- (ii) A correction of a *pre-bootstrap* execution has no registry entry, so it is held as T2-U (UNBOUNDED) until resolved. That is an availability cost.

**Definitions (DERIVED).**
- **Key order:** a global key is κ = (e, s). The order is lexicographic: (e, s) < (e′, s′) iff e < e′, or e = e′ and s < s′.
- **Opening item:** the bootstrap snapshot S0 = (e0, W0, F_b0), with boundary β0 = (e0, W0) and opening position **P_open = F_b0**. P_open is a baseline, not an execution, and it never changes afterwards.
- **Represented in the opening:** every event with κ ≤ β0. Such events are never added. On receipt they are SEQ_CONTRACT (R3, case 1), never applied.
- **Deltas:** every applied event v with κ(v) > β0, plus unsequenced applied executions (κ = ⊥, unknown timing).
- **Reconstruction:**
  ```
  F_d = P_open + Σ_{v applied, κ(v) > β0} δ(v)  +  Σ_{u applied, κ(u) = ⊥} δ(u)
  δ(NEW x) = signed qty of version 0;  δ(CORRECT) = signed (qty − prior_qty);  δ(BUST) = − signed current qty
  ```
  Equivalently, F_d = P_open + Σ over registry entries of their signed current-version quantities, with each entry's version transitions placed at their own keys.
- **Comparison at a snapshot boundary β = (e, W):**
  ```
  F_d(β) = P_open + Σ_{v applied, β0 < κ(v) ≤ β} δ(v)   (+ the unsequenced inclusion choices of 2.2)
  d = F_b − F_d(β)
  ```
  Because every key of an earlier epoch is below every key of a later one, β = (e1, W) includes **every** applied e0 event with κ > β0.
- **Holes per epoch:**
  - for e0: H_e0 = the largest h ≥ W0 such that every number in (W0, h] has been received;
  - for e ≠ e0: H_e = the largest h ≥ s_e − 1 such that every number in [s_e, h] has been received, where s_e is the epoch's declared first number (contract; default 1);
  - M_e = the highest received number in epoch e.
- **Status:** **GAP iff H_e < M_e for any epoch e**, or a snapshot's boundary β = (e, W) has W > H_e.
- **Snapshots in a later epoch are compared, never adopted.** No new P_open is set at an epoch change.
- **Late events of an old epoch** (e0, s):
  - s ∈ hole → it fills the hole;
  - s > M_e0 → it is a tail event, applied and placed below every e1 key;
  - s ≤ W0 → SEQ_CONTRACT.

**Counterexample D-1 (COMPUTED).** P_open = 100 at β0 = (e0, 500). No reservations. Our buy order O5 (quantity 10) appears in e1.

| Step | Evidence | F_d | Comparison | H / M per epoch | Status | Authorization |
|---|---|---|---|---|---|---|
| 0 | bootstrap S0 (e0, 500), F_b = 100 | 100 | d = 0 | e0: 500 / 500 | RECONCILED | allowed (U = A_raw = 100) |
| 1 | (e0, 501) buy 20 | 120 | — | e0: 501 / 501 | AWAITING | allowed |
| 2 | (e0, 503) ack; #502 (a sell of 30) missing | 120 | — | e0: 501 / 503 | **GAP** | none |
| 3 | e1 begins; (e1, 1) buy 10 fills O5 | 130 | — | e0: 501 / 503; e1: 1 / 1 | GAP | none |
| 4 | snapshot (e1, W = 1), F_b = 100 | 130 | F_d(β) = 100 + 20 + 10 = 130, so d = −30 (recorded) | unchanged | **GAP persists**: a snapshot never clears a hole | none |
| 5 | late (e0, 502) sell 30 fills the hole | 100 | F_d(β) = 100, so **d = 0** | e0: 503 / 503 | RECONCILED (vs (e1, 1)) | allowed |
| 6 | (e1, 2) sell 5 | 95 | — | e1: 2 / 2 | AWAITING | allowed |
| 7 | snapshot (e1, W = 2), F_b = 95 | 95 | d = 0 | — | RECONCILED | allowed |

The six required properties (DERIVED and COMPUTED):
1. **Events in the opening are not added again.** Nothing with κ ≤ (e0, 500) is applied.
2. **Post-opening events are counted exactly once.** 501, 502, 503 and (e1, 1), (e1, 2) each appear once in the sum.
3. **The missing old-epoch event prevents false boundedness.** Steps 2 to 4 are GAP.
4. **The new-epoch snapshot cannot erase the hole.** Step 4 keeps GAP and records d = −30.
5. **After resolution the comparison is correct.** Step 5 gives d = 0.
6. **There is no restart from zero.** P_open = 100 is carried into e1. A naive restart would show F_d = 10 after step 3 against a true 100.

**Naive adopt (COMPUTED).** Setting F_d := 100 at step 4 and then applying the late sell at step 5 gives 70 against a true 100, a double count of the 30. This is the reason the rule is compare, not adopt.

**Acceptance criterion: met (DERIVED)**, conditional on the A-2″ contract items: epoch ordering, declared epoch start, cross-epoch stable ids, opening item.

---

## Deliverable 2. Candidate Rev 3.2 amendments (affected text only)

Each block names the Rev 3.1 location it would replace or extend. None of this text is in force.

**CA-1. 2.2: identities, registry, epochs, opening item (new subsection "Identity and reconstruction").**
> *Message identity* is event_id. *Accounting identity* of an execution is its broker exec_id, unique per account across orders and epochs (A-11″).
> The **execution registry** holds one entry per exec_id: (exec_id, order_id or null, side, instrument, global key κ of its NEW event or ⊥, current version, current quantity). F_d is computed only from the registry and the opening item.
> A *global key* is κ = (epoch, broker_seq), ordered lexicographically.
> The **opening item** is P_open = F_b of the bootstrap snapshot at β0 = (e0, W0). It is a baseline, not an execution.
> F_d = P_open + Σ_{v applied, κ(v) > β0} δ(v) + Σ_{κ(u) = ⊥} δ(u), and F_d(β) = P_open + Σ_{β0 < κ(v) ≤ β} δ(v), with the unsequenced inclusion choices.
> An event with κ ≤ β0 is never applied.

**CA-2. 2.11: A-2 replaced by A-2″.**
> Where present, broker_seq is drawn from one contiguous integer sequence per (account, epoch), numbered at the source, starting at the epoch's declared first number s_e.
> Every sequenced message carries its epoch id. Epochs are totally ordered, and every event of epoch e precedes every event of e′ > e.
> The contract names the message classes that consume numbers (R-08).
> A watermark W of epoch e means the snapshot reflects exactly the executions with κ ≤ (e, W), including every event of earlier epochs.
> Delivery to the model is **not** assumed.

**CA-3. 2.11: A-11 replaced by A-11″.**
> exec_id is broker-unique per account, stable across epochs and delivery paths (stream, reconciliation list).
> event_id is message identity only.
> A delivery with neither exec_id nor broker_seq is **out of contract** (FD-8, recommended) and is held as a structural failure on the affected side until per-order reconciliation.

**CA-4. 2.11: A-12 replaced by A-12″, and A-15 added.**
> **A-12″.** Every execution that occurred at the broker before an evaluation time t, other than fills of known working orders (W4), has been received by t. Snapshot freshness, contiguity through W, internal serialization (R-12″) and reconciliation do not establish this. Its failure can invalidate both bounds and reduction permission in every status, including RECONCILED.
> **A-15 (account exclusivity, E).** Every execution on the account results from an order known to the model: reserved, working or UNKNOWN. Under A-15 and W4, a delayed notification never creates a false permission. A-15 is not established for any real account. It is the operational precondition for treating A-12″ as plausible.

**CA-5. 2.4.1 item 6: reconciliation-list exit (R-07″).**
> An **authoritative per-order execution list** is (order_id, watermark (e, W_o), a set of entries (exec_id, κ, side, current version, current quantity)). It is applied in one revision step, by exec_id, as follows:
> - an entry's exec_id is in the registry at the same version: no change;
> - at a higher version: version replacement under D27;
> - at a lower version: stale if κ(correction) > (e, W_o), else CONFLICT;
> - an exec_id not in the registry: inserted as applied at κ; this fills a hole if κ is in one; it raises M if κ > M;
> - an applied execution of the order with κ ≤ (e, W_o) that is absent from the list: CONFLICT for the order;
> - held id-less items on the order: dismissed and superseded by the list.
> The list is never an additive source.
> A list without global keys is *reduced-capability*: its new entries are unsequenced applied executions, and absence conflicts are not evaluated.

**CA-6. 2.9: reservation lifecycle and accounting (R-15″).**
> **Invariant:** every unexpired reservation contributes its order's R to B or S, whether ACTIVE or SUSPENDED. Suspension prevents consumption; it does not remove the commitment. Lifecycle changes never change B or S. Only expiry, release and order-terminal transitions release R.
> **States:** ACTIVE, SUSPENDED, CONSUMED (order working), EXPIRED (terminal), RELEASED (terminal). `release(reservation_id)` is allowed in ACTIVE or SUSPENDED.
> **Π(r, ρ):** for a buy r, U(ρ) ≤ L; for a sell r, A_raw(ρ) ≥ 0; with every unexpired reservation and working order already in B or S; plus BOUNDED, no structural failure, Consistency CORROBORATED, Freshness FRESH at the evaluation time, not OVER_RESERVED, not OVER_LIMIT, and the 2.7 side blocks.
> In the same revision step as any applied event or snapshot, every ACTIVE r with ¬Π becomes SUSPENDED. SUSPENDED → ACTIVE only when Π holds.
> `consume` requires ACTIVE and Π at its own linearization point.
> **OVER_LIMIT** iff U > L (added to I3 and I8).

**CA-7. 2.9: commit and consume (R-12″).**
> t_eval is the as_of of the decision passed to `commit` (immutable). t_L is read from the independent clock inside the store's serialized critical section, before the append.
> Inside the critical section the model evaluates E_L = evaluate(…, as_of = t_L), and commits iff E_L = ALLOW on the same revision and item hash, the proposal hash matches, and no reservation exists. Freshness is evaluated at t_L.
> [FD-10 (a): D_max removed as a safety rule. FD-10 (b): t_L − t_eval ≤ D_max, labelled an intent-age policy.]
> expires_at = min(t_L + TTL, snapshot.received_at + S_lim) (FD-7).
> **Note (normative):** serialization orders Sentinel's decisions. It does not establish that external executions before t_L were received by t_L (A-12″, A-15).

**CA-8. 2.6 / 2.6.2: status and sequence transitions (R-01′, R-03″).**
> Per epoch: H_e, M_e and holes as in Deliverable 1, Challenge D.
> **GAP** iff H_e < M_e for some e, or the snapshot boundary (e, W) has W > H_e.
> R3's transition table (cases 1 to 10) becomes normative, with SEQ_CONTRACT a structural Consistency failure.
> A snapshot of a non-bootstrap epoch is compared, never adopted.

**CA-9. 2.10: new vectors (hand-derived, to be frozen with the candidate).**
- V63: CX-01, tail loss in RECONCILED.
- V64: CX-12, later bust after an authorized reduction.
- V65: CX-08, a duplicated sell giving an increase false permission.
- V66: CX-27, a duplicate applied at the exit.
- V67: C-1, a delayed external execution.
- V68: A-1 steps 1 to 5.
- V69: B-1, with its mirror case.
- V70: D-1, steps 0 to 7.
- V71: A-1 variant (a), an absence conflict.
- V72: C-2, a delayed fill of our own order (safe).
- V73: D-1, the naive-adopt double count, as a negative test.

**CA-10. 5.7: test obligations added.**
- registry identity under both delivery orders;
- list stale/conflict versions;
- reservation-state transitions × B/S invariance (B and S must be unchanged by every lifecycle transition except expiry, release and terminal);
- Π aggregate tests including SUSPENDED reservations;
- epoch reconstruction, including late old-epoch tail events;
- corrections of pre-bootstrap executions (T2-U).

---

## Deliverable 3. Cross-interaction review (DERIVED)

| Pair | Interaction | Conflict or dependency |
|---|---|---|
| R-07″ × A-2″ | List entries carry global keys. They can fill holes and can **reveal** holes by raising M (A-1 step 2). A list in an old epoch places its executions below every newer-epoch key | Dependency: the broker supplies keys on list entries, otherwise reduced capability. No conflict |
| R-07″ × R-15″ | A list is a revision step, so Π is re-evaluated. A list that reveals sells lowers A and may suspend sell reservations; one that reveals a hole puts the status to GAP and suspends all | No conflict. This is the intended behaviour |
| R-15″ × R-12″ | Suspension is computed in the apply step; commit and consume test Π at their own t_L. **Snapshot ageing is not a revision step**, so a reservation would not be suspended merely by time passing | Resolved by FD-7 (expires_at bounded by S_lim) or by a time-tick step. **FD-7 becomes required, not optional** |
| R-12″ × A-12 | Serialization does not establish external completeness (C-1). A-12″ states the timeliness requirement; A-15 is what would make it plausible | New assumption A-15 (FD-11). Under FD-11 option (b), many existing orphan vectors (V11, V12, V22–V25) change their reduction outcome to UNRESOLVED |
| A-2″ × bootstrap | Reconstruction equation; only e0 has a baseline; later epochs' numbers are all deltas | Dependency: the declared epoch start s_e. Availability cost: corrections of pre-bootstrap executions are T2-U |
| R-07″ × FD-3 | List entries without keys become unsequenced, so permanent MISMATCH, so buy reservations are permanently suspended under R-15″ | Interaction already noted in R3. Strengthens the case for requiring keys |

**New conflicts found:** none that break consistency.
**New dependencies:** A-15 (FD-11), FD-7 becoming required, and broker capability for keyed lists and epochs (UNVERIFIED).

---

## Deliverable 4. Updated disposition

| Issue | Resolved? | Evidence level | Remaining dependency |
|---|---|---|---|
| R-07″ reconciliation | Yes: one registry identity; the list is never additive; absence and stale rules | DERIVED; A-1 COMPUTED | A-11″ (broker ids and keyed lists, UNVERIFIED); FD-8 |
| R-15′ accounting | Yes, as R-15″: R carries the commitment, states are capabilities, Π is aggregate; FD-9 moot | DERIVED; B-1 and mirror COMPUTED | FD-7 now required; `release` operation (FD-13) |
| R-12″ external chronology | **Limitation stated, not closed.** C-1 is a false permission unless A-15 holds | DERIVED; C-1 and C-2 COMPUTED | A-15 / FD-11; external mechanisms UNVERIFIED |
| A-2″ reconstruction | Yes: explicit equation, per-epoch holes, compare-not-adopt | DERIVED; D-1 COMPUTED | Declared epoch start; FD-2″ |
| Cross-interaction consistency | Consistent, with the dependencies listed | DERIVED | FD-7, FD-11 |

1. **Does any concrete false-authorization path remain within the proposed contracts?** None found **if A-15 is adopted**, alongside A-2″, A-11″ and A-12″ (DERIVED, not executed). **If A-15 is not adopted**, C-1 is a concrete false authorization that the proposed contracts do not exclude except through the timeliness reading of A-12″. That is the same thing stated as an assumption, and it is implausible for any account other parties can trade.
2. **Which paths remain outside the model's guarantees?**
   - C-1 and any violation of A-15;
   - CX-01 tail loss (A-12″);
   - V56 and CX-08 (A-11″ violations);
   - C4-R, an unlabelled renumbering (A-2″ violation);
   - W1 common mode;
   - A-7, state-keeper honesty;
   - CX-12 after consumption (no recall);
   - every consequence once an order has executed (G-06, G-07).
3. **Are the proposed amendments internally consistent?** Yes, with the dependencies above (DERIVED).
4. **Is the candidate ready for independent hostile review?** Yes, as candidate text. Recommended attack points:
   - the list-version rules in CA-5 against interleaved corrections;
   - the Π aggregate under mixed ACTIVE, SUSPENDED and CONSUMED reservations;
   - A-15's interaction with orphan treatment;
   - the per-epoch H with a declared epoch start.
   "Ready for hostile review" is not "verified".
5. **Founder decisions remaining:**
   - **FD-11 (new):** adopt A-15. If adopted, choose the response to a violation: (a) the bounded orphan treatment, as in Rev 3.1; or (b) an exclusivity violation, a structural failure. (b) is safer and changes the orphan vectors.
   - **FD-12 (new):** whether keyed (same-domain) reconciliation lists are mandatory, or reduced-capability lists are allowed.
   - **FD-13 (new):** add the `release` operation (recommended).
   - **FD-7:** now required (expires_at bounded by S_lim).
   - **Carried forward:** FD-2″ (mandatory epoch), FD-8 (id-less deliveries out of contract), FD-10 (D_max), FD-3 (unsequenced executions), FD-1′ (corroboration terminology), FD-4′ (bust limitation), FD-5 (drafting pass).
   - FD-6 and FD-9 are moot.

**Unchanged regardless:**
- no Rev 3.2 freeze without founder approval and a counter-review of this candidate;
- no reference implementation or oracle execution before the freeze and the 5.7 prerequisites;
- no broker contact: A-2″, A-11″, A-12″, A-15 and A-7 are unvalidated, and D23 and D24 are undecided;
- no paper or live trading.

*Agreement among Claude, GPT and Gemini is not independent verification. The only things executed for this document were integer arithmetic (COMPUTED) and hashing.*
