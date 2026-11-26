# SL-PT-001 R3: Claude self-findings (SEALED until both reviews are delivered)

**Author:** Claude. **Date:** 2026-11-25.
**Purpose:** a commit-before-reveal record of the defects Claude found in its own R3 (blob `203b4bf5…`) after delivering it and before the GPT and Gemini reviews.
- **Do not forward this note to GPT or Gemini until both reviews are delivered.**
- At reconciliation it shows which defects the reviewers found independently. A defect neither review finds is evidence about review sensitivity, not proof that R3 is sound.
- R3 is **not** edited, because the review target must stay fixed.

| ID | Section | Defect (failure mechanism) | Consequence | Smallest correction (proposed for R4) |
|---|---|---|---|---|
| SF-1 | R3 §3.7 / V11 | The revision check compares against "the previous cycle's accepted window". If the previous slot produced no accepted window (NO_DECISION, MISSING, SKIPPED, overrun, or the first slot of a run), the baseline is undefined | A bar revised between cycle i and cycle i+2 escapes detection whenever cycle i+1 failed. This is dispatch challenge C7 | compare against the **most recent accepted window** recorded, whatever its slot. For the first cycle of a run, record "no baseline" explicitly (the TER field `revision_baseline_cycle_id`) |
| SF-2 | R3 §9.3 items 1 and 2 | The slot ledger is bounded by "the run's declared end", but the run-manifest field list (item 1) contains **no end field** | the denominator is undefined at the tail. A harness or timer that stops early can truncate a run without producing MISSING slots. This is challenge C3 (selective omission) | add `declared_end` (a slot count N, or an end instant) to the manifest; every slot up to it is judged; ending early produces MISSING slots up to declared_end; an open-ended run is not allowed |
| SF-3 | R3 §4.2, §4.3, §5.2 | The ceiling is created + 180 s, and created can be as late as T_d(i+1) − ε, because any invocation inside the slot is valid (§5.2) | a late cycle that makes a proposal has ceiling > T_d(i+1). In Stage A, SHADOW_EXPIRED then lands after the next decision instant, which forces CYCLE_OVERRUN. In Stage B, expires_at can exceed T_d(i+1), breaking R1 §1 rule 4 ("before the next decision instant") and the U16 claim. This is challenge C1 (timer drift) | ceiling := min(created + 180 s, T_d(i) + 180 s). Equivalently: no proposal is created once created > T_d(i) + 180 s − (the time needed); record it as REJECTED (R13) |

**Not a defect, recorded for completeness:**
- The blob SHA the founder cited for R3 (`203b4bf5d0d5f2cba124a0ea693b796ecd38c7bd`) equals Claude's local `git hash-object`. That is consistent with a byte-identical commit. It is still CONDITIONAL until the `git ls-tree` output is returned.
