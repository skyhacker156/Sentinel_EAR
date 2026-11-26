SL-PT-001 R4.1 — Independent Stage A Hostile Review
Review date: 2026-11-26
Target repository: https://github.com/skyhacker156/Sentinel_EAR
Target commit: 0a4ddaf598f56caede262cc6b5204e7cbc45026f
Candidate path: experiments/sl-pt-001/SL-PT-001_R4.1_Stage_A_Review_Candidate_Claude_2026-11-25.md
Candidate blob: a653252a8b184f0e184c7f2b42b4dbba6ff49d3f (as identified in the Founder dispatch)
Founder record: experiments/sl-pt-001/SL-PT-001_Founder_Decision_Record_v2_2026-11-25.txt
Founder record blob: 801f7a57f5a87220a44f0bbc3e262e2704fdf77b
Classification: Independent hostile specification review; no implementation, test execution, credentials, broker connection, or order authority.
1. Independence and review provenance
Prior exposure disclosure: Before this review, I had reviewed the R3 specification and had seen Claude's earlier R3 findings and review material. I have not used those findings as evidence for the conclusions below. This review is based on the R4.1 candidate and Founder Decision Record v2 at the target commit.

The candidate was retrieved from the exact commit path stated above. Its retrieved text is 981 lines. The Founder Decision Record v2 was also retrieved from the same commit path and is 16 lines. The candidate blob identifier above is the identifier supplied in the dispatch; I did not independently resolve the Git tree metadata to verify that blob identifier. Accordingly, the review identifies the exact commit and path actually read, while not claiming an independent Git-object verification of the supplied blob ID.

The six supplied text chunks were used as review aids. Their chunk wrappers are not a substitute for the committed repository object. No later working-tree version was substituted.

Scope actually reviewed: R4.1 §§2–7, §8.1, §§10–11, §13, Stage A tests in §14, Stage A rows in §§15–16, and Founder Decision Record v2. Stage B text was read only where a Stage A dependency or boundary ambiguity required it. Stage B design is not certified by this review.

No tests were executed. All test cases in §14 are labelled DESIGNED and NOT EXECUTED in the candidate. This review does not authorize implementation, freeze, harness build, credentials, trading-host access, or any paper or live order.
2. Required verdict
NOT FREEZE-READY
R4.1 has a coherent high-level Stage A/Stage B separation and several sound fail-closed concepts. However, Stage A is not implementable as a single deterministic specification within the declared freeze boundary. The Stage A proposal path depends on sizing and reservation rules that are either absent from Stage A or placed in an expressly excluded Stage B section. In addition, the Stage A pre-flight requires a clock measurement that the specification says can only be obtained from a response fetched after pre-flight, and the clock-offset arithmetic does not establish the bound claimed.

These are specification defects, not implementation defects. They must be corrected before a Stage A freeze can define a single unambiguous implementation.
Single most important blocker
G-01 — Stage A proposal sizing and cash reservation are undefined inside the Stage A freeze.
Other freeze blockers
- G-02 — V12 pre-flight has a circular dependency on a bars-response header that is not available until after V12.
- G-03 — The HTTP Date-header/receipt-time calculation does not mathematically bound clock offset because response transit time is unbounded.
No Stage B-only issue is used to block the Stage A freeze.
3. Findings
G-01 — Stage A proposal sizing and cash reservation are not specified within the Stage A freeze
1. Exact section or requirement: §§0.2, 7.1, 7.3 (R6, R7, R10), 7.4, 8.1; §14 U33, U81, U82.
2. Severity: Critical.
3. Failure mechanism:
   - A live-data cycle produces a BUY signal and passes quote validation.
   - §7.1 requires construction of q and R, and §7.3 then evaluates R6 (R ≤ cash_available), R7 (R ≤ $150), and R10 (quantity minimum/increment and price increment).
   - §7.1 sends the reader to §8.2 for q and R.
   - But §0.2 explicitly excludes §8.2–§8.6 from the Stage A freeze and classifies them as Stage B draft. Stage A §8.1 supplies only opening cash, the no-simulated-fills rule, and same-cycle reservation release. It does not define the Stage A quantity calculation, reservation calculation, cash_available, the fee-reserve factor, or the budget from which quantity is derived.
   - §7.4 says the policy file will carry f_res and venue increment fields, but it does not supply the missing Stage A sizing algorithm. U33/U82 specify expected outcomes such as quantity flooring and budget selection without defining the calculation that produces them.
   - Two conforming Stage A implementations can therefore calculate different q and R, or cannot calculate them without importing a Stage B rule that the freeze map excludes.
4. Consequence: The core Stage A proposal and policy pipeline is not deterministic or implementable from the frozen Stage A sections. R6/R7/R10 outcomes, shadow reservations, and the evidence later audited can differ between implementations. A test result for U33 or U82 would not be reproducible from the Stage A specification alone.
5. Evidence:
   - §0.2 lists §8.1 as Stage A and §8.2–§8.6 as Stage B draft, and says Stage B sections are not part of the Stage A freeze.
   - §7.1 expressly says to construct q and R using §8.2.
   - §7.3 defines R6 in terms of cash_available and R10 in terms of min_order_size and qty_increment.
   - §8.1 does not define the sizing formula or cash_available.
   - §14 U33 expects quantity flooring; U82 expects budget = cash_available; U81 expects a minimum-size rejection.
6. Smallest sufficient correction: Put a complete Stage A-only sizing and shadow-reservation rule in a Stage A section (preferably §8.1 or §7). It must define, without relying on Stage B text:
   - the Stage A budget source;
   - the formula for q and the exact quantity-flooring operation;
   - the fee-reserve factor and the formula for R;
   - the definition of cash_available and whether/how reserved_usd is represented during the cycle;
   - when the reservation is created and released; and
   - the exact policy-file values used by Stage A, including their conditional/unverified status.
   If the founder does not want Stage A to exercise sizing, remove sizing-dependent policy checks and proposal claims from Stage A and narrow the Stage A mission accordingly. Do not silently import §8.2 into the Stage A freeze.
7. Stage A freeze blocker: Yes.
8. Confidence: High.
G-02 — V12 pre-flight requires a clock measurement that is only available after the fetch it is required to precede
1. Exact section or requirement: §§4.7–4.7 V12, 5.6, 6.4 step 1.
2. Severity: High.
3. Failure mechanism:
   - §4.7 says V12 pre-flight runs first, before any fetch, and that a V12 failure means no fetch happens.
   - §6.4 defines V12 as including an offset measurement and the test |offset_estimate| ≤ 2 s.
   - §5.6 defines offset_estimate using the HTTP Date header of the bars response minus the harness receipt instant.
   - That response does not exist until after the bars request is made, which §4.7 says cannot occur until V12 has passed.
   - No prior-cycle estimate, separate time-probe request, or other pre-fetch measurement source is specified as a substitute.
4. Consequence: A literal implementation cannot evaluate all of V12 before the first fetch. It must either violate the stated order, invent an unapproved measurement source, or fail the pre-flight. This affects every scheduled cycle, not merely an unusual boundary case.
5. Evidence: §4.7 explicitly says V12 runs first before any fetch. §5.6 defines the measurement from the bars response's Date header. §6.4 includes the measurable-offset check inside that first pre-flight.
6. Smallest sufficient correction: Define a measurement source available before the decision-data fetch. Options include a separately specified keyless time-probe request that is expressly permitted during pre-flight, or a trusted local time source with a stated bound. If a prior-cycle measurement is intended, define its age limit, reuse rule, and failure behavior. Then state exactly which network activity is permitted before V12 passes and test the first-ever cycle as well as subsequent cycles.
7. Stage A freeze blocker: Yes.
8. Confidence: High.
G-03 — The Date-header/receipt-time calculation does not establish the claimed clock-offset bound
1. Exact section or requirement: §5.6; §6.4 V12; §15 U-T2; §14 U79.
2. Severity: High.
3. Failure mechanism:
   - Let S be the data server's clock at the instant it creates the HTTP Date header, L the elapsed time from that header being created to the harness receipt instant, and ε the whole-second truncation error (−1 s < ε ≤ 0).
   - The estimate is Date_header − harness_receipt.
   - It therefore reflects the actual server/harness clock difference minus response transit/processing time, plus truncation. The error is not limited to the one-second header resolution.
   - No upper bound on L, no maximum response time, and no interval calculation using request-send and response-receipt times is specified.
   - For example, a server clock that is four seconds ahead combined with approximately two seconds of response transit can produce an estimate near +2 seconds and pass the stated threshold, even though the actual clock difference exceeds the asserted bound.
4. Consequence: |offset_estimate| ≤ 2 s does not prove the harness clock is within about three seconds of the data host. Time comparisons that rely on this estimate—including completed-candle selection and quote freshness—remain less bounded than the specification claims.
5. Evidence: §5.6 states that the estimate is Date header − harness receipt instant and attributes its error to header truncation in (−1 s, 0]. The same section derives an approximately three-second clock relationship from the two-second threshold plus one-second resolution. It does not include network transit time in the derivation. U79 tests only values of the resulting estimate at the threshold; it does not test whether the estimate is a valid bound on actual skew.
6. Smallest sufficient correction: Replace the point estimate with a defensible offset interval. Record request-send and response-receipt instants, bound the interval in which the server generated the header, include the header's one-second quantization, and define a maximum permitted uncertainty/round-trip time. Fail closed when the resulting interval cannot prove the accepted clock bound. Alternatively, use a time source whose error bound is independently specified and measured. Update U79 to test latency and uncertainty, not just the numeric threshold.
7. Stage A freeze blocker: Yes.
8. Confidence: High.
G-04 — CONFIRMED has two incompatible meanings in the revision store
1. Exact section or requirement: §4.9; §14 U35, U39, U40.
2. Severity: Medium.
3. Failure mechanism:
   - On a first-ever observation, §4.9 says a bar not in the store is added as CONFIRMED.
   - The same section later defines CONFIRMED to mean only that the source returned the same bytes on two fetches.
   - U35 explicitly expects all bars in an empty store to become CONFIRMED on the first observation.
   - Thus the state label asserts a two-observation property when the first-observation path has only one observation.
4. Consequence: The revision-store state and its audit meaning are ambiguous. A reviewer may read a CONFIRMED first-seen bar as having survived a repeated observation when it has not. This does not necessarily change the conservative decision rule, because the candidate intentionally treats the first observation as the baseline, but the evidence vocabulary is inaccurate.
5. Evidence: §4.9 first row (“t not in the store”) sets the state to CONFIRMED; the later “What CONFIRMED means” paragraph says it means the source returned the same bytes on two fetches. U35 expects confirmation on first observation.
6. Smallest sufficient correction: Rename the first-observation state to BASELINED/`FIRST_SEEN`, or redefine CONFIRMED to mean “accepted as the current baseline after the specified observation rule” and separately record the observation count. Preserve the founder's intended first-cycle behavior explicitly. Add tests for the exact state labels and audit reconstruction.
7. Stage A freeze blocker: No, provided the state semantics are corrected before implementation and the audit does not treat first-seen bars as two-fetch-confirmed.
8. Confidence: High.
G-05 — A proposal-cycle crash can leave fetched artifacts without a chain event linking them to the invocation
1. Exact section or requirement: §§6.4, 10.1–10.2, 11.2; §14 U75, U77.
2. Severity: Medium.
3. Failure mechanism:
   - A proposal cycle fetches and stores raw responses before parsing.
   - For a proposal, the CYCLE record is not committed until REJECTED or SHADOW_EXPIRED at the ceiling (§6.4).
   - If the process terminates after storing one or more response artifacts but before the terminal CYCLE commit, the invocation log has a wrapper line but the chain has no CYCLE record referencing those artifacts.
   - The artifacts may remain in the content-addressed directory, but §10.1–§10.2 define no orphan-artifact event or inventory that binds them to that invocation. The auditor can classify the slot as missing and flag the invocation mismatch, but cannot reconstruct which response artifacts belonged to the interrupted cycle from the specified chain.
4. Consequence: The slot correctly fails to qualify, so this does not create a false qualifying cycle. However, the stronger statement that every observation remains in the chain is not true for interrupted proposal cycles, and the retained orphan files are not independently attributable through the defined evidence chain.
5. Evidence: §10.2 says raw responses are stored before parsing and referenced by hash from CYCLE records. §6.4 delays the proposal CYCLE commit until REJECTED or SHADOW_EXPIRED. §11.2/U77 detects invocation/chain mismatches, but no event type records a fetched-but-uncommitted proposal cycle or its artifact hashes.
6. Smallest sufficient correction: Either (a) add a durable CYCLE_START/`CYCLE_PROGRESS` event before the first fetch and append artifact references as they are produced, or (b) explicitly classify unreferenced artifacts as orphaned/untrusted, prohibit their use in reconstruction, and narrow the “every observation remains in the chain” claim. The latter is smaller and remains fail-closed.
7. Stage A freeze blocker: No, if orphan artifacts are explicitly non-evidence and a missing slot can never qualify. It is a completeness/claim limitation that should be corrected before implementation.
8. Confidence: High.
G-06 — U9 requires a REPLAY flag that has no defined representation in the closed schema or event set
1. Exact section or requirement: §§10.1, 10.4, 11.1; §14 U9.
2. Severity: Low.
3. Failure mechanism:
   - U9 expects replayed stored artifacts to produce a byte-identical TER body, be “flagged REPLAY,” and never be appended.
   - The TER schema is declared closed and has origin ∈ {SCHEDULED, INJECTED}; it has no REPLAY field or origin.
   - The chain event list has no REPLAY event type, and REPLAY is not a terminal state in §11.1.
   - The test does not say whether the flag belongs to an external test report, a non-persisted wrapper output, or the TER itself.
4. Consequence: The expected result is not implementable exactly as written without inventing an extra-schema field or an out-of-band convention. This is not a live-cycle safety defect if replay output is kept outside the evidence chain.
5. Evidence: §10.1's event-type list; §10.4's closed TER fields and two-value origin enum; §11.1's closed terminal states; §14 U9.
6. Smallest sufficient correction: State that REPLAY is an out-of-band test-run label and is never part of the TER body or chain, or define a separate test-result schema. Keep the production TER schema closed.
7. Stage A freeze blocker: No.
8. Confidence: High.
G-07 — Stage A credential-absence language is broader than the specified pre-flight check
1. Exact section or requirement: §§2.2–2.3, 6.4 V12; §14 X9; §15 U-I1.
2. Severity: Medium.
3. Failure mechanism:
   - §2.2 says no broker credential exists in the harness environment, and Branch C's rationale says the absence of credentials means an unexcluded egress path cannot authenticate an order.
   - V12 is specified only as “no credential in the environment”; X9 tests a credential placed in the environment.
   - The candidate does not define whether “environment” means process environment variables only, or also configuration files, user credential stores, inherited handles, local agents, or other credential sources accessible to the process.
   - Branch C explicitly does not exclude alternate egress paths. If credentials can be obtained from an unexamined source, the rationale that alternate egress cannot authenticate is stronger than the specified check establishes.
4. Consequence: The chosen Branch C limitation is candid about network isolation, but the compensating credential-absence assertion is underspecified. Readers may infer a stronger no-credential guarantee than V12 and X9 demonstrate.
5. Evidence: §2.2's “no credential exists in the harness environment”; §2.3's Branch C rationale; §6.4 V12; X9; §15 U-I1.
6. Smallest sufficient correction: Narrow the claim to the exact sources actually checked (for example, “no configured broker credential variables are supplied to the harness process”), and state that credentials in other stores are not excluded; or enumerate and check the complete set of credential sources the process can access. Keep the Branch C limitation statement verbatim.
7. Stage A freeze blocker: No, if the claim is narrowed and no Stage A result implies process/host isolation or comprehensive credential absence.
8. Confidence: Medium.
4. Test and evidence adequacy
All §14 tests are DESIGNED and NOT EXECUTED. The following distinctions matter:
4.1 Tests that are directionally useful
- Strategy and exact arithmetic: U1–U4e, U18, U24, U25 and U87 address crossover boundaries, quote independence, zero-volume parsing and exact arithmetic.
- Candle selection and data quality: U5–U8, U11–U13, U17, U78, U84, U89 and U94 cover several important boundaries for completion, missing data, duplicate timestamps, pagination and revisions.
- Slot and invocation behavior: U15, U19, U52, U73–U77, U83 and U91 cover late invocations, overruns, missed slots, restart, sleep/resume, invocation mismatches and injection interruption.
- Audit integrity: U26, U27, U34, U41–U43 and U66–U72 test state classification, missing/duplicate/off-grid slots, recomputation, manifest consistency, chain alteration and origin/cycle identity.
- Quote and policy boundaries: U28, U33, U80–U82 and X1–X7 cover quote age, quantity flooring, invalid quote fields and several policy failures.
These are useful test designs, not evidence that the controls work.
4.2 Missing or insufficient Stage A tests
1. No test resolves G-01. U33 and U82 state expected quantity/budget outcomes, but there is no complete Stage A formula in the frozen text against which the expected values can be independently derived.
2. No test resolves G-02. U79 tests the value of offset_estimate; it does not test how V12 obtains that value before any fetch. Add a first-cycle test proving the complete pre-flight sequence.
3. No test resolves G-03. No test injects variable HTTP response delay while comparing the Date-header estimate with a known clock offset. Add latency/uncertainty cases, including a server offset outside the accepted bound that is masked by response transit.
4. Revision state semantics: U35 should assert the chosen first-observation state, not call it two-fetch confirmation. Add a first-observation then changed-second-observation case.
5. Crash boundaries: U75/U77 are broad. Add fault injection at each boundary: after invocation-log append; after bars response storage; after quote response storage; after bar-store transition calculation; immediately before CYCLE append; during CYCLE append; and after chain append but before process exit. Expected orphan/missing classifications should be explicit.
6. Replay representation: U9 needs an explicit out-of-band result format or separate test schema.
7. Credential scope: X9 only tests a credential placed in the environment. If the claim covers other stores, add corresponding negative tests; otherwise narrow the claim.
8. Data identity: the Stage A data contract should explicitly bind the returned bars and quote to BTC/USD, not rely solely on the request URL. Add a wrong-symbol response test unless the response schema itself makes the symbol binding structurally unambiguous and that binding is recorded.
9. No executed evidence exists yet. This is not by itself a freeze defect—the candidate expressly says tests are not executed, and §11.6 defines a pre-live executed-test gate. It does mean the review cannot certify operational behavior or say any control has passed.
5. Stage boundary and authority assessment
Sound as written
- Stage A vs Stage B is clearly mapped. §0.2 identifies the Stage A freeze set and explicitly excludes §8.2–§8.6, §9 and §12. Founder Decision Record v2 confirms that distinction.
- Branch C is candidly limited. §2.3 expressly says only the harness HTTP-client allowlist and absence of credentials are relied upon; alternate process/host egress is not excluded. It forbids Stage A claims of process-level or host-level isolation.
- No Stage B order authority is granted. The candidate says it is not frozen, not implemented, not verified, and grants no credentials, trading-host connection or order. Founder Decision Record v2 independently says no freeze, FD-5 harness build, paper credentials, Stage B implementation or order is authorized.
- Stage B-specific uncertainties are not used as Stage A blockers. TIF, paper fee behavior, venue metadata, COID semantics, approver authentication, send-time bounds and the BUY lifecycle reconstruction are properly deferred to Stage B/Stage C gates.
- No round trip or expanded trading mission is introduced. The milestone remains one governed BUY with a confirmed fill, terminal state, reservation/fill reconciliation, independent lifecycle reconstruction and recorded residual BTC exposure.
Claims that are appropriately limited
- §13 does not claim profitability, significance, robustness, market-data truth, broker behavior, G-07 properties, or process/host isolation.
- §4.9 correctly says that repeated identical bytes do not prove a bar is final or will never change again.
- §15 marks bar finality, Task Scheduler behavior, Date-header accuracy and process/host isolation as unverified or not established.
- The chain-completeness limitation in §11.3 is stated: completeness is relative to GENESIS and what the founder pushed.
Claims that need qualification
- The approximately three-second clock relationship in §5.6 is not derived unless response transit time is bounded (G-03).
- The statement that no credential exists in the harness environment needs an exact definition of the credential sources checked (G-07).
- “Every observation remains in the chain” needs an interruption qualification because a proposal cycle may fetch artifacts but terminate before its delayed CYCLE commit (G-05).
- CONFIRMED should not be described as a two-fetch property when the first observation is immediately labelled CONFIRMED (G-04).
6. Requirements that are sound as written
Subject to the blockers above, the following Stage A design elements are internally coherent and appropriately bounded:
1. Mission and scope: one governed BUY remains the eventual mission; Stage A itself remains keyless, read-only, and shadow-only.
2. Crossover definition: the literal inequalities in §3.2 are mutually exclusive and exhaustive, and the equality edge cases are explicit.
3. Signal independence: §3.4 separates close-derived SMA signal computation from quote-dependent proposal/policy evaluation.
4. Candle completion: with T_d aligned to the five-minute grid plus the accepted 60-second settle interval, the stated t_exp = T_d − 360 s follows from the completion rule.
5. Data failures: missing bars, duplicate timestamps, malformed values, stale series, incomplete pagination and pending revisions are assigned non-qualifying failure states.
6. Zero-volume treatment: exact zero is retained rather than silently filtered or interpolated; the strategy consequence is explicitly called out.
7. Exact arithmetic: the rational/inexact-trap approach and named rounding points are conceptually coherent, assuming the implementation language actually enforces them.
8. Slot identity: the half-open slot interval and cycle identity based on the expected completed candle are clear.
9. Audit denominator: missing slots remain in the denominator; the harness's own counter is not treated as evidence.
10. Claim restraint: the candidate does not equate thirty qualifying slots with thirty trades or claim strategy performance from the Stage A sample.
7. Explicitly accepted or safely deferred residual risks
These are not Stage A freeze blockers on the stated scope, provided they remain disclosed and are not silently promoted into Stage A guarantees.
Item	Status	Review disposition
Branch C does not prove process/host isolation	Founder accepted; disclosed in §2.3	Safe to defer for Stage A only if the limitation statement remains attached to every result and credential claims are narrowed as in G-07.
No second market-data source	Explicit single-source limitation	Acceptable for a bounded Stage A shadow experiment; no claim about market-data truth.
Bar finality and revision behavior	UNVERIFIED, §15 U-D4	Safe to defer as long as the two-observation state is described accurately and pending revisions fail closed.
Date-header accuracy against UTC	UNVERIFIED, §15 U-T2	Not safe to use as a clock bound until G-02/G-03 are corrected.
Task Scheduler settings and behavior	UNVERIFIED, §15 U-T1	Can remain a pre-run operational verification gate; must be evidenced from exported XML and observed behavior before the first run.
Live-data exercise of long-position branches, R8 and R12	OI-08	Founder has explicitly left this for Stage A exit acceptance. The limitation is acceptable if reported; synthetic fixtures are not live-data evidence.
Number of slots needed to reach 30 consecutive qualifying slots	UNBOUNDED, §15 U-O2	Acceptable; this is an experiment-duration uncertainty, not a correctness defect.
Common-mode risk in the same FD-6 script performing reconstruction and slot audit	UNBOUNDED, §15 U-O4; founder decision retained despite dissent	Explicitly disclosed and accepted as a founder decision. It must not be described as independent verification against a separately authored auditor.
Venue increments, minimums, fee behavior, paper fills and account configuration	Stage B, §15 U-V1 to U-V6	Correctly deferred to Stage B pre-flight; they must block any Stage B order until verified.
Approver authentication, COID retry behavior, independent broker reconciliation and send-time bound	Stage B, FD-9 / §15 U-G1–U-G2	Correctly deferred; no Stage B authorization follows from this review.
Stage B BUY lifecycle reconstruction	OI-15	Remains a Stage B freeze blocker, not a Stage A freeze blocker.


8. Smallest set of changes required for Stage A freeze readiness
The minimum correction set is:
1. Resolve G-01: add a complete Stage A sizing and shadow-reservation contract inside the Stage A freeze boundary, or remove sizing-dependent Stage A proposal behavior and narrow the Stage A mission. Do not rely on excluded Stage B §8.2.
2. Resolve G-02: make the V12 clock measurement available before V12 is evaluated, or explicitly permit and define a separate pre-flight time-probe request.
3. Resolve G-03: replace the point estimate with a mathematically defensible clock-offset interval that accounts for response transit and header quantization; define the failure threshold and test it.
4. Correct G-04 and G-05 wording/evidence semantics: distinguish first-seen from two-fetch-confirmed bars, and explicitly classify orphaned artifacts after interrupted cycles.
5. Clarify G-06 and G-07: define REPLAY as out-of-band test metadata, and narrow the credential-absence claim to the stores actually checked.
6. Add the missing tests listed in §4.2 to the Stage A inventory. The tests remain DESIGNED until implementation and retained execution evidence exist.
After these edits, a fresh review should verify that the Stage A freeze set is self-contained and that the fixes did not introduce a Stage B dependency. A freeze decision remains the Founder's authority.
9. Final disposition
NOT FREEZE-READY.

The R4.1 Stage A boundary is substantially clearer than a combined Stage A/Stage B specification, and the document is appropriately restrained about what the experiment can prove. That does not cure the three core specification failures: the Stage A sizing algorithm is outside the freeze, V12's clock pre-flight is circular, and the stated clock-offset bound is not mathematically supported by the measurement described.

No implementation, test execution, harness authorization, credential access, trading-host connection, or order is authorized or recommended by this review.