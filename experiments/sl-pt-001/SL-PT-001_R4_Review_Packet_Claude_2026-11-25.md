# SL-PT-001 R4 Review Packet

**Author:** Claude. **Date:** 2026-11-25.
**Responds to:** the founder dispatch "R4 CONSOLIDATION".
**Status:** design documentation only. **NOT FROZEN. NOT IMPLEMENTED. No test EXECUTED.**

**Packet contents:**

| Deliverable | Where |
|---|---|
| **D1** consolidated R4 candidate | `SL-PT-001_R4_Consolidated_Candidate_Claude_2026-11-25.md` (SHA-256 at the end of this packet) |
| **D2** traceability matrix | §1 below |
| **D3** founder decision register | **R4 §1**, held in one place so that the two copies cannot diverge |
| **D4** unresolved issues register | **R4 §16** (OI-01 to OI-14), held in one place for the same reason |
| **D5** self-review | §2 below |
| Recommendation | §3 below |

---

## 1. D2: R3-to-R4 traceability (RC-01 to RC-25)

| RC | Item | R4 section | Incorporated | Status | Remaining dependency |
|---|---|---|---|---|---|
| RC-01 | cash-only ledger; BTC reservation; fee asset and units | §8.2 to §8.6 | typed USD/BTC ledger; fee-asset rules; USD-equivalent L-2 checks for BUY and EXIT | CLOSED IN DRAFT | Stage B only; the fee asset and fill-id field are UNVERIFIED (U-V3) |
| RC-02 | per-fill ceiling underflow | §8.2 | outstanding computed from the cumulative Q_f, floored, ≥ 0 | CLOSED IN DRAFT | — |
| RC-03 | idempotent fill identity; corrections and busts; atomicity | §8.4, §8.5 | fill id applied once; monotone Q_f; DISCREPANCY halt; single-writer ledger events | CLOSED IN DRAFT | the venue fill-id field is UNVERIFIED |
| RC-04 | severity of the reservation defect (GPT Critical vs Gemini Medium/High) | §8 | fixed for both stages; the disagreement stays recorded in the reconciliation | CLOSED IN DRAFT | — |
| RC-05 | revision baseline across failed or missing cycles | §4.9 | bar store folded from the whole chain | CLOSED IN DRAFT | — |
| RC-06 | revision between cycles affecting a pending authorization | §4.9, §9.3 | re-fetch at checkpoints (b) and (c) | CLOSED IN DRAFT | Stage B |
| RC-07 | first-accepted-forever lockout | §4.9 | pending → confirmed on a second identical observation | CLOSED IN DRAFT | "confirmed" is explicitly not finality (U-D4) |
| RC-08 | run end undefined | §10.3, §11.2 | `declared_slots` N ≥ 30; open-ended runs ineligible | CLOSED IN DRAFT | — |
| RC-09 | manifest suppression; invocation log not an audit input | §10.1 to §10.3, §11.3 | push before T_d0; global chain; repository-versus-chain inventory; invocation log audited | CLOSED IN DRAFT | depends on the founder pushing (stated limitation) |
| RC-10 | timer contract | §6.1, §6.2 | Task Scheduler settings; wrapper; slot-anchor validation | CLOSED IN DRAFT | **OI-13** (wrapper confirmation); U-T1 (settings UNVERIFIED) |
| RC-11 | the ceiling crosses the next slot; U16 false | §5.3, §14 U16, U53 | slot-anchored clocks; cutoff with W = 90 s; non-contradiction proof | CLOSED IN DRAFT | — |
| RC-12 | overrun cascade; SKIPPED writer undefined | §6.3, §11.1 | successor writes CYCLE_OVERRUN and takes the token; SKIPPED removed | CLOSED IN DRAFT | the protocol needs review (§2.4) |
| RC-13 | auditor trusts asserted fields | §10.4, §10.5, §11.1, §11.2 | closed TER-1 schema; RFC 8785; string-only numbers; recomputation for every slot | CLOSED IN DRAFT | — |
| RC-14 | FD-6 common mode | §11.5 | founder decision recorded; GPT dissent preserved; hand cross-check specified | CLOSED IN DRAFT (decision recorded) | the residual common mode is UNBOUNDED (U-O4) |
| RC-15 | arithmetic context; rounding points; increments in the policy | §5.1, §7.4 | exact rationals (or Inexact trap); five named rounding points; policy fields | CLOSED IN DRAFT | increment values UNVERIFIED |
| RC-16 | Stage A process-level isolation | §2.3 | Branch H and Branch C both specified | **OPEN** | **OI-06** (founder) |
| RC-17 | CF-6: a missing quote cannot be REJECTED | §4.11, §11.1 | Q1 to Q5; QUOTE_INVALID is non-qualifying; stale-but-present → REJECTED (R4) | CLOSED IN DRAFT | — |
| RC-18 | Stage A clock unbounded; checkpoint instant | §5.3, §5.6 | checkpoint (a) defined; 2 s bound proposed | **OPEN** | **OI-07** (founder) |
| RC-19 | δ_send not bound to a send interval | §9.4 | defined as an enforced bound; NOT_SENT / AMBIGUOUS outcomes | DEFERRED | FD-G18 (Stage B) |
| RC-20 | query parameters unpinned | §4.2 | start, end and limit pinned; `end` semantics UNVERIFIED | CLOSED IN DRAFT | — |
| RC-21 | P-3 overstated | §4.5, §4.13 | the forming-bar claim withdrawn; labelling DOCUMENTED; conservative-rule argument | CLOSED IN DRAFT | — |
| RC-22 | CF-5 test gap | §5.4, §14 U90 | issuance ≤ approval_deadline tested | CLOSED IN DRAFT | — |
| RC-23 | FD-4 incorrectly closed in R3 | §8 | rebuilt; R3's FC-E closure withdrawn | CLOSED IN DRAFT | subject to R4 review |
| RC-24 | CF-7 (stale in GPT's review) | §9.6 | the founder's sequence integrated | CLOSED IN DRAFT | Stage B |
| RC-25 | R8 $300; R12 $450; settle 60 s; opening cash $500 | §7.3, §4.6, §8.1 | carried as CANDIDATE | **OPEN** | **OI-02 to OI-05** (founder) |

**R4-1 to R4-16 representation check:**

| Correction | R4 section |
|---|---|
| R4-1 | §4.9 |
| R4-2 | §6.1, §10 |
| R4-3 | §5.3 |
| R4-4 | §6.3 |
| R4-5 | §10.4, §10.5, §11 |
| R4-6 | §11.5 |
| R4-7 | §8 |
| R4-8 | §5.1, §7.4 |
| R4-9 | §2.3 |
| R4-10 | §4.11 |
| R4-11 | §5.6 |
| R4-12 | §9.4 |
| R4-13 | §4.2 |
| R4-14 | §4.5, §4.13 |
| R4-15 | §14 |
| R4-16 | §1, §4.13, this table |

**All 16 are represented.**

---

## 2. D5: self-review

### 2.1 Source limitations

- **The repository could not be inspected.** Claude's attempt to attach it was denied.
- **Committed founder decision record:** R4 §1 uses the text Claude gave for commit. The committed blob is **not verified** (OI-01).
- **The reconciliation commit:** the push that included it **was not confirmed to Claude**. The last push attempt stopped on a hash mismatch for the recovery document, and no later push output was supplied. The dispatch says the reconciliation is committed. Claude takes that as the founder's statement, not as evidence.
- Everything else comes from Claude's local copies, which match the blobs the founder listed at `0cf59f5`.

### 2.2 Interpretations beyond the source record (each needs review or founder confirmation)

| # | Interpretation | Where | Why |
|---|---|---|---|
| I-1 | a **wrapper** does the invocation logging | §6.1 (OI-13) | Task Scheduler writes no per-invocation log suitable for audit. The founder's "invoke and log only" is read as including a minimal logger |
| I-2 | **SKIPPED removed;** CONCURRENT_INVOCATION reclassified as an anomaly record that **disqualifies** its slot | §6.3, §11.1, §11.2 | the conservative reading of R1's reset rule. A refused duplicate does not alter the decision, but it signals a scheduler fault |
| I-3 | a bar's **first** observation is CONFIRMED immediately; only **changes** need a second observation | §4.9 | otherwise every new bar would need two fetches, delaying every decision by a slot |
| I-4 | Stage B re-fetches bars at (b) and (c), not (d) | §9.3 | at (d) only δ_send remains |
| I-5 | the Stage A offset estimate comes from the HTTP `Date` header | §5.6 | carried from R3 as CANDIDATE |
| I-6 | a BTC fee is valued at the fill price, and the L-2 fee checks use the formulas in §8.4 | §8.4 | an accounting convention, not a venue fact |
| I-7 | **every numeric TER value is a JSON string** | §10.4 | RFC 8785 serializes numbers as IEEE doubles, which would break exactness |
| I-8 | injections: not within 30 s of a T_d, aborted by a slot invocation | §6.5 | the 30 s figure is a Claude choice |
| I-9 | the T_d grid is tied to the settle value | §6.2 | R3 hard-coded 60 s. With settle still CANDIDATE, the grid must follow it |
| I-10 | U5 and U16 restated | §14.1 | U5 now uses a late invocation within a slot; U16 states the corrected bound |
| I-11 | shadow fills are **not** simulated | §8.1 (OI-08) | simulating them would invent venue behaviour. The consequence is reduced live coverage |

### 2.3 Source inconsistencies found and resolved in R4

- R3 §9.2 (CF-6): the missing-quote error. Fixed in §4.11.
- R3 §3.4: the overstated P-3 label. Fixed in §4.5 and §4.13.
- R3's hard-coded 60 s in the slot grid. Fixed in §6.2.
- R3's V12 ordering: pre-flight was listed last but runs first. Fixed in §4.7.
- R3's missing replay case: a second invocation after a slot completes. Fixed in §6.3.
- R3's L-2 "booked fee greater than reserved fee" check was unit-ambiguous. Replaced by exact formulas in §8.4.
- RC-07: Gemini's first-accepted-forever store versus the anti-lockout requirement. Resolved in §4.9.

### 2.4 Parts that remain internally ambiguous or risky

- **The lock and takeover protocol (§6.3).** It is specified at the level of an append lock plus a token. Whether OS file locking on Windows gives the exclusivity the text assumes is **UNVERIFIED**. "Termination request" for the old process is recorded but not enforced; only the append refusal is enforced.
- **The founder-push dependency (§10.3, §11.3).** Completeness relies on the founder pushing at RUN_OPEN and RUN_CLOSE. An unpushed chain is unauditable.
- **Stage A covers the long-position branches only through tests** (OI-08).
- **Branch H feasibility** (OI-06).
- **The venue fill-id field and fee reporting** (U-V3). §8.4's rules hold only if the venue reports fills that way.

### 2.5 Should return to independent review (priority order)

1. **§8, the ledger:** it was the most heavily rewritten part, and it is the exposure-limit mechanism.
2. **§6.3 with §10 and §11:** the lock, chain, manifest and audit model as one system (the dispatch's R4-2, R4-4 and R4-5 interaction).
3. **§4.9, the revision store:** confirmation semantics and the anti-lockout argument.
4. **§5.3, the timing proof:** check the DERIVED invariants.
5. **The interpretations in §2.2.**
6. **The areas reviewed only by GPT in R3** (R4 §17). Gemini B did not see them, and they are now restated inside R4.

**Reviewer independence:**
- **Gemini account B** has not seen R4, the reconciliation or GPT's review. It is the clean reviewer for R4.
- **GPT** has seen everything up to the reconciliation.
- Any new Claude self-findings on R4 should be sealed **to the founder only** before review (process rule RI-02).

---

## 3. Recommendation

**READY FOR INDEPENDENT HOSTILE REVIEW**

**Why:**
- All 25 reconciliation items have a disposition (§1). All 16 corrections are integrated into the specification itself, not appended. The recorded founder decisions are carried forward unchanged, and GPT's FD-6 dissent is preserved.
- Every open founder item is visible in R4 §1.2 and §16: RC-25 (OI-02 to OI-05), R4-9 (OI-06), R4-11 (OI-07), coverage (OI-09) and the wrapper (OI-13). Every test is labelled DESIGNED, and no evidence status is upgraded.
- The probe's labelling claim is withdrawn (§4.5, §4.13).
- Every test the text references is in the inventory; the one exception, U49, is recorded as subsumed by U30.

**Open items don't block the review.** They block the **freeze**, as R4 §16 states: OI-01 to OI-07, OI-09 and OI-13. A reviewer can assess R4 with them open, and should check that each open item is treated consistently wherever it appears.

**One item should be settled first: OI-01.** Confirm that the committed decision record matches R4 §1.1, so that reviewers don't review against a misstated decision.

**What this recommendation does not say:**
- It does not say R4 is correct.
- It does not say R4 is freeze-ready.
- It does not say anything should be built.

**Hashes:** computed when the files were delivered.

| File | SHA-256 | Git blob (local) |
|---|---|---|
| SL-PT-001_R4_Consolidated_Candidate_Claude_2026-11-25.md | `d4535df8a404dcc318b4cd10167ba6d942dc66f4307ab428b6a4fd7537fa2ddd` | `38b1de639a7ecea842269f8f48a2638363cb4871` |
