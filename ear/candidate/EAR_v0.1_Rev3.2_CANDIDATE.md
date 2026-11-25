# Sentinel Exposure Accounting Reference Model v0.1: Revision 3.2 CANDIDATE (consolidated)

**SPECIFICATION ONLY / NOT IMPLEMENTED / NOT VERIFIED / NOT FROZEN**

Date: 2026-11-24 (ET). Consolidated by Claude (Specification Lead) on founder authorization of 2026-11-24 (specification consolidation only).

**Candidate draft 4.** Integrates the "Draft 3: Targeted Clarifications" proposal (items A–E; founder-relayed; the document does not name its author) with the amendments set out in `ear/review/EAR_Rev3.2_Draft3_Clarifications_Response_Claude_2026-11-24.md`. Draft 3 (SHA-256 f647c36bfd4e632052bdcca13eb0b92f64a2964445d0f3021c5ee47f5fdc47ab) applied P0-1 to P0-3, P1-1 and Additional 1 and 2 (`ear/review/EAR_Rev3.2_Draft2_Response_Claude_2026-11-24.md`). Draft 2 (61ded4a1…) applied INT-01 to INT-05 and IC-1 to IC-6. Drafts 1 to 3 are superseded and remain in git history.

**Boundary.** This document authorizes nothing. It is not a freeze. It does not authorize implementation, construction or execution of an oracle, broker contact, paper trading or live trading.

---

## 0. Baseline, method and how to read this document

### 0.1 Frozen baseline (unchanged, not replaced)

| Item | Value |
|---|---|
| Artifact | `ear/spec/EAR_v0.1_Rev3.1_FROZEN.md`, repository skyhacker156/Sentinel_EAR |
| SHA-256 (supplied by the founder; matched by this author with `sha256sum` on fresh clones) | `dd9d87f76b01134e084827b0202c73c52fccb2b86f21a176a6b6e551241fa239` |
| Commits | `767f236` (Rev 3), `d4c9e66` (Rev 3.1 added) |
| Status | **FROZEN. NO-GO for implementation.** This candidate does not modify it |

### 0.2 Method: an integrated amendment text keyed to Rev 3.1 sections

This candidate is **Rev 3.1 plus the amendments below**:
- **Every Rev 3.1 section, rule, vector and register entry that is not amended here stays operative exactly as frozen.** It is incorporated by reference, not retyped. That prevents any accidental change to the frozen wording.
- Where an amendment says **REPLACES**, the cited Rev 3.1 wording is **SUPERSEDED** for the candidate. It stays in the frozen file as history.
- Where an amendment says **ADDS**, the text is new.
- Section numbers are Rev 3.1's. New subsections take the next free number (for example §2.2.A, §2.4.3).

A full merged text, Rev 3.1 with every change applied in line, can be generated from this document. It would be a second artifact, and it would itself need a byte-level diff check against Rev 3.1.

### 0.3 Source documents (all in `ear/review/`)

| Ref | File | SHA-256 |
|---|---|---|
| R1 | EAR_Rev3.1_Review_Claude_2026-11-24.md | 39c224a375c0afd3dc02500f151b1ddfe3fbc1b0bd7373452b32dafbadc3c199 |
| R2 | EAR_Rev3.1_CounterReview_Response_Claude_2026-11-24.md | e53d96ef605a80f69630f4ecbd92720241e534fc3b0911147eb6eb53d523505d |
| R3 | EAR_Rev3.1_FourChallenge_Response_Claude_2026-11-24.md | 1aef01e9dd2cad179824085792c5598786055f5593f0ece1fbf1e7fd20937992 |
| R4 | EAR_Rev3.2_Candidate_Clarifications_Claude_2026-11-25.md | d5967e5575b3e8a8189c47500892430b50329ba81d037d87c17e049291acab69 |

**Note (IC-6):** R4's filename carries the date of the dispatch it answered (2026-11-25). The document was prepared on 2026-11-24 (ET). The filename is kept unchanged because the file is hash-pinned; renaming it would break the record.
| R5 | EAR_Rev3.2_Closure_EFG_Claude_2026-11-24.md | 6faf10f293fe3b580b8bd11d84bafd50051150461b2efd99e9744af56cee3e6e |
| R6 | EAR_Rev3.2_ChallengeH_Claude_2026-11-24.md | 3148d4fa53e9d2d9f0ecab0cbc1da9029a94c535ffee56d92b4c96fb331e77e5 |
| R7 | EAR_Rev3.2_Residuals_EFG_Claude_2026-11-24.md | 7b376d68626da89257269d3fc5809f8ae16dc06e0a2f4e0e9e9b58cf7e734371 |
| R8 | EAR_Rev3.2_H1-H7_Claude_2026-11-24.md | f94685a69ab6471534412aa3019d15dfb63a6f377ba804a79294c5cb49b46770 |
| R9 | EAR_Rev3.2_H8-H14_Claude_2026-11-24.md | 57ccbb5f2496a7613d3fd762fd35319d5db73ef0ff6f92a79de58fc1c814c852 |

R1 is the review of Rev 3.1. Its findings and proposed revisions R-01 to R-14 were revised in R2 to R9. The operative forms are below; the superseded forms are in §11.

### 0.4 Labels and markers

**Evidence labels** are preserved exactly as their sources assigned them. None is promoted.

| Label | Meaning |
|---|---|
| **DERIVED** | follows from the stated definitions and assumptions (a hand derivation by one author) |
| **COMPUTED** | integer arithmetic or a single-example brute-force enumeration, run by a throwaway script. It shows arithmetic only: not an oracle, not a test suite, not implementation evidence |
| **ASSUMED** | an adopted environmental or contractual premise |
| **CONDITIONAL** | valid only if the named preconditions hold |
| **UNVERIFIED** | not established by available evidence |
| **UNBOUNDED** | cannot currently be bounded from available evidence |

**Item markers.**

| Marker | Meaning |
|---|---|
| **[OPERATIVE]** | the candidate rule |
| **[OPERATIVE-PROVISIONAL]** | the candidate rule, with a known open defect recorded in §12 |
| **[CONDITIONAL-ON-FD-n]** | operative only if founder decision n is taken a stated way |
| **[SUPERSEDED → x]** | a historical proposal, kept for the record (§11) |
| **[OPEN]** | unresolved (§12) |

**Nothing in this document has been executed** beyond hashing, integer arithmetic and single-example enumerations. **No acceptance test in it has been run** (§13.3). Agreement among Claude, GPT and Gemini is not independent verification.

---

## 1. Executive status (candidate)

| Dimension | Status |
|---|---|
| Implementation readiness | **NO-GO** |
| Rev 3.2 freeze | **not authorized** |
| Accounting core (sum rule, D19 within W1–W7) | no in-model false permission found. **DERIVED**, not executed |
| Evidence identity and ordering | rules defined. **CONDITIONAL** on A-11″, A-11‴ and A-11⁗ (all UNVERIFIED) |
| Historical reconstruction / authorization basis | strong concept. **OPERATIVE-PROVISIONAL**: placement semantics open (OQ-H15); determinism contract open (OQ-H16) |
| Finality | gate architecture defined. Boundary and ordering semantics open (OQ-H18); basis open (FD-15) |
| Migration | serialization defined. Historical classification open (OQ-H19) |
| Authentication / denial of service | trade-off explicit. **FD-20 unresolved** |
| Event-delivery completeness (A-12″) | **the boundary of every safety claim. Not establishable inside the model** |
| Independent verification | **none** |
| Draft 2 integration corrections | INT-01 to INT-05 corrected or clarified; IC-1 to IC-6 applied. All **DERIVED**; none tested |
| Draft 4 integration | proposal A (traceability, A-map), B (reactivation), C (consume), D (typed encoding), E (status envelope), each adopted with amendments. New OQ-R1. All **DERIVED**; none tested |
| Draft 3 corrections | P0-1 SR gate, P0-2 post-proposal Π, P0-3 single commitment identity, P1-1 basis boundary, delta hull H_Δ (draft-2 hull soundness claim withdrawn), injective identifier encoding. All **DERIVED**; none tested |

---

## 2. Cross-cutting principles

**P-1. Widen-only** (Rev 3.1 §2.4, R31-07′). Operative as frozen, **with the conditional amendment P-1a**.
- **P-1a [CONDITIONAL-ON-FD-15(b)], source R6 §H6.** "A bound may also narrow by a PROVISIONAL → FINAL disposition under A-16, recorded in L3, citing the L1 tick and the parameter set (T_f, L_n, σ, C_f) pinned by the configuration hash. No other time-based narrowing is permitted."
- Under FD-15(a), P-1 stays strict.

**P-2. Receipt asymmetry (P-RA) [OPERATIVE]** (R8). *Scope (IC-3):* P-RA governs **attributed** evidence, meaning evidence that has passed the attribution rule of §9. Unattributed evidence is channel evidence. It is governed by AM-17 and CHANNEL_SUSPECT, whose effect is FD-20 (unresolved). Under FD-20(b), not acting on unattributed evidence is permitted only because A-17 is assumed; that is not an application of P-RA. Evidence that is received but not applied may widen, block, defer finality or impugn a basis. It may never narrow, grant, start or restart a finality clock, or advance an effective version. **DERIVED** as a corollary of P-1.

**P-3. Compare, never adopt [OPERATIVE]** (R3, R4).
- A snapshot after bootstrap is *compared* with the reconstruction, never adopted as a new baseline.
- The only adoption is bootstrap, or an explicit founder-authorized re-bootstrap (FD-18).
- A snapshot establishes aggregate position only (§2.2.F).

**P-4. Narrowing is governance [OPERATIVE]** (R8 AM-14, R9 AM-14′). Any configuration change that can narrow a bound (deactivating CA-15, shortening T_f or L_n, removing a correction class) requires a founder-authorization L1 record before it takes effect.

**P-5. Corroboration is not independence [OPERATIVE]** (R2 §5). A same-broker snapshot or manifest is *corroboration*. Independent evidence (D24) does not exist in v0.1 and is never claimed.

---

## 3. Amendments to §2.2: state definitions

### 3.1 §2.2.A Evidence layers [OPERATIVE] (R6 §H2; status moved per R6)

| Layer | Content | Mutable? |
|---|---|---|
| L1 Raw evidence log | every received item, byte-exact, plus Sentinel records: ticks (TTL, FINAL trigger, staleness) and **operation records (P1-1): commit, consume, release, expiry, invalidation, migration (L_a)**, each carrying its own inputs; raw_hash, received_at, log position, hash chain | never |
| L2 Canonical version history | one entry per (exec_id, transition) claim derived from L1, with l1_ref. **No status field** | never; a differing claim is a new entry |
| L3 Disposition log | (disp_id, target, from → to, cause = L1 ref or rule, revision, t). *P1-1:* this is the only L3 schema. There is **no separate L3 "basis record"**: the authorization basis lives in the L1 commit record (§7.4), and the reservation's creation is an ordinary L3 disposition ∅ → ACTIVE whose cause is that record | never; status = the fold |
| L4 Derived state | registry, net_cum, R, B, S, F_d, F_d(β), position status, reservations, flags | recomputed cache |

**Fold discipline (P1-1) [OPERATIVE].** Appending an item to L1 and folding it into L2, L3 and L4 happen in **one** serialized step of the store, under the same lock as commit (§7.1). Each revision ρ therefore has an L1 frontier f(ρ), the position of the last item folded, and every L1 item at or below f(ρ) is folded. No item is ever appended without also being folded. **DERIVED.** It adds a liveness coupling (C-17).

**I9-ext [OPERATIVE-PROVISIONAL; CONDITIONAL on the determinism contract, OQ-H16]:** L2, L3 and L4 are pure functions of (L1, model version, configuration, **and the determinism environment of OQ-H16**). Stored layers must be byte-identical to re-derivation. A model-version change creates a new derivation lineage; old lineages are kept. **DERIVED.** The determinism *environment* is open (OQ-H16).

### 3.2 §2.2.B Identities [OPERATIVE, CONDITIONAL on A-11″, A-11‴, A-11⁗]

Sources: R4 CA-1 (identity), R7 §2 (τ), R8 AM-11 and R9 AM-11′ (ν).
- **Message identity:** event_id. **Accounting identity:** exec_id, broker-unique per account, across orders, epochs and delivery paths (A-11″).
- **Transition identity τ:**
  - τ_B: a broker-supplied transition id, stable across paths (A-11‴); or
  - τ_D (INT-03, REPLACES draft 1): SHA-256 of the canonical **identity field set** I = (account, instrument, exec_id, kind, side, order_id, **broker** prior_version, prior_qty, qty). It **excludes ordering and transport metadata**: κ, the epoch, event_id, received_at, headers, list or message envelopes, the broker's resulting version number. Those are *attributes* of a delivery, not of the transition. **Sentinel's internal version index never enters τ.**
  - **Attribute reconciliation** for one τ seen on two paths:
    - κ present on both and equal → consistent;
    - κ present on both and different → **CONFLICT (KEY_MISMATCH)**;
    - κ present on one path only → the key is **attached** to the transition by an L3 record. This is an applied disposition from attributed evidence, not a narrowing by unapplied data (P-RA);
    - the same comparison applies to the broker resulting version.
  - **Incomplete identity fields** on a path (any field of I missing): no τ_D can be formed. The delivery may *corroborate a value* (an L3 note) but never binds or deduplicates. If no path supplies a complete I and there is no τ_B, the transition is out of contract.
  - **Broker guarantee required (A-11‴, extended):** every path that reports a transition supplies every field of I, with identical values.
  - Neither available → the transition is out of contract (UNRESOLVED).
- **Version identity ν** = (exec_id, broker version, canonical payload). It binds only with the **full** field set, and only if A-11⁗ is declared for that path. Binds must be order-preserving and one-to-one per exec_id; otherwise **CONFLICT (NUMBERING_INCONSISTENT)**.
- **Canonicalization (Additional 2, REPLACES "ASCII-normalized identifiers") [OPERATIVE].**
  - **Typed canonical encoding (proposal D, adopted) [OPERATIVE].** I is encoded under a **schema version** that fixes the field order, field type, nullability and byte representation. Each field is encoded as:
    - a field tag identifying its position and declared type;
    - a presence tag (present / explicit null / absent);
    - a 64-bit **unsigned** big-endian byte length;
    - the canonical value bytes.

    Length prefixes make concatenation unambiguous ("ab" + "c" ≠ "a" + "bc").
  - **Enumerated fields** (kind, side): a fixed, versioned enumeration-to-byte mapping. A value outside the declared enumeration is malformed.
  - **Out-of-type or out-of-range field:** malformed. Malformed means the identity is incomplete: corroboration only, never a bind (§3.2 above).
  - **Schema or parser change:** recorded in the derivation lineage. It creates a new lineage (I9-ext) and requires explicit migration treatment (§7.6).
  - **Identifiers** (account, instrument, exec_id, order_id): the exact byte string the broker sent, after decoding only the transport encoding declared for that path (for example a JSON string → its UTF-8 bytes). **Prohibited:** case folding; trimming or collapsing whitespace; Unicode normalization (NFC, NFKC, …); stripping leading zeros; reinterpreting a string as a number or a number as a string; truncation; any lossy mapping.
  - **Path representation differences** (the same broker id arriving as JSON number 123 on one path and string "123" on another) may be reconciled only by a decoding that is **declared, version-pinned and injective over the entire allowed input domain of that field** (proposal D). Otherwise the identities remain **distinct**, and the dedup protocol then reports FORK → CONFLICT. *Amendment to D:* the proposal's alternative "or unresolved" is dropped. "Distinct" is the defined outcome, and it already yields a structural condition through FORK.
  - **Integers:** signed 64-bit, big-endian two's complement. A value outside that range is malformed.
  - **Why this direction:** splitting one broker identity into two is fail-safe. The second claim meets the same predecessor and is detected as FORK → CONFLICT, which costs availability. **Collapsing two broker identities into one is fail-unsafe:** a distinct transition is discarded as a duplicate, and F_d undercounts (CX-61). Every permitted transformation must therefore be injective over the broker's identifier space. **DERIVED.**
  - Hash: SHA-256 over the encoding. Collision resistance is **ASSUMED**.
  - Pinned by parser version within the lineage. The full determinism environment remains open in OQ-H16; this item fixes the identifier encoding only and does not close OQ-H16.

### 3.3 §2.2.C Version history and registry [OPERATIVE]

R5 §E-A fields; status moved to L3 (R6).
- **L2 entry fields:** account_id [S], exec_id [B], order_id [B], instrument and side [B], version index [S, validated against the broker claim], kind [B], broker prior_version and prior_qty [B], qty [B], signed_delta [D], κ or ⊥ [B], source (STREAM / LIST / BOOTSTRAP_MANIFEST / ANCHOR) [S], raw_hash, received_at, log position, revision [S]. Marked [B] broker claim, [S] Sentinel metadata, [D] derived.
- **Registry:** a derived cache of the effective current version per exec_id, used only for β = now.
- **[SUPERSEDED → this section]** R4 CA-1's sentence "F_d is computed only from the registry and the opening item".

### 3.4 §2.2.D Deduplication and transition protocol [OPERATIVE] (R7 §2, R8 AM-11, R9 AM-11′, R8 AM-10)

Applied on receipt of a transition t for execution x:
1. **τ lookup.** Same payload → duplicate (an L3 counter only). Different payload → **CONFLICT**.
2. **ν lookup** of t's resulting state. Same ν → **duplicate-by-state**: bind τ, with no quantity change. Same (exec_id, broker version), different payload → **CONFLICT**.
3. **Predecessor check** against the chain of broker versions:

| Predecessor relative to the chain | Result |
|---|---|
| equals the head | **APPLY** |
| ahead of the head | **PENDING** |
| fills a known gap in the chain | **HISTORY FILL** |
| already has a different successor | **FORK** → CONFLICT |
| older than the head, with no gap | **STALE** → CONFLICT |

4. **Keys contradicting the predecessor order** → **CONFLICT (ORDER_CONTRADICTION)** on both entries. x becomes UNRESOLVED; neither claim is preferred (AM-10).
5. **D27 refinements** (R5 E-C):
   - prior_version ahead → PENDING; behind → CONFLICT;
   - **BUST must also carry a broker predecessor version** (R7 §3);
   - reinstatement after a bust is permitted as a version transition, subject to E13's range checks.

### 3.5 §2.2.E Admissible histories and ExecutionState [OPERATIVE-PROVISIONAL] (R6 §H1, R7 §3)

- **Chain (INT-02, REPLACES draft 1):** x's versions are linked by their broker predecessor claims (prior_version names the exact predecessor), giving positions i = 0, 1, …, n. **i is the chain position, not the broker version number.** Broker version numbers are strictly increasing (A-11⁗) but **need not be contiguous**: a skipped number is not a gap. A *gap* exists only when a named predecessor has not been received (PENDING).
- **Order-coherence contract, A-11-ORD (ASSUMED, new; UNVERIFIED):** for one exec_id, if v_i precedes v_j in the chain and both are keyed, then κ(v_i) < κ(v_j). The broker emits an execution's transitions on the stream in version order.
  - A violation between two keyed versions is detected (ORDER_CONTRADICTION, AM-10).
  - Where one or both are ⊥, the contract is **assumed, not checked**.
- **Cut** k at β: positions 0..k lie at or before β. **Admissible** iff (a) k respects the chain, and (b) for every keyed version v_i, κ(v_i) ≤ β ⇔ i ≤ k. Under A-11-ORD, (b) yields k ∈ [i_lo, i_hi − 1].
- **Without A-11-ORD** (broker does not guarantee stream order matches version order): the chain-prefix model of a cut is **not sound**, because the snapshot may include a non-prefix subset of x's transitions (CX-62). The candidate uses the **delta hull H_Δ** below for x. *Placing keyed versions by their keys alone is not permitted.*
- **ExecutionState(x, β)** = {q_k : k admissible}, with q_{−1} = 0 and an IN_OPENING anchor contributing 0. It is **UNRESOLVED** if any PENDING, CONFLICT, FORK or ORDER_CONTRADICTION entry, or a version of unknown quantity, affects β.
- **F_d(β) = P_open + Σ_x ExecutionState(x, β)**, over the product of the per-execution sets:
  - d_max = F_b − P_open − Σ min;
  - d_min = F_b − P_open − Σ max.
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
- Provisional because the placement of *retro-relevant* evidence relative to an authorization basis is open (OQ-H15).

### 3.6 §2.2.F Reconciliation levels [OPERATIVE] (R7 §4)

| Evidence | Aggregate position | Execution identity | Lineage |
|---|---|---|---|
| accepted snapshot | yes (a broker claim at β; W1-T / W1-F) | no | no |
| complete per-order list, ids only | that order's total | that order | current version only |
| complete per-order list with per-version keys or τ | that order | that order | yes, through ω |
| M1 manifest | yes (arithmetic corroboration) | account-wide at β0 | anchors only; earlier history UNOBSERVED |
| stream with ids, keys and τ | what it delivered | what it delivered | what it delivered |
| incomplete list | no | the listed ids | the listed versions |

**[SUPERSEDED]** R5 case 8's "a snapshot with W ≥ the list watermark restores determinacy" (overstated; corrected in R6 §H3 and R7 §4).

### 3.7 §2.2.G Epochs, keys, opening item, reconstruction [OPERATIVE, CONDITIONAL on A-2″] (R3, R4 D, R5 E-B, R6 H1)

- **Global key** κ = (epoch, broker_seq), ordered lexicographically. Every event of epoch e precedes every event of e′ > e.
- **Opening item:** P_open = F_b of the bootstrap snapshot at β0 = (e0, W0). It is a baseline, not an execution.
- **Reconstruction:** F_d(β) as in §3.5. An event with κ ≤ β0 is never added.
- **Per-epoch holes:**
  - e0: H_e0 = the largest h ≥ W0 with every number in (W0, h] received;
  - e ≠ e0: H_e = the largest h ≥ s_e − 1 with every number in [s_e, h] received (s_e is the declared epoch start);
  - M_e = the highest received number in epoch e.

### 3.8 §2.2.H Bootstrap modes [OPERATIVE] (R5 §G, R7 §9, R8 AM-16, R9 AM-16′)

- **M0:** position only.
- **M1:** a manifest claiming **both** `identity_complete` and `quantity_complete`.
- **M1q:** quantity completeness only.
- **Identity-only:** falls back to M0 for Consistency.
- **M1 contract** (R7 §9; every capability UNVERIFIED):
  - producer identity; authentication per D23 (fixture in the reference model);
  - account and instrument scope; the exec fields; broker version or τ of the latest transition;
  - **as-of-β0** semantics; β0 equal to the bootstrap snapshot boundary; busted executions included;
  - arithmetic corroboration: Σ = P_open, or P_s + Σ = P_open;
  - any malformed, unauthenticated or contradictory entry, or a sum mismatch → rejected as M1 → M0.
- **Anchors** (R7 §5): L2 kind ANCHOR with κ_anchor = β0; the prefix before it is UNOBSERVED. A correction naming the anchor's version applies. A correction naming an earlier version: κ ≤ β0 → history fill, no effect; κ > β0 or ⊥ → CONFLICT. An anchor with no broker version or τ → corrections to it are held.
- **Identity-claim falsification** (R9 AM-16′): an unknown exec_id with κ ≤ β0 under a claimed identity-complete manifest → **CONFLICT (MANIFEST_CLAIM_FALSIFIED)**. The claim is revoked, M1 → M1q, and dependent bases are rechecked.

**[SUPERSEDED → AM-16′]** R8 H-7's acceptance test "M1 (both claims) plus X5 replay → CONFLICT" (CX-51).

### 3.9 §2.2.I Other definitions (operative)

- **proposal_hash** (Rev 3.1 R31-06B): unchanged.
- **net_cum_at(order, s)** [OPERATIVE] (R1 R-09): defined over execution **events** with their own broker_seq ≤ s, consistent with F_d(W) (C-04). **REPLACES** the Rev 3.1 §2.2 line-139 wording "using only executions with broker_seq <= s".
- **Snapshot schema** [OPERATIVE] (R1 R-11): ADDS master_version and content hash. E24's UNKNOWN clears only on an accepted snapshot of the new version.

---

## 4. Amendments to §2.3 limits and §2.11 assumptions

| ID | Text (candidate) | Class | Source | Status |
|---|---|---|---|---|
| **A-2″** (REPLACES A-2) | broker_seq is contiguous per (account, epoch), numbered at the source from the declared s_e; each sequenced message carries its epoch id; epochs are totally ordered; the coverage classes are named (R-08); a watermark (e, W) covers exactly the executions with κ ≤ (e, W), including every earlier epoch; **delivery is not assumed** | E, ASSUMED | R2 R-01′, R3 A-2″, R4 CA-2 | OPERATIVE; UNVERIFIED for any broker |
| **A-11″** (REPLACES A-11) | *(IC-2: two unsequenced classes are kept apart. Identified-but-unsequenced is §8 #10 / FD-3. Unidentified-and-unsequenced is the class below / FD-8.)* exec_id is broker-unique per account, stable across epochs and paths; event_id is message identity only; a delivery with neither exec_id nor broker_seq is out of contract ([CONDITIONAL-ON-FD-8]) | E | R4 CA-3 | OPERATIVE; UNVERIFIED |
| **A-11‴** | τ_B, or broker version claims, on every CORRECT and BUST | E | R7 §2 | OPERATIVE; UNVERIFIED |
| **A-11-ORD** (new, INT-02) | for one exec_id, chain order equals stream-key order wherever both versions are keyed; the broker emits an execution's transitions in version order | E | this draft | OPERATIVE; UNVERIFIED. Without it, the partial-order hull applies (§3.5) |
| **A-11⁗** | the broker version is a strictly increasing per-exec_id counter, with one numbering on every path; BUST and CORRECT advance it | E | R9 H-10 | OPERATIVE; UNVERIFIED. Version resets open (OQ-H17) |
| **A-12″** (REPLACES A-12) | every execution, **correction and bust** that occurred at the broker before evaluation time t, other than fills of known working orders (W4), has been received by t. Not established by freshness, contiguity, serialization or reconciliation. Its failure can invalidate both bounds in every status, including RECONCILED | E | R2 §2, R4 CA-4, R5 | **the boundary of every safety claim** |
| **A-14″** (extends A-14) | corrections stay within net_cum ∈ [0, Q_o] **and** never change side, instrument or order: the broker busts and re-reports instead | E | R6 H5 | [CONDITIONAL-ON-FD-19]; UNVERIFIED |
| **A-15** | account exclusivity: every execution results from an order known to the model | E | R4 CA-4 | [CONDITIONAL-ON-FD-11]; UNVERIFIED |
| **A-16** | finality: no correction or bust after FINAL; FINAL per §6.2 | E | R5, R6 H6, R7 F-3 | [CONDITIONAL-ON-FD-15]; parameters UNVERIFIED |
| **A-16b** | bootstrap clause: S0 is accepted only at least T_f + L_n + σ after the last pre-bootstrap execution | E | R6 H5(h) | [CONDITIONAL-ON-FD-16]; UNVERIFIED |
| **A-17** | authentication is sound and complete over the whole delivery path | E | R9 H-13 | **[CONDITIONAL-ON-FD-20(b)]; FD-20 UNRESOLVED** |

**Unchanged and operative by reference (Rev 3.1 §2.11):** A-1, A-3 to A-10 and A-13. A-5 is read with the consume rule of §7.1.

**§2.3 limits, ADDS** (R4 CA-4, R4 C): "Internal serialization orders Sentinel's decisions. It does not establish that external events before t_L were received by t_L. A correct reconstruction of *received* evidence is not a complete reconstruction of what *occurred*."

---

## 5. Amendments to §2.4: equations and the uncertainty inventory

**§2.4 decisions:** unchanged, except that Π (§7.3) now governs commit, consume and reactivation.

**§2.4.2 inventory ADDS these rows [OPERATIVE]:**

| Uncertainty | Home | Effect | Source |
|---|---|---|---|
| Buffered event above a hole | GAP | UNBOUNDED | R2 R-01′ |
| PENDING transition, order bound known | mandatory provisional range [0, q_x + (Q_o − N_o)] for x (upward term only if terminal) | widen; blocks increases | R8 AM-12 |
| PENDING transition, no order bound | T2-U | UNBOUNDED | R8 AM-12 |
| Unknown old execution (κ ≤ β0, unknown exec_id), M0 / M1q | held (structural) | both sides blocked | R5 G, R7 §10 |
| Version of unknown quantity in a chain window | UNRESOLVED | UNBOUNDED | R5 E-C case 8 |
| Content-identical id-less unsequenced deliveries | **out of contract** ([CONDITIONAL-ON-FD-8]) | structural, affected side | R3, R4 |
| Associated content-identical copy (if FD-8 is not adopted) | T2 of known side | widen own side | R2 R-07′; FD-6 moot under FD-8 |

**[SUPERSEDED]** R2's "multiplicity-uncertain item with exact-multiplicity exit" (R-07′ exit withdrawn in R3, CX: C1-a).

### 5.1 §2.4.3 Finality reserve CA-15′ [CONDITIONAL-ON-FD-14] (R5 CA-15, R7 §6, R8 AM-12, AM-14, AM-15; R9 AM-15′)

- All quantities are **effective current versions**.
- **Buy o:** F_min −= Σ PROVISIONAL effective qty; if o is terminal and has any PROVISIONAL execution, F_max += Q_o − N_o.
- **Sell o:** the mirror.
- **Working orders:** no upward term (W4).
- **A PENDING entry forces the reserve locally even if FD-14 is declined** (AM-12).
- **Rule F1:** no FINAL while any PENDING, CONFLICT, malformed or held entry exists for x or its order.
- **Activation** is a migration step (§7.6).
- Holds for quantity-only changes. **COMPUTED** (R7 F-2, six steps: the model bounds equal the brute-force extremes).
- **Does not hold** for a delayed identity change (CX-34, depends on A-14″) or for M0 opening busts (CX-35, depends on M1 or A-16b).

---

## 6. Finality

### 6.1 Status

PROVISIONAL or FINAL, per effective version. A FINAL can be revoked (FINAL_VIOLATED), which returns the execution to PROVISIONAL.

### 6.2 Gate [OPERATIVE-PROVISIONAL] (R9 AM-15′)

- **FINAL ⇔ W ∧ H ∧ ¬Blocker**, where:
  - W is t ≥ t_start + T_f + L_n + σ, with t_start = the APPLIED time of the current version;
  - H is: for every unhealthy interval [a, b] overlapping [t_start, t_start + T_f + σ], t ≥ b + L_n;
  - Blocker is any PENDING, CONFLICT, malformed or held entry for x, or an unresolved retro-relevant item affecting x.
- **The clock never pauses.**
- **Basis:** FD-15 (a) evidence, or (b) time; options table in §10.
- **Provisional** because exact-tick ordering and full outage boundaries are open (OQ-H18).
- **Interim determinism convention (IC-4) [OPEN under OQ-H18; not a resolution].**
  - Processing order is L1 log position (D20), so outcomes are deterministic *for a given log*. At equal timestamps, though, they depend on arrival order.
  - Conservative interim rule: a FINAL tick record for time t is appended only after the receive path has appended every item with received_at ≤ t. So evidence that is simultaneous with the tick is always processed **before** it: blocking or applied evidence takes precedence over finality.
  - Whether this is sufficient, including outage start and end at the tick and an applied correction at the tick, is exactly OQ-H18.
- **[SUPERSEDED → AM-15′]** R7 CA-15′ "PROVISIONAL from receipt of each version"; R8 AM-15 "freeze / resume from t_start".

### 6.3 After FINAL

A correction that arrives is applied (it is evidence). The result is FINAL_VIOLATED plus FINALITY_ASSUMPTION_FAILED: blocking under FD-17, or detection only.

---

## 7. Amendments to §2.9: reservations, commit and authorization basis

### 7.1 Commit and consume linearization [OPERATIVE] (R2 R-12′, R3 R-12″)

- t_eval = the as_of of the decision D (immutable).
- t_L = the clock read inside the critical section.
- E_L = evaluate at as_of t_L, inside the critical section.
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
- **Concurrent commits** serialize on the lock.
  - Another proposal's commit advances the revision, so the decision D no longer matches and must be re-evaluated. Its own reservation's R is then counted, as in V14 and V36.
  - A second commit of the same proposal_id hits step 3.
  - No reservation exists outside step 6. No two reservations can be created on one revision.
- Freshness is evaluated at t_L.
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
- **D_max** [CONDITIONAL-ON-FD-10]: (a) withdrawn as a safety rule; or (b) t_L − t_eval ≤ D_max, labelled an intent-age policy.
- **expires_at = min(t_L + TTL, snapshot.received_at + S_lim)** [CONDITIONAL-ON-FD-7, required per R4].
- **[SUPERSEDED]** R1 R-12's epsilon (R2); R2 R-12′'s ambiguous use of decision.as_of (R3).

### 7.2 Reservation lifecycle and accounting [OPERATIVE] (R4 R-15″)

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
- `release(reservation_id)` is allowed before consume [CONDITIONAL-ON-FD-13].
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
- **Invariant (unchanged in substance):** every unexpired reservation's commitment is counted in B or S, whether ACTIVE or SUSPENDED, and lifecycle changes of the reservation alone never change B or S.
- **[SUPERSEDED]** R2 R-15 (one-sided; A_raw-only reactivation); R3 R-15′'s "every other ACTIVE" wording; draft 2's "every unexpired reservation contributes its order's R", which was readable as a second summand (CX-59). FD-9 is moot.

### 7.3 Π [OPERATIVE] (R4 R-15″)

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

Π is evaluated in the same revision as every applied event, at commit, at consume and at reactivation. **DERIVED.**

### 7.4 Authorization basis AM-13′ [OPERATIVE-PROVISIONAL] (R9 H-8/H-9; defects open in OQ-H15 and OQ-H16)

- **Basis (P1-1, REPLACES "basis record"):** carried **inside the L1 commit record C** (§7.1 step 6a): p_b = f(ρ) = p_C − 1 (the last L1 item the decision saw), the model version, the configuration hash, and H_c (the per-epoch high-water H_e in the fold at p_b). There is no separate L3 basis schema. "Received after p_b" means L1 position > p_C, because none lies in between. Complete **CONDITIONAL** on the determinism contract (OQ-H16).
- **Retro-relevant evidence:** keyed ≤ H_c; or ⊥; or a disposition, conflict or bind on an entry effective at p_b; or a PENDING item whose missing segment could lie ≤ H_c; or FINAL_VIOLATED on an entry the basis treated as FINAL. Keyed > H_c is new history (I8, R-15″). **Relies on A-12″.**
- **Semantic test:** re-derive the as-of-commit state fold(L1[0..p_b]) ⊕ r, together with the retro-relevant items, and re-evaluate Π(r, ·) on that state (§7.3). The rule for placing those items is OQ-H15.
  - Current text: ALLOW → INTACT; UNRESOLVED → BASIS_INCOMPLETE; DENY → BASIS_IMPUGNED.
  - **Known defect (OQ-H15):** with ambiguous placement, a worst-case DENY means *some* placement denies, not all. The three-way placement rule is required.
- **Consequences:**

| State | BASIS_INCOMPLETE | BASIS_IMPUGNED |
|---|---|---|
| ACTIVE / SUSPENDED | SUSPENDED | INVALIDATED |
| CONSUMED | flagged; side blocked; G-07 review | flagged; side blocked; G-07 cancel candidate |
| Executed | flagged; on resolution, AUTHORIZATION_UNSAFE_RETROSPECTIVE if impugned | the same |

- **[SUPERSEDED → AM-13′]** R8 AM-13's basis_digest as the normative test (CX-48). The digest survives only as a superset-trigger index.

### 7.5 Lifecycle stages and reversibility [OPERATIVE] (R2 §8, R5 F6, R7 §8)

| Stage | Bust or correction arrives | Result |
|---|---|---|
| before evaluation | in the bounds | **prevented** |
| between evaluation and commit | revision moves; re-evaluation | **prevented** |
| between commit and consume | R-15″ suspension | **prevented** |
| after submission, acceptance or execution | **detection only**; the model cannot recall | prevented at authorization **only** under CA-15 for PROVISIONAL, quantity-only changes |

- Executed: irreversible.
- R-16 [OPERATIVE] (R2): an adapter acceptance test, "OVER_RESERVED between consume and transmit".

### 7.6 Configuration migration AM-14′ [OPERATIVE-PROVISIONAL] (R8 H-5, R9 H-14)

- **A single linearization point L_a.** In the same step: recompute; R-15″ on ACTIVE and SUSPENDED; recheck every consumed basis.
- A pre-L_a decision fails the configuration-hash check after L_a.
- A narrowing change needs a prior founder L1 record (P-4).
- **Flag:** BASIS_UNDER_SUPERSEDED_RULES. Currently "treated like BASIS_INCOMPLETE". **Known defect (OQ-H19):** that conflates historical validity with policy-migration exposure.
- Recommended placement: activate CA-15 at bootstrap.
- Adapter transmission after L_a: **UNVERIFIED**.

---

## 8. Amendments to §2.6, §2.6.2, §2.6.3: events, status and sequence

**§2.6.2 status [OPERATIVE] (P0-1, INT-01 and INT-05; REPLACES draft 2, draft 1 and the Rev 3.1 GAP rows at lines 418 and 499).** Rev 3.1's seven statuses are kept; no new status value is introduced.

Inputs:
- S = the latest accepted snapshot, with boundary (e_s, W) or no watermark;
- e* = the newest epoch with any received message;
- for every epoch e: H_e and M_e;
- the comparison cut β_c = (e_s, W) if S has a watermark; otherwise head (everything applied);
- the choice set X(β) = the product, over executions x, of the admissible-cut set at β (A-11-ORD mode) or of C(x, β) (H_Δ mode, §3.5).

**Structural-resolution predicate SR (P0-1) [OPERATIVE].** SR holds iff **none** of the following holds anywhere in the account's ledger:
1. any open L3 entry of kind SEQ_CONTRACT or CONFLICT, any subtype: FORK, STALE, KEY_MISMATCH, ORDER_CONTRADICTION, NUMBERING_INCONSISTENT, MANIFEST_CLAIM_FALSIFIED, overfill, snapshot conflicts. *(Draft 4: "proposal conflicts" removed. R_PROPOSAL_CONFLICT and CONSUME_IDENTITY_CONFLICT are caller refusals with no ledger effect: integrity alerts, not structural conditions. See §8 A-map.)*;
2. any PENDING transition, or any D26 / D27 hold;
3. any version, applied execution or order of unknown quantity (T2-U, or an L2 entry with qty absent);
4. any pre-bootstrap item whose R7 §10 per-mode disposition is UNRESOLVED, CONFLICT or held (including held anchor corrections and undismissed unknown-old executions);
5. any structural evidence failure in Rev 3.1 §2.8's sense (including snapshot quantity not a signed integer, V54), or CHANNEL_SUSPECT where FD-20(a) makes it structural;
6. for β ∈ {β_c, head}: ExecutionState(x, β) is UNRESOLVED or **empty** for some x, or X(β) is empty. *An empty set is never read as {0}, and never satisfies a universal condition vacuously.*

SR is global to the account: one unresolved item anywhere makes SR false (C-14). **DERIVED.**

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
- **Status envelope (proposal E, adopted with amendments) [OPERATIVE].** The seven Rev 3.1 status values are unchanged. This settles the draft-3 design call in favour of seven statuses plus the envelope; see the response document for the reviewer's position.
  - **Required fields:** every status result carries the status and a machine-readable reason-code set listing every applicable status condition and every failed SR clause.
  - *Amendment to E:* the set is **explicit, never omitted**. A clean ledger carries the single code NONE, so an absent field can be told apart from "no conditions".
  - UNKNOWN with STRUCTURAL_UNRESOLVED is distinct from UNKNOWN caused by an absent, stale, conflicting or epoch-less snapshot. Consumers must not infer permission from the top-level status alone.
  - **Denial:** authorization is denied whenever BOUNDED is false, SR is false, or any other Π predicate fails.
  - *Amendment to E (fault classification):* failure to produce or validate the reason-code set is an **evaluation fault**. That evaluation and any commit, consume or reactivation relying on it are DENY. It is **not** a persistent structural condition. Under A, a persistent structural condition with no resolution operation would lock the account until re-bootstrap, so a transient serialization fault would become a lockout (C-18).
  - **Adapter side:** "no downstream adapter or consumer may discard the reason-code set or substitute a status-only permission rule" is an **adapter acceptance requirement** (G-07, R-16). It is UNVERIFIED and outside the model's control.
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

A snapshot of a non-bootstrap epoch is compared, never adopted (P-3).

**Sequence transitions R-03″ [OPERATIVE]** (R2 §4, R3 Ch. 4). **REPLACES** the Rev 3.1 "stale" rule (lines 419 and 523).

| # | Incoming | Result |
|---|---|---|
| 1 | s ≤ W0 (e0) | **SEQ_CONTRACT** (not applied). Justified by reset detection, not double counting (R3 §0 correction of CX-28) |
| 2 | same number, same identity | idempotent |
| 3 | same number, conflicting | CONFLICT |
| 4 | fills a hole | applied; buffered events then applied in order |
| 5 | above H + 1 | buffered; GAP |
| 6 | same-epoch reset | SEQ_CONTRACT or CONFLICT |
| 6′ | **unlabelled renumbering at H + 1** | **undetectable** without A-2″ (C4-R) |
| 7 | lower-watermark snapshot | REPLAY (corroboration of the past) if the broker as_of is older; otherwise SEQ_CONTRACT [CONDITIONAL-ON-FD-2″] |
| 8 | new epoch | events applied; status UNKNOWN (EPOCH_UNBOOTSTRAPPED) until an e* snapshot is accepted; old holes keep GAP (row 3) and the band UNBOUNDED |
| 9 | new-epoch snapshot | compared (P-3) |
| 10 | unsequenced execution **with** an exec_id | interval; MISMATCH ([CONDITIONAL-ON-FD-3]). *IC-2:* this class (identified, no broker_seq) is distinct from the A-11″ out-of-contract class (**neither** exec_id **nor** broker_seq, FD-8). FD-3 decides whether this class too becomes out of contract |

- **SEQ_CONTRACT predicate:** s ≤ W0_e; a lower-watermark snapshot under FD-2″(a); or an undeclared epoch. A hole fill is never a failure.
- **Sequence-resolution evidence item [OPERATIVE]** (R1 R-08): (broker_seq, classification non-economic / foreign-instrument, authority, raw_hash). It is the only non-arrival way a hole clears.
- **Pre-bootstrap evidence classes** [OPERATIVE] (R5 §G, R7 §10): known replay; unknown old; correction to an opening execution; contradictory replay; known identity with incomplete history. Per-mode treatment as in R7 §10. **Dismissal of an unknown old execution requires an exec_id-level broker statement.** An omission from a complete list is a CONFLICT, not a dismissal.
- **Re-bootstrap** [CONDITIONAL-ON-FD-18] (R6 H4, R7 §4): an explicit founder-authorized operation. It closes the ledger, listing its unresolved items, and adopts a new P_open. Later corrections to pre-boundary executions are UNRESOLVED until an anchor arrives.

---

## 9. Amendments to §2.8: evidence and trust

- **Terminology [CONDITIONAL-ON-FD-1′]** (R2 R-02′). *IC-1:* draft 1 marked this OPERATIVE while FD-1′ was open. If FD-1′ is declined, Rev 3.1 §2.8 stands, and **CX-20 remains a blocking inconsistency** (the literal evidence model contradicts every ALLOW vector). accepted snapshot; corroboration; independent evidence.
  - Consistency results: CORROBORATED, UNCORROBORATED, INCONSISTENT.
  - D06 is restated as "UNCORROBORATED not tolerated for reductions".
  - NO_INDEPENDENT_EVIDENCE becomes a fixed limitation flag, not a failure state.
- **Reference-model evidence profile [CONDITIONAL-ON-FD-1′]** (R2): Integrity, Provenance and Authenticity are **SYNTHETIC_FIXTURE** values (FIXTURE_PASS or failure fixtures, never MATCH or VERIFIED). Consistency and Freshness are computed. Every Decision carries `evidence_profile`. A SYNTHETIC_FIXTURE run can never support claim level 5. Vectors gain an evidence_profile column; no vector outcome changes (DERIVED).
- **Attribution [OPERATIVE]** (R9 AM-17): only authenticated evidence creates L2 claims or execution-level holds. Unattributed evidence raises **CHANNEL_SUSPECT**. Its effect is **[OPEN: FD-20]**: (a) blocks both sides until an authoritative channel check; or (b) under A-17, ignored.
- **Authenticated but malformed:** a broker fault, held per item and scoped.
- Every hold names its releasing evidence. No timed release.
- **Structural flags ADDED:** SEQ_CONTRACT, ORDER_CONTRADICTION, FORK, NUMBERING_INCONSISTENT, MANIFEST_CLAIM_FALSIFIED, FINALITY_ASSUMPTION_FAILED, CHANNEL_SUSPECT, BASIS_INCOMPLETE, BASIS_IMPUGNED, BASIS_UNDER_SUPERSEDED_RULES.

---

## 10. Amendments to §3: decision register (founder decisions)

| FD | Question | Options | Status |
|---|---|---|---|
| FD-1′ | evidence terminology and profile (§9) | adopt / not | open (recommended: adopt) |
| FD-2″ | mandatory epoch id; lower-watermark snapshot handling | (a) SEQ_CONTRACT; (b) broker as_of / epoch in schema | open (R3: epoch required) |
| FD-3 | unsequenced executions | out of contract / permanent-MISMATCH cost | open |
| FD-4′ | later-bust exposure | merged into FD-14 | superseded |
| FD-5 | controlled Rev 3.2 drafting | **consolidation authorized 2026-11-24; freeze not authorized** | partly decided |
| FD-6 | associated duplicate copy | — | **moot** under FD-8 |
| FD-7 | expires_at bounded by S_lim | adopt / re-check at consume | open; **required** per R4 |
| FD-8 | id-less unsequenced deliveries | out of contract / R-07″ per-order lists | open (recommended: out of contract) |
| FD-9 | suspension scope | — | **moot** (R4: suspension never releases) |
| FD-10 | D_max | (a) withdraw as a safety rule; (b) intent-age policy | open |
| FD-11 | A-15 and the violation response | (a) bounded orphan treatment; (b) structural; changes V11, V12, V22–V25 | open |
| FD-12 | keyed reconciliation lists mandatory? | yes / reduced capability allowed | open |
| FD-13 | `release` operation | add / not | open (recommended: add) |
| FD-14 | finality reserve CA-15′ | adopt / accept delayed busts as environmental | open |
| FD-15 | basis for FINAL | (a) broker evidence; (b) time, A-16 plus P-1a | **open; presented without recommendation** (R7 §7) |
| FD-16 | bootstrap mode | require M1 / allow M0 or M1q with costs | open |
| FD-17 | correction after FINAL | block both sides / detection only | open |
| FD-18 | re-bootstrap as a governance operation | authorize / not | open |
| FD-19 | A-14″, or a 2q reserve | — | open |
| **FD-20** | channel suspicion vs A-17 | (a) fail closed (open to denial of service); (b) A-17 | **UNRESOLVED.** GPT's reviewer recommendation: (a) as the reference default until the authentication architecture is independently reviewed. Not a decision |

**FD-15 options table** (preserved from R7 §7, without recommendation):

| | Option A: broker evidence | Option B: time-based |
|---|---|---|
| Assumptions | the broker's finality statement is truthful | T_f per class C_f; L_n while healthy; σ |
| Failure modes | a false or premature statement; none ever supplied (the reserve becomes permanent) | a class outside C_f; L_n exceeded inside a healthy-looking stream (undetectable); a wrong T_f; skew |
| After FINAL | FINAL_VIOLATED + FINALITY_ASSUMPTION_FAILED | the same |
| Revocable | yes; every FINAL from the same source becomes suspect | yes; every FINAL under the same parameter set and class becomes suspect |
| Widen-only | unaffected | requires P-1a (a doctrine amendment) |
| Availability | depends on a broker capability (UNVERIFIED) | predictable, if the parameters are accepted |

---

## 11. Superseded proposals register (historical, not operative)

| Superseded | By | Reason | Source |
|---|---|---|---|
| R1 R-01 "every message that consumes a number is delivered" | A-2″ (no delivery assumption) | silently narrowed A-12 | R2 §2 |
| R1 R-07 "each delivery a separate orphan, conservative on both bounds" | R2 R-07′, then R3 (exit withdrawn), then FD-8 / R-07″ | applying duplicates gives false permission | R2 §3, R3 Ch. 1 |
| R2 R-07′ exact-multiplicity exit via cum_qty | R-07″ per-order execution lists, or FD-8 | cum_qty does not attribute (C1-a) | R3 |
| R1 R-12 epsilon | R-12′, then R-12″ | no operational meaning | R2 §7, R3 Ch. 3 |
| R2 R-12′ ambiguous decision.as_of | R-12″ (t_eval vs t_L) | invited a tautology | R3 |
| R2 R-15 | R-15′, then R-15″ | one-sided; A_raw-only reactivation | R3 Ch. 2, R4 |
| R3 R-15′ "every other ACTIVE reservation" | R-15″ (aggregate Π; suspended counted) | could exclude SUSPENDED | R4 |
| R2 CX-28 claim (pre-bootstrap event gives false permission) | R3 §0: availability only | ignored the F_d(W) comparison | R3 |
| R4 CA-1 registry-only F_d | §3.3 version history | historical boundaries | R5 §E |
| R5 E-B independent ⊥ placement | §3.5 admissible cuts | impossible values (CX-36) | R6 H1, R7 §3 |
| R5 case 8 "snapshot restores determinacy" | §3.6 | overstated | R6 H3, R7 §4 |
| R5 E-A status inside L2 | §3.1 status in L3 | evidence/disposition mixing | R6 H2 |
| R7 CA-15′ finality from receipt | §6.2 | receipt ≠ application | R8 AM-15 |
| R8 AM-15 freeze / resume | §6.2 gate (no pause) | ambiguous | R9 AM-15′ |
| R8 AM-13 basis_digest as the test | §7.4 AM-13′ | incomplete (CX-48) | R9 |
| R8 H-7 M1 acceptance test | §3.8 AM-16′ | contradicted its own definition (CX-51) | R9 |
| R8 H-4 INVALIDATED for every impugnment stage | §7.4 INCOMPLETE vs IMPUGNED | distinguishes uncertain from contradicted | R9 |
| FD-1 (a)/(b), FD-2′ | FD-1′, FD-2″ | refined | R2, R3 |
| Draft 1 §8 GAP rule (from R4 CA-8): "…or the snapshot boundary has W > H_e" | §8 status table | made AWAITING-BEHIND unreachable (INT-01, CX-53) | integration review |
| Draft 1 §3.2 τ_D including κ | τ_D over the identity field set I; κ as an attribute | broke cross-path identity (INT-03, CX-54) | integration review |
| Draft 1 §3.5 "versions 0..k", "κ ≤ β ⇔ i ≤ k" unqualified | chain positions + A-11-ORD; hull without it | assumed broker-version/stream-key equivalence (INT-02, CX-55) | integration review |
| Draft 1 §7.1 "no reservation exists" | scoped, atomic commit procedure | scope and atomicity unstated (INT-04) | integration review |
| R3 case 8 "e′ messages buffered pending bootstrap" | §8 row 2: applied; status UNKNOWN | contradicted R4 D-1 (INT-05) | integration review |
| Draft 1 R-02′ marked OPERATIVE | CONDITIONAL-ON-FD-1′ | FD-1′ was open (IC-1, CX-56) | integration review |
| Draft 2 §8 row 8 "otherwise (every choice gives d = 0)", and its "Bounded: yes" column | SR gate (row 7) + rows 8–9; BOUNDED per Rev 3.1 line 148 | vacuous truth on empty sets; structural states fell through (P0-1, CX-57) | draft-2 review |
| Draft 2 §7.3 "For a buy r: U(ρ) ≤ L … already counted" (used at commit) | Π over σ with r counted exactly once; ρ ⊕ r at commit | readable as a pre-proposal check (P0-2, CX-58) | draft-2 review |
| Draft 2 §7.2 "every unexpired reservation contributes its order's R" | single commitment identity order_id; B, S = Σ R over WORKING orders | readable as a second summand; handoff unspecified (P0-3, CX-59) | draft-2 review |
| Draft 2 §7.1 step 6 "append the L1 commit record; write the L3 basis record" and §7.4 "basis record" | basis inside L1 commit record C; p_b = p_C − 1; fold discipline | two schemas; p_b boundary ambiguous (P1-1, CX-60) | draft-2 review |
| Draft 2 §3.5 hull of chain states "{0} ∪ {q_i : not forced after β}", **DERIVED sound** | H_Δ | unsound without A-11-ORD (CX-62); claim withdrawn | draft-2 review |
| Draft 3 §7.1 "`consume` follows the same pattern" | consume linearization (proposal C, amended) | unspecified preconditions and idempotency | draft-3 clarifications |
| Draft 3 §3.2 untyped tag-length encoding | typed canonical encoding with schema version (proposal D) | no field types, enumerations or schema lineage | draft-3 clarifications |
| Draft 3 SR clause 1 "proposal … conflicts" | caller conflicts reclassified as integrity alerts | a caller error could lock the account | draft-3 clarifications |
| Draft 3 response §1 "design call" (UNKNOWN vs an eighth status) | status envelope (proposal E): seven statuses plus a mandatory reason-code set | settled by adopting E | draft-3 clarifications |
| Proposal A sentence "Receipt of additional evidence alone does not close it" (unamended) | evidence closes only through a named resolution rule | would make PENDING permanent (CX-65) | draft-3 clarifications |
| Proposal B clause 5 "or a separately authorized replacement basis" | not adopted; a new proposal and commit is the replacement path | undefined authority (CX-66) | draft-3 clarifications |
| Proposal C "verifies the relevant revision" | no revision binding; Π re-evaluated on the current revision | always fails, or TOCTOU (CX-68) | draft-3 clarifications |
| Proposal C "recorded as a conflict"; proposal E "itself a structural failure" | integrity alert; per-call evaluation fault | lockout with no resolution (CX-67) | draft-3 clarifications |
| Draft 2 §3.2 "ASCII-normalized identifiers" | injective, length-prefixed byte encoding | non-injective normalization can collapse identities (CX-61) | draft-2 review |

---

## 12. Open questions and unresolved items (carried forward, not resolved here)

| ID | Question (from GPT's assessment of R9) | Affects | Current operative text | Known state |
|---|---|---|---|---|
| **OQ-H15** | Define the admissible historical placements of retro-relevant evidence, especially unsequenced events. Required rule: INTACT iff every admissible placement allows; IMPUGNED iff every placement denies; INCOMPLETE iff mixed | §7.4 AM-13′ | the worst-case Π evaluation | **known defect**: the current text labels "some placement denies" as IMPUGNED, which over-reports impugnment. Not yet corrected |
| **OQ-H16** | Specify the full deterministic execution environment for reproducing Π from the basis: precision and rounding (integers only per A-13, to be confirmed for all derived values), schema and canonicalization versions, collection ordering, clock inputs, every external input, tie-breaking, runtime version | §3.1 I9-ext, §7.4 | "complete by construction" | **CONDITIONAL**; contract not written |
| **OQ-R1** (new, draft 4) | Define a resolution operation for every structural condition in the §8 A-map that lacks one (SEQ_CONTRACT; the FORK, STALE, KEY_MISMATCH, ORDER_CONTRADICTION and NUMBERING_INCONSISTENT subtypes), or confirm that governance closure (FD-18) is intended for each. Restate the three rows that defer to Rev 3.1 (overfill, D26/D27, §2.8 failures) | §8 A-map | none | OPEN |
| **OQ-H17** | Define legitimate broker version-counter resets: does a reset create a version epoch; can an execution survive across it; how are old list entries interpreted; keep the broker version distinct from the stream sequence. **Also: cross-namespace ordering (INT-02).** Under what broker guarantee does chain order equal stream-key order (A-11-ORD), and how should ⊥ versions be ordered against keyed ones when A-11-ORD cannot be checked? | §3.2 A-11⁗, §3.4 | none | open |
| **OQ-H18** | Finality ordering at exact ticks, and the outage boundary cases: an outage before or at the deadline; several outages; an outage during the latency allowance; a blocker arriving or dismissed at the tick; an applied correction and the tick together. Keep T_f, L_n, σ and observed stream health separate | §6.2 | gate W ∧ H ∧ ¬Blocker | provisional; only two examples |
| **OQ-H19** | Distinguish historical authorization invalidity from policy-migration exposure: a separate POLICY_MIGRATION_EXPOSURE class instead of "treated like BASIS_INCOMPLETE" | §7.6 AM-14′ | BASIS_UNDER_SUPERSEDED_RULES treated like INCOMPLETE | **known defect** (conflation). Not yet corrected |
| **FD-20** | authentication trade-off | §9 | — | **UNRESOLVED founder decision** |
| Others | FD-1′, FD-2″, FD-3, FD-7, FD-8, FD-10 to FD-19 | various | marked [CONDITIONAL-ON-FD-n] | open (§10) |

---

## 13. Consistency review

### 13.1 Unresolved conflicts

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
| C-18 | Under proposal A, structural conditions without a resolution operation persist until governance. With a global SR, one such condition locks the account. This sharpens C-8 and C-14 | §8 A-map | OQ-R1; FD-18; FD-20 |
| C-19 | An impugned original basis invalidates a reservation even when a later reactivation basis is intact. Conservative, possible over-denial | §7.2 reactivation | review; it could be relaxed only with an argument about the unexposed interval |
| C-20 | Integrity alerts (R_PROPOSAL_CONFLICT, CONSUME_IDENTITY_CONFLICT) are excluded from SR. This is safe only if every effect on the broker side is caught as an unknown order (E20). That detection depends on A-12″ and adapter behaviour (G-07) | §7.1, §8 | G-07; adapter acceptance R-16 |

### 13.2 Missing dependencies

- **Broker capabilities (all UNVERIFIED):**
  - stable account-unique exec_ids;
  - τ_B or broker versions on CORRECT and BUST, and predecessors on BUST;
  - one version numbering across paths;
  - keyed per-order lists with versions and declared bust semantics;
  - authenticated as-of M1 manifests;
  - epoch ids and declared starts;
  - contiguous numbering with declared coverage;
  - a finality window or finality evidence;
  - a notification-latency bound;
  - no-short / position barriers;
  - sub-account exclusivity.
- **Governance:**
  - D23 (key custody: blocks every Authenticity claim and A-17);
  - D24 (independent evidence);
  - G-04 (the limit L);
  - G-06 (protective intervention);
  - G-07 (adapter, cancellation authority).
- **Specification:**
  - the determinism contract (OQ-H16);
  - version resets (OQ-H17);
  - the adapter acceptance tests (5.7 item 8, R-16) have no specification of the adapter itself.

### 13.3 Acceptance tests and vectors: **none executed**

| Group | Items | Source | Status |
|---|---|---|---|
| Limitation vectors | V63 (CX-01), V64 (CX-12), V65 (CX-08), V66 (CX-27), V67 (C-1) | R1 R-14, R2, R4 | hand-derived; not executed |
| Clarification vectors | V68 to V73 (A-1, B-1, D-1, the A-1 absence variant, C-2, the naive-adopt negative) | R4 CA-9 | hand-derived |
| E/F/G vectors | V74 to V83 | R5 | hand-derived |
| H vectors | V84 to V94 | R6 | hand-derived |
| Draft-4 vectors | V114 every A-map row → SR false while open; resolution recorded in L3 → SR true; no timeout closes a row; V115 PENDING closes only through HISTORY FILL (CX-65); V116 reactivation with an impugned original basis → stays SUSPENDED → INVALIDATED; V117 reactivation with an expired TTL → refused; V118 consume with an intervening event → Π re-evaluated, no revision-equality failure (CX-68); V119 a duplicate consume with the same submission identity → idempotent; a different one → refused, alert, SR unchanged; V120 enumerated value out of range → malformed, no bind; V121 a reason-code serializer fault → that call DENY, no persistent condition (CX-67); V122 a clean ledger carries NONE | draft-3 clarifications | specified; **not executed** |
| Draft-3 vectors | V104 status truth table including every SR clause, empty X(β) and no-watermark quiescent; V105 an ORDER_CONTRADICTION on an otherwise d = 0 ledger → UNKNOWN (STRUCTURAL), never RECONCILED (CX-57); V106 buy with U = 140, L = 150, Q = 30 → DENY at commit (CX-58); V107 sell with A_raw = 40, Q = 50 → DENY (CX-58); V108 consume interleaved with an evaluation: no revision with R counted 0 or 2 times (CX-59); V109 expiry racing consume → exactly one wins; V110 a bust keyed ≤ H_c arriving between the frontier and C is impossible by fold discipline, and arriving after C triggers the retro-relevance test (CX-60); V111 distinct exec_ids "a1B" and "A1b" → distinct τ (CX-61); V112 the CX-62 chain → H_Δ contains 130 and 70; V113 under A-11-ORD, every admissible cut sum lies in H_Δ | draft-2 review | specified; **not executed** |
| Integration vectors (draft 2) | V95 status truth table (every combination → one row; rows 4 and 5 reachable); V96 τ_D: one transition via a keyless list and a keyed stream → one τ, key attached (CX-54); V97 KEY_MISMATCH; V98 broker versions 0, 2, 5 → no gap (CX-55); V99 A-11-ORD violation between keyed versions → ORDER_CONTRADICTION; V100 two concurrent commits on one revision → at most one reservation, the other re-evaluates; V101 duplicate proposal_id with a different hash → R_PROPOSAL_CONFLICT; V102 new-epoch events applied, status UNKNOWN until an e* snapshot; V103 evidence received at the tick time precedes the FINAL tick (IC-4, provisional) | integration review | specified; **not executed** |
| Rule acceptance tests | AM-1 to AM-9 (R7 §12); AM-10 to AM-16 (R8); AM-11′, AM-13′, AM-14′, AM-15′, AM-16′, AM-17 (R9) | R7–R9 | specified; not executed |
| Oracle and verification obligations | R-04 (G3 in every classification); R-05 (unknown-side orders in the oracle domain and grid); R-06′ (raw-fact grid, separate status checker, import ban, mutation suite: monotone-only GAP, narrow GAP, pre-W0 apply, REPLAY-ignore, independent placement, digest-only basis, τ from Sentinel index); admissible-cut enumeration; layer re-derivation byte-equality; finality deferral against stream-health intervals; interleaving tests of migration | R1, R2, R6–R9 | specified; **no oracle exists** |
| Rev 3.1 §5.7 prerequisites | items 1 to 9, plus additions from R4 CA-10, R5, R6, R7 | various | not produced |

### 13.4 Editorial items still to apply (R1 R-13)

- Rev 3.1 §7 says "56 hand vectors". It should be 61 (V01–V62 less V09), or the extended count once V63+ are adopted.
- Rev 3.1 §2.5 says "A-1 to A-11". It should cover every assumption, A-1 to A-17 in the candidate.
- In I2, label D19 preconditions 3 and 5 as consequences of the decision rule (R2 §9; R-17: D19 restated with two substantive preconditions).
- The validity predicate routes F_b < 0 to the V54 path instead of excluding it.
- 5.7(4): add the D26/D27 payload variants.

### 13.5 Counterexample register (consolidated; nothing deleted)

| IDs | Source | Status |
|---|---|---|
| CX-01, CX-08, CX-11, CX-12, CX-13, CX-18 | R1 | documented limitations (A-12″, A-11″, W1, W6/I8, A-7); CX-12 partly addressed by CA-15 |
| CX-02, CX-04 | R1 | resolved by A-2″ and R-03″ (DERIVED) |
| CX-03 | R1 | resolved by R-08 (DERIVED) |
| CX-06, CX-07, CX-09, CX-14, CX-16 | R1 | safe as specified (DERIVED) |
| CX-10 | R1 | resolved under A-2″ |
| CX-15 | R1 | coverage: R-05 plus generative tests |
| CX-17 | R1 | resolved by R-12″ |
| CX-19 | R1 | FD-8 / R-07″ |
| CX-20 | R1 | resolved by R-02′ |
| CX-21 | R1 | FD-3 |
| CX-22 | R1 | R-04 |
| CX-23 | R2 | resolved by the GAP rule |
| CX-24, CX-25 | R2 | R-12″ / FD-7 |
| CX-26 | R2 | R-15″ |
| CX-27 | R2 | FD-8 / R-07″ |
| CX-28 | R2 | **corrected in R3** (availability only) |
| C1-a, C3-a, C4-R | R3 | C1-a resolved by R-07″ / FD-8; C3-a by R-12″ / FD-10; C4-R outside the contract (A-2″) |
| A-1, B-1, C-1, C-2, D-1 | R4 | C-1 is a limitation (A-15 / A-12″); the others are demonstrations (COMPUTED) |
| CX-29, CX-30 | R5 | CX-29 under CA-15; CX-30 by version history |
| CX-31 | R5 | open (C-1 in §13.1) |
| CX-32 | R5 | M0 UNRESOLVED rule |
| CX-33 | R5 | case-8 windows |
| CX-34, CX-35 | R6 | outside CA-15 unless A-14″ or M1 / A-16b |
| CX-36 | R6 | admissible cuts |
| CX-37 | R7 | FORK rule |
| CX-38 | R7 | τ with broker versions (A-11‴) |
| CX-39 | R7 | availability (C-7) |
| CX-40 | R7 | AM-9 / C-9 |
| CX-41 | R7 | finality per version |
| CX-42 to CX-47 | R8 | resolved by AM-11, AM-12, AM-13→AM-13′, AM-14, AM-15→AM-15′, AM-16→AM-16′ respectively |
| CX-48 | R9 | AM-13′ |
| CX-49 | R9 | AM-11′ |
| CX-50 | R9 | AM-15′ |
| CX-51 | R9 | AM-16′ |
| CX-52 | R9 | open (FD-20) |
| **CX-53** | integration review | the draft-1 GAP predicate made AWAITING-BEHIND unreachable (a snapshot ahead with no hole reported GAP). Availability and reason-code defect, not a false permission (DERIVED). Corrected (§8 table) |
| **CX-54** | integration review | τ_D with κ: the same transition via a list without a key and the stream with one gave different τ, so the predecessor check reported STALE → a false CONFLICT (availability). Without ν, a list-first ordering also produces it. Corrected (τ_D over I) |
| **CX-55** | integration review | broker versions 0, 2, 5 (strictly increasing, skipping). Treating 1, 3 and 4 as missing makes x falsely PENDING/UNRESOLVED; treating numbers as contiguous positions mis-links the chain. Corrected (chain by predecessor links) |
| **CX-57** | draft-2 review | an ORDER_CONTRADICTION empties ExecutionState(x, β_c); draft-2 row 8 "every choice gives d = 0" is vacuously true → RECONCILED, marked Bounded yes. Rev 3.1 line 148 would still make it UNBOUNDED, so Π's BOUNDED test blocks, but the candidate's own table contradicted it. This was a latent false-permission path for any implementation that followed the table (DERIVED). Corrected (SR, row 7) |
| **CX-58** | draft-2 review | L = 150, F_max = 100, B = 40 (U = 140), buy Q = 30. The pre-proposal reading U(ρ) = 140 ≤ 150 passes, and the commit yields U = 170 > L: **false permission**. Sell: F_min = 100, S = 60 (A_raw = 40), Q = 50 passes A_raw ≥ 0 and yields A_raw = −10. Corrected (Π over ρ ⊕ r) |
| **CX-59** | draft-2 review | (a) reading B as Σ reservations + Σ WORKING orders counts an ACTIVE reservation's AUTHORIZED order twice: over-denial. (b) a two-step consume (reservation CONSUMED, then the order SUBMITTED in a later revision) with B counting unexpired reservations plus non-AUTHORIZED working orders leaves one revision in which the commitment counts zero times: **false permission** for any evaluation in that revision. Corrected (one identity; atomic consume) |
| **CX-60** | draft-2 review | p_b = p_C with a receive path that appends without folding. A bust keyed ≤ H_c is appended after the evaluated frontier but before C. It lies inside the prefix, so it is never "received after p_b" and never triggers the retro-relevance test. The basis stays INTACT although the decision never saw the bust: a missed BASIS_IMPUGNED. Corrected (fold discipline; p_b = p_C − 1 = f(ρ)) |
| **CX-61** | draft-2 review | exec_ids "a1B" and "A1b" are distinct at the broker and fill 5 each. Case folding gives the same τ, so the second is a duplicate and F_d undercounts a buy by 5: **false permission** at the margin. Corrected (no non-injective normalization) |
| **CX-62** | draft-2 review | chain v0 fill 100 (κ ≤ W), v1 correct 100 → 40 (δ = −60, ⊥, list only), v2 correct 40 → 70 (δ = +30, κ ≤ W). Without A-11-ORD, v1 may have been emitted after W. The stream-prefix truth at W is then 100 + 30 = 130. The chain-state hull {0, 100, 40, 70} has maximum 100 and excludes 130, so the bound is **unsound**. H_Δ = [100 + 30 − 60, 100 + 30] = [70, 130] contains both 130 and 70. Corrected (H_Δ; the draft-2 soundness claim withdrawn) |
| **CX-65** | draft-3 clarifications | proposal A unamended: a list delivers v2 before the stream delivers v1, giving routine PENDING. "Evidence alone does not close it", so the later arrival of v1 cannot close PENDING without an unnamed operation, and the account locks permanently on ordinary out-of-order arrival. Availability defect. Amended |
| **CX-66** | draft-3 clarifications | proposal B clause 5: with "a separately authorized replacement basis" and no definition of who authorizes it, any process that asserts a replacement could reactivate a reservation whose basis was impugned, and reach consume. A potential **false-permission path** through undefined authority. Not adopted |
| **CX-67** | draft-3 clarifications | proposal E unamended: a transient reason-code serialization fault is "a structural failure". Under proposal A it has no resolution operation, so the account is locked until founder re-bootstrap. Availability and governance defect. Amended (per-call evaluation fault) |
| **CX-68** | draft-3 clarifications | proposal C "verifies the relevant revision". (a) Read as equality with the commit revision, any applied event between commit and consume makes every consume fail (liveness). (b) Read as the revision of an evaluation performed outside the lock, consume acts on a stale evaluation, a time-of-check / time-of-use gap and a **false-permission** risk. Amended (Π on the current revision, inside the lock) |
| **CX-56** | integration review | FD-1′ declined while R-02′ was marked operative: the vectors assume FIXTURE_PASS, yet the literal §2.8 denies everything. A specification contradiction. Corrected by marking (IC-1); still blocking if FD-1′ is declined |

---

## 14. Change ledger (amendment → source → target → status)

| Amendment | Source (document §) | Target (Rev 3.1 §) | Status label | Marker |
|---|---|---|---|---|
| P-RA | R8 opening | §2.4 | DERIVED | OPERATIVE |
| P-1a | R6 §H6 | §2.4 | — | CONDITIONAL-ON-FD-15(b) |
| A-2″, H/M, GAP rule | R2 §2, R3 Ch. 4, R4 CA-2 / CA-8 | §2.11, §2.6, §2.6.2 | ASSUMED / DERIVED | OPERATIVE |
| R-03″ table, SEQ_CONTRACT | R2 §4, R3 Ch. 4 | §2.6, §2.6.3 | DERIVED | OPERATIVE |
| R-08 sequence resolution | R1 | §2.2, §2.4.1 | DERIVED | OPERATIVE |
| R-02′ evidence terminology and profile | R2 §5 | §2.8, D06 | DERIVED | OPERATIVE (FD-1′) |
| R-04 G3 classification | R1 | §2.5 I4, §5.1, §5.2 | verified by reading | OPERATIVE |
| R-05 unknown-side oracle | R1, R2 §9 | §5.1, §5.2 | DERIVED | OPERATIVE |
| R-06′ status checker | R2 §6 | §5 | — | OPERATIVE (obligation) |
| R-07″ per-order lists | R3 Ch. 1, R4 CA-5 | §2.4.1 item 6 | DERIVED | CONDITIONAL (FD-8, FD-12) |
| R-09 net_cum_at | R1 | §2.2 | DERIVED | OPERATIVE |
| R-10 unsequenced executions | R1 | §2.2, §2.6.2 | DERIVED (CX-21) | CONDITIONAL-ON-FD-3 |
| R-11 snapshot master version | R1 | §2.2, §2.12 | — | OPERATIVE |
| R-12″ linearization | R3 Ch. 3, R4 CA-7 | §2.9, I5 | DERIVED | OPERATIVE (FD-10, FD-7) |
| R-13 editorial | R1 | various | — | pending application |
| R-14 limitation vectors | R1, R2, R4 | §2.10 | hand-derived | OPERATIVE |
| R-15″ lifecycle, Π, OVER_LIMIT | R4 B, CA-6 | §2.9, I3, I8 | DERIVED; B-1 COMPUTED | OPERATIVE |
| R-16 adapter test | R2 §8 | §5.7 | — | OPERATIVE (obligation) |
| R-17 D19 restatement | R2 §9 | I2 | DERIVED | OPERATIVE |
| A-11″, A-11‴, A-11⁗, τ, ν, dedup | R4 CA-3, R7 §2, R8 AM-11, R9 AM-11′ | §2.2, §2.6.3, §2.11 | ASSUMED / DERIVED | OPERATIVE (CONDITIONAL) |
| A-12″ | R4 CA-4, R5 | §2.11, §2.3 | ASSUMED | OPERATIVE |
| A-15 | R4 CA-4 | §2.11 | ASSUMED | CONDITIONAL-ON-FD-11 |
| Execution registry and identity | R4 CA-1 (identity part) | §2.2 | DERIVED; A-1 COMPUTED | OPERATIVE |
| Reconstruction equation, epochs | R4 Ch. D, CA-1 | §2.2 | DERIVED; D-1 COMPUTED | OPERATIVE |
| Version history (L2) | R5 E-A | §2.2 | DERIVED; E-1 COMPUTED | OPERATIVE |
| Evidence layers L1–L4, I9-ext | R6 §H2 | §2.2, I9 | DERIVED | OPERATIVE (OQ-H16) |
| Admissible cuts, I13 | R6 §H1, R7 §3 | §2.2 | DERIVED; COMPUTED | OPERATIVE-PROVISIONAL |
| Reconciliation levels | R7 §4 | §2.2, §2.4.1 | DERIVED | OPERATIVE |
| Joint list + snapshot determinacy | R6 §H3 | §2.4.1 | DERIVED; COMPUTED | OPERATIVE |
| Bootstrap M0 / M1 / M1q, M1 contract | R5 G, R7 §9, R8 AM-16, R9 AM-16′ | §2.2 (new) | DERIVED | OPERATIVE |
| Anchors | R7 §5 | §2.2 | DERIVED | OPERATIVE |
| Pre-bootstrap classes, dismissal rule | R5 G, R7 §10 | §2.6 | DERIVED | OPERATIVE |
| Re-bootstrap | R6 §H4, R7 §4 | §2.2 / §3 | — | CONDITIONAL-ON-FD-18 |
| CA-15′ reserve, rule F1 | R5, R7 §6, R6 H5 | §2.4.3 (new) | DERIVED; F-2 COMPUTED | CONDITIONAL-ON-FD-14 |
| AM-12 pending local reserve | R8 | §2.4.2, §2.4.3 | DERIVED; COMPUTED | OPERATIVE |
| Finality gate AM-15′ | R9 | §2.4.3 / new §6 | DERIVED; COMPUTED | OPERATIVE-PROVISIONAL (OQ-H18) |
| A-16, A-16b, FINAL_VIOLATED | R5, R6 H6 | §2.11, §2.8 | ASSUMED | CONDITIONAL-ON-FD-15 / FD-16 / FD-17 |
| A-14″ | R6 H5 | §2.11 | ASSUMED | CONDITIONAL-ON-FD-19 |
| AM-10 ORDER_CONTRADICTION | R8 | §2.2, §2.8 | DERIVED | OPERATIVE |
| AM-13′ authorization basis | R9 | §2.9 (new) | DERIVED; CX-48 COMPUTED | OPERATIVE-PROVISIONAL (OQ-H15, OQ-H16) |
| AM-14′ migration | R8, R9 | §2.9 (new) | DERIVED | OPERATIVE-PROVISIONAL (OQ-H19) |
| AM-17 attribution, CHANNEL_SUSPECT | R9 | §2.8 | DERIVED | OPERATIVE; effect open (FD-20) |
| AM-9 list bust semantics | R7 §12 | §2.4.1 | DERIVED | OPERATIVE |
| Account-exclusivity limitation statement | R4 Ch. C | §2.3 | DERIVED | OPERATIVE |
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
| P0-1 SR predicate; status row 7; rows renumbered 8–9; truth table | draft-2 review | §2.6.2 | DERIVED (hand-enumerated) | OPERATIVE |
| P0-2 Π over σ with r counted once (ρ ⊕ r at commit) | draft-2 review | §2.9, §2.4 | DERIVED | OPERATIVE |
| P0-3 single commitment identity; state mapping table; atomic consume; exclusive pre-submission exits | draft-2 review | §2.9, I6, T04, T05 | DERIVED | OPERATIVE (RELEASED CONDITIONAL-ON-FD-13) |
| P1-1 fold discipline; L1 operation records; basis in L1 commit record; p_b = p_C − 1 | draft-2 review | §2.2.A, §2.9 | DERIVED | OPERATIVE (basis completeness CONDITIONAL on OQ-H16) |
| Additional 1: delta hull H_Δ; I13 amended; draft-2 hull withdrawn | draft-2 review | §2.2.E | DERIVED; relies on stream-prefix W1 (UNVERIFIED) | OPERATIVE-PROVISIONAL |
| Additional 2: injective identifier encoding | draft-2 review | §2.2.B | DERIVED; hash collision resistance ASSUMED | OPERATIVE |
| A: structural-state traceability, A-map, closure rule, SR completeness obligation (amended: evidence-driven resolution named) | draft-3 clarifications | §2.6.2 | DERIVED; map completeness not verified | OPERATIVE |
| B: reactivation as a new authorization; suspension causes; TTL fixed; reactivation basis (amended: no replacement-basis path) | draft-3 clarifications | §2.9 | DERIVED | OPERATIVE |
| C: consume linearization; submission identity; idempotency (amended: no revision binding; an alert, not structural) | draft-3 clarifications | §2.9 | DERIVED | OPERATIVE |
| D: typed canonical encoding; enumerations; schema lineage | draft-3 clarifications | §2.2.B | DERIVED | OPERATIVE |
| E: status envelope; explicit NONE; evaluation faults are per call (amended) | draft-3 clarifications | §2.6.2 | DERIVED; adapter side UNVERIFIED | OPERATIVE |

---

## 15. Readiness

1. **Internally coherent?** As candidate text, subject to the twenty conflicts in §13.1 (C-1 to C-20), of which two are known defects (OQ-H15, OQ-H19). **DERIVED.**
2. **False-authorization paths inside the proposed contracts?** The draft-2 review exposed false-permission readings of the draft-2 text: CX-58 (pre-proposal Π), CX-59(b) (handoff gap) and CX-61 (identifier collapse); a latent one, CX-57 (table versus Rev 3.1 BOUNDED); a missed impugnment, CX-60; and an unsound hull, CX-62. All are corrected in draft 3. **No further path found in draft 3: DERIVED, not executed.** The fact that four rounds have each found new paths is itself evidence that hand review is not converging to verification. OQ-H15 currently *over*-reports impugnment, which is conservative.
3. **Paths excluded only by environmental assumptions:**
   - CX-01 and C-1 (A-12″, A-15);
   - CX-34 (A-14″);
   - CX-35 (M1 or A-16b);
   - post-FINAL corrections (A-16);
   - C4-R (A-2″);
   - CX-38 and CX-54 (A-11‴, including the identity field set I);
   - CX-55 and cut admissibility (A-11-ORD);
   - CX-62 and H_Δ soundness (stream-prefix snapshot semantics, C-16);
   - CX-61 (injective per-path decoding declared correctly);
   - CX-08 (A-11″);
   - CX-11 (W1 common mode);
   - CX-18 (A-7);
   - CX-52 (FD-20 / A-17).
4. **Broker capabilities unverified:** all of them (§13.2).
5. **Ready for hostile review?** Yes, as one consolidated candidate. Recommended first targets: OQ-H15 to OQ-H19, and the §13.1 conflicts.
6. **Authorized:** none of implementation, oracle construction or execution, broker contact, paper trading, live trading, or a Rev 3.2 freeze.

*The central distinction this candidate is built to preserve: what the system believed when it authorized an action, and what later evidence establishes about whether that belief was justified. Every claim above is hand-derived or single-example arithmetic. Independent verification: none.*
