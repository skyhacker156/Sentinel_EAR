# SL-PT-001 Stage B founder decision batch (DRAFT for founder action)

**Prepared by:** Claude, 2026-11-26 | **Feeds:** R5-B0 `[PENDING]` markers; Strike 7 §7
**Status:** NOT DECIDED. Each item is the founder's decision. Claude's recommendation is shown; GPT's and Gemini B's positions are added when received.
**Gate rules:**
- Deciding these items **authorizes nothing to be built or run.** Building needs FD-9 at the Stage B freeze.
- **D-9 is the one exception.** It is an authorization by its nature (paper keys for read-only calls), so it is listed separately and may be deferred until after M1.
- Nothing here changes Stage A.

**How to decide:** for each item, write the chosen option letter in the "Founder" column, or "DEFER". Commit the completed record as `SL-PT-001_Founder_Decision_Record_v6_<date>.txt` after the Stage A run closes.

---

## Part 1. Specification decisions (no authority granted)

| ID | Question | Options | Claude | Why | Founder |
|---|---|---|---|---|---|
| **D-1** (FD-G16) | After an ambiguous send, may the system resubmit? | **a** never; query by the original COID only · **b** resubmit with the same COID only if broker deduplication is independently established · **c** the founder decides each case | **a** | GPT recommended (a) in the G-07 review; zero duplicate-order risk; costs at most a lost attempt | |
| **D-2** (FD-G17) | Which reconciliation path does not depend on the executor? | **a** through the executor only (no independence) · **b** a second trade-capable key (violates G7-I8) · **c** founder checks the Alpaca dashboard order history after each terminal order and at session close · **d** broker confirmation emails (UNVERIFIED for crypto paper) | **c** now; **d** optional later | c works today with no new authority; d is unverified; b adds an unmediated authority | |
| **D-3** (FD-G18) | Send bound δ_send, and the clock-skew treatment | **a** δ_send = 10 s; σ = 0 because both processes are on one host and one clock (void if split) · **b** a different δ_send (state a value strictly between 0 and 60 s) | **a** | one HTTPS POST needs far less than 10 s; single-host σ = 0 is true by construction | |
| **D-4** (FD-G4) | What happens if the audit store fails? | **a** the local chain with fsync is the write-ahead log; no send without it; push after each terminal state · **b** an external acknowledgement before every send · **c** local plus asynchronous external with bounded lag | **a** | it reuses the Stage A chain discipline; b adds a network dependency to every order | |
| **D-5** | What must the founder see before approving? | **a** the harness proposal summary (signal, q, L, R, all rule results, quote age, countdown); independent reconstruction **after** the terminal state · **b** an independent recomputation **before** approval, inside the ~90 s window | **a** | b does not fit in the window (U-O1); the milestone requires the after-the-fact reconstruction anyway | |
| **D-6** | How are proposals put in front of the founder? | **a** attended sessions only: local alert, countdown, typed approval; unattended proposals expire harmlessly · **b** add a remote or mobile channel | **a** | b is expansion with its own authentication problem; a is enough for one order | |
| **D-7** (OI-15) | Who independently reconstructs the order lifecycle (L-4)? | **a** GPT writes a blind Stage B auditor (FD-6 custody pattern); Gemini B reviews it · **b** GPT alone · **c** Gemini B writes it · **d** founder by hand only | **a** | reuses the custody tooling; Gemini's review answers GPT's own common-mode dissent on FD-6 | |
| **D-8** | Which chain does Stage B write to? | **a** the existing chain · **b** a new Stage B chain with its own GENESIS | **b** | keeps the Stage A record and its auditor's population rules untouched; avoids touching frozen §10.1 and §11.1 | |
| **FD-G19** (new) | How is the approver authenticated? | **a** interactive presence: approval in the founder's console, typing the first 12 characters of the proposal hash; recorded as "not cryptographically authenticated" · **b** a signature with a founder-held key, verified by the decision process | **a** | b's key sits on the same machine, so it adds a secret without beating host compromise (G7-A1) | |
| **FD-G13** | Proceed to Stage B knowing G7-I8 (and G7-I5) do not hold on this machine? | **a** yes, with the §9.8 claim language verbatim · **b** no; first build an isolated deployment | **a** | b is a different, much larger project; the claim language already discloses the gap | |
| **OI-08** (Stage A exit) | Accept that Stage A never exercised the long-position branches, R8 or R12 on live data? | **a** accept as a disclosed limitation (covered by unit tests and injections) · **b** require more Stage A evidence | **a** (decide at the Stage A exit) | shadow fills are prohibited by design, so live data cannot exercise them | |

**Decided after the pre-flight (not now):** OI-10 TIF.
- **a IOC:** if the observed price increment puts the BUY limit at essentially the ask.
- **b GTC + governed cancel by T_d + 180 s:** if the limit sits materially below the ask.

## Part 2. Authorizations (each grants authority; decide separately)

| ID | Authority | Bound | Claude | Founder |
|---|---|---|---|---|
| **FD-8** | paper-key custody | keys only in the executor's process environment, never in the decision process or any committed file; storage method chosen by the founder | needed before D-9 | |
| **D-9** | read-only keyed pre-flight before Stage B authorization | exactly five GET calls (account, positions, orders, BTC/USD asset, one never-used COID); submit and cancel routes refused before I/O; raw responses committed | **after M1**, so the M1 gate holds | |
| FD-9 | Stage B build | at the Stage B freeze | not now | |
| P23 | the first order | at the end | not now | |

---

## What changes when this is decided

- R5-B0's `[PENDING]` markers are replaced by the decided text.
- The draft becomes a **closure-round packet** for GPT and Gemini B.
- After M1 passes, the remaining path is: D-9 → pre-flight → OI-10 → Stage B freeze.

*Draft. Not a decision record.*
