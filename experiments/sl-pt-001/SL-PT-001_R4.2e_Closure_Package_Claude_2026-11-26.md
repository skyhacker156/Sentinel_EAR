# SL-PT-001 | R4.2e Closure Package (CL-01 to CL-04)

**Date:** 2026-11-26 · **From:** Claude (Specification Lead / ARBITER) · **To:** Founder; GPT and Gemini B for one bounded closure round
**Responds to:** Founder directive "SL-PT-001 / R4.2d CLOSURE" (2026-11-26)
**Authority:** none. **Nothing here is frozen.** No harness code exists.

The four closure conditions required changes to normative wording. The candidate is therefore **R4.2e**, which supersedes R4.2d (committed at `58661d4`, never frozen). R4.2d is kept as history. R4.2e still contains only D-1 to D-8. CL-01 to CL-04 changed the wording of D-2, D-3, D-4 and D-7 and added nothing outside those items.

---

## 1–3. Artifacts and identifiers

| Artifact | SHA-256 | Git blob |
|---|---|---|
| Base: frozen R4.2c | `9d417fb5b22147eec6785816b239ad6b76215ea5f18e662432dc7e9cfb283d76` | `316d08c046dd7e1ea4a61be980c037b1c62037d5` |
| **R4.2e candidate** `SL-PT-001_R4.2e_Stage_A_Amendment_Candidate_Claude_2026-11-26.md` | `c8ccf49352fa30c7f8787581005240b96ab548b679796623fd2a415d3c58d7bf` | `3328e47fc4abbe080d74266373e2eaed9605d403` |
| **Complete diff** `SL-PT-001_R4.2e_Delta_vs_R4.2c.diff` (238 lines, git format) | `c842ab6a28c09a07b400127d79761d20f36750b2285c3213be0288e27f990847` | `86864676634a38a1baa3c47440dc284448d5a571` |
| CL-03 check script `sl_pt_001_cl03_fixture_check.py` | `d1e5956554de707c561e4c3a2487056083e71c496701bda81d9138da0b5af91d` | `c810adc09fd15a19871500b306c4812157ba6b3f` |
| Superseded candidate R4.2d (history) | `68fe01e0f4d98fd575c13edb33c99030d54029a9b00723fedaf42f01ca059667` | `b60327c673f19285813311b0ee343ac6596ed813` |

**Diff integrity (COMPUTED, Claude):** the diff's `index` line names `316d08c0…` → `3328e47f…`. Applying it with `git apply` to a clean copy of R4.2c reproduces R4.2e at SHA-256 `c8ccf493…7bf` exactly. Change size: 55 insertions, 16 deletions, 25 hunks. Every line outside the hunks is byte-identical to R4.2c. Each of the 28 edits was asserted to match R4.2c exactly once, so none could apply silently. This was checked by Claude, not reproduced independently. Reviewers can repeat it with `git apply --check`.

---

## 4. Disposition of closure conditions

### CL-01: Seed and evidence custody → **met by D-7 (§11.5)**

R4.2e defines a three-step, pushed-commit order:
1. **Seed commitment** before the first audited T_d0. Only SHA-256 of a 64-hex-character seed is committed. The seed is 32 bytes from the OS cryptographic random source, so the hash cannot be inverted by guessing.
2. **Evidence fixing** after the last RUN_CLOSE and **before** the reveal. The commit names the evidence commit, the chain head, the audited manifests, and the **eligible population** (count, first and last `seq` of the SCHEDULED CYCLE records).
3. **Reveal** of the seed in a later commit.

The auditor checks all three against each other and checks their order in history. There is exactly one seed commitment per audit scope. The following each invalidate M1-6:
- evidence committed after step 2;
- a second seed commitment for the same manifests;
- any re-draw.

A failed reconstruction is reported, never re-drawn. The cleartext seed at `07f43e0` is preserved and **marked never usable**. Test U120 covers (a)–(e).

### CL-02: Attestation boundary → **met by D-2 (§6.4 step 1, §11.1, §13, §15)**

- V12a recomputation shows only that **the recorded observations satisfy the rule**. It is stated as **CONDITIONAL on those observations being true** (HARNESS-ATTESTED, U-I3).
- The name pattern and the closed config **define the checked scope only**. They explicitly do not establish absence of credentials under other names, stores or forms (U-I2 unchanged).
- §13 adds two prohibited claims: credential absence beyond the checked scope, and any V12a or timing property stronger than HARNESS-ATTESTED. Branch C text is unchanged.

### CL-03: Injection satisfiability → **met by D-4 (§6.5, §7.3 R3, §8.1.1, U121), with evidence**

- **Constructible (COMPUTED** by the check script, exact rationals, R4.2c policy values): flat BUY fixtures that fail **exactly one** rule exist for **R1, R4, R5, R10, R12 and R13**. That is six distinct rules, against five required. The fixtures:
  - R4: a 16 s old quote;
  - R5: ask 92000 / bid 90000;
  - R10: price 2,000,000, so q floors to 0;
  - R12: cash $400;
  - R13: created = T_d + 31 s;
  - R1: an instrument field, only if the fixture shape allows one.
- **Unreachable by construction (DERIVED, spot-checked):**
  - **R6 and R7** cannot fail: R ≤ budget ≤ min($150, cash_available).
  - **R8** cannot fail while flat: q ≥ 0.0001 forces L ≤ $150/(0.0001 × 1.0025), so the exposure stays below $300 (worst grid case $299.63).
  - **R2, R3, R11 and R16** cannot fail for a constructed BUY.
- **Dependency closed:** R3 is defined as schema-only. Without that, R10's fixture (q = 0) could also fail R3, and attribution to a single rule would break.
- **Coverage preserved:** BUY-only applies to the **M1-1 injections only**. Every §14 test and the §11.6 gate still require executed, fixture-backed EXIT and long-position cases. The FAIL cases of R2, R3, R6, R7, R8, R11, R16, R9 and R15 are evaluator-level unit tests (U121).
- **Adjacent gap closed:** §8.1.1 now states that EXIT has no R or budget, so **R6, R7, R8 and R12 do not apply to EXIT**. Without this, the required EXIT tests had no defined expected result. This was GPT's contract note on the EXIT R convention.

### CL-04: Commit timing semantics → **met by D-3 (§5.4, §6.4 step 8, §10.4, §15 U-T5)**

- The field is renamed **`committed_at` → `lock_clock_at`** and defined as the clock sample at the **start** of the append, taken under the lock.
- The procedure is: sample, check, write, flush, **fsync**, then release the lock.
- R4.2e says explicitly that **completion and durability are not timestamped**. Their only bound is ordering: no later slot can read the token state until the lock is released after fsync.
- A completion after T_d(i+1) by the write-and-fsync duration is **not excluded**, and is disclosed as U-T5.
- A record lost before fsync fails closed (INCOMPLETE or OVERRUN). Durable evidence is presence in a pushed commit.
- No new infrastructure is added: fsync is a standard library call.

---

## 5. Limitations requiring founder acceptance (at the R4.2e freeze)

| ID | Limitation | Consequence |
|---|---|---|
| U-I3 | V12a observations and `lock_clock_at` are HARNESS-ATTESTED (Branch C) | no independent claim of credential absence or commit timing |
| U-T5 | append completion and durability not timestamped; overshoot past T_d(i+1) by write+fsync duration not excluded | "within slot" means *append began before the boundary, and ordered before later slots* |
| CL-03 scope | runtime injections can demonstrate only R1, R4, R5, R10, R12, R13; nine other rules' FAIL cases are unit tests only | extends OI-08: those rules are never exercised by a runtime injection in Stage A |
| D-8 | header artifact is client-reported, not a wire capture | V1 and V12b inputs rest on the client's report |

The existing freeze-record residuals are unchanged: A-CLK, A-CLK2, data-host UTC accuracy, Branch C, U-I2, U-O2 and U-O4, OI-08, and the FD-6 common-mode dissent.

---

## Bounded closure round: what to send

Send **the same three files** to both reviewers, in **new chats**: frozen R4.2c, `SL-PT-001_R4.2e_Delta_vs_R4.2c.diff`, and `sl_pt_001_cl03_fixture_check.py`. Do not send this package, the reconciliation, or any chat, so each reviewer judges the text and not my reasoning. GPT may also receive its own interface contract v1, which it wrote.

**Prompt (identical for both):**
```
Bounded closure review, SL-PT-001 R4.2e. Inputs: frozen R4.2c (SHA-256 9d417fb5b22147eec6785816b239ad6b76215ea5f18e662432dc7e9cfb283d76), the diff to R4.2e (git format; applying it must give SHA-256 c8ccf49352fa30c7f8787581005240b96ab548b679796623fd2a415d3c58d7bf), and a fixture feasibility script.
Review ONLY the changed text, its direct dependencies in R4.2c, and any defect the changes introduce. Do not reopen other sections.
Closure conditions to test:
CL-01 commit-reveal seed; evidence commit, chain head and population fixed before reveal; no substitution or resampling; old seed preserved as superseded.
CL-02 V12a recomputation conditional on harness-attested observations; name matching defines checked scope only; no stronger isolation claims.
CL-03 five intended-rule BUY fixtures constructible with single-rule attribution; R6/R7/R8/R12 dependencies; BUY-only does not remove EXIT/long-position test coverage.
CL-04 clock sample under lock distinguished from append completion and durability; no pre-append timestamp presented as proof of completed or durable commit.
For each of D-1 to D-8 and CL-01 to CL-04: CLOSED / NOT CLOSED, with a concrete counterexample if NOT CLOSED. List any newly introduced defect. Final verdict: FREEZE-READY or NOT FREEZE-READY.
No harness code, credentials, orders or TER output exist or may be requested.
```

Commit each reviewer's reply **verbatim** to `experiments/sl-pt-001/reviews/` before sending it on. If both close, the next step is your R4.2e freeze record, which should also re-point FD-5 to R4.2e.
