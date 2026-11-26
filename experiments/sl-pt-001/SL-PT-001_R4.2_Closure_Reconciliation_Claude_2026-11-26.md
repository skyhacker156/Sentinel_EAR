# SL-PT-001 R4.2 Closure Reconciliation

**Author:** Claude. **Date:** 2026-11-26. **Status:** **NOT FROZEN.** No harness, no test executed, no credential, no order.

**Inputs:**

| Input | Identifier |
|---|---|
| R4.2 | blob `f87ad21f…` |
| GPT closure check | `reviews/SL-PT-001_R4.2_Closure_Check_GPT_2026-11-26.md`, SHA-256 `13b66275…6954`; read the full R4.2 and the R4.1 reconciliation |
| Gemini account B closure check | `reviews/SL-PT-001_R4.2_Closure_Check_GeminiB_2026-11-26.md`; read **only** the clean excerpts (§5.6, §8.1.1, §11.2) |

**Output:** **R4.2a**, `SL-PT-001_R4.2a_Stage_A_Review_Candidate_Claude_2026-11-26.md`.
- SHA-256 `9fdb7555b3914ab755686ad4fe755bf6ac703a04069d79b821963c0e1e8ccacb`
- git blob (local) `e5e10cebf934b9bcd3007b36e86c5a8e8914d023`

---

## 1. Verdicts

| Reviewer | Verdict |
|---|---|
| GPT | **NOT FREEZE-READY**; blockers G3-01, G3-02, G3-03 |
| Gemini B | **CLOSED WITH CONDITIONS** (for the three excerpted sections) |

Both confirmed that every R4.1 finding is closed or conditionally closed. Neither found a new Stage B dependency.

---

## 2. Finding-by-finding

| RC | Finding | Raised by | Claude check | Disposition | R4.2a change |
|---|---|---|---|---|---|
| RC3-01 | **the 3 s boundary:** the inclusive ±2 s checks allow a round trip of exactly 3 s; R4.2's text claimed "< 3 s" and U98 required 3 s to fail | **GPT G3-01 / G3-05 (High; blocker).** Gemini B said "≥ 3 s cleanly fails", which is **wrong at exactly 3 s** | **verified:** width = 1 s + RTT, so the checks pass at RTT = 3 s | **accept; blocker** | V12b condition 3: RTT < 3 s, an explicit ceiling (GPT's option 1); claim corrected; U79 fixed at RTT = 1 s; U98 at 3 s − 1 ns / exactly 3 s / 3 s + 1 ns |
| RC3-02 | the closed schema still listed an undefined "offset estimate" field | **GPT G3-02 (blocker)** | **verified** | **accept; blocker** | field removed; the clock fields defined in §5.6 are the only clock fields |
| RC3-03 | early-exit TERs: no encoding for checks not run or artifacts not fetched | **GPT G3-03 (High; blocker)** | **verified:** a V12a BOUNDARY_FAIL could not satisfy the closed schema | **accept; blocker** | §10.4: PASS / FAIL / NOT_EVALUATED (with a reason); `null` for absent artifacts, clock fields and computed values; a per-path table; U108 |
| RC3-04 | U105 not reproducible | GPT G3-04 (Medium) | verified | accept | four exact vectors, **COMPUTED by Claude with exact rationals**: a cent-ceiling case, a budget-step case, a floor case and an exact case |
| RC3-05 | missing `Date`; t_recv < t_send (a backward clock step) passes silently | **Gemini B3-01 (Low)** | **verified.** A backward step shrinks the interval and can pass | accept | V12b conditions 1 and 2; wall clock required; assumption A-CLK2 (steps smaller than the round trip are undetectable); U106, U107 |
| RC3-06 | L undefined in §8.1.1 | Gemini B3-02 (High) | **not a defect in R4.2:** L is defined in **§7.2**, a Stage A section. Gemini saw only the §8.1.1 excerpt, so this is an **artifact of the excerpt** | **reject as a defect; severity disputed.** Clarity accepted | §8.1.1 cross-references §7.2 |
| RC3-07 | shadow reserved BTC undefined | Gemini B3-03 (Low) | verified | accept | `shadow_reserved_btc` with its lifecycle; U110 |
| RC3-08 | budget off the cent grid if the opening cash has sub-cents | Gemini (within B3-02) | verified | accept | opening cash must be a multiple of $0.01; premises of the R ≤ budget claim stated |
| RC3-09 | INCOMPLETE versus the U77 mismatch: double-reported | Gemini B3-04 (Low) | verified | accept | reported once, under INCOMPLETE |
| RC3-10 | OVERRUN masks a malformed record, or a CYCLE alongside a CYCLE_OVERRUN | **Gemini B3-05 (Medium)** | verified | accept | a 9-row precedence: integrity failure first; then CONFLICT (overrun plus cycle); then OVERRUN; then the rest; U109 |
| RC3-11 | the audit's `now ≥ T_d(N)` depends on the clock | Gemini (B2-01 notes) | the audit runs after the fact, on the founder's command; the classification depends on records, not on the audit's clock | **reject** (no change) | — |

**Missed by each reviewer:**
- **GPT missed** B3-01, B3-03 and B3-05.
- **Gemini missed** G3-02 and G3-03, which were outside its excerpt, and **got G3-01's boundary wrong**.
- Gemini's one HIGH finding (B3-02) came from the excerpt's limited view.

**One finding is rejected as a defect** (RC3-06). Its clarity improvement is still made. One observation is rejected outright (RC3-11).

---

## 3. A founder item raised by this reconciliation

**OI-18 (blocks the Stage A freeze).** Decision record v2 accepted "|offset_estimate| ≤ 2 s". Since R4.2, the specification enforces that bound with an **interval check plus a round-trip ceiling of less than 3 s**. That is stricter, but it is not the measurement the decision names.

**The founder should confirm in writing that the interval check implements R4-11.** A one-line decision record v3 is enough.

---

## 4. Next step

**A closure check of R4.2a only.**
- **GPT:** R4.2a plus this reconciliation. It should confirm G3-01 to G3-05 are closed and that nothing new was introduced.
- **Gemini B:** the clean excerpt `GeminiB_R4.2a_Closure_Check_CLEAN.txt` only. It covers §5.6, §8.1.1, the §10.4 table, §11.2 and the new tests; attributions are removed; there is no GPT content. It should confirm B3-01 to B3-05.

**Then:** OI-18 confirmed, and a founder Stage A freeze decision.
