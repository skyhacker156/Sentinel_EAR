# **SL-PT-001 | R4.2h Independent Hostile Closure Review**

**Reviewer:** GPT\
**Date:** 2026-11-26\
**Classification:** Specification review only\
**Scope:** R4.2f → R4.2h amendments and their direct normative dependencies.

## **0. Exposure statement**

I inspected the supplied R4.2f closure findings, both R4.2h diffs, Claude's closure package, and relevant specification text retrieved directly from the identified repository blobs.

Exposure to Claude's reconciliation means this is an adversarial closure review, not a blinded review.

- **SOURCE-REVIEWED:** Changed specification text and relevant normative dependencies.
- **DERIVED:** Logical consistency, terminal-path constructibility and counterexamples.
- **COMPUTED:** SHA-256 hashes of both supplied diff files.
- **NOT EXECUTED:** Harness, runtime tests, broker requests or trading operations.

Previously closed findings G6-02, G6-03, G6-04 and G6-06 remain outside this review.

## **1. G7-01: U19 versus U117(c)**

CLOSED

**Sections:** §6.4 step 8, §14.1 U19, U117.

R4.2h now distinguishes two mutually exclusive cases:

| Condition                                                | Required outcome                 |
| -------------------------------------------------------- | -------------------------------- |
| Append has not begun before the next slot boundary       | Append refused; CYCLE_OVERRUN    |
| Append began before the boundary but completes afterward | In-slot record; no CYCLE_OVERRUN |
| Append begins exactly at the boundary                    | Append refused                   |
| Append begins in-slot but no record survives             | INCOMPLETE or OVERRUN            |

### **Original counterexample retested**

- Append begins 100 ms before the boundary.
- Write and fsync complete 200 ms after the boundary.
- The successor acquires the append lock and observes the terminal record.

Under amended U19, this is no longer an overrun. U117(c) governs the outcome.

The original contradiction identified in G7-01 has been removed.&#x20;

SL-PT-001_R4.2f_Closure_Check_GPT_2026-11-26(1).md



**Severity remaining:** None within the finding's scope.\
**Blocks freeze:** No.

## **2. G7-02: INJECTED terminal-path schema**

NOT CLOSED

**Section:** §10.4, with direct dependency U108.

The two original contradictions have been substantially corrected. The new table separates shared injection fields from three terminal-path categories.

| Field           | V12a failure  | QUOTE_INVALID      | Constructed proposal |
| --------------- | ------------- | ------------------ | -------------------- |
| V12a            | FAIL          | PASS               | PASS                 |
| Quote hash      | null          | Present            | Present              |
| Q1–Q5           | NOT_EVALUATED | Evaluated, ≥1 FAIL | PASS                 |
| Created         | null          | null               | Present              |
| Proposal        | null          | null               | Present              |
| Rule results    | Empty         | Empty              | Populated            |
| Bar collections | Empty         | Empty              | Empty                |

The original R4.2f contradiction requiring rule results to be simultaneously populated and empty is removed. An invalid quote no longer requires a constructed proposal.&#x20;

SL-PT-001_R4.2f_Closure_Check_GPT_2026-11-26(1).md



However, two residual defects prevent full closure.

### **G8-01: Ambiguous displayed_sizes nullability**

**Mechanism:** The QUOTE_INVALID row requires `displayed_sizes` where the fixture quote carries them, without explicitly specifying its representation otherwise.

**Counterexample:** A fixture contains valid bid and ask prices but neither displayed size.

- Q4 fails.
- The terminal state is NO_DECISION (QUOTE_INVALID).
- No proposal is constructed.
- The closed schema requires every field to be present.
- The revised row does not explicitly determine the value of `displayed_sizes`.

A second ambiguous case arises when only one displayed size is present.

**Smallest correction:** Specify the exact nullability of the displayed-size field and its members when one or both sizes are absent.

**Severity:** MEDIUM\
**Blocks amended Stage A freeze:** YES

### **G8-02: U108 terminal-path coverage**

**Mechanism:** U108 remains:

> one TER per terminal path in §10.4's table (seven paths)

The amended table now defines seven scheduled terminal-path categories and three injected terminal-path categories.

**Counterexample:** An implementation executes the seven scheduled schema tests but never tests the injected V12a failure or QUOTE_INVALID schemas.

The numerical coverage statement in U108 has been satisfied, while the newly amended schema paths remain untested.

This stale count predates R4.2h, but it is a direct dependency of the present correction and therefore within the bounded review scope.

**Smallest correction:** Replace the U108 test input with:

> One TER per scheduled and injected terminal-path category in §10.4, including both REJECTED and SHADOW_EXPIRED outcomes for constructed proposals.

**Severity:** MEDIUM\
**Blocks amended Stage A freeze:** YES

The architectural correction to G7-02 is sound. Its schema and test obligations need these two narrow completions.

## **3. C-09: U11 and first-failure precedence**

CLOSED

**Sections:** §4.6, §4.7, §14.1 U11.

V8 requires a bar at every 300-second step in the inclusive interval:

\\[ [t\_{\mathrm{exp}}-250\text{ min},\\,t\_{\mathrm{exp}}] \\]

The number of required timestamps is:

\\[ \frac{250\times60}{300}+1=51 \\]

Therefore:

\\[ V8=\mathrm{PASS}\implies V10=\mathrm{PASS} \\]

Equivalently, fewer than 51 completed bars necessarily fails V8.

The first-failure ordering is:

**V7 — Newest bar**

PASS: newest bar equals t_exp

PASS

**V8 — Complete window**

50 of 51 required bars

FAIL

**V9 — Numeric validity**

Assume otherwise valid candles

PASS

**V10 — Minimum history**

Fewer than 51 completed candles

FAIL

**NO_DECISION (DATA_GAP)**

V8 is the first failing check.

**Counterexample attempted:** Construct a bar set with fewer than 51 completed bars that passes V8 but fails V10.

No such bar set exists under the specified timestamp and completed-candle rules.

Assuming the preceding checks pass, amended U11 correctly expects DATA_GAP. INSUFFICIENT_HISTORY remains a declared sub-reason but is unreachable as the first failure under the current validation order.

Its continued presence does not require a correction in this bounded round.

**Evidence classification:** DERIVED\
**Blocks freeze:** No.

## **4. Non-normative freeze-record notes**

### **E-1: X8/X10 recorded in retained test output**

CLOSED

Accepted.

Section 10.1 defines the permitted chain-record types. Section 10.4 defines the closed TER schema. Neither authorizes BOUNDARY_VIOLATION_ATTEMPT as a new record type.

**Counterexample avoided:** An implementation appends a chain record of type BOUNDARY_VIOLATION_ATTEMPT after executing X8.

That would violate the closed chain schema. Recording the result in retained test output avoids the violation without changing the chain or TER contracts.

The proposed note is consistent with the established out-of-band test-output treatment in U9.

### **E-2: HOLD always maps to HOLD**

NOT CLOSED

The proposed interpretation is consistent with the intended qualifying conditions of §11.1:

- HOLD requires signal = HOLD.
- NO_ACTION requires signal ∈ BUY or EXIT.

However, §3.3 still contains a mapping row applying to *any* signal when an open or unresolved order or authorization exists.

**Counterexample:** A valid HOLD signal with an unresolved authorization satisfies both the general blocking row and the HOLD-specific row.

Section 11.1 determines qualification, but does not independently resolve that mapping conflict for every possible state.

**Disposition:** Accept HOLD → HOLD for the reachable Stage A conditions. Do not describe the unrestricted mapping as mathematically established by §11.1 alone.

This does not independently block the bounded Stage A amendment, provided the editorial note is appropriately scoped.

### **E-3: RFC-3339 leap seconds are malformed**

NOT CLOSED

Reject the note as presently worded.

RFC-3339 permits valid leap-second timestamps. Section 4.4 requires exact conversion into integer nanoseconds since the Unix epoch, but does not explicitly prohibit a seconds component of 60.

**Counterexample:**

`2016-12-31T23:59:60Z`

This is a valid RFC-3339 leap-second representation.

Rejecting leap seconds may be a sensible deterministic parsing policy for Sentinel, but that is a protocol-specific restriction, not an inherent RFC-3339 requirement.

**Disposition:** Omit E-3 from the non-normative freeze notes, or explicitly establish a restricted timestamp grammar through a normative amendment.

Do not introduce a new implementation requirement through an editorial note.

## **5. Independent artifact-integrity check**

VERIFIED

I retrieved the R4.2c, R4.2f and R4.2h specification blobs and independently computed their SHA-256 digests.

| Artifact           | SHA-256 (abbreviated) | Result |
| ------------------ | --------------------- | ------ |
| R4.2c              | `9d417fb5…283d76`     | Match  |
| R4.2f              | `d29ed327…0857b`      | Match  |
| R4.2h              | `ee4a8ceb…c8ef`       | Match  |
| R4.2c → R4.2h diff | `c852ad3a…b7ff`       | Match  |
| R4.2f → R4.2h diff | `cf3926fa…c18`        | Match  |

I additionally compared the supplied patches' old and new hunk contents against the retrieved specification blobs, checked the unchanged regions, and reconstructed R4.2h from both baselines.

Both reconstructions produced:

```
ee4a8ceb40cbef5f31d30d08c94ef753b920fb68869e077af1876f43b80fc8ef
```

**Evidence classification:** COMPUTED.

**Method limitation:** The reconstruction used programmatic hunk replacement and hash comparison rather than invoking `git apply` itself. Both reconstruction paths and all supplied artifact hashes matched.

This is independent artifact-integrity evidence, not runtime verification.

## **6. Additional editorial defect**

**G8-03 — Stale candidate identifier**

The amended introductory text states:

> **R4.2g proposes to replace frozen R4.2c**

This should identify R4.2h. The same sentence identifies R4.2g as superseded.

**Severity:** LOW\
**Blocks freeze independently:** No.\
**Correction:** Replace R4.2g with R4.2h in that sentence.

## **7. Closure register**

| Finding | Disposition | Freeze blocker |
| ------- | ----------- | -------------- |
| G7-01   | CLOSED      | No             |
| G7-02   | NOT CLOSED  | Yes            |
| C-09    | CLOSED      | No             |
| E-1     | CLOSED      | No             |
| E-2     | NOT CLOSED  | No, if scoped  |
| E-3     | NOT CLOSED  | Omit note      |
| G8-01   | OPEN        | Yes            |
| G8-02   | OPEN        | Yes            |
| G8-03   | OPEN        | No             |

FINAL VERDICT — R4.2h AMENDED STAGE A

# **NOT FREEZE-READY**

New freeze-blocking defects

# **2**

Required architectural changes

# **0**

Artifact integrity

Verified

Existing frozen baseline

**R4.2c**

## **8. Recommendation to the founder**

Authorize one surgical R4.2i amendment, restricted to:

1. Explicit `displayed_sizes` nullability.
2. U108 coverage of scheduled and injected terminal paths.
3. Correction of the stale R4.2g identifier.
4. Scoping E-2 and removing E-3 from the proposed freeze record.

No architectural expansion. No reopening previously closed findings. No new research branch.

**The remaining problems concern specification completeness, not the underlying execution-boundary architecture.** The center of gravity remains the implementation of a bounded, auditable Stage A harness and the eventual first governed trade.

R4.2c remains frozen. No credentials, trading-host connection, order, or Stage B authority is conferred by this review.

**END OF BOUNDED CLOSURE REVIEW**