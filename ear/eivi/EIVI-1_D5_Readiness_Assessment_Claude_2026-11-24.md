# EIVI-1 Deliverable 5: Readiness Assessment

**Date:** 2026-11-24 | **Author:** Claude, Specification Lead | **Initiative:** EIVI-1
**Classification:** assessment only. No test, oracle, implementation, broker contact or trading has occurred.

## 1. What has been demonstrated

**Nothing.** In the sense the dispatch means (an independently reproducible result), no property of EAR has been demonstrated. No vector (V01–V122) and no D3 test (41 specified) has been executed. No oracle exists.

## 2. What has only been derived (by hand, single author)

- **Specification lineage:** Rev 3.2 candidate Drafts 1–4, with 68 counterexamples (CX-01 to CX-68), 20 conflicts (C-1 to C-20) and the change ledger.
- **Behavioral semantics:** D1's world-set semantics and safety properties S1 to S7.
- **Oracle design:** D2.
- **Test expectations:** the 41 expected results in D3.
- **Comparison:** D4's 13 findings, including "no UNSAFE finding under A0".

Every one of these is **DERIVED**. Successive review rounds found new defects every time; the last two rounds found five false-permission paths. That pattern argues against treating hand derivation as near-verification.

## 3. What has been computed

**None.** The only machine operations in this program have been file hashing, byte comparison and text edits.

## 4. What remains assumed or unverified

| Item | Kind | Track |
|---|---|---|
| E-1 to E-11 (D1 §3); A-11″, A-11‴, A-11⁗, A-11-ORD, A-12″, A-14″, A-15, A-16 / A-16b, A-17 (candidate) | ASSUMED | B |
| E-4 snapshot semantics (prefix versus instant): H_Δ depends on it | UNVERIFIED | B |
| Adapter behaviour E-7 / G-07: the only possible enforcement point for submission (K-07) | UNVERIFIED and undesigned | B |
| SHA-256 collision resistance | ASSUMED | — |
| D1's own semantics (correlated readings R-1 to R-7) | UNVERIFIED (single author) | A |

## 5. What requires external evidence

| Question (dispatch §6 Track B) | Evidence needed | Authorization needed |
|---|---|---|
| Are exec_ids stable and unique? | broker API documentation; observed data | documentation review: **separate founder decision**; observed data: broker contact, **not authorized** |
| Are versions monotonic, with corrections carrying the prior version and quantity? | the same | the same |
| What do sequence numbers order, and how are resets signalled? | the same | the same |
| Are snapshots prefix-based or instantaneous? | the same, **highest priority** (K-02, K-03) | the same |
| Can events be omitted from both stream and snapshot? | broker guarantees; contractual or SLA terms | the same |
| What guarantees exist at the adapter boundary? | adapter design (G-07): not evidence but a design that must exist | separate design authorization |

## 6. Open items, unchanged

- OQ-H15, OQ-H16, OQ-H17, OQ-H18, OQ-H19, OQ-R1.
- **FD-20:** a founder decision, **unresolved**. The recommended interim posture is fail-closed for unattributed evidence. That posture is a recommendation, not an authorized decision.
- **C-14** (account-global SR and its denial-of-service cost) and **C-16** (snapshot semantics): flagged by the dispatch as priority, and still open.
- **H_Δ** is **not** represented as operationally safe (K-02).

## 7. Readiness

| Question | Answer |
|---|---|
| Ready for a separately authorized **implementation** phase? | **No.** No Track A result has been computed, Track B is entirely unverified, and the enforcement point (K-07) is undesigned |
| Ready for a Rev 3.2 freeze? | **No** |
| Ready for **independent oracle construction** (by a non-Claude party, per D2 §0)? | **Yes, as a recommendation, subject to the founder's authorization.** D1, D2 and D3 are specified to the point where another party can build it without consulting the candidate. Not authorized by this dispatch |
| Ready for Gemini's independent challenge of D1, D2 and D3? | **Yes** |

## 8. Recommended sequence (each step a separate founder decision)

1. **Gemini challenge** of D1 (especially R-1 to R-7 and A-01 to A-03), D2 (independence controls I-1 to I-7) and D3.
2. **GPT adversarial review** of the same material, focused on oracle independence and on whether S1 to S7 capture the central invariant.
3. **Founder decision:** authorize the independent oracle build (non-Claude builder, D2 §0), with the known-defect recall test (I-6) as its own acceptance criterion.
4. **Founder decision:** authorize Track B documentation research on snapshot semantics and correction delivery. This is research only, with no connectivity.
5. Only then: **compare** the computed oracle results with D3 and the candidate. Results become COMPUTED; agreement is still not proof of the semantics.
6. **Separately:** G-07 adapter capability design, the only route to closing K-07.

*Nothing in this deliverable authorizes any step above.*
