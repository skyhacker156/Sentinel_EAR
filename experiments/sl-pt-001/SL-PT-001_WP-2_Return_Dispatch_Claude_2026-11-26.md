# SL-PT-001 | WP-2 Return Dispatch: Harness Construction Map

**Date:** 2026-11-26 · **From:** Claude (Specification Lead / Harness Development) · **To:** Founder
**Responds to:** "WP-2: Harness Creation Strike" (reference HEAD `6948668`)
**Code written under this dispatch:** none.

Tags used throughout: **DESIGNED** (specified, not built) · **IMPLEMENTED** · **EXECUTED** · **OBSERVED** · **COMPUTED** · **UNVERIFIED**. Nothing below is IMPLEMENTED or EXECUTED.

---

## 1. Freeze and authorization status (OBSERVED, from a clone at `6948668`)

| Item | Status |
|---|---|
| Frozen Stage A authority | **R4.2c**, blob `316d08c0…`, freeze `030e7c0`, anchored `1f89cb7`, confirmed by decision v4 `b53b0cf` |
| FD-5 | authorizes building to **R4.2c** (`5252322`) |
| R4.2f | committed at `6948668`, blob `0a736a5c…` (verified); **NOT frozen** |
| R4.2f closure round | **not yet in the repository**: no R4.2f reviews under `reviews/` |
| FD-6 v1 (contract, auditor, seed) | committed (`b2bbbbb`, `07f43e0`); the v1 seed is superseded under R4.2f D-7 once frozen |
| FD-6 v2, new seed commitment | not started (they follow the R4.2f freeze) |
| Harness code, tests, TER, live data | **none exist** |

---

## 2. Minimum viable harness file tree (DESIGNED)

Six modules plus a wrapper. Standard library only, Python 3.12, with tests run by `unittest`, so nothing has to be installed.

```
harness/
  sl_pt_001/
    exact.py      exact rationals, token parsing, RFC-3339 → ns, rounding points
    market.py     allowlisted keyless client (http.client), V12a, V12b, artifact capture
    validate.py   V1–V11, Q1–Q5, bar-store fold
    decide.py     SMA-20/50, crossover, mapping, sizing, policy P-0.2, shadow ledger
    evidence.py   TER-1 build, JCS, record hash, chain append + lock + fsync, manifest checks
    cycle.py      slot ownership, run token, cycle procedure, injection runner, CLI entry
  wrapper.py      invocation log line + start harness; nothing else (§6.1)
  config/harness_config.json   {"client_allowlist": ["data.alpaca.markets"]}
  tests/  test_exact.py test_validate.py test_decide.py test_evidence.py test_cycle.py test_market.py
          fixtures/            (bars, quotes and ledgers for unit tests; never live)
  tools/run_tests.ps1          runs the suite, writes the retained result log
experiments/sl-pt-001/policy/P-0.2.json   (§7.4; evidence root per contract v1 §5)
```

**Design choices that serve the boundary** (DESIGNED):
- `market.py` uses `http.client.HTTPSConnection`, not `urllib`, because urllib silently honours `HTTPS_PROXY` and similar environment proxies. The allowlist check runs before any socket opens. No authorization header exists anywhere in the code.
- `decide.py` holds the shadow ledger as constants, because the ledger never changes in Stage A (§8.1). Folding it in removes one module and one interface.
- There is no harness-side milestone counter, because §11.4 says such a counter is never evidence.

---

## 3. Requirement-to-component mapping (DESIGNED)

| Component (dispatch) | File | Governing sections | Stage A tests |
|---|---|---|---|
| Market data client | `market.py` | §2.2–2.3, §4.1–4.3, §5.6, §6.4 steps 1–4 | U79, U112, U113, U116, X8, X9, U95 |
| Validation engine | `validate.py` | §4.4–4.11 | U5–U8, U11–U13, U17, U24, U31, U35–U40, U78, U80, U84, U85, U89, U94, U111, U115 |
| Signal engine | `decide.py` | §3.1–3.4, §5.1 | U1–U4e, U18, U25, U87 |
| Policy evaluator | `decide.py` | §7, R1–R13, R15, R16 | U28, U33, U44–U47, U81, U82, U119, U121, X1–X7 |
| Shadow ledger | `decide.py` | §8.1, §8.1.1 | U33, U82, U121 |
| Cycle controller | `cycle.py` | §6.2–6.4, §5.3–5.4 | U15, U19, U52, U53, U73–U77, U83, U91, U117 |
| Evidence recorder | `evidence.py` | §10.1–10.5, §11.3 inputs | U9, U10, U26, U27, U34, U41–U43, U66–U72, U88, U114 |
| Injection runner | `cycle.py` | §6.5, §11.4 | U68, U91, U118 |
| Scheduler wrapper | `wrapper.py` | §6.1 | U73–U77 against the exported XML |
| Test suite | `tests/` | §14 (Stage "A"), §11.6 gate | all of the above, with retained output |

---

## 4. Implementation dependency order (DESIGNED)

| Strike | Builds | Depends on | External prerequisite |
|---|---|---|---|
| 1 | `exact.py`, then `decide.py`, then `validate.py` | — | none |
| 2 | `evidence.py` | 1 | **TER-1 contract v2** (key names, fixture shape) |
| 3 | `cycle.py`, `wrapper.py` | 1, 2 | Task Scheduler XML on your machine |
| 4 | `market.py` | 1, 2 | none (keyless) |
| 5 | full §14 Stage-A suite + §11.6 gate, retained | 1–4 | Python 3.12 on your machine |
| 6 | live shadow runs, injections, audit | 5 | auditor v2, seed commitment, manifest pushed before T_d0 |

---

## 5. Test execution sequence (DESIGNED)

1. **Per strike:** each module's unit tests, run by me here (COMPUTED/EXECUTED in my sandbox, labelled as such), then **re-run by you on Windows**. Only your run counts as Stage A evidence.
2. **Pre-live gate (§11.6):** the full Stage-A inventory, plus a pass case and a fail case for every Stage-A rule. You run `tools/run_tests.ps1`; it writes `harness/tests/results/<UTC>.txt` with the harness commit hash, `py -3.12 --version` and every test result. You commit and push the log. Failures and their fixes are committed too, never overwritten.
3. **Scheduler checks:** U73–U77 against the exported task XML.
4. **First live run only after** steps 2–3 are committed, contract and auditor v2 are committed, the seed hash is committed, and the manifest is pushed before T_d0.

---

## 6. Remaining blockers

| # | Blocker | Kind | Blocks | Smallest resolution |
|---|---|---|---|---|
| B-1 | R4.2f closure round not yet run | gate | code against changed sections | send the round (closure package `6948668`) |
| B-2 | **X8 expected result is unrepresentable.** `BOUNDARY_VIOLATION_ATTEMPT recorded` appears only in X8: it is not a chain type, TER field or terminal state, and both schemas are closed. X10's "recorded" has the same gap | test expectation defect, **inherited from R4.2c** (OBSERVED: only occurrence is line 1162) | the §11.6 gate (X8 and X10 must be EXECUTED) | at the R4.2f freeze, a non-normative **editorial note** in the freeze record, as was done for B5-01 and G5-01: "X8 and X10 'recorded' means recorded in the retained test output; `BOUNDARY_VIOLATION_ATTEMPT` is a test-output label, never a chain record or TER value (cf. U9)". This needs no new revision cycle. Reviewers may object in the round |
| B-3 | TER-1 contract v2 and fixture JSON shape | dependency | Strike 2 onward, injections | GPT, after the R4.2f freeze |
| B-4 | Python 3.12 on your machine | environment, UNVERIFIED | Strike 5 evidence | install from python.org beside 3.14 |

No other blocker was found. Everything else is an executable test obligation, not a design question.

---

## 7. Smallest executable increment under current authority

**Strike 1a: `exact.py` plus the signal and mapping part of `decide.py`, with its unit tests.**

**Why it is legitimate now (COMPUTED):** I compared R4.2c and R4.2f section by section. Every section Strike 1a implements is **byte-identical** in the two: §3.1–3.4, §4.4–4.6, §4.8, §4.10, §5.1–5.3, §5.5, §5.6, §6.2 and §7.2. Changed sections are excluded. That rules out §4.7 V2, §4.9 fold, §7.3 R3 and §8.1.1, so sizing and policy wait.

The increment therefore implements frozen R4.2c text, which FD-5 already authorizes, and the R4.2f freeze cannot change it. If you prefer to hold all code until the R4.2f freeze, as your dispatch's sequence implies, nothing is lost but time.

**Strike 1a tests:** U1–U4e, U18, U24, U25, U87 (signal and exactness); U5, U17, U78, U89 (completed-candle rule); U52, U53 (slot identity and §5.3 invariants). U28 and U44–U47 wait: they test §5.4, which changed, and policy results (§7.3). Delivered as files with a one-command Windows run.

---

## 8. Next founder action

1. **Run the R4.2f closure round** with the package already committed at `6948668`. This is the critical path.
2. **One decision:** *authorize Strike 1a now under existing FD-5*, limited to the byte-identical sections listed in §7, or hold all code until the R4.2f freeze.

My recommendation is to authorize. Every section it uses is unchanged in R4.2f, so there is no rework risk, and it makes the harness exist as soon as possible.
