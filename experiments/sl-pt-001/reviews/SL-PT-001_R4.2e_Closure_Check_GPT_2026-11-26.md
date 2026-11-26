# **SL-PT-001 R4.2e — Bounded Closure Review**

**Reviewer:** GPT | Hostile reviewer\
**Date:** November 26, 2026\
**Scope:** Stage A amendment delta D-1 through D-8; founder closure conditions CL-01 through CL-04.\
**Classification:** Specification review only.

## **1. Exposure statement**

I inspected the supplied R4.2e candidate, the Git-format delta against R4.2c, and Claude's fixture feasibility script.

I reconstructed R4.2c by reverse-applying the delta, verified its SHA-256 and Git blob identifier, then reapplied the delta and verified the resulting R4.2e bytes against the supplied candidate.

I also executed the supplied standalone exact-arithmetic fixture feasibility script.

No harness code, TER output, credentials, broker connection or orders were inspected, generated or requested. The fixture script execution is arithmetic evidence only. It is not an executed Stage A test.

Previously frozen sections were examined only where directly necessary to assess the amendments. No general architectural review was reopened.

## **2. Artifact integrity**

## **Artifact integrity verified**

Reconstructed R4.2c SHA-256

9d417fb5b22147eec6785816b239ad6b76215ea5f18e662432dc7e9cfb283d76

MATCH

Frozen baseline

Reapplied R4.2e SHA-256

c8ccf49352fa30c7f8787581005240b96ab548b679796623fd2a415d3c58d7bf

MATCH

Amendment candidate

Reverse and forward delta application

PASS

Both Git blob identifiers

MATCH

Standalone fixture script execution

PASS

**Evidence classification: COMPUTED.**

The delta reproduces the exact frozen baseline and amendment candidate identified in the review request. There is no artifact identity discrepancy.

This establishes byte-level correspondence, not semantic correctness.

## **3. Delta closure register**

| Delta | Subject                                         | Verdict    |
| ----- | ----------------------------------------------- | ---------- |
| D-1   | Deterministic pagination rejection              | CLOSED     |
| D-2   | V12a evidence and claim boundaries              | CLOSED     |
| D-3   | Append timing and commit semantics              | NOT CLOSED |
| D-4   | Injection feasibility, attribution and coverage | NOT CLOSED |
| D-5   | Stage A R2 coverage                             | CLOSED     |
| D-6   | Revision-store admission                        | CLOSED     |
| D-7   | Commit-reveal seed custody                      | CLOSED     |
| D-8   | Raw HTTP artifact semantics                     | CLOSED     |

# **6/8**

Delta items closed

Two delta items require further bounded correction.

### **D-1 — CLOSED**

**References:** §4.2, §4.7 V2, U13, U94.

Pagination now has one deterministic outcome:

- JSON null: continue validation.
- Non-null page token, including an empty string: reject.
- Missing page-token field: reject under V1.
- No additional page request.

The amended tests agree with the normative text. No pagination implementation or additional request sequence is required.

### **D-2 — CLOSED**

**References:** §6.4 step 1, §10.4, §11.1, §13, U-I3, U116.

V12a now defines an explicit credential-name matching rule, a closed configuration object and a client-reported allowlist.

The auditor's conclusion is appropriately limited to recomputation from harness-attested observations and the retained configuration artifact where available.

The specification explicitly excludes claims concerning unchecked credential stores, alternative credential names and process-level or host-level isolation.

**Residual limitation:** a dishonest or defective harness could misreport its environment. The amended specification acknowledges rather than conceals that limitation.

### **D-3 — NOT CLOSED**

**References:** §5.4, §6.3, §6.4 step 8, §11.1, U-T5, U117.

The new text correctly distinguishes the under-lock clock sample from completion and durability. However, the immediately following inherited paragraph still requires completed commitment before the slot boundary.

These rules are inconsistent when applied together.

The concrete counterexample appears under finding G6-01 below.

### **D-4 — NOT CLOSED**

**References:** §6.5, §7.3, §8.1.1, §10.4, §11.4, §11.6, U118, U121.

The five principal BUY fixtures are arithmetically feasible. The amendments also preserve the stated requirement for EXIT and long-position unit testing.

However, U121 introduces an impossible single-rule attribution requirement for the R15 failure case. The reachability argument additionally overstates R8's unreachability, and the new injection-counting definition does not explicitly require agreement with the recorded rejection.

See G6-02 through G6-04.

### **D-5 — CLOSED**

**References:** §7.3 R2, §11.6, U119.

Stage A's LIMIT-only requirement is now included in the executed pre-live test gate.

TIF, partial-fill acceptance and R14 remain Stage B requirements.

No new Stage B dependency is introduced by this correction.

### **D-6 — CLOSED**

**References:** §4.7, §4.9, U115.

Bar-store admission now requires V1, V2, V3, V4 and V9 to pass.

Malformed or incomplete responses therefore cannot establish new baselines, confirm revisions or generate disappearance observations.

The distinction between retained evidence and admitted bar-store observations is maintained.

### **D-7 — CLOSED**

**References:** §11.5, §10.3, U120.

The amendment establishes the required commit-reveal sequence:

1. Commit and push the seed commitment before the first audited run.
2. Fix and push the evidence commit, chain head, manifest set and eligible population.
3. Reveal the seed in a later commit.

The same audit scope cannot substitute evidence, change seeds or redraw a failed reconstruction. The previous cleartext seed at `07f43e0` is expressly superseded and retained historically.

**Claim boundary:** this closes seed custody for the defined audit scope. It does not establish independently that the founder generated an unbiased seed, kept it secret or selected the audit scope without knowledge of that seed.

### **D-8 — CLOSED**

**References:** §4.3, V1, V12b.

The body and header artifacts now have explicit meanings.

Transfer-decoded body bytes and client-reported HTTP headers are distinguished from wire-level captures. Content encoding is constrained, and the status and Date used by the checks are derived from the retained header artifact.

The specification does not claim wire-level byte identity.

## **4. Founder closure conditions**

| Condition                                         | Verdict        | Reason                                                                                                                                |
| ------------------------------------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| CL-01 — Seed custody                              | **CLOSED**     | Commit-reveal ordering, fixed evidence and population, prohibition on substitution and resampling, superseded seed preserved.         |
| CL-02 — V12a epistemic limits                     | **CLOSED**     | Checked scope and conditional harness-attested recomputation are explicitly distinguished from independent observation and isolation. |
| CL-03 — Fixture feasibility and retained coverage | **NOT CLOSED** | Five BUY cases are feasible, but the new R15 single-rule expectation cannot be satisfied under the applicable policy rules.           |
| CL-04 — Clock versus commit                       | **NOT CLOSED** | The new distinction is correct, but the inherited commit-deadline requirement contradicts the amended timing semantics.               |

## **5. Independent fixture feasibility check**

**Status: COMPUTED.** I executed Claude's supplied script without modification. All six arithmetic cases returned `SINGLE-RULE OK`.&#x20;

sl_pt_001_cl03_fixture_check.py



| Intended rule          | Quantity (BTC) | Reservation | Isolated failure     |
| ---------------------- | -------------- | ----------- | -------------------- |
| R4 — Stale quote       | 0.0016         | $144.36     | PASS                 |
| R5 — Price deviation   | 0.0016         | $147.57     | PASS                 |
| R10 — Minimum quantity | 0              | $0.00       | PASS                 |
| R12 — Equity gate      | 0.0016         | $144.36     | PASS                 |
| R13 — Approval window  | 0.0016         | $144.36     | PASS                 |
| R1 — Instrument        | 0.0016         | $144.36     | Arithmetic pass only |

R1 remains supplementary because its runtime constructibility depends on whether the fixture interface permits overriding the otherwise fixed BTC/USD instrument.

It is not needed to reach the five-fixture requirement.

### **Dependency assessment**

| Dependency | Assessment                                                                                                  |
| ---------- | ----------------------------------------------------------------------------------------------------------- |
| R6         | Reservation remains within available cash for the five principal fixtures.                                  |
| R7         | Reservation remains within $150.                                                                            |
| R8         | Portfolio exposure remains within $300 for those fixtures.                                                  |
| R12        | The equity gate passes except in its intended failure fixture.                                              |
| R3         | The amendment expressly permits zero quantity as schema-valid, leaving minimum quantity enforcement to R10. |

**The five intended-rule BUY fixtures are constructible under the stated arithmetic model.**

However, the script does not evaluate the complete policy. In particular, it does not independently exercise R2, R3, R9, R11, R15 or R16. It also hardcodes reserved cash to zero. Its successful execution cannot establish complete injection-interface feasibility or EXIT coverage.&#x20;

sl_pt_001_cl03_fixture_check.py



The remaining CL-03 blocker is not the five BUY fixtures themselves.

## **6. Findings introduced or exposed directly by the delta**

### **G6-01 — Contradictory append-deadline semantics**

High severity

Blocks freeze: YES

**Section:** §6.4 step 8; direct dependencies §5.4, §6.3, §11.1 and U-T5.

The new paragraph states that append completion after the next slot boundary is not excluded.

The immediately following paragraph still states:

> The commit must happen before T_d(i+1). **A cycle that has not committed by T_d(i+1) is overrun.**

Both cannot govern the same execution.

**Counterexample:**

Amended append-start predicate

PASS

Inherited commit-deadline predicate

FAIL

The successor acquires the lock after 300.2 seconds and finds an existing terminal CYCLE record. It therefore does not necessarily write CYCLE_OVERRUN.

The auditor could classify the record as qualifying even though the inherited normative rule requires an overrun.

A related qualification is necessary for process termination: a process killed after writing but before fsync may leave a complete readable record. Its OS lock can be released without successful fsync. Chain ordering alone cannot establish that fsync occurred.

**Smallest correction:** replace the inherited commit-deadline paragraph with language consistently defining the under-lock append-start deadline. Distinguish normal lock release after successful fsync from process termination. Do not infer historical fsync completion from a surviving record.

Add a U117 case covering an append that begins before the boundary and completes after it, with an unambiguous expected classification.

### **G6-02 — Impossible R15 single-rule failure test**

High severity

Blocks freeze: YES

**Section:** U121; dependencies §3.3, §7.3 R9/R10/R15 and §8.1.1.

U121 requires exactly the constructed rule to fail, except for its expressly recognized joint R11/R16 case.

But R15 cannot fail independently when R9 and R10 remain applicable.

**Counterexample:** construct an EXIT proposal while flat.

By definition:

\\[ h < 0.0001 \\]

Where \\(h\\) is held BTC. Passing R9 requires:

\\[ q\_{\text{exit}}\leq h-r\leq h \\]

Where \\(r\\) is nonnegative reserved BTC. Passing R10 requires:

\\[ q\_{\text{exit}}\geq 0.0001 \\]

These conditions cannot both hold while flat.

| Proposed EXIT quantity | R9   | R10  | R15  |
| ---------------------- | ---- | ---- | ---- |
| 0 BTC                  | PASS | FAIL | FAIL |
| 0.0001 BTC             | FAIL | PASS | FAIL |

Directly constructing a proposal bypasses the normal signal-to-action mapping, but it does not eliminate the mathematical relationship between the applicable rules.

**Consequence:** the mandatory pre-live test gate contains an unsatisfiable expected result.

**Smallest correction:** permit the necessary joint failure for an EXIT-while-flat fixture, or explicitly distinguish an isolated R15 predicate test from full-policy evaluation.

Preserve all EXIT and long-position coverage requirements.

### **G6-03 — R8 unreachability is overstated**

Medium severity

Blocks freeze: YES, as written

**Section:** §6.5 reachability argument.

The proof that R8 cannot fail while flat assumes that quantity satisfies the minimum order size.

That assumption is not universal because the specification intentionally permits construction of proposals that fail R10.

Consider this exact fixture:

| Input                 | Value      |
| --------------------- | ---------- |
| Cash                  | $500       |
| Held BTC              | 0.00009    |
| Bid and ask           | $4,000,000 |
| Rounded BUY quantity  | 0 BTC      |
| Reservation           | $0         |
| Existing BTC notional | $360       |

The position is flat under §3.3, yet:

\\[ 360+0>300 \\]

R8 fails, and R10 also fails.

The supplied script's price-grid check skips cases where quantity is below minimum order size. It therefore does not test this counterexample class.&#x20;

sl_pt_001_cl03_fixture_check.py



**What survives:** the narrower claim that R8 cannot be the *sole* failing rule in a normally constructed flat BUY remains supported by the stated bound.

**Smallest correction:** replace “R8 cannot fail while flat” with:

> R8 cannot fail independently of R10 in a normally constructed flat BUY under the specified policy values.

The five principal BUY fixtures remain unaffected.

### **G6-04 — Injection counting does not explicitly bind recomputation to the recorded rejection**

Medium severity

Blocks freeze: YES

**Section:** §11.4, §11.6 M1-5, U118.

The amended definition of “rejected by the intended rule” requires precommitted fixtures, distinct fixture identities and single-rule failure on recomputation.

It does not explicitly require the recorded INJECTION terminal state and recorded rule results to agree with that recomputation.

**Counterexample:** a precommitted R4 fixture correctly fails R4 on auditor recomputation, but the harness records SHADOW_EXPIRED and reports R4 as PASS.

The newly stated §11.4 counting conditions can be satisfied by the fixture itself despite the incorrect recorded execution.

M1-5 separately requires correct rejection, which provides a downstream safeguard. However, M1-1's counting predicate should not independently credit a failed execution.

**Smallest correction:** require all of the following for a counted injection:

- Recorded terminal state is REJECTED.
- Recorded failing-rule set is exactly the intended rule.
- Independent recomputation agrees with the recorded result.
- Precommitment, fixture identity and distinctness checks pass.

Add a corresponding mismatch case to U118.

### **G6-05 — Newly expanded INJECTION schema requires explicit non-slot semantics**

Medium severity

Blocks freeze: YES

**Section:** §10.1, §10.4; dependencies §6.5 and §11.4.

D-4 changes INJECTION records from an injected proposal and result to a full TER with `origin = INJECTED`.

The closed TER schema requires scheduled-cycle identity fields, including `manifest_sha256`, `slot_index` and `cycle_id`. However, §6.5 expressly prohibits injections from occupying slots.

**Counterexample:** a valid founder-commanded R5 injection runs between scheduled invocations. The specification does not explicitly define which slot identity fields are null, fixture-derived or otherwise inapplicable.

One implementation could assign the neighboring slot identity; another could use null. The auditor lacks a single normative representation against which to validate both.

**Smallest correction:** add an INJECTED-origin schema row defining non-slot identity, fixture-derived fields, absent requests and artifacts, unevaluated validation results and applicable append timing. No injection may acquire scheduled-slot credit.

This is a schema clarification necessitated by D-4's expansion of the INJECTION record, not a request to reopen the scheduled-cycle TER design.

### **G6-06 — Branch H necessity claim is unsupported**

Low severity

Blocks freeze: NO

**Section:** §11.1.

The amendment correctly labels V12a observations and append-clock measurements as HARNESS-ATTESTED. However, it then states that making those observations independent would require Branch H.

Branch H is a host-level network-isolation mechanism. A firewall does not independently establish the contents of a process environment or the instant a chain append began.

**Smallest correction:** state that independent observation would require additional independently trusted instrumentation, which is outside the selected Stage A scope.

CL-02 remains closed because the actual Stage A claim is appropriately restricted.

## **7. Final verdict**

SL-PT-001 R4.2e — Stage A amendment

# **NOT FREEZE-READY**

Delta items closed

# **6 / 8**

Founder conditions closed

# **2 / 4**

Principal BUY fixtures feasible

# **5 / 5**

Blocking findings

# **5**

Frozen authority: R4.2c remains unchanged.

### **Recommended next action**

Produce a narrowly bounded R4.2f amendment addressing G6-01 through G6-06. Carry forward the six closed delta items and the two closed founder conditions without reopening them.

No architectural expansion, additional strategy research, Stage B design work or new founder policy decision is required if the append-start timing interpretation is retained.

**The center of gravity remains intact.** The outstanding defects concern precise timing semantics, executable test expectations and evidence attribution. The five BUY fixtures are feasible, the seed custody protocol is specified, and the epistemic boundaries are substantially improved.

The remaining work is specification reconciliation, not a redesign.

**Authorization status:** unchanged. This review authorizes no implementation, harness execution, credentials, broker connection or orders.