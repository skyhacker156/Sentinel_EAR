# EAR v0.1 Rev 3.2 Candidate: Challenges H-1 to H-7

SPECIFICATION ONLY / NOT IMPLEMENTED / NOT VERIFIED. Rev 3.1 (`dd9d87f76b01134e…a239`) stays frozen. No freeze, implementation, oracle, broker contact, paper or live trading.
Reviewer: Claude (Specification Lead). Date: 2026-11-24 (ET). Builds on R7 (`7b376d68…`).

**Labels.**
- **DERIVED**, **ASSUMED**, **CONDITIONAL**, **UNVERIFIED**, **UNBOUNDED**: as before.
- **COMPUTED**: integer arithmetic run by a throwaway script, on the single example shown. It is not an oracle.

**One principle runs through all seven answers. It is new, and stated once.**

> **Receipt asymmetry (P-RA).** Evidence that has been *received* but not *applied* (PENDING, CONFLICT, malformed, unauthenticated, or held) may **widen** a bound, **block** a permission, **defer** finality or **impugn** a basis. It may never **narrow** a bound, **grant** a permission, **start or restart** a finality clock, or **advance** an effective version. Only an APPLIED disposition (L3) can do those.

---

## H-1. Sequence keys contradict predecessor order

**Case (DERIVED).** x has v1, keyed (e, 510). Then v2 arrives keyed (e, 505), naming v1 as its predecessor. The predecessor order says v1 < v2; the keys say v2 < v1. No history satisfies both, so the admissible-cut set is empty (R6 §H1: i_lo ≥ i_hi).

**Rule (AM-10).**
- At the first moment both claims exist in L2, whatever order they arrived in:
  - record **CONFLICT (ORDER_CONTRADICTION)** in L3, against *both* entries;
  - x becomes **UNRESOLVED**, so the band is **UNBOUNDED**;
  - increases and reductions are both blocked.
- Neither claim is preferred. Either the broker's key or its predecessor reference is wrong, and the model cannot tell which.
- If v2 arrived first, it was PENDING (its predecessor was unseen). When v1 arrives, the contradiction is detected **before** v1 is applied. v1 is *not* applied.
- **H-4 applies:** every reservation whose basis included x is impugned.
- **Released by:** an authoritative broker resolution that names the correct order of v1 and v2. It is applied as new L2 evidence; nothing is rewritten.

**Acceptance test.** Both arrival orders give an identical L3 conflict and UNBOUNDED status. A mutant that "trusts keys" or "trusts predecessors" must disagree with the model on at least one generated case.

---

## H-2. A list carries the current version but no transition payload

**What agreement proves (DERIVED).**
- A list entry (exec_id, broker version k, payload p) **corroborates the version state** (k, p).
- It does **not** prove the identity of the transition that produced k. Several transitions could have led to (k, p).

**What goes wrong without a rule.** The list inserts version k, with no τ, into the chain. Later the stream delivers transition τ: (k−1 → k, p).
- The identity lookup misses, because τ is unknown.
- The predecessor check sees head = k and τ naming k−1, and calls it **STALE → CONFLICT**.
- That is a false conflict, an availability defect.

**Rule (AM-11), refining R7's E-1 protocol.** Add a **secondary identity**, the *version identity* ν = (exec_id, broker version, canonical payload). Check order on receipt:
1. Look up τ.
2. If τ is not found, look up the **resulting ν** of the incoming transition:
   - **same ν** → **duplicate-by-state**. An L3 record *binds* τ to the existing version. No quantity change.
   - **same (exec_id, broker version), different payload** → **CONFLICT**.
3. Only if neither is found, run the predecessor check.

**Limits, stated.**
- Without a broker version number, ν reduces to (exec_id, payload). That cannot tell repeated values apart (R7 CX-38).
- So a list without versions **cannot bind**. It supplies level-2 identity only, and corrections to versions it inserted are held (R7 E-4 reduced capability).
- Agreement of quantity alone never confirms a transition.

**Acceptance test.** List first, then stream τ: no conflict, τ bound to the version, F_d unchanged. Same again but with a different payload: CONFLICT.

---

## H-3. A PENDING correction arrives before its predecessor

**Answer.** It stays **outside the effective ledger** (P-RA: the effective version does not advance). It **immediately widens** the bounds for that execution and **blocks increases**. Reductions continue within the widened A, unless the bound is UNBOUNDED. It also **defers finality**.

**Why widen (DERIVED).** A PENDING correction is authentic evidence that x will change, through versions not yet seen, whose quantities are unknown. Under A-14 (net_cum ∈ [0, Q_o]):
- effective(x) ∈ [0, q_x + (Q_o − N_o)];
- for a working order, the upward part is already inside R (W4).

So x is forced **PROVISIONAL**, and the CA-15 reserve terms for x apply **whether or not FD-14 was adopted**. There is positive evidence of change. If o's Q is unknown (an orphan or unknown order), x is **UNRESOLVED (T2-U)**.

**Example (COMPUTED).**
- Terminal buy order, Q = 50. X1 = 30, X2 = 10 (head v0). A CORRECT for X2 names broker version 2 as its predecessor, which has not been seen.
- *Ignore it:* A = 40. If the truth is X2 = 0, a sell of 40 leaves **−10**.
- *Widen it:* F_min = 40 − 10 = 30, F_max = 40 + (50 − 40) = 50. The true range of P is [30, 50]. **Conservative and tight.**

**Effects.**
- The pending entry is an increase-blocking item (2.7).
- R-15″ re-evaluates Π, and may suspend reservations.
- The finality clock for x is **frozen** (H-6).

**Rule (AM-12).**

> A PENDING transition on x with a known order bound puts x into a mandatory provisional range [0, q_x + (Q_o − N_o)] (upward term only if o is terminal). Without an order bound, x is UNRESOLVED.

**Acceptance test.** The example above gives A = 30. A mutant that ignores PENDING entries must permit the sell of 40.

---

## H-4. A conflicting transition after an authorization (the central item)

**The defect (DERIVED).**
- Rev 3.1 and R1 to R7 store a reservation's *committed_revision* and *item_hash* (2.9).
- R-15″ re-evaluates **unconsumed** reservations on new evidence.
- Nothing preserves or acts on the authorization's **dependency** on the evidence it relied on, once consumed.
- A CONFLICT on evidence that *was* the basis is then treated as an ordinary later change (I8). It is not that. It means the authorization may never have been justified.

**Example (COMPUTED).**
- F = 100, RECONCILED. X1 (buy 20, τ1) is applied, so F_d = 120.
- A sell of 120 is committed and consumed; its basis includes X1 v0.
- A conflicting delivery of τ1 with quantity 5 arrives. If the truth is 5, P = 105, and the sell leaves **−15**.

**Rule (AM-13): authorization basis.**
1. **Basis record.** Every CommittedReservation stores:
   - `basis_revision`;
   - `basis_digest`: the SHA-256 of the sorted set {(exec_id, effective broker version, τ or ν, status)} for every execution that contributed to the bound governing its side (F_min for a sell, F_max for a buy), plus the snapshot id and the opening anchor.

   This is written in L3 at commit. It is a pure function of the ledger at basis_revision, so a separate implementation can recompute it.
2. **Impugnment.** A basis is **IMPUGNED** when any later L2 or L3 record does any of the following:
   - (a) marks a basis entry CONFLICT, ORDER_CONTRADICTION or DISMISSED;
   - (b) inserts a history fill (R7 E-1) that changes F_d(β) for the snapshot boundary β the basis used;
   - (c) binds a different payload to a basis ν;
   - (d) records FINAL_VIOLATED for an entry the basis treated as FINAL.

   A *later-keyed* NEW, CORRECT or BUST is **not** impugnment. That is new history, handled by I8 and R-15″.
3. **Consequence by stage** (P-RA: impugnment is triggered at **receipt**, not application):

| Reservation stage at impugnment | Action |
|---|---|
| ACTIVE / SUSPENDED | → **INVALIDATED** (a new terminal state: R released in the same revision, L3 record). Reactivation is **not** possible: a new proposal and a new commit are required. Π re-evaluation is not enough, because the old decision rested on contested evidence |
| CONSUMED, order working | order flagged **BASIS_IMPUGNED**; R stays counted; **all** new authorization blocked for that side until the conflict resolves; recorded as a G-07 review item (cancel candidate; the model does not cancel) |
| Executed | flagged; residual-risk register entry; once the conflict resolves, a retrospective check records **AUTHORIZATION_UNSAFE_RETROSPECTIVE** if A_raw at basis_revision, recomputed with the resolved evidence, was < Q |
| Others committed after a dependent | each has its own basis_digest; impugnment is evaluated per reservation |

4. **Why invalidate rather than suspend.** Suspension assumes the decision was valid and conditions changed. Impugnment means the decision's *premises* are disputed. Reviving it would convert a contested basis into permission.

**What this does not do.** It cannot recall a consumed or executed order. It turns a silent accounting discrepancy into an explicit, blocking, auditable state (DERIVED).

**Acceptance tests.**
- The example gives the consumed order BASIS_IMPUGNED, new sells blocked, and after resolution to 5, AUTHORIZATION_UNSAFE_RETROSPECTIVE.
- A later-keyed correction of X1 (not a conflict) must **not** impugn.

---

## H-5. Activating CA-15 with outstanding commitments

**The defect (DERIVED).** A safe steady state under CA-15 does not mean the switch to CA-15 is safe. At activation, applied executions with no finality evidence become PROVISIONAL, the reserve appears, and commitments made under the old rules can be over-reserved at once.

**Example (COMPUTED).**
- Opening 40. X1 (buy 60, now PROVISIONAL), so F_d = 100.
- A working sell of 70 (consumed) plus an ACTIVE sell reservation of 20, so S = 90.
- Before activation: A_raw = 10. After: F_min = 40 and **A_raw = −50**.
- Worst case if X1 is busted and every sell executes: **−50**. With the 20 suspended: **−30**.
- The 30 is **pre-existing** exposure that activation *reveals*. Activation creates none.

**Rule (AM-14): activation is one migration step.**
1. Activation is an L1 configuration record, so a new config hash and a revision step. In that **same** step:
   - recompute every bound with the reserve;
   - apply R-15″ to every ACTIVE or SUSPENDED reservation (suspend those that fail);
   - evaluate every consumed and working commitment against the new bounds, flagging those whose side bound is now negative as **BASIS_UNDER_SUPERSEDED_RULES**, treated like BASIS_IMPUGNED for blocking and review.
2. **Direction rule.** A configuration change that can only *widen* (activating CA-15, lengthening T_f or L_n) may take effect by this migration step. A change that can *narrow* (deactivating CA-15, shortening T_f, removing a correction class) is a **governance act**: founder-authorized, recorded and effective only at a revision boundary. The same standing as FD-15(b).
3. **Recommended placement:** activate CA-15 at **bootstrap**, before the first authorization. Runtime activation is permitted only through step 1.

**Acceptance test.** The example: in the activation revision, the 20 is SUSPENDED, the 70 is flagged, and no new sell is authorized. A mutant that activates "lazily" (on the next evaluation) must show one revision in which a sell is authorized against the unreserved bound.

---

## H-6. The finality clock and invalid or pending data

**The defect, R7's own wording.** R7 CA-15′ said "PROVISIONAL from the *receipt* of each version; the clock restarts on every applied transition". That mixes receipt and application.

**Rule (AM-15).**
- **Clock start.** t_start(x) = the time of the **APPLIED** disposition (L3) of x's current effective version. Not receipt.
  - Application happens no earlier than receipt, and receipt no earlier than broker issuance. So the bound received + T_f + L_n + σ, taken from this point, is still conservative (DERIVED).
- **Finality blockers.** x cannot reach FINAL while any L2 entry for x is PENDING, CONFLICT, malformed or held, received but not resolved. Such entries **freeze** the clock: P-RA allows deferral. They never **restart** it: P-RA forbids starting a clock from unapplied data.
- **When a blocker clears:**
  - if it resolves to APPLIED (a new version), the clock starts at that application;
  - if it is DISMISSED, the clock **resumes from its original t_start**, but not earlier than the end of any stream-unhealthy interval (R6 §H6).
- **Duplicates** (τ or ν match) never touch the clock.
- **Receipt of authentic, unapplied evidence against an already FINAL x** (for example a PENDING correction) raises **FINALITY_ASSUMPTION_FAILED** at receipt, by P-RA. It must not wait for application. Malformed or unauthenticated data against a FINAL x raises a *suspected* violation, which blocks until reviewed. That is conservative, because authenticity is not established.

**Acceptance test.**
- A malformed correction for x at t = 30 (t_start = 0, window 60): FINAL is not reached at 60 while it is held.
- If it is dismissed at t = 70, FINAL is reached at 70, not at 130.
- An applied correction at t = 70 moves FINAL to 130.

---

## H-7. An M1 manifest omits a busted execution

**Two separate completeness claims (DERIVED).**
- **Identity completeness:** every exec_id with any transition keyed ≤ β0 is listed, busted ones included.
- **Quantity completeness:** Σ of the listed current signed quantities reconciles with P_open (directly or through P_s).

Omitting a busted execution leaves quantity completeness **intact**, because busted quantity is 0. **The arithmetic check cannot detect an identity omission.**

**Example (COMPUTED).**
- P_open = 100 = X0 (buy 100). X5 (buy 30, busted to 0) is omitted. The manifest sum is 100, so the check passes.
- A replay of X5's NEW (κ ≤ β0, quantity 30) arrives. **Naive add: 130 against a true 100.** That adds a busted execution as if it were live.
- A later reinstatement CORRECT of X5 (κ > β0) has no anchor.

**Rule (AM-16).**
- The manifest declares `identity_complete` and `quantity_complete` **separately**. Each has its own scope (account, instrument, β0) and its own failure behaviour.

| Claims | Treatment |
|---|---|
| both | full M1: an unknown old execution is a CONFLICT (G class 2); a correction to an unlisted execution is a CONFLICT |
| quantity only ("M1q") | anchors for listed entries; an unknown old execution such as X5's replay → **M0 hold** (both sides blocked; not added, not discarded); a correction to an unlisted execution → G class 3, so **UNRESOLVED** |
| identity only | anchors; the P_open reconciliation is unchecked, so position corroboration is absent and bootstrap falls back to M0 for Consistency (UNCORROBORATED, which D06 does not tolerate for reductions) |
| neither | M0 |

- Identity completeness has **no internal check**. It rests entirely on the broker's claim (UNVERIFIED). The only external check would be reconciling against an independent source (D24).

**Acceptance test.** M1q plus the X5 replay: a hold, F_d = 100. M1 (both claims) plus the X5 replay: a CONFLICT. A mutant treating M1q as full M1 must CONFLICT where the model holds, or hold where it conflicts. Either way it shows as a disagreement.

---

## Cross-interactions (DERIVED)

| Pair | Finding |
|---|---|
| H-4 × R-15″ | Two distinct mechanisms. Suspension: conditions changed, the basis is intact, reactivation is possible. Invalidation: the basis is disputed, reactivation is impossible. The basis digest is what tells them apart |
| H-4 × H-1 / H-2 / H-7 | ORDER_CONTRADICTION, a payload conflict on ν, and manifest conflicts are all impugnment triggers |
| H-3 × CA-15 / FD-14 | A pending correction forces the reserve for that execution even if FD-14 is declined. **The reserve is no longer purely optional:** evidence of a change activates it locally |
| H-5 × FD-15 | Narrowing configuration changes are governance acts, consistent with FD-15(b) |
| H-6 × H-3 | A pending entry freezes the clock and widens the bounds. Both follow from P-RA |
| P-RA × widen-only | P-RA is a stricter corollary of the widen-only principle, applied to unapplied evidence. It introduces no conflict |

## New counterexamples registered

- **CX-42:** a false STALE conflict when list-inserted versions meet stream transitions (H-2, fixed by ν).
- **CX-43:** a pending correction ignored, giving −10 (H-3).
- **CX-44:** a consumed reservation on a contested basis, giving −15 (H-4).
- **CX-45:** activation over-reservation, −50, of which 30 was pre-existing (H-5).
- **CX-46:** the clock restarting from a malformed correction (H-6).
- **CX-47:** a busted-execution replay under M1q, giving 130 against 100 (H-7).

## Candidate amendments

- **P-RA:** the receipt-asymmetry principle (§2.4, beside the widen-only principle).
- **AM-10:** ORDER_CONTRADICTION.
- **AM-11:** the version identity ν and bind-on-match.
- **AM-12:** a mandatory local reserve on PENDING entries.
- **AM-13:** the authorization basis (basis_digest, IMPUGNED, INVALIDATED, BASIS_IMPUGNED, AUTHORIZATION_UNSAFE_RETROSPECTIVE).
- **AM-14:** the activation migration step and the narrowing-as-governance rule.
- **AM-15:** finality clock start at application; freeze and resume.
- **AM-16:** separate identity and quantity completeness, and M1q.

Each carries the falsifiable acceptance test stated above. All are **hand-derived**; the examples are **COMPUTED** on single cases; **nothing is independently tested**.

## Founder decisions

- **New:** none needed for H-1 to H-7. Each is resolved by a technical rule.
- **AM-14 point 2** makes narrowing configuration changes governance acts. That is consistent with, and depends on, the existing **FD-15** choice. It adds no new decision.
- **Unchanged:** FD-14 to FD-19 and the earlier FD-2″, FD-7, FD-8, FD-10 to FD-13.

## Readiness

- **No new false-authorization path** inside the proposed contracts (DERIVED).
- **H-4 closes a real gap.** Contested evidence behind a consumed authorization is now an explicit, blocking, auditable state. It is still **not reversible**: no rule can recall an order that has been submitted.
- **The A-12″ boundary is unchanged.**
- **NO-GO for implementation**, unchanged.
- **Recommendation, repeated:** consolidate R4 to R8 into one Rev 3.2 candidate text before the next hostile review. Seven documents now supersede each other in parts.

*Agreement among reviewers is not independent verification. Only integer arithmetic was executed (COMPUTED).*
