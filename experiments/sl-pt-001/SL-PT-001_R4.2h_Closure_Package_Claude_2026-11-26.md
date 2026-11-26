# SL-PT-001 | R4.2h Closure Package (G7-01, G7-02, C-09)

**Date:** 2026-11-26 · **From:** Claude (Specification Lead / ARBITER) · **To:** Founder; GPT and Gemini B for one bounded closure round
**Authority:** none. **Nothing here is frozen.** R4.2c remains the frozen Stage A specification.
**Supersedes:** the R4.2g package and candidate, which were delivered but never committed. R4.2h = R4.2g + one test-row correction (C-09).
**Source of G7 findings:** the founder dispatches of 2026-11-26. The reviewers' R4.2f replies are not yet committed; each reviewer should check the correction against its own finding text.

**Scope:** R4.2h = R4.2f plus three corrections. The R4.2f → R4.2h diff is 68 lines (+11/−8), with no tag renames.

## Corrections

| ID | Defect | Correction | Where |
|---|---|---|---|
| **G7-01** | U19 ("a slot-i cycle still active at T_d(i+1) → CYCLE_OVERRUN") contradicted the append-start deadline: an append begun before the boundary and still completing is in-slot (U117(c)) | U19 now covers only a cycle that has **not begun** its CYCLE append by T_d(i+1). The old process's later append is refused. It cross-references U117(c) | §14.1 U19 |
| **G7-02** | The single INJECTED row listed rule results as present while also requiring "collections `[]`" (rule results are a collection, §10.4), and it merged four terminal paths | **One common row** (shared fields; the **bar collections** named explicitly as `[]`; rule results set per path) plus **three path rows**: V12a FAIL → BOUNDARY_FAIL; NO_DECISION (QUOTE_INVALID); REJECTED / SHADOW_EXPIRED. Each row fixes presence, nullability and the rule-result collection | §10.4 table |
| **C-09** (new; inherited from R4.2c) | U11 expects 50 completed bars → INSUFFICIENT_HISTORY. But V8 requires every one of the 51 steps in [t_exp − 250 min, t_exp], and V8 precedes V10 in the first-failure order (§4.7). Fewer than 51 completed bars **always** fails V8, so V10 can never be the first failure, and U11's expected sub-reason is unattainable by any implementation that follows §4.7 (DERIVED) | U11's expected result now reads "V8 and V10 both FAIL; sub-reason **DATA_GAP**". **§4.7 itself is unchanged**: the normative rule governs, and the test row is corrected to match it | §14.1 U11 |

Records also updated: the header, the OI-16 row and the closing line.

**Not changed:** every previously closed item, and the requirement text of §§3.1–3.4, 4.4–4.6, 4.7 (rows V1 and V3–V12b and the evaluation rule), 4.8, 4.10, 4.11, 5.1–5.3, 5.5, 5.6, 6.2, 7.1, 7.2, the §7.3 rows other than R3, and §8.1.

## Proposed founder freeze record (draft, for use only after a clean round)

```
SL-PT-001 STAGE A SPECIFICATION FREEZE RECORD (AMENDED)
Status: FROZEN BY FOUNDER (Stage A scope only)
Frozen document: experiments/sl-pt-001/SL-PT-001_R4.2h_Stage_A_Amendment_Candidate_Claude_2026-11-26.md
  git blob 29e422a74bc50035f92594fc2251d672b4762786
  SHA-256  ee4a8ceb40cbef5f31d30d08c94ef753b920fb68869e077af1876f43b80fc8ef
Supersedes, for Stage A: R4.2c (blob 316d08c0..., freeze 030e7c0). Evidence produced under R4.2c stays tied to R4.2c.
Frozen scope: as R4.2h section 0.2 (Stage A sections and the Stage A rows of sections 14-16).
Review basis: R4.2d-R4.2h closure rounds (GPT, Gemini B), committed verbatim under experiments/sl-pt-001/reviews.
Editorial notes (non-normative; no change to frozen text):
  E-1 X8 and X10 "recorded" means recorded in the retained test output; BOUNDARY_VIOLATION_ATTEMPT is a test-output label, never a chain record type or TER value (cf. U9).
  E-2 A HOLD signal always maps to HOLD; the section 3.3 "any signal + open/unresolved" row applies to BUY and EXIT (DERIVED from section 11.1).
  E-3 An RFC-3339 timestamp with second = 60 is malformed (section 4.4).
Accepted residuals: those of the R4.2c freeze record, plus U-I3 (V12a and lock_clock_at HARNESS-ATTESTED), U-T5 (append completion and durability not timestamped; file order only), runtime injections limited to R1/R4/R5/R10/R12/R13 with other FAIL cases as unit tests (U121), header artifact client-reported (D-8).
FD-5 synchronization: FD-5 (5252322) applies to R4.2h from this record. Unchanged: no credentials, no trading-host connection, no order, no Stage B.
Seed: the cleartext seed at 07f43e0 is superseded (section 11.5); a new seed hash is committed before the first audited run.
```

## Identifiers

| Artifact | SHA-256 | Git blob |
|---|---|---|
| Frozen R4.2c | `9d417fb5b22147eec6785816b239ad6b76215ea5f18e662432dc7e9cfb283d76` | `316d08c046dd7e1ea4a61be980c037b1c62037d5` |
| R4.2f (committed, superseded) | `d29ed327d7a692c3383ae4e0b0320ad93a0104a78e88afd06ffa6a7fa090857b` | `0a736a5ca35b4a80618ca7689d5e1e4d9f8dbcf9` |
| **R4.2h candidate** | `ee4a8ceb40cbef5f31d30d08c94ef753b920fb68869e077af1876f43b80fc8ef` | `29e422a74bc50035f92594fc2251d672b4762786` |
| **Diff R4.2f → R4.2h** (68 lines) | `cf3926fa8e736ec04f190e3649b49ed95dab6192c39f36a1efa87b12c6a53c18` | `034e24cdcec3538cd96b3e9e8d5abb65c9f55ccc` |
| Diff R4.2c → R4.2h (290 lines, complete) | `c852ad3a2b2de788cf9feed6d3a162bda46aef6610a3256a5b695a0113bfb7ff` | `05f420a378c1182c99ddc35145c28bb78b0ede97` |

**Integrity (COMPUTED, Claude):** both diffs, applied with `git apply` to clean copies of R4.2c and R4.2f, reproduce R4.2h at `ee4a8ceb…c8ef`. Each of the 35 edits was asserted to match exactly once.

## Bounded round: what to send

Use **new chats**. Send each reviewer: frozen R4.2c, both R4.2h diffs, and **its own** R4.2f review. Do not send this package, the other reviewer's review, or anything from `harness/`.

```
Bounded closure review, SL-PT-001 R4.2h. Inputs: frozen R4.2c (SHA-256 9d417fb5b22147eec6785816b239ad6b76215ea5f18e662432dc7e9cfb283d76), diff R4.2f -> R4.2h and diff R4.2c -> R4.2h (git format; applying either must give R4.2h SHA-256 ee4a8ceb40cbef5f31d30d08c94ef753b920fb68869e077af1876f43b80fc8ef), and your own R4.2f review.
Review ONLY the R4.2f -> R4.2h changes and any defect they introduce. Do not reopen closed items.
Targets: G7-01 (U19 consistent with U117(c) and the append-start deadline); G7-02 (INJECTED terminal paths distinct, field presence and nullability per path, no contradictory collection requirement); C-09 (U11 corrected to DATA_GAP: verify that fewer than 51 completed bars always fails V8, and that V8 precedes V10 in the section 4.7 first-failure order).
Also give a view on three NON-NORMATIVE freeze-record notes: E-1 X8/X10 "recorded" = retained test output; E-2 a HOLD signal always maps to HOLD (from section 11.1); E-3 an RFC-3339 leap second is malformed.
For each: CLOSED / NOT CLOSED with a concrete counterexample. Final verdict: FREEZE-READY or NOT FREEZE-READY.
No harness code, credentials, orders or TER output exist or may be requested.
```
