# SL-PT-001 R4.2a: consolidated specification candidate (Stage A review version)

**Author:** Claude (Specification Lead / ARBITER). **Date:** 2026-11-25.
**Responds to:** the R4.2 closure checks (GPT, findings G3-01 to G3-05; Gemini account B, findings B3-01 to B3-05) and their reconciliation (2026-11-26). R4.2 responded to the R4.1 reviews.
**Base:** R4.2 (blob `f87ad21f4c70f558335070b843cb270e026005d2`), corrected per the R4.2 closure reconciliation. R4.2 was R4.1 (blob `a653252a8b184f0e184c7f2b42b4dbba6ff49d3f`, commit `0a4ddaf…` as reported by the founder) corrected per the R4.1 review reconciliation. R4.1 was itself R4 (blob `38b1de639a7ecea842269f8f48a2638363cb4871`) synchronized with founder decision record v1 (blob `eb76d8a2…`) and **v2** (blob `801f7a57f5a87220a44f0bbc3e262e2704fdf77b`). Changes from R4 to R4.1 are listed in the R4.1 review packet; from R4.1 to R4.2 in the R4.1 review reconciliation; from R4.2 to R4.2a in the R4.2 closure reconciliation.
**Classification:** design documentation only.
- **CANDIDATE. NOT FROZEN. NOT IMPLEMENTED. NOT VERIFIED.**
- No test has been executed.
- No implementation, credential, trading-host connection or order is authorized by this document.

**What R4 is:** one complete specification for SL-PT-001.
- It integrates R3 (blob `203b4bf5…`), the R3 review reconciliation (corrections R4-1 to R4-16), the founder decision record and the probe evidence.
- A reader needs no other SL-PT-001 document to follow the system.
- **R4.2a replaces R4.2**, which replaced R4.1 and R4. All remain in the repository as history.
- Earlier documents are **history**, not specification.
- **G-07 Draft 0.3** (blob `1cdbd7d3…`) still defines the execution-boundary components and terms used in §9 (K3, K5, LP-CONSUME, LP-WAL, LP-PRESEND, invariants G7-I1 to I10). R4 changes G-07 only by the approval predicate A0.3-13, stated in full in §9.2.

**Labels** (every material claim carries one):

| Label | Meaning |
|---|---|
| DERIVED | follows logically from stated rules |
| COMPUTED | arithmetic on recorded data |
| DOCUMENTED | stated by a vendor's documentation |
| OBSERVED | seen in recorded evidence |
| ASSUMED | taken as true without evidence |
| CONDITIONAL | holds only if a named condition holds |
| UNVERIFIED | not established |
| UNBOUNDED | no limit can be stated |
| DESIGNED | a test or control that is specified but not executed |
| EXECUTED | run, with retained evidence. **No item in R4 has this label** |
| CANDIDATE | proposed, with no founder decision covering it |

**Model agreement is not verification.**

---

## 0. Mission endpoint and freeze map

### 0.1 Mission endpoint (founder decision record v2)

The SL-PT-001 milestone is **one governed BUY** with:
- at least one confirmed fill;
- a terminal order status;
- complete reservation and fill reconciliation, L-1 to L-3 (§12);
- independent reconstruction of the order lifecycle;
- the remaining BTC exposure recorded: quantity held, cost basis, and value at the bid.

**This is not a round trip.** A governed EXIT is outside this milestone. A BUY that reaches a terminal state with zero fills does not meet the milestone; the next BUY signal is a new attempt, and the wait for it is UNBOUNDED (§15 U-O3).

### 0.2 Freeze map (FD-5 as clarified in v2)

| Scope | Sections | Frozen at | Gates |
|---|---|---|---|
| **Stage A** | §2 to §7, §8.1, §10, §11, §13; tests in §14 whose Stage column contains "A"; the Stage A rows of §15 and §16 (marked **A**). This is exactly the list in decision record v2 | the **Stage A freeze**: a committed record naming one R4.x blob and these sections | **FD-5** (harness build) |
| **Stage B (DRAFT)** | §8.2 to §8.6, §9, §12; tests in §14 whose Stage column is "B" only; the Stage B rows of §15 and §16 (marked **B**) | the **Stage B freeze**, later | **FD-9**, together with the Stage A exit |
| Records | §0, §1 and §17. §0 and §1 restate committed founder decisions; the decision records themselves govern | not frozen | — |

**Rules (founder decision record v2):**
- Findings that affect only Stage B sections or Stage B tests **do not block FD-5**. They must be resolved, or accepted in writing, at the Stage B freeze.
- A Stage B change that touches any Stage A section requires a **new Stage A freeze**. Evidence produced earlier stays tied to its original specification hash.
- **Stage B sections in this document are DRAFT.** They are present for continuity and are **not part of the Stage A freeze decision.**

---

## 1. Founder decision register (deliverable D3)

**Sources (blob-verified):**
- v1 `experiments/sl-pt-001/SL-PT-001_Founder_Decision_Record_2026-11-25.txt`, blob `eb76d8a21521ad02e2c5530bf3bc30cafe583169`;
- v2 `experiments/sl-pt-001/SL-PT-001_Founder_Decision_Record_v2_2026-11-25.txt`, blob `801f7a57f5a87220a44f0bbc3e262e2704fdf77b`.

Each blob was reproduced byte-exactly by Claude from the decision text, using the founder's `git ls-tree` and `Get-Content` output. Claude did not read the repository directly.

### 1.1 Recorded founder decisions (carried forward; not reopened)

| ID | Decision | Where in R4 |
|---|---|---|
| Baseline | SMA-20/50; BTC/USD only; 5-minute candles; Alpaca paper as the eventual Stage B venue; limit orders only; no leverage, shorting or derivatives | §3 |
| FD-1 | the Stage A-0 data probe: **EXERCISED** (2026-11-26T03:13Z) | §4.13 |
| FD-2 | literal crossover: BUY iff D(k−1) ≤ 0 ∧ D(k) > 0; EXIT iff D(k−1) ≥ 0 ∧ D(k) < 0; equality is never a crossover | §3.2 |
| FD-3 | no new proposal while any order, partial fill, unresolved authorization or ambiguous prior order remains open → NO_ACTION / BLOCKED_OPEN_ORDER | §7.3 R16 |
| FD-4 | $150 maximum total reserved spend **including fees**; quantity rounds **down** to the verified venue increment; a fresh quote is required at authorization issuance; **no repricing after approval**; displayed top-of-book size is informational, not a cap; partial fills must be explicitly accepted and documented; increments and fees stay UNVERIFIED until checked at the venue | §7, §8 |
| CF-1 | limit price and quantity are derived **at proposal** and bound by approval; the issuance quote **validates only**; no repricing or resizing after approval; a validation failure kills the authorization | §7.2, §9.3 |
| CF-2 | BUY while long → NO_ACTION; EXIT while flat → NO_ACTION | §3.3 |
| FD-6 | **GPT** writes the blind reconstruction script **after the freeze**, from the frozen set only; the script hash is recorded before any TER exposure; the founder runs it on five pre-seeded random cycles; differences are findings. **The same script performs the slot audit** (§11), and the founder performs a **hand cross-check of one manifest** | §11.5 |
| FD-6 dissent | **GPT dissents** (R3 review §4: "one blind script performing both reconstruction and slot audit creates common-mode risk"). This is preserved; the decision is **not** unanimous technical agreement | §11.5 |
| FD-7 | **Windows Task Scheduler**, invoke and log only. No catch-up; no retry; overlapping launches are permitted at the scheduler and refused by the harness lock; the same cycle never executes twice; the machine stays awake; the task XML and invocation log are preserved and hashed | §6.1 |
| W | minimum remaining approval window **90 s**, applied in Stage A and Stage B. Stage B feasibility UNVERIFIED | §5.3 |
| CF-7 | the first order is the first governed order; a read-only not-found COID query happens in pre-flight; the duplicate-COID test needs separate authorization | §9.6 |
| FD-5 | the Stage A harness build: **CONDITIONAL**, not authorized. **Clarified (v2):** its "specification freeze" is the **Stage A freeze** (§0.2) | §0.2, §16 |
| MISSION | endpoint: one governed BUY (v2) | §0.1 |
| RC-25a | R8 portfolio cap **$300.00**: accepted (v2) | §7.3 |
| RC-25b | R12 **$450.00**: accepted (v2), as a **buy gate, not a loss limit** | §7.3 |
| RC-25c | settle **60 s**: accepted (v2) | §4.6 |
| RC-25d | opening shadow cash **$500.00**: accepted (v2) | §8.1 |
| R4-9 | Stage A isolation: **Branch C (client level only)** accepted (v2); host firewall not required | §2.3 |
| R4-11 | Stage A clock bound **\|offset_estimate\| ≤ 2 s**, otherwise BOUNDARY_FAIL: accepted (v2) | §5.6 |
| OI-13 | the FD-7 wrapper is the "log" part of "invoke and log only"; it has no other logic (v2) | §6.1 |
| OI-09 | A | coverage of §2, §13 and the claim limits | — | — | — | **CLOSED:** Gemini B reviewed them in the R4.1 Stage A review (its attack area A) |
| FD-8 | paper-key custody: **DEFERRED** | §16 |
| FD-9 | Stage B (FD-G13, FD-G16, FD-G17, FD-G18): **DEFERRED** | §9 |

### 1.2 Pending founder decisions (open; R4 does not decide them)

| ID | Item | Scope | R4.1 treatment |
|---|---|---|---|
| FD-4 TIF | GTC with a Sentinel cancel, or IOC | **B** | DEFERRED to the Stage B package (§9.5) |
| FD-G13, FD-G16, FD-G17, FD-G18 | Stage B controls | **B** | DEFERRED (FD-9) |
| FD-8 | paper-key custody | **B** | DEFERRED |
| Stage B reconstruction | who independently reconstructs the BUY lifecycle (FD-6 covers Stage A cycles only) | **B** | open (§16 OI-15) |

**No Stage A founder decision is pending.**

---

## 2. Scope and stage boundary

### 2.1 Stages

| Stage | What it is | Status |
|---|---|---|
| **A** (shadow) | keyless, read-only market data; the full decision and policy pipeline; shadow proposals only; no orders, no credentials | specified here; **not built** (FD-5) |
| **B** (paper) | governed paper orders through G-07 controls | rules specified here **for review only**; DEFERRED (FD-9) |
| **C** | corrections, busts, duplicate-COID tests | out of scope |

### 2.2 Stage A properties (normative)

- **No credential (checked scope only):** no broker credential is supplied to the harness process through the **two sources the pre-flight checks**: the process environment variables and the harness configuration file (V12a). **Credentials held in other stores the process could read (user credential stores, other files, local agents) are not excluded** (UNVERIFIED; §15 U-I2).
- **Allowlisted hosts:** the harness HTTP client contacts only `data.alpaca.markets`. Requests to any other host are refused before network I/O.
- **No submit capability:** Stage A has no code path that submits, cancels or queries orders.
- **Claim limit:** Stage A results never establish any G-07 property (G7-I1 to I10).

### 2.3 Network isolation boundary (R4-9; **Branch C selected**, founder decision record v2)

**Branch C applies.** Branch H is retained below for the record only. It is **not selected, not required and not part of Stage A.**

**Branch H (host-level; NOT SELECTED):**
- a host firewall outbound rule for the harness process allows only the market-data host;
- at each RUN_OPEN, the harness attempts a TCP connection to the trading host; it must be **refused by the host firewall**, which is recorded (test U92);
- feasibility on the founder's machine (hostname versus IP-based rules, DNS changes) is **UNVERIFIED**.

**Branch C (client-level only; SELECTED):**
- isolation is enforced only by the harness's own HTTP allowlist and the absence of credentials;
- **every Stage A result carries this limitation, verbatim:** *"Disconnection from trading is asserted at the HTTP-client level only. Alternate egress paths in the process or host (other libraries, raw sockets, proxies, inherited handles) were not excluded."*
- **Consequence:** Stage A shows that the intended code path is read-only. It does **not** show that the process could not reach a trading host. No Stage A result may claim process-level or host-level isolation.
- *Why this is acceptable for Stage A (DERIVED, within the checked scope):* the harness is given no broker credential through the sources V12a checks, and has no submit code path (§2.2). An unexcluded egress path would therefore need both an unchecked credential source and code that Stage A does not contain. This is an argument about the harness as specified, not a guarantee about the host. Isolation is a claim Stage A does not need to make.

---

## 3. Strategy (normative)

### 3.1 Indicators

- **Input:** k is the newest completed candle; close_i is the exact decimal close of candle i (§4.3).
- **Sums:** S20(k) = Σ close_i for i = k−19 … k, and S50(k) = Σ close_i for i = k−49 … k.
- **D(k)** = 5·S20(k) − 2·S50(k). sign(D(k)) = sign(SMA20(k) − SMA50(k)), **DERIVED**: SMA20 − SMA50 = S20/20 − S50/50 = D/100.
- **History:** 51 consecutive completed candles (k−50 … k) are required.

### 3.2 Crossover (FD-2)

| Signal | Condition |
|---|---|
| BUY | D(k−1) ≤ 0 ∧ D(k) > 0 |
| EXIT | D(k−1) ≥ 0 ∧ D(k) < 0 |
| HOLD | otherwise, including D(k) = 0 |

The three are mutually exclusive and exhaustive (DERIVED).

**Edge cases (DERIVED; tests U4a to U4e):**

| ID | D sequence | Result | Note |
|---|---|---|---|
| EC-1 | + → 0 → + | BUY at the third step | accepted consequence of the literal rule |
| EC-2 | − → 0 → − | EXIT at the third step | accepted consequence of the literal rule |
| EC-3 | − → 0 → + | BUY at the third step | — |
| EC-4 | 0 → 0 | HOLD | — |

Missing history is a data failure (§4.7), never HOLD.

### 3.3 Signal-to-action mapping

| Signal | Position | Result |
|---|---|---|
| any | an open, partial, AMBIGUOUS or unresolved order or authorization exists | NO_ACTION / BLOCKED_OPEN_ORDER (FD-3) |
| BUY | flat | proposal (§7) |
| BUY | long | NO_ACTION (CF-2) |
| EXIT | long | proposal (§7) |
| EXIT | flat | NO_ACTION (CF-2) |
| HOLD | any | HOLD |

- **Flat** := held BTC < min_order_size. The value is from the policy file (§7.4) and is UNVERIFIED at the venue.
- **Stage A consequence (DERIVED):** the shadow ledger never acquires BTC (§8.1), so in Stage A the position is always flat. On live data, EXIT always maps to NO_ACTION and BUY always produces a proposal. The long-position branches (EXIT proposal, R9, R15, BUY while long) are exercised **only by unit tests and injections** in Stage A (§16, OI-08).

### 3.4 Quote independence

- The signal is a pure function of completed closes. **No quote field enters S20, S50, D or the signal** (U18).
- Quotes are used only in proposal construction and policy (§7).

---

## 4. Data contract (normative)

### 4.1 Source

- Two keyless GETs per cycle to `data.alpaca.markets`, `/v1beta3/crypto/us/`. The single-source limitation stands: no second source cross-checks the data.
- Keyless access is **OBSERVED** in one probe (§4.13).

### 4.2 Pinned requests (R4-13)

| Request | Parameters |
|---|---|
| bars | `symbols=BTC/USD`, `timeframe=5Min`, `start = t_exp − 59 × 300 s`, `end = T_d` (RFC-3339 UTC, second precision), `limit=1000` |
| quote | `latest/quotes?symbols=BTC/USD` |

- The exact meaning of `end` (inclusive or exclusive; whether it applies to bar start) is **UNVERIFIED**. The rules are written so any reading is handled: extra bars are excluded by §4.6, missing bars fail V7 or V8, and further pages are handled by V2.
- The request URLs, send instants and receipt instants are recorded.

### 4.3 Raw artifacts and exact values

1. Raw response bytes and headers are stored **before** parsing, under their SHA-256 (artifact ownership: §10.2).
2. Every numeric value is converted to an exact value (§5.1) from its **original JSON number token text**. No binary floating-point value exists anywhere in the decision, sizing, policy, ledger or audit paths, in the harness or in the reconstructor.
3. Exponent forms are valid. Non-finite or non-numeric tokens where a number is required are malformed (§4.10).
4. For each bar, the token text of o, h, l, c, v, vw and n is kept in the TER (§10.4).

### 4.4 Timestamps

- Every instant is an **integer number of nanoseconds since the Unix epoch, UTC** (written "ns" below). Conversion from RFC-3339 is exact.
- Up to 9 fractional digits are kept; the quote `t` is OBSERVED to carry 9.
- A missing zone designator, more than 9 fractional digits, or a parse failure → malformed (§4.10).

### 4.5 Bar labelling (R4-14)

- **DOCUMENTED:** Alpaca bars are labelled by their **start** time.
- **The probe does not establish this.** A bar with `t` = 03:10:00Z returned at 03:13:20Z is forming under start-labelling and complete under end-labelling; one response cannot tell these apart.
- The completed-candle rule (§4.6) is **conservative under either labelling:**
  - under end-labelling it discards one complete bar, so the signal lags one bar;
  - it never uses a bar before its interval has closed (DERIVED; test U89).
- **Evidence that would settle it:** a later re-fetch showing the latest bar's values changed after the response. Stage A's revision records (§4.9) provide this.

### 4.6 Completed candles

- **T_d(i)** = the slot decision instant (§6.2).
- **Settle** = 60 s (accepted, RC-25c).
- A bar with start t is **completed** iff t + 300 s + settle ≤ T_d.
- Every other bar is **excluded**. It is recorded with its token text and never used.
- **Expected newest completed bar:** t_exp = floor₃₀₀ₛ(T_d − settle) − 300 s. With settle = 60 s this equals T_d − 360 s (DERIVED, since T_d − 60 s lies on a 300 s boundary; §6.2).

### 4.7 Validation set V (all must pass)

| ID | Check | Failure → NO_DECISION sub-reason |
|---|---|---|
| V1 | HTTP 200; well-formed JSON; required fields present (bars: t, o, h, l, c, v, n, vw; response: next_page_token); **the response's symbol key is exactly `BTC/USD`** for both bars and quote, with no other symbol present (U95) | FETCH_FAILED / INCOMPLETE_RESPONSE |
| V2 | `next_page_token` null, or every page fetched and concatenated | INCOMPLETE_RESPONSE |
| V3 | every `t` parses (§4.4) and lies on a 300 s boundary | MALFORMED_VALUE |
| V4 | `t` unique within the response. Byte-identical duplicates collapse with a note; differing duplicates fail | DATA_CONFLICT |
| V5 | arrival order recorded; bars sorted ascending by t | — (never fails) |
| V6 | non-completed bars excluded (§4.6) | — (never fails) |
| V7 | the newest completed bar has t = t_exp | STALE_SERIES |
| V8 | every 300 s step in [t_exp − 250 min, t_exp] has a bar (51 bars) | DATA_GAP |
| V9 | numeric validity: finite; o, h, l, c, vw > 0; v ≥ 0; n ≥ 0 and an integer | MALFORMED_VALUE |
| V10 | at least 51 completed candles | INSUFFICIENT_HISTORY |
| V11 | no **pending** revision (§4.9) for any bar in the 51-bar window | SOURCE_REVISION |
| V12a | pre-fetch boundary check (§6.4 step 1): credential sources and allowlist | BOUNDARY_FAIL, a separate terminal state |
| V12b | clock check (§5.6), evaluated on the bars response **immediately after it is received and before V1** | BOUNDARY_FAIL |

- **V12a runs first, before any fetch.** Its failure → BOUNDARY_FAIL, and no fetch happens.
- **V12b runs on the bars response, before any data from it is used.** Its failure → BOUNDARY_FAIL; the response is stored as an artifact but not validated or used. *(This corrects R4.1, where the clock check was placed before the fetch that supplies it: GPT G-02.)*
- V1 to V11 are then evaluated, and **all failures are recorded**.
- The NO_DECISION sub-reason is the **first** failing check, in the order listed.
- The quote is not in V (see §4.11).

### 4.8 Zero-volume bars

- **zero_volume ⇔ the exact value of v = 0.** This covers `0`, `0.0`, `0e0` and `-0`. Text matching is not used.
- Zero-volume bars are DOCUMENTED as quote-derived. They are **retained in the signal window** and flagged with their token text. They are never filtered or interpolated.
- Changing this changes the strategy and is a founder decision.

### 4.9 Revision handling (R4-1)

**Bar store.** The bar store maps (instrument, t) to the **current accepted** token tuple (o, h, l, c, v, vw, n), its state and its **observation count**.

**States:** BASELINED (accepted on first observation; observed once), PENDING (a changed tuple seen once, not yet accepted), CONFIRMED (a changed tuple accepted after being observed again unchanged). Both BASELINED and CONFIRMED are **accepted** states usable as signal input.
- It is **not a separate mutable file.** It is the deterministic fold of every CYCLE record in the global chain (§10), across all cycles and runs.
- Any reviewer can rebuild it from the chain.

**Per cycle, for every completed bar fetched:**

| Situation | Action |
|---|---|
| t not in the store | add it as **BASELINED** (observation count 1) |
| tuple equals the store's | observation count + 1; state unchanged |
| tuple differs from the store's, and no change is pending for t | record a SOURCE_REVISION event (old and new tuples, both kept); t becomes PENDING with the new tuple |
| t is PENDING, and the tuple equals the pending tuple | t becomes **CONFIRMED** with the new tuple; the revision is recorded once; **not re-counted** |
| t is PENDING, and the tuple differs from both | a new SOURCE_REVISION; PENDING with the newest tuple |
| t was in an accepted state and is **absent** from this response, while inside the requested range | a SOURCE_REVISION note (disappearance); if inside the 51-bar window, V8 already fails (DATA_GAP) |

**Rules:**
- Comparison is by **token text**, so `60000.0` versus `60000.00` is a revision (U85).
- **V11:** any PENDING bar inside the current 51-bar window → NO_DECISION (SOURCE_REVISION).
- Original bytes are never replaced. **Every observation made by a committed cycle remains in the chain.** Observations made by a cycle that never committed are orphaned (§10.2) and are not evidence.
- **Anti-lockout (DERIVED, conditional):** a single revision costs at least one slot, and blocks **no more than one slot if the source returns the revised bytes again on the next fetch.** A bar that keeps changing on every fetch (A → B → C → …) keeps the window PENDING and blocks **every** slot whose window contains it. That is fail-closed and its duration is UNBOUNDED (§15 U-D9).
- **Stage B:** at checkpoints (b) and (c) (§9.3), the 51-bar window is re-fetched and compared with the store. Any difference from the bytes bound in the proposal invalidates the authorization (U86).

**What the accepted states mean — and do not mean:**
- **BASELINED** means only that the bar was observed **once** and accepted as the baseline. It is **not** a two-fetch property.
- **CONFIRMED** means only that **a changed tuple was returned again, unchanged, on a later fetch.**
- The observation count records how many fetches returned the accepted tuple.
- It does **not** mean that the bar is final or will never change again. That is **UNVERIFIED** (U-D4).
- Settle and confirmation are policies, not proofs of finality.

### 4.10 Malformed values

A non-finite or non-numeric token, a price ≤ 0, v < 0, a non-integer n, or a malformed timestamp → NO_DECISION (MALFORMED_VALUE).

### 4.11 Quote validity (R4-10)

The quote is fetched every cycle and recorded. It is **validated only when a proposal is to be constructed** (signal BUY or EXIT, mapped to a proposal by §3.3).

| ID | Check |
|---|---|
| Q1 | bid (`bp`) present and > 0 |
| Q2 | ask (`ap`) present and > 0 |
| Q3 | ask ≥ bid |
| Q4 | bid size and ask size present and ≥ 0 |
| Q5 | `t` parses (§4.4) |

**Outcomes:**
- Any of Q1 to Q5 fails, or the quote is absent → **NO_DECISION (QUOTE_INVALID)**. This is **non-qualifying** (§11.1).
- Q1 to Q5 pass but the quote is stale → a proposal is constructed and **REJECTED (R4)**. This is **qualifying**.

*This corrects R3 CF-6 (RC-17): a missing quote cannot construct a proposal.*

### 4.12 Venue increments and minimum

| Item | Status |
|---|---|
| price increment | DOCUMENTED as 1, contradicted by OBSERVED quote cents (P-1): **UNVERIFIED** |
| quantity increment | DOCUMENTED as 0.0001: **UNVERIFIED** |
| minimum order size | DOCUMENTED as 0.0001, contradicted by a 1/price statement: **UNVERIFIED** |

- **No increment is inferred from quote or bar precision.**
- **Stage A:** the policy file carries the support-table values with `source: support_table_DOCUMENTED` and `status: UNVERIFIED`. Shadow sizing is **CONDITIONAL** on them.
- **Stage B:** the pre-flight reads the asset metadata. Any field absent or different from the policy file → **STOP, no order**.

### 4.13 Stage A-0 probe evidence

The probe is **one response**. It establishes nothing beyond itself.

**Probe artifacts** (`experiments/sl-pt-001/probe-A0/`; blobs from the founder's `git ls-tree` at `0cf59f5`):
- bars_body.json `c0e41bca…`, SHA-256 `E3640E5C…`;
- quote_body.json `9274cebf…`.

| Fact | Label |
|---|---|
| keyless HTTP 200 on both requests | OBSERVED |
| 72 bars; 72 unique `t`; first 21:15:00Z, last 03:10:00Z; 0 non-ascending; every step exactly 300 s; 0 off-grid | COMPUTED (the founder's P1 and P2, from raw token text) |
| 7 bars with v exactly 0, all written `0`; 72 `v` tokens extracted | COMPUTED (P3, exact decimal parse) |
| `c` tokens with at most 4 fraction digits; no exponent tokens | COMPUTED (P4, the artifact only) |
| quote `t` = 03:13:20.445036299Z; last bar `t` = 03:10:00Z | OBSERVED (P5) |
| the bar-labelling convention; that a **forming** candle was returned | **NOT established** (§4.5). R3's "forming bar OBSERVED" is withdrawn |
| price increment, fee, fill behaviour, revision behaviour, repeatability | UNVERIFIED |

---

## 5. Arithmetic and time (normative)

### 5.1 Exact arithmetic (R4-8)

- All values are **exact rationals** (integer numerator and denominator). A decimal implementation is allowed only if every operation other than the named rounding points runs with the **Inexact trap enabled**, so any rounding raises an error.
- Overflow is impossible with arbitrary-precision integers. A fixed-width representation is not permitted.

**Named rounding points (the only ones):**

| Quantity | Rounding |
|---|---|
| q (quantity) | floor to the quantity increment |
| L (limit) | to the price increment, conservatively: BUY down, EXIT up |
| R (reservation) | ceil to the cent |
| outstanding reservation | floor to the cent of the filled-cost term (§8.2) |
| display values | 8 dp, round-half-even; display only |

**Units:** USD values are exact rationals in dollars and are compared to the cent only at named points. BTC values are exact rationals.

### 5.2 Instants and comparison conventions

All instants are in ns (§4.4). Every inequality in §5.3 to §5.5 is evaluated exactly on integers.

### 5.3 Slot-anchored clocks (R4-3)

| Symbol | Definition |
|---|---|
| T_d | the slot decision instant (§6.2) |
| created | the **checkpoint-(a) instant**: the harness clock sample taken immediately before the proposal's policy evaluation, recorded in the TER (R4-11) |
| W | **90 s** (founder) |
| cutoff | the proposal proceeds only if T_d + 120 s − created ≥ W. Otherwise it is REJECTED (R13), never presented for approval |
| approval_deadline | min(created + 120 s, T_d + 120 s) |
| approved_at | when the approval record is committed (Stage B) |
| issued | when the authorization is issued; requires approved_at ≤ issued ≤ approval_deadline |
| expires_at | min(issued + 60 s, T_d + 180 s) |
| ceiling | T_d + 180 s |

**Non-contradiction (DERIVED; property test U53):**
1. Since created ≥ T_d (§6.2), **approval_deadline = T_d + 120 s** always.
2. Since issued ≤ T_d + 120 s, **expires_at = issued + 60 s ≤ T_d + 180 s** always. Every authorization gets its full 60 s and dies before T_d(i+1) = T_d + 300 s.
3. The cutoff guarantees at least W of approval time for any proposal presented. No proposal is ever presented with an expired or too-short window.
4. **Stage A:** SHADOW_EXPIRED is recorded at the ceiling, which is before T_d(i+1).

### 5.4 Comparison table

| Condition | True iff |
|---|---|
| bar completed | t + 300 s + settle ≤ T_d |
| quote fresh at checkpoint c | 0 ≤ c − quote.t ≤ 15 s. A quote dated after c fails, with zero tolerance until FD-G18 defines σ |
| cutoff passed | T_d + 120 s − created ≥ 90 s |
| approval timely | approved_at ≤ approval_deadline |
| issuance timely | issued ≤ approval_deadline (U90) |
| authorization live | now < expires_at (strict: expired **at** expires_at) |
| LP-PRESEND passes | now ≤ expires_at − δ_send, with 0 < δ_send < 60 s (§9.4) |
| cycle within slot | the CYCLE record is committed at an instant < T_d(i+1) |

### 5.5 Rationale for the bounds (DERIVED)

- Freshness of 15 s is shorter than the 60 s authorization, so every checkpoint gets its own fresh quote.
- The ceiling of T_d + 180 s leaves 120 s before the next slot. Since δ_send < 60 s, LP-PRESEND is satisfiable.

### 5.6 Clock source (R4-11)

**Stage A:**
- the harness **wall clock** (UTC epoch, integer ns). A monotonic clock is not used for t_send and t_recv, because θ compares epoch-anchored clocks;
- each cycle records, for the bars request: **t_send** (harness wall-clock instant immediately before sending), **t_recv** (harness wall-clock instant at receipt of the response headers) and **D**, the HTTP `Date` header (whole seconds, truncated), converted exactly to integer ns;
- **offset interval (DERIVED, under assumption A-CLK):** with θ = (data-host clock − harness clock),
  - θ_low = D − t_recv;
  - θ_high = D + 1 s − t_send;
  - θ lies in the open interval (θ_low, θ_high);
  - **assumption A-CLK (ASSUMED):** the server generated the `Date` header at some instant between t_send and t_recv on the harness clock. This excludes proxies or caches that rewrite or replay `Date`;
- **check V12b (implements the accepted R4-11 bound of 2 s; §16 OI-18):** pass iff **all four** hold, otherwise BOUNDARY_FAIL:
  1. `D` is present and parses (RFC 7231 IMF-fixdate);
  2. t_recv ≥ t_send (a negative round trip means the wall clock stepped backwards: fail);
  3. t_recv − t_send < 3 s (an explicit latency ceiling);
  4. θ_low ≥ −2 s **and** θ_high ≤ +2 s.
- Both offset bounds and the recorded instants go in the TER;
- *Consequences (DERIVED):* a pass proves |θ| < 2 s under A-CLK and A-CLK2, because θ lies in the open interval (θ_low, θ_high) ⊆ [−2 s, +2 s]. The interval width is 1 s + (t_recv − t_send), so condition 4 alone would admit a round trip of up to and **including** 3 s; condition 3 excludes exactly 3 s. *This corrects R4.2, whose text claimed a strict 3 s bound that the inequalities did not give;*
- **assumption A-CLK2 (ASSUMED):** the harness wall clock does not step during the bars request. Only a backward step larger than the round trip is detectable, by condition 2;
- **what this does not give:** it bounds the harness clock against the **data host's** clock only. It does not establish the accuracy of either clock against UTC. Stage A timing claims are therefore **CONDITIONAL on the data host's clock being accurate** (UNVERIFIED; §15 U-T2).

**Stage B:** the time source, skew bound σ and δ_send are **DEFERRED** (FD-G18).

---

## 6. Slots, invocations and cycles (normative; R4-2, R4-4)

### 6.1 Timer contract (FD-7)

| Item | Rule |
|---|---|
| Trigger | **Windows Task Scheduler**, every 5 minutes at T_d. For settle = 60 s that is minutes 1, 6, …, 56 of each hour, second 0 |
| Scheduler settings | "run a new instance in parallel"; "run as soon as possible after a missed start" **off**; no retry; the machine kept awake for the run |
| Wrapper | the task runs a **wrapper**, not the harness. The wrapper (1) appends one line to the **invocation log**: invocation instant in ns, process id, wrapper hash; then (2) starts the harness, passing the invocation instant and the manifest path, both fixed in the task definition. It has no other logic: no strategy, policy, credential or trading capability |
| Integrity | the task's exported XML and the wrapper's hash are recorded in the run manifest. The invocation log's hash is recorded at RUN_CLOSE |
| Verification | the setting names and behaviours above are recalled, not checked: **UNVERIFIED**. They must be checked against the exported XML before the first run (U73 to U77) |
| Branch C note | V12a's pre-fetch check covers the harness's own client and the checked credential sources only (§2.2, §2.3) |

**Wrapper status (OI-13, founder decision record v2):** the wrapper is the "log" part of FD-7's "invoke and log only". It performs **no** policy, authorization, trading or recovery logic.

### 6.2 Slot identity

| Symbol | Definition |
|---|---|
| T_d0 | the run's first decision instant. It must satisfy (T_d0 − settle) mod 300 s = 0, so that T_d = a candle close + settle |
| T_d(i) | T_d0 + 300 s · i, for i = 0 … N − 1 (N = `declared_slots`, §10.3) |
| owning slot | an invocation at instant x belongs to slot i iff T_d(i) ≤ x < T_d(i+1). An invocation before T_d0 or at/after T_d(N) belongs to **no slot**: it is recorded as an OFF_RUN anomaly and does nothing else |
| cycle_id(i) | (BTC/USD, t_exp(i)), where t_exp(i) = T_d(i) − settle − 300 s (= T_d(i) − 360 s for settle = 60 s) |

Lateness within a slot does not change the slot (DERIVED).

### 6.3 Single writer, lock and hard slot boundary (R4-4)

**The append lock:**
- The global chain file (§10.1) has one **append lock**, an OS exclusive file lock.
- **Every** chain append happens under it.
- An appender must hold the **run lock token** for its slot and must find now < T_d(its slot + 1). Otherwise the append is refused and the process exits.

**Run lock token.** The token is a record of (slot index, process id, acquired_at). It is acquired and transferred only under the append lock.

**A new invocation for slot j, holding the append lock:**

| Token state | Action |
|---|---|
| a CYCLE record for slot j already exists (a duplicate invocation after completion) | append a **CONCURRENT_INVOCATION** anomaly for slot j, then exit (replay protection) |
| no token, or a token for slot i < j whose slot has a terminal CYCLE record | take the token for j |
| token for slot i < j **without** a terminal record | append **CYCLE_OVERRUN** for slot i (written by this successor), record the termination request for the old process id, then take the token for j. The old process's later appends are refused (it no longer holds the token) |
| token for slot j (a second invocation of the same slot) | append a **CONCURRENT_INVOCATION** anomaly record for slot j, then exit. The running cycle continues |
| token held by an INJECTION (§6.5) | append INJECTION_ABORTED, then take the token for j |

**Consequences:**
- A cycle that overruns never causes the next slot to fail (this resolves Gemini B-03).
- **SKIPPED is removed.** A slot without a CYCLE record is classified by the auditor as OVERRUN, INCOMPLETE or MISSING (§11.2). No component writes those classifications except CYCLE_OVERRUN records (§6.3, §10.1).

### 6.4 Cycle procedure (per slot)

1. **Pre-fetch boundary check (V12a):**
   - no broker credential in the process environment variables or the harness configuration file (the checked scope, §2.2);
   - the client allowlist is exactly the market-data host.
   - Failure → a BOUNDARY_FAIL CYCLE record; no fetch.
2. **Fetch** bars, recording t_send and t_recv (§5.6). Store the raw artifacts (§10.2).
3. **Clock check (V12b)** on the bars response (§5.6). Failure → a BOUNDARY_FAIL CYCLE record; the quote is not fetched.
4. **Fetch** the quote (§4.2). Store the raw artifacts.
5. **Validate** V1 to V11 (§4.7). Update the bar store observations (§4.9).
6. **Compute** S20 and S50 at k and k−1, then D(k−1) and D(k); then the signal (§3.2) and the mapping (§3.3).
7. **Propose** (only if mapped to a proposal): §7.
8. **Commit** the CYCLE record (§10.4):
   - for HOLD, NO_ACTION, NO_DECISION and BOUNDARY_FAIL: immediately;
   - for a proposal: at REJECTED, or at SHADOW_EXPIRED when the ceiling is reached.
   - The commit must happen before T_d(i+1). **A cycle that has not committed by T_d(i+1) is overrun.** It is recorded as CYCLE_OVERRUN by the successor invocation (§6.3) or, for the last slot of a run, by RUN_CLOSE (§10.1). If neither exists, the auditor classifies the slot INCOMPLETE (§11.2). *(Gemini B2-01.)*

### 6.5 Injections

- Injected proposals (`origin: INJECTED`) are run only on the founder's command.
- They use fixture inputs, never live slots. They take the run lock token as an INJECTION. They may not start within 30 s of the next T_d. They are aborted by any slot invocation (§6.3).
- They are recorded as INJECTION records and **never occupy or satisfy a slot**.

---

## 7. Proposal construction and policy (normative)

### 7.1 Evaluation order (deterministic; all failures recorded)

1. Quote validity Q1 to Q5 (§4.11). Failure → NO_DECISION (QUOTE_INVALID); no proposal record.
2. Sample checkpoint (a) → `created`.
3. Construct the proposal: side; L (§7.2); q, R and budget (**§8.1.1**; EXIT: q_exit per §8.1.1); `partial_fill_accepted` (Stage B only; §9.5).
4. Evaluate **every** applicable rule (§7.3) and record each result.
5. Any FAIL → REJECTED, with all failing rule codes. All PASS → Stage A: SHADOW_EXPIRED at the ceiling; Stage B: present it for approval (§9).

### 7.2 Limit price (FD-4, CF-1)

- **BUY:** L = the ask of the checkpoint-(a) quote, rounded **down** to the price increment.
- **EXIT:** L = the bid, rounded **up**.
- L is fixed at proposal creation and bound by approval (Stage B). Later quotes **validate only**; nothing is repriced or resized.
- *Recorded consequence (DERIVED):* if the price increment is $1, a BUY limit rounded down sits below the ask and may not execute immediately. This bears on the TIF decision (§9.5).

### 7.3 Policy P-0.2

| Rule | Check (exact) | Value | Stage | Status |
|---|---|---|---|---|
| R1 | instrument allowlisted | BTC/USD | A, B | settled |
| R2 | limit order; TIF allowlisted; `partial_fill_accepted` = true | TIF DEFERRED | B (A: limit) | FD-4 |
| R3 | proposal schema complete and valid | — | A, B | — |
| R4 | quote fresh at the checkpoint (§5.4) | 15 s | A: (a); B: (a)–(d) | — |
| R5 | \|L − mid\| ≤ 0.01 × mid, with mid = (bid + ask) / 2 of the checkpoint quote | ±1% | A, B | — |
| R6 | R ≤ cash_available (§8) | — | A, B | — |
| R7 | R ≤ $150.00 | $150 | A, B | **FD-4** |
| R8 | BTC notional at bid + R ≤ $300.00 | $300 | A, B | accepted (RC-25a) |
| R9 | q_exit ≤ held BTC − reserved BTC | — | A, B | — |
| R10 | q ≥ min_order_size; q on qty_increment; L on price_increment | policy file (§7.4) | A: CONDITIONAL; B: metadata | UNVERIFIED |
| R11 | at most one open authorization or order per instrument | — | A, B | — |
| R12 | **buy gate, not a loss limit:** equity < $450.00 → reject BUY (equity = cash + BTC × bid) | $450 | A, B | accepted (RC-25b) |
| R13 | cutoff (§5.3); clock rules (§5.4) | W = 90 s | A, B | founder (W) |
| R14 | re-check at (b), (c) and (d): §9.3 | — | B | — |
| R15 | EXIT only while long; q_exit per §8.3 | — | A, B | — |
| R16 | **FD-3** | — | A (vacuous), B | **FD-3** |

**Notes on R7, R8 and R12 (DERIVED; v2):**
- **R12 is a buy gate.** It never sells and never limits loss. It is evaluated at checkpoint (a) only. It **can block the first BUY** if the reconciled pre-trade cash is below $450.00. The founder's dashboard showed $500.00 cash (OBSERVED, screenshot, 2026-11-25 09:34 PM EST); the Stage B pre-flight must confirm this from the reconciled ledger.
- **R8 cannot bind on the first BUY,** provided the pre-flight confirms there is no BTC position: notional 0 + R ≤ $150 < $300.
- **The milestone's loss bound is R7** (spot, no leverage): at most the reserved spend R ≤ $150.00. Worst-case equity at the milestone is $350.00 if BTC goes to zero.
- **In Stage A,** R8 and R12 never bind on live data, because the shadow ledger never changes (§8.1).

### 7.4 Policy file

- `policy/P-0.2.json` is to be created at build. It encodes §7.3 exactly, plus:
  - `price_increment`, `qty_increment` and `min_order_size`, each with `source` and `status`;
  - `f_res`;
  - `settle_s`, `W_s` and `freshness_s`.
- Its SHA-256 is recorded in every CYCLE record and in the manifest.
- Any change is a new version with a founder record.

---

## 8. Ledgers and reservations (normative; R4-7)

### 8.1 Stage A shadow ledger

- **Opening cash** is declared in the manifest: **$500.00** (accepted, RC-25d). BTC opens at 0.
- **Shadow fills are not simulated.** Doing so would mean inventing venue behaviour, which the dispatch prohibits.
- A shadow reservation R is created when a proposal passes policy at checkpoint (a), and released at SHADOW_EXPIRED **in the same cycle**. A shadow reservation therefore never crosses a slot (DERIVED).
- Consequence: shadow cash and BTC never change. R8 and R12 never bind on live data (§16, OI-08).

#### 8.1.1 Stage A sizing and shadow reservation (normative; Stage A freeze)

*This subsection supplies the sizing rule that R4.1 placed only in the Stage B draft (GPT G-01). In R4 and R4.1 the BUY quantity formula was missing altogether; it is restored here from R3 §6.2.*

| Symbol | Definition (exact; §5.1) |
|---|---|
| shadow_cash | the manifest's opening cash ($500.00). **It must be an exact multiple of $0.01**; otherwise the manifest is invalid. It never changes in Stage A |
| L | the limit price, **as defined in §7.2**: the checkpoint-(a) ask rounded down to `price_increment` (BUY), or the bid rounded up (EXIT) |
| shadow_reserved | the amount of the cycle's own shadow reservation, if any. It is 0 before step 3 of §7.1, because reservations never cross a slot (§8.1) |
| cash_available | shadow_cash − shadow_reserved |
| f_res | the policy file's reservation fee rate, 0.0025 (DOCUMENTED tier-1 taker; UNVERIFIED for paper). A reservation bound, not a booked fee |
| budget | min($150.00, cash_available) |
| q | floor to `qty_increment` of budget / (L × (1 + f_res)) |
| R | ceil to the cent of q × L × (1 + f_res) |
| shadow_reserved_btc | 0 before step 3 of §7.1. Set to q_exit when an EXIT proposal passes every rule at checkpoint (a); released at SHADOW_EXPIRED in the same cycle |
| q_exit | floor to `qty_increment` of (shadow BTC − shadow_reserved_btc). Shadow BTC is always 0 on live data, so EXIT proposals arise only from fixtures (§3.3) |

**Rules:**
- R6, R7 and R10 (§7.3) are evaluated against these values. **R ≤ budget ≤ $150.00 holds by construction** (DERIVED, given L > 0, f_res ≥ 0 and shadow_cash on the cent grid: q × L × (1 + f_res) ≤ budget, and budget is on the cent grid), but R7 is still evaluated and recorded.
- q < `min_order_size` → REJECTED (R10).
- **Shadow reservation:** created with amount R, only if every rule passes at checkpoint (a). Released at SHADOW_EXPIRED in the same cycle.
- **Increment values:** `qty_increment`, `price_increment` and `min_order_size` come from the policy file with `source: support_table_DOCUMENTED`, `status: UNVERIFIED` (§4.12). All Stage A sizing results are **CONDITIONAL** on them.
- The Stage B ledger (§8.2) reuses the formulas for q and R, with its reconciled cash_available in place of the shadow value.

### 8.2 Stage B typed ledger (specified; DEFERRED) — **STAGE B DRAFT: not in the Stage A freeze**

**Balances:**
- **USD:** cash and reserved_usd, in exact cents.
- **BTC:** held_btc and reserved_btc, exact, on the quantity increment.

**cash_available** = cash − reserved_usd. **btc_available** = held_btc − reserved_btc.

**BUY reservation:**
- q and R as in §8.1.1, with the reconciled cash_available. R = ceil to the cent of q × L × (1 + f_res), where f_res = 0.0025 is a DOCUMENTED tier-1 taker rate. Whether it applies on paper, and whether maker or taker, is UNVERIFIED.
- f_res is a **reservation bound, not a booked fee.**
- With Q_f = the **cumulative** filled quantity: outstanding_usd = max(0, R − floor to the cent of (Q_f × L × (1 + f_res))).
- This is computed from the cumulative quantity, **never by per-fill decrements** (S2-2, Gemini B-06).

### 8.3 EXIT reservation (Stage B) — **STAGE B DRAFT: not in the Stage A freeze; outside the milestone (§0.1)**

- q_exit = floor to the quantity increment of btc_available.
- reserved_btc increases by q_exit.
- outstanding_btc = q_exit − Q_f.

### 8.4 Fill events (Stage B) — **STAGE B DRAFT: not in the Stage A freeze**

**Identity and order:**
- Each fill event is identified by the venue's fill or activity id (the field name is UNVERIFIED) and applied **once** (idempotent; U54).
- Q_f is monotone non-decreasing. A reported decrease, or any correction or bust → **DISCREPANCY: halt** (U55, U59). Handling of corrections stays Stage C.

**BUY fill** (q_f at price p_f):
- **Fee in BTC** (DOCUMENTED as the received asset; UNVERIFIED on paper): held_btc += q_f − fee_btc; cash −= q_f × p_f; fee_usd_equiv = fee_btc × p_f.
- **Fee in USD:** held_btc += q_f; cash −= q_f × p_f + fee_usd; fee_usd_equiv = fee_usd.
- **L-2 fee check for a BUY** (U57, U58), evaluated exactly with no rounding: Σ fee_usd_equiv ≤ Q_f × L × (1 + f_res) − Σ (q_f × p_f). That is, the fees on the filled quantity must fit inside the part of the reservation the fills did not use. Otherwise DISCREPANCY: halt.
- *Note:* valuing a BTC fee at p_f is a defined accounting convention, not a venue fact.

**EXIT fill:** held_btc −= q_f; cash += q_f × p_f − fee_usd. A fee in BTC is handled symmetrically: held_btc −= fee_btc, and fee_usd_equiv = fee_btc × p_f.
- **L-2 fee check for an EXIT:** Σ fee_usd_equiv ≤ f_res × Σ (q_f × p_f). Otherwise DISCREPANCY: halt.

**Release:**
- A reservation remainder (outstanding_usd or outstanding_btc) is released **only** on a terminal order state **confirmed by reconciliation**: filled, canceled, expired, or venue-rejected.
- A cancel **request** changes nothing (U56).
- An authorization that dies unconsumed releases R in full, citing the death event.

**AMBIGUOUS:** fully reserved until reconciled. It blocks proposals (R16). No resubmission (FD-G16, DEFERRED).

### 8.5 Atomicity (Stage B) — **STAGE B DRAFT: not in the Stage A freeze**

- The ledger has a **single writer**.
- Each transition is **one append-only ledger event** under the ledger lock, citing its trigger: the authorization, the fill event id, the terminal evidence or the death event.
- No transition is inferred.

### 8.6 Invariants and falsifiers (DERIVED; DESIGNED tests) — **STAGE B DRAFT: not in the Stage A freeze**

**Invariants:**
- reserved_usd ≥ 0 and reserved_btc ≥ 0;
- at most one unreleased reservation per instrument (R11, R16; U60);
- Σ unreleased reservations + booked spend ≤ opening cash;
- every release cites evidence.

**Falsifiers:**
- two simultaneously unreleased reservations;
- a release without evidence;
- a negative outstanding amount;
- a fill applied twice.

---

## 9. Approval, authorization and execution boundary (Stage B; DEFERRED; FD-9) — **STAGE B DRAFT: not in the Stage A freeze**

Nothing in this section is implemented. G-07 Draft 0.3 defines the execution components and terms used here: K3, K5, LP-CONSUME, LP-WAL, LP-PRESEND.

### 9.1 Approval record (A0.3-13)

- **Append-only, in K3.** It is bound to the proposal's fields.
- **Bound fields:**
  - proposal_id, cycle_id;
  - strategy id and version; input_snapshot_sha256;
  - instrument, side, q, L, TIF, `partial_fill_accepted`, R, fee estimate;
  - policy hash, configuration hash;
  - account, venue, executor_id;
  - approved_at, approval_deadline;
  - approver identity.
- **Approver authentication is UNVERIFIED** (FD-G13).
- **Approval of the experiment is not approval of an order.**

### 9.2 Issuance predicate (A0.3-13)

- K3 issues an authorization only if:
  - an approval record exists whose bound fields **exactly** equal the proposal's (U63);
  - approved_at ≤ issued ≤ approval_deadline (U90);
  - every check at checkpoint (b) passes.
- **No approval, no authorization.**
- LP-CONSUME additionally requires that the approval record still exists unrevoked (U64).
- **Falsifier:** an ACTIVE or CONSUMED authorization without a matching, timely approval record (U21, U22).

### 9.3 Checkpoints (R14)

| Checkpoint | Instant | Fresh quote | Rules re-evaluated with the bound L and q | Bars re-fetched |
|---|---|---|---|---|
| (a) | creation | Q1–Q5 and R4 | all | — |
| (b) | issuance | new quote; Q1–Q5; R4 | R4, R5, R6, R7, R9, R10, R11, R16 | yes (§4.9) |
| (c) | LP-CONSUME | new quote; Q1–Q5; R4 | same as (b) | yes |
| (d) | LP-PRESEND | new quote; Q1–Q5; R4 | R4, R5 | no (only δ_send remains) |

**Any failure kills the authorization** and releases R. No repricing or parameter change occurs.

### 9.4 Send interval (R4-12)

- **δ_send** := the enforced upper bound on (first-outbound-byte instant − LP-PRESEND sample instant), with 0 < δ_send < 60 s.
- If the send has not begun by sample + δ_send → abort, recorded NOT_SENT. The authorization dies.
- If the send began but exceeded the bound, or any send outcome is uncertain → **AMBIGUOUS**: query by the original COID only; no replacement and no new authorization until resolved.
- The value of δ_send and its measurement are **DEFERRED** (FD-G18).
- The remote-acceptance race is **residual**: no local check bounds broker-side acceptance time.

### 9.5 TIF and partial fills (FD-4; TIF DEFERRED)

- The candidates are GTC (with a Sentinel cancel request no later than the ceiling) or IOC. FOK is excluded, because its support is DOCUMENTED-contradictory.
- `partial_fill_accepted` must be **true** in the approval. If it is false, no order can be constructed (no all-or-none TIF is verified), so the result is REJECTED (R2).

### 9.6 First-order sequence (CF-7)

1. Stub-venue tests of every G-07 minimum control and of the AMBIGUOUS path.
2. **Pre-flight, read-only, with paper keys** (FD-8). No order. It covers:
   - the account configuration (1×, shorting off, buying power);
   - the asset metadata, which must match the policy;
   - a list of orders, expected empty;
   - a query for a **never-used** COID, expected not-found and recorded.
3. The first order is the first **governed** order. After it reaches a terminal state, a query by its COID establishes the found branch.
4. The duplicate-COID test is **separately authorized**, later (Stage C).

### 9.7 STOP conditions (Stage B)

Each condition means: stop, record, and no new authorization until it is resolved.

| Condition | Where detected |
|---|---|
| a pending, conflicting or missing bar in the window; a re-fetch mismatch | §4.7, §4.9 |
| quote invalid, or stale at any checkpoint | §4.11, §5.4 |
| clock offset unmeasured or beyond its bound | §5.6, FD-G18 |
| overrun, concurrent invocation | §6.3 |
| approval missing or late; issuance late; authorization expired | §9.2 |
| any change to bound parameters | §9.1 |
| an open, partial or AMBIGUOUS order; an unresolved authorization | R16 |
| LP-PRESEND failure; δ_send exceeded | §9.4 |
| missing durable LP-WAL record | G-07 I7 |
| uncertain submission (query by the original COID only) | §9.4 |
| an unmatched broker order (L-3); any DISCREPANCY | §12, §8.4 |

### 9.8 Required claim language (first paper trade)

> "A paper order was submitted through the Sentinel workflow under recorded approval and reconciled against Alpaca paper records. This deployment does not satisfy G7-I5 or G7-I8; it does not demonstrate that external actions on the account can occur only through Sentinel."

**G7-I8 is known false** on the founder's machine, and **G7-I5 is not established.** No R4 text claims either.

---

## 10. Evidence model (normative; R4-2, R4-5)

### 10.1 Global chain

**One append-only file**, `chain/events.jsonl`, shared by all runs.
- Record: `{seq, prev_hash, type, body, hash}`, where hash = SHA-256 of the canonical serialization (§10.5) of the record without `hash`.
- `seq` starts at 0 with GENESIS and increases by exactly 1.
- **Writer:** the harness only, under the append lock (§6.3).
- **Founder action:** push the chain at least at every RUN_OPEN and RUN_CLOSE.

| Type | Written by | Content |
|---|---|---|
| GENESIS | the harness, once | experiment id, frozen-set hashes |
| RUN_OPEN | the harness, at the first invocation of a run | manifest SHA-256 |
| CYCLE | the slot's harness process | the TER (§10.4) |
| CYCLE_OVERRUN | the successor (§6.3) | slot index; old process id |
| CONCURRENT_INVOCATION | the duplicate invocation | slot index; invocation instant |
| OFF_RUN | an invocation outside the run | invocation instant |
| INJECTION / INJECTION_ABORTED | the harness | injected proposal and result |
| RUN_STOPPED | the harness, optionally, on the founder's command | instant. It **does not shorten N** |
| RUN_CLOSE | the harness, on the founder's command after T_d(N) | invocation-log SHA-256; task-XML SHA-256. **If the run token is held by slot N − 1 without a terminal record, RUN_CLOSE first appends CYCLE_OVERRUN for that slot** |

### 10.2 Artifacts

- Raw responses are stored at `artifacts/<sha256>`. They are written by the harness before parsing and referenced by hash from CYCLE records.
- The **invocation log** (`chain/invocations/<manifest_sha256>.log`) is owned and written **only by the wrapper**; it is append-only.
- **Manifests** (`runs/<name>.json`) are owned by the **founder**.
- **Orphaned artifacts** (*GPT G-05*): an artifact not referenced by any committed chain record (for example, fetched by a cycle that crashed before committing) is **not evidence**. The auditor lists orphaned artifacts in its report and never uses them in reconstruction. Such a slot cannot qualify (§11.2).
- Nothing else writes these files.

### 10.3 Run manifest (founder-authored; immutable)

**Fields:**
- `instrument`;
- `T_d0` (§6.2);
- **`declared_slots`** = N, an integer ≥ 30;
- `opening_cash`;
- frozen-set hashes, harness hash, policy hash;
- task-XML hash, wrapper hash;
- `prev_chain_head`: the hash of the chain's last record before this run.

**Rules:**
- **No open-ended run is milestone-eligible.**
- The founder **commits and pushes the manifest before T_d0.** The GitHub push record is the timing evidence; a local commit alone is insufficient (git dates are self-asserted).
- A manifest is never edited. A changed manifest is a different hash, so it is a different run (U72).

### 10.4 TER schema v1 (closed)

**Fields (closed set; an unknown or missing field is invalid; U67):**
- `schema` = "TER-1";
- `origin` ∈ {SCHEDULED, INJECTED};
- `manifest_sha256`, `slot_index`, `cycle_id`;
- invocation instant; T_d; checkpoint-(a) instant;
- request URLs and instants; artifact hashes (bars, quote, headers);
- per-bar token tuples for every completed bar fetched; excluded bars;
- bar-store transitions (§4.9);
- V1 to V11, V12a and V12b results; Q1 to Q5 results (if evaluated);
- S20 and S50 at k and k−1; D(k−1) and D(k); signal; mapping;
- proposal (if any), with L, q, R and the rounding inputs;
- every rule result with its rule code;
- `terminal_state`, from the closed set (§11.1);
- policy hash; displayed sizes; `egress_scope` = "CLIENT_ALLOWLIST_ONLY" (§2.3). *Renamed from R4.1's "isolation-branch marker" so the field cannot be read as an isolation claim (Gemini B2-06);*
- t_send, t_recv, D, θ_low, θ_high (§5.6);
- for each bar used: its bar-store state and observation count (§4.9).

**Unevaluated checks and absent artifacts (every field is always present; omission is invalid):**
- each V1 to V11, V12a, V12b and Q1 to Q5 result is one of `PASS`, `FAIL` or `NOT_EVALUATED`. A `NOT_EVALUATED` result carries a reason: `V12A_FAILED`, `V12B_FAILED`, `DATA_INVALID` (a V1 to V11 failure), or `NO_PROPOSAL`;
- an artifact hash, the clock fields (t_send, t_recv, D, θ_low, θ_high) and the computed values (S20, S50, D(k−1), D(k), signal, mapping, proposal) are JSON `null` when they do not exist. `null` is the **only** non-string value permitted in a TER.

| Terminal path | Present | `null` or `NOT_EVALUATED` |
|---|---|---|
| V12a fails | V12a = FAIL | all artifacts and clock fields `null`; every other check NOT_EVALUATED (V12A_FAILED); computed values `null` |
| V12b fails | bars artifact; clock fields; V12a = PASS; V12b = FAIL | quote artifact `null`; V1 to V11 and Q1 to Q5 NOT_EVALUATED (V12B_FAILED); computed values `null` |
| a V1 to V11 failure | both artifacts; V results as evaluated | Q1 to Q5 NOT_EVALUATED (DATA_INVALID); computed values `null` |
| HOLD or NO_ACTION | all V; computed values up to the mapping | Q1 to Q5 NOT_EVALUATED (NO_PROPOSAL); proposal `null` |
| a proposal (REJECTED, SHADOW_EXPIRED) or QUOTE_INVALID | everything evaluated | proposal `null` if QUOTE_INVALID |

**Encoding rule:** **every numeric value is encoded as a JSON string** holding the exact decimal or the integer ns. **No JSON numbers appear in a TER** (U88), because canonical JSON serializes numbers as IEEE doubles (§10.5).

### 10.5 Canonical serialization

- Canonicalization follows **RFC 8785** (JSON Canonicalization Scheme).
- Because RFC 8785 formats numbers as IEEE-754 doubles, the string-only rule in §10.4 is **required for exactness** (DERIVED).

---

## 11. Milestone counter and audit (normative)

### 11.1 Terminal states (closed set)

- **Can qualify:** HOLD, NO_ACTION, REJECTED, SHADOW_EXPIRED.
- **Never qualify:** NO_DECISION(sub-reason), CYCLE_OVERRUN, BOUNDARY_FAIL.
- NO_DECISION sub-reasons are: FETCH_FAILED, INCOMPLETE_RESPONSE, MALFORMED_VALUE, DATA_CONFLICT, STALE_SERIES, DATA_GAP, INSUFFICIENT_HISTORY, SOURCE_REVISION, QUOTE_INVALID.
- **Removed from R3:** SKIPPED (see §6.3) and CONCURRENT_INVOCATION as a terminal state (it is now an anomaly record).

**Qualifying conditions.** The auditor checks each condition by **recomputation**, never from fields:

| State | Conditions (all required) |
|---|---|
| HOLD | V1 to V11, V12a and V12b pass; D(k−1) and D(k) are recomputed from the artifacts; signal = HOLD |
| NO_ACTION | V pass; D recomputed; signal ∈ {BUY, EXIT}; mapped to NO_ACTION by §3.3 |
| REJECTED | V pass; D recomputed; Q1 to Q5 pass; a proposal constructed; ≥ 1 rule fails on recomputation (including the R13 cutoff) |
| SHADOW_EXPIRED | V pass; D recomputed; Q pass; all rules pass on recomputation; recorded at the ceiling |

### 11.2 Slot classification

The auditor runs this per manifest and per slot i = 0 … N − 1, once now ≥ T_d(N):

Rows are applied **in this order of precedence**; the first matching row decides.

| # | Evidence for slot i | Classification |
|---|---|---|
| 1 | any chain record for slot i (CYCLE, CYCLE_OVERRUN or CONCURRENT_INVOCATION) fails the schema or the hash-chain check | **NON-QUALIFYING** (integrity finding) |
| 2 | a CYCLE_OVERRUN record **and** one or more CYCLE records for slot i | **CONFLICT** (non-qualifying; a finding) |
| 3 | a CYCLE_OVERRUN record and no CYCLE record | **OVERRUN** (non-qualifying) |
| 4 | no CYCLE record, and an invocation-log line for slot i | **INCOMPLETE** (non-qualifying; orphaned artifacts listed, §10.2) |
| 5 | no CYCLE record, and no invocation-log line | **MISSING** (non-qualifying) |
| 6 | more than one CYCLE record | **DUPLICATE** (non-qualifying) |
| 7 | exactly one CYCLE record and a CONCURRENT_INVOCATION anomaly | **NON-QUALIFYING** (a scheduler fault) |
| 8 | exactly one CYCLE record whose artifact hashes or recomputation fail | **NON-QUALIFYING** (a finding) |
| 9 | exactly one valid CYCLE record meeting §11.1 | **QUALIFYING** |

**Findings that never qualify:**
- **OFF_GRID:** a CYCLE record matching no slot of its manifest;
- an INJECTION presented as SCHEDULED (U68);
- the same cycle_id appearing under two manifests (U69).

**Invocation consistency (U77):**
- each invocation-log line must correspond to a chain record for its slot (a CYCLE, CONCURRENT_INVOCATION, CYCLE_OVERRUN or OFF_RUN record). **An invocation line whose slot is classified INCOMPLETE is reported once, under INCOMPLETE, not as a separate mismatch;**
- each CYCLE record must correspond to an invocation line;
- any mismatch is a finding.

### 11.3 Completeness of the run set (U66, U70, U72)

The auditor:
1. verifies the chain from GENESIS (contiguous `seq`, every `prev_hash` and `hash`);
2. lists every RUN_OPEN manifest hash in the chain and every manifest file in the repository;
3. reports any manifest that appears in one list but not the other;
4. checks each manifest's `prev_chain_head` against the chain;
5. **records in its report** the repository commit it audited, the chain head hash it audited, and the list of orphaned artifacts (*Gemini B2-05*).

**The exit report lists every manifest.** Its denominator is every slot of every manifest: **missing, incomplete and overrun slots stay in the denominator.**
- **The exit report also counts qualifying NO_ACTION slots by their underlying signal** (BUY or EXIT). In Stage A every live EXIT maps to NO_ACTION because the shadow ledger is always flat (§3.3), so these slots qualify without exercising a position (*Gemini B2-04*).

**Limitation (stated):** completeness is relative to the GENESIS record and to what the founder pushed. A chain that was never pushed cannot be audited.

### 11.4 Counter (DERIVED)

- run_length = the longest run of consecutive QUALIFYING slots **within one manifest**.
- **M1-1 is met iff run_length ≥ 30 and ≥ 5 runtime injections were rejected by the intended rule.**
- The harness's own counter, if any, is never evidence. Any mismatch with the audit is reported.

### 11.5 Auditor and reconstruction (FD-6)

**Author:** GPT, after the freeze, from the frozen set only. The script's hash is committed before any TER exists.
- It performs **(a)** the blind reconstruction of 5 cycles drawn by a seed committed before the run, and **(b)** the full slot audit (§11.2, §11.3).
- The founder runs it.

**Founder hand cross-check:** for one manifest, the founder enumerates the expected cycle_id(i) for i = 0 … N − 1 by hand and compares them with the audit's slot list.

**GPT dissent (preserved):** combining reconstruction and audit in one script creates common-mode risk, and GPT recommended a separate author.
- The founder decided otherwise.
- R4's mitigation **reduces but does not remove** that risk: the audit is pure recomputation from the raw artifacts, plus the hand cross-check.
- A misreading of R4 shared by the harness and the script would still go undetected (UNBOUNDED; §15).

### 11.6 Other M1 criteria

| Criterion | Requirement |
|---|---|
| M1-2 completeness | every required TER field present for every slot record; MISSING slots are findings |
| M1-3 integrity | the chain verifies end to end; every artifact hash resolves; git history shows no rewrites |
| M1-4 look-ahead | no input is used from after its decision instant (from §4.6 and the checkpoint instants) |
| M1-5 governance | every injection is rejected with the correct rule code; 0 non-injected proposals that violate P-0.2 on recomputation |
| M1-6 reconstruction | 5 seeded cycles reconstructed by the FD-6 script with 0 unexplained differences |
| M1-7 honesty | no performance claim beyond the sample |

**Test coverage (pre-live gate):** before the first live-data cycle, at least one **EXECUTED** pass case and fail case for every rule applicable in Stage A (R1, R3 to R13, R15, R16), plus every §14 test whose Stage column contains "A", with the evidence retained.
- **R2 and R14 exist only in Stage B.** Their executed tests belong to the Stage B gate, before the first order.

---

## 12. Reconciliation (Stage B; DEFERRED) — **STAGE B DRAFT: not in the Stage A freeze**

| Level | Compares | Tolerance | On mismatch |
|---|---|---|---|
| L-1 | approved parameters vs the raw request | exact | governance failure; halt |
| L-2 | Sentinel ledger vs the broker (cash, BTC, open orders, fees per §8.4) | exact, in cents and on the quantity increment | DISCREPANCY; halt |
| L-3 | every broker order ↔ exactly one auth_id (COID) | exact | UNMEDIATED or DUPLICATE: failure |
| L-4 | independent recomputation from the artifacts | exact | an independence finding |

**No automatic correction.** Every resolution is an explicit event citing evidence.

---

## 13. Claims

**What M1 can support** (when met):
- distinct completed candles were processed;
- deterministic decisions on recorded inputs;
- the specified bad data was rejected in the observed slots;
- a complete, reproducible record for the audited manifests;
- the injections were rejected by the intended rules;
- an independent reconstruction of the sample was obtained.

**What M1 cannot support:**
- profitability or significance;
- robustness or multi-day reliability;
- the truth of the market data;
- broker behaviour;
- **any G-07 property.**
- **process-level or host-level isolation** (Branch C, §2.3). Every Stage A result carries the §2.3 limitation statement verbatim.

Thirty slots are not thirty trades. **Qualifying NO_ACTION slots from EXIT-while-flat show only that the signal and mapping ran correctly on live data; they do not exercise any position logic** (§11.3).

---

## 14. Test inventory (all **DESIGNED**; none **EXECUTED**)

"Stage" means the stage whose code the test exercises. Stage B tests use synthetic state-machine fixtures and prove nothing about the venue.

### 14.1 Strategy and data

| ID | Test | Expected (DERIVED) | Stage |
|---|---|---|---|
| U1 | D(k−1) = −4, D(k) = −1 | HOLD | A |
| U2 | −3 → +2 | BUY | A |
| U3 | +3 → −2 | EXIT | A |
| U4a | −1 → 0 | HOLD | A |
| U4b | 0 → +1 | BUY | A |
| U4c | +1, 0, +1 | BUY at the 3rd step (literal) | A |
| U4d | −1, 0, −1 | EXIT at the 3rd step | A |
| U4e | closes whose float sums differ but whose exact sums are equal | HOLD at exact equality | A |
| U5 | T_d = 10:05:30 (a late invocation in the slot whose T_d = 10:01); bars up to t = 10:00 | the 10:00 bar is excluded; t_exp = 09:55 | A |
| U6 | one bar absent in the 51-bar window | DATA_GAP | A |
| U7a | duplicate t, byte-identical | collapsed; proceed with a note | A |
| U7b | duplicate t, differing content | DATA_CONFLICT | A |
| U8 | (a) the newest completed bar is 10 min older than t_exp; (b) a valid quote 16 s old with a BUY signal | (a) STALE_SERIES; (b) REJECTED (R4) | A |
| U9 | replay of stored artifacts | byte-identical TER body. **REPLAY is an out-of-band test-run label**: it is never a TER field or chain record, and replay output is never appended (*GPT G-06*) | A |
| U10 | 100 runs; other process, locale, timezone | identical results | A |
| U11 | 50 completed bars | INSUFFICIENT_HISTORY | A |
| U12 | bars in reverse order | sorted; recorded; same result | A |
| U13 | next_page_token not null | all pages fetched, or INCOMPLETE_RESPONSE | A |
| U14 | BUY while long; EXIT while flat (**fixture-backed**) | NO_ACTION (CF-2) | A |
| U15 | invocation at T_d + 200 s | same cycle_id; no proposal past the cutoff (R13) | A |
| U16 | **restated:** for any issued ≤ approval_deadline, expires_at ≤ T_d + 180 s < T_d + 300 s; never two live authorizations | holds | B |
| U17 | the response includes a bar with t + 360 s > T_d | excluded and recorded | A |
| U18 | identical candles, varied quotes | identical S20, S50, D and signal | A |
| U19 | a slot-i cycle is still active at T_d(i+1) | CYCLE_OVERRUN(i) written by the successor; slot i+1 runs normally | A |
| U20 | a bar in a pending Stage B proposal's window changes on re-fetch | authorization invalidated | B |
| U24 | v tokens `0`, `0.0`, `0e0`, `-0`, `0.00000001` | first four zero_volume; all retained | A |
| U25 | tokens whose float sums differ from the exact sums; exponents | exact D; no float present | A |
| U78 | bar with t + 360 s = T_d, and with T_d one ns earlier | included / excluded | A |
| U84 | a confirmed bar disappears from the response | DATA_GAP (if in the window) plus a revision note | A |
| U85 | `60000.0` → `60000.00` | SOURCE_REVISION (pending), then confirm | A |
| U87 | inexact operation; long mantissa; large and small exponents; NaN or Infinity token | trap fires / exact / exact / MALFORMED_VALUE | A |
| U89 | an end-labelled fixture | no bar used before its interval closes (conservative) | A |
| U94 | pagination mutated or a page omitted | INCOMPLETE_RESPONSE | A |

### 14.2 Revision store (R4-1)

| ID | Test | Expected | Stage |
|---|---|---|---|
| U31 | revision outside the 51-bar window / inside it | recorded only / NO_DECISION (SOURCE_REVISION) | A |
| U35 | first cycle ever (empty store) | all bars **BASELINED**, observation count 1; decision proceeds | A |
| U36 | slot 1 OK, slot 2 NO_DECISION, slot 3; a bar revised between 1 and 3 | detected at slot 3 against the store | A |
| U37 | as U36, with slot 2 MISSING | detected | A |
| U38 | slot 2 CYCLE_OVERRUN | detected at slot 3 | A |
| U39 | revision at slot 3 (pending → NO_DECISION); the same bytes at slot 4 | slot 4 confirms and proceeds; revision counted once | A |
| U40 | A → B → A over three cycles | two revisions | A |
| U86 | Stage B re-fetch at (b) or (c) differs from the bound input | authorization invalidated | B |

### 14.3 Time, approval and authorization

| ID | Test | Expected | Stage |
|---|---|---|---|
| U21 | authorization without an approval | refused at issuance and at LP-CONSUME | B |
| U22 | approval after approval_deadline | EXPIRED_UNAPPROVED | B |
| U23 | the quote at LP-CONSUME puts L outside ±1% | authorization dies; no reprice | B |
| U28 | quote dated 1 ns after the checkpoint; age exactly 15 s; age 15 s + 1 ns | fail / pass / fail | A |
| U29 | approval at exactly approval_deadline / + 1 ns | valid / EXPIRED_UNAPPROVED | B |
| U30 | now = expires_at − 1 ns / expires_at | live / not live | B |
| U44 | created = T_d + 5 s | proposal; deadline T_d + 120 s | A, B |
| U45 | created = T_d + 30 s exactly | passes the cutoff (inclusive) | A, B |
| U46 | created = T_d + 30 s + 1 ns | REJECTED (R13); slot QUALIFYING | A, B |
| U47 | created = T_d + 250 s | REJECTED (R13); no SHADOW_EXPIRED after the ceiling | A |
| U48 | issued = approval_deadline | expires_at = T_d + 180 s | B |
| U50 | LP-PRESEND at expires_at − δ_send and + 1 ns; configurations δ_send = 0 and = 60 s | pass / fail; BOUNDARY_FAIL at start-up | B |
| U51 | an order from slot i resting at T_d(i+1) | slot i+1 NO_ACTION / BLOCKED_OPEN_ORDER | B |
| U52 | invocation at exactly T_d(i+1) | belongs to slot i+1 | A |
| U53 | **property:** random created ∈ [T_d, T_d + 300 s) and lawful approval and issuance times | §5.3 invariants 1 to 4 hold; seed recorded | A, B |
| U63 | approval mismatch on each bound field in turn | refused, every time | B |
| U64 | revoked between LP-CONSUME and LP-PRESEND | refused | B |
| U65 | two concurrent LP-CONSUME attempts | exactly one succeeds | B |
| U79 | with t_recv − t_send = 1 s: θ_high = +2 s exactly / + 1 ns; θ_low = −2 s exactly / − 1 ns (§5.6) | pass / BOUNDARY_FAIL | A |
| U90 | approval before the deadline, issuance after it | refused | B |
| U93 | send not begun by sample + δ_send / begun, then exceeded | NOT_SENT / AMBIGUOUS | B |

### 14.4 Quotes, sizing and policy

| ID | Test | Expected | Stage |
|---|---|---|---|
| U33 | a budget exactly divisible; a budget one cent short | q floors; R ≤ $150.00 exactly | A |
| U80 | Q1, Q2, Q3, Q4 and Q5 each failing; and a valid but stale quote | NO_DECISION (QUOTE_INVALID), non-qualifying / REJECTED (R4), qualifying | A |
| U81 | q < min_order_size | REJECTED (R10) | A |
| U82 | cash_available < $150 | budget = cash_available; R ≤ cash_available | A |

### 14.5 Ledger (R4-7)

| ID | Test | Expected | Stage |
|---|---|---|---|
| U32 | a 40% fill; cancel requested; a second proposal; terminal confirmed | reservation per cumulative fill; no change on the request; BLOCKED_OPEN_ORDER; remainder released at terminal | B |
| U54 | the same fill event delivered twice | applied once | B |
| U55 | cumulative filled quantity decreases | DISCREPANCY: halt | B |
| U56 | cancel requested, then a late fill, then terminal | the fill is applied; release only at terminal | B |
| U57 | BTC fee: held_btc += q_f − fee_btc; the L-2 check in USD equivalent | consistent | B |
| U58 | fee above the reserved fee | DISCREPANCY: halt | B |
| U59 | correction or bust event | DISCREPANCY: halt | B |
| U60 | a simultaneous second reservation attempt | refused | B |
| U61 | three fills whose per-fill ceilings sum to R + 2¢ | outstanding ≥ 0 and consistent with the cumulative formula | B |
| U62 | EXIT reservation in BTC; R9 against reserved_btc | correct | B |

### 14.6 Audit, scheduling and chain (R4-2, R4-4, R4-5)

| ID | Test | Expected | Stage |
|---|---|---|---|
| U26 | states `"hold"`, `"HOLD "`, absent, two states, `"OK"` | none qualifies | A |
| U27 | slot 17 absent; slot 23 duplicated; an off-grid record; harness counter falsely 41 | MISSING / DUPLICATE / OFF_GRID; counter mismatch reported | A |
| U34 | a HOLD record whose recomputation from artifacts fails V | NON-QUALIFYING | A |
| U41 | N = 40; records for slots 0 to 24 only | slots 25 to 39 MISSING | A |
| U42 | manifest without `declared_slots`, or N = 29 | not milestone-eligible | A |
| U43 | run 2's records removed from the chain | chain break reported | A |
| U66 | a manifest in the repository but not in the chain, and the reverse | reported | A |
| U67 | a TER with an unknown or missing field | invalid; NON-QUALIFYING | A |
| U68 | an injection with origin SCHEDULED and a valid cycle_id | detected (invocation log and origin); not qualifying | A |
| U69 | the same cycle_id under two manifests | finding | A |
| U70 | one byte of a chain record altered | chain break | A |
| U71 | a V-pass asserted against the wrong raw artifact | recomputation mismatch; NON-QUALIFYING | A |
| U72 | manifest edited after the run | hash mismatch; reported | A |
| U73 | missed tick (no invocation) | MISSING; the invocation log is consistent | A |
| U74 | duplicate wake in the same slot | CONCURRENT_INVOCATION; slot NON-QUALIFYING | A |
| U75 | harness restart mid-run | slots during the downtime MISSING; later slots normal | A |
| U76 | machine sleep, then resume late in a slot | correct slot by §6.2; missed slots MISSING | A |
| U77 | an invocation without a record / a record without an invocation | findings | A |
| U83 | an overrunning old process tries to append after takeover | refused | A |
| U88 | a TER containing a JSON number | schema violation | A |
| U91 | an injection running at a slot boundary | INJECTION_ABORTED; slot unaffected | A |

### 14.7 Boundary

| ID | Test | Expected | Stage |
|---|---|---|---|
| X1 | malformed proposal | REJECTED (R3) | A |
| X2 | unsupported instrument | REJECTED (R1) | A |
| X3 | a proposal built on the previous cycle's snapshot | REJECTED (R4); snapshot mismatch recorded | A |
| X4 | BUY with R = $150.01 | REJECTED (R7) | A |
| X5 | **fixture-backed** ledger with equity $449 / notional over R8 | REJECTED (R12 / R8) | A |
| X6 | **fixture-backed:** sell exceeding holdings | REJECTED (R9) | A |
| X7 | limit 1.5% off mid | REJECTED (R5) | A |
| X8 | request to a trading host | refused before network I/O; BOUNDARY_VIOLATION_ATTEMPT recorded | A |
| X9 | a broker credential placed (a) in an environment variable, (b) in the harness configuration file | BOUNDARY_FAIL in both cases (the checked scope, §2.2) | A |
| X10 | a downstream step treats a passed shadow proposal as permission to submit | no submit path exists; recorded | A |
| X11 | a fabricated signal | reconstruction finding | A |
| U92 | Branch H: TCP connect to the trading host from the harness process | refused by the host firewall | **not applicable** (Branch H not selected) |

### 14.8 Tests added in R4.2 (all DESIGNED)

| ID | Test | Expected | Stage |
|---|---|---|---|
| U95 | a bars or quote response keyed by a symbol other than `BTC/USD`, or containing an extra symbol | FETCH_FAILED (V1) | A |
| U96 | the first-ever cycle: the V12a → bars fetch → V12b → quote fetch sequence | the order is exactly as §6.4; no quote fetch after a V12b failure | A |
| U97 | clock masking: a data-host offset of +4 s with 2 s of response transit (a point estimate near +2 s) | θ_high > +2 s → BOUNDARY_FAIL | A |
| U98 | an interval centred on 0 with round trip 3 s − 1 ns / exactly 3 s / 3 s + 1 ns | pass / BOUNDARY_FAIL (condition 3) / BOUNDARY_FAIL | A |
| U99 | crash injected after each boundary: invocation-log append; bars stored; V12b; quote stored; bar-store transition; immediately before the CYCLE append; during it; after it | INCOMPLETE (with orphaned artifacts listed) for every point before a completed append; the normal classification after it | A |
| U100 | a bar BASELINED, then a changed tuple, then the same changed tuple again | PENDING (NO_DECISION), then CONFIRMED; observation counts recorded | A |
| U101 | a bar changing on every fetch, A → B → C → D | PENDING throughout; every affected slot NO_DECISION (SOURCE_REVISION) | A |
| U102 | the last slot of a run still holding the token at RUN_CLOSE | CYCLE_OVERRUN appended for it by RUN_CLOSE; classified OVERRUN | A |
| U103 | a slot with both a CYCLE_OVERRUN record and no CYCLE record | OVERRUN, not MISSING (precedence) | A |
| U104 | a proposal whose SHADOW_EXPIRED append is delayed past T_d(i+1) | append refused; the successor writes CYCLE_OVERRUN; classified OVERRUN | A |
| U105 | sizing vectors, with qty_increment 0.0001, f_res 0.0025 and price_increment 1 (the Stage A policy values): (a) L 59850, budget 150.00 → q 0.0025, R 150.00 (exact cost 149.9990625; the cent ceiling rounds up); (b) L 59850, budget 149.99 → q 0.0024, R 144.00 (the budget step changes q); (c) ask 60663.76 → L 60663, budget 150.00 → q 0.0024, R 145.96 (the floor changes q; cost 145.955178); (d) L 100000, budget 150.00 → q 0.0014, R 140.35 (exact, no rounding) | exactly these values (COMPUTED by Claude with exact rationals) | A |
| U106 | t_recv < t_send | BOUNDARY_FAIL (condition 2) | A |
| U107 | `Date` absent; `Date` unparseable | BOUNDARY_FAIL (condition 1), both cases | A |
| U108 | one TER per terminal path in §10.4's table | each validates against the closed schema, with the stated `null` and NOT_EVALUATED values | A |
| U109 | (a) a malformed CYCLE_OVERRUN record; (b) a CYCLE record and a CYCLE_OVERRUN record for the same slot | (a) integrity finding, row 1; (b) CONFLICT, row 2 | A |
| U110 | an EXIT fixture: shadow BTC 0.0030, passing proposal | shadow_reserved_btc = q_exit until SHADOW_EXPIRED, then 0 | A |

**Fixture-backed tests** (U14, X5, X6, and every test using a fixture ledger) are labelled as such. Their results are **not** live-data evidence (*Gemini B2-07*).

**Freeze scope:** tests whose Stage column contains "A" (including "A, B") are in the Stage A freeze. Tests marked "B" only are Stage B draft.

**Reserved and unused IDs:**
- U49 is subsumed by U30.
- The R3 IDs U44 to U53 are reused here with the recovery-document meanings.

---

## 15. UNVERIFIED / CONDITIONAL / UNBOUNDED register

Scope: **A** = Stage A freeze; **B** = Stage B draft.

| ID | Scope | Item | Label | Blocks |
|---|---|---|---|---|
| U-D1 | A | keyless access over repeated requests | OBSERVED once | — (Stage A evidence) |
| U-D4 | A | 5Min bar revision behaviour; finality | UNVERIFIED | bounds claims |
| U-D5 | A | how bar prices with 3 or 4 decimals are derived | UNVERIFIED | — |
| U-D6 | A | gap frequency; behaviour under load | UNVERIFIED | — |
| U-D7 | A | bar labelling (start vs end) | DOCUMENTED; not established by the probe | — (conservative rule) |
| U-D8 | A | `end` parameter semantics | UNVERIFIED | — (handled by V2, V6, V7) |
| U-T1 | A | Task Scheduler settings and behaviour | UNVERIFIED | the first run (U73 to U77) |
| U-T2 | A | accuracy of the data host's clock against UTC | UNVERIFIED; the 2 s bound is relative to it | timing claims stay CONDITIONAL (§5.6) |
| U-I1 | A | process- or host-level isolation | **not established** (Branch C) | — (disclosed limitation, §2.3) |
| U-I2 | A | broker credentials in stores outside the checked scope (§2.2) | **not excluded** | — (disclosed limitation) |
| U-D9 | A | how long a continuously changing bar keeps slots blocked | UNBOUNDED (fail-closed) | — |
| A-CLK | A | the data host generates its `Date` header between t_send and t_recv | ASSUMED (§5.6) | timing claims |
| A-CLK2 | A | the harness wall clock does not step during the bars request | ASSUMED (§5.6); only steps larger than the round trip are detected | timing claims |
| U-O2 | A | slots needed to reach run_length ≥ 30 | UNBOUNDED | — |
| U-O4 | A | a shared misreading of R4.1 by the harness and the FD-6 script | UNBOUNDED (common mode) | — |
| U-V1, U-V2 | B | price increment; quantity increment and minimum | UNVERIFIED | the first order |
| U-V3 | B | paper fee rate, asset and maker/taker; the fill/activity id field | UNVERIFIED | the first order |
| U-V4 | B | paper fills relative to displayed size | UNVERIFIED | — |
| U-V5, U-V6 | B | account configuration; metadata readable with paper keys | UNVERIFIED (dashboard $500.00 cash OBSERVED by screenshot only) | the first order |
| U-V7 | B | COID semantics | DOCUMENTED | the first order (CF-7 sequence) |
| U-G1, U-G2 | B | approver authentication; σ and δ_send | UNVERIFIED | Stage B |
| U-G3 | B | G7-I8 known false; G7-I5 not established | disclosed limitation | claim language |
| U-O1 | B | Stage B reconstruction plus review within W = 90 s | UNVERIFIED | Stage B |
| U-O3 | B | time to the first BUY signal | UNBOUNDED (market-dependent) | the milestone date, not a gate |

---

## 16. Open items register (deliverable D4)

### 16.1 Closed since R4

| ID | Closed by |
|---|---|
| OI-01 | v1 blob verified byte-exactly (`eb76d8a2…`) |
| OI-02 to OI-05 | v2 (RC-25a to RC-25d accepted) |
| OI-06 | v2 (Branch C) |
| OI-07 | v2 (2 s bound) |
| OI-13 | v2 (wrapper) |

### 16.2 Open

| ID | Scope | Issue | Why it matters | If unresolved | Decision-maker | Blocks |
|---|---|---|---|---|---|---|
| OI-09 | A | coverage: §2, §13 and the claim limits need a clean review | review independence | those areas rest on one reviewer | Gemini B review, then the founder | **Stage A freeze** |
| OI-16 | A | review status: R4.1 reviewed by Gemini B and GPT; R4.2 closure-checked by both; **R4.2a closure check pending** | the freeze must rest on reviewed text | the freeze would rest on unreviewed corrections | GPT and Gemini B; founder | **Stage A freeze** |
| OI-18 | A | **R4-11 as implemented:** decision record v2 accepts "\|offset_estimate\| ≤ 2 s". R4.2 and R4.2a enforce it as an **interval** check plus a < 3 s round-trip ceiling (§5.6), which is stricter than the original point estimate | the decision's wording names a measurement that no longer exists | founder: confirm in writing that the interval check implements R4-11 | **Stage A freeze** |
| OI-08 | A | Stage A never exercises the long-position branches, R8 or R12 on live data (no shadow fills) | coverage of the policy on live inputs | those branches are evidenced only by tests and injections | founder: accept the limitation at the Stage A exit | Stage A exit (acceptance) |
| OI-14 | A | FD-5 harness build | implementation authority | no Stage A evidence | founder, after the Stage A freeze | implementation |
| OI-10 | B | FD-4 TIF | order lifetime; the $1-increment BUY-below-ask consequence (§7.2) bears on reaching a fill | Stage B text incomplete | founder | Stage B freeze |
| OI-11 | B | FD-G13, FD-G16, FD-G17, FD-G18 | Stage B controls | Stage B cannot be authorized | founder (FD-9) | Stage B freeze |
| OI-12 | B | FD-8 paper-key custody | the Stage B pre-flight needs keys | no pre-flight | founder | Stage B |
| OI-15 | B | who independently reconstructs the BUY lifecycle (FD-6 covers Stage A cycles only) | the milestone requires an independent reconstruction | the milestone cannot be met | founder | Stage B freeze |
| OI-17 | B | GPT's critical G-01 (the ledger) and the other Stage B findings: rewritten in §8 but unreviewed | the exposure-limit mechanism | Stage B freeze | reviewers; founder | Stage B freeze |

---

## 17. Review integrity and coverage record

- **Incidents:** RI-2026-11-25-01 (SF-1 to SF-3 disclosed to both reviewers before review) and RI-2026-11-25-02 (annex S2 disclosed to GPT). Recorded in the recovery document; nothing is removed.

**Coverage by area:**

| Area | R3 round | R4.1 Stage A round |
|---|---|---|
| §3 to §7, §8.1, §10, §11 and the tests (R3 counterparts) | GPT (exposed) and Gemini B (clean, R3 text only) | **new review**: Gemini B (clean) and GPT |
| §2 stage boundary; §13 claims; claim limits; G-07 claim language | **GPT only** | **new review**: Gemini B (closes OI-09) and GPT |
| the closure-package register; R1 §3 and §6 retention | GPT only | R1 §3 and §6 are now integrated as §9.1, §9.7 and §9.8 (Stage B draft), so they are **not** in this round; the register is superseded by R4.1 itself |
| §8.2 to §8.6, §9, §12 (Stage B) | GPT (R3 counterparts) | **not reviewed this round** (OI-17) |

**Independence:**
- Gemini account B has seen **R3 only**: no reconciliation, no R4, no GPT review.
- GPT has seen everything up to the reconciliation and R4.
- **Agreement between them is not independent verification.**

*End of R4.2a candidate.*
