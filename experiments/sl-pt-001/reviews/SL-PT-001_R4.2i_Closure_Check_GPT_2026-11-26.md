# **SL-PT-001 | R4.2i Independent Hostile Closure Review**

**Reviewer:** GPT\
**Date:** November 26, 2026\
**Classification:** Specification review only\
**Scope:** R4.2h → R4.2i amendments and their direct normative dependencies.

## **0. Exposure statement**

I inspected all four supplied artifacts:

- R4.2h GPT closure review.
- R4.2i complete Stage A amendment candidate.
- R4.2h → R4.2i diff.
- R4.2c → R4.2i diff.

I restricted the review to the remaining closure findings, their direct dependencies, and defects potentially introduced by the new amendments.

**Evidence classification:**

| Classification  | Activity                                                                 |
| --------------- | ------------------------------------------------------------------------ |
| SOURCE-REVIEWED | Complete candidate, previous findings and both diffs                     |
| COMPUTED        | SHA-256 hashes, Git blob identifiers and bidirectional patch application |
| DERIVED         | Schema consistency, closure conditions and counterexamples               |
| NOT EXECUTED    | Harness, runtime tests, broker requests or orders                        |

This is an adversarial closure review, not a blinded review. Previously closed findings have not been reopened.

## **1. Artifact integrity**

# **VERIFIED**

Both patch reconstruction paths passed.

R4.2c baseline SHA-256 matches

R4.2h baseline SHA-256 matches

Both baseline Git blob identifiers match

Reverse Git patch application successful

Forward Git patch application successful

Both reconstructed candidates byte-identical

R4.2i Git blob identifier matches

Unlike the R4.2h review, this round used actual `git apply` commands in isolated temporary repositories.

Both patches were reverse-applied to the supplied candidate. The reconstructed baselines matched the previously recorded SHA-256 hashes and Git blob identifiers. Forward application then reproduced the supplied R4.2i candidate byte-for-byte.

**R4.2i verified SHA-256:**

4259551121fa3d271074fb13da51fb270ae859b0b516a953752731f20972a51a

&#x20;Copy SHA-256

**R4.2i verified Git blob:**

`3549d2275ce3f5490f93802ff9eec1570f2fb48f`

| Artifact      | Result                                |
| ------------- | ------------------------------------- |
| R4.2c         | Matches frozen baseline               |
| R4.2h         | Matches previously reviewed candidate |
| R4.2c → R4.2i | PASS                                  |
| R4.2h → R4.2i | PASS                                  |
| R4.2i         | Byte-identical across both paths      |

**Limitation:** This establishes local artifact integrity against the previously recorded identifiers. I did not independently retrieve the current remote repository or verify that R4.2i has been pushed.

## **2. G8-01: Displayed-size nullability**

CLOSED

**Section:** §10.4.

R4.2i now explicitly defines `displayed_sizes` as an object containing `bs` and `as`, with each member independently nullable.

The object itself is null when no quote is available under the specified conditions.

### **Counterexample retest**

| Quote input                        | Required `displayed_sizes`  |
| ---------------------------------- | --------------------------- |
| Both sizes present                 | `{"bs":"0.25","as":"0.40"}` |
| Bid size absent                    | `{"bs":null,"as":"0.40"}`   |
| Ask size absent                    | `{"bs":"0.25","as":null}`   |
| Both sizes absent                  | `{"bs":null,"as":null}`     |
| Bid size non-numeric               | `{"bs":null,"as":"0.40"}`   |
| Negative bid size                  | `{"bs":"-1","as":"0.40"}`   |
| Quote request receives no response | `null`                      |
| Injected V12a failure              | `null`                      |

The negative-size example is particularly important: the original numeric token is preserved as evidence even though Q4 fails. Evidence preservation and validation remain separate operations.

The new rule also requires displayed sizes to be recorded independently of whether Q1–Q5 are evaluated.

**Result:** The original counterexamples have been resolved. An invalid quote can now produce a deterministic, schema-compliant TER without constructing a proposal.

**Evidence:** DERIVED.\
**Remaining severity:** None within the original finding's scope.\
**Blocks freeze:** No.

## **3. G8-02: U108 terminal-path coverage**

CLOSED

**Sections:** §10.4 and §14, U108.

The previous test incorrectly limited coverage to seven terminal paths. R4.2i replaces that numerical restriction with explicit scheduled and injected coverage.

### **Required U108 coverage**

**Scheduled**

V12a failure

Bars request: no response

V12b failure

V1–V11 failure

HOLD / NO_ACTION

QUOTE_INVALID

REJECTED

SHADOW_EXPIRED

**Injected**

V12a failure

QUOTE_INVALID

REJECTED

SHADOW_EXPIRED

**Additional cases**

&#x20;One displayed size absent

&#x20;Both displayed sizes absent

Coverage specified, not executed. Checkmarks indicate inclusion in the test obligation, not passing runtime results.

The original counterexample, in which an implementation could satisfy U108 while omitting the injected failure paths, is no longer admissible.

**Evidence:** DERIVED.\
**Remaining severity:** None.\
**Blocks freeze:** No.

## **4. G8-03: Stale candidate identifier**

CLOSED

The introductory text now correctly identifies R4.2i as the proposed replacement for frozen R4.2c.

R4.2h and the preceding unsuccessful amendment candidates are correctly identified as superseded and never frozen.

No ambiguity concerning the governing specification remains in the introductory freeze statement.

**Blocks freeze:** No.

## **5. Editorial and normative reconciliation**

### **E-1: X8/X10 retained test output**

**CLOSED — carried forward.**

The previous disposition remains valid. Boundary-violation test results belong in retained test output rather than an unauthorized chain-record type.

No conflicting amendment was introduced.

### **E-2: HOLD mapping**

**CLOSED CONDITIONALLY — Stage A scope only.**

The R4.2i diff does not modify §3.3 or §11.1.

The previous distinction therefore remains:

- HOLD maps to HOLD under reachable scheduled Stage A conditions.
- An unrestricted assertion covering unresolved external orders or authorizations remains unsupported.

The R4.2i closure package was not included among the four supplied artifacts, so I cannot independently confirm that its editorial freeze note has been appropriately scoped.

This is a freeze-record condition, not a reason to reopen the Stage A architecture.

### **E-3: Leap-second handling**

CLOSED

Claude selected the normative-amendment option rather than removing the proposed restriction.

Section 4.4 now explicitly rejects a seconds field of 60 and correctly identifies this as a **Sentinel-specific timestamp restriction**, not an RFC 3339 requirement.&#x20;

SL-PT-001_R4.2i_Stage_A_Amendment_Candidate_Claude_2026-11-26.md



U122 supplies both a rejection case and a positive parsing control.

| Timestamp                        | Required parser outcome |
| -------------------------------- | ----------------------- |
| `2016-12-31T23:59:60Z`           | Malformed               |
| `2016-12-31T23:59:59.999999999Z` | Exact conversion        |

I independently computed the expected Unix nanosecond representation of the second timestamp:

`1483228799999999999`

U122 should be understood as a timestamp-parser test. Downstream bar-grid validation and quote-validation terminal reasons remain governed by V3 and Q5 respectively.

**New Stage B dependency:** None.\
**Blocks freeze:** No.

## **6. Hostile examination of newly introduced text**

I attempted to identify new blocking defects arising directly from the amendments.

| Attack surface                             | Result                                  |
| ------------------------------------------ | --------------------------------------- |
| One or both displayed sizes missing        | Resolved                                |
| Malformed size token                       | Resolved                                |
| Numeric but invalid size                   | Original token preserved                |
| No quote response                          | Explicit null representation            |
| Injection without an HTTP request          | Covered by injected schema              |
| Q checks not evaluated                     | Displayed-size recording still required |
| Incomplete U108 coverage                   | Resolved                                |
| Leap-second conversion ambiguity           | Explicitly prohibited                   |
| Conflict with existing append timing rules | None introduced                         |
| New broker or Stage B dependency           | None identified                         |
| Unauthorized scope expansion               | None identified                         |

For implementation purposes, a received but unparseable quote body should retain its raw artifact and represent unavailable displayed-size members as null. This is consistent with the amended rule's treatment of malformed members.

**New G9-series freeze-blocking findings: NONE.**

I do not recommend another specification revision on the basis of this bounded review.

## **7. Final closure register**

| Finding | Disposition          | Blocks freeze     |
| ------- | -------------------- | ----------------- |
| G7-01   | CLOSED               | No                |
| G7-02   | CLOSED               | No                |
| C-09    | CLOSED               | No                |
| G8-01   | CLOSED               | No                |
| G8-02   | CLOSED               | No                |
| G8-03   | CLOSED               | No                |
| E-1     | CLOSED               | No                |
| E-2     | CLOSED CONDITIONALLY | Freeze-note scope |
| E-3     | CLOSED               | No                |

## **8. Final verdict**

GPT INDEPENDENT HOSTILE REVIEW — R4.2i

# **FREEZE-READY**

Within the bounded technical Stage A review scope.

Outstanding technical blockers

# **0**

New architectural changes required

# **0**

Artifact integrity

## **Verified**

Runtime verification

## **Not executed**

Governing frozen baseline

**R4.2c**

Recommended replacement

**R4.2i**

Founder freeze authority and the remaining review-record conditions are not conferred by this verdict.

## **9. Recommendation to the founder**

**Terminate the specification amendment loop once the remaining review-record conditions are satisfied.**

The outstanding work should now transition from specification reconciliation to implementation and empirical evidence production.

MISSION PROGRESSION

1. **R4.2c baseline freeze**

   Completed
2. **FD-6 reconciliation**

   GPT technical closure achieved
3. **R4.2i amended freeze**

   Remaining review-record conditions and founder decision
4. **FD-5 harness implementation**

   Awaiting authorization
5. **Stage A pre-live tests**
6. **Scheduled shadow run and independent reconstruction**
7. **Stage A exit and Stage B authorization**
8. **First governed paper BUY with confirmed fill**

## **10. Dispatch to Claude**

# A-TEAM DISPATCH: SL-PT-001 R4.2i — TECHNICAL CLOSURE

**From:** GPT, Independent Hostile Reviewer\
**To:** Claude, Specification Lead\
**Date:** 2026-11-26\
**Classification:** Specification closure / no implementation authority

**VERDICT: FREEZE-READY within the bounded technical Stage A scope.**

G8-01, G8-02 and G8-03 are CLOSED. G7-02 is consequently CLOSED. E-3 is CLOSED by normative amendment and U122.

No new freeze-blocking findings. No additional specification revision requested.

Artifact integrity independently established using actual reverse and forward `git apply` operations against both supplied patches.

Verified R4.2i SHA-256:\
`4259551121fa3d271074fb13da51fb270ae859b0b516a953752731f20972a51a`

Verified Git blob:\
`3549d2275ce3f5490f93802ff9eec1570f2fb48f`

**Next actions:**

1. Record GPT's technical closure.
2. Complete the required independent review register.
3. Preserve E-1 and scope E-2 explicitly to reachable Stage A conditions.
4. Prepare the amended Stage A freeze record for founder approval.
5. Bind the interface contract and FD-6 reconstruction script to the amended frozen specification, documenting compatibility or necessary changes.
6. Prepare the FD-5 harness implementation authorization package.

Do not reopen closed findings without a concrete contradiction or counterexample.

Do not expand the architecture, introduce additional research branches, or advance Stage B authority.

The center of gravity is now executable Stage A evidence production.

R4.2c remains governing until the founder approves the amended freeze.

No credentials, trading-host connection or orders authorized.

**END DISPATCH**

## **11. Center of gravity assessment**

**MAINTAINED.**

The reconciliation cycle has reached technical closure from GPT's side. Further specification refinement without a concrete defect would now risk diminishing returns.

The next meaningful advance for Sentinel is not another design document. It is an authorized harness producing evidence that can be independently reconstructed and challenged.

The distinction between a reviewed specification and a functioning system must remain intact.

**END OF BOUNDED CLOSURE REVIEW**