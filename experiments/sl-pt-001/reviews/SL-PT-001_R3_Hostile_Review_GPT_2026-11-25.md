SL-PT-001 R3 Hostile Review — GPT
"Prior exposure: before this review I saw Claude's self-findings SF-1 to SF-3 and Claude's annex S2. Any of my findings that overlap them is not independent detection."

Date: 2026-11-25
Reviewer: GPT
Scope: Specification review only. No implementation, test execution, harness construction, trading connection, credentials, or orders.
Review set: R3, First-Trade Closure Package, R1 (retained §3 and §6), SMA20-50 amendment v0.2, Stage A Design v0.1, and G-07 Draft 0.3, as reproduced in the dispatch.
1. Verdict
NOT FREEZE-READY
R3 is materially more explicit than its predecessors. It separates signal computation from quote use, defines exact timing inequalities, introduces a positive milestone allowlist, explicitly accounts for missing scheduled slots, and retains the distinction between Stage A evidence and Stage B execution controls.

Those improvements do not yet make the specification safe to freeze. The most serious defect is that the reservation model is not a complete accounting model for both cash and BTC exposure. Other material gaps concern the audit's ability to distinguish genuine scheduled-cycle records from malformed or misclassified records, the lack of a bounded Stage A clock assumption, and the absence of a fully specified scheduler/slot contract.

The review distinguishes four levels:
1. Specified: the rule is written.
2. Reconstructible: an independent reviewer can determine the required result from the defined inputs and records.
3. Enforceable: the implementation can prevent forbidden transitions under concurrency, crashes, and timing races.
4. Demonstrated: executed evidence establishes the property in the stated environment.
R3 is strongest at level 1. It has not demonstrated levels 2–4. No tests have been executed; every test result below is a proposed expected result, not evidence.
2. Critical findings
G-01 — Reservation accounting is incomplete across asset units and fill lifecycle
Severity: CRITICAL
Sections: R3 §§2.3, 6.1, 6.4–6.6, 8 R9/R16; G-07 §8 C.2.

Failure mechanism

The ledger defines Reservation as (auth_id or shadow proposal_id, amount, state) and defines cash_available by subtracting unreleased reservation amounts. That is a cash-only representation. Yet R9 requires q_exit ≤ held − reserved BTC, while no corresponding reserved-BTC field, unit, lifecycle, or invariant is defined.

The fill rule also mixes unlike quantities. The reservation is reduced using ceil_cent(q_f × L × (1 + f_res)), while booked spend is described as reported q_f × p_f plus any reported USD fee. G-07 explicitly acknowledges fee assets may differ, but R3 does not define how a BTC-denominated fee changes held BTC, net acquired quantity, or the BTC reservation. Nor does R3 define how non-USD fees are valued for cash/exposure accounting.

A partial-fill event can also be replayed, duplicated, corrected, or busted. There is no cumulative-fill identity or monotonicity rule preventing the same fill from reducing a reservation twice. A cancel request leaves the reservation unchanged, correctly, but the handling of fills arriving while cancellation is pending and of an AMBIGUOUS outcome needs a cumulative, idempotent ledger transition model.

Finally, the invariants are not tied to an atomic transaction boundary. The text says at most one unreleased BUY reservation exists, but does not define how reservation creation, authorization issuance, fills, reconciliation, and terminal release serialize against one another.

Consequence

A literal implementation can understate held-BTC commitments, double-apply fills, misstate fee exposure, or release a reservation while an unresolved fill/cancel outcome remains possible. The stated “no double allocation” conclusion is therefore not established.

Smallest required correction

Define two typed reservation balances (USD cash and BTC quantity), with explicit units and fee-asset treatment. Define an append-only, idempotent fill-event identity and cumulative-fill reconciliation rule, including corrections/busts. Specify atomic ledger transitions and the exact evidence required before releasing each asset reservation. Do not claim FC-E closed until those rules are present.
G-02 — Stage A clock validity is measured but not bounded
Severity: HIGH
Sections: R3 §§3.3–3.5, 4.2–4.4; R1 §6; CF-4 and CF-8.

Failure mechanism

Stage A uses the harness clock to decide whether bars are complete and quotes are fresh. R3 requires an offset estimate from the bars HTTP Date header, but explicitly imposes no skew bound. V12 requires only that the offset was measured. The header has one-second resolution and is measured against the harness receipt time; it is not an authoritative, high-resolution clock guarantee.

The quote test 0 ≤ checkpoint − quote.t ≤ 15 s is exact as an inequality, but the checkpoint instant is not fully defined (for example, request start, response receipt, or the time immediately before policy evaluation). A clock that is materially wrong can therefore make an incomplete bar appear complete or a fresh quote appear future-dated/stale while still passing the “offset measured” condition.

Consequence

Stage A can produce a deterministic answer to the wrong temporal question. Exact arithmetic does not cure a wrong clock.

Smallest required correction

For Stage A, either define an explicit maximum acceptable offset and the exact checkpoint timestamp, or state that Stage A results are conditional on an unbounded harness clock and cannot qualify for any timing-dependent milestone claim. For Stage B, FD-G18 must define σ, its measurement cadence, failure threshold, and monotonic/wall-clock responsibilities before Stage B text is considered complete.
G-03 — Slot scheduling and manifest boundaries are not fully reconstructible
Severity: HIGH
Sections: R3 §§5.2–5.4, 9.3; FD-7; closure package §4.

Failure mechanism

The slot ledger is a good improvement, but its anchor and run-boundary contract is incomplete. The manifest says T_d(0) must be :MM:00 + 60 s, but does not explicitly require MM ∈ {00,05,…,55} or fully define how an arbitrary invocation is mapped to a slot relative to that anchor. The timer option is described as a minimal timer but does not specify absolute-time scheduling versus repeated relative sleeps, missed-tick behavior, restart recovery, duplicate wakeups, or whether a late invocation is discarded or assigned to a slot by a monotonic schedule.

The run's declared end determines the denominator. The specification does not fully constrain how the end is committed, whether it can be shortened after the run, or how the auditor establishes that every manifest and every run is included. A run can be incomplete because the timer stopped, the process crashed, or the manifest/report omitted it; the audit must distinguish these cases.

Consequence

A timer can drift, miss, duplicate, or suppress scheduled invocations without the harness itself providing a complete explanation. The audit can detect missing slots only if the manifest set and its declared interval are themselves complete and immutable.

Smallest required correction

Define a UTC slot anchor on a five-minute boundary, an absolute slot schedule, and exact late/missed/restart semantics. Make manifest start/end immutable and committed before the run (or append a separately committed close record that cannot rewrite the original interval). Require a complete invocation/event ledger and a repository-wide manifest inventory in the audit output.
G-04 — Milestone qualification trusts fields that are not yet evidence
Severity: HIGH
Sections: R3 §§9.1–9.4, 11, 12.

Failure mechanism

The positive allowlist is preferable to the old broad terminal-state rule. However, §9.2 says a HOLD qualifies when V1–V12 passed and D was computed from 51 validated candles. The specification does not define a strict record schema, canonical serialization, evidence-reference requirements, or a verifier that independently checks the validation artifacts and recomputes the signal. A record containing V1…V12: true is not itself proof that those validations occurred.

Likewise, injected proposals are excluded by origin: INJECTED, but the specification does not define a closed origin enum and a rule that only origin: SCHEDULED records can be slot records. A malformed or injected record with a missing/incorrect origin could be misclassified. The rules for malformed records, duplicate records with different manifest IDs, and records with conflicting terminal-state fields are not sufficiently specified to ensure they cannot qualify.

Consequence

A malformed, fabricated, or misclassified record could contribute to run_length. A HOLD could hide missing validation evidence if the auditor treats asserted flags as proof. Missing-slot detection does not by itself prove that the one record found for a slot is a valid record.

Smallest required correction

Define a closed, versioned TER schema and canonical serialization. Require a scheduled-origin record bound to exactly one manifest and slot. The auditor must verify hashes and evidence references, parse the raw inputs, and independently recompute the qualification predicate; it must not trust Boolean validation claims. Invalid, unknown, duplicate, or incomplete records must be NON-QUALIFYING and reported.
G-05 — “Exact decimal” is a requirement, not yet a complete arithmetic contract
Severity: HIGH
Sections: R3 §§3.2, 3.6, 3.9, 4.1, 6.2–6.4, 11.

Failure mechanism

R3 correctly requires conversion from original JSON number token text and prohibits binary floating point. But it does not specify the arithmetic engine's precision/context, overflow/underflow behavior, or how exactness is preserved through every intermediate operation. A finite-precision decimal context can round even when no binary float is used.

The policy also combines decimal arithmetic with venue increments, cent ceilings, fee estimates, and fee assets. The exact rule for increment metadata in the policy file is missing: §3.9 says Stage B must compare metadata with the policy file, while R10's policy value is UNVERIFIED; no numeric increment/minimum values are defined in P-0.2.

Consequence

An implementation can satisfy “no float” and still round an intermediate result, or cannot perform the required Stage B metadata comparison because the expected policy values are absent.

Smallest required correction

Specify exact rational arithmetic or a decimal implementation with formally sufficient precision and traps for inexact operations. Define all rounding points and units. Define the schema and versioned source of price increment, quantity increment, and minimum size in the policy artifact; missing or contradictory values must stop.
G-06 — Stage A boundary check does not prove process-level disconnection
Severity: HIGH
Sections: Stage A Design D4; R3 §§3.5 V12, 11 X8–X10; G-07 §8 A.4/E.4.

Failure mechanism

The Stage A walkthrough checks that the HTTP client's allowlist contains only the market-data host and that no trading credential is present in the environment. X8 tests that this client refuses a trading-host request. Those checks do not establish that the process has no alternate HTTP client, raw socket path, proxy route, inherited handle, credential file, or other egress route.

G-07 Draft 0.3 itself recognizes that same-host tests do not transfer to production and calls for deployment-level egress inventory. The Stage A boundary is narrower than that deployment-level guarantee.

Consequence

Stage A may be keyless and read-only by intended code path without being demonstrably disconnected from trading egress at the process or host boundary.

Smallest required correction

Define Stage A as having no trading credentials and enforce network egress outside the application (host firewall or equivalent allowlist) to the market-data endpoint only. Test the actual process boundary, not only the selected HTTP client. Keep all Stage A results explicitly separate from G-07 I1/I5/I8 claims.
G-07 — Quote validation is incomplete, and CF-6 conflates stale with missing quotes
Severity: HIGH
Sections: R3 §§3.5, 4.3, 6.3, 8 R4/R5; §9.2 note CF-6.

Failure mechanism

R4 specifies quote age, and R5 checks the limit price against the mid. The data contract does not define a complete quote-validity predicate for bid/ask presence, positivity, crossed markets, nonnegative displayed sizes, or internally inconsistent fields. A quote may be fresh but structurally invalid.

CF-6 says a REJECTED result due to a stale or missing quote qualifies. A stale quote can still be present and allow a proposal to be constructed and rejected by R4. A missing quote cannot supply the ask/bid needed to construct L and a proposal under §6.3. That makes the stated missing-quote qualification incompatible with §9.2's requirement that a proposal was constructed.

Consequence

A missing quote can be classified as a qualifying REJECTED cycle despite no constructible proposal, or an invalid but fresh quote can flow into proposal construction.

Smallest required correction

Define quote structural validation separately from freshness. A present-but-stale quote may produce a constructed proposal rejected by R4 and may qualify if all other conditions hold. A missing or malformed quote must produce a non-qualifying NO_DECISION (or another explicit non-qualifying state), not a qualifying REJECTED proposal.
G-08 — LP-PRESEND margin is not tied to a bounded send interval
Severity: HIGH
Sections: R3 §§4.2–4.3, 7; G-07 Draft 0.3 §1 and G7-A3.

Failure mechanism

R3 requires now ≤ expires_at − δ_send and states only that δ_send > 0; FD-G18 defers its value. G-07 Draft 0.3 says expiry cannot occur in the LP-PRESEND-to-first-byte window if the send completes within δ_send, but does not define the measured interval, a maximum scheduling delay to the first byte, or the exact event whose duration δ_send bounds.

The pre-send check is locally atomic, but the remote broker acceptance is not. G-07 acknowledges this residual. The margin must therefore be a quantified operational bound, not merely a positive constant.

Consequence

The specification can pass LP-PRESEND and still begin transmission after the intended expiry boundary if the process is descheduled or the send path stalls beyond the assumed margin.

Smallest required correction

Define δ_send as a measured and enforced upper bound on the interval from the LP-PRESEND time sample to first outbound byte (or use an equivalent mechanism that prevents an unbounded delay). Specify what happens if that bound is exceeded. Keep the remote-acceptance race explicitly residual.
3. Prior-finding matrix
Prior finding / requirement	Classification	Independent disposition
R1 timing clocks and exact boundaries	CLOSED CONDITIONALLY	Approval, issuance, expiry, and strict/inclusive inequalities are now separated. Clock authority, Stage A skew, and exact checkpoint sampling remain conditional.
Fresh-quote checks at proposal, issuance, LP-CONSUME, LP-PRESEND	CLOSED CONDITIONALLY	All four checkpoints are stated. Quote structure and exact checkpoint instant are not fully defined; Stage A clock skew is unbounded.
Cycle identity, overrun, duplicates, skipped slots	CLOSED CONDITIONALLY	Identity and fail-closed overrun semantics are explicit. FD-7 and the slot-anchor/timer contract remain open; the audit does not yet prove complete run enumeration.
Founder approval as an authorization predicate	CLOSED CONDITIONALLY	R1 §3 / A0.3-13 is retained and R3 §7 binds approval to proposal fields. Approver authentication remains UNVERIFIED (FD-G13); the Stage B lifecycle is unimplemented.
R1 §3 and §6 retained without conflict	CLOSED CONDITIONALLY	The closure package expressly retains them and R3 carries the approval and STOP logic forward. The STOP table's clock assumptions depend on FD-G18; the retained-by-reference chain still needs final manifest/hash confirmation.
Positive milestone allowlist and missing-slot audit	CLOSED CONDITIONALLY	The allowlist and explicit MISSING/DUPLICATE/OFF_GRID classifications fix the earlier broad-counter problem. Record schema, evidence verification, origin classification, and auditor independence remain incomplete.
Exact decimal arithmetic and zero-volume classification	CLOSED CONDITIONALLY	Token-text parsing and numeric zero comparison are normatively clear. Arithmetic context/precision and the complete fee/increment/unit path are not. U24/U25 are examples, not executed evidence.
Supersession register	CLOSED CONDITIONALLY	The package gives explicit retained/replaced/superseded classes and a backstop. Final repository blob confirmation and a complete frozen manifest remain outstanding.
FD-4 reservation, partial-fill, and displayed-size rules	INCORRECTLY CLOSED	Displayed size is correctly informational, and partial-fill acceptance is explicit. Reservation accounting does not define BTC reservations, fee-asset effects, idempotent fill events, corrections/busts, or atomic ledger transitions.


4. New findings and open-item dispositions
ID	Severity	Finding	Falsifiable resolution criterion
G-01	Critical	Cash/BTC reservation and fill accounting incomplete	A typed two-asset ledger handles partial fills, fees in each supported asset, duplicate fill events, cancel-pending fills, corrections/busts, AMBIGUOUS outcomes, and concurrent updates without double allocation or premature release.
G-02	High	Stage A clock offset is measured but unbounded	A documented Stage A skew bound and exact checkpoint definition exist, or timing-dependent Stage A claims are explicitly conditional and non-qualifying.
G-03	High	Scheduler and manifest interval are underspecified	Absolute UTC slot schedule, anchor validation, missed/late/restart semantics, immutable run interval, and complete invocation ledger are specified and independently auditable.
G-04	High	Milestone auditor can trust asserted fields rather than evidence	Strict TER schema, closed origin enum, manifest/slot binding, hash verification, and independent recomputation are specified. Malformed and injected records cannot qualify.
G-05	High	Exact arithmetic context and increment source incomplete	Exact intermediate arithmetic, rounding, unit and overflow rules are specified; Stage B policy contains explicit versioned venue increments/minimums.
G-06	High	Stage A boundary checks only the chosen client/environment	Process/host-level egress is restricted to market-data endpoints and tested at the actual boundary.
G-07	High	Quote validity incomplete; missing quote cannot construct a proposal	Freshness and structural quote checks are separate; missing/malformed quotes cannot qualify as constructed REJECTED proposals.
G-08	High	LP-PRESEND margin lacks a bounded send interval	δ_send has a defined, measured bound from the check to first byte and an explicit overrun response.


Technical disposition of R3 open items
- FD-7 — OPEN; freeze blocker. Choose manual triggering or a minimal timer only after the schedule, slot anchor, missed-tick, restart, and audit semantics are specified. A timer that merely calls the cycle is not enough unless it records every scheduled slot and invocation.
- FD-6 scope — CANDIDATE; do not promote. One blind script performing both reconstruction and slot audit creates common-mode risk. The audit logic should be independently implemented or separately authored and should independently enumerate manifests/slots. Founder decision remains separate.
- CF-1 — OPEN; Stage B text blocker. The R3 candidate is internally coherent if the limit price is fixed at proposal creation, bound by approval, and only validated—not changed—at issuance. The alternative issuance-priced flow is a different lifecycle. Founder must decide which reading satisfies FD-4; no technical reviewer can decide that intent.
- CF-2 — OPEN; founder decision. BUY-while-long and EXIT-while-flat remain candidate mapping rules. Preserve that status; do not treat them as accepted merely because U14 tests the candidate.
- CF-3 — technically acceptable, conditional. Failing closed on a revision inside the current 51-candle window is conservative. Preserve original bytes and invalidate any affected pending authorization. The one-source and revision-detection limitations remain.
- CF-4 — acceptable fail-closed rule, conditional on G-02. A future-dated quote fails with zero tolerance. Without a bounded clock, that can produce false rejection or incorrect age evaluation.
- CF-5 — accepted as a necessary rule; test gap remains. Issuance must occur by approval_deadline, not merely approval. Add a case where approval occurs before the deadline but issuance occurs after it.
- CF-6 — incorrect as written. A stale-but-present quote may support a constructed proposal rejected by R4. A missing quote cannot support price construction and must be non-qualifying.
- CF-7 — unresolved circular precondition. Query-by-COID and duplicate-COID tests cannot be prerequisites to the first paper order if those tests themselves require paper orders. Either conduct them as the first controlled, fully governed Stage B test orders or move the tests to a post-first-order acceptance gate. Do not imply they have been completed beforehand.
- CF-8 — unresolved and related to G-02. The Stage A offset estimate is not a clock guarantee. Define its bound or retain the explicit conditional limitation.
5. Test adequacy matrix
Status for every test: designed only; none executed. “Executable” below means a synthetic fixture can be constructed from the specification, not that the test has been run. An example test exercises a case; it does not prove the general invariant.
Critical invariant / area	Existing IDs and pass/fail coverage	Fixture status	Adequacy
SMA arithmetic and crossover	U1–U4e cover ordinary signs, equality and touch cases; U10 determinism; X11 fabricated signal	Synthetic fixtures are described; some tests specify only a pass result	Exercises examples. Does not prove the parser/arithmetic implementation or exhaustive edge handling.
Bar completion and cadence	U5, U15, U17; U6/U11 gaps/history; U12 ordering	Synthetic time/bar fixtures are feasible	Useful examples. Add exact ±1 ns completion boundaries and malformed/off-grid timestamps.
Duplicate, pagination, source revision	U7, U13, U20, U31	Synthetic fixtures feasible; U20/U31 require revision sequences	Partial. Add pagination mutation, omitted page, malformed token, revision with representation-only change, and a revision affecting a pending proposal.
Numeric token and zero-volume handling	U24, U25	Raw JSON fixtures can be created	Partial. Add exponent forms, -0, long mantissas, large/small exponents, non-finite tokens, decimal-context traps, and an explicit proof no float is introduced.
Quote freshness and policy	U8(b), U18, U23, U28	Synthetic quote/checkpoint fixtures feasible	Partial. U28 covers future timestamp and 15 s boundaries. Missing, malformed, crossed, zero/negative bid/ask, and invalid sizes are absent.
Cycle identity, overrun, duplicate slots	U9, U15, U19, U27	Synthetic cycle logs feasible	Partial. No timer drift/missed tick/restart fixture; no test of slot-anchor validation or multiple manifests.
Approval and authorization	U21, U22, U29, U30	Stage B synthetic state-machine fixtures are possible; not Stage A runtime proof	Partial. Add approval-field mismatch tests, revoke-before-consume, revoke-between-consume-and-presend, issuance-after-deadline, and concurrent consume attempts.
Reservation and partial fill	U32, U33	Synthetic ledger events feasible	Inadequate. No BTC reservation, fee-asset, duplicate-fill, correction/bust, cancel/fill race, ambiguous reconciliation, or concurrent-ledger tests.
Positive allowlist and slot audit	U26, U27, U34	Synthetic TER/manifest fixtures feasible	Partial. Add malformed schema, missing/unknown origin, injected record masquerading as scheduled, hash-chain tampering, omitted manifest, duplicate cycle across manifests, and invalid evidence references.
Stage A egress boundary	X8–X10	Client/environment fixtures feasible; host-level boundary fixture not specified	Does not prove process-level or host-level disconnection. Add actual egress-denial tests and inventory of alternate paths.
G-07 I1–I10	Draft 0.3 §8 lists surface tests and crash points but no complete executable test inventory with IDs/fixtures	Most require Stage B/C environment; some can be modeled synthetically	Design coverage only. No invariant is established by the listed surfaces; I5/I8 require deployment-level evidence.


Minimum additional tests before claiming test adequacy
1. Reservation: duplicate fill replay; cumulative fill out of order; cancel request followed by fill; cancel confirmation with late fill; AMBIGUOUS order; fee in BTC and USD; fee above reserve; correction/bust; simultaneous reservation attempt.
2. Authorization: approval at deadline with issuance after deadline; one-nanosecond-late issuance; approval field mismatch for every bound field; revocation at each checkpoint; concurrent LP-CONSUME; LP-PRESEND at and around δ_send.
3. Audit: missing manifest; malformed TER; invalid origin; injected record with a scheduled cycle ID; duplicate slot record; same cycle ID across manifests; hash-chain break; asserted V-pass without supporting artifact; run interval alteration.
4. Scheduler: timer drift, missed tick, duplicate wake, process restart, machine sleep/resume, late invocation, and end-of-run closure.
5. Data/time: exact completion boundary ±1 ns; skew just inside/outside bound; malformed quote; malformed timestamp; numeric token preservation and exact arithmetic with exponent/negative-zero cases.
6. Decision register
Founder decisions — remain with the founder
Item	Status	Reviewer position
FD-7 cycle trigger	OPEN	Required before freeze.
FD-6 slot-audit scope	CANDIDATE	Do not silently accept same-script audit. Decide after technical separation is specified.
CF-1 limit-price timing	OPEN	Choose proposal-time binding/issuance-time validation or redesign the approval lifecycle.
CF-2 position-mismatch mapping	CANDIDATE	Preserve as undecided.
FD-G13 approver authentication	DEFERRED	Must be defined before Stage B.
FD-G16 same-COID retry	DEFERRED	No retry under a new ID; ambiguous outcomes remain unresolved pending broker evidence.
FD-G17 independent reconciliation	DEFERRED	R-c/R-d remain proposals, not established controls.
FD-G18 time source, σ, δ_send	DEFERRED	Must be defined before Stage B.
FD-4 TIF	DEFERRED	Stage B decision; partial-fill semantics must be reconciled with chosen TIF.
FD-5 build authorization / FD-9 Stage B authorization	NOT AUTHORIZED	This review grants neither.
Policy candidates R8/R12 and settle value	CANDIDATE	Do not treat as founder decisions.


Technical questions — not founder intent decisions
- What is the complete cash/BTC reservation and fee-asset accounting model?
- What exact TER schema and evidence-verification algorithm governs qualification?
- What clock skew bound applies to Stage A and what is the exact checkpoint sampling instant?
- What timer semantics guarantee a complete, independently auditable slot schedule?
- What host-level controls make Stage A genuinely disconnected from trading egress?
- What structural quote checks are required before pricing?
- What exact arithmetic context and increment metadata format are required?
- How are fill corrections, busts, duplicate reports, and late reports reconciled?
7. Residual UNVERIFIED / CONDITIONAL / UNBOUNDED items
UNVERIFIED
- Stage A repeated keyless access and data-source reliability beyond the single probe.
- Bar revision behavior and longer-horizon gap frequency.
- Price and quantity increments and minimum order size.
- Paper fee rate, fee asset, maker/taker treatment, and whether the reservation fee is a true upper bound.
- Account buying power, 1× configuration, shorting setting, and account-configuration permissions.
- Asset metadata access with paper credentials.
- COID uniqueness/query semantics and duplicate-COID behavior.
- Approver authentication, K3 linearizability, authoritative time, σ, and δ_send.
- Independent reconciliation channel and completeness of broker-originated confirmations.
- G-07 I1–I7 and I9–I10 implementation properties.
CONDITIONAL
- Stage A sizing while venue increments remain UNVERIFIED.
- Stage A timing and quote checks while harness clock skew is unbounded.
- G-07 K3/K5 behavior conditional on uncompromised components, linearizable reads, and clock assumptions.
- I10 conditional on broker idempotency semantics.
- FD-6 independence conditional on the auditor being independently implemented and frozen before TER exposure.
- FC-D per-bar probe check remains conditional until the local evidence is actually produced.
UNBOUNDED
- Time to obtain 30 consecutive qualifying slots, depending on FD-7 and data quality.
- Time to the first BUY signal, which is market-dependent.
- Loss/exposure under compromise of K5, its host, or a trade-capable credential; G-07 explicitly does not claim a verified loss bound.
- Detection completeness for out-of-boundary activity where reconciliation is manual or email-based and not guaranteed.
8. Freeze recommendation
Do not freeze R3 in its current form.

The smallest targeted corrections required before reconsideration are:
1. Resolve G-01 by specifying a complete, typed, idempotent, atomic cash/BTC reservation and fill lifecycle.
2. Resolve G-02/G-08 by defining clock bounds, checkpoint instants, and a measurable LP-PRESEND margin.
3. Resolve G-03 by specifying absolute slot scheduling, timer failure semantics, and immutable manifest/run boundaries; obtain the founder's FD-7 decision.
4. Resolve G-04 by making the slot auditor verify evidence and recompute qualification rather than trusting TER assertions; decide FD-6 separately.
5. Resolve G-05 by specifying exact arithmetic context, rounding, units, and versioned venue increments.
6. Resolve G-06 by specifying and testing process/host-level Stage A egress restrictions.
7. Resolve G-07 by separating missing/malformed quote outcomes from stale-but-present quote rejections.
8. Add the missing boundary, race, malformed-record, and reservation tests listed above. Keep all results labeled DESIGNED until actually executed.
9. Keep all founder decisions in the decision register. No CANDIDATE is promoted by this review.
10. Preserve the Stage A/Stage B boundary and the explicit statement that no Stage A result establishes G-07 I5 or I8.
After these corrections, obtain the independent review, reconcile findings, confirm repository blob hashes, record the founder's decisions, and only then reconsider a freeze. A freeze would still authorize no harness or trading activity by itself; FD-5 and later Stage B authorization remain separate.
9. Single most important blocker
G-01: the reservation ledger is not a complete, unit-safe, idempotent accounting model.

This is the most important blocker because the reservation model is the mechanism intended to prevent double allocation and understated exposure across proposals, authorizations, partial fills, cancellations, fees, and ambiguous outcomes. The current text does not define the BTC side of that ledger and does not fully define how reported fills and fee assets alter either side.

A specification that cannot reconstruct its own remaining cash and BTC commitments cannot reliably enforce its exposure rules. Fixing the timer or polishing the milestone counter would not cure that defect.
Review status: Delivered as a hostile specification review. No tests executed. No implementation authorized. No trading authority conferred