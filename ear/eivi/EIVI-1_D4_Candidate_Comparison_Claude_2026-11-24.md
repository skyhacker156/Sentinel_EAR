# EIVI-1 Deliverable 4: Candidate Comparison Report

**Date:** 2026-11-24 | **Author:** Claude, Specification Lead | **Initiative:** EIVI-1
**Compares:** D1 (behavioral specification) and D2 (oracle design) against **Rev 3.2 Draft 3** (`f647c36b…`), as the dispatch directs. A column records whether **Draft 4** (`a527f262…`, which integrated the A–E clarifications after Draft 3) changes the finding.
**Classification:** analysis only. **No oracle was run and no test was executed.** Every finding is DERIVED by hand. D1, D2 and the candidate share one author, so agreement between them is **not** evidence of correctness (see K-10).

## 0. Record discrepancy for the founder

The dispatch's §2 lists **Draft 3** as the current candidate and vectors V01–V113. The record already contains:
- **Draft 4** (a527f26297d83e5d79d8735c5fe833960fa75e359cf15a56c751a89fd6651bfc), produced in response to the "Draft 3: Targeted Clarifications" (A–E);
- vectors **V01–V122**.

This report compares against Draft 3 as instructed and marks the Draft-4 deltas. The founder decides which draft is the review baseline. No draft is withdrawn by this report.

---

## 1. Findings

Classes:
- **UNSAFE:** the candidate may permit what D1 does not justify;
- **OVER-DENIAL:** the candidate denies what D1 justifies;
- **CONTRADICTION:** the candidate is internally or mutually inconsistent;
- **AMBIGUOUS:** not testable as written;
- **ENVIRONMENT:** correct only under an unverified assumption;
- **SCOPE:** a mechanism whose core place is questioned.

| ID | Class | Finding | Evidence (D3) | Draft 4? | Disposition |
|---|---|---|---|---|---|
| **K-01** | SCOPE / contested | **Time-based finality expands authority.** FD-15(b) and CA-15 let the passage of T_f remove worlds and enlarge the sell-justified set (50 units in T-AUTH-05). Against the founder invariant ("no … convenience-driven operational transition may silently create or expand execution authority"), this is legitimate only as a **declared, logged assumption (E-9)** whose falsification is detected (T-AUTH-04). The candidate leaves the choice open as FD-15 | T-AUTH-04, T-AUTH-05 | unchanged | **Preserved as a disagreement.** The analysis recommends FD-15(a) evidence-based finality, or (b) only with E-9 named on every decision that relies on it. The decision is the founder's |
| **K-02** | ENVIRONMENT | **H_Δ is safe only under E-4P.** Under E-4I, T-ORD-07 is a contradiction and CX-64 shows H_Δ unsound. Draft 3 labels H_Δ OPERATIVE-PROVISIONAL, which could be read as operationally usable. The dispatch forbids representing it as operationally safe | T-ORD-07, CX-64 | unchanged | **Recommend relabelling** H_Δ to CONDITIONAL-ON-E-4P (a demotion, not a promotion) in the next candidate edit. Not applied here, because this dispatch is not a revision pass |
| **K-03** | OVER-DENIAL | **The candidate cannot use snapshot information that it does not commit a semantics for.** T-ORD-02: under either reading the evidence justifies buy 40 or 45, while the candidate (AWAITING-BEHIND) denies everything | T-ORD-02 | unchanged | Recorded. The cost is availability, not safety. It is fixable only once E-4 is established (Track B) |
| **K-04** | ENVIRONMENT (dominant) | **Every candidate permission is conditional on E-6** (no omission from both stream and snapshot) **and E-8** (exclusivity). With either dropped, D1 gives UNBOUNDED everywhere. The candidate encodes these as A-12″ and A-15 and states the boundary honestly. No model mechanism can remove this dependency | T-AUTH-10, T-EXP-06 | unchanged | **Track B priority 1.** Not a model defect |
| **K-05** | OVER-DENIAL | **One-sided unboundedness denies both sides.** An unknown-quantity buy order makes Up unbounded, but Down is determinate. The candidate (T2-U → UNBOUNDED) denies the sell | T-EXP-01 | unchanged | Recorded under D7-02. A safe scoping rule needs its own argument |
| **K-06** | ENVIRONMENT (hidden) | **Freshness (S_lim) and D_max are environment hedges, not consequences of the model.** Under A0, a quiet period changes nothing (T-ORD-08), and c1 is counted throughout a delayed transmission (T-RES-10). The candidate's freshness denial is protection against **E-6 failure**. It should be labelled as that, so that it is not mistaken for a Track A rule | T-ORD-08, T-RES-10 | unchanged | **Recommend:** label freshness as "Track B hedge for A-12″". D_max remains not a safety rule (FD-10), consistent with the candidate's own statement |
| **K-07** | ENFORCEMENT GAP | **Nothing in EAR prevents a transmission without a commitment.** Consume is atomic only up to the model's linearization point. An adapter that transmits a released, expired or never-committed payload is **detected after the fact** (unknown order), not prevented. Against center-of-gravity question 4 ("what prevents a prohibited action beyond a policy statement?"), the answer today is: **the adapter, which is undesigned (G-07)** | T-RES-07, T-RES-08 (E-7 variant) | Draft 4 states the scope explicitly (proposal C) | **The central-invariant gap of the current architecture.** EAR can make authority *accountable* but cannot *enforce* it without an adapter that holds non-forgeable submission capabilities. Recommend G-07 becomes the next design object after the oracle |
| **K-08** | AMBIGUOUS | **Basis impugnment under uncertain placement** (OQ-H15). D1 gives INTACT, IMPUGNED or INDETERMINATE over worlds. Draft 3's text gives IMPUGNED whenever *some* placement denies. That is a different answer on T-AUTH-02, and the candidate itself calls it a known defect | T-AUTH-02, T-AUTH-03 | unchanged | **Disagreement preserved.** OQ-H15 stays open. T-AUTH-03 also shows that a *definite* impugnment needs an undeclared timestamp assumption (A-03 / E-12) |
| **K-09** | OVER-DENIAL / AMBIGUOUS | **Corrections to executions unseen since bootstrap.** Under E-5, a correction carries its own delta, so the position is determinate (T-AUTH-01). The candidate holds it (no anchor) and denies. Either the candidate is over-conservative or D1's E-5 is too strong. Which one depends on what brokers actually send | T-AUTH-01 | unchanged | Recorded. Track B question: do corrections carry prior_qty reliably? |
| **K-10** | CORRELATION | **The strict-consistency reading and the global SR coincide.** On T-AUTH-08 (a fork on an irrelevant, fully busted execution), D1's strict reading (D2 R-6) and the candidate both deny everything. That agreement comes from **one author's shared reading**, not from independent confirmation. A tolerant reading justifies the actions | T-AUTH-08 | Draft 4 makes the lockout explicit (C-18, OQ-R1) | **Flagged for Gemini.** C-14 cannot be judged by Claude-authored material alone |
| **K-11** | AMBIGUOUS | **Overfill semantics.** Neither D1 nor the candidate says whether fills beyond the order quantity are a possible world or a contradiction (A-01). The candidate treats an overfill as a CONFLICT (Rev 3.1 E05) | T-ID-05 variant, T-EXP-05 | unchanged | Return to D1 and the candidate. Track B: can brokers overfill? |
| **K-12** | AMBIGUOUS | **Equal-time ordering** (expiry versus consume, tick versus evidence). D1 requires "exactly one takes effect" but cannot say which. The candidate's IC-4 interim convention covers finality ticks only | T-RES-06 | unchanged | OQ-H18 stays open, and its scope should include expiry versus consume |
| **K-13** | AGREE (no finding) | Commit counts the proposal (T-RES-01); concurrent commits (T-RES-02); suspended commitments stay counted (T-RES-03, T-RES-04); atomic consume (T-RES-05); duplicate direction (T-ID-01); identifier injectivity (T-ID-07); gaps, resets and epochs (T-ORD-01, 03, 04); conflicts (T-ID-02, 06; T-ORD-05) | — | — | Agreement between Claude-authored documents: **not verification** |

**No UNSAFE finding against Draft 3 under profile A0.** This is DERIVED by hand over 41 cases written by the same author, so it is weak evidence. The unsafe outcomes D3 does exhibit (T-ID-04, T-RES-07, T-AUTH-10) are all **assumption-boundary or enforcement-boundary** cases (K-04, K-07), not Track A defects.

---

## 2. Mechanism audit against the five center-of-gravity questions

**Question key:**
- **A**uthority: what grants permission, and what does not;
- **E**vidence: what supports the decision, and what is unknown;
- **U**ncertainty: how unresolved uncertainty limits the admissible actions;
- **En**forcement: what prevents a prohibited action;
- **R**econstruction: can an independent reviewer reproduce the decision.

| Mechanism | Strengthens | Verdict |
|---|---|---|
| Committed reservation as the only authority; atomic commit and consume | A, En (model side) | core |
| L1 immutable log; L2/L3/L4 layering; I9-ext | E, R | core; determinism environment open (OQ-H16) |
| Version history, τ and ν identity, typed encoding | E, U | core |
| Status table plus SR plus reason-code envelope | U, R | core; global scope contested (C-14, K-10) |
| H_Δ / admissible cuts | U | core **only once E-4 is established** (K-02) |
| Π over the post-proposal state; R-15″ suspension; reactivation as a new authorization | A, U | core |
| Basis record and impugnment (AM-13′) | R, U | core; placement rule open (K-08) |
| Finality gate and CA-15 reserve | U | contested: it expands authority by time (K-01) |
| Freshness S_lim | (Track B hedge) | keep, relabel (K-06) |
| D_max | none for safety | **does not strengthen any of the five**. Already marked an intent-age policy (FD-10). Candidate for removal from the core |
| CHANNEL_SUSPECT / attribution | E, U | core in principle; behavior is FD-20, unresolved |
| Configuration migration L_a | A, R | core; OQ-H19 open |
| Re-bootstrap (FD-18) | A (governance) | core as a governance escape. C-18 makes it the only exit for several conditions |
| **Adapter capability (G-07)** | **En** | **absent; it is the gap (K-07)** |

---

## 3. Disagreements preserved (not forced to consensus)

1. **K-01:** time as an authority-expanding transition. D1 treats it as contested; the candidate keeps both options.
2. **K-08:** INDETERMINATE (D1) versus worst-case IMPUGNED (Draft 3 text) for uncertain placement.
3. **K-10:** strict versus tolerant world consistency. Unresolvable by this author.
4. **K-02:** whether H_Δ's label should be demoted now. Recommended; not applied.

*End of D4.*
