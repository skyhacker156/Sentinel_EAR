# EIVI-1 Independence Protocol v2 (repair of D2 §0)

**Date:** 2026-11-24 | **Author:** Claude, Specification Lead (an interested party: author of the candidate, D1 to D3 and the sealed expectations)
**Classification:** verification-process design only. No oracle has been built, and no scenario has been run.
**Supersedes:** D2 §0 (I-1 to I-7) and D2 §5 as the governing process. D1 to D5 remain unchanged in the record; corrections found since are listed in §8 as errata, not edits.

## 1. Defects in the v1 protocol

| # | Defect | Effect |
|---|---|---|
| V-1 | D3 gave expected verdicts **and** the candidate's behavior alongside every input | a builder could fit the oracle to the answers |
| V-2 | D2 I-6 gave the builder the candidate's counterexample catalogue (CX-01 to CX-68), written in candidate vocabulary | the candidate's structure leaks into the oracle |
| V-3 | The recall test was not blind (the builder knew which cases were traps), and it had **no over-denial control** | an oracle that denies everything would pass with 100% recall |
| V-4 | D1 cross-referenced the candidate's open questions, conflicts and decisions | candidate framing in the builder's normative text |
| V-5 | D1 to D4 sit in the same repository as the candidate | anyone with repository access sees everything |
| V-6 | Every trap and every expected value has one author | traps share that author's blind spots |
| V-7 | No commit-before-reveal step and no named adjudicator | results could be reinterpreted after the fact |

---

## 2. Material separation

| Pack | Contents | Who may see it | Where it lives |
|---|---|---|---|
| **CP: construction** | CP-1 behavioral specification (construction edition of D1: candidate-neutral; adds B-00 bootstrap; E-8 split into E-8a/E-8b; new E-12 to E-14; the R-8 readings; D7-11 to D7-14); CP-2 oracle build specification (replaces D2 for the builder; no comparison protocol; no CX catalogue); CP-3 scenario inputs (60 scenarios in an exact log language, shuffled, neutral IDs S-01 to S-60, **no** expected results, sources, classes or candidate fields) | builder, challengers, everyone | `ear/eivi/cp/`, and a **clean bundle** that contains nothing else |
| **SP: sealed** | SP-1 expected results, provenance (scenario → D3 test / recall scenario / CX), class (ORDINARY / TRAP-UNSAFE / TRAP-OVERDENY), candidate expectations, shuffle seed; plus the scenario source file | founder only, until the reveal | **off-repository**. Only its SHA-256 is committed (§4) |
| **R: restricted** | candidate (all drafts), Rev 3.x, reviews R1 to R9 and the responses, D1 to D5 originals | not the builder, until the builder's results are frozen | the main repository |

**Repository visibility.** If `skyhacker156/Sentinel_EAR` is public, or the builder can read it, then:
- D3's original expectations count as **exposed**. Scenarios derived from D3 are still run and graded, but are **excluded from the blind recall statistic**.
- Only the recall scenarios (RS series, new in SP-1) and any third-party traps (§3.3) count as blind.

The builder works from the clean CP bundle and declares in writing that they have not accessed the main repository.

---

## 3. Known-defect recall test

### 3.1 What it measures

Whether the oracle can see the failures that this programme already knows a governance model can make. Each relevant historical counterexample is translated into a **behavioral scenario**: inputs plus the action that a defective system would wrongly permit or wrongly deny. The translation uses CP-1 vocabulary only.

### 3.2 Composition (SP-1 holds the classes; the builder does not)

| Class | Count | Pass rule |
|---|---|---|
| TRAP-UNSAFE (a wrong ALLOW would violate S1, S2, S5 or S7) | 12 | every trap query whose sealed result is NOT_JUSTIFIED, UNBOUNDED or CONTRADICTION must **not** come back JUSTIFIED. **Required: 100%** |
| TRAP-OVERDENY (a correct ALLOW that a conservative system misses) | 8 | every trap query whose sealed result is JUSTIFIED must come back JUSTIFIED. **Required: 100%**. This is the deny-all control |
| ORDINARY (the D3 conversions) | 40 | agreement recorded per query; disagreements go to adjudication. **Not** part of the blind statistic if D3 was exposed |
| UNDETERMINED queries (inside any class) | marked in SP-1 | the oracle must **report the ambiguity**. A definite verdict is a miss |

**Translation coverage.** CX entries that are specification-text defects (for example CX-56, marker contradictions) have no behavioral form and are **excluded, with a stated reason** in the coverage table to be completed at the reveal. CX-01 to CX-28 are described only in R1 to R3; translating them is **incomplete** in this version and is listed as work outstanding.

### 3.3 Third-party traps (closes V-6 as far as possible)

GPT and Gemini each independently write **at least 5** scenarios in CP-3's log language, with sealed expected results. Each party:
- commits the SHA-256 of their sealed file before the build starts;
- sends the inputs to the founder, who appends them to CP-3 as an addendum, renumbers and shuffles, and records the mapping in their own sealed file.

Claude does not see the other parties' traps before the reveal.

### 3.4 Failure handling

A miss is **not** automatically an oracle defect. Section 5 decides among four causes: an oracle defect, a CP-1 defect, an SP-1 expectation error (Claude's derivation was wrong), or a genuine ambiguity.

---

## 4. Commit-before-reveal sequence

1. **Commit.** The founder computes SHA-256 of SP-1 and of every third-party sealed file, and commits `ear/eivi/SEALED_COMMITMENTS.md` listing them. **The sealed files themselves are not committed.**
2. **Hand over.** The builder receives the clean CP bundle (CP-1, CP-2, CP-3 and any addenda) and acknowledges §2.
3. **Freeze.** The builder runs every scenario and publishes the results file with its SHA-256, plus the oracle source hash, plus a list of every ambiguity they reported.
4. **Reveal.** The founder commits SP-1 and the third-party sealed files. Anyone can now verify that their hashes match step 1.
5. **Compare.** A **non-Claude comparator** (GPT, or the founder) applies §3.2. Claude may comment, marked as an interested party, but does not grade.
6. **Record.** Every disagreement and its adjudication goes into `ear/eivi/ADJUDICATION_LOG.md`. **SP-1 is never edited after step 1**; errors in it are recorded as errata against its hash.

---

## 5. Adjudication

| Cause | Test | Consequence |
|---|---|---|
| Oracle defect | the oracle's output contradicts CP-1 as written | fix the oracle; rerun everything; publish the new hash |
| CP-1 defect | CP-1 permits more than one reading, or none | record it in the CP-1 ambiguity list; both readings become required outputs |
| SP-1 expectation error | the oracle follows CP-1, and Claude's hand derivation does not | record an erratum against SP-1. **This counts against the hand-derivation record, not against the oracle** |
| Genuine ambiguity | as for a CP-1 defect, and the dispute is about intent, not text | the founder decides; the decision is logged |

**Adjudicator:** the founder, advised by GPT and Gemini. Claude's position is recorded and marked as an interested party.

---

## 6. Builder question channel and leak audit

- Questions go to the founder in writing. Answers may quote **only CP text**. Every exchange is appended to `ear/eivi/QA_LOG.md`, visible to all.
- Claude may draft answers, limited to CP text. Any answer that adds semantics is a CP-1 amendment and must be logged as one.
- **Leak audit at the reveal:** the comparator checks the Q&A log for any information beyond CP.

---

## 7. What independence this still does not buy (residual, declared)

- CP-1's semantics come from the candidate's author. A builder who implements CP-1 faithfully tests the candidate against **this author's reading** of the founder invariant. Gemini's challenge of CP-1 (S1 to S7, the world model) is the only check on that reading, and it is a review, not a computation.
- Translating the CX entries into recall scenarios is Claude's work. The third-party traps (§3.3) are the countermeasure.
- Even a perfect recall score shows sensitivity to *known* failure classes only.

---

## 8. Errata found while building CP-3 (recorded, not edited into D1 to D4)

| # | Where | Erratum |
|---|---|---|
| E-01 | D1, D3 (whole) | **R-8 ambiguity.** D3 treated a later bust as a later event in T-ID-04, but treated an unfinal fill as revisable now in T-AUTH-05. D1 does not say which reading S1 and S2 use. Both readings are now defined in CP-1 §1 (R-8C current, R-8V revisable) and are required oracle outputs. **The two readings give different results in T-ID-03, T-ID-04, T-AUTH-01, T-AUTH-02, T-AUTH-04, T-AUTH-05 and RS-04** |
| E-02 | D3 T-ID-03 | depends on the new E-13 (a terminal order stays terminal after a fill correction). It was unstated |
| E-03 | D3 T-ORD-06 | the world description was wrong under E-4P (X9 must lie after W). The verdict is unchanged |
| E-04 | D3 T-EXP-01 | **ill-posed under A0** (an own order of unknown quantity is impossible under E-8 and E-14). Reworked as a one-sided correction with profile A0 − E-5. *Its sell side is now the unbounded one.* |
| E-05 | D3 T-EXP-04, T-AUTH-07 | **ill-posed under A0** (an unknown-side order is impossible under E-8). E-8 is split into E-8a/E-8b; T-EXP-04 uses A0 − E-8a, and T-AUTH-07 is reworked with a correction |
| E-06 | D3 T-AUTH-09 | **wrong expectation.** Under IGNORE, an unattributed item still occupies a sequence number, so the position is a hole: UNBOUNDED, not JUSTIFIED. New D7-13 |
| E-07 | D3 T-AUTH-02 / CP-3 | the INDETERMINATE basis needs R-8C. Under E-9, finality has no delivery-horizon term (new D7-12), so one scenario is marked UNDETERMINED by design |
| E-08 | D4 | K-01 and K-13 do not account for R-8. Under R-8C, time-based finality does not expand authority at all: **K-01's "50 units" holds only under R-8V**. Under R-8C, the risk moves to post-authorization busts (T-ID-04: detection only) |
| E-09 | candidate §13.5 | **register gap:** CX-63 and CX-64 (Draft-2 response document §3.2) are missing from the candidate's counterexample register. They are not deleted; the omission is noted for the next candidate edit |

The hand-derived D3 expectations had **six errors or ill-posed cases out of 41** (E-02 to E-07), found only by making the inputs exact. That is direct evidence that hand derivation should not be graded as verification.

*End of Protocol v2.*
