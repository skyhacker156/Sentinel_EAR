# EAR v0.1 Rev 3.2 Candidate: Closure Pass on Challenges E, F and G

SPECIFICATION REVIEW ONLY. No freeze, implementation, oracle, broker, paper or live work is authorized.
Reviewer: Claude (Specification Lead / ARBITER). Date: 2026-11-24 (ET).
Prior documents: R1 `39c224a3…`, R2 `e53d96ef…`, R3 `1aef01e9…`, R4 (candidate clarifications) `d5967e55…`.

**Baseline hash discrepancy in the dispatch.** The dispatch quotes `dd9d87f76f01134e…`. The frozen Rev 3.1 artifact is **`dd9d87f76b01134e084827b0202c73c52fccb2b86f21a176a6b6e551241fa239`**: the tenth hex character is `b`, not `f`. This was verified by `sha256sum -c` on fresh clones of commit d4c9e66 in earlier passes. This response is against the `…76b…` artifact. Please correct the dispatch template.

**Labels.**
- **DERIVED**: follows from the stated definitions.
- **COMPUTED**: integer arithmetic executed by a throwaway Python script using Rev 3.1 §2.4: F_max = F_d + d_plus + Q3_buy + Q3_unk; F_min = F_d − d_minus − Q3_sell − Q3_unk; U = F_max + B; A_raw = F_min − S; d = F_b − F_d(W). It establishes the arithmetic only.
- **ASSUMED**, **CONDITIONAL**, **UNVERIFIED**, **UNBOUNDED**: as before.

No oracle exists. The tables are hand-derived.

---

## 1. Technical response

### Challenge E: registry versus immutable version history

**Disposition: accept; R4's CA-1 is corrected.**
- R4 said "F_d is computed only from the registry and the opening item", with the registry holding only current versions. That is wrong for every boundary β below the latest transition.
- R4's own F_d(β) formula summed transitions by key. That formula is right, but it needs a history the registry does not hold. The two statements contradicted each other.
- The fix: the **version history** is the source of truth, and the registry is a derived cache.

**E-A. Version history (immutable, append-only; one chain per exec_id).** Each entry carries the fields below. Who vouches for each field matters, so the last column marks it: **[B]** is a broker claim, **[S]** is Sentinel-generated metadata, authoritative only about Sentinel's own processing, and **[D]** is derived.

| Field | Content | Origin |
|---|---|---|
| account_id | the configured account | [S] |
| exec_id | the accounting identity | [B] |
| order_id | or null | [B] |
| instrument, side | | [B] |
| version | 0 for NEW; previous + 1 for each later transition | [S] (validated against the claimed prior_version) |
| kind | NEW, CORRECT or BUST | [B] |
| prior_version, prior_qty | null for NEW | [B] (D27) |
| qty | resulting quantity: 0 for BUST, the replacement value for CORRECT | [B] |
| signed_delta | sign(side) × (qty − prior qty) | [D] |
| key κ | (epoch, broker_seq), or ⊥ explicitly | [B] |
| source | STREAM(event_id), LIST(list_id, entry), or BOOTSTRAP_MANIFEST(manifest_id, entry) | [S] |
| raw_hash, received_at, log_position, revision | | [S] |
| status | APPLIED, PENDING(prerequisite), CONFLICT, IN_OPENING (represented in P_open, so delta not added), or DISMISSED | [S] |
| conflict_ref | the other entry it conflicts with | [S] |

Broker claims are never authoritative about the economic truth (A-7, 2.8). Sentinel metadata is authoritative only about what Sentinel received and did.
The **registry** is the last APPLIED or IN_OPENING entry per exec_id. It is a cache that can always be recomputed from the history. It is **never** used to evaluate F_d(β) for any β other than "now".

**E-B. Reconstruction (DERIVED).**
- The chain must keep its keys in order: κ(v_i) < κ(v_{i+1}) whenever both are present. A transition whose key is at or below its predecessor's key is a CONFLICT.
- **ExecutionState(x, β)**, defined for β ≥ β0:
  - **UNRESOLVED** if x's chain has any PENDING or CONFLICT entry that matters at β.
  - Otherwise, let v* be the last entry with κ(v*) ≤ β:
    - **ABSENT** (contributes 0) if there is no such entry, or if v* is IN_OPENING (it is already inside P_open);
    - **QTY(signed qty of v*) minus QTY(IN_OPENING anchor, if any)** if v* is APPLIED.
  - **AMBIGUOUS({…})**: an entry with κ = ⊥ has unknown placement relative to β, so both "before" and "after" are enumerated, extending the inclusion choices of Rev 3.1 §2.2 from executions to version transitions.
- **F_d(β) = P_open + Σ_x ExecutionState(x, β)**.
  - AMBIGUOUS contributions widen d over every choice.
  - Any UNRESOLVED contribution makes the band UNBOUNDED (T2-U).
- **F_d (now) = F_d(β = +∞).**
- Telescoping: the sum over x of the effective versions equals P_open plus the sum of signed_delta over transitions with κ ≤ β. So this is R4's event-sum formula, now with a defined data source.

**E-C. The ten cases.**

| # | Case | Treatment | History | Registry | F_d | F_d(β) |
|---|---|---|---|---|---|---|
| 1 | correction received after the snapshot boundary | APPLIED at its own κ > β | +1 entry | updated | changes | **unchanged for β < κ** |
| 2 | corrections out of order | Sequenced: buffered in key order (GAP until contiguous; R-01′). Unsequenced: prior_version > current → **PENDING** until the predecessor arrives; prior_version < current → CONFLICT (stale, V49); equal but prior_qty mismatched → CONFLICT. *This refines D27(4): "ahead" is pending, "behind" is a conflict* | entry PENDING | unchanged until resolved | unchanged | UNRESOLVED while pending |
| 3 | several corrections | chain v0 → v1 → v2, each at its own κ | +1 each | last | last | effective version at β |
| 4 | bust, then a correction | allowed as a version transition (qty 0 → q, "reinstatement"), subject to the net_cum ∈ [0, order qty] check (E13). A terminal order keeps R = 0 (I7). *Alternative: treat it as a structural failure. Not adopted; replacement semantics already cover it* | +1 | updated | changes | effective at β |
| 5 | duplicate delivery of the same version (same exec_id, version, payload) | idempotent; duplicate counter only | unchanged | unchanged | unchanged | unchanged |
| 6 | same exec_id and version, conflicting payload | **CONFLICT**; both payloads retained | entry CONFLICT | unchanged | unchanged | **UNRESOLVED**, so UNBOUNDED |
| 7 | correction before its NEW | PENDING (V31) | entry PENDING | — | unchanged | UNRESOLVED |
| 8 | list reports a newer version than the stream | If the list gives every intermediate version with keys, they are appended as entries (source LIST). If it gives only the current version k: when k = current + 1, one transition with unknown key (κ = ⊥ within (stream κ, list watermark]) → AMBIGUOUS for β inside that window. When k > current + 1, the intermediate quantities are unknown → **UNRESOLVED for β below the list watermark**. In both cases, a snapshot with W ≥ the list watermark restores determinacy (the effective version there is v_k) | +entries | updated to v_k | changes | ambiguous or unresolved inside the window |
| 9 | list reports an older version | list watermark ≥ κ(stream's later version) → CONFLICT; list watermark < κ → stale, recorded, no change; κ unknown → **CONFLICT** (two broker claims disagree and cannot be ordered) | entry recorded | unchanged | unchanged | CONFLICT → UNBOUNDED |
| 10 | incomplete history (version numbers skipped, or a reference to a version never received) | PENDING; **never treated as complete** | entry PENDING | unchanged | unchanged | UNRESOLVED |

**E-D. Counterexample E-1 (COMPUTED).**

Setup: P_open = 100 at β0 = (e0, 500). Our working buy order O1, quantity 30. No sells. B = R(O1).

| Step | Evidence | History (X1, X2) | Registry | F_d | R = B | U | F_d(505) | F_d(506) | Snapshot comparison | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | (501) NEW X1 10; (502) ack; (503) NEW X2 10; (504), (505) acks | X1: v0 @501 = 10. X2: v0 @503 = 10 | X1 10, X2 10 | 120 | 10 | 130 | 120 | — | S1 = (e0, 505), F_b = 120: d = 0 | RECONCILED |
| 2 | (506) CORRECT X2, prior v0 / 10 → 6 | X2: v0 @503 = 10, **v1 @506 = 6** (appended; v0 not rewritten) | X1 10, X2 6 | 116 | 14 | 130 | **120** (history) | 116 | against S1: d = 120 − 120 = 0 | AWAITING |
| 2′ | *naive: F_d(505) from the current registry* | — | — | 116 | 14 | — | 116 | — | d = +4, so MISMATCH: U = 134, A_raw = 116 | spurious MISMATCH; increases blocked |
| 3 | snapshot S2 = (e0, 506), F_b = 116 | unchanged | unchanged | 116 | 14 | 130 | 120 | 116 | d = 116 − 116 = 0 | RECONCILED |

- **The history is not rewritten.** After step 2, F_d(505) still reconstructs to 120 and F_d(506) to 116.
- In this instance the naive registry approach fails conservatively (a spurious MISMATCH, so availability). But it disagrees with the oracle's world values (which use F_d(W)), so it is a **spec-coherence defect**, not merely an availability cost. In general it gives no guarantee: under D26-type ambiguity the naive value has no defined meaning (DERIVED).

**E-E. Reduced-capability behaviour.** The broker may not supply exec_id, version, keys or full chains (UNVERIFIED for any broker).
- With no exec_id: out of contract (A-11″, FD-8): a structural failure on the affected side.
- With an exec_id but no keys on corrections: every transition is κ = ⊥, so AMBIGUOUS at every β. Comparisons widen d by |delta| per transition, which usually means MISMATCH and increases blocked.
- Lists without intermediate versions: case 8, UNRESOLVED windows.
- **Missing history never becomes a complete record:** PENDING and UNRESOLVED are the only outcomes for gaps in a chain.

**Acceptance criteria:** all six met (DERIVED). Conditional on A-11″ for the full capability; the reduced-capability rules apply otherwise.

---

### Challenge F: delayed corrections and busts under A-15

**Disposition: accept.** **A-15 does not address finality.** It is about who can create executions, not whether a reported execution is final. Execution identity is not execution finality. R4 did not claim otherwise, and this response must not imply it either (DERIVED).

**F-1: delayed bust of a buy fill (COMPUTED).**
- Start: position 0. A known buy O1 of 50 fills (X1), and X1 is received and applied: F_d = 50, RECONCILED, A = 50.
- The broker busts X1, and the notification is delayed.
- A sell of 50 is evaluated and committed: A = 50, so ALLOW. It is then consumed, submitted and executed.
- Actual position: 0 − 50 = **−50**, a short in the long-only envelope.
- When the bust arrives: F_d = 50 − 50 − 50 = −50. The next snapshot is negative, giving a structural failure (V54) and UNRESOLVED.
- **This is a false authorization** under the Rev 3.1 rules and the R1–R4 candidates alike.

**F-2: delayed upward correction of a sell (COMPUTED).**
- Start: position 100. Our sell order O2, quantity 100, filled 40 and was then cancelled at cum 40 (terminal, R = 0). The model shows 60 and A = 60.
- The broker corrects the fill from 40 to 70, and the correction is delayed.
- A sell of 30 is ALLOWED. The true position afterwards is 100 − 70 − 30 = **0**: on the boundary, not past it.
- The model would ALLOW up to 60. A sell of 60 leaves a true position of **−30**: the lower bound is violated.
- *Variant: O2 still working* (R = 60 in S). A_raw = 60 − 60 = 0, so every sell is DENY. The correction moves quantity from R into the position, exactly like an unreported fill, so W4 covers it.

**F-3: correction after commit, before consume (DERIVED).**
- F-1 with the reservation still ACTIVE when the bust arrives: A_raw = 0 − 50 = −50, OVER_RESERVED is raised, and R-15″ moves the reservation to **SUSPENDED** in the same revision. `consume` is refused. **Controlled within the model.**

**F-4: after submission or broker acceptance (DERIVED).**
- Suspension cannot recall an order.
- *Submitted, not accepted:* only a cancel request is possible (authority is G-07), and it is not guaranteed to win.
- *Accepted, not executed:* the same.
- *Executed:* irreversible. Only an offsetting trade could correct it, which is G-06 and out of scope.
- What v0.1 guarantees: OVER_RESERVED or OVER_LIMIT in the revision that applies the bust or correction, and no new authorization or consumption while it holds.

**F3. What W4 actually guarantees (DERIVED).** For each working order o (including UNKNOWN; and CANCEL_PENDING via W5), any unreported fill x in [0, R(o)] leaves U and A_raw conservative. This works because moving quantity from R into the position is neutral to U for a buy and to A_raw for a sell (I1a, I1b). W4 is about **fills inside R**. It is not about finality.

| Delayed event | Covered? | Why |
|---|---|---|
| initial execution report, known working order | **yes** (W4) | a fill inside R |
| partial fill | **yes** (W4) | cumulative ≤ R |
| upward correction on a **working** order, within R | **yes** | the same as an unreported fill |
| upward correction on a **terminal** order, or beyond R | **no** | R = 0; F-2 |
| downward correction (either side) | **no** | removes position that was never reserved |
| bust | **no** | a downward correction to 0; F-1 |
| several corrections | per net effect, by the rows above | — |
| correction to a pre-bootstrap execution | **no**; also an identity problem | Challenge G |
| correction received after authorization, before consume | **controlled** | R-15″ (F-3) |
| correction received after submission | **not controlled** | F-4 |

**F4. Candidate control mechanisms (none is assumed to be available).**

| Mechanism | Guarantees | Does not guarantee | Broker capability needed | Cost | Representable in EAR? |
|---|---|---|---|---|---|
| 1. Broker finality window T_f (no bust or correction after T_f) | executions are final after T_f *at the broker* | timely *notification* of a bust issued inside T_f (latency is a separate matter, A-12″) | a documented, enforced policy (UNVERIFIED for any broker) | reductions wait T_f plus a latency bound | as an assumption, A-16 |
| 2. **Provisional status with an uncertainty reserve** | the bounds stay conservative against any bust or correction allowed by the contract while an execution is provisional | that finality is ever reached; corrections beyond the order quantity (those are excluded by contract and are a CONFLICT on receipt) | a *finality signal*: either broker evidence, or A-16 | fills not usable for reductions until final; buys blocked after sells, symmetrically | **yes, mechanically** (CA-15 below) |
| 3. No consume until finality | a consumption never relies on a provisional fill | authorization is still computed on provisional quantities | as 2 | as 2, but weaker | yes; subsumed by 2 |
| 4. Broker-side position or no-short barrier | the broker rejects a sell beyond *its own* position at that moment | busts processed after our sell executes; the upper limit L; broker consistency | a cash or no-short account (UNVERIFIED) | rejects | external only; the model records T07 rejections. Not part of the bound |
| 5. Dedicated sub-account | supports A-15 | finality | account structure | operational | no change to the model |
| 6. Assume no correction after point T | the same as 1, but stated as a bare assumption | anything, if the assumption is false | none | none | as A-16 |

**The mechanism-2 reserve (DERIVED).** For each order o with any provisional applied execution:
- **Buy order:**
  - F_min −= the sum of provisional buy quantities on o (risk of a bust or downward correction);
  - if o is terminal, F_max += (Q_o − N_o) (risk of an upward correction up to the order quantity).
- **Sell order:**
  - F_max += the sum of provisional sell quantities on o;
  - if o is terminal, F_min −= (Q_o − N_o).
- **Working orders** need no upward term, because R already holds it (W4).
- The reserve only ever *widens* the bounds.

Applied to the counterexamples (COMPUTED):
- F-1: F_min = 50 − 50 = 0, so A = 0 and the sell of 50 is DENY.
- F-2: terminal, Q − N = 60, so F_min = 60 − 60 = 0 and A = 0. DENY.

**F5. Disposition of each path.**

| Path | Disposition |
|---|---|
| Bust or downward correction arriving before consume | **Mechanically controlled** (R-15″) |
| Delayed bust or downward correction of a provisional execution, before authorization | **Conservatively bounded**, *if* mechanism 2 is adopted (FD-14). Otherwise **excluded only by A-12″**, extended to busts and corrections (environmental) |
| Upward correction on a terminal order, within the order quantity | as the row above |
| Correction beyond the order quantity | **Excluded by contract**: net_cum ∈ [0, Q_o] (A-14 / E13). A CONFLICT on receipt |
| Any correction or bust after finality | **Excluded by A-16** (environmental), or by broker evidence (UNVERIFIED) |
| Any correction or bust after submission or acceptance or execution | **Explicitly unsupported**: detection only, no recall |
| Correction to a pre-bootstrap execution | **UNBOUNDED** under bootstrap mode M0; controlled under M1 (Challenge G) |

**F6. What stays reversible at each stage (DERIVED).**
- Evaluation: no authority exists yet.
- Committed reservation: reversible internally (suspension, release, expiry).
- Consumed: the internal capability is spent. Whether the order has left is an adapter (G-07) matter.
- Submitted or accepted: only a cancel *request*. Not reversible by the model.
- Executed: irreversible.

**Acceptance:** the candidate no longer treats initial reports as final without a stated basis (CA-15, A-16). Identity and finality are separated (DERIVED).

---

### Challenge G: classifying pre-bootstrap evidence

**Disposition: accept.** R3 and R4 collapsed five different situations into SEQ_CONTRACT. The candidate now separates them and introduces two **bootstrap modes**:
- **M0, position-only:** the bootstrap snapshot gives P_open and nothing more. No execution identities.
- **M1, attested manifest:** an authoritative execution manifest complete through β0, listing for each execution its exec_id, κ, identity fields, current version and quantity. Its entries enter the history as IN_OPENING. They contribute nothing to F_d, because they are inside P_open, but they anchor later transitions. Whether any broker supplies one is UNVERIFIED.

**A useful fact (DERIVED).** Every accepted snapshot has W ≥ W0. So reconstruction is only ever needed at β ≥ β0, and history before β0 matters only to the extent that it anchors later transitions. The manifest needs current versions, not full pre-β0 chains.

**G-A. Transition table.**

| Class | Mode | Disposition | Registry | History | F_d | F_d(β) | Sequence status | Blocks | Reconciliation resolves? |
|---|---|---|---|---|---|---|---|---|---|
| 1. Known replay (exec_id, version and payload match the manifest; κ ≤ β0) | M1 | idempotent replay | no | duplicate counter only | no | no | no | none | n/a |
| | M0 | cannot be recognized, so it is class 2 | | | | | | | |
| 2. Unknown old execution (κ ≤ β0, exec_id unknown) | M1 | **CONFLICT**: the manifest claimed completeness | no | entry CONFLICT | no | no | structural | **both** | yes, by an authoritative re-attestation (manifest or list) |
| | M0 | **held** as SEQ_CONTRACT evidence: neither added nor discarded | no | entry PENDING (held) | no | no | structural | **both** | yes. An authoritative list showing the execution inside the opening reclassifies it IN_OPENING (no F_d change). A list showing it never existed dismisses it |
| 3. Correction or bust (κ > β0) of an execution in the opening | M1 | validated against the manifest anchor (identity, prior_version, prior_qty) and applied, or CONFLICT / D26 | yes | anchor + new entry | yes, by delta | yes, for β ≥ κ | normal | per the outcome | n/a |
| | M0 | **PENDING, T2-U** (V31/V55): with no anchor, identity changes (D26) cannot be checked, so its effect is unbounded | no | entry PENDING | no | UNRESOLVED | — | **both** | yes. A per-order list or manifest supplies the anchor; the entry is then re-validated |
| 4. Contradictory replay (same exec_id and version as an entry, different side or quantity) | M1 | **CONFLICT** against the manifest; both payloads retained | no | entry CONFLICT | no | UNRESOLVED | structural | **both** | yes, by an authoritative resolution |
| | M0 | detectable only against an earlier post-bootstrap delivery of the same version (then CONFLICT); otherwise it is class 2 | | | | | | | |
| 5. Identity known, original history unavailable (manifest or list gives the current version only) | M1 | anchor at the current version, as IN_OPENING; no earlier versions are needed, because β ≥ β0 | anchor | anchor entry | no | no | — | none | n/a |

**G-B. Counterexamples (COMPUTED where there is arithmetic).** Opening: P_open = 100 at β0 = (e0, 500). Under M1 the manifest lists X0 (buy 100, v0, κ = (e0, 480)).
- **G-1, known replay.** X0 v0 arrives again at κ = (e0, 480) with the same payload.
  - M1: idempotent, F_d = 100. It is not added twice because X0 is IN_OPENING, so its delta is never added to P_open.
  - M0: held (class 2), F_d = 100, both sides blocked until reclassified.
- **G-2, unknown old execution.** X9 (a sell of 10) arrives at κ = (e0, 490) with no identity on record.
  - *Naive add:* F_d = 90 against a true 100, double counting, since P_open already reflects X9 by watermark exactness.
  - *Naive discard:* silent. If A-2″ was violated (an unlabelled renumbering), X9 is real and new, and discarding it omits a sell of 10.
  - The candidate does neither. M0: held, both sides blocked, F_d = 100 kept. M1: CONFLICT.
- **G-3, pre-bootstrap correction.** A CORRECT for X0 at κ = (e0, 510), prior v0 / 100 → 80.
  - M1: validated against the anchor and applied. F_d = 80, F_d(β ≥ 510) = 80, F_d(β < 510) = 100.
  - M0: PENDING, so UNBOUNDED.
  - *Why not apply the delta from the CORRECT's own fields?* Because identity cannot be checked. Suppose the CORRECT restates X0 as a *sell* of 100 (a D26 identity change). The fields give qty − prior_qty = 0, so a naive F_d = 100, against a true 100 − 200 = **−100**. The model **cannot reconstruct the corrected position under M0** and must enter an unresolved state.
- **G-4, contradictory replay.** X0 v0 arrives with quantity 90. M1: CONFLICT. F_d stays 100 (not applied). Both payloads are retained, and both sides are blocked until an authoritative resolution.

**Availability cost of incomplete pre-bootstrap history (M0), DERIVED:**
- any replay of pre-bootstrap history blocks both sides until a list resolves it;
- any correction or bust of an opening execution is UNBOUNDED until an anchor is supplied.
How often these occur is UNVERIFIED (it depends on the broker).

**Acceptance:** all four criteria met (DERIVED).

---

## 2. Counterexample index (all in section 1; arithmetic COMPUTED with the formulas in the header)

- E-1 (steps 1–3, plus the naive 2′)
- F-1, F-2 (sells of 30 and 60, plus the working variant), F-3
- G-1 to G-4

**New in this pass:**

| ID | What it shows |
|---|---|
| CX-29 | F-2 with a sell of 60 (−30) |
| CX-30 | E-1 step 2′, the naive registry F_d(β) |
| CX-31 | the finality release conflicts with the widen-only principle (section 4) |
| CX-32 | G-3, a side-changing pre-bootstrap correction under M0 |
| CX-33 | case 8, a list that skips versions, giving an ambiguity window |

---

## 3. Candidate amendment language (affected sections only; not in force)

**Replacement text**
- **R4 CA-1, the sentence "F_d is computed only from the registry and the opening item"** → "F_d(β) is computed from the immutable version history and the opening item (§2.2 'Version history'). The registry is a derived cache of current versions, used only for β = now."
- **Rev 3.1 §2.2 'Execution versions and corrections', item 4 (D27 prior version)** → "If prior_version exceeds the current version, the CORRECT is held PENDING until the predecessor is applied. If it is lower, or equal with a different prior_qty, the result is a structural conflict."
- **Rev 3.1 §2.6.3 'Identity and economic uniqueness'**: add "Idempotency is by (exec_id, version, canonical payload). The same (exec_id, version) with a different payload is a structural conflict."

**New definitions (§2.2)**
- **Version history** (fields as in E-A, with origin markers [B], [S] and [D]).
- **ExecutionState(x, β)** and **F_d(β) = P_open + Σ_x ExecutionState(x, β)** (E-B).
- **Bootstrap modes M0 and M1**; manifest entries carry status IN_OPENING.
- **PROVISIONAL / FINAL** status of an applied execution (CA-15).

**New assumptions (§2.11)**
- **A-12″ (extended):** "…every execution, **correction and bust** that occurred at the broker before evaluation time t…"
- **A-16 (finality, E):** a correction or bust cannot occur for an execution after it becomes FINAL. FINAL is reached on authoritative broker finality evidence, or (FD-15 option b) at received_at + T_f + L_n, where T_f is the broker's finality window and L_n a notification-latency bound. Both are parameters. Not established for any broker.

**New invariants (§2.5)**
- **I10 (history immutability):** history entries are only ever appended. Status changes are new log records. The effective version at any β is a function of the history and β alone.
- **I11 (single quantity source):** for every exec_id, F_d(β) includes exactly one effective version, or an explicit AMBIGUOUS or UNRESOLVED result. Stream, list and manifest are evidence paths into the same chain.
- **I12 (finality reserve), if FD-14 is adopted:**
  - while any execution of order o is PROVISIONAL, the reserve of CA-15 applies;
  - the reserve only widens;
  - releasing it is the PROVISIONAL → FINAL transition, a logged revision step that triggers R-15″ re-evaluation.

**CA-15 (new §2.4.3, if FD-14 is adopted)**
> The finality reserve per order o, with Q_o the order quantity and N_o its net_cum:
> - buy: F_min −= Σ PROVISIONAL buy qty on o; and, if o is terminal, F_max += Q_o − N_o;
> - sell: F_max += Σ PROVISIONAL sell qty on o; and, if o is terminal, F_min −= Q_o − N_o.
> Working orders carry no upward term, because R covers it (W4).

**New vectors**
- V74: E-1 (steps 1–3), checking F_d(505) and F_d(506) after the correction.
- V75: F-1, without and with CA-15.
- V76: F-2, sells of 30 and 60; terminal and working variants; with CA-15.
- V77: F-3, suspension.
- V78 to V81: G-1 to G-4, each under M0 and M1.
- V82: case 8, a list that skips versions.
- V83: case 2, an unsequenced CORRECT arriving ahead of its predecessor.

**New test obligations (§5.7)**
- history immutability: replay the log and check every F_d(β) for β in the set of observed keys;
- every pair of delivery paths (stream, list, manifest) × every version relation (=, +1, +k, −1);
- the ten E cases;
- the provisional → final transition × R-15″ reactivation;
- every G class under each bootstrap mode;
- the oracle domain extended so that each PROVISIONAL execution may be busted, or corrected anywhere within [0, Q_o].

---

## 4. Cross-interaction analysis (DERIVED)

| Pair | Finding |
|---|---|
| Version history × lists | Lists append entries (source LIST) to the same chain. Skipped versions create an ambiguity or unresolved window that only a snapshot with W ≥ the list watermark closes (CX-33). A list is never additive (I11) |
| Version history × bootstrap | IN_OPENING anchors. Reconstruction only for β ≥ β0. M0 has no anchors, so corrections of opening executions are UNBOUNDED |
| Corrections and busts × suspension | Any applied correction or bust is a revision step, so Π is re-evaluated. With CA-15, PROVISIONAL → FINAL *narrows* the bounds and may reactivate reservations (never suspends them) |
| Corrections and busts × commit and consume | Both re-evaluate Π at their own t_L, including the reserve. A bust received after t_L of consume is F-4 (not controlled) |
| Corrections and busts × A-12 and A-15 | Delayed busts and corrections are A-12″ (extended), not A-15. A-15 is irrelevant to finality |
| Pre-bootstrap corrections × identity | Resolved only under M1, or once an anchor list arrives. Otherwise T2-U |
| Finality × exposure bounds | **New conflict, CX-31.** Rev 3.1's widen-only principle (§2.4, R31-07') forbids narrowing by "timeout". A time-based FINAL (A-16 with T_f + L_n) is narrowing by timeout. Either finality requires broker *evidence* (strict; capability UNVERIFIED), or the widen-only principle is amended to allow narrowing by a declared environmental assumption. That is a governance choice: **FD-15** |
| CA-15 × availability | With CA-15, a buy fill cannot back a reduction until FINAL, and a sell fill cannot back an increase. Combined with M0, this may leave almost nothing authorizable. To be measured, not asserted |

**New counterexamples:** CX-29 to CX-33 (section 2). **No new false-authorization path inside the contracts**, as amended here (DERIVED).

---

## 5. Updated disposition

| Issue | Disposition | Evidence level | Remaining dependency |
|---|---|---|---|
| E: version history | Resolved: history is the source of truth, the registry a cache; ExecutionState and F_d(β) defined; ten cases tabulated | DERIVED; E-1 COMPUTED | A-11″ (broker ids, versions and keys: UNVERIFIED); reduced-capability rules defined |
| F: correction and bust finality | Bounded, but not closed. Pre-consume: controlled (R-15″). Pre-authorization: conservatively bounded under CA-15 (FD-14); otherwise excluded only by A-12″ (extended). After finality: A-16 or broker evidence. After submission: unsupported | DERIVED; F-1 and F-2 COMPUTED | FD-14, FD-15; broker finality (UNVERIFIED); notification-latency bound (UNVERIFIED) |
| G: pre-bootstrap classes | Resolved: five classes × two modes; no double counting, no silent discard | DERIVED; G-2 and G-3 COMPUTED | FD-16 (bootstrap mode); manifest availability (UNVERIFIED) |
| Cross-interaction | Consistent except CX-31 (finality versus widen-only), which is now explicit | DERIVED | FD-15 |

---

## 6. Founder decisions (genuine governance choices only)

- **FD-14:** adopt the finality reserve CA-15. The availability cost is real: fills cannot back opposite-side actions until FINAL. The alternative is to accept delayed busts and corrections as an environmental risk under A-12″.
- **FD-15:** if FD-14 is adopted, the basis for finality: (a) broker finality evidence only, which keeps the widen-only principle strict but depends on a capability not shown to exist; or (b) a time-based A-16, which requires amending the widen-only principle to allow narrowing by a declared assumption.
- **FD-16:** bootstrap mode. Either require M1 (an attested manifest) before any authorization, or allow M0 with its stated costs (replays and pre-bootstrap corrections block).

*Not* founder decisions, and resolved technically above:
- reinstatement after a bust (allowed as a version transition);
- the pending-versus-conflict split for prior_version (pending if ahead, conflict if behind);
- the treatment of lists with older versions (CONFLICT when ordering is unknown).

Carried forward from R3/R4 unchanged: FD-2″, FD-7, FD-8, FD-10, FD-11, FD-12, FD-13, FD-3, FD-1′, FD-5.

---

## 7. Readiness recommendation

1. **Is the candidate internally coherent?** Yes, with CX-31 made explicit and gated on FD-15 (DERIVED). CA-1's registry-only statement is withdrawn.
2. **Are there concrete false-authorization paths within the proposed contracts?**
   - **F-1 and F-2 remain concrete** unless FD-14 adopts CA-15. Without it they are excluded only by A-12″ (extended), an environmental assumption that is implausible for any broker that can bust trades.
   - With CA-15 and A-16, none was found (DERIVED, not executed).
3. **Paths excluded only by environmental assumptions:**
   - A-12″: tail loss, and delayed busts if CA-15 is not adopted;
   - A-15: external executions (C-1);
   - A-16: corrections after finality;
   - A-2″: an unlabelled renumbering (C4-R);
   - A-11″: re-sends under new ids;
   - A-7: state-keeper honesty;
   - W1: common mode;
   - A-14 / E13: corrections beyond the order quantity.
4. **Broker capabilities that remain unverified:**
   - account-unique, stable exec_ids;
   - version numbers and keys on corrections;
   - keyed per-order lists with intermediate versions;
   - an attested bootstrap manifest (M1);
   - epoch ids and declared epoch starts;
   - a finality window or finality evidence;
   - a notification-latency bound;
   - no-short / position barriers;
   - sub-account exclusivity.
   **None** has been checked against any broker.
5. **Is it ready for independent hostile review?** Yes, as candidate text. Suggested targets:
   - ExecutionState with AMBIGUOUS transitions and multiple unsequenced versions;
   - the CA-15 reserve on orders that mix working and terminal states;
   - the M0 class-2 hold (can it deadlock with an epoch change?);
   - CX-31.
6. **Is any implementation or oracle execution authorized?** **No.** Not a freeze, not a reference model, not an oracle run, not broker contact, not paper or live trading.

*Agreement among Claude, GPT and Gemini is not independent verification. The only things executed for this document were integer arithmetic (COMPUTED).*
