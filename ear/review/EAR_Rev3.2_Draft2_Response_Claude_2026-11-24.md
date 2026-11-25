# EAR v0.1 Rev 3.2 Candidate: Response to the Draft-2 Hostile Review

- **Author:** Claude (Specification Lead / ARBITER)
- **Date:** 2026-11-24
- **Responds to:** A-TEAM DISPATCH, "EAR REV 3.2 CANDIDATE DRAFT 2: targeted hostile-review findings" (GPT; CC Gemini)
- **Reviewed object:** `ear/candidate/EAR_v0.1_Rev3.2_CANDIDATE.md`, draft 2 (SHA-256 `61ded4a1c3d024ea7b8ae1bf77ccc9f3a09176a3fad30663b4d4d632aededd15`)
- **Produces:** candidate draft 3 (SHA-256 in the push manifest)
- **Baseline:** Rev 3.1 FROZEN, SHA-256 `dd9d87f76b01134e084827b0202c73c52fccb2b86f21a176a6b6e551241fa239`. **Not modified**; the byte comparison against the pushed copy is identical.

**Boundary.** Specification correction only.
- No implementation, oracle construction or execution, broker contact, paper trading, live trading, or freeze.
- OQ-H15 to OQ-H19 remain **open**; nothing here answers them by implication.
- FD-20 remains **unresolved**, and no founder decision is made.
- Evidence labels are unchanged, except one demotion: the draft-2 hull's "DERIVED sound" is **withdrawn** (CX-62). Nothing is promoted.
- Agreement between GPT and Claude is not independent verification.

---

## 1. Disposition table

| Finding | Disposition | Draft-3 location | Label |
|---|---|---|---|
| **P0-1** Structural status gate | **ACCEPTED, CORRECTED.** Structural-resolution predicate SR (six clauses, account-global); new row 7 UNKNOWN (STRUCTURAL_UNRESOLVED) ahead of MISMATCH and RECONCILED; empty sets never satisfy a universal condition; no-watermark quiescent handled through β_c = head; BOUNDED tied to Rev 3.1 line 148; a twelve-line truth table. No new status value: Rev 3.1's seven are kept | §8 (§2.6.2) | DERIVED |
| **P0-2** Proposed exposure in Π | **ACCEPTED, CORRECTED.** Π(r, σ) is always on a state that counts r exactly once: ρ ⊕ r at commit, the actual state at consume and reactivation, fold(L1[0..p_b]) ⊕ r in the basis. The buy and sell predicates are written over σ; equivalence with Rev 3.1 `evaluate` is shown | §7.3, §7.1 step 4 | DERIVED |
| **P0-3** Reservation and working-order handoff | **ACCEPTED, CORRECTED.** One commitment identity order_id = reservation_id; B and S are Σ R over WORKING orders only; a state-mapping table; atomic consume; exclusive pre-submission exits; the T22 re-entry path | §7.2 | DERIVED |
| **P1-1** Basis schema and linearization | **ACCEPTED, CORRECTED.** One L3 schema; the basis is carried in the L1 commit record C; fold discipline (append and fold in one step); p_b = f(ρ) = p_C − 1; ordering 6a (append C) → 6b (fold) → 6c (revision ρ + 1) | §3.1, §7.1, §7.4 | DERIVED |
| **Add. 1** Partial-order hull | **ACCEPTED, and the defect is larger than stated.** The draft-2 hull was not merely informal; it is **unsound** without A-11-ORD under Rev 3.1's stream-prefix W1 (CX-62). It is replaced by the delta hull H_Δ, with a containment argument for (i) feasible sums, (ii) the true world without A-11-ORD and (iii) every admissible cut under A-11-ORD. I13 is amended | §3.5 | DERIVED; stream-prefix semantics UNVERIFIED (C-16) |
| **Add. 2** Identifier normalization | **ACCEPTED, CORRECTED.** Length-prefixed byte encoding; no lossy or non-injective transformation; declared injective per-path decoding only; the fail-safe direction (split) versus the fail-unsafe direction (collapse) is shown | §3.2 | DERIVED; collision resistance ASSUMED |
| **Add. 3** OQ-H15..H19 open | **PRESERVED.** The P1-1 boundary fixes *where* the as-of-commit prefix ends. It does not fix *how* retro-relevant items are placed (OQ-H15) or the determinism environment (OQ-H16). The identifier encoding fixes one component of OQ-H16 and does not close it | §12 unchanged | OPEN |
| **Add. 4** FD-20 | **PRESERVED.** SR clause 5 refers to CHANNEL_SUSPECT only "where FD-20(a) makes it structural" | §10, §12 | UNRESOLVED |
| **Add. 5** Labels | **PRESERVED**, with the single demotion noted above | — | — |
| **Add. 6** Rev 3.1 | **PRESERVED** | — | — |

**Rejected:** none.

**Deferred (recorded as conflicts, with counterexamples in §3):**
- a *scoped* SR to reduce the denial-of-service surface (C-14, CX-63);
- an instant-semantics hull (C-16, CX-64).

**Design choice to flag for review.** Draft 3 reports ¬SR as UNKNOWN with reason code STRUCTURAL_UNRESOLVED instead of adding an eighth status. This keeps Rev 3.1's "exactly one of seven" and its BOUNDED definition intact. The cost is that UNKNOWN now covers two different situations (no usable snapshot, and structural failure), distinguished only by reason code. A distinct status would be cleaner but would amend a frozen enumeration. That is a reviewer or founder call; draft 3 does not make it irreversibly.

---

## 2. Exact replacement text (verbatim from draft 3)

### 2.1 P0-1: §8 status

**§2.6.2 status [OPERATIVE] (P0-1, INT-01 and INT-05; REPLACES draft 2, draft 1 and the Rev 3.1 GAP rows at lines 418 and 499).** Rev 3.1's seven statuses are kept; no new status value is introduced.

Inputs:
- S = the latest accepted snapshot, with boundary (e_s, W) or no watermark;
- e* = the newest epoch with any received message;
- for every epoch e: H_e and M_e;
- the comparison cut β_c = (e_s, W) if S has a watermark; otherwise head (everything applied);
- the choice set X(β) = the product, over executions x, of the admissible-cut set at β (A-11-ORD mode) or of C(x, β) (H_Δ mode, §3.5).

**Structural-resolution predicate SR (P0-1) [OPERATIVE].** SR holds iff **none** of the following holds anywhere in the account's ledger:
1. any open L3 entry of kind SEQ_CONTRACT or CONFLICT, any subtype: FORK, STALE, KEY_MISMATCH, ORDER_CONTRADICTION, NUMBERING_INCONSISTENT, MANIFEST_CLAIM_FALSIFIED, overfill, proposal or snapshot conflicts;
2. any PENDING transition, or any D26 / D27 hold;
3. any version, applied execution or order of unknown quantity (T2-U, or an L2 entry with qty absent);
4. any pre-bootstrap item whose R7 §10 per-mode disposition is UNRESOLVED, CONFLICT or held (including held anchor corrections and undismissed unknown-old executions);
5. any structural evidence failure in Rev 3.1 §2.8's sense (including snapshot quantity not a signed integer, V54), or CHANNEL_SUSPECT where FD-20(a) makes it structural;
6. for β ∈ {β_c, head}: ExecutionState(x, β) is UNRESOLVED or **empty** for some x, or X(β) is empty. *An empty set is never read as {0}, and never satisfies a universal condition vacuously.*

SR is global to the account: one unresolved item anywhere makes SR false (C-14). **DERIVED.**

Status is the **first** row that applies.

| # | Condition | Status | BOUNDED (Rev 3.1 line 148) |
|---|---|---|---|
| 1 | no accepted snapshot; or S stale beyond S_lim; or conflicting snapshots at one watermark; or S declares no epoch | UNKNOWN | no |
| 2 | e* > e_s: **EPOCH_UNBOOTSTRAPPED** (INT-05) | UNKNOWN | no |
| 3 | ∃ e: H_e < M_e (a recorded hole, in any epoch) | GAP | no |
| 4 | S has a watermark, W > H_{e_s}, and the wait limit (D08) has passed | GAP (AB_TIMEOUT) | no |
| 5 | S has a watermark and W > H_{e_s} | AWAITING-BEHIND | no |
| 6 | S has no watermark and the ledger is not quiescent | AWAITING-UNVERIFIED | no |
| 7 | **¬SR: STRUCTURAL_UNRESOLVED** (P0-1) | UNKNOWN | no |
| 8 | some choice in X(β_c) gives d ≠ 0 | MISMATCH | yes, by d |
| 9 | otherwise: X(β_c) is non-empty (by row 7) and every choice gives d = 0 | RECONCILED if no applied event has κ > β_c (always so without a watermark); otherwise AWAITING | yes |

- "Quiescent" is as in Rev 3.1: no working, authorized or unknown orders and no pending events.
- **Reason codes:** every condition that holds (each row's condition, and each SR clause that fails) is listed as a reason code, whatever the status. So a GAP that also carries a CONFLICT reports GAP with CONFLICT among its codes.
- **BOUNDED.** Rows 1–7 are UNBOUNDED. Rows 8 and 9 are reachable only with SR, so they have no T2-U item and no structural failure. Hence BOUNDED ⇔ row 8 or 9, which agrees with Rev 3.1 line 148 (DERIVED). The draft-2 "Bounded" column, which marked RECONCILED as bounded unconditionally, is SUPERSEDED (CX-57).
- **No fall-through (DERIVED).** RECONCILED, AWAITING and MISMATCH occur only at rows 8 and 9, which lie after row 7. Every structural state listed in SR, including CONFLICT, FORK, ORDER_CONTRADICTION, NUMBERING_INCONSISTENT, unknown quantity, unresolved pre-bootstrap items and empty admissible sets, therefore stops at row 7 or earlier.
- Buffered events (received above H_e + 1) exist **iff** row 3's condition holds. They have no separate status.
- **INT-05, new-epoch events.** Events of epoch e* are **applied** to F_d on receipt, in key order, as deltas (§3.7). They are not buffered. Draft 1 and R3 case 8 said "buffered pending bootstrap"; that wording is SUPERSEDED. The status is UNKNOWN (row 2) until a snapshot of e* is accepted and compared. That comparison is the mechanism that reveals an old-epoch tail loss (C4-R). Applying the events keeps the accounting current; withholding boundedness keeps authorization safe.
- **Truth table (DERIVED, hand-enumerated; mutually exclusive by first match, exhaustive because row 9 is the default).** Variables: Snap ∈ {usable, absent / stale / conflicting / epoch-less}; NE = (e* > e_s); Hole = (∃ e: H_e < M_e); Wm = S has a watermark; Ahead = Wm ∧ W > H_{e_s}; Wait = the D08 limit has passed; Q = quiescent; SR; Dz = every choice in X(β_c) gives d = 0.

| Snap | NE | Hole | Wm | Ahead | Wait | Q | SR | Dz | Row → status |
|---|---|---|---|---|---|---|---|---|---|
| not usable | * | * | * | * | * | * | * | * | 1 UNKNOWN |
| usable | T | * | * | * | * | * | * | * | 2 UNKNOWN |
| usable | F | T | * | * | * | * | * | * | 3 GAP |
| usable | F | F | T | T | T | * | * | * | 4 GAP (AB_TIMEOUT) |
| usable | F | F | T | T | F | * | * | * | 5 AWAITING-BEHIND |
| usable | F | F | F | — | — | F | * | * | 6 AWAITING-UNVERIFIED |
| usable | F | F | T | F | * | * | F | * | 7 UNKNOWN (STRUCTURAL) |
| usable | F | F | F | — | — | T | F | * | 7 UNKNOWN (STRUCTURAL) |
| usable | F | F | T | F | * | * | T | F | 8 MISMATCH |
| usable | F | F | F | — | — | T | T | F | 8 MISMATCH |
| usable | F | F | T | F | * | * | T | T | 9 RECONCILED / AWAITING |
| usable | F | F | F | — | — | T | T | T | 9 RECONCILED |

  ("—" means not applicable: Ahead and Wait are defined only with a watermark.) Each consistent assignment of the variables (Ahead and Wait taken only when Wm holds) matches exactly one line, and every structural state reaches row 7 or earlier. Rows 4 and 5 are reachable and distinct. This is **DERIVED, not executed** (V104).

### 2.2 P0-2: §7.3 Π

**Evaluated state (P0-2, REPLACES the draft-2 first sentence).** Π(r, σ) is always evaluated on a state σ in which r's commitment is counted **exactly once**:
- **at commit:** σ = ρ ⊕ r, the state at revision ρ plus r's AUTHORIZED order with R = Q_r on r's side. Step 3 of §7.1 guarantees that r is not in ρ: no reservation exists for proposal_id, and reservation_id = order_id is fresh;
- **at consume, at reactivation (SUSPENDED → ACTIVE), and in any re-check of a live reservation:** σ = the actual current state, which already contains r;
- **in the basis re-derivation (§7.4):** σ = fold(L1[0..p_b]) ⊕ r, together with the retro-relevant items.

Over σ:
- **buy r:** U(σ) = F_max(σ) + B(σ) ≤ L. At commit, B(ρ ⊕ r) = B(ρ) + Q_r, so this is U(ρ) + Q_r ≤ L;
- **sell r:** A_raw(σ) = F_min(σ) − S(σ) ≥ 0. At commit, this is A_raw(ρ) − Q_r ≥ 0, i.e. Q_r ≤ A_raw(ρ);
- not OVER_LIMIT(σ) and not OVER_RESERVED(σ), for **both** sides. A buy leaves A_raw unchanged, and a sell leaves U unchanged, so the side that r does not move is checked at its pre-proposal value.

**Equivalence with Rev 3.1 (DERIVED):** at commit, these quantity tests are exactly Rev 3.1's `evaluate` rules on ρ: increase "U + Q ≤ L" (line 224) and reduction "Q ≤ A". If A_raw(ρ) < 0 the ledger is OVER_RESERVED and both deny. **A proposal therefore cannot pass on the pre-proposal exposure alone.** Reading "U(ρ) ≤ L" on ρ without r would admit any Q while U(ρ) ≤ L (CX-58).

Plus:
- BOUNDED(σ) in Rev 3.1's sense (line 148), which under §8 holds iff the status row is 8 or 9;
- SR(σ), the structural-resolution predicate of §8, which includes and extends the following; no structural failure (SEQ_CONTRACT, CONFLICT, FORK, ORDER_CONTRADICTION, NUMBERING_INCONSISTENT, D26/D27 holds, CHANNEL_SUSPECT under FD-20(a));
- Consistency CORROBORATED and Freshness FRESH at the evaluation time;
- not OVER_RESERVED and not OVER_LIMIT;
- the 2.7 side blocks.

Π's structural clause:

- BOUNDED(σ) in Rev 3.1's sense (line 148), which under §8 holds iff the status row is 8 or 9;
- SR(σ), the structural-resolution predicate of §8, which includes and extends the following; no structural failure (SEQ_CONTRACT, CONFLICT, FORK, ORDER_CONTRADICTION, NUMBERING_INCONSISTENT, D26/D27 holds, CHANNEL_SUSPECT under FD-20(a));

### 2.3 P0-3: §7.2 commitment identity and handoff

- **One commitment identity (P0-3, REPLACES the draft-2 invariant wording).** The commitment identity is **order_id = reservation_id** (Rev 3.1 §2.9, I6). B and S are defined **only** as Σ R(o) over orders o whose lifecycle state is in WORKING (Rev 3.1 line 140, with AUTHORIZED ∈ WORKING). A reservation is **never** a second summand. The reservation state is an attribute of the same order and determines R only through the order's lifecycle state.
- **Reservation state ↔ order state ↔ counted R:**

| Reservation state | Order lifecycle state | R counted in B or S |
|---|---|---|
| ACTIVE | AUTHORIZED | qty (= Q_r) |
| SUSPENDED | AUTHORIZED | qty (= Q_r) |
| CONSUMED | SUBMITTED, ACKNOWLEDGED, PARTIALLY_FILLED, CANCEL_PENDING, UNKNOWN | qty − net_cum |
| CONSUMED | FILLED, CANCELED, REJECTED (terminal) | 0 |
| EXPIRED | EXPIRED (T05, cause TTL) | 0 |
| RELEASED [CONDITIONAL-ON-FD-13] | EXPIRED (T05, cause RELEASE) | 0 |
| INVALIDATED (§7.4) | EXPIRED (T05, cause INVALIDATED) | 0 |

- **Atomic handoff (P0-3).** `consume(reservation_id, payload)` is one serialized fold (§3.1). It appends the L1 consume record, then in the same fold sets the reservation ACTIVE → CONSUMED and the order AUTHORIZED → SUBMITTED (Rev 3.1 T04), and advances the revision once. Because AUTHORIZED and SUBMITTED are both in WORKING and net_cum is unchanged, R(o) is the same immediately before and after. So there is **no revision at which the commitment is counted twice, and none at which it is counted zero times.** **DERIVED.**
- **Exclusive pre-submission exits.** TTL expiry, release and invalidation apply only to ACTIVE or SUSPENDED. Each is one fold with its own L1 record, moving the order AUTHORIZED → EXPIRED with a cause code (R → 0). They and `consume` serialize on the lock, and whichever runs first wins; consume then requires ACTIVE (or fails). A CONSUMED reservation never expires.
- **Late events.** A broker event for an order in a pre-submission terminal state follows Rev 3.1 T22 (order UNKNOWN, R re-reserved). This is the only way such an order is counted again. **DERIVED.**
- **Rev 3.1 mapping.** Rev 3.1 §2.9's reservation state RELEASED for "reject, cancel, fill complete" (after submission) is represented here as CONSUMED with a terminal order state. The counted R is identical. RELEASED here is the pre-consume release of FD-13 only (C-15).

- **Invariant (unchanged in substance):** every unexpired reservation's commitment is counted in B or S, whether ACTIVE or SUSPENDED, and lifecycle changes of the reservation alone never change B or S.
- **[SUPERSEDED]** R2 R-15 (one-sided; A_raw-only reactivation); R3 R-15′'s "every other ACTIVE" wording; draft 2's "every unexpired reservation contributes its order's R", which was readable as a second summand (CX-59). FD-9 is moot.

### 2.4 P1-1: schema, fold discipline, commit ordering, basis

§3.1 rows and rule:

| L1 Raw evidence log | every received item, byte-exact, plus Sentinel records: ticks (TTL, FINAL trigger, staleness) and **operation records (P1-1): commit, consume, release, expiry, invalidation, migration (L_a)**, each carrying its own inputs; raw_hash, received_at, log position, hash chain | never |
| L3 Disposition log | (disp_id, target, from → to, cause = L1 ref or rule, revision, t). *P1-1:* this is the only L3 schema. There is **no separate L3 "basis record"**: the authorization basis lives in the L1 commit record (§7.4), and the reservation's creation is an ordinary L3 disposition ∅ → ACTIVE whose cause is that record | never; status = the fold |

**Fold discipline (P1-1) [OPERATIVE].** Appending an item to L1 and folding it into L2, L3 and L4 happen in **one** serialized step of the store, under the same lock as commit (§7.1). Each revision ρ therefore has an L1 frontier f(ρ), the position of the last item folded, and every L1 item at or below f(ρ) is folded. No item is ever appended without also being folded. **DERIVED.** It adds a liveness coupling (C-17).

§7.1 commit (steps 1, 4 and 6 changed):

- **Commit (INT-04, REPLACES "no reservation exists").** Reservation scope: **proposal_id within the single configured account** (Rev 3.1 I5 and R31-06B). One serialized critical section of the store performs, with no interleaving:
  1. acquire the store lock. Every L1 item already appended has been folded (fold discipline, §3.1), so the current revision ρ has frontier f(ρ) = the last L1 position;
  2. read t_L;
  3. look up any reservation for proposal_id:
     - same proposal_hash → return the existing reservation (R_DUPLICATE), and stop;
     - different hash → refuse (R_PROPOSAL_CONFLICT), and stop;
  4. evaluate E_L at as_of t_L on revision ρ, **over the post-proposal state ρ ⊕ r** (§7.3);
  5. require ALLOW, the same revision, item hash and configuration hash as D, and the proposal_hash of D;
  6. (P1-1, REPLACES the draft-2 step 6) in one fold, in this order:
     - 6a. append the **L1 commit record C** at position p_C = f(ρ) + 1. Its payload is the reservation fields, the decision hash, t_L, and the basis (p_b = f(ρ), model version, configuration hash, H_c computed from the fold at p_b);
     - 6b. fold C: create the reservation (ACTIVE) and its AUTHORIZED order as **one commitment** (§7.2), and write the L3 disposition (reservation_id, ∅ → ACTIVE, cause = p_C, revision ρ + 1, t_L);
     - 6c. set revision = ρ + 1, with frontier f(ρ + 1) = p_C. The step folds C and nothing else;
  7. release the lock.
- **Boundary (P1-1).** p_b = f(ρ) = p_C − 1, which is the last L1 item before C, and every item at or below p_b was seen by E_L. No L1 item lies strictly between p_b and p_C. Every item after C (position > p_C) was not seen by the decision. The as-of-commit state is fold(L1[0..p_b]) ⊕ r, which equals fold(L1[0..p_C]) in L4 terms. **DERIVED.**
- **Boundary (P1-1).** p_b = f(ρ) = p_C − 1, which is the last L1 item before C, and every item at or below p_b was seen by E_L. No L1 item lies strictly between p_b and p_C. Every item after C (position > p_C) was not seen by the decision. The as-of-commit state is fold(L1[0..p_b]) ⊕ r, which equals fold(L1[0..p_C]) in L4 terms. **DERIVED.**

§7.4:

- **Basis (P1-1, REPLACES "basis record"):** carried **inside the L1 commit record C** (§7.1 step 6a): p_b = f(ρ) = p_C − 1 (the last L1 item the decision saw), the model version, the configuration hash, and H_c (the per-epoch high-water H_e in the fold at p_b). There is no separate L3 basis schema. "Received after p_b" means L1 position > p_C, because none lies in between. Complete **CONDITIONAL** on the determinism contract (OQ-H16).
- **Semantic test:** re-derive the as-of-commit state fold(L1[0..p_b]) ⊕ r, together with the retro-relevant items, and re-evaluate Π(r, ·) on that state (§7.3). The rule for placing those items is OQ-H15.

### 2.5 Additional 1: §3.5 hull

- **Without A-11-ORD** (broker does not guarantee stream order matches version order): the chain-prefix model of a cut is **not sound**, because the snapshot may include a non-prefix subset of x's transitions (CX-62). The candidate uses the **delta hull H_Δ** below for x. *Placing keyed versions by their keys alone is not permitted.*

- **I13 [OPERATIVE] (amended, Additional 1):** in admissible-cut mode, no non-admissible cut contributes to any bound. In H_Δ mode, the bound is H_Δ, and non-prefix subsets **do** contribute (C-13).
- **Delta hull H_Δ (Additional 1, REPLACES the draft-2 "partial-order fallback") [OPERATIVE-PROVISIONAL].**
  - *Semantics relied on:* Rev 3.1 W1, read as **stream-prefix semantics**: the snapshot position at β is the net effect of exactly the events with κ ≤ β. Whether the broker's snapshots have this semantics, or instead report the internal state at an instant, is **UNVERIFIED** (C-16).
  - *Inputs for x at β:* every transition t_i of x with its own signed delta δ_i = qty_i − prior_qty_i, taken from the transition itself, not from the chain (δ_0 = q_0 for the original fill; a bust has δ = −prior_qty). Partition: In = {i : κ_i ≤ β}; Out = {i : κ_i > β}; Free = {i : κ_i = ⊥}.
  - *Definition:* the feasible contributions are C(x, β) = {Σ_{i ∈ In ∪ S} δ_i : S ⊆ Free}, and H_Δ(x, β) = [ Σ_In δ + Σ_Free min(0, δ), Σ_In δ + Σ_Free max(0, δ) ]. An IN_OPENING anchor contributes 0 plus its post-anchor deltas.
  - *Containment (DERIVED):* (i) C(x, β) ⊆ H_Δ(x, β), because each Free term lies between min(0, δ) and max(0, δ). (ii) Under stream-prefix semantics and A-11‴ / A-11⁗ (every delivered transition correctly identified, with a correct delta), the true contribution of x at β is Σ over the transitions actually emitted at or before β. That set contains In, excludes Out, and meets Free in some subset, so it lies in C(x, β). **A-11-ORD is not needed.** (iii) If A-11-ORD does hold, every admissible chain cut k gives Σ_{i ≤ k} δ_i with In ⊆ [0, k] and Out ∩ [0, k] = ∅, which is one member of C(x, β). Hence **every admissible exposure state lies in H_Δ**.
  - *Aggregate:* F_d(β) ∈ P_open + Σ_x H_Δ(x, β), a sum of intervals. This contains every joint choice (DERIVED). It is not tight, because constraints between Free transitions are ignored, so it errs conservative.
  - *Not covered:* undelivered transitions (A-12″); unknown-quantity transitions (UNRESOLVED; ¬SR, §8); PENDING (UNRESOLVED).
  - *Mode selection:* H_Δ is used for x **iff** A-11-ORD is not declared for every path that reports x. Otherwise the admissible-cut set is used.
- **[SUPERSEDED → H_Δ]** draft 2 "hull [min, max] of {0} ∪ {q_i : v_i not forced after β}. **DERIVED** sound." Chain states are not sound without A-11-ORD (CX-62), and "forced after" was undefined. The soundness claim is **withdrawn**, not carried over.
- **[SUPERSEDED → this section]** R5 E-B's "independent before/after placement per ⊥ transition" (defect CX-36).

### 2.6 Additional 2: §3.2 canonicalization

- **Canonicalization (Additional 2, REPLACES "ASCII-normalized identifiers") [OPERATIVE].**
  - **Encoding of I:** the fields in the fixed order listed for τ_D, each as a tag byte (present / explicit null / absent) followed by a 64-bit big-endian length and the value bytes. Length prefixes make concatenation unambiguous ("ab" + "c" ≠ "a" + "bc").
  - **Identifiers** (account, instrument, exec_id, order_id): the exact byte string the broker sent, after decoding only the transport encoding declared for that path (for example a JSON string → its UTF-8 bytes). **Prohibited:** case folding; trimming or collapsing whitespace; Unicode normalization (NFC, NFKC, …); stripping leading zeros; reinterpreting a string as a number or a number as a string; truncation; any lossy mapping.
  - **Path representation differences** (the same broker id arriving as JSON number 123 on one path and string "123" on another) may be reconciled only by a **declared, injective per-path decoding**, pinned by parser version and recorded in the lineage. An undeclared difference leaves the identities **distinct**.
  - **Integers:** signed 64-bit, big-endian two's complement. A value outside that range is malformed.
  - **Why this direction:** splitting one broker identity into two is fail-safe. The second claim meets the same predecessor and is detected as FORK → CONFLICT, which costs availability. **Collapsing two broker identities into one is fail-unsafe:** a distinct transition is discarded as a duplicate, and F_d undercounts (CX-61). Every permitted transformation must therefore be injective over the broker's identifier space. **DERIVED.**
  - Hash: SHA-256 over the encoding. Collision resistance is **ASSUMED**.
  - Pinned by parser version within the lineage. The full determinism environment remains open in OQ-H16; this item fixes the identifier encoding only and does not close OQ-H16.

---

## 3. Counterexamples

### 3.1 Exposed by this review (all corrected in draft 3)

| **CX-57** | draft-2 review | an ORDER_CONTRADICTION empties ExecutionState(x, β_c); draft-2 row 8 "every choice gives d = 0" is vacuously true → RECONCILED, marked Bounded yes. Rev 3.1 line 148 would still make it UNBOUNDED, so Π's BOUNDED test blocks, but the candidate's own table contradicted it. This was a latent false-permission path for any implementation that followed the table (DERIVED). Corrected (SR, row 7) |
| **CX-58** | draft-2 review | L = 150, F_max = 100, B = 40 (U = 140), buy Q = 30. The pre-proposal reading U(ρ) = 140 ≤ 150 passes, and the commit yields U = 170 > L: **false permission**. Sell: F_min = 100, S = 60 (A_raw = 40), Q = 50 passes A_raw ≥ 0 and yields A_raw = −10. Corrected (Π over ρ ⊕ r) |
| **CX-59** | draft-2 review | (a) reading B as Σ reservations + Σ WORKING orders counts an ACTIVE reservation's AUTHORIZED order twice: over-denial. (b) a two-step consume (reservation CONSUMED, then the order SUBMITTED in a later revision) with B counting unexpired reservations plus non-AUTHORIZED working orders leaves one revision in which the commitment counts zero times: **false permission** for any evaluation in that revision. Corrected (one identity; atomic consume) |
| **CX-60** | draft-2 review | p_b = p_C with a receive path that appends without folding. A bust keyed ≤ H_c is appended after the evaluated frontier but before C. It lies inside the prefix, so it is never "received after p_b" and never triggers the retro-relevance test. The basis stays INTACT although the decision never saw the bust: a missed BASIS_IMPUGNED. Corrected (fold discipline; p_b = p_C − 1 = f(ρ)) |
| **CX-61** | draft-2 review | exec_ids "a1B" and "A1b" are distinct at the broker and fill 5 each. Case folding gives the same τ, so the second is a duplicate and F_d undercounts a buy by 5: **false permission** at the margin. Corrected (no non-injective normalization) |
| **CX-62** | draft-2 review | chain v0 fill 100 (κ ≤ W), v1 correct 100 → 40 (δ = −60, ⊥, list only), v2 correct 40 → 70 (δ = +30, κ ≤ W). Without A-11-ORD, v1 may have been emitted after W. The stream-prefix truth at W is then 100 + 30 = 130. The chain-state hull {0, 100, 40, 70} has maximum 100 and excludes 130, so the bound is **unsound**. H_Δ = [100 + 30 − 60, 100 + 30] = [70, 130] contains both 130 and 70. Corrected (H_Δ; the draft-2 soundness claim withdrawn) |

### 3.2 For the deferred items

| ID | Deferred item | Counterexample showing why it is not adopted now |
|---|---|---|
| **CX-63** | Scoped SR: ignore unresolved items that do not affect β_c or head | A held anchor correction (pre-bootstrap, the named version unknown) has no key above β0, so a key-based scope ignores it. Yet its resolution changes x's contribution at **every** later cut (R7 §5): applying it moves F_d(β_c) and F_d(head) by the correction delta. A scope defined by keys therefore drops an item that does affect both cuts. A correct scoped SR needs a per-item dependence argument that is not written. Until then the global SR stands (C-14). DERIVED |
| **CX-64** | Hull under instant snapshot semantics | Chain v0 fill 100 (κ ≤ W), v1 correct 100 → 40 (κ > W). Under instant semantics, v1 may have occurred before the snapshot instant and been emitted late, so the truth at the snapshot is 40. H_Δ excludes Out and gives [100, 100], which excludes 40 and is **unsound** under that semantics. A hull that is sound under both semantics must treat Out like Free, [40, 100], at the cost of more MISMATCH. Which semantics the broker has is UNVERIFIED (C-16). Draft 3 follows Rev 3.1 W1 as written (stream-prefix) and records the dependency instead of silently choosing the wider hull. DERIVED |

---

## 4. Updated consistency and conflict register (candidate §13.1, complete)

| # | Conflict | Where | Resolution path |
|---|---|---|---|
| C-1 | Time-based finality narrows bounds, which P-1 forbids (CX-31) | §2 P-1 / §6 | FD-15: (a) keeps P-1 strict; (b) requires P-1a |
| C-2 | AM-13′ worst-case labelling versus the required three-way placement rule | §7.4 | OQ-H15 |
| C-3 | BASIS_UNDER_SUPERSEDED_RULES conflates historical validity with policy exposure | §7.6 | OQ-H19 |
| C-4 | FD-3 "permanent MISMATCH" together with R-15″ permanently suspends buy reservations whenever unsequenced executions exist | §8 #10 / §7.2 | decide FD-3 knowing this |
| C-5 | FD-11(b) (exclusivity violation is structural) changes the reduction outcomes of V11, V12 and V22–V25 | §4 A-15 / Rev 3.1 §2.10 | rewrite the vectors if (b) is chosen |
| C-6 | D_max withdrawal (FD-10(a)) requires restating V44's D_max half | §7.1 / Rev 3.1 V44 | editorial, after FD-10 |
| C-7 | CA-15 activation over existing working sells can force OVER_RESERVED immediately (CX-39, CX-45). An availability shock, not unsafe | §5.1 / §7.6 | activate at bootstrap; measure |
| C-8 | Fail-closed handling is a denial-of-service surface (CX-52) | §9 | FD-20; D23 |
| C-9 | Lists that omit busted executions make absence ambiguous (CX-40) | §3.6, §8 | AM-9 (R7): lists declare their bust semantics; an undeclared semantic counts as "excluded", so an absence widens downward |
| C-10 | A-11-ORD is unverified, and cannot be checked where ⊥ versions are involved. Without it, admissible cuts degrade to the hull (more MISMATCH, less availability) | §3.5 | OQ-H17; broker evidence |
| C-11 | If FD-1′ is declined, the evidence model of Rev 3.1 §2.8 remains self-contradictory (CX-20) | §9 | FD-1′ |
| C-12 | Finality outcomes at equal timestamps depend on arrival order; the interim convention is conservative but unproven | §6.2 | OQ-H18 |
| C-13 | I13 (R6) forbids non-admissible cuts in every bound; in H_Δ mode, non-prefix subsets contribute. I13 is amended to admissible-cut mode only | §3.5 | review of the amendment; A-11-ORD evidence |
| C-14 | SR is account-global. A single unresolved item anywhere (for example an old-epoch conflict) makes the status UNKNOWN and denies everything. This widens the fail-closed denial-of-service surface of C-8 | §8 | FD-20 / C-8 analysis; a scoped SR would need its own soundness argument |
| C-15 | Rev 3.1 §2.9 reservation state RELEASED (after submission: reject, cancel, fill) is re-expressed as CONSUMED with a terminal order. The counted R is identical, but the state names differ from the frozen text | §7.2 | editorial reconciliation at any freeze |
| C-16 | H_Δ relies on stream-prefix snapshot semantics (W1 as written). If the broker's snapshots report the internal state at an instant, keyed-after-β transitions can be inside the snapshot, and H_Δ's exclusion of Out is unsound. Snapshot semantics are UNVERIFIED | §3.5, W1 | broker evidence; OQ-H17 (related, not closed) |
| C-17 | Fold discipline: append and fold are one step. A slow fold delays receipt; a commit waits for the backlog. Liveness only; the safe direction | §3.1, §7.1 | interacts with the IC-4 convention and OQ-H18 |

Superseded wording added to candidate §11:

| Draft 2 §8 row 8 "otherwise (every choice gives d = 0)", and its "Bounded: yes" column | SR gate (row 7) + rows 8–9; BOUNDED per Rev 3.1 line 148 | vacuous truth on empty sets; structural states fell through (P0-1, CX-57) | draft-2 review |
| Draft 2 §7.3 "For a buy r: U(ρ) ≤ L … already counted" (used at commit) | Π over σ with r counted exactly once; ρ ⊕ r at commit | readable as a pre-proposal check (P0-2, CX-58) | draft-2 review |
| Draft 2 §7.2 "every unexpired reservation contributes its order's R" | single commitment identity order_id; B, S = Σ R over WORKING orders | readable as a second summand; handoff unspecified (P0-3, CX-59) | draft-2 review |
| Draft 2 §7.1 step 6 "append the L1 commit record; write the L3 basis record" and §7.4 "basis record" | basis inside L1 commit record C; p_b = p_C − 1; fold discipline | two schemas; p_b boundary ambiguous (P1-1, CX-60) | draft-2 review |
| Draft 2 §3.5 hull of chain states "{0} ∪ {q_i : not forced after β}", **DERIVED sound** | H_Δ | unsound without A-11-ORD (CX-62); claim withdrawn | draft-2 review |
| Draft 2 §3.2 "ASCII-normalized identifiers" | injective, length-prefixed byte encoding | non-injective normalization can collapse identities (CX-61) | draft-2 review |

Change-ledger rows added to candidate §14:

| P0-1 SR predicate; status row 7; rows renumbered 8–9; truth table | draft-2 review | §2.6.2 | DERIVED (hand-enumerated) | OPERATIVE |
| P0-2 Π over σ with r counted once (ρ ⊕ r at commit) | draft-2 review | §2.9, §2.4 | DERIVED | OPERATIVE |
| P0-3 single commitment identity; state mapping table; atomic consume; exclusive pre-submission exits | draft-2 review | §2.9, I6, T04, T05 | DERIVED | OPERATIVE (RELEASED CONDITIONAL-ON-FD-13) |
| P1-1 fold discipline; L1 operation records; basis in L1 commit record; p_b = p_C − 1 | draft-2 review | §2.2.A, §2.9 | DERIVED | OPERATIVE (basis completeness CONDITIONAL on OQ-H16) |
| Additional 1: delta hull H_Δ; I13 amended; draft-2 hull withdrawn | draft-2 review | §2.2.E | DERIVED; relies on stream-prefix W1 (UNVERIFIED) | OPERATIVE-PROVISIONAL |
| Additional 2: injective identifier encoding | draft-2 review | §2.2.B | DERIVED; hash collision resistance ASSUMED | OPERATIVE |

Open questions, unchanged and open:

| **OQ-H15** | Define the admissible historical placements of retro-relevant evidence, especially unsequenced events. Required rule: INTACT iff every admissible placement allows; IMPUGNED iff every placement denies; INCOMPLETE iff mixed | §7.4 AM-13′ | the worst-case Π evaluation | **known defect**: the current text labels "some placement denies" as IMPUGNED, which over-reports impugnment. Not yet corrected |
| **OQ-H16** | Specify the full deterministic execution environment for reproducing Π from the basis: precision and rounding (integers only per A-13, to be confirmed for all derived values), schema and canonicalization versions, collection ordering, clock inputs, every external input, tie-breaking, runtime version | §3.1 I9-ext, §7.4 | "complete by construction" | **CONDITIONAL**; contract not written |
| **OQ-H17** | Define legitimate broker version-counter resets: does a reset create a version epoch; can an execution survive across it; how are old list entries interpreted; keep the broker version distinct from the stream sequence. **Also: cross-namespace ordering (INT-02).** Under what broker guarantee does chain order equal stream-key order (A-11-ORD), and how should ⊥ versions be ordered against keyed ones when A-11-ORD cannot be checked? | §3.2 A-11⁗, §3.4 | none | open |
| **OQ-H18** | Finality ordering at exact ticks, and the outage boundary cases: an outage before or at the deadline; several outages; an outage during the latency allowance; a blocker arriving or dismissed at the tick; an applied correction and the tick together. Keep T_f, L_n, σ and observed stream health separate | §6.2 | gate W ∧ H ∧ ¬Blocker | provisional; only two examples |
| **OQ-H19** | Distinguish historical authorization invalidity from policy-migration exposure: a separate POLICY_MIGRATION_EXPOSURE class instead of "treated like BASIS_INCOMPLETE" | §7.6 AM-14′ | BASIS_UNDER_SUPERSEDED_RULES treated like INCOMPLETE | **known defect** (conflation). Not yet corrected |
| **FD-20** | authentication trade-off | §9 | — | **UNRESOLVED founder decision** |
| Others | FD-1′, FD-2″, FD-3, FD-7, FD-8, FD-10 to FD-19 | various | marked [CONDITIONAL-ON-FD-n] | open (§10) |

---

## 5. Acceptance tests and vectors that remain unexecuted (candidate §13.3, complete)

| Group | Items | Source | Status |
|---|---|---|---|
| Limitation vectors | V63 (CX-01), V64 (CX-12), V65 (CX-08), V66 (CX-27), V67 (C-1) | R1 R-14, R2, R4 | hand-derived; not executed |
| Clarification vectors | V68 to V73 (A-1, B-1, D-1, the A-1 absence variant, C-2, the naive-adopt negative) | R4 CA-9 | hand-derived |
| E/F/G vectors | V74 to V83 | R5 | hand-derived |
| H vectors | V84 to V94 | R6 | hand-derived |
| Draft-3 vectors | V104 status truth table including every SR clause, empty X(β) and no-watermark quiescent; V105 an ORDER_CONTRADICTION on an otherwise d = 0 ledger → UNKNOWN (STRUCTURAL), never RECONCILED (CX-57); V106 buy with U = 140, L = 150, Q = 30 → DENY at commit (CX-58); V107 sell with A_raw = 40, Q = 50 → DENY (CX-58); V108 consume interleaved with an evaluation: no revision with R counted 0 or 2 times (CX-59); V109 expiry racing consume → exactly one wins; V110 a bust keyed ≤ H_c arriving between the frontier and C is impossible by fold discipline, and arriving after C triggers the retro-relevance test (CX-60); V111 distinct exec_ids "a1B" and "A1b" → distinct τ (CX-61); V112 the CX-62 chain → H_Δ contains 130 and 70; V113 under A-11-ORD, every admissible cut sum lies in H_Δ | draft-2 review | specified; **not executed** |
| Integration vectors (draft 2) | V95 status truth table (every combination → one row; rows 4 and 5 reachable); V96 τ_D: one transition via a keyless list and a keyed stream → one τ, key attached (CX-54); V97 KEY_MISMATCH; V98 broker versions 0, 2, 5 → no gap (CX-55); V99 A-11-ORD violation between keyed versions → ORDER_CONTRADICTION; V100 two concurrent commits on one revision → at most one reservation, the other re-evaluates; V101 duplicate proposal_id with a different hash → R_PROPOSAL_CONFLICT; V102 new-epoch events applied, status UNKNOWN until an e* snapshot; V103 evidence received at the tick time precedes the FINAL tick (IC-4, provisional) | integration review | specified; **not executed** |
| Rule acceptance tests | AM-1 to AM-9 (R7 §12); AM-10 to AM-16 (R8); AM-11′, AM-13′, AM-14′, AM-15′, AM-16′, AM-17 (R9) | R7–R9 | specified; not executed |
| Oracle and verification obligations | R-04 (G3 in every classification); R-05 (unknown-side orders in the oracle domain and grid); R-06′ (raw-fact grid, separate status checker, import ban, mutation suite: monotone-only GAP, narrow GAP, pre-W0 apply, REPLAY-ignore, independent placement, digest-only basis, τ from Sentinel index); admissible-cut enumeration; layer re-derivation byte-equality; finality deferral against stream-health intervals; interleaving tests of migration | R1, R2, R6–R9 | specified; **no oracle exists** |
| Rev 3.1 §5.7 prerequisites | items 1 to 9, plus additions from R4 CA-10, R5, R6, R7 | various | not produced |

**Every row above is unexecuted.** Nothing in this pass ran a vector, a truth-table enumeration, an oracle, a mutation suite or an interleaving test.

---

## 6. Claims by label (this pass)

- **DERIVED:**
  - P0-1: the SR gate and the truth table's exclusivity, exhaustiveness and no-fall-through;
  - P0-2: the Π equivalence with Rev 3.1 `evaluate`, and r counted exactly once;
  - P0-3: no double count and no zero-count revision;
  - P1-1: no L1 item lies between p_b and p_C;
  - Additional 1: H_Δ containment (i) to (iii);
  - Additional 2: split is fail-safe and collapse is fail-unsafe;
  - CX-57 to CX-64.
- **COMPUTED:** none. No machine arithmetic or enumeration was run.
- **ASSUMED:**
  - SHA-256 collision resistance;
  - A-11-ORD (where declared);
  - A-11‴ and A-11⁗;
  - A-12″, A-14″, A-15, A-16 / A-16b and A-17 (carried over).
- **CONDITIONAL:**
  - RELEASED on FD-13;
  - basis completeness on OQ-H16;
  - CHANNEL_SUSPECT's place in SR on FD-20;
  - H_Δ on stream-prefix snapshot semantics.
- **UNVERIFIED:**
  - every broker capability;
  - stream-prefix versus instant snapshot semantics (C-16);
  - declared per-path decodings.
- **UNBOUNDED:** status rows 1–7.
- **Withdrawn:** the draft-2 hull's "DERIVED sound".
- **OPEN:** OQ-H15, OQ-H16, OQ-H17, OQ-H18, OQ-H19; FD-20 (founder decision, unresolved).

---

## 7. Confirmation

**No implementation, oracle construction or execution, broker contact, paper trading, live trading, or freeze occurred.** No acceptance test or vector was executed, V104 to V113 included. The only machine operations were text edits to the candidate, with exactly-once replacement assertions, a byte comparison confirming Rev 3.1 unchanged, and SHA-256 hashing. Draft 3 supersedes draft 2 as candidate text; drafts 1 and 2 remain in git history.

**Readiness: NO-GO** for freeze and implementation. Four successive hand-review rounds have each found new defects, three of them false-permission paths in this round. The specification is not converging toward verified closure by review alone. The next useful step is an oracle that is independently specified and independently built, not a fifth hand-review round. Authorizing that oracle is a founder decision, and this document does not make it.
