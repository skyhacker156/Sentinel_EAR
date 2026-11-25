# EAR v0.1 Rev 3.2 Candidate: Response to the Integration Defect Review

- **Author:** Claude (Specification Lead / ARBITER)
- **Date:** 2026-11-24
- **Responds to:** A-TEAM DISPATCH, "EAR REV 3.2 CANDIDATE — INTEGRATION DEFECT REVIEW" (GPT)
- **Reviewed object:** `ear/candidate/EAR_v0.1_Rev3.2_CANDIDATE.md`, draft 1 (SHA-256 `583ab609422baac1d8f8f582132bdc19dd2713995c19bc11c874382c60e82e52`)
- **Produces:** candidate draft 2 (SHA-256 given in the push manifest; see §7)
- **Baseline:** Rev 3.1 FROZEN, SHA-256 `dd9d87f76b01134e084827b0202c73c52fccb2b86f21a176a6b6e551241fa239`. **Not modified.** Byte comparison against the pushed copy: identical.

**Boundary.** This is specification consolidation only. There is no freeze, no implementation, no oracle construction or execution, no broker contact or broker-capability assertion, and no paper or live trading authorization. FD-20 remains a founder decision and is **not** made here. OQ-H15 to OQ-H19 remain **open**. Agreement between GPT and Claude on any item below is not independent verification.

---

## 1. Disposition table

| ID | Defect (short) | Disposition | Where in draft 2 | Label |
|---|---|---|---|---|
| INT-01 | The GAP predicate ("…or W > H_e") swallowed AWAITING-BEHIND, making it unreachable | **CORRECTED.** Status precedence table (rows 1–8) with a truth-table check | §8 (§2.6.2) | DERIVED (hand-enumerated) |
| INT-02 | κ conflated with the broker version index ("versions 0..k", "κ ≤ β ⇔ i ≤ k") | **CORRECTED.** The chain is built from predecessor links; i is the chain position; non-contiguous broker numbers are not gaps; a new contract A-11-ORD; partial-order hull without it | §3.5; §4 A-11-ORD; OQ-H17 extended | ASSUMED (A-11-ORD) / DERIVED |
| INT-03 | τ_D included κ, so the same transition on two paths hashed differently | **CORRECTED.** τ_D over the identity field set I, excluding all ordering and transport metadata; attribute reconciliation; KEY_MISMATCH | §3.2 | DERIVED; CONDITIONAL on A-11‴ |
| INT-04 | Commit "no reservation exists" check: scope and atomicity unstated | **CLARIFIED.** Scope = proposal_id within the single account; seven-step serialized critical section; concurrent-commit behaviour | §7.1 | DERIVED |
| INT-05 | *(found by this author while fixing INT-01)* R3 case 8 "buffered pending bootstrap" contradicted R4 D-1 (applied) | **CORRECTED.** New-epoch events are applied; status UNKNOWN (EPOCH_UNBOOTSTRAPPED) until an e* snapshot is accepted | §8 rows 2 and 8 | DERIVED |
| IC-1 | FD-1′ open while its terminology and profile were marked OPERATIVE | **CORRECTED** (markers). Now CONDITIONAL-ON-FD-1′; if declined, CX-20 stays blocking | §9; §3.9 profile | — |
| IC-2 | Unsequenced executions both "out of contract" (A-11″) and given interval treatment (§8 #10) | **CLARIFIED.** These are two classes: identified-but-unsequenced (FD-3) and unidentified-and-unsequenced (FD-8) | §4 A-11″; §8 row 10 | — |
| IC-3 | P-RA × unauthenticated evidence / CHANNEL_SUSPECT | **CLARIFIED.** P-RA is scoped to attributed evidence; unattributed evidence is governed by AM-17 and FD-20 | §2 P-2 | DERIVED |
| IC-4 | Finality ordering of simultaneous events | **UNRESOLVED** (OQ-H18 stays open). An interim conservative convention is recorded and explicitly marked *not a resolution* | §6.2 | — (OPEN) |
| IC-5 | "Basis determinism" stated as OPERATIVE while its environment is OQ-H16 | **CORRECTED** (marker). I9-ext is OPERATIVE-PROVISIONAL, CONDITIONAL on OQ-H16 | §3.1 | DERIVED |
| IC-6 | R4 filename dated 2026-11-25 | **CLARIFIED.** The filename carries the dispatch date; the file is hash-pinned and is not renamed | §0.3 | — |

Rejected: none.

---

## 2. Exact replacement text (as applied in draft 2)

The text below is copied verbatim from candidate draft 2. Where the dispatch and the candidate differ, the candidate governs.

### 2.1 INT-01 and INT-05: §8, status (replaces the draft-1 status rules and the Rev 3.1 GAP rows)

**§2.6.2 status [OPERATIVE] (INT-01 and INT-05, REPLACES draft 1 and the Rev 3.1 GAP rows at lines 418 and 499).**

Inputs:
- S = the latest accepted snapshot, with boundary (e_s, W) or no watermark;
- e* = the newest epoch with any received message;
- for every epoch e: H_e and M_e.

Status is the **first** row that applies. The rows are mutually exclusive by precedence and exhaustive because row 8 is the default (DERIVED). Every condition that holds is also listed as a reason code, whatever the status.

| # | Condition | Status | Bounded |
|---|---|---|---|
| 1 | no accepted snapshot; or S stale beyond S_lim; or conflicting snapshots at one watermark | UNKNOWN | no |
| 2 | e* > e_s (an epoch has begun with no accepted snapshot in it): **EPOCH_UNBOOTSTRAPPED** (INT-05) | UNKNOWN | no |
| 3 | ∃ e: H_e < M_e (a recorded hole, in any epoch, including old ones) | GAP | no |
| 4 | S has W > H_{e_s}, and the wait limit (D08) has passed | GAP (AB_TIMEOUT) | no |
| 5 | S has W > H_{e_s} (S ahead of everything received; no hole) | AWAITING-BEHIND | no |
| 6 | S has no watermark and the ledger is not quiescent | AWAITING-UNVERIFIED | no |
| 7 | W ≤ H_{e_s} = M_{e_s}, and some admissible inclusion choice gives d ≠ 0 | MISMATCH | yes (by d) |
| 8 | otherwise (every choice gives d = 0) | RECONCILED if no applied event has κ > (e_s, W); otherwise AWAITING | yes |

- Buffered events (received above H_e + 1) exist **iff** row 3 holds. They have no separate status.
- **INT-05, new-epoch events.** Events of epoch e* are **applied** to F_d on receipt, in key order, as deltas (§3.7). They are not buffered. Draft 1 and R3 case 8 said "buffered pending bootstrap"; that wording is SUPERSEDED. The status is UNKNOWN (row 2) until a snapshot of e* is accepted and compared. That comparison is the mechanism that reveals an old-epoch tail loss (C4-R). Applying the events keeps the accounting current; withholding boundedness keeps authorization safe.
- **Truth-table check (DERIVED, hand-enumerated):** every combination of {snapshot accepted / stale / conflicting / absent} × {e* = e_s / e* > e_s} × {hole in some epoch: yes / no} × {W vs H_{e_s}: below-or-equal / above} × {watermark: yes / no} × {quiescent: yes / no} × {wait limit passed: yes / no} maps to exactly one row. Rows 4 and 5 are now reachable and distinct. AWAITING-BEHIND (row 5) arises exactly when the snapshot is ahead and nothing above H has arrived.

Sequence-transition rows changed in the same section:

| 8 | new epoch | events applied; status UNKNOWN (EPOCH_UNBOOTSTRAPPED) until an e* snapshot is accepted; old holes keep GAP (row 3) and the band UNBOUNDED |
| 10 | unsequenced execution **with** an exec_id | interval; MISMATCH ([CONDITIONAL-ON-FD-3]). *IC-2:* this class (identified, no broker_seq) is distinct from the A-11″ out-of-contract class (**neither** exec_id **nor** broker_seq, FD-8). FD-3 decides whether this class too becomes out of contract |

**Superseded by this:**
- the draft-1 rule "GAP if a hole exists **or the snapshot boundary has W > H_e**" (from R4 CA-8);
- R3 case 8 "e′ messages buffered pending bootstrap".

### 2.2 INT-02: §3.5, chain and cut (replaces the draft-1 "versions 0..k" wording)

- **Chain (INT-02, REPLACES draft 1):** x's versions are linked by their broker predecessor claims (prior_version names the exact predecessor), giving positions i = 0, 1, …, n. **i is the chain position, not the broker version number.** Broker version numbers are strictly increasing (A-11⁗) but **need not be contiguous**: a skipped number is not a gap. A *gap* exists only when a named predecessor has not been received (PENDING).
- **Order-coherence contract, A-11-ORD (ASSUMED, new; UNVERIFIED):** for one exec_id, if v_i precedes v_j in the chain and both are keyed, then κ(v_i) < κ(v_j). The broker emits an execution's transitions on the stream in version order.
  - A violation between two keyed versions is detected (ORDER_CONTRADICTION, AM-10).
  - Where one or both are ⊥, the contract is **assumed, not checked**.
- **Cut** k at β: positions 0..k lie at or before β. **Admissible** iff (a) k respects the chain, and (b) for every keyed version v_i, κ(v_i) ≤ β ⇔ i ≤ k. Under A-11-ORD, (b) yields k ∈ [i_lo, i_hi − 1].
- **Without A-11-ORD** (broker does not guarantee stream order matches version order): (b) is not available. The relative order of chain position and stream key is **unresolved**, and the candidate uses the partial-order hull below for x. *Placing keyed versions by their keys alone is not permitted.*

New assumption row (§4):

| **A-11-ORD** (new, INT-02) | for one exec_id, chain order equals stream-key order wherever both versions are keyed; the broker emits an execution's transitions in version order | E | this draft | OPERATIVE; UNVERIFIED. Without it, the partial-order hull applies (§3.5) |

OQ-H17 extended (§12):

| **OQ-H17** | Define legitimate broker version-counter resets: does a reset create a version epoch; can an execution survive across it; how are old list entries interpreted; keep the broker version distinct from the stream sequence. **Also: cross-namespace ordering (INT-02).** Under what broker guarantee does chain order equal stream-key order (A-11-ORD), and how should ⊥ versions be ordered against keyed ones when A-11-ORD cannot be checked? | §3.2 A-11⁗, §3.4 | none | open |

### 2.3 INT-03: §3.2, τ_D (replaces the draft-1 τ_D, which included κ)

  - τ_D (INT-03, REPLACES draft 1): SHA-256 of the canonical **identity field set** I = (account, instrument, exec_id, kind, side, order_id, **broker** prior_version, prior_qty, qty). It **excludes ordering and transport metadata**: κ, the epoch, event_id, received_at, headers, list or message envelopes, the broker's resulting version number. Those are *attributes* of a delivery, not of the transition. **Sentinel's internal version index never enters τ.**
  - **Attribute reconciliation** for one τ seen on two paths:
    - κ present on both and equal → consistent;
    - κ present on both and different → **CONFLICT (KEY_MISMATCH)**;
    - κ present on one path only → the key is **attached** to the transition by an L3 record. This is an applied disposition from attributed evidence, not a narrowing by unapplied data (P-RA);
    - the same comparison applies to the broker resulting version.
  - **Incomplete identity fields** on a path (any field of I missing): no τ_D can be formed. The delivery may *corroborate a value* (an L3 note) but never binds or deduplicates. If no path supplies a complete I and there is no τ_B, the transition is out of contract.
  - **Broker guarantee required (A-11‴, extended):** every path that reports a transition supplies every field of I, with identical values.
  - Neither available → the transition is out of contract (UNRESOLVED).

### 2.4 INT-04: §7.1, commit (replaces "no reservation exists")

- **Commit (INT-04, REPLACES "no reservation exists").** Reservation scope: **proposal_id within the single configured account** (Rev 3.1 I5 and R31-06B). One serialized critical section of the store performs, with no interleaving:
  1. acquire the store lock;
  2. read t_L;
  3. look up any reservation for proposal_id:
     - same proposal_hash → return the existing reservation (R_DUPLICATE), and stop;
     - different hash → refuse (R_PROPOSAL_CONFLICT), and stop;
  4. evaluate E_L at as_of t_L on the current revision;
  5. require ALLOW, the same revision, item hash and configuration hash as D, and the proposal_hash of D;
  6. create the reservation and its AUTHORIZED order (one record); append the L1 commit record; write the L3 basis record (§7.4); advance the revision;
  7. release the lock.
- **Concurrent commits** serialize on the lock.
  - Another proposal's commit advances the revision, so the decision D no longer matches and must be re-evaluated. Its own reservation's R is then counted, as in V14 and V36.
  - A second commit of the same proposal_id hits step 3.
  - No reservation exists outside step 6. No two reservations can be created on one revision.

### 2.5 IC-1: §9, terminology

- **Terminology [CONDITIONAL-ON-FD-1′]** (R2 R-02′). *IC-1:* draft 1 marked this OPERATIVE while FD-1′ was open. If FD-1′ is declined, Rev 3.1 §2.8 stands, and **CX-20 remains a blocking inconsistency** (the literal evidence model contradicts every ALLOW vector). accepted snapshot; corroboration; independent evidence.

### 2.6 IC-2: §4, A-11″ row

| **A-11″** (REPLACES A-11) | *(IC-2: two unsequenced classes are kept apart. Identified-but-unsequenced is §8 #10 / FD-3. Unidentified-and-unsequenced is the class below / FD-8.)* exec_id is broker-unique per account, stable across epochs and paths; event_id is message identity only; a delivery with neither exec_id nor broker_seq is out of contract ([CONDITIONAL-ON-FD-8]) | E | R4 CA-3 | OPERATIVE; UNVERIFIED |

(§8 row 10 is quoted in §2.1 above.)

### 2.7 IC-3: §2, P-2

**P-2. Receipt asymmetry (P-RA) [OPERATIVE]** (R8). *Scope (IC-3):* P-RA governs **attributed** evidence, meaning evidence that has passed the attribution rule of §9. Unattributed evidence is channel evidence. It is governed by AM-17 and CHANNEL_SUSPECT, whose effect is FD-20 (unresolved). Under FD-20(b), not acting on unattributed evidence is permitted only because A-17 is assumed; that is not an application of P-RA. Evidence that is received but not applied may widen, block, defer finality or impugn a basis. It may never narrow, grant, start or restart a finality clock, or advance an effective version. **DERIVED** as a corollary of P-1.

### 2.8 IC-4: §6.2, interim convention (OQ-H18 open)

- **Interim determinism convention (IC-4) [OPEN under OQ-H18; not a resolution].**
  - Processing order is L1 log position (D20), so outcomes are deterministic *for a given log*. At equal timestamps, though, they depend on arrival order.
  - Conservative interim rule: a FINAL tick record for time t is appended only after the receive path has appended every item with received_at ≤ t. So evidence that is simultaneous with the tick is always processed **before** it: blocking or applied evidence takes precedence over finality.
  - Whether this is sufficient, including outage start and end at the tick and an applied correction at the tick, is exactly OQ-H18.

Note: this convention defers FINAL whenever the receive path is behind. That is the safe direction, but it adds a liveness dependency on receive-path progress. It is recorded under C-12.

### 2.9 IC-5: §3.1, I9-ext

**I9-ext [OPERATIVE-PROVISIONAL; CONDITIONAL on the determinism contract, OQ-H16]:** L2, L3 and L4 are pure functions of (L1, model version, configuration, **and the determinism environment of OQ-H16**). Stored layers must be byte-identical to re-derivation. A model-version change creates a new derivation lineage; old lineages are kept. **DERIVED.** The determinism *environment* is open (OQ-H16).

### 2.10 IC-6: §0.3

**Note (IC-6):** R4's filename carries the date of the dispatch it answered (2026-11-25). The document was prepared on 2026-11-24 (ET). The filename is kept unchanged because the file is hash-pinned; renaming it would break the record.

---

## 3. New counterexamples

| **CX-53** | integration review | the draft-1 GAP predicate made AWAITING-BEHIND unreachable (a snapshot ahead with no hole reported GAP). Availability and reason-code defect, not a false permission (DERIVED). Corrected (§8 table) |
| **CX-54** | integration review | τ_D with κ: the same transition via a list without a key and the stream with one gave different τ, so the predecessor check reported STALE → a false CONFLICT (availability). Without ν, a list-first ordering also produces it. Corrected (τ_D over I) |
| **CX-55** | integration review | broker versions 0, 2, 5 (strictly increasing, skipping). Treating 1, 3 and 4 as missing makes x falsely PENDING/UNRESOLVED; treating numbers as contiguous positions mis-links the chain. Corrected (chain by predecessor links) |
| **CX-56** | integration review | FD-1′ declined while R-02′ was marked operative: the vectors assume FIXTURE_PASS, yet the literal §2.8 denies everything. A specification contradiction. Corrected by marking (IC-1); still blocking if FD-1′ is declined |

**New conflicts recorded in §13.1:**

| C-10 | A-11-ORD is unverified, and cannot be checked where ⊥ versions are involved. Without it, admissible cuts degrade to the hull (more MISMATCH, less availability) | §3.5 | OQ-H17; broker evidence |
| C-11 | If FD-1′ is declined, the evidence model of Rev 3.1 §2.8 remains self-contradictory (CX-20) | §9 | FD-1′ |
| C-12 | Finality outcomes at equal timestamps depend on arrival order; the interim convention is conservative but unproven | §6.2 | OQ-H18 |

**New vectors (specified, not executed), added to §13.3:**

| Integration vectors (draft 2) | V95 status truth table (every combination → one row; rows 4 and 5 reachable); V96 τ_D: one transition via a keyless list and a keyed stream → one τ, key attached (CX-54); V97 KEY_MISMATCH; V98 broker versions 0, 2, 5 → no gap (CX-55); V99 A-11-ORD violation between keyed versions → ORDER_CONTRADICTION; V100 two concurrent commits on one revision → at most one reservation, the other re-evaluates; V101 duplicate proposal_id with a different hash → R_PROPOSAL_CONFLICT; V102 new-epoch events applied, status UNKNOWN until an e* snapshot; V103 evidence received at the tick time precedes the FINAL tick (IC-4, provisional) | integration review | specified; **not executed** |

---

## 4. Superseded wording (added to candidate §11)

| Draft 1 §8 GAP rule (from R4 CA-8): "…or the snapshot boundary has W > H_e" | §8 status table | made AWAITING-BEHIND unreachable (INT-01, CX-53) | integration review |
| Draft 1 §3.2 τ_D including κ | τ_D over the identity field set I; κ as an attribute | broke cross-path identity (INT-03, CX-54) | integration review |
| Draft 1 §3.5 "versions 0..k", "κ ≤ β ⇔ i ≤ k" unqualified | chain positions + A-11-ORD; hull without it | assumed broker-version/stream-key equivalence (INT-02, CX-55) | integration review |
| Draft 1 §7.1 "no reservation exists" | scoped, atomic commit procedure | scope and atomicity unstated (INT-04) | integration review |
| R3 case 8 "e′ messages buffered pending bootstrap" | §8 row 2: applied; status UNKNOWN | contradicted R4 D-1 (INT-05) | integration review |
| Draft 1 R-02′ marked OPERATIVE | CONDITIONAL-ON-FD-1′ | FD-1′ was open (IC-1, CX-56) | integration review |

---

## 5. Updated change ledger (rows added to candidate §14)

| INT-01 status precedence table (rows 1–8) | integration review | §2.6.2 | DERIVED (hand-enumerated truth table) | OPERATIVE (replaces draft 1) |
| INT-02 chain positions, A-11-ORD, hull fallback | integration review | §2.2, §2.11 | ASSUMED / DERIVED | OPERATIVE-PROVISIONAL (OQ-H17) |
| INT-03 τ_D identity set I, attribute reconciliation, KEY_MISMATCH | integration review | §2.2, §2.6.3 | DERIVED | OPERATIVE (CONDITIONAL on A-11‴) |
| INT-04 scoped atomic commit procedure | integration review | §2.9, I5 | DERIVED | OPERATIVE |
| INT-05 new-epoch events applied; EPOCH_UNBOOTSTRAPPED | this author, during the integration review | §2.6.2 | DERIVED | OPERATIVE |
| IC-1 R-02′ / profile marked CONDITIONAL-ON-FD-1′ | integration review | §2.8 | — | marker correction |
| IC-2 two unsequenced classes separated | integration review | §2.11, §2.6 | — | clarification |
| IC-3 P-RA scoped to attributed evidence | integration review | §2.4 | DERIVED | clarification |
| IC-4 interim tick-ordering convention | integration review | §6.2 | — | OPEN (OQ-H18) |
| IC-5 I9-ext conditional on OQ-H16 | integration review | §2.2 | — | marker correction |
| IC-6 R4 filename date note | integration review | §0.3 | — | clarification |

The ledger rows for R2–R9 carried over from draft 1 are unchanged.

---

## 6. Claims by status label (integration-review scope)

**DERIVED** (hand reasoning; not verified):
- the status table is mutually exclusive by precedence and exhaustive by default, and rows 4 and 5 are reachable (INT-01);
- τ_D over I gives one identity per transition across paths, provided A-11‴ holds (INT-03);
- non-contiguous broker numbering does not create false gaps under predecessor chaining (INT-02);
- the serialized commit creates at most one reservation per revision and per proposal_id (INT-04);
- applying new-epoch events while withholding boundedness keeps authorization safe (INT-05);
- P-RA as scoped is a corollary of P-1 (IC-3);
- the hull fallback is sound (§3.5, carried over).

**COMPUTED:** none in this pass. No arithmetic was executed by machine.

**ASSUMED:**
- A-11-ORD (new);
- A-11‴ extended to require the full field set I on every path;
- A-11″, A-11⁗, A-12″, A-14″, A-15, A-16 / A-16b and A-17 (carried over).

**CONDITIONAL:**
- §9 terminology and the evidence profile on FD-1′;
- §8 row 10 on FD-3;
- the A-11″ out-of-contract class on FD-8;
- I9-ext on OQ-H16;
- the τ_D binding on A-11‴;
- cut admissibility clause (b) on A-11-ORD;
- CHANNEL_SUSPECT's effect on FD-20.

**UNVERIFIED:**
- every broker capability, including A-11-ORD and the presence of field set I on every path;
- whether the IC-4 convention is sufficient.

**UNBOUNDED:**
- status rows 1–6 (UNKNOWN, GAP, AWAITING-BEHIND, AWAITING-UNVERIFIED) give no bound;
- old-epoch holes after a new epoch stay UNBOUNDED (row 3).

**OPEN (not closed by this pass):**
- OQ-H15 (retro-relevance / worst-case impugnment);
- OQ-H16 (determinism environment);
- OQ-H17 (version resets, now also cross-namespace ordering);
- OQ-H18 (exact-tick ordering; IC-4 is interim only);
- OQ-H19 (migration conflation);
- **FD-20** (the founder's decision; unresolved).

---

## 7. Execution statement

**No acceptance tests, vectors, oracle or implementation were executed.** Every vector named above, V95 to V103 included, is specified only. No oracle exists. No code was written for the reference model. No broker was contacted. The only machine operations in this pass were text edits to the candidate, with exactly-once replacement assertions, a byte comparison showing Rev 3.1 is unchanged, and SHA-256 hashing of the files.

Candidate draft 2 replaces draft 1 as the operative candidate text. Draft 1 remains historical; its hash is recorded above. Readiness verdict unchanged: **NO-GO** for freeze, implementation and any trading stage.
