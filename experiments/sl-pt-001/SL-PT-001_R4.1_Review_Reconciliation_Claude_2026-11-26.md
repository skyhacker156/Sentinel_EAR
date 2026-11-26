# SL-PT-001 R4.1 Stage A Review Reconciliation

**Author:** Claude. **Date:** 2026-11-26.
**Status:** reconciliation and targeted correction only. **NOT FROZEN.** No harness, no test executed, no credential, no order.

**Inputs:**

| Input | Identifier |
|---|---|
| R4.1 | blob `a653252a8b184f0e184c7f2b42b4dbba6ff49d3f` (commit `0a4ddaf…`, reported by the founder) |
| Gemini account B review | `reviews/SL-PT-001_R4.1_Stage_A_Review_GeminiB_2026-11-26.md`, SHA-256 `061cd1e4…7a80` |
| GPT review | `reviews/SL-PT-001_R4.1_Stage_A_Review_GPT_2026-11-26.md`, SHA-256 `32cb0950…fafe` |

**Output:** R4.2, `SL-PT-001_R4.2_Stage_A_Review_Candidate_Claude_2026-11-26.md`.
- SHA-256 `c06b3d7a46de5166cf1cfc29c2d392bb4ab4f3979def175b209745c34f033279`
- git blob (local) `f87ad21f4c70f558335070b843cb270e026005d2`

---

## 1. Review conditions

| Reviewer | Exposure as stated | Material read | Verdict |
|---|---|---|---|
| Gemini B | "R3 only; not R4.1". It reviewed R4.1, so this reads as "before this review". It had seen R4.1's text, including Claude findings incorporated into it | the six Stage A chunks (Stage B sections omitted) | **CONDITIONALLY FREEZE-READY** (conditions: B2-01, B2-02) |
| GPT | had seen R3 and Claude's earlier findings; states it did not use them as evidence | the committed file at `0a4ddaf` (981 lines), plus the chunks as aids. It did **not** verify the blob ID itself | **NOT FREEZE-READY** (blockers: G-01, G-02, G-03) |

**Neither review was shown the other before delivery** (founder's process). **Agreement between them is not verification.**

---

## 2. Finding-by-finding matrix

Every finding was checked against the R4.1 text by Claude. "Verified" means Claude confirmed the mechanism in the text, not that any behaviour was observed.

| RC | Finding | Raised by | Claude check | Disposition | R4.2 change |
|---|---|---|---|---|---|
| RC2-01 | **Stage A sizing is undefined inside the freeze:** §7.1 sends q and R to §8.2, which is Stage B draft | **GPT G-01 (Critical)**; Gemini did not raise it | **verified, and worse than stated:** the BUY quantity formula q = floor(budget / (L × (1 + f_res))) and `budget` were **dropped entirely** in R4 (they existed in R3 §6.2). Only R's formula survived, in §8.2. This is Claude's consolidation error | **accept; blocker** | new §8.1.1 (budget, q, R, q_exit, cash_available, f_res, reservation timing, increment status); §7.1 step 3 and §8.2 point to it; U105 |
| RC2-02 | **V12 is circular:** the clock check needs the bars response, but V12 runs before any fetch | **GPT G-02 (High)** | **verified** | **accept; blocker** | V12 split into V12a (pre-fetch: credentials, allowlist) and V12b (clock check on the bars response, before V1); §6.4 reordered; U96 |
| RC2-03 | **The clock estimate ignores transit time:** "Date − receipt" does not bound the offset | **GPT G-03 (High)**; Gemini B2-01 touches clock drift but not transit | **verified.** Example: a +4 s server offset with 2 s transit yields an estimate near +2 s, which passes | **accept; blocker** | §5.6 replaced by an offset **interval** (θ_low = D − t_recv, θ_high = D + 1 s − t_send); pass iff both lie within ±2 s; assumption A-CLK stated; this implies a round trip < 3 s; U97, U98. The accepted 2 s bound (R4-11) is kept and now actually enforced |
| RC2-04 | **"CONFIRMED" has two meanings:** first observation versus two fetches | **GPT G-04 and Gemini B2-03, independently** | verified | accept (non-blocking per both) | states BASELINED / PENDING / CONFIRMED plus an observation count; U35 restated; U100 |
| RC2-05 | the anti-lockout claim overstated for continuously changing bars | Gemini B2-03 | verified: R4.1's wording was conditional, but the multi-slot case was not stated | accept | §4.9 states the condition and the fail-closed, UNBOUNDED case (U-D9); U101 |
| RC2-06 | **a proposal that has not committed by T_d(i+1) is refused and becomes MISSING** | **Gemini B2-01 (High)** | **partially verified.** The refusal is real, and so is the misclassification. **Disputed:** that a "valid qualifying proposal" is lost. A cycle that cannot commit within its slot **should not** qualify under the hard-boundary rule, and R4.1 already made that outcome non-qualifying. The defect is that the classification was imprecise and unexplained, not that a valid slot was rejected | **accept the classification defect; dispute the severity** (Claude: MEDIUM; Gemini: HIGH) | §6.4 step 8: an uncommitted cycle is overrun; RUN_CLOSE writes CYCLE_OVERRUN for the last slot; the auditor's INCOMPLETE class; U102, U104 |
| RC2-07 | MISSING versus CYCLE_OVERRUN precedence | **Gemini B2-02 (Medium; blocker)** | verified | **accept; blocker** (it determines the audit outcome) | §11.2 rows applied in precedence order: OVERRUN, then INCOMPLETE, then MISSING; U103 |
| RC2-08 | a crash leaves orphaned artifacts; "every observation remains in the chain" was overclaimed | GPT G-05 (Medium) | verified | accept (non-blocking) | §10.2 orphan rule (non-evidence, listed by the auditor); §4.9 claim narrowed to committed cycles; U99 at each crash boundary |
| RC2-09 | REPLAY has no representation in the closed schema | GPT G-06 (Low) | verified | accept | U9: REPLAY is an out-of-band label, never in a TER or the chain |
| RC2-10 | the credential-absence claim is broader than the check | GPT G-07 (Medium) | verified | accept | §2.2 narrowed to the checked scope (environment variables and the harness configuration file); §2.3 rationale restated within that scope; X9 covers both sources; U-I2 records other stores as not excluded |
| RC2-11 | qualifying NO_ACTION from EXIT-while-flat inflates the streak's apparent coverage | Gemini B2-04 (Medium) | verified as a disclosure issue. The behaviour is correct under CF-2 | accept (reporting only) | §11.3 exit report counts NO_ACTION by underlying signal; §13 claim limit added |
| RC2-12 | the audit should record the commit and chain head it audited | Gemini B2-05 (Medium) | verified | accept | §11.3 item 5 |
| RC2-13 | an "isolation" field name invites over-reading | Gemini B2-06 (Low) | verified | accept | field renamed `egress_scope` = "CLIENT_ALLOWLIST_ONLY" |
| RC2-14 | U7 compound; fixture-backed tests unlabelled | Gemini B2-07 (Low) | verified | accept | U7a and U7b; fixture-backed labels on U14, X5 and X6, plus a rule for others |
| RC2-15 | no symbol binding in the response | GPT §4.2 item 8 | verified: V1 checked fields, not the symbol key | accept | V1 binds the `BTC/USD` key; U95 |
| RC2-16 | crash-boundary fault injection | GPT §4.2 item 5 | — | accept | U99 |
| RC2-17 | verdict | GPT NOT READY; Gemini CONDITIONALLY | — | **disagreement recorded.** Claude sides with **NOT FREEZE-READY for R4.1**: GPT's G-01 to G-03 are verified defects that Gemini did not raise | — |

**Missed by each reviewer:**
- **Gemini B missed** GPT G-01, G-02 and G-03. G-01 and G-02 are mechanical defects in the text.
- **GPT missed** Gemini B2-01 and B2-02.
- Each reviewer caught blockers the other missed. That is the value of two reviews, and it is **not** evidence that no further defects remain.

**No finding was rejected.** One severity is disputed (RC2-06). Minority positions are preserved above.

---

## 3. Change log (R4.1 → R4.2)

| # | Section | Change | Closes |
|---|---|---|---|
| D-1 | header | R4.2 identity; base R4.1 blob; this reconciliation named as the source of changes | — |
| D-2 | §2.2, §2.3 | credential claim narrowed to the checked scope; rationale restated within that scope | RC2-10 |
| D-3 | §4.7 V1 | symbol-key binding | RC2-15 |
| D-4 | §4.7 V12 | split into V12a and V12b, with their ordering | RC2-02 |
| D-5 | §4.9 | BASELINED, PENDING and CONFIRMED with an observation count; claims narrowed; conditional anti-lockout | RC2-04, RC2-05, RC2-08 |
| D-6 | §5.6 | offset interval; assumption A-CLK; implied round-trip bound | RC2-03 |
| D-7 | §6.3, §6.4 | SKIPPED replaced by the new classifications; steps reordered (V12a, bars, V12b, quote); an uncommitted cycle at the boundary is overrun | RC2-02, RC2-06 |
| D-8 | §7.1, **§8.1.1 (new)**, §8.2 | Stage A sizing and shadow reservation; the missing q formula restored from R3 §6.2; §8.2 reuses it | RC2-01 |
| D-9 | §10.1, §10.2, §10.4 | RUN_CLOSE writes the final-slot overrun; orphan rule; `egress_scope` field; clock fields; bar-store state fields | RC2-06, RC2-08, RC2-13 |
| D-10 | §11.2, §11.3, §11.1 HOLD row | precedence order; OVERRUN, INCOMPLETE and MISSING; audited commit and chain head; NO_ACTION by signal; V12a and V12b references | RC2-06, RC2-07, RC2-11, RC2-12 |
| D-11 | §13 | the EXIT-while-flat claim limit | RC2-11 |
| D-12 | §14 | U7a and U7b; U9, U35, U79 and X9 restated; fixture labels; **§14.8: U95 to U105** | all test gaps |
| D-13 | §15 | U-I2, U-D9 and A-CLK added; U-T2 restated | — |

**Stage B sections are unchanged,** apart from §8.2's pointer to §8.1.1. That pointer is a Stage B change touching Stage A content only by reference, so it requires nothing more under the FD-5 rule.

---

## 4. Verdict and next step

**R4.1: NOT FREEZE-READY** (GPT's G-01 to G-03 are verified).

**R4.2 corrects every finding,** but **no reviewer has seen R4.2.** Three of the corrections are substantive new text:
- §8.1.1, sizing;
- §5.6, the clock interval;
- §11.2, the classification precedence.

**Recommendation: a GPT closure check on R4.2's changes**, using §3 above as its scope. GPT raised the three blockers, so it is best placed to confirm they are closed. **Plus a short Gemini B check of §5.6, §8.1.1 and §11.2.** Gemini B is still unexposed to GPT's review; this document's §2 must not be sent to it.

After both, the founder decides on the Stage A freeze. Then come FD-5, the blind script, and the build.

**Remaining Stage A freeze blockers:** only the closure checks above. **Stage B blockers are unchanged:** OI-10, OI-11, OI-12, OI-15 and OI-17.
