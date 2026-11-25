# EAR v0.1 Rev 3.2 Candidate: Challenges H-8 to H-14

SPECIFICATION ONLY / NOT IMPLEMENTED / NOT VERIFIED. Rev 3.1 (`dd9d87f76b01134e…a239`) stays frozen. No freeze, implementation, oracle, broker contact, paper or live trading.
Reviewer: Claude (Specification Lead). Date: 2026-11-24 (ET). Builds on R8 (`f94685a6…`), cited below as "H-series 1".

**Labels.**
- **DERIVED**, **ASSUMED**, **CONDITIONAL**, **UNVERIFIED**, **UNBOUNDED**: as before.
- **COMPUTED**: integer arithmetic on one example, run by a throwaway script. It is not an oracle.

---

## H-8 + H-9. Authorization basis: completeness, and pending corrections

### H-9 first: AM-13's digest is incomplete. Withdrawn as normative.

**Defect (DERIVED).** AM-13's basis_digest listed only the executions behind the governing bound, plus the snapshot and the anchor. But Π depends on much more:
- all band items (orphans, pending items, T1/T2 classifications);
- B and S (every reservation and working order's R, and the order states and cum checks behind them);
- the sequence state (H, M, holes, epoch), which decides BOUNDED;
- the unsequenced inclusion choices behind d;
- the evidence-property results;
- finality statuses;
- configuration (L, S_lim, T_f, L_n, σ, C_f), the model version and the master version.

A digest that omits any of these can mark a basis "intact" when an omitted dependency was wrong.

**CX-48 (COMPUTED).**
- F_d = 100, RECONCILED, no orders. A sell of 100 is committed and consumed: A = 100.
- Later, an **unsequenced** orphan sell of 30 (κ = ⊥) arrives. It might have occurred before the commit.
- It is not a basis *execution*, so AM-13's triggers (a) to (d) miss it.
- Recomputed as of the commit: F_min = 70, so Π(sell 100) fails. Worst-case true position afterwards: **−30**.

**Replacement (AM-13′): the basis is the evidence prefix, and impugnment is semantic.**
1. **Complete basis record.** basis = (L1 log position p_b at the commit's linearization point, model version, configuration hash).
   - By the layer-determinism invariant (R6 §H2), L2, L3, L4 and Π at commit are pure functions of exactly this. So the record is **complete by construction**: nothing Π used can lie outside it (DERIVED).
   - The commit also records H_c: the per-epoch contiguous high-water H_e at commit.
2. **Retro-relevant evidence.** An L1 item received after p_b is *retro-relevant* to the basis iff it could describe the state at or before the commit. That is, any of:
   - (i) it is keyed κ ≤ H_c in its epoch;
   - (ii) it is unsequenced (⊥);
   - (iii) it is a disposition, conflict, contradiction or binding on an L2 entry that was effective at p_b;
   - (iv) it is a PENDING transition whose *missing segment* (the versions between the head at p_b and its named predecessor) could contain a transition placed ≤ H_c (H-8 below);
   - (v) it is a FINAL_VIOLATED or FINALITY_ASSUMPTION_FAILED record touching an execution the basis treated as FINAL.

   Items keyed > H_c in their epoch are **new history**: they are handled by I8 and R-15″, and are not impugnment.

   **ASSUMED (A-12″):** events before the commit were delivered by the commit, so a key > H_c means the event occurred after the commit. Without A-12″, nothing keyed can be placed reliably; the A-12″ boundary is unchanged.
3. **Semantic impugnment test.** Whenever retro-relevant evidence arrives, re-derive the **as-of-commit state**: the L1 prefix p_b plus every retro-relevant item received since, under the same model version and configuration. Then re-evaluate Π for the reservation's proposal. The outcome is:
   - ALLOW → **basis intact**: an L3 note, no action;
   - UNRESOLVED → **BASIS_INCOMPLETE** (the evidence is insufficient to say);
   - DENY → **BASIS_IMPUGNED** (the evidence now shows the decision was not justified).
4. **The digest survives only as an index.** It is an optimization that picks which bases to recheck. It must be a *superset trigger*: any retro-relevant item triggers a recheck of every live basis it could touch. It is never the test itself.

### H-8: does a PENDING correction impugn a basis?

**Answer (DERIVED).** Only when its missing segment could fall at or before the commit's horizon. Then it is retro-relevant under (iv). Since a pending item usually leaves Π UNRESOLVED or narrower, the typical outcome is **BASIS_INCOMPLETE**, not IMPUGNED.
- *Missing segment entirely keyed > H_c:* new history. H-series 1's H-3 widening plus R-15″ apply, but not impugnment.
- *Missing segment unsequenced, or the pending item itself keyed ≤ H_c:* the versions might have existed at the commit, so it is retro-relevant. Under A-2″ contiguity, a sequenced transition ≤ H_c would already have been received. So this case arises from ⊥ transitions, or from a contract violation, which is SEQ_CONTRACT.

**Example (COMPUTED).**
- X, a buy on a terminal order with Q = 50, N = 50: head v0 at (e, 510), H_c = 520. A sell of 120 is committed from F_d = 150.
- A PENDING CORRECT arrives naming broker v2. v1 is missing, with unknown key.
- As of commit: X ∈ [0, 50], so F_min = 100, and Π(sell 120) gives DENY. Under the H-3 widening it is UNRESOLVED **only** if Q is unknown.
- **Result:** BASIS_IMPUGNED. With an unknown Q it would be BASIS_INCOMPLETE.

**Consequences by state.** This replaces the stage table in H-series 1's H-4.

| Reservation | BASIS_INCOMPLETE | BASIS_IMPUGNED |
|---|---|---|
| ACTIVE or SUSPENDED | **SUSPENDED** (nothing proven wrong yet). On resolution: an intact basis allows reactivation through full Π; an impugned basis leads to INVALIDATED | **INVALIDATED**: R released, a new proposal required |
| CONSUMED (order working) | flag BASIS_INCOMPLETE; new authorization on that side blocked until resolved; G-07 review item | flag BASIS_IMPUGNED; same blocking; G-07 cancel candidate |
| Executed | flag; on resolution, AUTHORIZATION_UNSAFE_RETROSPECTIVE if impugned | the same |

**Acceptance tests.**
- **CX-48** must impugn, or mark incomplete, under AM-13′. The old digest rule must miss it, which is the mutant check.
- A PENDING item with its missing segment keyed > H_c must **not** impugn.
- The basis record (p_b, model, config) re-derives byte-identical L4 and an identical Π outcome.

---

## H-10. Does ν uniquely identify a resulting state?

**The unstated assumption, now made explicit.** ν = (exec_id, broker version, canonical payload) identifies a state uniquely only if:

> **A-11⁗ (contract, ASSUMED; UNVERIFIED for any broker).**
> - The broker version is a per-exec_id counter, strictly increasing, with **one numbering scheme on every delivery path** (stream, list, manifest).
> - BUST and CORRECT each advance it.
> - No two different states of one exec_id share a version number.

**Failure modes if it is false (DERIVED).**
- *Different numbering on different paths* (for example, the list counts only corrections, or starts at 1):
  - equal (exec_id, k) on two paths may be different states. If the payloads also happen to be equal (repeated values), a **false bind** occurs, and later corrections are resolved against the wrong lineage;
  - if the payloads differ, a **false CONFLICT** occurs.
- *Partial payloads* (a list omits κ or order_id): ν is computed on a smaller field set, which is weaker identity.

**Rules (AM-11′).**
1. A ν bind requires the **full** canonical field set on both sides. With a partial set, the list may **corroborate the value** (an L3 note) but **never binds** τ.
2. **Cross-path consistency check.** The mapping from list versions to stream versions created by binds must be order-preserving and one-to-one per exec_id. Any violation is **CONFLICT (NUMBERING_INCONSISTENT)** for that exec_id. It is also a retro-relevant item (H-9) for every basis containing it.
3. If A-11⁗ is not declared for a path, ν binding is disabled for that path. It then supplies identity (level 2) only, as in R7 §E-3.

**Acceptance test.** A list using version offset +1 against the stream, with repeated payload values: the model must report NUMBERING_INCONSISTENT on the first non-order-preserving bind, never a silent bind.

---

## H-11. A finality gate, not a paused clock

H-series 1 (H-6) said "freeze" and "resume from t_start". That was ambiguous, and is replaced as follows.

**Definitions (AM-15′).**
- **The window condition is real time, not paused time.** The broker's correction window and the delivery latency elapse whether or not Sentinel holds a blocker. So the clock **never pauses**.
  - W(x, t): t ≥ t_start(x) + T_f + L_n + σ, where t_start is the APPLIED disposition time of the current effective version.
- **The health condition.** For every stream-unhealthy interval [a, b] that overlaps [t_start, t_start + T_f + σ]: t ≥ b + L_n. A correction issued while delivery was down must still arrive within L_n of recovery. That bound on backlog delivery is itself **ASSUMED**: part of L_n, UNVERIFIED.
- **The gate.** G(x, t) is true iff W holds, the health condition holds, and **no blocker** for x is outstanding. A blocker is any PENDING, CONFLICT, malformed or held entry for x, or an unresolved retro-relevant item affecting x.
- **FINAL** is recorded at the first tick at which G becomes true.
  - A blocker *dismissed* at time t_d leaves the window untouched. FINAL follows at the first tick ≥ max(window end, t_d).
  - A blocker *resolved by applying a new version* sets a new t_start, so a new window.

**Example (COMPUTED).** t_start = 0, window 60, a malformed blocker from 30 to 70, no unhealthy interval overlapping.
- **Gate semantics: FINAL at 70.**
- A paused clock would give 100. That delay has no basis: the broker's window did not pause.
- Restarting would give 130, which wrongly treats unapplied data as a new version (P-RA).

**Acceptance tests.**
- The three numbers above.
- An unhealthy interval [40, 55] with L_n = 10 moves FINAL to max(60, 65) = 65.

---

## H-12. The M1 full-identity acceptance test, corrected

**Defect, my own.** H-series 1's H-7 test said "M1 (both claims) plus the X5 replay → CONFLICT". But a manifest that *truthfully* claims identity completeness **lists** X5 (busted, version 1, qty 0). A replay of X5's NEW (broker version 0, κ ≤ β0) is then a replay of an *earlier* version, before β0. Under R7 E-4 that is an **UNOBSERVED history fill with no effect**, not a conflict. The test conflated a truthful claim with a false one.

**Corrected tests (AM-16′).**

| Manifest | X5 | Replay of X5 v0 (κ ≤ β0, qty 30) | Result |
|---|---|---|---|
| identity_complete, X5 listed (v1, busted, 0) | listed | earlier version before β0 | **history fill, no effect**; F_d = 100 |
| identity_complete, **X5 omitted** | omitted | unknown exec_id, κ ≤ β0 | **CONFLICT (MANIFEST_CLAIM_FALSIFIED)**. The identity-completeness claim is revoked (L3), M1 → **M1q** for the rest of the ledger, and every basis that relied on the claim gets a retro-relevant recheck (H-9) |
| quantity_complete only (M1q) | omitted | unknown exec_id | **M0 hold** (both sides blocked) |
| neither (M0) | — | — | M0 hold |

**Acceptance tests.** All four rows. A mutant that CONFLICTs in row 1 must disagree with the model.

---

## H-13. Can malformed evidence deny service indefinitely?

**Answer: yes, within the current contracts.** This cannot be eliminated inside the model (DERIVED).
- Fail-closed handling makes any message the model cannot reject as non-broker able to block. A permanent hold, with no time-based release, is a deliberate denial-of-service surface.
- Releasing holds on a timer would be narrowing by timeout, which is forbidden. It would also give an attacker a way to make holds expire on schedule.

**What can be bounded (AM-17).**
1. **Attribution comes first.** Only evidence that passes the Authenticity check (2.8) is attributed to the broker and may create L2 claims or holds about a specific execution. Everything else stays in L1 as unattributed.
2. **Unattributed evidence**, whether unauthenticated or failing authentication:
   - it creates no execution-level holds;
   - it raises **CHANNEL_SUSPECT** for the channel, which **blocks both sides** while active. It is cleared only by an authoritative channel check: a broker-confirmed sequence and position reconciliation over the suspect interval.

   *Why both sides:* if a genuine broker message failed authentication, ignoring it is an omission (A-12 class), and an omission can create false permission in either direction.
3. **Authenticated but malformed** evidence is a **broker fault**. It is held per item, scoped to the affected execution or order where possible: a T2-U on that order, not account-wide unless the instrument or account is unknown. A broker that emits faulty authenticated data denies service to itself. That is outside the threat model, an operational matter.
4. **Every hold has a defined exit.** Each hold class names its releasing evidence (R7 §G-3). If that evidence cannot be obtained, the only exit is the founder-authorized re-bootstrap (FD-18). Never a timer.
5. **The real mitigation is outside the model.** If authentication is sound and complete, so that every genuine broker message authenticates and no forged one does, unattributed evidence can be *ignored* safely, and the attack surface shrinks to key compromise (D23).

**Founder decision FD-20.** For v0.1, choose one:
- **(a)** keep CHANNEL_SUSPECT blocking both sides (fail-closed, open to denial of service); or
- **(b)** adopt **A-17 (authentication completeness and soundness, ASSUMED)** and ignore unattributed evidence. Availability improves; if A-17 is false, a genuine message is omitted.

This is a governance trade-off between availability and omission risk, not a technical definition.

**Acceptance tests.**
- An unauthenticated malformed message about X: no X-level hold, and CHANNEL_SUSPECT raised under (a).
- An authenticated malformed message: a hold on X's order only.
- No hold of any class is released without its named evidence.

---

## H-14. Migration atomicity across outstanding operations

**Rule (AM-14′, replacing H-series 1 H-5 point 1).**
1. **One linearization point.** A configuration change is an L1 record appended inside the store's serialized critical section. That is the migration linearization point L_a, a single revision step.
   - In that **same** step, under the new configuration hash: recompute every bound, apply R-15″ to every ACTIVE and SUSPENDED reservation, and run the H-9 semantic recheck of every consumed basis against the new rules. Failures are flagged BASIS_UNDER_SUPERSEDED_RULES, treated like BASIS_INCOMPLETE.
   - A narrowing change additionally needs a founder-authorization L1 record **before** L_a (H-series 1 H-5 point 2).
2. **No interleaving (DERIVED).** Every commit and consume evaluates Π inside the critical section at its own t_L, under the configuration hash in force at its linearization point (R-12″, I5: the configuration hash must equal the decision's).
   - Operations linearized **before** L_a used the old configuration, and are treated by step 1 as outstanding commitments.
   - Operations **after** L_a use the new one.
   - A decision evaluated before L_a but committed after it fails the configuration-hash check and must be re-evaluated.
   - Event applications are serialized on the same log, so before or after L_a, never inside it.
   - Hence no Π evaluation ever mixes the two configurations.
3. **Adapter boundary (UNVERIFIED).** An order consumed before L_a, but transmitted by the adapter after L_a, was authorized under the old rules. Step 1 flags it. The model cannot stop the transmission; whether the adapter re-checks before transmitting is G-07 (adapter acceptance test R-16).
4. **Timeline example.**
   - t1: decision D evaluated (old configuration).
   - t2: L_a, CA-15 activated.
   - t3: commit of D refused (configuration hash mismatch); re-evaluated under the new configuration.
   - Meanwhile reservation r, consumed at t0 < t2, is rechecked at L_a and flagged if it fails.

   There is no point at which a permission is granted under a mix of configurations.

**Acceptance tests.**
- An exhaustive interleaving of {evaluate, commit, consume, apply-event} × {activation} over two proposers: no committed decision may carry a configuration hash different from the one in force at its linearization point.
- Every pre-L_a commitment is rechecked within the L_a step.

---

## New counterexamples

- **CX-48:** an incomplete digest misses an unsequenced past orphan, giving −30 (H-9).
- **CX-49:** a false bind under different list numbering with repeated values (H-10).
- **CX-50:** pause semantics delaying FINAL by 30 with no basis (H-11; availability).
- **CX-51:** H-series 1's H-7 test contradicting its own definition (H-12; a spec-test defect).
- **CX-52:** fail-closed denial of service by injected unauthenticated messages (H-13).

## Amendments, status

All of AM-11′, AM-13′, AM-14′, AM-15′, AM-16′ and AM-17 are **hand-derived**. The examples are **COMPUTED** on single cases. **None is independently tested.**
- A-11⁗ and A-17 are **ASSUMED** and UNVERIFIED.
- A-12″ remains the boundary of every claim: AM-13′ uses it to tell past evidence from new history.

## Founder decisions

- **New:** **FD-20** (H-13: fail-closed channel suspicion, or the A-17 authentication assumption).
- **Unchanged:** FD-14 to FD-19 and the earlier FD-2″, FD-7, FD-8, FD-10 to FD-13.

## Readiness

| Dimension | Status |
|---|---|
| Evidence identity and ordering | conditional on A-11″, A-11‴ and A-11⁗ (all UNVERIFIED) |
| Exposure uncertainty | edge cases closed by rule (DERIVED) |
| Authorization dependency | **complete by construction** under AM-13′ (DERIVED); the semantic test is CONDITIONAL on A-12″ |
| Configuration migration | atomic by serialization (DERIVED); adapter side UNVERIFIED |
| Finality | gate semantics defined (DERIVED); every parameter UNVERIFIED; FD-15 open |
| Manifest completeness | tests reconciled (DERIVED) |
| Denial of service | **not eliminable inside the model**; bounded; FD-20 |
| Independent verification | none performed |
| Implementation | **NO-GO** |

I agree with the reviewer's sequencing: H-8 to H-14 are answered here, so consolidating R4 to R9 can now proceed, if the founder authorizes it. The consolidated text must carry each item's status label (DERIVED, COMPUTED, ASSUMED, CONDITIONAL, UNVERIFIED or UNBOUNDED) unchanged, and must not promote any hand-derived closure to verified.

*Agreement among reviewers is not independent verification. Only integer arithmetic was executed (COMPUTED).*
