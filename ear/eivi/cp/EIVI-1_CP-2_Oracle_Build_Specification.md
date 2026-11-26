# EIVI-1 Construction Pack CP-2: Oracle Build Specification

**Normative input:** CP-1 only. **Scenario input:** CP-3.
**Classification:** build specification. Building the oracle requires the founder's authorization of the build; this document grants none.

## 0. Builder rules

1. Implement CP-1's semantics. **Do not** consult any other EAR document, repository directory, review or reference implementation. Do not ask anyone how another system behaves.
2. Use the computational principle below: **explicit enumeration of possible worlds**. Do not substitute interval or bound arithmetic, even where it looks equivalent. Equivalence is what is being tested.
3. **Write no domain logic shared with any other EAR implementation.** General-purpose libraries are fine.
4. **Run every CP-3 scenario.** Record the verdicts and **freeze** the results file. Publish its SHA-256 **before** seeing any expected result (Independence Protocol §4).
5. Some CP-3 scenarios are traps, and you are not told which. Treat every scenario the same way.
6. Report every ambiguity you meet in CP-1 or CP-3 in writing. Where the text forces a choice, run every reasonable reading and report each.

---

## 1. Interface

```
oracle(log, profile, config, query) → verdict
  log     : ordered list of CP-3 log entries
  profile : assumption switches (CP-1 §3), e.g. "A0", "A0 − E-5", "A0 with E-4I", "A0 + E-9(T_f=60)"
  config  : L (exposure limit), expiry times, T_f if E-9, enumeration limit
  query   : JUSTIFIED?(buy q | sell q) at a log position
            | COMMIT?(p) | REACTIVATE?(p)
            | STATE (U*, D*) at a log position
            | BASIS(p) at a log position
            | SAFETY at a log position (is S1/S2 currently violated in some world?)
verdict   : result, world_count, U*, D*, one witness world for any negative result,
            assumption_dependence
```

**Results:**
- JUSTIFIED / NOT_JUSTIFIED;
- UNBOUNDED (with the unbounded variable named);
- CONTRADICTION (with the conflicting items named);
- ENUMERATION_LIMIT, which is never a pass;
- for BASIS: INTACT / IMPUGNED / INDETERMINATE;
- for SAFETY: HOLDS / VIOLATED_IN_SOME_WORLD / VIOLATED_IN_ALL_WORLDS.

---

## 2. State model

### 2.1 Certain part

Replay the internal operations in log order with a state machine written from CP-1 B-21 to B-27 and B-31:
- PROPOSE, COMMIT, CONSUME, EXPIRE, RELEASE, INVALIDATE, REACTIVATE, GOV;
- suspension is **derived** (CP-1 B-22): after every entry, check every live commitment and suspend any that fails S1 or S2 with itself counted;
- a COMMIT, CONSUME or REACTIVATE entry in the log that would not be justified at its position is **refused**, and the refusal is recorded. It is not silently applied.

### 2.2 Uncertain part: hypothesis variables

| Variable | Domain |
|---|---|
| identity of an execution report without an exec_id | {new} ∪ {each compatible known execution} |
| binding of a list item to a stream item | {same, different}, unless every identity field is present on both and equal (then same) |
| content of each sequence hole | {non-economic} ∪ {fill of 1..remaining on a working order} ∪ {correction or bust of a known execution} ∪ {correction or bust of an execution unknown since bootstrap, delta any integer (bounded only by the assumptions in force)} |
| placement of each unsequenced item | every position consistent with its identity links and with E-3 and E-6 |
| snapshot inclusion | E-4P: exactly the transitions keyed ≤ W. E-4I: the state at some broker instant τ_s consistent with E-3 |
| adapter outcome for each consumed order | as E-7 allows: {not transmitted, pending, filled 0..q, rejected, cancelled} |
| fills not yet reported, on each working order | 0..remaining (under E-6, they are delivered eventually) |

### 2.3 Algorithm

1. **Propagate constraints** in log order. Discard assignments that contradict an observation.
2. **Detect unbounded domains first.** If an exposure-relevant variable has no finite domain, return UNBOUNDED and name it. **Never** truncate a domain to make it finite.
3. **Enumerate** surviving worlds up to the configured limit. If the limit is reached, return ENUMERATION_LIMIT.
4. **Per world**, compute P, Up and Down directly from CP-1 §2.5 by summing true quantities.
5. **Evaluate the query** per CP-1:
   - JUSTIFIED iff W is non-empty and determinate, and the action is safe in **every** world, with every live and suspended commitment counted;
   - BASIS per CP-1 B-29;
   - FINAL only under E-9.

---

## 3. Assumption dependence

For every query, rerun under each single-assumption relaxation of the profile: drop one assumption, or flip E-4 between P and I. Report every relaxation that changes the verdict. Results that change when E-6, E-8a, E-8b or E-7 is dropped are labelled **CONDITIONAL-ON-ENVIRONMENT**.

Report model results and environment dependence in **separate columns**.

---

## 4. Shared-reading register (to be challenged, not assumed)

| # | Reading used | Alternative a challenger should test |
|---|---|---|
| R-1 | exposure = P + remaining buys + unknown-side remaining | count of cancel-pending and immediate-or-cancel orders |
| R-2 | long-only: Down ≥ 0 | other envelopes |
| R-3 | live **and** suspended commitments count in every world | excluding suspended ones |
| R-4 | a correction replaces the quantity | additive corrections |
| R-5 | E-4P and E-4I are the only snapshot readings | settlement-based or other readings |
| R-6 | **strict consistency:** every attributed observation is a correct report, so one contradiction empties W | a tolerant reading, under which contradictions that cannot affect an action are scoped away |
| R-7 | single account, single instrument | multi-instrument interaction |
| R-8 | **both** R-8C and R-8V (CP-1 §1) are computed for every S1/S2 query | — (both are required outputs) |

Where a scenario's outcome differs between R-6 strict and tolerant, report both.

---

## 5. Limits

- Exhaustive enumeration is a reference for small scenarios, not a production component.
- The oracle checks the model under a profile. It cannot check that a profile is true of a broker.

*End of CP-2. No oracle has been built or run.*
