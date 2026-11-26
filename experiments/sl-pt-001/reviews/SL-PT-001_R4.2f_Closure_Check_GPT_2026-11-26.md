SL-PT-001 | GPT R4.2f CLOSURE FINDING G7-01
Reviewer: GPT - Independent Hostile Reviewer
Date: 2026-11-26
Reference: R4.2f, repository commit 6948668

G7-01 - U19 Contradicts U117

Section: Section 14, U19; Section 6.4 step 8; U117.

Mechanism:
U19 requires CYCLE_OVERRUN when a cycle remains active at the next slot boundary. However, R4.2f explicitly permits an append that begins before the boundary to complete afterward and remain in-slot.

Concrete counterexample:
- Append begins at T_d(i+1) - 100 ms.
- The write and fsync finish at T_d(i+1) + 200 ms.
- The successor acquires the append lock and finds a complete terminal record.
- U117 permits the record to qualify.
- U19 requires CYCLE_OVERRUN because the previous cycle remained active at the boundary.

Both expectations cannot simultaneously hold.

Smallest correction:
Amend U19 to distinguish an active cycle that has not begun its terminal append from an in-slot append that completes after the boundary. Align the expected outcomes with U117 and Section 6.4.

Severity: HIGH
Blocks amended Stage A freeze: YES
G6-01 disposition: NOT CLOSED
R4.2f verdict: NOT FREEZE-READY

END FINDING
SL-PT-001 | GPT R4.2f CLOSURE FINDING G7-02
Reviewer: GPT - Independent Hostile Reviewer
Date: 2026-11-26
Reference: R4.2f, repository commit 6948668

G7-02 - INJECTED TER Schema Contradiction

Section: Section 10.4, INJECTED-origin terminal-path row.

Mechanism:
The new injection row simultaneously requires every applicable rule result and requires collections to be empty. Rule results are explicitly classified as a collection.

Additionally, the row permits NO_DECISION (QUOTE_INVALID) while requiring a constructed proposal, although quote validation failure prevents proposal construction.

Concrete counterexamples:
1. An R4 injection produces a valid REJECTED disposition with R4 marked FAIL. Its rule-results collection must be populated and empty simultaneously.
2. An injection contains an invalid fixture quote. Its expected terminal state is NO_DECISION (QUOTE_INVALID), but the schema requires a proposal that must not have been constructed.

Smallest correction:
Separate the INJECTED schema into three terminal paths:
- V12a failure.
- Invalid fixture quote.
- Constructed proposal resulting in REJECTED or SHADOW_EXPIRED.

Specify field presence, nullability, evaluated checks and collection contents independently for each path.

Only bar-related collections should be universally empty.

Severity: HIGH
Blocks amended Stage A freeze: YES
G6-05 disposition: NOT CLOSED
R4.2f verdict: NOT FREEZE-READY

END FINDING

CLOSURE INSTRUCTIONS
Resolve both findings through the smallest targeted amendment.
Preserve previously closed findings: G6-02, G6-03, G6-04, G6-06.
Carry forward the X8/X10 retained-test-output clarification for founder acceptance.
No architectural expansion is required.

Provenance: structured restatement of GPT's original review findings, not a verbatim repository artifact.
