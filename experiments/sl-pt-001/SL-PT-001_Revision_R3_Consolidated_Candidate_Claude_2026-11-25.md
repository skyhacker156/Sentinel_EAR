# SL-PT-001 Revision R3: consolidated specification candidate (revised R1)

**Author:** Claude (Specification Lead / ARBITER). **Date:** 2026-11-25.
**Responds to:** the founder dispatch "SL-PT-001 FIRST-TRADE CRITICAL PATH" (2026-11-25), §3 A–F and §10 items 1, 4 and 5.
**Classification:** specification candidate. **NOT FROZEN.** Nothing is implemented.

**What R3 does not do:**
- No test has been executed, and R3 claims none. Every "Expected" result is DERIVED.
- G-07 is not changed. A0.3-13 is integrated exactly as scoped in R1 §3.
- **No implementation, trading or order authority is implied.** The first paper trade is not authorized.

**Companion document:** *SL-PT-001 First-Trade Closure Package* (same date). It holds the section-level supersession register, the GPT finding-to-resolution matrix, the candidate freeze manifest, the critical-path table and the blocker statement.

**Labels:** DERIVED / COMPUTED / OBSERVED / DOCUMENTED / ASSUMED / CONDITIONAL / UNVERIFIED / UNBOUNDED, as in every earlier document. **CANDIDATE** marks a value proposed by Claude that no founder decision covers. Model agreement is not verification.

**Relation to earlier revisions:**
- R3 is the revised R1 named in the dispatch's specification set.
- R3 **replaces R1** (`8cc5168b…`) **and R2** (`851d295b…`) in full.
- R1 remains in the repository as history. R2 was delivered but never reviewed, and is not part of the freeze set.
- Where an earlier SL-PT-001 document conflicts with R3, **R3 governs**. Every earlier provision has an explicit status in the closure package's register.

---

## 1. Founder decision register (deliverable 4)

| ID | Decision | Status | Normative text | Source |
|---|---|---|---|---|
| Baseline | SMA-20/50; BTC/USD only; 5-minute candles; Alpaca paper venue for Stage B; limit orders only; no leverage, shorting or derivatives | **SETTLED** | §2 | dispatch §2 |
| FD-1 | Stage A-0 data probe | **EXERCISED** (2026-11-26T03:13Z; report `f6642894…`) | — | R1 §7 |
| FD-2 | crossover semantics | **ACCEPTED** | §2.2 | dispatch §2 |
| FD-3 | open-order handling: no new proposal while an order, partial fill, unresolved authorization or ambiguous prior order remains open → `NO_ACTION / BLOCKED_OPEN_ORDER` | **ACCEPTED** | §8 R16 | dispatch §2 |
| FD-3 (residual) | BUY while already long → NO_ACTION; EXIT while flat → NO_ACTION | **CANDIDATE** (the Readiness D2 default; the founder's acceptance text covers open orders only) | §2.3 | Readiness D2; U14 |
| FD-4 | sizing and price handling | **ACCEPTED WITH CLARIFICATION**. One wording conflict (CF-1) needs founder confirmation and **blocks Stage B text only** | §6, §7 | dispatch §2 |
| FD-4 (TIF) | GTC with Sentinel cancel, or IOC | **DEFERRED to the Stage B package** (Stage A sends no orders) | §6.5 | — |
| FD-5 | Stage A harness build | **CONDITIONAL** (dispatch §5): the FD-1 record; reviews reconciled; criticals resolved or founder-accepted in writing; freeze authorized | — | dispatch §5 |
| FD-6 | independent reconstruction: GPT writes the blind script **after the freeze**, from the frozen set only, with its hash recorded before seeing any TER; the founder runs it on five pre-seeded random cycles; differences are findings | **ACCEPTED** | §9.4 | dispatch §2 |
| FD-6 (scope) | the same blind script also performs the **milestone slot audit** (§9.3) | **CANDIDATE** (an extension of FD-6; founder confirmation needed) | §9.3 | — |
| FD-7 | where the harness runs, and **the cycle trigger** (manual vs a minimal timer) | **OPEN**. It **blocks the freeze**, because it sets the harness scope and decides whether M1-1 is reachable (§5.4) | §5.4 | Readiness D2 |
| FD-8 | paper-key custody | **DEFERRED** (Stage B) | — | Readiness D2 |
| FD-9 | Stage B authorization, including FD-G13, FD-G16, FD-G17, FD-G18 | **DEFERRED** | §7 | dispatch §2 |
| Policy values | R8 portfolio cap $300; R12 drawdown stop $450 | **CANDIDATE** (Spec v0.1 values marked FD but never decided; R8 does not bind under BTC-only) | §8 | Spec v0.1 §4 |
| Settle | 60 s | **CANDIDATE** (amendment v0.2; the founder chose 5Min, not the settle value) | §3.4 | amendment v0.2 |

**Obsolete OPEN labels removed:**
- FD-2, FD-3, FD-4 and FD-6 are no longer OPEN anywhere.
- SA-FD-1 to SA-FD-8 are retired; their mapping is in the closure package register.

---

## 2. Strategy (normative)

### 2.1 Unchanged from Stage A Design D1 and amendment v0.2

- Inputs: completed 5-minute BTC/USD candles (§3).
- S20(k) and S50(k) are means of the last 20 and 50 completed closes ending at candle k.
- The comparison uses exact sums. D(k) = 5·ΣC₂₀(k) − 2·ΣC₅₀(k), and sign(D) = sign(S20 − S50), **DERIVED** (multiply both sides by 100).
- 51 completed candles are required.
- The edge cases are those in Stage A Design D1 §1.4 (RETAINED).

### 2.2 Crossover (FD-2, ACCEPTED)

- **BUY** iff D(k−1) ≤ 0 ∧ D(k) > 0.
- **EXIT** iff D(k−1) ≥ 0 ∧ D(k) < 0.
- **HOLD** otherwise. In particular, D(k) = 0 is never a crossover.
- *Consequence (DERIVED; recorded, not a defect):* the touch sequences +1, 0, +1 and −1, 0, −1 yield BUY and EXIT respectively at the third step. This is the literal reading the founder accepted, so tests U4c and U4d expect it.

### 2.3 Signal to action mapping

| Signal | Shadow position (Stage A) / reconciled position (Stage B) | Result |
|---|---|---|
| BUY | flat | a proposal (§6) |
| BUY | long | NO_ACTION, signal recorded (CANDIDATE, FD-3 residual) |
| EXIT | long | a proposal (§6) |
| EXIT | flat | NO_ACTION, signal recorded |
| any | an open, partial, AMBIGUOUS or unresolved order or authorization exists | NO_ACTION / BLOCKED_OPEN_ORDER (FD-3; R16) |
| HOLD | any | HOLD |

**Flat** := held BTC < the venue minimum order size. That minimum is UNVERIFIED (§13). Dust below it is recorded and does not make the position "long".

### 2.4 Quote independence (normative)

- The signal is a pure function of completed candle closes.
- **No quote field enters S20, S50, D or the signal** (test U18).
- Quotes are used only for proposal pricing and the policy checks (§6, §8).

---

## 3. Data contract (normative; dispatch §3 D)

### 3.1 Source

- Two keyless GETs per cycle to `data.alpaca.markets`:
  - BTC/USD `5Min` bars, with a window of at least 60 candles ending at T_d;
  - the latest BTC/USD quote.
- Keyless access: **OBSERVED, one probe**.
- The single-source limitation stands (Stage A Design §2.1).

### 3.2 Raw artifacts and exact values

1. The raw response bytes and headers are stored **before** parsing, with their SHA-256.
2. **Every numeric value is converted to an exact decimal (or an exact rational) from the original JSON number token text.**
   - No binary floating-point value may exist in signal inputs, price, quantity, fee, reservation or policy calculations, in the harness or in the reconstructor.
   - ILLUSTRATIVE only, not an implementation instruction: a parser hook that passes the token text to a decimal constructor.
3. Exponent forms are valid and are converted exactly.
4. The token text of o, h, l, c, v and vw is kept per bar in the TER.
5. Revision comparison uses token text (§3.7). Display rounding is 8 dp, round-half-even; it is display only.

### 3.3 Timestamps (normative)

- Every timestamp (bar `t`, quote `t`, harness instants) is converted to an **integer number of nanoseconds since the Unix epoch, UTC**. The conversion is exact.
- Fractional seconds of up to 9 digits are kept without truncation. OBSERVED: the quote `t` carries 9 fractional digits.
- A timestamp without a zone designator, with more than 9 fractional digits, or failing RFC-3339 parsing is **malformed** (§3.8).

### 3.4 Completed candles and the forming bar (normative; P-3, U17)

- Settle = 60 s (CANDIDATE).
- A bar with start t is **completed** iff t + 300 s + 60 s ≤ T_d.
- Every other bar, including the forming bar the API returns (OBSERVED, P-3), is **excluded**. It is recorded with its token text and never used.
- **Expected latest candle:** t_exp = floor₃₀₀ₛ(T_d − 60 s) − 300 s, in integer nanoseconds.

### 3.5 Validation set V (all must pass; any failure → NO_DECISION with the sub-reason shown)

| ID | Check | Failure sub-reason |
|---|---|---|
| V1 | HTTP 200; well-formed JSON; every required field present (Stage A Design §2.2) | FETCH_FAILED / INCOMPLETE_RESPONSE |
| V2 | `next_page_token` null, or every page fetched | INCOMPLETE_RESPONSE |
| V3 | every `t` parses (§3.3) and lies on a 300 s boundary | FETCH_FAILED (MALFORMED_VALUE) |
| V4 | `t` unique. Byte-identical duplicates collapse with a DUPLICATE_IDENTICAL note; differing duplicates fail | DATA_CONFLICT |
| V5 | arrival order is recorded, then bars are sorted ascending by `t` | — (never fails) |
| V6 | incomplete bars excluded (§3.4) | — (never fails) |
| V7 | the newest completed bar has t = t_exp | STALE_SERIES |
| V8 | no gap: every 300 s step in [t_exp − 250 min, t_exp] has a bar (51 bars) | DATA_GAP |
| V9 | numeric validity: finite; every price > 0; v ≥ 0 (§3.8) | FETCH_FAILED (MALFORMED_VALUE) |
| V10 | at least 51 completed candles | INSUFFICIENT_HISTORY |
| V11 | no SOURCE_REVISION inside the current 51-candle window (§3.7) | SOURCE_REVISION |
| V12 | the boundary self-check passes (Stage A Design D4: endpoint allowlist, no credential present) and the clock offset was measured (§4.4) | BOUNDARY_FAIL (a separate terminal state, not NO_DECISION) |

The quote is **not** in V. A missing or stale quote is a policy failure (R4) after a valid signal (§8).

### 3.6 Zero-volume and quote-derived bars (normative)

- **zero_volume ⇔ decimal(v) = 0, compared numerically.** This covers `0`, `0.0`, `0e0` and `-0`. Text matching is not acceptable.
- Zero-volume bars are DOCUMENTED as quote-derived. They are **retained in the signal window and classified** (`zero_volume: true` with the token text). They are never filtered or interpolated.
- **Only the founder can change this,** because filtering would change the strategy.
- The probe's 7/72 figure was a text-pattern count and may be an undercount. Its numeric re-count is a closure-package evidence step (§13 U-D3).

### 3.7 Revision of accepted bars (normative; fail-closed)

- Each cycle compares, by token text, every bar it has in common with the previous cycle's accepted window.
- A difference → a SOURCE_REVISION event. **The original bytes are kept; nothing is replaced.**
- The current cycle returns NO_DECISION (SOURCE_REVISION) if the revised bar lies inside its own 51-candle window (V11).
- Any Stage B proposal or authorization whose input contains the revised bar is **invalidated**.
- *Change from R1, flagged CF-3:* R1 only annotated a revision in Stage A. R3 fails closed, per dispatch §3 F.

### 3.8 Malformed values

- Covers: a non-finite or non-numeric token where a number is required; a price ≤ 0; v < 0; a malformed timestamp.
- Result: NO_DECISION (FETCH_FAILED, detail MALFORMED_VALUE). There is no new terminal state.

### 3.9 Price and quantity increments

- **Price increment: UNVERIFIED.** DOCUMENTED as 1; contradicted by OBSERVED quote cents (P-1).
- **Quantity increment and minimum: UNVERIFIED.** DOCUMENTED as 0.0001; contradicted by the 1/price statement.
- **No order increment is inferred from quote or bar precision.**
- **Stage A** rounds with the support-table values, recorded as `increment_source: support_table_DOCUMENTED` and `increment_status: UNVERIFIED`. Shadow sizing is therefore **CONDITIONAL**.
- **Stage B** reads the asset metadata at pre-flight. A missing field or any mismatch with the policy file → **STOP, no order**.

---

## 4. Time and comparison semantics (normative; dispatch §3 F)

### 4.1 Representation

- All instants are integer nanoseconds since the Unix epoch, UTC (§3.3). Durations are integer nanoseconds.
- Money is exact decimal USD. Quantity is exact decimal BTC.
- **No comparison in §3 to §9 is evaluated on a floating-point or rounded value.**

### 4.2 Clocks (R1 §1, preserved; issuance follows approval)

| Symbol | Definition |
|---|---|
| T_d | close_t + 60 s |
| created | `proposal_created_at`: when the proposal is computed (≈ T_d) |
| approval_deadline | created + 120 s |
| approved_at | when the founder's approval record is committed (Stage B) |
| issued | `authorization_issued_at`: ≥ approved_at; **only after a valid approval** |
| expires_at | min(issued + 60 s, created + 180 s) |
| ceiling | created + 180 s |

### 4.3 Exact comparison table (normative)

| Condition | True iff | Boundary |
|---|---|---|
| bar completed | t + 360 s ≤ T_d | inclusive |
| quote fresh at checkpoint c | 0 ≤ (c − quote.t) ≤ 15 s | both inclusive; a quote dated **after** c fails (CF-4) |
| approval timely | approved_at ≤ approval_deadline | inclusive |
| authorization issuable | timely approval ∧ issued ≤ approval_deadline (CF-5) ∧ every §8 check passes at checkpoint (b) | — |
| authorization live | now < expires_at | **strict**: at expires_at it is expired |
| LP-PRESEND passes | now ≤ expires_at − δ_send, **with δ_send > 0** (FD-G18) | G-07 Draft 0.3 text |
| cycle overrun | the cycle has no terminal record committed before T_d(i+1) = T_d(i) + 300 s | strict |
| shadow expiry | SHADOW_EXPIRED is recorded at exactly the ceiling | — |
| order cancel (Stage B) | the cancel request for any unfilled remainder is sent no later than the ceiling | inclusive |

### 4.4 Time source

- **Stage A:** the harness clock. Each cycle records an offset estimate (HTTP `Date` header of the bars response minus the harness receipt time; 1 s resolution). This is CANDIDATE.
  - Offset not measurable (header absent or unparseable) → BOUNDARY_FAIL (V12).
  - **Stage A imposes no skew bound;** it records only.
- **Stage B:** time source, skew bound σ and δ_send are **DEFERRED to FD-G18**.

---

## 5. Cycle identity, overrun and scheduling

### 5.1 Rules preserved from R1 §2

- cycle_id = (instrument, t_exp). A cycle_id already in the log is never processed again.
- One active cycle per instrument. A second invocation → CONCURRENT_INVOCATION.
- Overrun (§4.3) → CYCLE_OVERRUN, and **any proposal from that cycle is blocked.** The next cycle processes only its own t_exp; intervening slots are recorded SKIPPED.
- A cycle never processes two candles and never back-fills a decision.

### 5.2 Slot identity (DERIVED)

- An invocation anywhere in [T_d(i), T_d(i+1)) selects t_exp = T_d(i) − 360 s.
- So lateness within a slot does not change the cycle_id. An invocation at or after T_d(i+1) belongs to slot i+1.

### 5.3 Fail-closed summary

Overrun, a data failure (V1 to V11), a revision (§3.7), a boundary failure (V12) and an ambiguous order (R16) each yield **no proposal**. None is ever reported as HOLD.

### 5.4 Scheduling (FD-7, OPEN; blocks the freeze)

- M1-1 needs 30 consecutive qualifying slots, about 2.5 h, and a missing slot breaks the run (§9).
- Hand triggering must hit every slot inside a 300 s window, 30 times in a row.
- Options for the founder (no default from R3):
  - **(i)** a minimal local timer inside the FD-5 harness scope. It only invokes the cycle, carries no logic of its own, and logs every invocation;
  - **(ii)** hand triggering, accepting that M1-1 may take many attempts (UNBOUNDED);
  - **(iii)** change the milestone. This reopens a founder decision and GPT's adopted strict rule.

---

## 6. Proposal, sizing and reservation contract (normative; FD-4; dispatch §3 E)

### 6.1 Ledgers

| Term | Definition |
|---|---|
| Cash | exact USD |
| BTC | exact |
| Reservation | (auth_id or shadow proposal_id, amount, state) |
| cash_available | cash − Σ amount of every reservation not yet released |

**Stage A:**
- Stage A uses a **shadow ledger**. Its opening cash is declared in the run manifest (§9.3).
- *CANDIDATE:* $500.00, the OBSERVED paper-account equity (founder screenshot). Buying power is UNVERIFIED.
- The reconciled (Stage B) ledger is never written by Stage A.

### 6.2 BUY sizing (exact)

| Symbol | Definition |
|---|---|
| L | the limit price (§6.3) |
| f_res | 0.0025: the **reservation** fee rate. DOCUMENTED tier-1 taker; whether it applies on paper, and whether maker or taker, is UNVERIFIED. It is a conservative upper bound, **not** a booked fee |
| budget | min($150.00, cash_available) |
| q | floor to the quantity increment of budget / (L × (1 + f_res)) |
| R | ceil to the cent of q × L × (1 + f_res): the reserved spend |

**Requirements:**
- R ≤ $150.00 (**FD-4: maximum total reserved spend including fees**).
- R ≤ cash_available.
- q ≥ the minimum order size; otherwise the proposal is REJECTED under R10.
- **No order is ever sized against displayed top-of-book size** (FD-4; §6.6).

### 6.3 Limit price (CF-1 governs Stage B)

- **Stage A:** L = the ask (BUY) or the bid (EXIT) of the quote fresh at checkpoint (a), rounded to the price increment in the conservative direction (BUY down, EXIT up). The increment is CONDITIONAL (§3.9).
- **Stage B (CANDIDATE reading of FD-4, CF-1):**
  - L and q are derived from the proposal-time fresh quote;
  - they are shown to the founder and **bound by the approval** (A0.3-13);
  - the **fresh quote required at authorization issuance** (checkpoint b) **validates** L. It does **not** re-derive it;
  - after approval nothing is repriced or resized. Any check failure kills the authorization.

### 6.4 EXIT sizing

- q_exit = floor to the quantity increment of the **reconciled held BTC** (Stage B), or the shadow BTC (Stage A). It is never the ordered BUY quantity.
- DOCUMENTED: the buy fee is taken in the received asset. UNVERIFIED on paper.
- R9 applies.

### 6.5 Order lifetime and partial fills (Stage B; recorded now)

- TIF is DEFERRED to the Stage B package (FD-4 TIF):
  - **GTC** with a Sentinel cancel request at the ceiling; or
  - **IOC**.
  - FOK is excluded, because its support is DOCUMENTED-contradictory.
- **Partial fills must be explicitly accepted** (FD-4):
  - the approval record binds `partial_fill_accepted: true | false`;
  - **false** → no order can be constructed, because no all-or-none TIF is verified. The proposal is REJECTED under R2 and recorded;
  - **true** → each reported fill is recorded with its quantity, price, fee and fee asset, and the TER documents the partial outcome.

### 6.6 Reservation lifecycle (no double allocation)

| Event | Reservation effect |
|---|---|
| Stage A: a proposal passes policy at checkpoint (a) | shadow reservation R created; released at SHADOW_EXPIRED |
| Stage B: authorization issued | R created (R6 and R7 already checked at checkpoint b) |
| authorization dies unconsumed (EXPIRED_UNAPPROVED, expiry, invalidation, any check failure at c or d) | released, citing the event |
| fill (partial or full) | reduced by ceil to the cent of q_f × L × (1 + f_res); the booked spend is the **reported** q_f × p_f plus any reported USD fee |
| cancel **requested** | **no change** |
| terminal state **confirmed** by reconciliation (filled, canceled, expired, venue-rejected) | the remainder released |
| AMBIGUOUS | **fully reserved** until reconciled; it blocks proposals (R16); no resubmission (FD-G16, DEFERRED) |

**Invariants (DERIVED from R11, R16 and this table):**
- at most one unreleased BUY reservation exists;
- Σ unreleased reservations + booked spend ≤ opening cash;
- every release cites terminal evidence or an expiry event.

**Falsifiers:**
- two simultaneously unreleased reservations;
- a release without cited evidence;
- a booked fee greater than its reserved fee. This is a DISCREPANCY (L-2): halt.

### 6.7 Displayed size

- The displayed bid and ask sizes at every checkpoint are **recorded, as information only**.
- They are not a total-liquidity estimate, not a fill guarantee, and **not a cap**. The ≈ $60 observation is not a $60 cap (FD-4).
- Paper-fill behaviour relative to displayed size is UNVERIFIED.

---

## 7. Approval and authorization (Stage B; specified now, FD-9 DEFERRED)

1. **No approval means no authorization.** K3 issues only on an approval record (A0.3-13, R1 §3) whose bound fields **exactly** equal the proposal's.
   - The bound fields are those of R1 §3, plus `partial_fill_accepted`, TIF, R and the fee estimate.
   - The approval must satisfy approved_at ≤ approval_deadline.
2. At issuance (b), LP-CONSUME (c) and LP-PRESEND (d):
   - a **new** quote is fetched and §4.3 freshness checked;
   - R4, R5, R6, R7, R9, R10, R11 and R16 are re-evaluated **with the bound L and q**;
   - any FAIL → the authorization dies (released, §6.6). **No repricing and no parameter change** (FD-4).
3. LP-CONSUME also requires the approval record to still exist unrevoked (A0.3-13).
4. **Falsifier:** any ACTIVE or CONSUMED authorization lacking a matching, timely approval record. Tests U21 and U22.
5. **Approver authentication is UNVERIFIED** (FD-G13).
6. **Approval of the experiment is not approval of an order.** Each order needs its own record (dispatch §9).
7. **Claim limit:** the first paper trade must not be represented as satisfying G7-I5 or G7-I8 (dispatch §8; R1 §6).

---

## 8. Policy P-0.2 (policy inventory; replaces Spec v0.1 §4 and Readiness D3 A-6/A-7)

`policy/P-0.2.json`, which is to be created at build time, must encode exactly this table. Its hash is recorded in every decision.

| Rule | Check (exact; §4) | Value | Stage | Status |
|---|---|---|---|---|
| R1 | instrument allowlisted | BTC/USD only | A, B | settled |
| R2 | limit order; TIF allowlisted; `partial_fill_accepted` = true | TIF per FD-4 TIF (deferred) | B (A: limit only) | settled / deferred |
| R3 | proposal schema complete and parseable | — | A, B | retained |
| R4 | quote fresh at each checkpoint (§4.3) | 15 s | A: (a); B: (a) to (d) | retained |
| R5 | \|L − mid\| ≤ 0.01 × mid, mid = (bid + ask) / 2 of the checkpoint quote | ±1% | A, B | retained |
| R6 | R ≤ cash_available | — | A, B | retained |
| R7 | R ≤ $150.00 total reserved spend, including fees | $150 | A, B | **FD-4** |
| R8 | total notional at mark + R ≤ $300 | $300 | A, B | CANDIDATE |
| R9 | q_exit ≤ held − reserved BTC | — | A, B | retained |
| R10 | q ≥ the venue minimum; q and L on the venue increments | UNVERIFIED (§3.9) | A: conditional; B: metadata | retained |
| R11 | at most one open authorization or order per instrument | — | A, B | retained |
| R12 | equity < $450 → reject BUY | $450 | A, B | CANDIDATE |
| R13 | the §4.2 clocks | 120 s / 60 s / 180 s | B (A: ceiling only) | replaces the 5-minute TTL |
| R14 | re-check at (b), (c) and (d) per §7 item 2 | — | B | replaces the "fresh snapshot" wording |
| R15 | EXIT only while long (§2.3); q_exit per §6.4 | — | A, B | from Readiness A-6 |
| R16 | **FD-3:** no proposal while any order is open or partial, any authorization is unresolved, or any prior order is AMBIGUOUS → NO_ACTION / BLOCKED_OPEN_ORDER | — | A (vacuous: no orders), B | **FD-3** |

---

## 9. Milestone counter and independent audit (normative; dispatch §3 B)

### 9.1 Closed terminal-state set

Each scheduled-slot record carries exactly one `terminal_state` from this set:
- HOLD, NO_ACTION, REJECTED, SHADOW_EXPIRED;
- NO_DECISION (with a §3.5 sub-reason), CYCLE_OVERRUN, SKIPPED, CONCURRENT_INVOCATION, BOUNDARY_FAIL.

### 9.2 Qualifying slots (positive allowlist)

**Only these four states can qualify,** and each only when every condition in its row holds:

| State | Additional conditions (all required) |
|---|---|
| HOLD | V1 to V12 passed ∧ D(k−1) and D(k) computed from 51 validated candles ∧ signal = HOLD |
| NO_ACTION | V1 to V12 passed ∧ D computed ∧ signal ∈ {BUY, EXIT} ∧ mapped to NO_ACTION by §2.3 |
| REJECTED | V1 to V12 passed ∧ D computed ∧ signal ∈ {BUY, EXIT} ∧ a proposal constructed ∧ ≥ 1 rule of R1 to R16 failed, with its rule code recorded |
| SHADOW_EXPIRED | V1 to V12 passed ∧ D computed ∧ a proposal constructed ∧ all policy rules passed at (a) ∧ SHADOW_EXPIRED recorded at the ceiling |

**Every other record does not qualify.** That includes:
- a state outside the set, an absent state, more than one state, or a wrong case or spelling;
- a record that fails its hash-chain check;
- a record missing a required condition field.

**Injected proposals** (`origin: INJECTED`) are not slot records. They never qualify and never occupy a slot.

*Note for review (CF-6):* REJECTED by R4, a stale or missing quote, qualifies, because the quote is not a signal input (§2.4) and a correct policy rejection is a successful cycle.

### 9.3 Scheduled-candle ledger and independent milestone audit

1. **Run manifest:** committed to the repository before a run's first slot. It contains the instrument; T_d(0), which must be :MM:00 + 60 s; the opening shadow cash; and the hashes of the frozen specification set, the harness and the policy file.
   - **Every committed manifest must appear in the Stage A exit report.** A run cannot be dropped.
2. **Scheduled-candle ledger, built by the auditor and never by the harness:** slots i = 0 … n with T_d(i) = T_d(0) + 300 s · i. Slot i expects cycle_id(i) = (BTC/USD, T_d(i) − 360 s).
   - n is the last slot with T_d(n+1) ≤ the run's declared end. A slot still in progress is not judged.
3. **Classification per slot:**

| Records with cycle_id(i) | Classification |
|---|---|
| exactly one | QUALIFYING if it meets §9.2; otherwise NON-QUALIFYING (with its state) |
| none | **MISSING** (non-qualifying; an M1-2 completeness finding) |
| more than one | **DUPLICATE** (non-qualifying; a finding) |

   A record whose cycle_id matches no slot is **OFF_GRID**: a finding, never qualifying.

4. **Denominator:** every slot of every manifest. **Missing slots stay in the denominator.**
5. **Counter (DERIVED):** run_length = the longest sequence of consecutive slots within one manifest, all QUALIFYING. **M1-1 is met iff run_length ≥ 30.** There are no reset semantics to interpret: any non-qualifying slot simply ends a sequence.
6. **The harness's own counter, if any, is not evidence.** The audit reports it and any mismatch.
7. **Owner:** the FD-6 blind script, written by GPT after the freeze and hashed before any TER is seen. This is a CANDIDATE scope extension (§1). The founder runs it.
8. **Falsifiers:**
   - a slot with no record that the audit fails to report as MISSING;
   - a non-allowlisted state counted;
   - a disagreement between the audit and the founder's own slot enumeration for any manifest.

### 9.4 Rest of M1 (Spec v0.1 §9; R1 §5)

- M1-1: run_length ≥ 30, **and** ≥ 5 runtime injected proposals, each rejected by the intended rule.
- M1-2 to M1-5 and M1-7: RETAINED.
- **M1-6 (FD-6):** the blind reconstruction of **five cycles** drawn by a seed recorded before the run.
- **Test-suite coverage** (R1 §5) is separate from the runtime injections: at least one **executed** pass case and fail case per rule R1 to R16, plus every test in §11, before the first live-data cycle.

---

## 10. Claims (R1 §5 retained)

**What M1 can support:**
- distinct completed candles were processed;
- the decision computation is deterministic on recorded inputs;
- the specified bad data was rejected in the observed slots;
- the record is complete and reproducible for the sampled cycles;
- the injected proposals were rejected by the intended rules;
- an independent reconstruction of the sample was obtained.

**What M1 cannot support:**
- profitability, returns or significance;
- robustness across regimes, or reliability over days;
- the truth of the market data;
- broker behaviour or execution quality;
- **any G-07 execution-enforcement property.**

Thirty cycles are not thirty trades.

---

## 11. Test inventory (designed; **none executed**)

| Set | IDs | Source | Status in R3 |
|---|---|---|---|
| Strategy | U1–U4e, U7, U9, U10, U12, U13 | Stage A Design §6.1 | retained; U4c and U4d expect the literal results (FD-2) |
| Position mapping | U14 | Stage A Design | retained (CANDIDATE mapping) |
| 5Min timing | U5, U6, U8, U11 | amendment v0.2 §3 | retained; U8(b) means a quote 16 s old |
| Cadence | U15 | amendment v0.2 | retained |
| Clocks | U16 | amendment v0.2 | **re-expressed:** expires_at = min(issued + 60 s, created + 180 s) < T_d + 300 s; no two authorizations live together |
| R1 additions | U17–U23 | R1 §8 | retained |
| R2 additions | U24 (zero-volume forms), U25 (decimal tokens, float trap), U26 (allowlist), U27 (slot audit) | R2 §7 | retained; U26 now checks the §9.2 conditions |
| New | **U28** | R3 | quote `t` 1 ns after the checkpoint → R4 FAIL; age exactly 15 s → pass; 15 s + 1 ns → FAIL |
| New | **U29** | R3 | approval at exactly approval_deadline → valid; deadline + 1 ns → EXPIRED_UNAPPROVED |
| New | **U30** | R3 | authorization at now = expires_at → not live; LP-PRESEND at expires_at − δ_send → passes; 1 ns later → fails |
| New | **U31** | R3 | revision inside the current window → NO_DECISION (SOURCE_REVISION); outside it → recorded only |
| New | **U32** | R3 | reservation: partial fill of 40%, then cancel requested → reservation unchanged; terminal confirmed → remainder released; a second proposal during it → BLOCKED_OPEN_ORDER |
| New | **U33** | R3 | sizing at a boundary: budget exactly divisible, and budget one cent short → q floors; R ≤ $150.00 holds exactly |
| New | **U34** | R3 | a HOLD record missing the V-pass evidence → NON-QUALIFYING in the audit |
| Adversarial | X1–X11 | Stage A Design §6.2 | retained, with the R3 clock and freshness values |

---

## 12. TER field delta

As in R2 §1.5, plus:
- `validation{V1…V12}` with a result for each;
- `offset_estimate_ns`;
- `displayed_sizes[]` for each checkpoint;
- `reservation{id, amount, state, events[]}`;
- `partial_fill_accepted`, recorded in Stage B.

---

## 13. UNVERIFIED / UNBOUNDED register (deliverable 5)

| ID | Item | Label | What would settle it | Blocks the first paper order? |
|---|---|---|---|---|
| U-D1 | keyless access on repeated requests | OBSERVED once | the Stage A run itself | no (Stage A evidence) |
| U-D2 | 5Min start-labelling and per-bar uniqueness, ordering and gaps in the probe | **CONDITIONAL**: COMPUTED only from first/last `t` and the count | the closure-package local check on `bars_body.json` | no (Stage A V3–V8 re-establish it per cycle) |
| U-D3 | the true zero-volume count in the probe (7/72 may be low) | UNVERIFIED | the same local check | no |
| U-D4 | revision behaviour of 5Min bars | UNVERIFIED | the Stage A SOURCE_REVISION record | no; it bounds claims |
| U-D5 | how bar prices with 3 or 4 decimals are derived | UNVERIFIED | documentation or vendor statement | no |
| U-D6 | gap frequency, behaviour under load, time-of-day effects | UNVERIFIED | Stage A runs | no |
| U-V1 | **price increment** (P-1) | UNVERIFIED | Stage B asset metadata | **yes** |
| U-V2 | **quantity increment and minimum order** | UNVERIFIED (contradictory) | Stage B asset metadata | **yes** |
| U-V3 | **fee on paper** (rate; maker or taker; fee asset) | UNVERIFIED | Stage B fills plus documentation | **yes** (the reservation bound must be ≥ the actual fee) |
| U-V4 | paper fills relative to displayed size; total depth | UNVERIFIED | Stage B observation | no (partial fills accepted and handled) |
| U-V5 | **account: buying power, 1×, shorting off** | UNVERIFIED (equity $500 OBSERVED) | Stage B pre-flight read | **yes** |
| U-V6 | asset metadata readable with paper keys | UNVERIFIED | Stage B pre-flight | **yes** |
| U-V7 | COID uniqueness and query-by-COID on paper | DOCUMENTED | the Stage B test, which needs a paper order (CF-7) | **yes** |
| U-V8 | corrections or busts on paper | UNVERIFIED | — | no (Stage C) |
| U-G1 | **approver authentication** | UNVERIFIED | FD-G13 | **yes** |
| U-G2 | **time source, σ, δ_send** | UNVERIFIED | FD-G18 | **yes** |
| U-G3 | G7-I8 | **known false** on the founder's machine; I5 not established | — (a disclosed limitation) | no, if disclosed (dispatch §8) |
| U-O1 | Stage B reconstruction-before-approval (Readiness D7 step 2) fits inside 120 s | UNVERIFIED | Stage B dry run | **yes** |
| U-O2 | slots needed to reach run_length 30 | **UNBOUNDED** (depends on FD-7 and data quality) | — | indirectly |
| U-O3 | time to the first BUY signal | **UNBOUNDED** (market-dependent; not a defect) | — | indirectly |

---

## 14. Conflicts and review points (flagged; none silently resolved)

| ID | Issue | R3 position | Who decides |
|---|---|---|---|
| **CF-1** | FD-4 says the limit price "is derived from a fresh quote at authorization issuance". R1, A0.3-13 and dispatch §3 F and §9 say approval precedes issuance and binds the limit price, with no repricing after approval. Taken literally, both cannot hold | **CANDIDATE reading (§6.3):** the price is derived at proposal creation and bound at approval; the issuance quote validates it (matching dispatch §3 E's "fresh quote **required** at authorization issuance"). **Alternative:** a non-consumable pre-approval authorization priced at issuance, then activated by approval. That alternative moves A0.3-13 from issuance to activation and adds a K3 state, which R3 judges outside the scoped G-07 change. *R2's S-2 is replaced by this entry.* | **founder** (blocks Stage B text only) |
| CF-2 | FD-3 acceptance covers open orders; the BUY-while-long and EXIT-while-flat mapping is still a CANDIDATE | carried as CANDIDATE | founder |
| CF-3 | revision fails closed in Stage A (stricter than R1) | adopted per dispatch §3 F; this can lengthen the time to M1 | reviewers; founder |
| CF-4 | a future-dated quote fails R4 with zero tolerance until FD-G18 sets σ | fail-closed; in Stage A it yields REJECTED, which still qualifies | reviewers |
| CF-5 | issuance must also fall within approval_deadline. Otherwise an approval at 119 s could be issued later | added | reviewers |
| CF-6 | REJECTED(R4) qualifies for the counter | adopted (§9.2 note) | reviewers |
| **CF-7** | Readiness D7 precondition: the "Stage C tests for query-by-COID and duplicate COID executed on paper" require paper orders **before** the first paper order | **flagged:** either those test orders run under the full Stage B governance and are themselves the first orders, or the precondition becomes a post-first-order test. That is a Stage B package decision | founder (Stage B) |
| CF-8 | the Stage A offset estimate (§4.4) is a CANDIDATE mechanism | recorded only; no bound | reviewers |

*End of R3.*
