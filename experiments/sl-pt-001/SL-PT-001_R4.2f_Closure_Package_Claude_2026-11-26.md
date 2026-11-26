# SL-PT-001 | R4.2f Closure Package (G6-01 to G6-06)

**Date:** 2026-11-26 · **From:** Claude (Specification Lead / ARBITER) · **To:** Founder; GPT and Gemini B for one bounded closure round
**Responds to:** R4.2e closure round. Gemini B: **FREEZE-READY** (with one stale-pointer note). GPT: **NOT FREEZE-READY** (G6-01 to G6-05 blocking, G6-06 non-blocking).
**Authority:** none. **Nothing here is frozen.** No harness code exists.

## Disposition: all six GPT findings accepted

I checked each finding against the R4.2e text. All six are valid, and I'm not disputing any of them. G6-01 and G6-02 are defects I introduced in R4.2e and should have caught.

| Finding | Accepted? | Correction in R4.2f |
|---|---|---|
| **G6-01** inherited "must have committed by T_d(i+1)" contradicts append-start timing; a kill after the write leaves a record with no fsync | **Yes.** Both parts hold | §6.4 step 8: the deadline is now that the append **begins** before T_d(i+1). An append that completes after the boundary is **in-slot**, and the successor writes no CYCLE_OVERRUN. A surviving record shows it was written, **not that fsync completed**. A killed process's lock is released by the OS. The ordering claim is restated as **file order**, which holds with or without fsync. §6.3 names `lock_clock_at` as *now* for CYCLE appends. U117 adds (c) completes after the boundary, (d) kill after the write and before fsync, and (e) kill before the write, each with an unambiguous result. U-T5 adds the fsync point |
| **G6-02** R15 cannot fail alone; U121's expectation was unsatisfiable | **Yes**, and confirmed by computation | U121 now states the **exact failing set** per case, computed over every rule applicable to the side. EXIT while flat → **{R10, R15}**; open authorization → {R11, R16}; every other case is a single rule; plus two all-pass controls |
| **G6-03** "R8 cannot fail while flat" overstated | **Yes.** GPT's counterexample reproduces as {R8, R10} | Wording adopted: R8 **cannot fail independently of R10** in a normally constructed flat BUY. R6 and R7 are scoped to "normally constructed" |
| **G6-04** counting not bound to the recorded result | **Yes** | §11.4: a counted injection needs a precommitted plan and fixture, a **recorded** REJECTED, a **recorded** failing set exactly {intended rule}, recomputation agreeing with both, and distinct fixtures. A disagreement is a finding and is never counted. U118 adds case (e) |
| **G6-05** INJECTED-origin TER fields undefined | **Yes** | §10.4 gains an INJECTED row that fixes every field: open run's manifest; null slot, cycle_id, requests, bar and clock fields; fixture T_d, created and quote hash; V1–V11 and V12b NOT_EVALUATED with the new reason **`INJECTED`**; empty collections; SHADOW_EXPIRED recorded at once. §6.5: injections run only while a run is open, never enter the bar store, and never acquire slot credit |
| **G6-06** Branch H necessity unsupported | **Yes** | Now reads "separately trusted instrumentation outside the harness, outside the Stage A scope" |
| Gemini B note: stale §0/§16 pointers | **Yes** | Closing line and the §16 OI-16 row updated. Both are records |

**Fixture evidence, replacing v1:** `sl_pt_001_cl03_fixture_check_v2.py` (COMPUTED, Claude) addresses GPT's remark that v1 covered only part of the policy. It evaluates **every rule applicable to the side**, BUY and EXIT, on 17 cases: the five principal injections, R1, GPT's G6-03 counterexample, U121's eleven evaluator cases, and two pass controls. **All 17 match their expected failing sets.** The R8 bound is recomputed with the q < min region excluded and labelled as such. Exit code 0 means every expectation holds. GPT's v1 run stays valid for what v1 claimed.

## Carried forward without change

D-1, D-2, D-5, D-6, D-7, D-8 and CL-01, CL-02 were closed by both reviewers and are not reopened.

The R4.2e → R4.2f diff is larger than the substance because the amendment tags were renamed from `R4.2e D-x` to `R4.2f D-x` on every amended line. Substantive changes are limited to the rows in the table above.

## Artifacts and identifiers

| Artifact | SHA-256 | Git blob |
|---|---|---|
| Base: frozen R4.2c | `9d417fb5b22147eec6785816b239ad6b76215ea5f18e662432dc7e9cfb283d76` | `316d08c046dd7e1ea4a61be980c037b1c62037d5` |
| **R4.2f candidate** | `d29ed327d7a692c3383ae4e0b0320ad93a0104a78e88afd06ffa6a7fa090857b` | `0a736a5ca35b4a80618ca7689d5e1e4d9f8dbcf9` |
| **Diff R4.2c → R4.2f** (complete; 277 lines; +62/−21) | `fd18d21382c98b02ba9858e9c1a35228be81cf79d530c5520b98481cb44448cb` | `c7cb510e38388adc6a5b9587150fd6487f9a0d10` |
| **Diff R4.2e → R4.2f** (this round's changes; 263 lines) | `2b832e54dc84749715a686cce12b873007c5b5ea36595647fd78e1aca426dfbb` | `a03bb972a049fb50f608dc28e3ea9cdfbcbf4a47` |
| Fixture check v2 | `c6e3a22bc203d2780a93f2da9d4f6032a0a7f3515f0ae998bacc3568602f1dc7` | `5a68da1776b73b705c99cab36ca0b44328af1791` |
| Superseded R4.2e (history) | `c8ccf49352fa30c7f8787581005240b96ab548b679796623fd2a415d3c58d7bf` | `3328e47fc4abbe080d74266373e2eaed9605d403` |
| GPT R4.2e review (verbatim) | `01f9937f8d8a2a8f7fa8e2b5e35101a3ca2ee10d6fb01d0bda20112889212b02` | — |
| Gemini B R4.2e review (verbatim) | `1e23317c8b35ae08000b5c31db05875b70835aa27c5df7333c96aae7cb0cc69c` | — |

**Diff integrity (COMPUTED, Claude):** both diffs, applied with `git apply` to clean copies of R4.2c and R4.2e respectively, reproduce R4.2f at `d29ed327…857b` exactly. Each of the 33 edits was asserted to match R4.2c exactly once.

## Limitations requiring founder acceptance at the freeze (updated)

- **U-I3:** V12a observations and `lock_clock_at` are HARNESS-ATTESTED.
- **U-T5:** an append that begins in-slot may complete after T_d(i+1). A surviving record does not prove fsync. The only bound is file order.
- **Coverage:** runtime injections demonstrate R1, R4, R5, R10, R12 and R13 only. The other rules' FAIL cases are evaluator-level unit tests (U121).
- **D-8:** the header artifact is the client's report, not a wire capture.

The residuals from the existing freeze record are unchanged.

## Bounded closure round: what to send

Use **new chats**. Send both reviewers frozen R4.2c, `SL-PT-001_R4.2f_Delta_vs_R4.2c.diff`, `SL-PT-001_R4.2f_Delta_vs_R4.2e.diff` and `sl_pt_001_cl03_fixture_check_v2.py`. **GPT** also gets its own R4.2e review. **Gemini B** gets its own R4.2e review only, not GPT's, so it stays independent. Don't send this package.

```
Bounded closure review, SL-PT-001 R4.2f. Inputs: frozen R4.2c (SHA-256 9d417fb5b22147eec6785816b239ad6b76215ea5f18e662432dc7e9cfb283d76); diff R4.2c -> R4.2f and diff R4.2e -> R4.2f (git format; applying either must give R4.2f SHA-256 d29ed327d7a692c3383ae4e0b0320ad93a0104a78e88afd06ffa6a7fa090857b); a fixture/policy feasibility script (exit 0 iff all expectations hold); your own R4.2e review.
Review ONLY the R4.2e -> R4.2f changes, their direct dependencies, and any defect they introduce. Items closed in R4.2e by your review are not reopened unless these changes affect them. Most changed lines are an amendment-tag rename (R4.2e D-x -> R4.2f D-x); ignore those.
Targets: G6-01 (append-start deadline; in-slot completion after the boundary; kill before or after fsync; file order), G6-02 (U121 exact failing sets incl. EXIT-while-flat {R10, R15}), G6-03 (R8 not independent of R10), G6-04 (counting bound to recorded REJECTED, recorded failing set and agreeing recomputation), G6-05 (INJECTED-origin TER row, reason INJECTED, run-open requirement, no bar store, no slot credit), G6-06 (independence wording), and the updated closing line and OI-16 row.
For each: CLOSED / NOT CLOSED with a concrete counterexample. List any newly introduced defect. Final verdict: FREEZE-READY or NOT FREEZE-READY.
No harness code, credentials, orders or TER output exist or may be requested.
```

Commit both replies verbatim to `reviews\` before anything else. If both close, the next step is your R4.2f freeze record, which also re-points FD-5 to R4.2f.
