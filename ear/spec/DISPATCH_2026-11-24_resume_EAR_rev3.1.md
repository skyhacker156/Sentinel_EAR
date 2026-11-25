# SENTINEL A-TEAM DISPATCH
## Resume Exposure Accounting Reference Model (EAR) v0.1, Revision 3.1

**From:** Founder / Orchestrator  
**To:** Claude (Specification Lead / ARBITER)  
**CC:** GPT (Independent Adversarial Reviewer), Gemini (Independent Review)  
**Date:** November 24, 2026

### 1. MISSION

Resume work on the Sentinel Exposure Accounting Reference Model (EAR) v0.1, Revision 3.1.

The immediate objective is to advance the specification toward a defensible implementation decision without prematurely authorizing code.

Maintain the established Sentinel center of gravity:

> Intelligence proposes. Governance disposes. Authorization permits. Execution obeys.

EAR is the current technical proving ground for translating this principle into explicit financial exposure accounting, uncertainty treatment, authorization conditions, and bounded execution permissions.

Do not expand the mission into a general Sentinel redesign.

### 2. CURRENT BASELINE

The latest submitted specification is:

**Exposure Accounting Reference Model v0.1, Revision 3.1**

Founder-supplied full-file SHA-256:

`dd9d87f76b01134e084827b0202c73c52fccb2b86f21a176a6b6e551241fa239`

Treat this hash as supplied, not independently verified. If the source file is available, verify it before relying on it as an artifact identity.

Status:

- Specification only.
- Not implemented.
- Not independently verified.
- No broker integration.
- No live trading.
- Implementation authorization remains NO-GO.

Revision 3.1 is the current review baseline. Do not silently alter frozen requirements or assume that previous reviewer agreement constitutes verification.

### 3. ARCHITECTURAL CONTEXT

The historical Sentinel repository review has reinforced several principles:

1. Intelligence and execution authority must remain separate.
2. Governance must be expressed through enforceable conditions, not merely policy language.
3. Uncertainty must affect permission.
4. Evidence provenance and dissent must be preserved.
5. Deterministic reconstruction does not establish completeness or authenticity of the underlying event history.
6. Human authority does not substitute for technical enforcement.
7. Model consensus is not independent verification.

The historical repositories are context, not authority. Do not revive unsupported S³ claims, historical numerical assertions, or earlier mathematical guarantees unless independently justified.

### 4. KNOWN TECHNICAL ISSUES TO PRESERVE

The following are important existing review findings. Reassess them against the actual Revision 3.1 text rather than treating this summary as a replacement for the specification.

**A. Exposure accounting**

The current model uses:

- `F_max = F_d + d_+ + Q3_buy + Q3_unk`
- `F_min = F_d - d_- - Q3_sell - Q3_unk`
- `U = F_max + B + U_unknown`
- `A_raw = F_min - S - A_unknown`
- `A = max(0, A_raw)`

D17 sets `U_unknown = 0` and `A_unknown = 0`.

The sum rule is normative. The earlier maximum-based rule was rejected.

OVER_RESERVED is defined by `A_raw < 0`.

Orphan treatment is conservative. Only application, authoritative dismissal, or a newer snapshot can narrow a discrepancy.

**B. D19**

D19 remains conditional.

The quantified MISMATCH reduction candidate is permissible only if all five specified preconditions hold. A false permission in the relevant test space requires reverting to blocking reductions during quantified MISMATCH.

Do not characterize D19 as a proven safety property.

**C. D20 and D21**

D20 establishes append-only log position as canonical replay order. Do not claim order invariance for non-commuting events.

D21 requires D_max and commit-time re-evaluation. Freshness must be checked against S_lim at commit.

**D. D22-D25**

Preserve the specified minimal E24 master-change handling.

Key custody, independent evidence, and broker-contact/live-use claims remain subject to the applicable evidence requirements. Do not overstate these controls.

**E. A-12: event-delivery completeness**

This is a particularly important unresolved assumption.

The model assumes event delivery is complete between snapshots except for known working-order unreported fills.

Freshness and reconciliation do not establish event-delivery completeness.

A-12 failure can invalidate both exposure bounds and potentially permit false reduction even when the system reports RECONCILED.

Do not bury this assumption in a general limitations section. Treat it as a potentially fundamental boundary of the model.

**F. Oracle**

The oracle in `exposure_oracle/` imports nothing from `exposure_model/`, but both are same-author work.

It is not independent verification.

The modeled oracle enumerates W1-T/F, T1u, T2/T3/T4, and working-order unreported fills `x ∈ [0,R]`.

The stated comparison is:

- `U_oracle = max(U_w)`
- `A_oracle = min(A_w)`

Soundness is evaluated through:

- `U >= U_oracle`
- `A_raw <= A_oracle`

No independent reproduction or execution of the oracle has been established.

**G. Remaining clarification items**

Previously identified open or deferred matters include:

- Canonical proposal hash.
- No precommit ALLOW public API.
- Identity-changing correction behavior.
- Same-identity correction fields.
- Schedule precedence.
- A-2 monotone broker sequence/snapshot watermark assumption.
- A-7 honest and complete statekeeper trust.
- A-11 stable event IDs without economic-execution uniqueness.
- W1-T/F exhaustiveness limited to the modeled envelope, not the real-world broker failure taxonomy.

Reconcile each against the actual current specification. Do not assume an item remains open if Revision 3.1 explicitly resolved it.

### 5. TASKING

Resume with a targeted technical review, not a wholesale rewrite.

**Task 1: Establish the exact baseline**

Confirm the full Revision 3.1 text, section structure, decision register, assumptions, and artifact hash.

Identify any mismatch between the current document and the review history.

**Task 2: Reconcile open decisions**

Produce a decision ledger identifying each item as:

- RESOLVED
- OPEN
- CONDITIONAL
- DEFERRED
- REQUIRES FOUNDER DECISION

For every item, cite the exact specification section and explain the operational consequence of leaving it unresolved.

Preserve D19's conditional status.

**Task 3: Re-examine the most consequential assumptions**

Prioritize:

1. A-12 event-delivery completeness.
2. A-2 sequence and snapshot-watermark assumptions.
3. A-7 statekeeper trust.
4. A-11 event identity versus economic-execution uniqueness.
5. D19's conditional reduction permission.
6. Oracle completeness within the declared test envelope.
7. Commit-time freshness and authorization behavior.

For each, provide:

- Exact assumption.
- Why the model needs it.
- What happens if it is false.
- Whether the failure is detectable.
- Whether the system blocks, permits, or potentially falsely permits an action.
- What evidence would be needed to justify the assumption.
- Whether the assumption should remain, be weakened, or be replaced.

**Task 4: Construct adversarial counterexamples**

Do not merely restate the known cases.

Develop minimal event sequences that challenge:

- Upper and lower exposure bounds.
- Working-order accounting.
- Partial fills and unreported fills.
- Duplicate or reordered events.
- Corrections and cancellations.
- Snapshot/event disagreement.
- Missing event delivery.
- Stale authorization.
- State changes between proposal and commit.
- Any path to false ALLOW.

Distinguish genuine counterexamples from cases excluded by the declared model assumptions.

**Task 5: Challenge the oracle**

Examine whether the oracle independently and exhaustively evaluates the intended state space.

Specifically assess:

- Whether its enumerated event classes are sufficient.
- Whether boundary values are included.
- Whether combinations of event conditions are represented.
- Whether the oracle shares assumptions or conceptual errors with the model.
- Whether its inequalities establish the intended conservative bounds.
- What independent implementation or reproduction would be necessary.

Do not describe same-author structural separation as independent verification.

**Task 6: Produce a bounded implementation-readiness assessment**

Do not write implementation code or authorize implementation.

Instead determine:

- Which specification requirements are sufficiently defined.
- Which remain ambiguous.
- Which are internally inconsistent.
- Which depend on unvalidated external assumptions.
- Which can be tested using a bounded reference model.
- Which cannot be established without broker-specific evidence.

Recommend GO, CONDITIONAL GO, or NO-GO for moving to a bounded implementation, with explicit reasoning.

A recommendation to implement must not be confused with authorization to connect a broker or trade.

### 6. REVIEW DISCIPLINE

Apply the following rules throughout:

- Specification is not implementation.
- Implementation is not verification.
- Verification within a model is not validation against reality.
- Deterministic replay is not proof of event completeness.
- A passing test suite is not proof of exhaustive correctness.
- Same-author agreement is not independent confirmation.
- A conservative assumption must be identified as an assumption, not presented as an established fact.
- Do not turn an unresolved question into a default favorable assumption.
- Do not broaden the declared scope to make a counterexample disappear.
- Preserve rejected claims and the reasons for rejection.

If the specification is ambiguous, identify the ambiguity and propose alternatives. Do not silently choose one.

### 7. REQUIRED DELIVERABLE

Return a structured report:

1. Executive assessment.
2. Exact baseline and artifact identity.
3. Decision ledger.
4. Critical assumption inventory.
5. New adversarial counterexamples.
6. Oracle assessment.
7. Specification inconsistencies and ambiguities.
8. Recommended revisions, if any.
9. Implementation-readiness verdict.
10. Specific questions requiring Founder decision.

For every proposed specification change, provide:

- Current wording or reference.
- Proposed wording.
- Reason for change.
- Behavioral consequence.
- New or modified tests required.
- Whether the change alters the frozen baseline.

Do not produce a new frozen revision until the Founder has reviewed the proposed changes.

### 8. FINAL DIRECTIVE

The purpose of this phase is not to make EAR look complete.

It is to discover whether its claims survive adversarial examination.

A smaller model with explicit limitations and defensible behavior is preferable to a comprehensive model whose guarantees depend on unexamined assumptions.

Keep the center of gravity held.

**The immediate objective is a technically defensible decision about whether EAR is ready for bounded implementation, not a declaration that Sentinel is ready for the market.**