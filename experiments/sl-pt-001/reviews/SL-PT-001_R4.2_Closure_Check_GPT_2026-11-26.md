## **Exposure statement**

**EXPOSURE: PRIOR CONTEXT.** I have previously reviewed the R4.1 findings, the Claude reconciliation, and the stated R4.2 change plan. I am therefore not an unexposed independent reviewer. I have not been given GPT-B's new R4.2 closure report or Gemini-B's targeted closure report in this review.

**Review basis:** the attached R4.2 candidate, identified by the supplied Git blob `f87ad21f4c70f558335070b843cb270e026005d2`, and the attached R4.1 reconciliation. I am treating the candidate as design documentation only. No implementation, tests, credentials, trading connection, or orders are involved.

I will distinguish a correction that is textually present from one whose logic is actually closed. Stage B defects are not Stage A blockers unless they create a dependency or contradiction in the Stage A freeze scope.

## **1. Closure of R4.1 findings**

**Classification key:** CLOSED means the original defect is corrected in the candidate. CLOSED CONDITIONALLY means the correction works only under a stated assumption or limitation. Neither classification means implementation or testing has been verified.

| Finding                                        | Verdict                  | R4.2 location     | Assessment                                                                                                                                                                                                                     |
| ---------------------------------------------- | ------------------------ | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GPT G-01: Stage A sizing missing               | **CLOSED CONDITIONALLY** | §§7.1, 8.1.1      | The BUY quantity, budget, fee reserve, reservation, and EXIT sizing formulas are now inside Stage A. The venue increments and fee rate remain explicitly UNVERIFIED, so sizing outputs are conditional on those policy values. |
| GPT G-02: circular V12 ordering                | **CLOSED**               | §§4.7, 6.4        | V12a now runs before fetching; V12b runs on the received bars response, before validation or use.                                                                                                                              |
| GPT G-03: clock point estimate ignores transit | **CLOSED CONDITIONALLY** | §5.6              | The point estimate is replaced by a proper interval. The derivation is sound under A-CLK, but A-CLK itself remains ASSUMED, not established. There is also a new boundary inconsistency discussed below.                       |
| GPT G-04: CONFIRMED ambiguity                  | **CLOSED**               | §4.9              | BASELINED, PENDING, and CONFIRMED now have distinct meanings and observation counts.                                                                                                                                           |
| GPT G-05: orphaned artifacts                   | **CLOSED**               | §§4.9, 10.2, 11.3 | Unreferenced artifacts are explicitly non-evidence, excluded from reconstruction, and reported by the auditor.                                                                                                                 |
| GPT G-06: REPLAY absent from closed schema     | **CLOSED**               | U9, §14.1         | REPLAY is explicitly an out-of-band test label, not a TER field or chain record.                                                                                                                                               |
| GPT G-07: credential claim too broad           | **CLOSED**               | §§2.2, 2.3, 6.4   | The claim is limited to the process environment and harness configuration file. Other credential stores are expressly not excluded.                                                                                            |

The G-01 correction is substantive, not cosmetic: R4.2 restores the quantity formula that had disappeared from R4 and R4.1. The fee and increment limitations are disclosed rather than silently treated as verified.&#x20;

SL-PT-001_R4.2_Stage_A_Review_Candidate_Claude_2026-11-26.md

SL-PT-001_R4.1_Review_Reconciliation_Claude_2026-11-26.md



## **2. Closure of Gemini-B findings**

| Finding                                           | Verdict                  | R4.2 location          | Assessment                                                                                                                                                   |
| ------------------------------------------------- | ------------------------ | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| B2-01: overrun / delayed terminal commit          | **CLOSED CONDITIONALLY** | §§6.3, 6.4, 10.1, 11.2 | A cycle that misses its hard boundary is non-qualifying. A successor or RUN_CLOSE records CYCLE_OVERRUN; otherwise the auditor classifies it INCOMPLETE.     |
| B2-02: MISSING versus CYCLE_OVERRUN precedence    | **CLOSED**               | §11.2                  | Explicit ordered precedence now resolves OVERRUN before INCOMPLETE and MISSING.                                                                              |
| B2-03: BASELINED versus CONFIRMED semantics       | **CLOSED**               | §4.9                   | First observation and repeated unchanged observation are now distinguished.                                                                                  |
| B2-03: anti-lockout overclaim                     | **CLOSED**               | §4.9                   | The single-revision condition is stated, and continuously changing bars are acknowledged as capable of blocking every affected slot for an UNBOUNDED period. |
| B2-04: EXIT-while-flat inflates apparent coverage | **CLOSED**               | §§11.3, 13             | Qualifying NO_ACTION slots are counted by underlying signal, with an explicit warning that EXIT-while-flat does not exercise position logic.                 |
| B2-05: audited commit and chain head              | **CLOSED**               | §11.3                  | The audit report must identify the repository commit and chain head it examined.                                                                             |
| B2-06: isolation terminology                      | **CLOSED**               | §§2.3, 10.4            | `egress_scope = CLIENT_ALLOWLIST_ONLY` is a better-scoped name, with the limitation stated.                                                                  |
| B2-07: fixture-backed test labels                 | **CLOSED**               | §14.8                  | U14, X5, X6 and fixture-ledger tests are explicitly distinguished from live-data evidence.                                                                   |

The B2-01 classification is particularly important: the correction does not promise that every delayed cycle gets an OVERRUN record. If neither the successor nor RUN_CLOSE writes one, INCOMPLETE is the defined fallback. That is fail-closed, and the distinction is now visible in the specification.&#x20;

SL-PT-001_R4.2_Stage_A_Review_Candidate_Claude_2026-11-26.md

SL-PT-001_R4.2_Stage_A_Review_Candidate_Claude_2026-11-26.md



## **3. New-text attack**

### **G3-01: The three-second clock boundary contradicts the stated check**

Stage A freeze blocker

**Section:** §5.6; tests U79 and U98.

**Mechanism**

R4.2 defines:

\\[ \theta\_{\text{low}}=D-t\_{\text{recv}} \\]

\\[ \theta\_{\text{high}}=D+1s-t\_{\text{send}} \\]

and passes V12b when:

\\[ \theta\_{\text{low}}\geq -2s \quad\land\quad \theta\_{\text{high}}\leq +2s \\]

The interval width is:

\\[ \theta\_{\text{high}}-\theta\_{\text{low}} =1s+(t\_{\text{recv}}-t\_{\text{send}}) \\]

Therefore, the two inclusive inequalities imply:

\\[ t\_{\text{recv}}-t\_{\text{send}}\leq 3s \\]

They do **not** imply a strict less-than-three-second round trip.

There is a concrete boundary case:

- \\(\theta\_{\text{low}}=-2s\\)
- \\(\theta\_{\text{high}}=+2s\\)
- round trip = 3 seconds

Both V12b conditions pass. This is also consistent with U79, which explicitly expects the exact ±2-second interval boundaries to pass.

But U98 says a round trip of **3 seconds or more** must fail.

**Consequence**

A correct implementation of §5.6 can pass the exact three-second case, while U98 requires it to fail. The prose claiming RTT less than three seconds is also mathematically incorrect.

**Smallest correction**

Choose one of these:

1. Retain the inclusive ±2-second interval test and add an explicit `t_recv − t_send < 3 s` condition to V12b; or
2. Change the intended boundary semantics and update U79, U98, and the claimed implication consistently.

I prefer option 1. It preserves the stated offset-bound acceptance rule and separately enforces the intended latency ceiling.

**Severity:** High.

**Blocks Stage A freeze:** **Yes.**

### **G3-02: The closed TER schema retains an undefined offset-estimate field**

Stage A freeze blocker

**Section:** §10.4, read with §5.6.

**Mechanism**

The new clock contract records:

- `t_send`
- `t_recv`
- `D`
- `θ_low`
- `θ_high`

But the closed TER schema still lists an `offset estimate` field. There is no definition of that estimate in the revised §5.6. The point-estimate method that prompted G-03 has been removed.

This is not merely a naming concern. §10.4 says the TER has a closed field set and that missing fields are invalid.

**Consequence**

An implementer cannot know whether the field means the old point estimate, the interval midpoint, one of the bounds, or something else. Two implementations could produce different TERs while both believing they followed the specification.

**Smallest correction**

Remove `offset estimate` from the closed schema, unless the founder specifically wants a derived midpoint retained. If retained, define its exact calculation, units, rounding, and status as informational only. It must not replace the interval or control V12b.

**Severity:** Medium-high.

**Blocks Stage A freeze:** **Yes.**

SL-PT-001_R4.2_Stage_A_Review_Candidate_Claude_2026-11-26.md

SL-PT-001_R4.2_Stage_A_Review_Candidate_Claude_2026-11-26.md

### **G3-03: Early-exit CYCLE records have no defined encoding for unevaluated fields**

Stage A freeze blocker

**Sections:** §§4.7, 6.4, 10.4; U96 and U99.

**Mechanism**

R4.2 correctly introduces early terminal paths:

- V12a fails before any fetch.
- V12b fails after the bars response is stored, before the quote fetch.
- V1–V11 are not evaluated after V12b fails.
- Q1–Q5 are not evaluated if the quote is never fetched.

However, the closed TER schema lists:

- V1–V11, V12a and V12b results;
- artifact hashes for bars, quote and headers;
- Q1–Q5 results, if evaluated.

The schema does not define the required representation for fields that cannot exist or checks that were never run. It is clear that Q1–Q5 are conditional, but the same clarity is absent for V1–V11, V12b, and the artifact hashes.

**Consequence**

A V12a failure cannot naturally produce a bars or quote artifact hash. A V12b failure cannot produce a quote artifact hash or quote-validation results. If those fields are mandatory under the closed schema, the very BOUNDARY_FAIL records required by §6.4 may fail the schema.

That would make the specified early-exit behaviour difficult to reconcile with §11.2's rule that a CYCLE failing schema validation is non-qualifying.

**Smallest correction**

Define a canonical encoding for every not-yet-run check and unavailable artifact:

- check result: `NOT_EVALUATED`, with a reason such as `V12A_FAILED` or `V12B_FAILED`;
- artifact hash: explicit `null` when no artifact exists;
- specify which fields must be present and which may be null for each terminal path.

Do not simply omit fields if omission makes the TER invalid.

**Severity:** High.

**Blocks Stage A freeze:** **Yes.**

SL-PT-001_R4.2_Stage_A_Review_Candidate_Claude_2026-11-26.md

SL-PT-001_R4.2_Stage_A_Review_Candidate_Claude_2026-11-26.md

SL-PT-001_R4.2_Stage_A_Review_Candidate_Claude_2026-11-26.md

### **G3-04: U105 does not yet define reproducible sizing vectors**

**Section:** §14.8, U105; §8.1.1.

**Mechanism**

U105 asks for calculations using budgets of $150.00 and $149.99 and two values of L, with results matching hand-derived exact values. It does not specify the two L values, the expected q and R outputs, or the quantity increment and fee-rate inputs to use.

The sizing formula itself is present and sufficiently understandable. The test description is not yet a reproducible test vector.

**Consequence**

A test writer must choose inputs and calculate expected values independently. Different reviewers may test different cases and still claim to have completed U105.

**Smallest correction**

Specify two exact L values, the applicable `qty_increment` and `f_res`, and the expected q and R for each of the four combinations. Include at least one case where rounding down changes q and one where the reservation rounds up to a cent.

**Severity:** Medium.

**Blocks Stage A freeze:** No, provided the normative sizing formula is accepted. It should be corrected before U105 is treated as completed.

### **G3-05: U98's test expectation is inconsistent with U79**

**Section:** §14.8, U98; §14.3, U79.

This is the test-inventory expression of G3-01, not an additional independent defect.

U79 expects the exact interval boundaries to pass. U98 requires a three-second round trip to fail. The test suite must be updated after the clock-boundary correction, and should include:

- just under 3 seconds;
- exactly 3 seconds;
- just over 3 seconds.

**Severity:** High.

**Blocks Stage A freeze:** Yes, as part of G3-01.

## **4. Findings on the requested sections**

| Area                     | Assessment                                                                                                                                  | Stage A consequence                                                                 |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| §8.1.1 sizing            | Formula restored; inputs and reservation timing are explicit. Venue-dependent increments and fee remain conditional.                        | Acceptable for freeze with disclosed limitations. U105 should be made reproducible. |
| §5.6 clock interval      | Interval mathematics is sound under A-CLK. Exact three-second boundary is inconsistent with U98 and the strict RTT claim.                   | Blocker G3-01.                                                                      |
| A-CLK                    | Explicitly ASSUMED; excludes rewritten or replayed Date headers. Not independently established.                                             | Conditional claim, not by itself a blocker if retained as an explicit limitation.   |
| §§4.7, 6.4 ordering      | V12a → bars fetch → store artifacts → V12b → quote fetch → V1–V11 is coherent.                                                              | Ordering correction closes G-02.                                                    |
| §10.4 early-exit schema  | Required TER fields lack explicit not-evaluated/null semantics.                                                                             | Blocker G3-03.                                                                      |
| §10.2 orphaned artifacts | Unreferenced artifacts are excluded from reconstruction and reported.                                                                       | G-05 closed.                                                                        |
| §11.2 precedence         | OVERRUN, then INCOMPLETE, then MISSING is explicit and unambiguous for the three classifications.                                           | B2-02 closed.                                                                       |
| U95–U105                 | Useful coverage additions, but U98 conflicts with §5.6/U79, U105 lacks fixed vectors, and early-exit TER encoding is not tested adequately. | U98 part of G3-01; U105 non-blocking improvement; early-exit schema is G3-03.       |

### **Stage B dependency check**

I do **not** find a new Stage B dependency that prevents Stage A from being specified independently.

- §8.1.1 is within Stage A's §8.1 freeze boundary.
- Its sizing formulas are self-contained.
- Its final sentence says Stage B reuses the formulas, but Stage A does not depend on §8.2.
- Stage B's time source and other deferred controls remain identified as Stage B draft.
- The Stage A candidate continues to state that no implementation, credentials, trading-host connection, or order is authorized.

This respects the freeze map in §0.2.&#x20;

SL-PT-001_R4.2_Stage_A_Review_Candidate_Claude_2026-11-26.md

SL-PT-001_R4.2_Stage_A_Review_Candidate_Claude_2026-11-26.md



## **5. Verdict**

NOT FREEZE-READY

**Stage A scope only.**

There are three distinct freeze blockers:

1. **G3-01:** the clock contract permits an exact three-second response while U98 requires it to fail.
2. **G3-02:** the closed TER schema retains an undefined `offset estimate`.
3. **G3-03:** early-exit paths do not define how required TER fields represent checks not run and artifacts not fetched.

These are specification defects, not requests for additional architecture. They can be corrected without changing the mission, expanding Stage B, or revisiting the founder's settled decisions.

**The single most important correction:** fix the clock boundary first. It is the clearest mathematical contradiction and has a direct test-level counterexample. Then close the TER schema ambiguities.

### **Recommended next waypoint**

Have Claude issue a narrowly scoped R4.2a correction addressing only G3-01 through G3-03, with no unrelated changes. Then send the corrected candidate to GPT-B and Gemini-B for closure verification against these exact findings.

No implementation, test execution, harness authorization, credentials, or orders are authorized by this review.