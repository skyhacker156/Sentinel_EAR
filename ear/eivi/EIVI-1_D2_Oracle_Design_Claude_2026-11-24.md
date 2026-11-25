# EIVI-1 Deliverable 2: Independent Oracle Design

**Date:** 2026-11-24 | **Author:** Claude, Specification Lead | **Initiative:** EIVI-1, Workstream B
**Classification:** design only. **No oracle has been built or run.** Oracle construction is not authorized by this dispatch (it authorizes oracle *design*). Building one requires a separate founder decision.
**Normative input:** D1 (behavioral specification) only. Not the candidate.

## 0. Independence requirements

These requirements, not this document's content, are what would make the oracle independent.

| # | Requirement | Why |
|---|---|---|
| I-1 | **Built by a party other than the candidate's author.** Claude may not write oracle code. Gemini, a human engineer, or a separately instructed agent with no access to the candidate | otherwise the oracle and the candidate share the same mind |
| I-2 | The builder reads D1, this document and D3 only. **Not** Rev 3.2, the R-series reviews, or the candidate formulas | otherwise interpretation leaks across |
| I-3 | **Different computational principle**: explicit enumeration of worlds, not interval arithmetic or status tables | a shared method shares the same errors |
| I-4 | No shared code, libraries for domain logic, or test fixtures with any candidate implementation | shared bugs |
| I-5 | Every expected result in D3 is recomputed by the oracle. A disagreement between the oracle and D3's hand-derived expectation is reported, **not** resolved toward either | D3 is also Claude's |
| I-6 | **Known-defect recall:** the oracle must flag every historical counterexample (CX-01 to CX-68) as unsafe or over-denying. Any it fails to flag is a defect in the oracle or in D1 | it shows the oracle can see errors |
| I-7 | **Correlated-interpretation register (§6):** places where D1 and the candidate share one author's reading are listed and probed by Gemini | independence cannot be complete; the residue is declared |

---

## 1. Interface

```
oracle(log, profile, config, query) → verdict
  log     : ordered list of observations and internal operations (D1 B-01)
  profile : assumption switches {E-1 … E-11, E-4 ∈ {P, I}} (D1 §3)
  config  : L, TTLs, T_f (if E-9), limits on world enumeration
  query   : JUSTIFIED?(action) at a log position
            | EXPOSURE at a log position
            | BASIS(decision, later position)
verdict   : { result ∈ {JUSTIFIED, NOT_JUSTIFIED, UNBOUNDED, CONTRADICTION, ENUMERATION_LIMIT},
              world_count, U*, D*, witness worlds, assumption_dependence }
```

**ENUMERATION_LIMIT** is a first-class result. It means the oracle could not decide, never "pass". It counts as NOT_JUSTIFIED for safety comparisons.

---

## 2. State model (independent of the candidate)

### 2.1 Certain part (internal state)

The certain part is a straightforward replay of internal operations:
- proposals;
- commitments with status {live, suspended, consumed, ended};
- fixed expiry times;
- configuration and model versions in force.

It is fully determined by the log. It is replayed with a simple state machine written from D1 B-21 to B-27 and B-31.

### 2.2 Uncertain part (world variables)

For a log prefix, the oracle builds a finite set of **hypotheses**:

| Variable | Domain |
|---|---|
| identity of each execution report | known exec_id; or, if missing, {new} ∪ {each compatible known execution} (B-07) |
| binding of each cross-path pair | {same, different} unless both carry a complete identity (B-09) |
| content of each sequence hole | {non-economic} ∪ {execution of quantity k : k ∈ Q} (B-11). **If Q is unbounded, the hypothesis is UNBOUNDED**; no cap is imposed |
| unobserved intermediate versions | as holes, per execution (B-05) |
| placement of each unsequenced item | every position consistent with its identity links (B-15) |
| snapshot inclusion | under E-4P: the set of transitions keyed ≤ W. Under E-4I: every broker instant τ_s and the version state of each execution at τ_s consistent with E-3 |
| adapter outcome for each consumed order | {not transmitted, transmitted–pending, transmitted–filled k, rejected, cancelled}, as E-7 allows |
| fills of each working order | 0 … remaining, as the evidence allows |

A **world** is one assignment. Consistency is checked against every observation, in log order, under the profile.

### 2.3 Enumeration strategy

1. **Generate** assignments lazily, with constraint propagation: prune an assignment as soon as it contradicts an observation.
2. **Detect unbounded domains first.** If any exposure-relevant variable has an unbounded domain after propagation, return UNBOUNDED with that variable as the witness. The oracle never truncates a domain to make it finite.
3. **Enumerate** surviving worlds up to the configured limit. If the limit is hit, return ENUMERATION_LIMIT.
4. **Per world:** compute P_w, Up(w) and Down(w) directly from first principles (D1 §2.5), by summing true quantities. No formula from the candidate is used.

**Practicality:** D3 cases are small by design (≤ 8 executions, ≤ 3 holes, small Q). World counts are expected in the hundreds to low thousands. Larger runs are out of scope for Phase 1.

---

## 3. Authorization evaluation

- **JUSTIFIED?(buy q):** JUSTIFIED iff W is non-empty and determinate, and **for every** w: Up(w) + q ≤ L, with every live or suspended commitment counted as working in w.
- **JUSTIFIED?(sell q):** JUSTIFIED iff W is non-empty and determinate, and for every w: Down(w) − q ≥ 0.
- **Witness:** for NOT_JUSTIFIED, one world in which the action is unsafe. This makes each disagreement concrete and checkable by hand.
- **BASIS(decision at e_b, later position e′):** recompute W(e_b ∪ R, A), where R is the set of items received in (e_b, e′] that **could** describe the world at or before e_b. Every placement of a doubtful item is a world, so R is not decided by rule. Return:
  - INTACT: safe in all worlds;
  - IMPUGNED: unsafe in all;
  - INDETERMINATE: some of each (D1 B-29).
- **FINAL(x, t):** only if E-9 is in the profile. Remove worlds containing corrections to x occurring after occurrence + T_f. The verdict records "depends on E-9".

---

## 4. Assumption dependence (exposed, never concealed)

For every query, the oracle also runs the query under each **single-assumption relaxation** of the profile: drop E-k, or for E-4 flip P ↔ I. It reports:

```
assumption_dependence = { E-k : verdict_without_E-k   for each k where verdict changes }
```

A verdict that depends on E-6 or E-8 (which, when dropped, make almost everything UNBOUNDED) is labelled **CONDITIONAL-ON-ENVIRONMENT**. These are the Track B items. **Track A results (correctness under the profile) and Track B dependence are reported in separate columns and never merged.**

---

## 5. Comparison protocol (oracle vs candidate)

Run each D3 case through the oracle, and through a candidate implementation if one is ever separately authorized. Until then, compare against the candidate's hand-derived expected outcome.

| Candidate | Oracle | Classification | Severity |
|---|---|---|---|
| ALLOW | JUSTIFIED | agree | — |
| ALLOW | NOT_JUSTIFIED / UNBOUNDED / CONTRADICTION / ENUMERATION_LIMIT | **UNSAFE PERMISSION** | critical: violates the central invariant |
| DENY | JUSTIFIED | over-denial | recorded; measures availability cost (C-14) |
| DENY | not justified | agree | — |
| candidate bound U_c | oracle U* | U_c < U* → **unsound bound**; U_c > U* → conservative gap, recorded | critical / informational |
| candidate status reason | oracle witness | traceability check: the candidate's reason must name a cause that appears in the oracle's witness | informational |

**Mutation testing (Phase 2, not authorized now).** Seed known defects into a candidate implementation, using the CX list as the mutation catalogue. The oracle-based comparison must kill every mutant.

---

## 6. Correlated-interpretation register

These are places where the oracle's semantics come from the same author's reading as the candidate. Each must be challenged independently (Gemini).

| # | Shared reading | Alternative a challenger should test |
|---|---|---|
| R-1 | exposure = position + remaining buys + unknown-side remaining (Up) | should cancel-pending orders count? Should unfilled IOC orders? |
| R-2 | long-only: Down ≥ 0 is the reduction limit | the envelope may be wrong for the intended strategy |
| R-3 | every live **and suspended** commitment counts in every world | could suspended commitments be safely excluded? (D1 says no) |
| R-4 | a correction replaces the quantity; it does not add a new fill | broker semantics may differ (E-5) |
| R-5 | E-4P and E-4I as the only snapshot readings | other semantics (for example a settlement-based snapshot) |
| R-6 | world consistency requires *every* attributed observation to be a correct report | an alternative tolerant reading (some reports wrong) makes nearly everything UNBOUNDED |
| R-7 | single account, single instrument | multi-instrument interactions are not modelled |

---

## 7. Limits of this design

- **Claude-authored.** Independence depends entirely on I-1 to I-7 being honoured in construction.
- **Exhaustive enumeration does not scale.** It is a reference for small adversarial cases, not a production component.
- **The oracle verifies the model under the profile (Track A).** It cannot establish that any profile is true of a broker (Track B). That needs external evidence (D5).
- **The oracle's own correctness is unverified until** (a) it recalls the CX catalogue (I-6) and (b) an independent party reviews it.

*End of D2. No oracle exists and nothing has been executed.*
