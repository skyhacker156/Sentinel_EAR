# EIVI-1 Deliverable 1: EAR Behavioral Specification (world-set semantics)

**Date:** 2026-11-24
**Author:** Claude, Specification Lead
**Initiative:** EIVI-1, Workstream A
**Classification:** specification and verification planning only. **Not implemented, not executed, not verified, not frozen.**

**Baseline:** Rev 3.1 FROZEN, SHA-256 `dd9d87f76b01134e084827b0202c73c52fccb2b86f21a176a6b6e551241fa239` (unchanged)

**Candidate referenced (comparison only, D4):**
- Rev 3.2 Draft 3: `f647c36bfd4e632052bdcca13eb0b92f64a2964445d0f3021c5ee47f5fdc47ab`
- Draft 4: `a527f26297d83e5d79d8735c5fe833960fa75e359cf15a56c751a89fd6651bfc`

## 0. Independence statement (read first)

This document is written by the author of the candidate. It is therefore **not independent** of the candidate, and agreement between it and the candidate is not verification.

What it does to reduce correlation:
1. It defines every result in terms of a **set of possible worlds** consistent with the evidence and the declared assumptions. It does not use the candidate's bound formulas (F_max, d_plus, Q3, H_Δ), statuses (RECONCILED, GAP, …), or rule numbers. The candidate is one proposed *implementation* of these semantics.
2. Every environmental dependency is a named, switchable assumption (§3). Where two readings give different safety outcomes, both are kept.
3. Where a behavior could not be stated precisely enough to test, it is listed as a **specification defect** (§7), not resolved by choice.

**Residual risk:** the framing below, the choice of world model and the reading of Rev 3.1's requirements all come from one author. An oracle built *from this document by a different party* tests the candidate against this document's semantics. It does not test whether this document's semantics are the right ones; Gemini's challenge (CC) is the check on that.

---

## 1. The central requirement, stated behaviorally

Founder invariant: *no increase in intelligence, no unresolved uncertainty, and no convenience-driven operational transition may silently create or expand execution authority.*

Behavioral reading, used throughout:

- **W(e, A)** is the set of worlds (§2) consistent with the evidence log e under the assumption profile A.
- An action is **justified** at e iff it is safe in **every** world of W(e, A), and W(e, A) is non-empty and determinable (§2.4).
- **Authority** is the set of actions for which a committed, live commitment exists. Nothing else is authority: an evaluation, a model output, a status label, a recommendation or a strategy signal is not.

Safety properties (each test in D3 traces to one or more):

| ID | Property |
|---|---|
| **S1** No unjustified increase | An exposure-increasing action is authorized only if, in every world of W, the post-action worst-case exposure is ≤ L |
| **S2** No unjustified reduction | A reduction is authorized only if, in every world of W, the position after this and every other working reduction stays ≥ 0 (long-only envelope) |
| **S3** No silent expansion | Between log prefixes e and e′, the justified action set may grow only through (a) logged evidence that removes worlds, (b) a logged internal operation that ends a commitment, or (c) a logged, founder-authorized governance or assumption change. The passage of time alone, a reinterpretation, or a model or config change that is not logged as (c) never grows it |
| **S4** Fail closed | If W is empty (the evidence contradicts the assumptions), or cannot be determined, or is unbounded in exposure, no action is justified |
| **S5** Commitment conservation | Every commitment that could still produce exposure in some world is counted in every such world, exactly once, from commit until it provably cannot produce exposure |
| **S6** Reconstruction | Every authorization decision is reproducible from the log prefix it used plus the declared model, assumption and configuration versions, by a party without access to the deciding process |
| **S7** Identity fidelity | Two distinct true transitions are never merged; one true transition is never counted twice |

---

## 2. World model (ground truth that the evidence describes)

### 2.1 Entities

- One account, which only Sentinel trades (assumption E-8), and one instrument per test unless stated. Quantities are integers. Long-only with exposure limit L.
- **True execution** x: a broker-side fill with a true identity and a **true version history** h_x = (t_0, t_1, …). Here t_0 is the original fill and each later t_i is a correction (new quantity) or a bust (quantity 0). Each transition has a true occurrence time.
- **True order** o: side, original quantity, a true lifecycle, and its true executions.
- **True position** P*(τ) at broker time τ: the sum, over true executions, of the quantity of the version current at τ.

### 2.2 Emission and observation

- A true transition may be **emitted** on the stream as a message with epoch and sequence number, delivered once, many times, late, or (only if E-6 is false) never.
- A list response reports some true executions and versions.
- A **snapshot** reports a position. Its relation to P* is assumption **E-4**, which has two readings that are both kept:
  - **E-4P (prefix):** the snapshot at watermark W equals the net effect of exactly the stream events with key ≤ W;
  - **E-4I (instant):** the snapshot equals P*(τ_s) for some broker instant τ_s, with no exact relation to stream keys beyond E-3.
- **Internal operations** (propose, commit, consume, expiry, release, reactivation, migration, finality tick, governance) are **certain**. They are Sentinel's own records, not evidence about the world. Their *consequences at the broker* (did a consumed order reach the broker; was it filled) are world uncertainty.

### 2.3 A world

A world w fixes:
- the true execution set and histories;
- the true order states;
- a mapping from every observed message to the true transition it reports (or to "spurious", only if E-10 is false);
- the emission order and times;
- for each consumed order: transmitted or not, accepted or not, and its fills.

w is **consistent** with e under A iff every observation in e is a correct report of w under the readings A declares, and w violates no assumption in A.

### 2.4 Determinability

W(e, A) is:
- **determinate** if every exposure-relevant quantity has a finite set of values across W, in which case max and min exist;
- **unbounded** if some exposure-relevant variable has an unbounded domain (for example, an execution of unknown quantity, or a gap whose content is unconstrained);
- **empty** if no world is consistent: a contradiction between evidence and assumptions.

Only "determinate" can justify an action (S4).

### 2.5 Exposure in a world

For world w at decision time:
- **Up(w)** = P_w + (remaining quantity of every working buy) + (remaining quantity of every working order of unknown side);
- **Down(w)** = P_w − (remaining quantity of every working sell) − (remaining quantity of every working order of unknown side).

"Working" includes every live commitment (committed, not yet consumed) and every order that may be live at the broker in w.

This is the requirement Rev 3.1 states as I4 and requirement F. It defines *what* is bounded; it is not the candidate's method for bounding it.

---

## 3. Environmental assumptions (Track B; each one switchable in the oracle)

| ID | Assumption | If false, effect on W | Track B question |
|---|---|---|---|
| E-1 | exec_id is stable and unique per account, across paths, epochs and orders | worlds may merge two true executions or split one; S7 cannot be checked | Are execution identifiers stable and unique? |
| E-2 | each execution's broker version numbers strictly increase along its history, with one numbering on every path | version order is unknown; every placement of corrections is possible | Are broker versions monotonic? |
| E-3 | within an epoch, sequence numbers are contiguous, and their order is the emission order | holes cannot be detected; reordering is unconstrained | What do sequence numbers actually order? |
| E-3O | for one execution, stream order equals version order | non-prefix inclusion of corrections in a prefix snapshot becomes possible | (part of the above) |
| E-4P / E-4I | snapshot semantics: prefix or instant (§2.2) | the two give different consistent-world sets (see T-ORD-07) | Are snapshots prefix-based or instantaneous? |
| E-5 | every correction and bust names the prior version and carries its quantity | correction targets are ambiguous | How are corrections and busts delivered? |
| E-6 | every true transition affecting the account is eventually emitted on the stream within the delivery horizon | W includes worlds with unobserved executions: **unbounded**, so nothing is justified | Can events be omitted from both stream and snapshot? |
| E-7 | the adapter transmits only consumed payloads, at most once, and reports its outcome | orders may exist at the broker with no commitment: S5 fails silently until detected | What guarantees exist at the adapter boundary? |
| E-8 | account exclusivity: only Sentinel places orders | unknown orders are always possible: **unbounded** | (operational) |
| E-9 | finality horizon: no correction occurs after T_f from a version's occurrence | without it, no version is ever final | Is there a correction window? |
| E-10 | authentication: an item that passes authentication is genuine, and genuine items pass (FD-20 territory) | spurious or dropped items: W changes arbitrarily | (FD-20; founder decision, unresolved) |
| E-11 | the broker never changes an execution's identity fields (side, order, instrument) through a correction | corrections can move exposure between sides or orders | (D26) |

**Default profile A0** = all of E-1 to E-11 true, with E-4P. Every expected result in D3 states which assumptions it depends on, and the oracle (D2) reports the dependence mechanically.

---

## 4. Behaviors

**Format.** Each behavior gives:
- **Pre:** preconditions;
- **In:** inputs;
- **Δ:** state transition;
- **Out:** output;
- **Perm:** permission consequence;
- **Fail:** failure behavior;
- **Ev:** evidence required to establish the result.

"Log" means Sentinel's append-only record of every observation and internal operation.

### 4.1 Observable inputs and provenance

**B-01 Receive.**
- **Pre:** none.
- **In:** any observation.
- **Δ:** appended to the log, byte-exact, with receipt time, position and source path. Never modified or deleted.
- **Out:** a log position.
- **Perm:** none by itself.
- **Fail:** if the append fails, the observation is not received; no later behavior may act on it.
- **Ev:** the log entry.

**B-02 Attribute.**
- **Pre:** a received item.
- **In:** its authentication data.
- **Δ:** the item is marked *attributed* (a genuine broker report under E-10) or *unattributed*.
- **Out:** the attribution result.
- **Perm:** unattributed items never remove worlds. Whether they may *add* worlds, block or suspend is **FD-20 (unresolved)**. Recommended interim posture: they block (fail closed). This posture is recommended, **not** an authorized decision.
- **Fail:** if attribution cannot be determined, treat the item as unattributed.
- **Ev:** the authentication record.

### 4.2 Evidence identity

**B-03 Exact duplicate.**
- **Pre:** a received item reports the same true transition as an earlier attributed item, with identical identity fields and quantity.
- **In:** the item.
- **Δ:** none to W.
- **Out:** a duplicate record.
- **Perm:** none.
- **Fail:** —
- **Ev:** an identity-field comparison under the declared encoding. The encoding must be injective: no case folding, trimming or numeric reinterpretation (S7).

**B-04 Conflicting payload for one identity.**
- **Pre:** two attributed items claim the same transition identity with different content.
- **In:** both.
- **Δ:** under A0, no world is consistent with both, so W restricted to that execution is **empty**.
- **Out:** a contradiction record naming both items.
- **Perm:** S4: nothing is justified while the contradiction stands. Whether the contradiction may be scoped to fewer actions than "all" is open (D7-02).
- **Fail:** —
- **Ev:** both items, kept.

**B-05 Correction.**
- **Pre:** an attributed item names an execution x, its prior version and a new quantity.
- **In:** the item.
- **Δ:** worlds in which x's history includes this transition after the named prior version. If the prior version has not been observed, worlds include every history in which the missing versions exist with unknown content.
- **Out:** a version record.
- **Perm:** exposure changes as Up and Down change across W. An unobserved intermediate version of unknown quantity makes W **unbounded** (S4).
- **Fail:** if the named prior version contradicts an observed history, W is empty (B-04).
- **Ev:** the version chain.

**B-06 Bust.** As B-05 with new quantity 0.

**B-07 Missing exec_id.**
- **Pre:** an execution report without an exec_id.
- **In:** the item.
- **Δ:** worlds include both "this is a new execution" and "this reports an already-known execution". Each reading gives a different P.
- **Out:** an unidentified-execution record.
- **Perm:** permitted only if the action is safe under both readings (both are kept, never chosen).
- **Fail:** if the item has no sequence number either, its placement is also free (B-15).
- **Ev:** the item.

**B-08 Version conflict.** Two versions of one execution claim the same version number with different content, or are inconsistent with the predecessor links. W for x is empty (B-04).

**B-09 Cross-path binding.**
- **Pre:** a stream item and a list item may describe the same transition.
- **In:** both.
- **Δ:** they are bound as one transition **only** if every identity field is present on both and equal under the declared injective encoding. Otherwise worlds include both "same" and "different".
- **Out:** a binding record, or a both-readings record.
- **Perm:** safe under both readings, or deny.
- **Fail:** different values in a field that both supply → contradiction (B-04).
- **Ev:** both items and the encoding version.

### 4.3 Ordering and reconstruction

**B-10 In-order stream event.** Under E-3, an event with the next sequence number is placed at that position, which removes the worlds in which it lies elsewhere.

**B-11 Gap.**
- **Pre:** a sequence number above the next expected one arrives.
- **In:** the item.
- **Δ:** the missing numbers are holes. Worlds include any content for each hole (an execution of any quantity, or a non-economic message).
- **Out:** a hole record.
- **Perm:** W is **unbounded** unless every hole's content is constrained by other evidence (for example a sequence-resolution statement). So deny.
- **Fail:** —
- **Ev:** the sequence numbers received.

**B-12 Late arrival (hole fill).** The missing item arrives, and the hole's content becomes that item. W shrinks. This is S3(a), a legitimate expansion.

**B-13 Sequence reset or renumbering.**
- **Pre:** the numbering restarts within an epoch with no declared new epoch.
- **In:** the item.
- **Δ:** under E-3, W is empty: a contradiction.
- **Out:** contradiction.
- **Perm:** S4.
- **Fail:** an unlabelled renumbering that happens to continue at the expected next number is **undetectable**. The world set then wrongly excludes the true world. This is a Track B dependency on E-3, not a model defect, and it is kept as such (T-ORD-04).
- **Ev:** —

**B-14 Epoch transition.**
- **Pre:** a message from a new epoch.
- **In:** the item.
- **Δ:** worlds now include every possible unobserved tail of the old epoch, unless a snapshot taken in the new epoch constrains the total.
- **Out:** an epoch record.
- **Perm:** deny until the total is constrained.
- **Fail:** —
- **Ev:** the epoch declaration.

**B-15 Unsequenced evidence.** An item with no sequence number may be placed at any point consistent with its identity links. Worlds include every placement.

**B-16 Snapshot.**
- **Pre:** an attributed snapshot.
- **In:** the reported position s, its watermark W (if any) and its epoch.
- **Δ:** under E-4P, the worlds kept are those whose stream-prefix total at W equals s. Under E-4I, the worlds kept are those with P*(τ_s) = s for some τ_s consistent with E-3. Each reading defines its own world set; neither is chosen ("computed" is not claimed: nothing is executed).
- **Out:** a snapshot record.
- **Perm:** a snapshot may remove worlds. It never *adds* exposure capacity beyond what its readings justify.
- **Fail:** two snapshots at one watermark with different s → empty → S4.
- **Ev:** the snapshot and the readings applied.

**B-17 Alternative admissible placements.** Whenever several placements, bindings or readings remain, every one is a separate world. The result is the intersection of the safe action sets across them.

### 4.4 Exposure accounting

**B-18 Exposure determination.**
- **Pre:** W is determinate.
- **In:** —
- **Δ:** —
- **Out:** U* = max over W of Up(w), and D* = min over W of Down(w).
- **Perm:** these are the only quantities that S1 and S2 consult.
- **Fail:** W unbounded or empty → no U* or D*; deny.
- **Ev:** the world set.

**B-19 Unknown quantity.** Any execution or working order of unknown quantity → W unbounded on that side (or on both sides if the side is unknown) → deny on the affected side. The unaffected side is judged on its own worlds; whether candidates may exploit that is part of D7-02.

**B-20 Side asymmetry.**
- A buy increases Up and does not change Down.
- A sell lowers Down and does not change Up.
- An unknown-side order counts against both.

### 4.5 Reservations and commitments (internal, certain state)

**B-21 Commit.**
- **Pre:** a proposal p of quantity q and side σ; no live commitment for p's identity.
- **In:** p.
- **Δ:** if S1 (buy) or S2 (sell) holds **with p counted as working**, a commitment c_p is created and counted from that instant in every world (S5). Otherwise nothing happens.
- **Out:** the commitment, or a refusal.
- **Perm:** the commitment is authority to submit p exactly; nothing else is.
- **Fail:** two commits evaluated against the same state cannot both be created unless both hold with **both** counted (serialization).
- **Ev:** the commit record, which includes the log position it was evaluated at.

**B-22 Suspension.**
- **Pre:** a live, unconsumed commitment, and new evidence or time under which S1 or S2 no longer holds with it counted, or under which its basis is in doubt (B-29).
- **In:** —
- **Δ:** the commitment cannot be consumed. **It remains counted** (S5), because it could still be reactivated.
- **Out:** a suspension record with its causes.
- **Perm:** removes the authority to submit.
- **Fail:** —
- **Ev:** the cause.

**B-23 Reactivation.**
- **Pre:** a suspended commitment, unexpired; every suspension cause cleared; S1 or S2 holds now with it counted; its decision basis is not impugned.
- **In:** a request.
- **Δ:** the commitment can be consumed again.
- **Out:** a record with a **new** basis.
- **Perm:** a new authorization, judged at this moment and not inherited.
- **Fail:** any precondition fails → it stays suspended.
- **Ev:** the record.

**B-24 Consume.**
- **Pre:** a live, unsuspended, unexpired commitment; a payload identical to the committed proposal; S1 or S2 holds now.
- **In:** the payload.
- **Δ:** the commitment becomes a working order in one step. Its count is unchanged and continuous. From here, worlds include "transmitted or not" until the broker confirms either way.
- **Out:** a submission permission for that payload.
- **Perm:** exactly one submission of exactly that payload.
- **Fail:** a second consume with the same payload → the same result (idempotent). A different payload → refused.
- **Ev:** the consume record.

**B-25 Expiry.**
- **Pre:** an unconsumed commitment past its fixed expiry.
- **In:** a time tick.
- **Δ:** it ends, and its count is removed.
- **Out:** a record.
- **Perm:** S3(b), a legitimate expansion: it can never produce exposure.
- **Fail:** if consume and expiry race, exactly one takes effect.
- **Ev:** the tick record.

**B-26 Release.** As B-25, by explicit request, unconsumed only. *(The release operation itself is subject to a pending founder decision, FD-13.)*

**B-27 Invalidation.** As B-25, triggered by a proven-impugned basis (B-29). Unconsumed only.

**B-28 Delayed adapter transmission.**
- **Pre:** a consumed order whose transmission is delayed, lost or repeated.
- **In:** —
- **Δ:** worlds include every adapter outcome that E-7 allows. If E-7 is false, worlds include broker orders that have no commitment.
- **Out:** —
- **Perm:** under E-7 false, U* is **unbounded**, and S1 cannot be met for any increase.
- **Fail:** **The model can detect such orders only after the fact.** What prevents a transmission with no commitment is outside the model (D4 K-07).
- **Ev:** adapter reports.

### 4.6 Authorization conditions

**B-29 Basis and later contradiction.**
- **Pre:** an authorization was made at log prefix e_b.
- **In:** later evidence that describes the world *at or before* e_b.
- **Δ:** recompute W(e_b plus that evidence, A).
- **Out:** INTACT if the action is still safe in every world; IMPUGNED if it is unsafe in every world; **INDETERMINATE** if it is safe in some worlds and unsafe in others.
- **Perm:** IMPUGNED or INDETERMINATE → an unconsumed commitment is invalidated or suspended; a consumed one is flagged for review. The model cannot recall it.
- **Fail:** if the evidence's placement before or after e_b cannot be decided, every placement is a world. *This is the semantics the candidate's OQ-H15 has not yet adopted (D7-01).*
- **Ev:** e_b and the later items.

**B-30 Finality.**
- **Pre:** a version of x.
- **In:** time.
- **Δ:** **only** under E-9 does the passage of T_f remove worlds with later corrections to x. Without E-9, no version is ever final.
- **Out:** a finality record that names E-9 as its basis.
- **Perm:** under E-9 this is an assumption-driven expansion of the justified set. Whether S3(c) permits it (an expansion through a *declared* assumption that is logged) or forbids it (time alone) is **D7-03, kept open**.
- **Fail:** a correction after T_f falsifies E-9 for that execution. W under A is then empty → S4, and the authorizations that relied on finality are reported.
- **Ev:** the tick, and the declaration of E-9.

**B-31 Configuration or model migration.**
- **Pre:** a new limit, rule set or model version.
- **In:** a governance record.
- **Δ:** from one logged instant, every live commitment is rechecked under the new rules. Authorizations decided under the old rules keep their record, with the rule version stated.
- **Out:** a migration record.
- **Perm:** a change that grows the justified set requires a founder-authorized record (S3(c)). A change that shrinks it may suspend commitments.
- **Fail:** —
- **Ev:** the governance record.

**B-32 Stale authorization.** A decision evaluated at prefix e may not authorize at prefix e′ ⊋ e unless it is re-judged at e′. A commitment's authority lasts only while B-22 has not fired and B-25 has not ended it.

### 4.7 Failure and uncertainty

**B-33 Fail closed.**
- **Pre:** W is empty, unbounded or not computable, or an assumption in A is contradicted.
- **In:** —
- **Δ:** —
- **Out:** every authorization request is denied, with the reason.
- **Perm:** none is justified.
- **Fail:** **an availability cost is expected and must be measured, not hidden** (C-14 class).
- **Ev:** the reason record.

**B-34 Partial knowledge.** Nothing is "assumed zero". An unknown is a variable over its full domain.

### 4.8 Reconciliation and reconstruction

**B-35 Reconciliation.** A snapshot or list *corroborates* when it removes worlds without contradiction. It *reconciles* when W collapses to worlds with identical Up and Down. Corroboration from paths that share a failure mode is not independent corroboration.

**B-36 Reconstruction (S6).** Given the log prefix, A, the model version and the configuration, any party must obtain the same W, the same U* and D*, and the same decision. A decision whose inputs cannot be reproduced is unjustified in retrospect.

---

## 5. Permission summary

| Situation | Justified increase | Justified reduction |
|---|---|---|
| W determinate, U* + q ≤ L | yes | — |
| W determinate, q ≤ D* (all working reductions counted) | — | yes |
| W empty (contradiction) | no | no |
| W unbounded on the up side | no | judged on the down side only if the unboundedness is one-sided (D7-02) |
| a structural doubt that is not resolved | no | no |
| time passes under E-9 | open (D7-03) | open (D7-03) |
| A changes | only via a founder record | only via a founder record |

---

## 6. Mapping to the five center-of-gravity questions

1. **Authority.** Only a live commitment (B-21 to B-24) grants it. Evaluations, statuses, model outputs and policy statements do not.
2. **Evidence.** The log (B-01) and the world set W.
3. **Uncertainty.** It enters only as more worlds. A justified action must be safe in all of them.
4. **Enforcement.** Inside the model: serialization and the single consume path. **Outside the model (the adapter, E-7): nothing in EAR prevents an uncommitted transmission. EAR only detects it (K-07).**
5. **Reconstruction.** B-36.

---

## 7. Specification defects and unresolved ambiguities (not resolved here)

| ID | Defect or ambiguity | Why it is untestable or ambiguous | Candidate link |
|---|---|---|---|
| D7-01 | How later evidence of uncertain placement affects a past basis: worst case, all cases, or three-way | B-29 gives the world-set semantics (INTACT / IMPUGNED / INDETERMINATE); the candidate has not adopted any rule | OQ-H15 |
| D7-02 | Whether a contradiction or unboundedness on one execution or side may be scoped, or must deny everything | The world-set semantics permits scoping when the contradiction cannot affect the action. The candidate denies account-wide | C-14 |
| D7-03 | Whether finality by time (E-9) is a legitimate expansion | It is an assumption-driven expansion: S3(c) versus "time alone" | FD-15, C-1 |
| D7-04 | Snapshot semantics E-4P versus E-4I | The two give different W; both are kept | C-16 |
| D7-05 | Ordering of simultaneous events at a finality tick | B-30 is undefined at equal times | OQ-H18 |
| D7-06 | Determinism environment for S6 | Reconstruction needs a pinned environment that is not specified | OQ-H16 |
| D7-07 | Version resets and cross-namespace ordering | E-2 and E-3O are unverified, and no reset semantics are defined | OQ-H17 |
| D7-08 | Historical validity versus migration exposure | B-31 separates "decided under old rules" from "exposed under new rules"; the candidate's flag conflates them | OQ-H19 |
| D7-09 | Unattributed evidence | FD-20, unresolved; the interim recommendation is fail closed (§4.1) | FD-20 |
| D7-10 | Structural conditions with no resolution | In world terms, a contradiction persists until evidence or governance removes it. Which evidence may do so is undefined for several classes | OQ-R1 (Draft 4) |

*End of D1. Nothing in this document has been executed.*
