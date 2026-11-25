# EAR v0.1 Rev 3.2 Candidate: Response to "Draft 3: Targeted Clarifications" (A–E)

- **Author:** Claude (Specification Lead / ARBITER)
- **Date:** 2026-11-24
- **Responds to:** "EAR Rev 3.2 Draft 3: Targeted Clarifications", a specification proposal relayed by the founder. The document does not name its author, and authorship is not assumed here.
- **Reviewed object:** candidate draft 3, SHA-256 `f647c36bfd4e632052bdcca13eb0b92f64a2964445d0f3021c5ee47f5fdc47ab`
- **Produces:** candidate draft 4 (SHA-256 in the push manifest)
- **Baseline:** Rev 3.1 FROZEN, `dd9d87f76b01134e084827b0202c73c52fccb2b86f21a176a6b6e551241fa239`. **Not modified.** The byte comparison is identical.

**Boundary.** Specification correction only.
- No implementation, oracle construction or execution, broker contact, paper or live trading, or freeze.
- OQ-H15 to OQ-H19 remain open. FD-20 remains unresolved.
- One new open question, OQ-R1, is **added**, and none is closed.
- Labels are unchanged; nothing is promoted.

---

## 1. Disposition

| Item | Disposition | Amendment | Why |
|---|---|---|---|
| **A** Structural-state traceability | **ADOPTED, AMENDED** | (1) Evidence closes a condition only through a resolution rule that **names** the condition type and the evidence class, for example HISTORY FILL for PENDING. (2) The required map is now **built**, not just promised: the A-map in §8 | Unamended, "receipt of additional evidence alone does not close it" makes routine PENDING permanent (CX-65). Building the map exposed conditions with **no** resolution operation (C-18, OQ-R1) |
| **B** Reactivation | **ADOPTED, AMENDED** | (1) The "separately authorized replacement basis" path is **not adopted**. (2) Every basis in the reservation's chain must be INTACT. (3) The TTL is fixed at commit. (4) Suspension causes are recorded, and all must clear. (5) The reactivation record carries its own basis | An undefined authority would be an authorization path (CX-66). Resetting the TTL would let suspend/reactivate cycles defeat expiry |
| **C** Consume | **ADOPTED, AMENDED** | (1) No revision-equality binding; Π is re-evaluated on the current revision inside the lock. (2) Submission identity = hash of the canonical payload. (3) A different submission identity → refused plus an **integrity alert**, not an SR condition. (4) A time-only freshness failure at consume leaves the reservation ACTIVE | "Verifies the relevant revision" either always fails or opens a time-of-check / time-of-use gap (CX-68). A structural classification would let a faulty caller lock the account (C-18, C-20) |
| **D** Typed identity encoding | **ADOPTED** | The alternative outcome "or unresolved" is dropped: an undeclared representation difference leaves identities **distinct** (then FORK → CONFLICT) | "Unresolved" had no defined handling, while "distinct" already reaches SR |
| **E** Status envelope | **ADOPTED, AMENDED** | (1) The reason-code set is explicit, with NONE for a clean ledger. (2) A missing or invalid set is a **per-call evaluation fault (DENY)**, not a persistent structural condition. (3) The adapter clause is an adapter acceptance requirement (G-07 / R-16, UNVERIFIED) | Combined with A, "itself a structural failure" turns a transient fault into a lockout until re-bootstrap (CX-67) |

**Rejected outright:** none.

**Not adopted:** one clause, B.5's replacement-basis path.

**Settles:** the draft-3 design call. Seven statuses plus a mandatory reason-code envelope; no eighth status. Gemini has not reviewed this point.

---

## 2. Exact text as integrated (verbatim from draft 4)

### 2.1 A: traceability, the A-map, closure (§8)

**Structural-state traceability (proposal A, adopted with amendments) [OPERATIVE].**
- **Visibility.** Every structural condition that can affect execution identity, transition ordering, quantity, attribution, bootstrap disposition or authorization has either an L3 disposition or an explicitly defined derived state (SR clause 6) that SR reads directly. No ingestion, reconciliation, bootstrap, migration or lifecycle path may create an unresolved structural condition that SR cannot see.
- **Mapping obligation.** The A-map below records, for each condition: its origin, the L1 reference, the L2 target, the L3 disposition, the SR clause that reads it, and its resolution operation.
- **Closure.** A condition stays open until its specified resolution operation is applied and recorded in L3. The resolution names the condition it resolves and the evidence or authorized operation it relies on. The original condition and its resolution remain permanently auditable.
- *Amendment to A (evidence-driven resolution):* the proposal's sentence "Receipt of additional evidence alone does not close it" is **narrowed**. Evidence closes a condition **only** through a resolution rule that names that condition type and the evidence class that resolves it. An example is HISTORY FILL on the arrival of the named predecessor, which closes PENDING. That rule's application is the resolution operation. Evidence that is merely consistent with resolution never closes anything. Without this amendment, every PENDING would be permanent, which contradicts §3.4.
- **No defined resolution.** A condition with no defined resolution operation remains open until an explicitly authorized re-bootstrap (FD-18) or another governance operation closes the affected ledger scope. **No condition expires by timeout** (consistent with Rev 3.1 line 547).
- **SR completeness obligation.** In every reachable state, if any structural condition is unresolved, SR is false. If the model cannot establish whether a condition is resolved, SR is false.
- The map's completeness is **DERIVED, not verified**. Three rows depend on Rev 3.1 rules that this candidate does not restate.

**A-map (structural conditions → SR):**

| Condition | Origin | L1 ref | L2 target | L3 disposition | SR | Resolution operation |
|---|---|---|---|---|---|---|
| SEQ_CONTRACT | sequence ingestion (R-03″ rows 1, 6 and 7; undeclared epoch) | the item | — | SEQ_CONTRACT | 1 | **none defined** → FD-18 / governance (C-18) |
| CONFLICT, same broker_seq with different content | ingestion (R-03″ row 3) | both items | — | CONFLICT | 1 | sequence-resolution item (R1 R-08) naming broker_seq |
| FORK, STALE, KEY_MISMATCH, ORDER_CONTRADICTION, NUMBERING_INCONSISTENT | dedup protocol (§3.4, §3.2) | both claims | the L2 entries of x | CONFLICT (subtype) | 1 | **none defined** (AM-10: "neither claim preferred") → governance (C-18) |
| MANIFEST_CLAIM_FALSIFIED | bootstrap (AM-16′) | the falsifying item and the manifest | the manifest claim | CONFLICT | 1 | the revocation M1 → M1q plus the basis recheck (defined) |
| Overfill (q > R) | E05 | the fill | the order and the L2 entry | CONFLICT | 1 | per Rev 3.1 E05 / D27 (not restated here) |
| Snapshot conflict (equal W, different content) | snapshot ingestion | both snapshots | — | Consistency INCONSISTENT | 1 (status row 1) | broker resolution (Rev 3.1 §2.6.2) |
| PENDING | dedup (§3.4) | the transition | the L2 entry | PENDING | 2 | HISTORY FILL / APPLY on arrival of the named predecessor (defined, evidence-driven) |
| D26 / D27 hold | correction ingestion | the correction | the L2 entry | hold | 2 | per Rev 3.1 D26 / D27 (not restated here) |
| Unknown quantity (T2-U, qty absent) | ingestion | the item | the L2 entry or order | UNRESOLVED | 3 | an authoritative broker response giving the quantity (Rev 3.1 line 547) |
| Unresolved pre-bootstrap item | bootstrap (R7 §10) | the item | the L2 entry or anchor | UNRESOLVED / CONFLICT / held | 4 | exec_id-level broker dismissal; anchor arrival (R7 §5); otherwise governance |
| Structural evidence failure (Rev 3.1 §2.8, V54) | evidence acceptance | the item | — | Consistency failure | 5 | per Rev 3.1 §2.8 (not restated here) |
| CHANNEL_SUSPECT | attribution (AM-17) | the item | — | CHANNEL_SUSPECT | 5, only under FD-20(a) | **FD-20 (unresolved)** |
| Unknown order (E20) | ingestion | the item | the order | UNKNOWN order | 3 if its remaining quantity is unknown; otherwise counted in B and S | authoritative broker response |
| Empty or UNRESOLVED ExecutionState(x, β) | derived from L2 and L3 | — | x | none: a derived state | 6 | resolves when its underlying conditions resolve |
| *Not structural:* R_PROPOSAL_CONFLICT, CONSUME_IDENTITY_CONFLICT | caller requests | the request | — | integrity alert | — | none needed; no ledger effect |
| *Not structural:* an evaluation fault or a missing reason-code set (proposal E) | evaluation | — | — | evaluation fault (per call) | — | per call: that evaluation is DENY |

- **Finding from building the map (C-18):** at least two families have **no defined resolution** (SEQ_CONTRACT, and the dedup CONFLICT subtypes). Under A, any one of them blocks the whole account (global SR) until founder-authorized governance. That is the intended fail-closed behaviour, but its availability cost is now explicit. **OQ-R1** (new) asks for a resolution operation per condition.

### 2.2 B: reactivation (§7.2)

- **Suspension causes.** A SUSPENDED reservation records the set of causes that suspended it: Π_FAIL (R-15″) and BASIS_INCOMPLETE (§7.4). Further causes are added as they arise. Reactivation requires every recorded cause to have cleared.
- **Reactivation (proposal B, adopted with amendments) [OPERATIVE].** Reactivation SUSPENDED → ACTIVE is a **new authorization event**, not a restoration of the original one. It is permitted only if all of the following hold, checked in one serialized fold:
  1. the reservation is SUSPENDED and its commitment is counted exactly once (§7.2 mapping);
  2. it has not expired, been released or been invalidated. *TTL is not reset:* expires_at is fixed at commit;
  3. SR holds and BOUNDED holds (status row 8 or 9);
  4. Consistency CORROBORATED, Freshness FRESH, and the other evidence requirements of Π;
  5. **every** basis recorded for the reservation (the commit basis and any earlier reactivation bases) is INTACT. *Amendment to B:* the proposal's alternative "or a separately authorized replacement basis" is **not adopted**. It would create an authorization path with no defined authority, procedure or basis semantics. A reservation whose basis cannot be restored to INTACT stays SUSPENDED until it expires or is released; a fresh proposal and commit is the replacement path;
  6. Π(r, σ) holds on the actual current state σ, with the existing commitment counted exactly once (§7.3).
- **If all hold,** the fold appends an **L1 reactivation record** carrying its own basis: p_b = (that record's position) − 1, the model version, the configuration hash and H_c, exactly as for a commit (§7.1 and §7.4). It also writes the L3 disposition SUSPENDED → ACTIVE, with that record as its cause.
- **If any fails,** the reservation stays SUSPENDED and no permission is created.
- A BASIS_IMPUGNED or INVALIDATED reservation is never reactivated.
- **Later impugnment** of any basis in the chain → INVALIDATED (if the reservation is ACTIVE or SUSPENDED), under the §7.4 table. This is conservative and can over-deny, because an impugned *original* basis invalidates even when a later reactivation basis is intact (DERIVED choice; C-19).
- **OVER_LIMIT** ⇔ U > L (added to I3 and I8).

### 2.3 C: consume (§7.1)

- **Consume linearization (proposal C, adopted with amendments) [OPERATIVE].** REPLACES "`consume` follows the same pattern".
  - **Lock:** consume runs under the same serialized store lock as event application, commit, expiry, release, invalidation and reactivation (fold discipline, §3.1).
  - **Preconditions**, checked inside the lock:
    - the reservation is ACTIVE and unexpired at t_L;
    - its configuration hash equals the current configuration (otherwise AM-14′ governs), and its model version lies in the current lineage;
    - the payload equals the committed proposal payload byte for byte (Rev 3.1 payload binding);
    - Π(r, σ) holds on the actual current state σ, which already counts r exactly once (§7.3).
  - *Amendment to C (revision binding):* there is **no** revision-equality check against the commit revision. That check would always fail after any intervening event. Π is re-evaluated on the current revision instead.
  - **Any precondition fails:** no lifecycle change and no submission permission. An L1 consume-refusal record is appended with its reason codes. If Π failed only on time-based freshness, the reservation stays ACTIVE; it is not suspended at consume.
  - **All pass:** one fold appends the L1 consume record and changes the reservation ACTIVE → CONSUMED and the order AUTHORIZED → SUBMITTED together (§7.2). No intermediate revision exists.
  - **Submission identity** = SHA-256 of the canonical order payload (plus the broker client-order id once G-07 defines one).
    - A duplicate consume with the same reservation and the same submission identity is idempotent: it returns the existing CONSUMED result.
    - A different submission identity for an already-consumed reservation is **refused**, with an L3 integrity alert CONSUME_IDENTITY_CONFLICT.
  - *Amendment to C (conflict classification):* that alert is **not** an SR condition. The refusal prevents any ledger effect, so it carries no exposure uncertainty, and making it structural would let a faulty caller lock the account (C-14, C-18). If a second order nevertheless reaches the broker, it is detected as an unknown order (Rev 3.1 E20), and that path **is** structural.
  - **Scope:** this atomicity ends at the model's consume linearization point. It does **not** establish atomicity with adapter transmission or broker acceptance (G-07, R-16).

### 2.4 D: typed encoding (§3.2)

  - **Typed canonical encoding (proposal D, adopted) [OPERATIVE].** I is encoded under a **schema version** that fixes the field order, field type, nullability and byte representation. Each field is encoded as:
    - a field tag identifying its position and declared type;
    - a presence tag (present / explicit null / absent);
    - a 64-bit **unsigned** big-endian byte length;
    - the canonical value bytes.

    Length prefixes make concatenation unambiguous ("ab" + "c" ≠ "a" + "bc").
  - **Enumerated fields** (kind, side): a fixed, versioned enumeration-to-byte mapping. A value outside the declared enumeration is malformed.
  - **Out-of-type or out-of-range field:** malformed. Malformed means the identity is incomplete: corroboration only, never a bind (§3.2 above).
  - **Schema or parser change:** recorded in the derivation lineage. It creates a new lineage (I9-ext) and requires explicit migration treatment (§7.6).
  - **Path representation differences** (the same broker id arriving as JSON number 123 on one path and string "123" on another) may be reconciled only by a decoding that is **declared, version-pinned and injective over the entire allowed input domain of that field** (proposal D). Otherwise the identities remain **distinct**, and the dedup protocol then reports FORK → CONFLICT. *Amendment to D:* the proposal's alternative "or unresolved" is dropped. "Distinct" is the defined outcome, and it already yields a structural condition through FORK.

### 2.5 E: status envelope (§8)

- **Status envelope (proposal E, adopted with amendments) [OPERATIVE].** The seven Rev 3.1 status values are unchanged. This settles the draft-3 design call in favour of seven statuses plus the envelope; see the response document for the reviewer's position.
  - **Required fields:** every status result carries the status and a machine-readable reason-code set listing every applicable status condition and every failed SR clause.
  - *Amendment to E:* the set is **explicit, never omitted**. A clean ledger carries the single code NONE, so an absent field can be told apart from "no conditions".
  - UNKNOWN with STRUCTURAL_UNRESOLVED is distinct from UNKNOWN caused by an absent, stale, conflicting or epoch-less snapshot. Consumers must not infer permission from the top-level status alone.
  - **Denial:** authorization is denied whenever BOUNDED is false, SR is false, or any other Π predicate fails.
  - *Amendment to E (fault classification):* failure to produce or validate the reason-code set is an **evaluation fault**. That evaluation and any commit, consume or reactivation relying on it are DENY. It is **not** a persistent structural condition. Under A, a persistent structural condition with no resolution operation would lock the account until re-bootstrap, so a transient serialization fault would become a lockout (C-18).
  - **Adapter side:** "no downstream adapter or consumer may discard the reason-code set or substitute a status-only permission rule" is an **adapter acceptance requirement** (G-07, R-16). It is UNVERIFIED and outside the model's control.

---

## 3. Counterexamples

| **CX-65** | draft-3 clarifications | proposal A unamended: a list delivers v2 before the stream delivers v1, giving routine PENDING. "Evidence alone does not close it", so the later arrival of v1 cannot close PENDING without an unnamed operation, and the account locks permanently on ordinary out-of-order arrival. Availability defect. Amended |
| **CX-66** | draft-3 clarifications | proposal B clause 5: with "a separately authorized replacement basis" and no definition of who authorizes it, any process that asserts a replacement could reactivate a reservation whose basis was impugned, and reach consume. A potential **false-permission path** through undefined authority. Not adopted |
| **CX-67** | draft-3 clarifications | proposal E unamended: a transient reason-code serialization fault is "a structural failure". Under proposal A it has no resolution operation, so the account is locked until founder re-bootstrap. Availability and governance defect. Amended (per-call evaluation fault) |
| **CX-68** | draft-3 clarifications | proposal C "verifies the relevant revision". (a) Read as equality with the commit revision, any applied event between commit and consume makes every consume fail (liveness). (b) Read as the revision of an evaluation performed outside the lock, consume acts on a stale evaluation, a time-of-check / time-of-use gap and a **false-permission** risk. Amended (Π on the current revision, inside the lock) |

---

## 4. Register updates

**New conflicts:**

| C-18 | Under proposal A, structural conditions without a resolution operation persist until governance. With a global SR, one such condition locks the account. This sharpens C-8 and C-14 | §8 A-map | OQ-R1; FD-18; FD-20 |
| C-19 | An impugned original basis invalidates a reservation even when a later reactivation basis is intact. Conservative, possible over-denial | §7.2 reactivation | review; it could be relaxed only with an argument about the unexposed interval |
| C-20 | Integrity alerts (R_PROPOSAL_CONFLICT, CONSUME_IDENTITY_CONFLICT) are excluded from SR. This is safe only if every effect on the broker side is caught as an unknown order (E20). That detection depends on A-12″ and adapter behaviour (G-07) | §7.1, §8 | G-07; adapter acceptance R-16 |

**New open question (added; nothing closed):**

| **OQ-R1** (new, draft 4) | Define a resolution operation for every structural condition in the §8 A-map that lacks one (SEQ_CONTRACT; the FORK, STALE, KEY_MISMATCH, ORDER_CONTRADICTION and NUMBERING_INCONSISTENT subtypes), or confirm that governance closure (FD-18) is intended for each. Restate the three rows that defer to Rev 3.1 (overfill, D26/D27, §2.8 failures) | §8 A-map | none | OPEN |

**Superseded wording:**

| Draft 3 §7.1 "`consume` follows the same pattern" | consume linearization (proposal C, amended) | unspecified preconditions and idempotency | draft-3 clarifications |
| Draft 3 §3.2 untyped tag-length encoding | typed canonical encoding with schema version (proposal D) | no field types, enumerations or schema lineage | draft-3 clarifications |
| Draft 3 SR clause 1 "proposal … conflicts" | caller conflicts reclassified as integrity alerts | a caller error could lock the account | draft-3 clarifications |
| Draft 3 response §1 "design call" (UNKNOWN vs an eighth status) | status envelope (proposal E): seven statuses plus a mandatory reason-code set | settled by adopting E | draft-3 clarifications |
| Proposal A sentence "Receipt of additional evidence alone does not close it" (unamended) | evidence closes only through a named resolution rule | would make PENDING permanent (CX-65) | draft-3 clarifications |
| Proposal B clause 5 "or a separately authorized replacement basis" | not adopted; a new proposal and commit is the replacement path | undefined authority (CX-66) | draft-3 clarifications |
| Proposal C "verifies the relevant revision" | no revision binding; Π re-evaluated on the current revision | always fails, or TOCTOU (CX-68) | draft-3 clarifications |
| Proposal C "recorded as a conflict"; proposal E "itself a structural failure" | integrity alert; per-call evaluation fault | lockout with no resolution (CX-67) | draft-3 clarifications |

**Ledger rows:**

| A: structural-state traceability, A-map, closure rule, SR completeness obligation (amended: evidence-driven resolution named) | draft-3 clarifications | §2.6.2 | DERIVED; map completeness not verified | OPERATIVE |
| B: reactivation as a new authorization; suspension causes; TTL fixed; reactivation basis (amended: no replacement-basis path) | draft-3 clarifications | §2.9 | DERIVED | OPERATIVE |
| C: consume linearization; submission identity; idempotency (amended: no revision binding; an alert, not structural) | draft-3 clarifications | §2.9 | DERIVED | OPERATIVE |
| D: typed canonical encoding; enumerations; schema lineage | draft-3 clarifications | §2.2.B | DERIVED | OPERATIVE |
| E: status envelope; explicit NONE; evaluation faults are per call (amended) | draft-3 clarifications | §2.6.2 | DERIVED; adapter side UNVERIFIED | OPERATIVE |

---

## 5. Unexecuted tests

| Draft-4 vectors | V114 every A-map row → SR false while open; resolution recorded in L3 → SR true; no timeout closes a row; V115 PENDING closes only through HISTORY FILL (CX-65); V116 reactivation with an impugned original basis → stays SUSPENDED → INVALIDATED; V117 reactivation with an expired TTL → refused; V118 consume with an intervening event → Π re-evaluated, no revision-equality failure (CX-68); V119 a duplicate consume with the same submission identity → idempotent; a different one → refused, alert, SR unchanged; V120 enumerated value out of range → malformed, no bind; V121 a reason-code serializer fault → that call DENY, no persistent condition (CX-67); V122 a clean ledger carries NONE | draft-3 clarifications | specified; **not executed** |

Every vector in candidate §13.3, V63 to V122, remains **unexecuted**. No oracle exists.

---

## 6. Claims by label (this pass)

- **DERIVED:**
  - A-map coverage (not verified complete; three rows defer to Rev 3.1 text that is not restated here);
  - the reactivation preconditions and counting exactly once;
  - the consume atomicity and idempotency;
  - the encoding's injectivity;
  - the envelope's denial rule;
  - CX-65 to CX-68.
- **COMPUTED:** none.
- **ASSUMED:** SHA-256 collision resistance; A-12″ (C-20).
- **CONDITIONAL:**
  - FD-18 (governance closure);
  - FD-20 (CHANNEL_SUSPECT);
  - FD-13 (release).
- **UNVERIFIED:** adapter compliance with the envelope and the consume scope (G-07, R-16).
- **OPEN:**
  - OQ-H15 to OQ-H19 and OQ-R1;
  - FD-20 (founder decision, unresolved).

---

## 7. Confirmation

**No implementation, oracle construction or execution, broker contact, paper trading, live trading, or freeze occurred.** No acceptance test or vector was executed. The only machine operations were text edits with exactly-once assertions, a byte comparison of Rev 3.1, and SHA-256 hashing.

Readiness: **NO-GO.** The most material finding of this pass came from *building* the map that A requires. Several structural conditions have no resolution operation at all. Fail-closed is therefore also fail-permanent for them until the founder acts (C-18, OQ-R1).
