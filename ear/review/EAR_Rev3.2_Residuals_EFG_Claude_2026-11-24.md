# EAR v0.1 Rev 3.2 Candidate: Targeted Closure of the E/F/G Residuals

SPECIFICATION ONLY / NOT IMPLEMENTED / NOT VERIFIED. Rev 3.1 stays frozen. No freeze, implementation, oracle execution, broker-capability assertion, paper or live trading.
Reviewer: Claude (Specification Lead). Date: 2026-11-24 (ET).

**Baseline hash.** The dispatch quotes `dd9d87f76b01134e…a239`, which matches what this reviewer checked with `sha256sum` on fresh clones of commit d4c9e66. That check was made by this reviewer, not by GPT, and it establishes byte identity only.

**Relation to prior work.** This dispatch was written before GPT had seen the Challenge H response, R6 (`3148d4fa…`). Several items here overlap it:
- E-2 is R6's H1, extended below;
- F-3 is R6's H6, restated neutrally as required;
- E-3 partly overlaps R6's H3.
This document supersedes R5 and R6 where they differ.

**Labels.**
- **DERIVED**, **ASSUMED**, **CONDITIONAL**, **UNVERIFIED**, **UNBOUNDED**: as defined in the dispatch.
- **COMPUTED**: run by a throwaway Python script that compares model bounds (Rev 3.1 §2.4 plus CA-15) with a brute-force enumeration of the declared worlds for **one hand-built example**. It is not an oracle and not a test suite, and it shows nothing about any implementation.

---

## 1. Executive disposition

| Item | Status | Basis |
|---|---|---|
| E-1 transition identity | **Conditionally closed**: requires a broker transition id *or* broker version claims; otherwise out of contract | DERIVED; CX-38 COMPUTED |
| E-2 admissible histories | **Closed** for chains (total order via predecessor claims); bounded fallback for partial orders | DERIVED; COMPUTED |
| E-3 three reconciliation levels | **Closed by qualification.** R5's case 8 overstated what a snapshot contributes; corrected here | DERIVED |
| E-4 opening anchors | **Conditionally closed**: an anchor must carry the broker's version or transition id; otherwise corrections to it are held | DERIVED |
| F-1 / F-2 effective-version CA-15 | **Closed for quantity-only changes** within the contract | DERIVED; F-2 COMPUTED (6 steps, bounds equal the brute-force extremes) |
| F-3 FD-15 | **Founder decision, presented neutrally** | — |
| F-4 reservation lifecycle, two-sided | **Closed for prevention up to consumption.** After submission: detection only, not reversible | DERIVED |
| G-1 M1 contract | **Specified.** Every capability UNVERIFIED | — |
| G-2 / G-3 M0 resolution and classes | **Closed by rule.** Dismissal needs an exec_id-level broker statement; otherwise the hold blocks both sides | DERIVED |
| A-12″ boundary | **Unchanged and unresolvable inside the model** | ASSUMED |

---

## 2. E-1: canonical transition identity and idempotency

**The defect.** If a second delivery is checked against Sentinel's *current* version before anything else, a redelivered correction (predecessor v0) looks stale once Sentinel is at v1. The fix: **look up identity first; check the predecessor only for transitions not seen before.**

**Transition identity (candidate).** A transition is any NEW, CORRECT or BUST. Its identity τ is one of the following, in order of preference:
1. **τ_B, broker-supplied:** a transition identifier that is stable across delivery paths. For example, the correction message's own execution-report id, distinct from the exec_id of the execution it corrects. ASSUMED as a contract item (A-11‴); UNVERIFIED for any broker.
2. **τ_D, derived:** SHA-256 over the canonical serialization of the **immutable economic fields**: account, instrument, exec_id, kind, side, order_id, *broker* prior_version, prior_qty, qty, κ (or ⊥).
   - It excludes transport fields: event_id, received_at, headers, the list or message envelope.
   - **The predecessor must be the broker's version claim, not Sentinel's.** Sentinel's version index is internal bookkeeping and never enters identity.
3. **Neither available:** a CORRECT or BUST with no τ_B and no broker version claim is **out of contract**. It is held as a structural failure (UNRESOLVED), because CX-38 shows that value-only matching can drop a genuine correction.

**Canonicalization.** UTF-8, sorted keys, integers only, fixed field set, explicit `null` for absent optional fields (null and absent are distinct), ASCII-normalized identifiers. Pinned by parser version inside the derivation lineage (R6 §H2). Deterministic for a fixed parser version (DERIVED).

**Deduplication protocol, for an incoming transition t on execution x:**
1. **Identity lookup.** If τ(t) is already in x's L2 history:
   - same canonical payload → **duplicate**: no L2 entry, an L3 counter only;
   - different payload → **CONFLICT**: a new L2 entry and an L3 conflict record; x is UNRESOLVED and the band UNBOUNDED, blocking both sides.
2. **New identity, predecessor check** against the chain of *broker* versions:
   - predecessor = the chain head → **APPLY**;
   - predecessor ahead of the head → **PENDING** until the predecessor arrives;
   - predecessor fills a **known gap** in the chain (an entry inserted by a list with an unknown predecessor) → **HISTORY FILL**: an L2 entry that does not change the current state but does affect F_d(β) inside the gap window;
   - predecessor already has a successor with a different τ → **FORK**, which is a **CONFLICT**;
   - predecessor older than the head, with no gap → **STALE**, which is a **CONFLICT**.

| Delivery case | Example | Result |
|---|---|---|
| duplicate, same path | C1 (v0 → 6) delivered twice by the stream | duplicate; no change |
| duplicate, cross path | C1 applied by the stream; a list shows C1's τ_B, or the matching current version and broker version 1 | duplicate; no change |
| conflicting duplicate | C1's τ arrives again with qty 7 | CONFLICT |
| delayed | C1 arrives after C2 (v1 → 3), which was itself inserted from a list with an unknown predecessor | history fill |
| reordered | C2 (predecessor v1) arrives before C1 | C2 PENDING; C1 arrives and is applied; then C2 is applied |
| fork | C1 (v0 → 6) applied; C1′ (v0 → 4, different τ) arrives | CONFLICT |
| no τ_B, no broker version | CORRECT carrying only prior_qty / qty | out of contract: UNRESOLVED |

**A genuinely different correction with the same apparent predecessor** is a fork. A repeat correction later in the chain (for example 10 → 6, then 6 → 10, then 10 → 6 again) is distinct, because its broker predecessor version differs. This is exactly why the broker's version claim must enter τ_D (CX-38).

**Acceptance tests.**
- (i) Every delivery case in the table yields the stated result, independent of arrival order.
- (ii) Mutation: computing τ_D from Sentinel's version index must make CX-38 fail, i.e. drop the genuine repeat correction.

---

## 3. E-2: admissible histories 𝓗_x(β)

This extends R6 §H1.

**Construction.**
- By D27 (extended here to BUST: a BUST must also carry its broker predecessor version), every transition names its predecessor. So x's transitions form a **chain**: a total order.
- **𝓗_x(β)** is the set of *cuts* k such that versions 0..k lie at or before β, respecting:
  - (a) the chain order;
  - (b) every known key: κ(v_i) ≤ β ⇔ i ≤ k.
- Admissible k ∈ [i_lo, i_hi − 1]. Here i_lo is the last keyed index with κ ≤ β, and i_hi is the first keyed index with κ > β.
- The quantity is effective(x, β) ∈ {q_k : k admissible}. That set is finite, and computing it takes time linear in the chain length. **No enumeration of histories is ever needed.**

**Worked example (COMPUTED).** Chain: v0 = 10 at 501, v1 = 6 (κ = ⊥), v2 = 3 (κ = ⊥), v3 = 8 at 512.
- At β = 505, the cuts are {0, 1, 2}, giving values **{10, 6, 3}**.
- At β = 515, the cut is {3}, giving **{8}**.
- *Here* independent before/after placement happens to give the same set. It is not sufficient in general.
- **Second chain** (COMPUTED): v0 = 10 at 501, v1 = 6 (⊥), v2 = 4 at 508, v3 = 2 (⊥). At β = 505 the admissible values are **{10, 6}**. Independent placement would also admit **2**, which is impossible because v3 follows v2 at 508.

**Partially ordered transitions.** These arise only if a transition lacks a broker predecessor claim, which is out of contract per E-1. If the founder wants to admit them anyway, the **sound conservative bound** is:
> effective(x, β) ⊆ [min, max] of {0} ∪ {q_i : v_i not forced after β by its key}.

This is sound (DERIVED): every linear extension's cut yields one of those versions, or 0 before NEW. It may over-widen, but it cannot exclude a reachable state.

**Aggregation.** Chains are independent (R6 §H1), so:
- d_max = F_b − P_open − Σ_x min effective;
- d_min = F_b − P_open − Σ_x max effective.

**Finite and usable.** The interval is always finite when every version's quantity is known.
- **Fail closed:** any PENDING, CONFLICT, FORK, out-of-contract item, or version of unknown quantity makes x **UNRESOLVED**, so the band is **UNBOUNDED**.
- No history is ever discarded to make a result convenient. Excluded cuts are exactly those that contradict a known key or the chain order.

**Acceptance test.** For chains of up to 6 versions with any mixture of ⊥ and keyed versions, a separately written checker enumerates every linear extension and cut. The model's value set must equal it (or, under the partial-order fallback, contain it).

---

## 4. E-3: aggregate, identity and lineage reconciliation

| Evidence | (1) Aggregate position | (2) Execution identity | (3) Execution lineage |
|---|---|---|---|
| Accepted snapshot at β | **yes**, as a broker claim at β (W1-T / W1-F) | **no** | **no** |
| Complete per-order list with ids (no version keys) | for that order's total only | **yes, for that order** | current version only. History windows stay ambiguous (R6 §H3) |
| Complete per-order list with ids, per-version keys or τ_B | that order | that order | **yes, for that order**, through ω |
| Complete account-wide manifest (M1) at β0 | yes, via the arithmetic check (corroboration) | **yes, account-wide** at β0 | current-version **anchors** only; history before the anchor is UNOBSERVED |
| Stream with ids, keys and τ | what it delivered | what it delivered | what it delivered |
| Incomplete or bounded list | no | identities listed only | listed versions only |

**Correction to R5.** R5's case 8 ("a snapshot with W ≥ the list watermark restores determinacy") was **overstated**. Determinacy came from the list's completeness bracket. The snapshot only provided a comparison point beyond the window. **An aggregate snapshot never establishes level 2 or level 3** (DERIVED). Already stated in R6 §H3; recorded again here as a correction.

**Using an aggregate snapshot as a new baseline while lineage is unresolved** is the re-bootstrap of R6 §H4 (FD-18). Its exact semantics:
- *Boundary:* β_r = (e, W_r) of the adopted snapshot, with P_open′ = F_b.
- *Unresolved pre-boundary executions:* closed with the old ledger and listed. The new ledger treats every execution with NEW key ≤ β_r as **pre-boundary unknown**.
- *Later corrections to pre-boundary executions:* G class 3 under M0, so **UNRESOLVED (UNBOUNDED)** until an anchor arrives.
- *No double counting:* the new ledger adds only transitions keyed > β_r. A NEW keyed ≤ β_r is never added.
- *Releasing the hold:* an anchor for the referenced exec_id at β_r (a per-order list with versions, or a manifest), after which the held correction is validated by E-1.

---

## 5. E-4: opening-anchor semantics

| Object | L2 kind | Means | Does not mean |
|---|---|---|---|
| Newly received execution event | NEW / CORRECT / BUST with its own κ | Sentinel received this transition | — |
| **Current-version opening anchor** | ANCHOR (source: manifest), with κ_anchor = β0, the broker version or τ_B of its latest transition, and its qty | as of β0, the broker claims x exists at this version and quantity, inside P_open (delta 0) | that Sentinel received or reconstructed any earlier transition. Everything before is explicitly **UNOBSERVED** |
| Reconstructed historical chain | NEW … CORRECT entries actually received | Sentinel holds those transitions | anything about UNOBSERVED segments |
| Later correction whose predecessor is the anchor | CORRECT, predecessor = the anchor's broker version or τ | applied with delta = qty − anchor qty | — |

**Rules (candidate).**
- **A correction naming the anchor's version** → apply (E-1 step 2).
- **A correction naming an earlier, unavailable version:**
  - with κ ≤ β0 → UNOBSERVED history fill, no effect (already reflected in P_open);
  - with κ > β0 → **CONFLICT** (it corrects a version that, by the manifest's claim, was superseded before β0);
  - with κ = ⊥ → **CONFLICT** (it cannot be ordered against β0).
- **An anchor without a broker version or τ** → corrections to it are **held** (UNRESOLVED). Matching on prior_qty alone fails under repeated values (CX-38). This is a reduced capability, stated.

**Acceptance test.** A manifest anchor plus a later correction at the anchor's version gives F_d = P_open + delta. The same correction naming anchor version − 1 with κ > β0 must give CONFLICT.

---

## 6. F-1 / F-2: effective-version accounting

**Rule (candidate CA-15′).** All quantities are **effective current versions**: the chain head, or the IN_OPENING anchor. They are never sums of versions or of deltas. For each order o:
- **N_o** = Σ over applied executions on o of the effective qty. A busted execution contributes 0.
- An execution is **PROVISIONAL** from the receipt of *each* version. Its finality clock restarts on every applied transition (CX-41).
- **Buy o:**
  - F_min −= Σ effective qty of its PROVISIONAL executions;
  - if o is terminal and has any PROVISIONAL execution: F_max += Q_o − N_o.
- **Sell o:**
  - F_max += Σ effective qty of its PROVISIONAL executions;
  - if o is terminal and has any PROVISIONAL execution: F_min −= Q_o − N_o.
- **Working orders** carry no upward term, because R = Q_o − N_o is already in B or S (W4).
- **A busted PROVISIONAL execution** has effective qty 0. It needs no separate reinstatement term: on a terminal order the Q − N term covers reinstatement, and on a working order R does.

**F-2 example (COMPUTED; model bounds checked against a brute-force enumeration of the declared worlds at every step).**

Setup:
- P_open = 0.
- Order A: buy, Q = 100, **terminal**. Executions A1 = 40 (FINAL), A2 = 30 (PROVISIONAL), A3 = 20 (PROVISIONAL).
- Order B: sell, Q = 30, **working**. Execution B1 = 10 (PROVISIONAL), so R_B = 20 in S.
- Reservation C: buy 20, counted in B. It is ACTIVE until step 6, then SUSPENDED (still counted), then EXPIRED.
- Formulas: U = F_max + B; A_raw = F_min − S.

| Step | Event | F_d | F_min | F_max | B | S | U | A_raw | Brute-force U / A | Sound and tight? |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | initial | 80 | 80 − 50 = 30 | 80 + 10 + 10 = 100 | 20 | 20 | 120 | 10 | 120 / 10 | yes |
| 1 | CORRECT A2: 30 → **25** (replaced, not added) | 75 | 30 | 100 | 20 | 20 | 120 | 10 | 120 / 10 | yes |
| 2 | BUST A3 (effective 0) | 55 | 30 | 100 | 20 | 20 | 120 | 10 | 120 / 10 | yes |
| 3 | reinstate A3 → 15 | 70 | 30 | 100 | 20 | 20 | 120 | 10 | 120 / 10 | yes |
| 4 | A2 → FINAL (*only under FD-15*) | 70 | 55 | 100 | 20 | 20 | 120 | 35 | 120 / 35 | yes |
| 5 | BUST B1 (sell fill reversed) | 80 | 65 | 100 | 20 | 30 | 120 | 35 | 120 / 35 | yes |
| 6 | a GAP opens → status UNBOUNDED; C → SUSPENDED | — | — | — | **20** | 30 | (diagnostic) | — | — | no authorization; C still counted |
| 7 | GAP resolved; C expires | 80 | 65 | 100 | **0** | 30 | 100 | 35 | — | — |

- **Naive additive correction** at step 1 would give F_d = 40 + 30 + 25 + 20 − 10 = **105** (COMPUTED), counting A2 twice.
- The bounds stay unchanged through steps 1 to 3, because the reserve already covered every quantity-only change.
- Step 5 leaves U and A_raw unchanged, because the bust's effect was already reserved.
- **No reservation is released early:** C's 20 stays in B through suspension, and goes only at expiry.

**Acceptance test.** The tables above, extended to every interleaving of steps 1 to 5. The model bounds must equal the brute-force extremes in every case.

---

## 7. F-3: FD-15, presented without a recommendation

| | **Option A: broker-evidence finality** | **Option B: time-based finality** |
|---|---|---|
| Assumptions | the broker's FINALITY statement is truthful for that (exec_id, version) | T_f (correction window, per correction class C_f), L_n (notification-latency bound while the stream is healthy), σ (clock skew) |
| Evidence | an L1 FINALITY item per execution version | an L1 tick record at max over versions of received_at + T_f + L_n + σ, with the stream-health deferral (R6 §H6) |
| Failure modes | a false or premature broker statement; the broker never supplies one (then nothing becomes FINAL, and the CA-15 reserve is permanent) | a correction class outside C_f; L_n exceeded inside a healthy-looking stream (undetectable by construction); a wrong T_f; skew beyond σ |
| A correction after FINAL | applied (it is evidence); FINAL_VIOLATED; FINALITY_ASSUMPTION_FAILED (FD-17) | the same |
| Can FINAL be revoked? | yes: x returns to PROVISIONAL; and, *as a consequence the founder should weigh*, every FINAL resting on the same evidence source becomes suspect | yes: x returns to PROVISIONAL; and every FINAL in the same correction class under the same parameter set has its assumption falsified |
| A broker violating the latency bound | n/a | detected only when a late correction arrives; never before |
| Effect on widen-only | **none**: narrowing is caused by evidence | **requires an explicit doctrine amendment**: narrowing by a declared environmental assumption (R6 amendment text) |
| Compatible with the current spec? | yes | only with that amendment |
| Availability | depends entirely on a broker capability (UNVERIFIED) | predictable, if the parameters are accepted |

---

## 8. F-4: reservation lifecycle, two-sided

**The R-15″ requirements, checked (DERIVED):**
- every unexpired reservation is in B or S through its order's R, whether ACTIVE or SUSPENDED;
- each is counted exactly once (one order record);
- expiry is evaluated at t_L in commit and consume, and by L1 tick records;
- suspension never releases quantity;
- `release` is allowed only before consumption; after consumption, R goes only through order-terminal transitions with cum checks;
- the move from reservation to working order is the atomic consume CAS (T04, same order id);
- every consume re-evaluates Π at its own t_L.

**Two directions:**
- **(1) A delayed buy-fill bust endangers a sell authorization** (R5 F-1).
- **(2) A delayed sell-fill bust endangers a buy authorization (COMPUTED).** L = 150. F_d = 100 after a sell fill of 50 from 150, applied and terminal. A buy of 50 is authorized: U = 150. The sell fill is busted, but the bust is delayed. True U = 150 + 50 = **200 > L**.

When the correction or bust arrives, relative to the authorization:

| Arrives | Without CA-15 | With CA-15 (the fill PROVISIONAL) | Reversible? |
|---|---|---|---|
| before evaluation | in the bounds → **prevented** | prevented | — |
| between evaluation and commit | revision moves → commit re-evaluates → **prevented** | prevented | — |
| between commit and consume | R-15″: OVER_RESERVED / OVER_LIMIT → SUSPENDED → consume refused → **prevented** | prevented (the bounds already held the reserve, so nothing was over-committed) | internal: yes |
| after submission | **detected only** (flag; no new authorization) | **already prevented at authorization**, because the reserve was in the bounds | the model cannot reverse; only a cancel request (G-07) |
| after broker acceptance | detected only | already prevented | same |
| after execution | detected only. Direction (1): a short, then V54. Direction (2): over L | already prevented, *for provisional fills within the contract* | **irreversible** |

**Boundary (ASSUMED).** CA-15 prevents only for **PROVISIONAL** executions and **quantity-only** changes within [0, Q_o]. A bust of a FINAL execution relies on A-16 or finality evidence. An identity-changing correction relies on A-14″ (R6, CX-34).

---

## 9. G-1: the M1 manifest contract (every capability UNVERIFIED)

| Element | Requirement |
|---|---|
| Producer identity | a named broker endpoint or service |
| Authentication and integrity | a signature or MAC under a key whose custody is decided by D23 (open). In the reference model: **fixture** (R2 SYNTHETIC_FIXTURE) |
| Account and instrument scope | exactly the configured account and the canonical instrument id |
| Execution fields | exec_id, order_id, side, instrument, κ of NEW, broker version (or τ_B of latest transition), current qty (0 if busted) |
| Version semantics | **as of β0**: reflects every transition with κ ≤ β0 and **none** with κ > β0 |
| Watermark | β0 = (e0, W0) **equals the bootstrap snapshot's boundary** |
| Completeness | every exec_id with any transition keyed ≤ β0 on that account and instrument, **busted ones included** |
| Corrections and busts already reflected | only via the current version; earlier versions are UNOBSERVED |
| Arithmetic corroboration | inception-complete: Σ = P_open; or interval-complete: P_s + Σ = P_open |
| Times | generation time (a broker claim); received_at (Sentinel) |
| Provenance | raw bytes and hash in L1 |
| Failure behaviour | any malformed, unauthenticated or contradictory entry, or an arithmetic mismatch → **rejected as M1** (an L3 record), and bootstrap falls back to M0. Its entries may be retained only as *incomplete identity evidence*, with no completeness claim |

"Complete through β0" means: for that account and instrument, no execution with a transition keyed ≤ β0 is missing. **A broker attestation is a broker claim, not economic truth** (2.8, W1).
Evidence that would establish the capability: broker API documentation of an as-of execution report with completeness semantics, sample manifests, and a reconciliation of a sample against an independent custodian or clearing statement. None has been obtained.

---

## 10. G-2 / G-3: M0 resolution and the evidence classes

**Dismissing an unknown old execution h requires an exec_id-level broker statement** about h (for example, "exec_id h does not exist", or "h duplicates y", with y's content matching). Nothing weaker suffices:

| Evidence | Effect on h |
|---|---|
| a complete per-order list for h's claimed order that omits h | **CONFLICT** (two broker claims disagree), not dismissal |
| unknown execution outside the known order set | per-order lists cannot speak to it; hold continues |
| aggregate snapshot | cannot (W1-F, netting); a note only |
| complete account-wide manifest that includes h | **IN_OPENING** |
| complete account-wide manifest that omits h (κ(h) ≤ its boundary) | **CONFLICT** |
| incomplete or bounded response | no effect |

If account-wide completeness cannot be established, the hold is structural (SEQ_CONTRACT suspicion) and **blocks both sides**.
- *Rejected alternative:* treat h as a T2 item of known side (bounded). That assumes the suspected contract violation is isolated, which is not justified.

**The five classes:**

| Class | Established | Unknown | Safely reconcilable | Blocked | Released by |
|---|---|---|---|---|---|
| 1. Known replay | it matches the anchor or history, by τ | — | yes (duplicate) | nothing | — |
| 2. Unknown old execution | it was reported, with that content | whether it is inside P_open or is a contract violation | no | **both** | an exec_id-level broker statement, or an account-wide manifest including it |
| 3. Correction or bust to an opening execution | the correction's own fields | the identity and version of the target, under M0 | under M1, via the anchor; under M0, no | **both** under M0 | an anchor for that exec_id (manifest or versioned list) |
| 4. Contradictory replay | two conflicting claims for one τ | which is true | no | **both** | an authoritative broker resolution of that τ |
| 5. Known identity, incomplete history | identity and current version (anchor) | the UNOBSERVED earlier history | yes, for β ≥ β0 | corrections naming unavailable versions with κ > β0 or ⊥ (CONFLICT) | a versioned list covering that version |

---

## 11. New counterexamples

| ID | Case | Result |
|---|---|---|
| **CX-37** | **Fork across paths.** The stream applies C1 (v0 → 6). A list shows X at version 1 with qty 4 (C1′ from v0, a different τ). A naive "latest received wins" gives 4 | E-1 rule: CONFLICT (DERIVED) |
| **CX-38** | **Repeat correction without broker versions.** A sell execution X goes 10 → 6 (C1), 6 → 10 (C2), then genuinely 10 → 6 again (C3), whose value-only fields equal C1's. Value matching drops C3 as a duplicate: the model keeps 10 sold against a true 6, so the model position is too low by 4 and **U is understated by 4: an increase false permission** (COMPUTED) | E-1 requires broker version claims in τ_D, or τ_B; otherwise out of contract |
| **CX-39** | **Adopting CA-15 over existing working sells.** If fills already backing outstanding sell reservations become PROVISIONAL, the reserve can push A_raw < 0 immediately: OVER_RESERVED, and every sell reservation is suspended. Not unsafe, but an availability shock at adoption or bootstrap | to be stated in CA-15 and measured, not asserted |
| **CX-40** | **List completeness versus busts.** A broker's "complete" list omits busted executions. A busted execution applied with qty 0 then looks absent → spurious CONFLICT. Worse, if the bust has not yet reached the stream, the omission is the only signal | G-1 and R-07″: completeness semantics must say whether busted executions are listed. If not, an absence means "possibly busted" (widen downward), not a CONFLICT |
| **CX-41** | **Anchor for the finality clock.** X is received at t = 0 with T_f + L_n + σ = 60. A correction arrives at t = 50. If FINAL runs from the original receipt, X is FINAL at 60. If the broker's window runs from the correction, a further correction can come up to 110 | CA-15′: the finality clock restarts at each version's receipt (conservative) |

---

## 12. Candidate amendments

| # | Defect addressed | Rule | Preconditions | Failure behaviour | Falsifiable acceptance test |
|---|---|---|---|---|---|
| AM-1 | E-1 redelivery and fork | identity first (τ_B, else τ_D over immutable fields including the **broker** predecessor version), then the predecessor check; the outcomes duplicate / CONFLICT / APPLY / PENDING / HISTORY FILL / FORK / STALE | A-11‴: τ_B or broker version claims | neither → out of contract → UNRESOLVED | the E-1 table under every arrival order; the τ_D-from-Sentinel-index mutant fails CX-38 |
| AM-2 | E-2 impossible orders | admissible cuts; D27 extended to BUST; linear-time value sets; separable d; fallback hull for partial orders | chains carry predecessor claims | any PENDING / CONFLICT / FORK / unknown qty → UNRESOLVED | the model's value set equals an exhaustive linear-extension enumeration for chains of up to 6 versions |
| AM-3 | E-3 overclaim | the evidence-capability table (aggregate / identity / lineage); a snapshot establishes level 1 only | — | — | a vector in which a snapshot agrees while lineage is unresolved must stay UNRESOLVED |
| AM-4 | E-4 anchor semantics | ANCHOR kind; UNOBSERVED prefix; correction rules by κ relative to β0 | the anchor carries a broker version or τ | otherwise corrections to anchored executions are held | the E-4 test pair |
| AM-5 | F-1 effective versions | CA-15′ over effective versions; finality clock restarts per version | FD-14 adopted | — | the F-2 table over every interleaving equals the brute-force extremes |
| AM-6 | F-4 consumption | consume re-evaluates Π at t_L; `release` only before consume; R only via terminal transitions after consume | R-15″ | consume refused | all six arrival times × both directions give the table's prevent / detect result |
| AM-7 | G-1 bootstrap | the M1 contract; as-of-β0 semantics; busted entries included; arithmetic corroboration | broker capability (UNVERIFIED) | reject → M0 | an arithmetic mismatch, or one unauthenticated entry, forces M0 |
| AM-8 | G-2 dismissal | dismissal only by an exec_id-level statement; omissions from complete lists are CONFLICTs | — | hold, blocking both sides | a per-order list omitting h must not dismiss h |
| AM-9 | CX-40 | lists declare whether busted executions are included; if excluded, an absence widens downward instead of conflicting | — | an undeclared semantic → treated as excluded | a list without busts plus a delayed bust must leave the bounds conservative |

---

## 13. Residual assumptions and unverified broker capabilities

- **Assumptions (ASSUMED):**
  - A-2″: epochs and contiguity;
  - A-11″ and A-11‴: stable exec_id; τ_B or broker version claims;
  - **A-12″: delivery complete and timely. This is the boundary of every safety claim, and it is not establishable inside the model;**
  - A-14 / A-14″: corrections only within [0, Q] and never identity-changing;
  - A-15: account exclusivity;
  - A-16 or finality evidence (FD-15);
  - A-7: state keeper;
  - W1–W7.
- **Unverified broker capabilities:**
  - account-unique stable exec_ids;
  - transition ids or version numbers on corrections and busts;
  - predecessor references on busts;
  - complete per-order lists with keys, versions and stated bust semantics;
  - as-of M1 manifests, authenticated;
  - epoch ids;
  - a finality window or finality evidence;
  - a notification-latency bound;
  - no-short or position barriers.
- **Not established by anything here:** independent implementation, independent review of these amendments, executed tests, broker evidence, paper-trading or live evidence. A clean replay does not prove completeness. A fresh snapshot does not prove no later event exists. Serialized commits do not order external events. Deterministic reconstruction does not prove authenticity.

---

## 14. Updated readiness verdict

- **Rev 3.1: NO-GO**, unchanged.
- **The Rev 3.2 candidate:** E-1, E-2, E-3, E-4, F-1, F-2, F-4, G-1, G-2 and G-3 are closed **by logical argument and hand derivation**. The F-2 example and the E-2 chains are **COMPUTED** on single examples. **None is independently tested.**
- **Inside the proposed contracts:** no false-authorization path was found (DERIVED).
- **Excluded only by environmental assumptions:**
  - CX-01 and C-1 (A-12″, A-15);
  - CX-34 (A-14″);
  - CX-35 (M1 or A-16b);
  - post-FINAL corrections (A-16, or finality evidence);
  - C4-R (A-2″);
  - CX-38 (A-11‴).
- **Open founder decisions:** FD-14, FD-15 (section 7), FD-16, FD-17, FD-18 and FD-19, plus the earlier FD-2″, FD-7, FD-8, FD-10, FD-11, FD-12 and FD-13.
- **Process recommendation (for the founder).** The candidate amendments are now spread across R4, R5, R6 and this document, each superseding parts of the last. That fragmentation is itself a consistency risk. The next step should be a single **consolidated Rev 3.2 candidate draft** that integrates them into one text, followed by a hostile review of that text. Drafting is not a freeze.
- **No implementation, oracle execution, broker contact, paper or live trading is authorized.**

*Agreement among Claude, GPT and Gemini is not independent verification. The only things executed were integer arithmetic and single-example brute-force enumerations (COMPUTED).*
