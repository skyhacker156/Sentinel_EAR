# EIVI-1 Deliverable 3: Adversarial Test Plan (Phase 1, five critical domains)

**Date:** 2026-11-24 | **Author:** Claude, Specification Lead | **Initiative:** EIVI-1, Workstream C
**Classification:** synthetic test design only. **No test has been executed.** Every expected result below is **DERIVED by hand** from D1's world-set semantics. None is COMPUTED, and none is verified. The oracle (D2, once built by an independent party) must recompute each one. Any disagreement is reported, not resolved toward this document.

## 0. Conventions

- **Defaults** (unless a test says otherwise):
  - one account and one instrument, long-only, limit **L = 150**;
  - profile **A0** = E-1 to E-11 true, with snapshot semantics E-4P (D1 §3);
  - quantities are integers. "P" is the true position; "Up" and "Down" are as in D1 §2.5;
  - "snapshot 100 @ W=10" means an attributed snapshot reporting 100 at watermark 10, epoch 1;
  - "fill buy 20 X1 #11" means a stream execution, exec_id X1, sequence 11.
- **Field "Expected":** the oracle verdict under A0, plus any profile variants that change it.
- **Field "Candidate":** the hand-derived Draft 3 behavior, for D4. This is **not** the test's oracle.
- **Field "Status":** DERIVED (hand), unless stated.
- **Field "Challenge":** marks tests designed to make the architecture fail or to expose a cost. These are not demonstrations that it works.
- **Safety properties S1 to S7:** as in D1 §1.

---

## 1. Execution identity and corrections

**T-ID-01 Duplicate delivery, unsafe direction.**
- *Init:* snapshot 100 @ W=10; working sell o1 of 20 (committed and consumed).
- *Events:* fill sell 20 X1 #11; the same execution again on the list path (exec_id X1, identical fields, no sequence).
- *Expected:* P = 80 in every world. Buy 70 → **JUSTIFIED** (150). Buy 71 → NOT.
- *Safety:* S7, S1.
- *Assumptions:* E-1.
- *Challenge:* double-counting a **sell** fill understates P. Read P = 60, buy 90 would pass, giving a true exposure of 170. This is the unsafe direction of duplication.
- *Candidate:* τ match → duplicate → agrees.

**T-ID-02 Conflicting payload.**
- *Init:* as T-ID-01, before the fill.
- *Events:* X1 version 0 qty 20 (stream #11); X1 version 0 qty 25 (list).
- *Expected:* **CONTRADICTION**; every action NOT_JUSTIFIED.
- *Safety:* S4.
- *Assumptions:* E-1 and E-2.
- *Challenge:* the availability cost. With no resolution operation (OQ-R1), the account stays denied until governance acts.
- *Candidate:* CONFLICT → status row 7 → agrees.

**T-ID-03 Correction.**
- *Init:* snapshot 100 @ W=10.
- *Events:* fill buy 30 X1 #11 (order o1 qty 30, now filled); CORRECT X1 v0 → v1, qty 30 → 10, #12.
- *Expected:* P = 110. Buy 40 → JUSTIFIED. Buy 41 → NOT.
- *Variant:* with E-5 relaxed (correction target ambiguous), the result is UNBOUNDED.
- *Safety:* S1.
- *Assumptions:* E-2 and E-5.

**T-ID-04 Bust after a reduction is consumed.**
- *Init:* snapshot 100 @ W=10.
- *Events:* fill buy 50 X1 #11 (P = 150); commit sell 140 (Down 150 − 140 = 10 ≥ 0, JUSTIFIED); consume; BUST X1 #12.
- *Expected:* after the bust, P = 100 and Down = 100 − 140 = −40 in every world where the sell fills.
- *Safety:* S2.
- *Challenge:* **architecture limit.** The authorization was justified when made, and the model cannot recall the order. Prevention is possible only under the E-9 finality treatment (withhold sell authority against unfinal fills). Otherwise it is detection only. The test records whether the system reports the breach.
- *Candidate:* the CA-15 finality reserve would have withheld 50 if active (FD-14, unresolved). Otherwise detection.

**T-ID-05 Missing exec_id.**
- *Init:* snapshot 100 @ W=10; working buy o1 qty 40.
- *Events:* fill buy 20 X1 o1 #11; list item: fill buy 20 on o1, **no exec_id**.
- *Expected:* worlds {same: P = 120, o1 remaining 20} and {distinct: P = 140, o1 remaining 0}. Up = 140 in both. Buy 10 → JUSTIFIED (150). Buy 11 → NOT.
- *Safety:* S7, S1.
- *Challenge:* a candidate that binds on (order, quantity) is fine here, because Up is equal in both worlds. Variant: o1 qty 20 (not 40). Then "distinct" means an overfill. Is that a contradiction (W restricted to "same") or an unknown order? The world model must decide whether an overfill is possible; **flag as D1 ambiguity A-01.**

**T-ID-06 Version fork.**
- *Events:* X1 v0 qty 30; CORRECT X1 v0 → v1 qty 10 (#12); CORRECT X1 v0 → v1′ qty 20 (#13).
- *Expected:* **CONTRADICTION**.
- *Safety:* S4.
- *Assumptions:* E-2 and E-3O.

**T-ID-07 Case-distinct identifiers.**
- *Init:* snapshot 135 @ W=10.
- *Events:* fill buy 5 exec_id "a1B" (#11); fill buy 5 exec_id "A1b" (#12, distinct).
- *Expected:* P = 145. Buy 5 → JUSTIFIED. Buy 6 → NOT.
- *Safety:* S7.
- *Challenge:* any normalization that collapses the two gives P = 140 and admits buy 10 (true 155). Unsafe (CX-61).

---

## 2. Event ordering and reconstruction

**T-ORD-01 Gap.**
- *Init:* snapshot 100 @ W=10.
- *Events:* fill buy 5 X2 #12. Sequence 11 is missing.
- *Expected:* hole 11 could be an execution of any quantity → **UNBOUNDED** on both sides.
- *Then:* #11 arrives as a non-economic message → P = 105; buy 45 JUSTIFIED (S3(a), a legitimate expansion).
- *Safety:* S4, S3.

**T-ORD-02 Snapshot ahead of the stream.**
- *Init:* snapshot 100 @ W=10.
- *Events:* fill buy 5 X2 #12 (#11 missing); snapshot 105 @ W=12.
- *Expected:*
  - **E-4P:** 100 + h₁₁ + 5 = 105, so h₁₁ = 0 (non-economic). P = 105. Buy 45 → **JUSTIFIED**.
  - **E-4I:** the snapshot instant may lie after #12 (h = 0, P = 105) or between #11 and #12 (h = +5, P = 110). Buy 45 → NOT; buy 40 → JUSTIFIED.
- *Safety:* S1.
- *Assumptions:* **E-4 (the two readings differ).**
- *Candidate:* status AWAITING-BEHIND → deny everything. Under either reading this is **over-denial**.
- *Challenge:* the candidate cannot use the snapshot's information because it does not commit to a semantics. The cost is recorded.

**T-ORD-03 Sequence reset.**
- *Events:* within epoch 1, after #50, a message arrives as #1.
- *Expected:* CONTRADICTION.
- *Variant (undetectable):* the broker silently renumbers and continues at #51 with different events. A0 accepts the true world's reports as if contiguous, so the oracle's W excludes the true world. A0 says JUSTIFIED, but that holds **only under E-3**.
- *Challenge:* records that E-3 is load-bearing and that no model can detect this. Status: DERIVED; Track B.

**T-ORD-04 Epoch transition.**
- *Init:* snapshot 100 @ e1 W=10, with e1 received through #14.
- *Events:* e2 #1, fill buy 5.
- *Expected:* the e1 tail after #14 is unconstrained → **UNBOUNDED**.
- *Then:* snapshot 110 @ e2 W=1. Under E-4P the tail plus 5 = 10, so the tail sum = 5. P = 110. Buy 40 → JUSTIFIED.
- *Challenge:* is the tail *sum* enough when the tail's individual items are unknown? For *current* exposure, yes. For later corrections to tail items, the identities are unknown, so they are unbounded. **D1 ambiguity A-02.**

**T-ORD-05 Snapshot conflict.**
- *Events:* snapshot 100 @ W=10 and snapshot 102 @ W=10.
- *Expected:* CONTRADICTION.

**T-ORD-06 Unsequenced placement.**
- *Init:* snapshot 100 @ W=10, everything received through #10.
- *Events:* a list reports X9 buy 10, no sequence, timing unknown.
- *Expected:* worlds {inside the snapshot: P = 100} and {after W, delivery pending: P = 110}. Buy 40 → JUSTIFIED; buy 41 → NOT.
- *Assumptions:* E-6 only bounds the *eventual* delivery.

**T-ORD-07 Prefix versus instant snapshot, three versions (CX-62 / CX-64).**
- *Init:* empty before #5.
- *Events:* fill buy 100 X #5; CORRECT X v0 → v1, 100 → 40 (list only, no sequence); CORRECT X v1 → v2, 40 → 70, #8; snapshot 130 @ W=10.
- *Expected:*
  - **E-4P:** consistent, with v1 emitted after W. P now = 70. Buy 80 → JUSTIFIED.
  - **E-4I:** the instant state must be a chain state {0, 100, 40, 70}, so 130 is impossible → **CONTRADICTION**.
- *Safety:* S1, S4.
- *Assumptions:* E-4, E-3O.
- *Candidate:* Draft 3's H_Δ = [70, 130] is consistent with E-4P. Draft 2's chain hull would have reported MISMATCH.

**T-ORD-08 Late fill after an apparent quiet period.**
- *Init:* snapshot 100 @ W=10; working buy o1 20.
- *Events:* no messages for a long time.
- *Expected:* under E-6, o1 may have filled 0 to 20 with no delivery yet. Up = 120 regardless. Buy 30 → JUSTIFIED.
- *Variant:* E-6 relaxed → UNBOUNDED.
- *Candidate:* the snapshot freshness rule (S_lim) makes it UNKNOWN → deny.
- *Challenge:* freshness is an **environment hedge** against E-6 failure, not a consequence of the model under A0. See D4 K-06.

---

## 3. Exposure bounds

**T-EXP-01 Unknown quantity, one-sided.**
- *Init:* P = 100 determinate; a working buy order whose remaining quantity is unknown.
- *Expected:* Up is unbounded → buy NOT. Down = 100 → sell 100 **JUSTIFIED**.
- *Candidate:* T2-U → UNBOUNDED on both sides → deny the sell: **over-denial** (D7-02).

**T-EXP-02 Pending intermediate version, current version known.**
- *Events:* X v0 qty 50 (#11); CORRECT X v1 → v2 qty 30 (#13, names v1, not yet received). #12 is missing.
- *Expected:*
  - **If #12 is v1:** X is now 30 and the rest is unchanged. But #12 could instead be another execution entirely (E-3 does not say what is at #12).
  - **Two hypotheses:** (a) #12 = X v1 → P = base + 30, determinate; (b) #12 is something else and v1 was emitted elsewhere or not yet. Under E-6, v1 must be emitted somewhere: (b) means v1 is at a later number and #12 is an unknown item, which makes it unbounded.
  - **Verdict:** UNBOUNDED until #12 arrives.
- *Challenge:* it shows that a known *latest* version does not make the position determinate while holes exist. Candidate: agrees (PENDING plus GAP).

**T-EXP-03 Buy/sell asymmetry.**
- *Init:* P = 100; committed sell 60; working buy 40.
- *Expected:* Up = 140 and Down = 40. Buy 10 JUSTIFIED, buy 11 NOT. Sell 40 JUSTIFIED, sell 41 NOT.

**T-EXP-04 Unknown-side order.**
- *Init:* P = 100; an unknown order u with remaining 20 and side unknown.
- *Expected:* Up = 120 and Down = 80. Buy 30 JUSTIFIED; sell 80 JUSTIFIED; sell 81 NOT.

**T-EXP-05 Duplicate versus independent executions on one order.**
- *Init:* working buy o1 qty 20; P = 100.
- *Events:* fill buy 10 X1 (#11); fill buy 10 X2 (#12).
- *Expected:* E-1 says they are distinct → P = 120, o1 filled. Up = 120.
- *Challenge:* the same events with X2 = X1 and an identical payload is a duplicate (P = 110, o1 remaining 10, Up still 120). The exposures happen to be equal. Variant with o1 qty 10: X1 ≠ X2 is an overfill. **Ambiguity A-01** again.

**T-EXP-06 Bound becomes unbounded through an unknown order.**
- *Init:* P = 100.
- *Events:* an order report for an order Sentinel never committed, with quantity missing.
- *Expected:* under E-8 this cannot happen, so W is empty → CONTRADICTION. Under E-8 relaxed → UNBOUNDED.
- *Challenge:* the reported verdict differs (CONTRADICTION vs UNBOUNDED), but both deny.

---

## 4. Reservations and commitments

**T-RES-01 The proposal counts itself (CX-58).**
- *Init:* P = 100; working buy 40 (Up = 140).
- *Events:* propose buy 30.
- *Expected:* with the proposal counted, 170 > 150 → **NOT**. Buy 10 → JUSTIFIED.
- *Safety:* S1.

**T-RES-02 Concurrent commits.**
- *Init:* P = 100.
- *Events:* two buy proposals of 30, both evaluated on the same log prefix.
- *Expected:* each alone gives 130 ≤ 150. Together they give 160 > 150. **At most one commitment exists** after both are processed.
- *Safety:* S1, S5.

**T-RES-03 A suspended commitment stays counted.**
- *Init:* P = 100; commitment c1 buy 30.
- *Events:* an unknown order of unknown quantity appears (c1 suspended); it is then resolved (cancelled, zero quantity); then propose buy 25.
- *Expected:* Up counts c1 = 130. 130 + 25 = 155 → **NOT**.
- *Safety:* S5.
- *Challenge:* excluding the suspended c1 gives 125 and allows the buy. If c1 is then reactivated, 155 > L.

**T-RES-04 Two suspended commitments (the R4 naive case).**
- *Init:* P = 90; c1 buy 30 and c2 buy 30 (Up = 150).
- *Events:* a correction raises P to 100 (Up = 160 > L), so both are suspended.
- *Expected:* neither may reactivate (160 > 150). If c2 expires, Up = 130 and c1 may reactivate.
- *Safety:* S1, S5.

**T-RES-05 Atomic consume.**
- *Init:* P = 100; c1 buy 30.
- *Events:* consume c1, with an evaluation requested at every log position around it.
- *Expected:* c1 contributes 30 at every position. Never 0 and never 60.
- *Safety:* S5.

**T-RES-06 Expiry racing consume.**
- *Init:* c1 with expiry t.
- *Events:* a consume request and the expiry tick at the same t.
- *Expected:* exactly one takes effect. Either c1 is consumed (counted as working) or c1 ends (not counted). Never both, never neither.
- *Safety:* S5.
- *Status:* DERIVED. The ordering rule at equal t is **open (OQ-H18 class)**.

**T-RES-07 Release, then a broker fill on that order.**
- *Init:* c1 buy 30, released (never consumed).
- *Events:* the broker reports a fill on c1's order id.
- *Expected:* under E-7 this is impossible → CONTRADICTION. Under E-7 relaxed → an unknown order, UNBOUNDED until resolved.
- *Challenge:* **the enforcement gap.** Nothing in EAR prevented the transmission (D4 K-07).

**T-RES-08 Invalidation removes the count only when it is safe to.**
- *Init:* c1 sell 50 unconsumed, with its basis then proven impugned.
- *Expected:* c1 ends and its count is removed. This is legitimate (S3(b)) because under E-7 it can never execute.
- *Variant:* E-7 relaxed → it must stay counted (it may have been transmitted). Removing it is **unsafe**.

**T-RES-09 Adapter outcome unknown.**
- *Init:* c1 buy 30, consumed.
- *Events:* the adapter reports nothing.
- *Expected:* worlds {not transmitted, transmitted–pending, filled 0 to 30}. Up includes 30 in every world. A later attributed "not transmitted" report removes the worlds under E-7.
- *Safety:* S5.

**T-RES-10 Delayed transmission after the conditions changed.**
- *Init:* c1 buy 30 consumed at t0; transmission delayed one hour.
- *Events:* during the hour, a new buy is proposed.
- *Expected:* c1 is counted throughout, so the new buy is judged with c1 included. **Safe.** The staleness of c1's *intent* is a policy matter, not exposure (FD-10, D_max).
- *Challenge:* verifies that D_max is not needed for S1.

---

## 5. Authorization

**T-AUTH-01 A correction to an execution unseen since bootstrap.**
- *Init:* M0 bootstrap: position 100 from snapshot @ β0, with no execution list.
- *Events:* CORRECT Y v3 → v4, prior qty 20 → qty 5, keyed after β0 (Y unknown to Sentinel).
- *Expected:* under E-5 the correction carries its own delta (−15), so P = 85. Determinate. Sell 85 → JUSTIFIED.
- *Variant:* E-5 relaxed → UNBOUNDED.
- *Candidate:* held (no anchor) → deny: **over-denial** under A0.
- *Challenge:* tests how much the candidate's conservatism costs.

**T-AUTH-02 Authorization followed by contradictory evidence of uncertain placement.**
- *Init:* snapshot 100 @ W=10; fill buy 50 X #11 (P = 150).
- *Events:* commit sell 120 (Down 30 ≥ 0: JUSTIFIED at the time); then a **list-only bust of X, timing unknown** (before or after the commit).
- *Expected:*
  - **Basis:** in worlds where the bust preceded the commit, the true P at commit was 100 and the sell leaves −20, so it is unsafe; in worlds where it followed, the basis is intact. → **INDETERMINATE.**
  - **Current:** P = 100 in every world. With the unconsumed sell counted, Down = −20, so the commitment must be suspended regardless.
- *Safety:* S2, S6.
- *Candidate:* the OQ-H15 rule is open. Draft 3's current worst-case text yields IMPUGNED → INVALIDATED. **Disagreement preserved** (D4).

**T-AUTH-03 Basis definitely impugned.**
- As T-AUTH-02, but the bust arrives on the stream with #11′, a key ≤ H_c, impossible under E-3 and E-6. Variant: an unsequenced bust with an attributed broker timestamp before the commit, under an added assumption that broker timestamps are reliable (**E-12, not in A0**).
- *Expected:* under E-12 → IMPUGNED → invalidate (if unconsumed).
- *Challenge:* it shows that a definite impugnment needs an assumption EAR does not currently declare. **D1 ambiguity A-03.**

**T-AUTH-04 Finality failure.**
- *Init:* under E-9 with T_f, X becomes final at t₀ + T_f.
- *Events:* a correction of X occurring after T_f.
- *Expected:* E-9 is falsified for X → **CONTRADICTION** under the profile. Every authorization that relied on X's finality is listed.
- *Variant:* profile without E-9 → no finality was ever granted, so those authorizations were never justified.
- *Safety:* S4, S6.

**T-AUTH-05 Time expands authority (D7-03).**
- *Init:* P0 = 100; fill buy 50 X (P = 150), X correctable down to 0.
- *Events:* time passes beyond T_f.
- *Expected:*
  - **Before T_f:** Down's minimum = 100. Sell 100 JUSTIFIED; sell 150 NOT.
  - **After T_f under E-9:** sell 150 JUSTIFIED.
  - **Without E-9:** sell 150 is never justified.
- *Safety:* **S3 (contested).**
- *Challenge:* this is exactly the founder's "convenience-driven operational transition" question. Under E-9 the expansion is assumption-driven and logged. Whether that is "silent" is a governance call (FD-15, D7-03).

**T-AUTH-06 Configuration migration.**
- *Events:*
  - (a) L 150 → 200 with a founder record;
  - (b) the same with no founder record;
  - (c) L 150 → 120 while c1 is live with Up = 140.
- *Expected:*
  - (a) the justified set grows (S3(c));
  - (b) no change; the record is refused;
  - (c) c1 is suspended (140 > 120). Decisions made before the migration keep their validity under the old rules.
- *Safety:* S3, S6.
- *Status:* DERIVED. The historical-validity semantics is **open (OQ-H19)**.

**T-AUTH-07 Stale authorization.**
- *Events:* a decision is evaluated at prefix e (Up = 140, buy 10 OK). Before the commit, an unknown-side order of remaining 20 arrives. The commit is attempted at e′.
- *Expected:* at e′, Up = 160 + 10 → NOT. The decision at e does not authorize at e′.
- *Safety:* S3.

**T-AUTH-08 Structural contradiction on an unrelated execution (C-14).**
- *Init:* P = 100, determinate.
- *Events:* a fork on an old, fully busted execution Z (both successors have qty 0).
- *Expected:* under the strict consistency reading (D2 R-6), W is empty → CONTRADICTION → deny everything. Under a **tolerant** reading, both Z successors give 0, so exposure is unaffected and the actions are justified.
- *Challenge:* the candidate's global SR coincides with the strict reading. Whether scoping is safe depends on R-6, a **correlated interpretation** (D2 §6). Preserved, not resolved.

**T-AUTH-09 Unattributed evidence (FD-20).**
- *Events:* an unattributed bust of X.
- *Expected:*
  - **Interim recommended posture (fail closed):** blocks authorization.
  - **FD-20(b) reading:** no effect.
- *Status:* FD-20 is **unresolved**, and both are recorded.

**T-AUTH-10 Omission from both stream and snapshot (E-6 false).**
- *Init:* P = 100 determinate under A0.
- *Events:* the broker fills an order Sentinel believes is cancelled, and neither the stream nor the snapshot reports it.
- *Expected:* under A0 the oracle cannot see it, so buy 50 is JUSTIFIED. With E-6 relaxed → UNBOUNDED; nothing is justified.
- *Classification:* **CONDITIONAL-ON-ENVIRONMENT.** Not a Track A failure. It is the dominant Track B risk (D4 K-04).

---

## 6. Regression catalogue (for the D2 I-6 known-defect recall)

The oracle must flag each historical counterexample, CX-01 to CX-68 (candidate §13.5), as unsafe, inconsistent or over-denying, as appropriate. CX entries describe the candidate's own history, so they test the oracle's sensitivity. They do not test D1's semantics.

## 7. D1 ambiguities found while writing the tests (returned to D1)

| ID | Ambiguity |
|---|---|
| A-01 | Is an overfill (fills exceeding the order quantity) a possible world (broker error) or a contradiction? |
| A-02 | After an epoch tail is pinned by a sum, are later corrections to the unseen tail items unbounded? |
| A-03 | Definite impugnment of a past basis needs a reliable broker-timestamp assumption (E-12) that is not declared |

*End of D3. 41 tests specified; 0 executed.*
