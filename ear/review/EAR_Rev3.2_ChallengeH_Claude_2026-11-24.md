# EAR v0.1 Rev 3.2 Candidate: Challenge H (Version Ordering, Evidence Layers, Bootstrap Resolution, Finality)

SPECIFICATION ANALYSIS ONLY. Rev 3.1 (`dd9d87f76b01134e…a239`) stays frozen. No implementation, oracle, broker contact, paper or live trading is authorized. All amendment text is candidate only.
Reviewer: Claude (Specification Lead / ARBITER). Date: 2026-11-24 (ET).
Prior documents: R5, the E/F/G closure pass (`6faf10f2…`), and earlier.

Labels:
- **DERIVED**: follows from the stated definitions.
- **COMPUTED**: integer arithmetic or a brute-force enumeration of one hand example, run by a throwaway Python script using Rev 3.1 §2.4 and the ExecutionState definition below. It establishes arithmetic only.
- **ASSUMED**, **CONDITIONAL**, **UNVERIFIED**, **UNBOUNDED**: as before.

---

## H1. Admissible order-preserving histories for unsequenced corrections

**A defect in R5 (E-B), confirmed.** R5 said an unsequenced transition is "enumerated before and after β". Doing that *independently* for each transition admits impossible orderings.

Counterexample, CX-36 (COMPUTED). Execution X has the chain:
- v0 = 10 at (e, 501);
- v1 = 6 at (e, 508);
- v2 = 3 unsequenced (κ = ⊥), and by its prior_version it comes after v1.

At β = (e, 505), the only admissible effective version is v0, giving 10. Independent placement also allows "v2 before β", giving 3, which is impossible because v2 follows v1 and v1 is at 508 > 505.
- With P_open = 100 and F_b = 110, the admissible d is {0}; independent placement adds d = 7.
- The result is still conservative (a larger world set only widens the bounds), but the bounds no longer equal the declared world set. That breaks oracle equivalence and costs availability.

**Definition (candidate).**
- For an execution x with chain v_0 … v_n (ordered by version, which D27's prior_version makes total), a **cut** at β is an index k ∈ {−1, 0, …, n}: versions 0..k are at or before β, the rest after.
- A cut is **admissible** iff every keyed version v_i satisfies (κ(v_i) ≤ β) ⇔ (i ≤ k).
- So with i_lo = the largest keyed index with κ ≤ β (−1 if none) and i_hi = the smallest keyed index with κ > β (n+1 if none), the admissible cuts are exactly **k ∈ [i_lo, i_hi − 1]**.
- When i_lo ≥ i_hi, there is no admissible cut: the keys contradict the version order, which is already a CONFLICT under R5's E-B monotonic-key rule.
- Effective value: q_k (signed), with q_{−1} = 0 (not yet existing); an IN_OPENING anchor contributes 0.
- **ExecutionState(x, β)** = the set {q_k : k admissible}. It is a singleton exactly when i_hi = i_lo + 1.
- **F_d(β)** ranges over the product of the per-execution sets. Different chains are independent: no constraint links their cuts beyond each chain's own keys, which are fixed. So:
  - **d_max = F_b − P_open − Σ_x min ExecutionState(x, β)**
  - **d_min = F_b − P_open − Σ_x max ExecutionState(x, β)**

  This is the same linear separability as Rev 3.1 §2.2's interval, now over versions. Values need not be monotone in k, which is why min and max are taken over the set.

Check (COMPUTED): the admissible cuts for the CX-36 chain are {0} at β = 505 (values {10}) and {1, 2} at β = 510 (values {6, 3}). Independent placement gives {3, 10} at 505.

**Impossible combinations cannot enter (DERIVED).** Every value in ExecutionState comes from an admissible cut. Non-admissible cuts are never generated. Chains with PENDING or CONFLICT entries are UNRESOLVED (band UNBOUNDED), so they contribute no value at all. Invalid chains therefore cannot widen or narrow the bounds.

**Oracle obligation.** The oracle enumerates admissible cuts per chain, not per-transition before/after flags. A mutation test must include the independent-placement rule as a known-wrong variant: it should register as an availability (UNEXPLAINED-gap) disagreement.

---

## H2. Four evidence layers: nothing is rewritten

R5 put `status` and `conflict_ref` inside history entries. That mixes evidence with disposition, so they are moved out. Each layer is append-only.

| Layer | Content | Written by | Mutable? |
|---|---|---|---|
| **L1 Raw evidence log** | every received item, byte-exact: stream messages, lists, manifests, snapshots, broker responses, plus Sentinel **tick records** (TTL expiry, the FINAL time trigger, staleness). Fields: raw bytes, raw_hash, received_at, log position, hash-chain link | the receive path; ticks by the clock service | never |
| **L2 Canonical version history** | one entry per (exec_id, version) claim derived from L1, carrying the R5 E-A fields **minus status**, plus `l1_ref` | the deterministic parser | never. A second, different claim for the same (exec_id, version) is a **new L2 entry**, not an edit |
| **L3 Disposition log** | records (disp_id, target: an L2 entry, item or reservation; from_status → to_status; cause: L1 ref or rule id; revision; t) | the pure fold | never. Status = the fold of dispositions in log order |
| **L4 Derived state** | registry, net_cum, R, B, S, F_d, F_d(β), position status, reservations, flags | the pure fold of L1 → L2 → L3 | recomputed; a cache |

**Determinism invariant (I9 extended).** L2, L3 and L4 are pure functions of (L1, model version, configuration).
- Stored L2 and L3 must be byte-identical to re-derivation.
- A model-version change produces a **new derivation lineage**, recorded as such. Older lineages are retained, never overwritten.

**Every status transition is an L3 record**, citing its cause:

| Transition | Cause cited |
|---|---|
| PENDING → APPLIED | the L1 evidence of the predecessor |
| APPLIED → CONFLICT (that version) | the conflicting L2 entry |
| PENDING(held) → IN_OPENING or DISMISSED | the L1 list or manifest |
| PROVISIONAL → FINAL | an L1 finality message, or an L1 tick under A-16 (H6) |
| ACTIVE → SUSPENDED → ACTIVE | the revision whose Π failed or held |
| PROVISIONAL → FINAL_VIOLATED | the L1 correction that arrived after FINAL (H6) |

Disposition never deletes. A DISMISSED item stays in L1 and L2, with its L3 history.

---

## H3. How a list and a snapshot jointly restore determinacy

**Definitions (DERIVED).**
- A list L for order o has a watermark ω = (e, W_o), a completeness claim, and entries (exec_id, per-version keys or only the current version).
- A snapshot S at β supplies F_b. **A snapshot never supplies execution-level information.** It cannot make ExecutionState determinate. It only gives the comparison target.
- x is **determinate at β** iff ExecutionState(x, β) is a singleton. This happens when the chain restricted to keys ≤ β is fully keyed or *bracketed*:
  - every unkeyed transition is known to lie wholly on one side of β;
  - a complete list with ω ≥ β brackets every transition it reflects as ≤ ω;
  - a complete list showing version k at ω proves v_{k+1} > ω (otherwise the list would include it).

**Joint restoration rule.** d at a snapshot S (at β) is determinate iff:
- (i) every execution is determinate at β;
- (ii) the stream is contiguous through β (H ≥ W, no holes);
- (iii) no PENDING or CONFLICT chain exists.

A list helps with (i) only if it is **complete** (it claims completeness through ω) and either carries per-version keys, or has ω ≥ β for every transition it collapses. A list without a completeness claim can add identities and keyed versions, but can neither bracket nor support absence conflicts.

**Example (COMPUTED).**
- P_open = 100. X: v0 = 10 at 501, v1 = 6 at 508. A complete list with ω = 510 shows v1 = 6, with keys. The stream is contiguous to 520. Snapshot at W = 515, F_b = 106.
- F_d(515) = 106 and d = 0, so the state is **determinate, RECONCILED**.
- Add the stream-delivered v2 = 3 (κ = ⊥). The list proves v2 > 510, but v2 may fall either side of 515.
- ExecutionState(X, 515) = {6, 3}, so F_d(515) ∈ {106, 103} and d ∈ {0, +3}: **MISMATCH**, with d_plus = 3.
- Determinacy returns only with a complete list with ω′ ≥ 515 that shows v2's status, a keyed later version of X, or a snapshot with W′ beyond a bracket that some evidence places v2 inside.

**Contradictory evidence.**

| Conflict | Result |
|---|---|
| List vs stream, same (exec_id, version), different payload | CONFLICT (new L2 entry, L3 record), so UNBOUNDED |
| List vs list, same ω, different content | CONFLICT |
| List older than the stream (R5 E-C case 9) | CONFLICT when the order cannot be established |
| List vs snapshot (both determinate, d ≠ 0) | **not a conflict**: a quantified MISMATCH (W1-T / W1-F worlds), D19 as conditioned |
| List completeness vs a stream execution keyed ≤ ω but absent from the list | CONFLICT |
| An incomplete list (no claim) contradicting nothing | additive identity and version information only |

---

## H4. M1 manifest completeness and M0 reconciliation across epochs

**M1 manifest completeness (candidate definition).** A manifest is complete through β0 when both hold:
1. **Scope:** every exec_id on the account and instrument with any transition keyed ≤ β0 is listed, *including* fully busted executions (current quantity 0). Listing busted ones is what lets later replays of them be recognized.
2. **Arithmetic corroboration:** either
   - (a) *inception-complete*: Σ of the listed signed current quantities = P_open; or
   - (b) *interval-complete over (β_s, β0]*: P_s + Σ = P_open, where P_s comes from an accepted snapshot at β_s.

   A mismatch rejects the manifest. Bootstrap then falls back to M0, recorded in L3.

This is **corroboration from the same source** (R2's R-02′), not independent evidence. A manifest whose sum matches can still be wrong in common mode (W1).

**M0 hold across an epoch change.**
- State: a class-2 held item h, an unknown execution keyed (e0, s ≤ W0).
- Epoch e1 begins. h stays held: it lives in e0's key domain, and the band stays UNBOUNDED.
- The e1 snapshot is **compared, and the comparison is recorded as an L3 note**: "consistent with h ∈ opening" when d = 0, or "inconsistent" otherwise. **The note does not resolve h.**
- Reason (DERIVED): d = 0 is consistent with h being inside P_open under W1-T. Under W1-F (a false snapshot), h could be a real, renumbered execution. That is the same logic as F-4 / D18 and V48: a later snapshot never clears an unexplained item.
- **Accepting a newer snapshot is therefore never a resolution**, whether or not it is related to h.

**Resolution paths (all L3 records, with h kept in L1 and L2):**
- (i) an authoritative list or manifest shows h's exec_id with κ ≤ β0, so h becomes **IN_OPENING** (F_d unchanged);
- (ii) it shows h does not exist, or duplicates a known execution, so h is **DISMISSED** with that cause;
- (iii) it shows h is real with a key > β0, which is an A-2″ violation: h is applied at its true key, and a **SEQ_CONTRACT** record is raised for review.

**No other exit.** If none arrives, h holds indefinitely (availability cost).

**Re-bootstrap (the only remaining escape, and a governance act).** An explicit, recorded action that:
- closes the current ledger, listing every unresolved item;
- opens a new ledger with a new P_open adopted from an accepted snapshot.
This is the *only* place adoption is allowed. It knowingly accepts the W1-F risk of the closed items, so it is a founder-authorized operation (**FD-18**), never automatic.

---

## H5. CA-15 under mixed and changing conditions (COMPUTED)

Reserve, recalled:
- buy order: F_min −= Σ PROVISIONAL buy quantities; if the order is terminal, F_max += Q − N;
- sell order: the mirror.
The reserve applies only while the order has a PROVISIONAL execution.

| Case | Setup | Model bounds | True worlds | Holds? |
|---|---|---|---|---|
| (a) mixed, terminal buy | opening 0; buy Q = 100, terminal, N = 60 (X1 40 FINAL, X2 20 PROV) | F_min = 60 − 20 = 40; F_max = 60 + 40 = 100 | X2 ∈ [0, 60], so P ∈ [40, 100] | **yes, tight**. A sell of 40 is ALLOWED; without the reserve A = 60, and a sell of 60 followed by a bust ends at −20 |
| (b) several delayed corrections of X2 (20 → 30 → 10 → …) | as (a) | as (a) | every value ∈ [0, 60] | **yes**: the reserve covers any sequence of quantity-only corrections within [0, Q] |
| (c) mixed, working buy | opening 100; buy Q = 100, working, N = 40 (X1 20 FINAL, X2 20 PROV); F_d = 140, R = 60 | U = 200; A_raw = 140 − 20 = 120 | unchanged: U 200, A 140. X2 busted: U 200, A 120. X2 → 50: U 200, A 170 | **yes**, A tight at the bust |
| (d) sell orders | the mirror of (a) to (c) | the mirror | — | yes (DERIVED by symmetry) |
| (e) transition to FINAL | (a), with X2 → FINAL | F_min = F_max = 60 | — | narrowing: allowed only under FD-15 (CX-31) |
| (f) FINAL with a correction pending | X2 has a PENDING CORRECT | — | — | **FINAL forbidden** while any correction or bust for x is PENDING or CONFLICT (rule F1) |
| (g) **delayed side flip** (CX-34, new) | (a); a CORRECT, delayed, restating X2 as a *sell* of 20 | F_min = 40 | true P = 60 − 40 = **20** | **no: escapes the reserve** |
| (h) opening executions under M0 | opening position made of unknown executions, some possibly provisional | no reserve possible | a bust of an opening execution → unbounded | **no** (CX-35, new) |

**Resolving (g).** A D26 identity change is a structural failure *on receipt*. While delayed, its effect is up to 2q. The options:
- (i) **A-14″ (environmental):** a broker never changes an execution's side, instrument or order through a CORRECT; it busts and re-reports instead. A bust is covered by the reserve, and a re-report on an unknown order is A-15.
- (ii) a reserve of 2q for side flips. Heavy, and only covers side.
- Recommended: (i), stated as an assumption and **FD-19**.

**Resolving (h).** Under M0, opening executions have no identities or finality status, so CA-15 cannot reserve against their busts.
- Options: require M1 with a per-entry finality status; or adopt the **A-16b bootstrap clause**: S0 is accepted only if it is taken at least T_f + L_n + σ after the last pre-bootstrap execution. That needs a broker statement of last execution time, which is UNVERIFIED.
- Otherwise opening busts are **excluded only by assumption**. Folded into FD-16.

**Rule F1 (candidate).** An execution may become FINAL only if:
- no L2 entry for it is PENDING or CONFLICT;
- its order has no CONFLICT;
- the stream health condition of H6 holds over its finality interval.

---

## H6. The basis for FINAL under FD-15

**Option (a): evidence-based finality.**
- **Basis:** an L1 item of kind FINALITY(exec_id, version), an authoritative broker statement that this version can no longer be corrected or busted, for example cleared or locked.
- **Scope:** that exec_id at that version only.
- **Limits:**
  - it is a broker claim (A-7, 2.8); integrity, authenticity and corroboration apply;
  - it does not cover the *delivery* of a correction issued before the statement (L1 order resolves that: a correction received before the FINALITY item is applied first).
- The widen-only principle stays strict, since the narrowing is caused by evidence.
- Broker capability: **UNVERIFIED**.

**Option (b): time-based finality (A-16).**
- **Basis:** FINAL at t_final(x) = received_at(x_v) + T_f + L_n + σ, evaluated by an L1 tick record. Here:
  - **received_at** is Sentinel's receipt of the version being finalized. Execution precedes receipt, so this is a *conservative* stand-in for the unknown broker execution time;
  - **T_f** is the broker's correction window, measured from execution on the broker's clock, for **the declared correction classes C_f** only;
  - **L_n** is a bound on latency from the broker's correction action to Sentinel's receipt, *while the stream is healthy*;
  - **σ** is a bound on broker-to-Sentinel clock skew.
- **Soundness (DERIVED, CONDITIONAL on T_f, L_n, σ and C_f being true).** Any correction of a class in C_f is issued by t_exec + T_f on the broker's clock. On Sentinel's clock that is at most t_exec + T_f + σ, and it is received by then plus L_n, which is at most received_at + T_f + L_n + σ = t_final. So at t_final, any such correction has already been received.
- **Stream health condition.** L_n holds only while delivery works. FINAL is therefore *deferred* whenever, at any point in [received_at, t_final]:
  - the status was GAP, AWAITING-BEHIND, UNKNOWN or SEQ_CONTRACT;
  - an epoch change occurred;
  - a heartbeat or liveness gap exceeded a declared bound.
  A deferred FINAL is re-timed from the end of the unhealthy interval.
- **Scope limits (stated, not hidden):**
  - correction classes outside C_f (late allocations, regulatory or legal reversals, corrections days later) are **not covered**; executions remain exposed to them, which is environmental (A-12″);
  - L_n cannot be measured from inside a healthy stream: a stuck broker queue looks healthy. **L_n is an assumption (UNVERIFIED)**, never an established property;
  - T_f varies by venue, product and correction type, and is UNVERIFIED for any broker.
- **The widen-only principle is amended** (this is FD-15(b)). "A bound may also narrow by a PROVISIONAL → FINAL disposition under A-16, recorded in L3, citing the L1 tick and the parameter set (T_f, L_n, σ, C_f) pinned by the configuration hash. No other time-based narrowing is permitted."

**A correction arriving after FINAL (both options).**
- The correction is applied: it is evidence, so I8 detection runs and OVER_RESERVED or OVER_LIMIT may result.
- An L3 record **FINAL_VIOLATED** is made for x.
- A **structural flag FINALITY_ASSUMPTION_FAILED** is raised. It blocks both sides until reviewed, because the declared parameters have been shown false for at least one case (**FD-17**: block, recommended, or detection only).

---

## Candidate amendment summary (affected sections only)

| Section | Change |
|---|---|
| §2.2 | Version history uses **admissible cuts** (H1), replacing R5's "before/after per transition"; **ExecutionState returns a set**; F_d(β) is a product range; d_max and d_min formulas |
| §2.2 (new) | **Evidence layers L1–L4** (H2); status moved to L3; derivation lineages |
| §2.4.1 item 6 | Determinacy and the joint list + snapshot rule (H3); the contradiction table |
| §2.2 / bootstrap | **M1 completeness** (scope plus arithmetic corroboration); M0 hold resolution paths; snapshots never resolve holds; **re-bootstrap** as a governance act (H4) |
| §2.4.3 (CA-15) | Rule F1; cases (g) and (h) recorded; A-14″ (FD-19); A-16b bootstrap clause |
| §2.11 | **A-16** with the parameters (T_f, L_n, σ, C_f), the stream-health deferral, scope limits; **A-14″**; A-16b |
| §2.4 widen-only | Amendment text under FD-15(b) |
| §2.8 | Structural flags FINALITY_ASSUMPTION_FAILED and FINAL_VIOLATED |
| §2.5 | I9 extended (layer determinism); I10 restated over L1 and L2; I13 (no impossible cut contributes to any bound) |
| §2.10 | V84 (CX-36, admissible cuts); V85 (H3, both variants); V86 (M1 sum mismatch → M0); V87 (an M0 hold across an epoch, the snapshot note does not resolve); V88 to V91 (H5 cases a, c, e, f); V92 (CX-34); V93 (H6 deferral across a GAP); V94 (a correction after FINAL → FINALITY_ASSUMPTION_FAILED) |
| §5.7 | Oracle enumerates admissible cuts; known-wrong mutant: independent placement; layer re-derivation byte-equality; FINAL deferral × stream-health intervals |

---

## Disposition

| Item | Disposition | Evidence | Remaining dependency |
|---|---|---|---|
| H1 admissible histories | Resolved; the R5 defect corrected (CX-36) | DERIVED; COMPUTED | none technical |
| H2 evidence layers | Resolved | DERIVED | none technical |
| H3 joint determinacy | Resolved; snapshots never create determinacy | DERIVED; COMPUTED | broker lists with completeness claims and keys (UNVERIFIED) |
| H4 M1 / M0 across epochs | Resolved; holds never cleared by a snapshot; re-bootstrap is explicit | DERIVED | FD-16, FD-18; manifest availability (UNVERIFIED) |
| H5 CA-15 | Holds for quantity-only changes (COMPUTED); **fails for delayed identity changes (CX-34) and M0 opening busts (CX-35)** | COMPUTED; DERIVED | FD-19 (A-14″), FD-16 |
| H6 basis for FINAL | Formalized for (a) and (b); soundness of (b) CONDITIONAL on T_f, L_n, σ and C_f | DERIVED | FD-15, FD-17; every parameter UNVERIFIED |

**Founder decisions (governance only):**
- **FD-15:** (a) evidence-based finality, or (b) time-based A-16 with the amended widen-only principle.
- **FD-17:** whether a correction arriving after FINAL blocks both sides (recommended) or is detection only.
- **FD-18:** authorize re-bootstrap as an explicit, recorded operation for unresolvable holds.
- **FD-19:** adopt A-14″ (no identity-changing CORRECT from the broker), or reserve 2q.
- **FD-14 and FD-16** carry forward, now informed by CX-34 and CX-35.

**Readiness.**
- Internally coherent as candidate text: DERIVED.
- Within the proposed contracts (A-2″, A-11″, A-12″, A-14″, A-15, A-16 or finality evidence), no false-authorization path was found: DERIVED, not executed.
- CX-34 and CX-35 are excluded **only** by A-14″ and by M1 or A-16b.
- Ready for hostile review. Suggested targets:
  - the product-range d over many chains together with CA-15 widening;
  - the stream-health deferral (can a healthy-looking stream hide an L_n violation? **Yes, by construction**: that is why L_n is UNVERIFIED);
  - FD-18 abuse cases.
- **No implementation, oracle execution, broker contact, paper or live trading is authorized.**

*Agreement among reviewers is not independent verification. Only integer arithmetic and one small enumeration were executed (COMPUTED).*
