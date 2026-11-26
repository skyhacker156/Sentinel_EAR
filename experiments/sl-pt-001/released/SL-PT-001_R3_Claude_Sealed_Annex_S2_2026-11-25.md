# SL-PT-001 R3: Claude sealed annex S2 (FOUNDER ONLY)

**Author:** Claude. **Created:** 2026-11-26T03:5xZ (2026-11-25 local), after the SF-1 to SF-3 disclosure and before either standalone R3 review was delivered.

**Distribution rule:**
- Founder only. **Do not paste, forward or summarize this to GPT or Gemini until both standalone reviews are delivered.**
- Record only its SHA-256, now, in a commit message or commitments file.

**Purpose:** to restore a valid commit-before-reveal sensitivity check on two R3 defects that neither reviewer has seen. R3 is not edited.

| ID | R3 section | Defect (failure mechanism) | Consequence | Proposed R4 correction |
|---|---|---|---|---|
| S2-1 | §3.4 ("forming bar … OBSERVED, P-3"); probe report P-3 | The probe cannot distinguish start-labelled from end-labelled bars. A bar `t = 03:10Z` returned at 03:13:20Z is **forming** if start-labelled (it covers 03:10 to 03:15) but **complete** if end-labelled (it covers 03:05 to 03:10). Nothing in a single response separates the two. The "forming bar OBSERVED" claim is therefore DOCUMENTED-conditional, not OBSERVED | an overstated label on a data-contract fact. **Safety direction:** if bars are actually end-labelled, the rule t + 360 s ≤ T_d discards one complete bar. The signal then lags one bar, but there is no look-ahead (conservative). **No unsafe direction exists** under either labelling, *provided* V7 and the completed-candle rule use the same convention (they do) | relabel P-3 and R3 §3.4 as DOCUMENTED, with the probe **consistent with** start-labelling. Settle it by evidence: (a) a re-fetch of the same `t` after its window closes, showing changed o/h/l/c/v/n (start-labelled and forming); or (b) Stage A's own revision records for the latest bar. Add test U-S2-1: under an end-labelled fixture, the harness is conservative and never uses a bar before its window closes |
| S2-2 | §6.6, fill row | On each partial fill the reservation is reduced by ceil to the cent of q_f × L × (1 + f_res). The sum of per-fill ceilings can **exceed** R, by up to (number of fills − 1) cents. The reservation then underflows, or the last fill's reduction is undefined | premature or negative release; an exact-arithmetic and reservation defect (challenges C4 and C5) | the reservation outstanding after fills F₁…F_k := R − floor to the cent of (Σq_f × L × (1 + f_res)), never below 0 while the order is open. It is computed from the **cumulative** filled quantity, not by per-fill decrements. Test U-S2-2: three partial fills whose per-fill ceilings sum to R + 2¢ → outstanding ≥ 0 and consistent; full fill → outstanding = R − floor to the cent of (q × L × (1 + f_res)), released at terminal |
