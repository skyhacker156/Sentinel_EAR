GPT Closure Check: SL-PT-001 R4.2a
NOT FREEZE-READY
4 findings substantially closed
New issues identified

Review date: 2026-11-26
Reviewer: GPT
Scope: R4.2a, Stage A only, against the R4.2 closure reconciliation.

Exposure statement: I reviewed the uploaded R4.2a specification, including the revised clock logic, Stage A sizing, TER schema, audit precedence, test inventory, open-items register and review-integrity record. I also independently recalculated all four U105 sizing vectors using exact rational arithmetic.

No repository checkout, harness execution, implementation, or test execution occurred. This is a document-level closure review, not empirical verification.
1. Previous findings: closure determination
Finding	Result	Assessment
G3-01	CLOSED	Strict RTT ceiling correctly implemented
G3-02	CLOSED	Undefined offset estimate removed from TER fields
G3-03	PARTIAL	Early-exit encoding improved, but request metadata remains underspecified
G3-04	CLOSED	All four U105 arithmetic vectors independently reproduced
G3-05	CLOSED	Backward clock check and strict boundary corrected

G3-01 / G3-05: Clock boundary
Verdict: CLOSED.

R4.2a now requires:
1. Valid HTTP Date header.
2. t_recv ≥ t_send.
3. Round trip strictly less than 3 seconds.
4. Both interval bounds within ±2 seconds.
The important correction is condition 3:
\[
t_{recv}-t_{send}<3s
\]

The interval width is:
\[
\theta_{high}-\theta_{low}=1s+RTT
\]

The previous inclusive checks alone admitted exactly 3 seconds. The new explicit ceiling excludes that case.

U79 tests the exact ±2-second endpoints. U98 addresses the 3-second boundary.

The mathematical reasoning is sound under assumptions A-CLK and A-CLK2. The resulting guarantee is strictly stronger than the original point-estimate bound.

Remaining qualification: This does not establish either clock's accuracy against UTC. The document correctly preserves that limitation. 
Pasted text(20261126-161234).txt

G3-02: Undefined offset estimate
Verdict: CLOSED.

The undefined offset_estimate field is no longer in the TER field list.

The defined clock fields are now:
- t_send
- t_recv
- D
- θ_low
- θ_high
This removes the previous undefined-field problem. 
Pasted text(20261126-161234).txt

G3-03: Early-exit TER encoding
Verdict: PARTIALLY CLOSED.

The new PASS / FAIL / NOT_EVALUATED scheme is a meaningful improvement.

The document now distinguishes:
- V12a failure;
- V12b failure;
- data validation failure;
- HOLD / NO_ACTION;
- proposal and quote-invalid paths.
It also explicitly provides null handling for absent artifacts, clock fields and computed values.

However, I found a remaining schema defect.

G3-06: Early-exit request metadata is not fully specified.

The closed TER field list requires:
request URLs and instants

But consider two terminal paths:
- V12a fails before any fetch.
- V12b fails after the bars request but before the quote request.
The table specifies absent artifacts and clock fields, but does not define how the request URL and request-instant fields are encoded when a request was never issued.

The specification also says every field must be present and omission is invalid.

Consequently, U108 cannot yet be considered fully specified for these paths. The author needs to define the exact representation of an unissued request and its absent timestamp, along with the empty collection representation for paths with no fetched bars or bar-store transitions.

This is a schema-completeness problem, not a request to change the underlying architecture. 
Pasted text(20261126-161234).txt

G3-04: U105 reproducibility
Verdict: CLOSED.

I independently calculated all four vectors.
All four reproduced
Vector	Quantity	Reservation	Result
A	0.0025	$150.00	Correct
B	0.0024	$144.00	Correct
C	0.0024	$145.96	Correct
D	0.0014	$140.35	Correct

The exact unrounded costs also match:
- A: $149.9990625
- B: $143.9991
- C: $145.955178
- D: $140.35
The cent ceiling and quantity flooring behave as specified.

No discrepancy found. 
Pasted text(20261126-161234).txt
 Pasted text(20261126-161234).txt


2. New findings
I identified two additional document issues.
G3-06: Incomplete early-exit schema
High: closure blocker
Described above.

Required correction:
- Define request URL and timestamp values when a request is not issued.
- Define empty collections for absent observations and transitions.
- Ensure every terminal path has an unambiguous, valid TER representation.
- Update U108 to test those exact representations.
This should be a small specification correction.
G3-07: OI-09 status contradiction
Medium: document integrity
There is an internal inconsistency in the open-items register.

Section 1.1 says OI-09 is CLOSED following Gemini B's R4.1 Stage A review.

Section 17 likewise says Gemini B's clean review closed OI-09.

However, §16.2 still lists OI-09 as OPEN and blocking the Stage A freeze.

These three statements cannot simultaneously describe the same item status. 
Pasted text(20261126-161234).txt
 Pasted text(20261126-161234).txt
 Pasted text(20261126-161234).txt

Recommendation: Remove OI-09 from the open register if the recorded R4.1 review fully satisfied it. Otherwise, explicitly identify the remaining founder acceptance requirement.
Minor reproducibility observation: U98
The test describes an interval centred exactly on zero with a 3-second-minus-1-nanosecond round trip.

Given integer-nanosecond endpoints, the interval width is 3,999,999,999 ns, an odd number. It cannot be exactly symmetric around zero.

This does not invalidate the expected PASS result. However, the fixture should specify its actual endpoints or use a representable centre.

I classify this as a low-severity test-definition clarification, not a freeze blocker.

3. OI-18: Founder decision remains outstanding
Founder action required
The revised implementation is mathematically coherent.

However, the decision record v2 names:
\[
|\text{offset\_estimate}|\leq 2s
\]

R4.2a instead uses an interval test with a strict latency ceiling.

That is a more conservative measurement procedure, but it is not literally the same measurement.

I agree with Claude that this requires explicit founder acceptance.

I am not treating technical correctness as authorization to reinterpret the founder's decision.

The proposed one-line decision record v3 remains appropriate.

4. Overall assessment
Area	GPT determination
Clock mathematics	Closed
Clock boundary handling	Closed
Clock schema	Closed
Sizing arithmetic	Closed
Shadow reservation	Consistent
Early-exit TER encoding	Incomplete
Audit precedence	Consistent on reviewed paths
Open-items register	One status contradiction
Stage B dependencies	No new dependency identified
Implementation evidence	None
Test execution	None

Important distinction: The specification remains a design candidate. U79, U98, U105 and U108 are designed tests, not executed evidence.
5. Recommendation to Claude
My recommendation is to produce R4.2b, rather than freeze R4.2a.

The correction package should be limited to:
1. Close G3-06 by completing the early-exit request metadata encoding.
2. Correct the OI-09 register inconsistency.
3. Clarify the U98 exact interval fixture.
4. Preserve the existing clock mathematics and U105 sizing calculations without unnecessary redesign.
Then request a narrow closure check of those changes.

No reason has emerged to reopen the broader architecture or Stage B.

6. Freeze gate
The following remain necessary:
- [ ] R4.2b correction and GPT closure check.
- [ ] Gemini B independent clean-excerpt closure check.
- [ ] OI-18 founder confirmation in decision record v3.
- [ ] Founder Stage A freeze decision naming the exact committed blob and scope.
Final verdict: R4.2a is materially improved and the previous clock and arithmetic blockers are resolved. However, I do not recommend freezing it yet.

The remaining work is specification closure, not architectural redesign.