# SL-PT-001 Stage A Design v0.1: SMA-20/50 v0.1 first shadow cycle (D1 to D7)

**Date:** 2026-11-25 | **Author:** Claude | **Dispatch:** "SL-PT-001: First Deterministic Strategy Adoption and Stage A Preparation"
**Classification:** DESIGN ONLY. **Stage A implementation is not authorized.** No connection to Alpaca, no credentials, no orders, no change to EAR. **No market value in this document is real**; the illustrative TER in §3.3 is marked ILLUSTRATIVE and contains invented numbers.
**Labels:** DERIVED / COMPUTED / OBSERVED / ASSUMED / CONDITIONAL / UNVERIFIED / UNBOUNDED. **Nothing here is COMPUTED or OBSERVED from market data.** OBSERVED is used only for documentation statements, and marked as such.
**Naming:** the dispatch says "Trade Event Record"; Spec v0.1 says "Trade Evidence Record". **They are the same object, TER.** v0.1 of this design uses the dispatch's term.

**Founder decisions this design surfaces:** SA-FD-1 to SA-FD-8 (§5). Three of them change the strategy's observable behaviour and must be settled before the first actual cycle: SA-FD-1, SA-FD-2 and SA-FD-3.

---

## D1. Strategy definition: SMA-20/50 v0.1 (implementation-independent)

### 1.1 Inputs

- C = the sequence of **completed** 1-hour BTC/USD candles, ordered by start time ascending, with **no gaps** (§2.4).
- Index k denotes the **latest completed candle**.
- close_i is the decimal close price of candle i, **exactly as delivered** (§2.5).

### 1.2 Indicators (exact arithmetic)

- S20(k) = Σ_{i=k−19..k} close_i;  SMA20(k) = S20(k) / 20.
- S50(k) = Σ_{i=k−49..k} close_i;  SMA50(k) = S50(k) / 50.
- **Comparison without division (normative):**
  - SMA20(k) > SMA50(k) ⇔ 5·S20(k) > 2·S50(k);
  - SMA20(k) < SMA50(k) ⇔ 5·S20(k) < 2·S50(k);
  - equality ⇔ 5·S20(k) = 2·S50(k).

  Every comparison uses exact decimal (rational) arithmetic on the delivered decimal strings. **No binary floating point is used anywhere in the decision path.** This is DERIVED: it removes rounding as a source of spurious crossovers or missed equality.
- **Minimum history:** 51 consecutive completed candles (k−50 .. k), because the previous-period SMA-50 needs candle k−50.

### 1.3 Crossover semantics (literal reading of the founder's definition; normative for v0.1)

Let D(k) = 5·S20(k) − 2·S50(k), whose sign equals the sign of SMA20 − SMA50. Then:

| Signal | Condition (founder text → formal) |
|---|---|
| **BUY** | "crosses from at-or-below to above": **D(k−1) ≤ 0 ∧ D(k) > 0** |
| **EXIT** | "crosses from at-or-above to below": **D(k−1) ≥ 0 ∧ D(k) < 0** |
| **HOLD** | otherwise, including D(k) = 0 |

**Mutually exclusive and exhaustive (DERIVED):** BUY needs D(k) > 0 and EXIT needs D(k) < 0, so both cannot hold together. HOLD is the complement.

### 1.4 Edge cases (each one is a unit test in D6)

| ID | Situation | Literal-rule result | Note |
|---|---|---|---|
| EC-1 | D: + → 0 → + (touch from above, no real cross) | the second step gives **BUY** (D(k−1) = 0 ≤ 0, D(k) > 0) | **a spurious re-entry signal.** The literal rule treats a touch as a cross. **SA-FD-1** |
| EC-2 | D: − → 0 → − | the second step gives **EXIT** | the mirror of EC-1. **SA-FD-1** |
| EC-3 | D: − → 0 → + | step 1 HOLD; step 2 **BUY** | a genuine cross through equality, detected one candle late (at the step that leaves 0) |
| EC-4 | D: 0 → 0 | HOLD | — |
| EC-5 | D(k−1) undefined (fewer than 51 candles) | **no decision**: state INSUFFICIENT_HISTORY | not HOLD; it is recorded as a data failure |
| EC-6 | a gap anywhere in k−50..k | **no decision**: state DATA_GAP | §2.4 |

**SA-FD-1 options:**
- (a) **literal** (as above; v0.1 default, because it is what was approved);
- (b) **strict-regime**: track the last non-zero sign of D, and signal only when the non-zero sign flips. That ignores touches (EC-1 and EC-2 become HOLD; EC-3 still BUYs).

This design does not choose between them.

### 1.5 From signal to proposal (intelligence #0's output; needs SA-FD-2)

The strategy emits a **signal**. A **proposal** exists only when the mapping below creates one. **A signal is never an authorization and never an order.**

| Signal | Shadow position | Proposal (v0.1 default; SA-FD-2) |
|---|---|---|
| BUY | flat | BUY proposal (sizing and price per §1.6) |
| BUY | long | **none**: NO_ACTION (the signal is recorded) |
| EXIT | long | EXIT proposal: sell the entire held quantity |
| EXIT | flat | **none**: NO_ACTION |
| HOLD | any | none |

The alternative to SA-FD-2 is to emit the proposal anyway and let policy reject it. That exercises more policy rules but produces predictable, uninformative rejections.

### 1.6 Price and size (the strategy does not define them; SA-FD-3)

Proposed defaults, so that a proposal is complete:
- **Limit price:**
  - BUY limit = the **ask** from the decision-time quote;
  - EXIT limit = the **bid**;
  - in both cases rounded to the instrument's price increment, **toward the conservative side** (BUY down, EXIT up).
  - The ±1% band (R5) is then checked against the mid.
- **BUY quantity** = floor_to_increment( min($150 − current BTC notional at ask, available cash) / (limit × (1 + fee)) ).
- **EXIT quantity** = the entire held quantity.

The fee rate is **ASSUMED** at 0.25% (Spec v0.1 §5; unverified for paper). **SA-FD-3** is to approve or replace these rules.

---

## D2. First-cycle data contract

### 2.1 Source (single source; the limitation is stated, not hidden)

- **Alpaca crypto market data**, location `us`. Two calls per cycle:
  - **(a)** historical bars, BTC/USD, timeframe `1Hour`, a window covering at least 56 hours ending at the decision time (51 needed, plus margin to detect gaps and the latest bar);
  - **(b)** the latest quote, BTC/USD, used for the limit price and the ±1% band.
- **Keyless access is UNVERIFIED.** Alpaca's SDK guidance says no keys are needed for crypto data, but the REST reference lists 401 responses. **The first fetch decides it.** If a key turns out to be required, Stage A is **blocked** (credentials are prohibited by the dispatch), and that becomes a founder decision (SA-FD-6).
- **Single-source limitation:** the decision data and any later shadow-outcome data come from one provider. A wrong feed is invisible to cross-checking. **No second source is added** (per the dispatch).

### 2.2 Required fields

| From | Field | Use |
|---|---|---|
| bars | `t` (RFC-3339 timestamp) | the candle start (§2.3) |
| bars | `c` | close (the decision input) |
| bars | `o`, `h`, `l`, `v`, `n`, `vw` | kept raw; `v` = 0 marks a quote-derived bar (§2.6) |
| response | `next_page_token` | must be null, or every page must be fetched |
| quote | `t`, `bp`, `ap`, `bs`, `as` | freshness (R4); limit price; mid = (bp + ap) / 2 |

A missing required field → **INCOMPLETE_RESPONSE**: no decision.

### 2.3 Timestamp and completed-candle rules

- **Convention (OBSERVED in documentation, UNVERIFIED for hourly crypto bars):** a bar is labelled by its **start** time and covers [t, t + 1h). Verify on the first fetch: every `t` must lie exactly on an hour boundary, in UTC.
- **Decision time** T_d is the cycle's wall-clock time in UTC, recorded at fetch.
- **Completed:** a bar with start t is completed iff **t + 1h + settle ≤ T_d**, with settle = **5 minutes** (default; SA-FD-4). Bars not yet completed are **discarded and recorded** as excluded. They are never used.
- **Expected latest candle:** k must have t_k = floor_hour(T_d − settle) − 1h. If the newest completed bar is older than that → **STALE_SERIES**: no decision.
- **Ordering:** sort by `t` ascending after fetch. A response that is not already sorted is **recorded** (it is evidence about the source), then sorted.

### 2.4 Missing and duplicate candles

- **Duplicate:** two bars with the same `t`.
  - Identical content → keep one and record a DUPLICATE_IDENTICAL note.
  - Different content → **DATA_CONFLICT**: no decision.
- **Missing:** any hour in [t_k − 50h, t_k] without a bar → **DATA_GAP**: no decision. **No interpolation or forward-filling** in v0.1, because a filled close would be an invented value.
- Documentation states that a bar with no trades gets prices from quotes (§2.6). So genuine gaps may be rare, but that is **UNVERIFIED**.

### 2.5 Precision

- **Parse closes as decimal strings exactly as delivered** (a JSON number literal → a decimal, never a float).
- Record the raw literal and the parsed decimal.
- Stored SMA values are rounded **only for display** (8 decimal places, round-half-even). **Decisions use the exact sums (D1 §1.2).**

### 2.6 Quote-derived bars (documented source behaviour, recorded per candle)

When a bar has no trades, its prices come from quotes (documentation). The TER records, for each of the 51 candles, whether `v` = 0. The SMA is then partly an average of **quote levels**, not trades. **This is recorded, not corrected.** It affects what the signal *means*, not its determinism.

### 2.7 Revision of historical bars

- **UNVERIFIED** for hourly crypto bars. The documented case is late trades recalculating a just-closed minute bar about 30 seconds later.
- **Control (v0.1):**
  - (a) the settle margin (§2.3);
  - (b) a **re-fetch check**: at the next cycle, re-fetch the previous cycle's 51-candle window and compare byte-wise canonical forms. Any difference is recorded as **SOURCE_REVISION** (OBSERVED evidence about the source), and the earlier TER is annotated through a **new event**, never edited.

### 2.8 Failure behaviour (all are "no decision"; none is HOLD)

| Condition | State | Proposal |
|---|---|---|
| HTTP error, timeout, malformed JSON | FETCH_FAILED | none |
| missing required field | INCOMPLETE_RESPONSE | none |
| a further page indicated but not fetched | INCOMPLETE_RESPONSE | none |
| fewer than 51 candles | INSUFFICIENT_HISTORY | none |
| a gap | DATA_GAP | none |
| a conflicting duplicate | DATA_CONFLICT | none |
| latest completed candle not the expected one | STALE_SERIES | none |
| quote older than 60 s at evaluation (R4), or an absent quote | the signal is computed, but **any proposal → REJECTED (R4)** | rejected |

**HOLD means "data valid, no cross".** A data failure is never reported as HOLD.

---

## D3. TER v0.1

### 3.1 Storage (from Spec v0.1 §2.1; unchanged)

- An append-only `events.jsonl`, hash-chained.
- Raw artifacts are stored by SHA-256 under `artifacts/`.
- The TER is the fold of a cycle's events and is never edited.

### 3.2 Canonical schema (JSON; every value carries a label)

```
TER v0.1 {
  ter_id:            UUIDv7                                   [OBSERVED-at-creation]
  ter_schema:        "TER-0.1"
  experiment:        "SL-PT-001", stage: "A-shadow"
  cycle: {
    decision_time_utc, harness_version (git commit), host_note   [OBSERVED]
  }
  strategy: { id: "SMA-20/50", version: "0.1", params:{fast:20, slow:50, interval:"1Hour", settle_min:5},
              semantics: "literal" | "strict-regime" (SA-FD-1), mapping: SA-FD-2 rule id }
  instrument:        "BTC/USD"
  data: {
    source: { provider:"alpaca", api:"market-data v1beta3 crypto", loc:"us", endpoints:[...], auth:"none"|"key" },
    bars_request:  { url_with_params, sent_at_utc },          [OBSERVED]
    bars_raw_sha256, bars_raw_artifact,                        [OBSERVED]
    quote_request, quote_raw_sha256, quote_raw_artifact,       [OBSERVED]
    candles_used: [{t, c_literal, c_decimal, v, n}] x51 (k-50..k)   [OBSERVED]
    candles_excluded: [{t, reason:"incomplete"|"duplicate-identical"}]
    checks: { hour_aligned, sorted_on_arrival, gaps:[], duplicates:[], page_complete, latest_expected_t, latest_actual_t,
              quote_age_s, quote_derived_bar_count }          [COMPUTED]
    input_snapshot_sha256  (canonical JSON of candles_used + quote) [COMPUTED]
  }
  indicators: {
    S20_k, S50_k, S20_k1, S50_k1 (exact decimals),             [COMPUTED]
    SMA20_k, SMA50_k, SMA20_k1, SMA50_k1 (display, 8dp HALF_EVEN), [COMPUTED]
    D_k, D_k1 (= 5*S20 - 2*S50)                                 [COMPUTED]
  }
  signal: { value:"BUY"|"EXIT"|"HOLD"|none, condition_text, data_state:"VALID"|<failure state> } [COMPUTED]
  proposal: null | { proposal_id, side, qty (base units), limit, tif:"GTC", origin:"intelligence#0"|"INJECTED",
                     sizing_rule, price_rule }                 [COMPUTED]
  exposure: {
    before: { cash, cash_reserved, btc_held, btc_reserved, btc_notional_at_bid, equity },   [COMPUTED from shadow ledger]
    after_if_authorized: { same fields },                      [COMPUTED]
    caps: { per_instrument:150, portfolio:300, min_equity:450 } [ASSUMED working parameters]
  }
  authorization: null | {
    policy_version:"P-0.1", policy_sha256,                     [OBSERVED]
    rules: [{id:"R1".."R14", result:"PASS"|"FAIL"|"N/A", values}],  [COMPUTED]
    decision:"AUTHORIZE_SHADOW"|"REJECT", auth_id, issued_at, expires_at, reject_codes  [COMPUTED]
  }
  lifecycle: { terminal_state: one of
     NO_DECISION:<state> | HOLD | NO_ACTION | REJECTED | AUTHORIZED_SHADOW→SHADOW_EXPIRED },  [COMPUTED]
  boundary: { order_endpoint_reachable:false, credentials_present:false }   [OBSERVED by harness self-check; UNVERIFIED by independent test]
  labels_note:  "COMPUTED values are reproducible from data.* artifacts; they are not verified market facts."
  prev_event_hash, event_hash
}
```

**Terminal states:**
- An authorized shadow proposal ends at **SHADOW_EXPIRED** at its TTL. Stage A never consumes or submits.
- The shadow-outcome resolution (Spec v0.1 §6 step 6) is a **separate later event**, kept out of the first-cycle scope (D7).

### 3.3 Illustrative example (ILLUSTRATIVE: invented values, not market data)

```json
{
  "ter_id": "ILLUSTRATIVE-0000",
  "ILLUSTRATIVE": "All numbers below are invented to show structure. They are not BTC prices and must never be read as data.",
  "strategy": {"id": "SMA-20/50", "version": "0.1", "semantics": "literal"},
  "instrument": "BTC/USD",
  "data": {
    "candles_used": "[51 entries omitted; illustrative closes were 100.00 for k-50..k-1 and 103.00 for k]",
    "checks": {"hour_aligned": true, "gaps": [], "duplicates": [], "quote_age_s": 4},
    "input_snapshot_sha256": "<illustrative>"
  },
  "indicators": {
    "S20_k1": "2000.00", "S50_k1": "5000.00", "D_k1": "0.00",
    "S20_k":  "2003.00", "S50_k":  "5003.00", "D_k":  "9.00",
    "SMA20_k": "100.15000000", "SMA50_k": "100.06000000"
  },
  "signal": {"value": "BUY", "condition_text": "D(k-1)=0 <= 0 and D(k)=9 > 0 (literal rule; EC-3-type, from equality)", "data_state": "VALID"},
  "proposal": {"side": "BUY", "limit": "103.10", "qty": "<per sizing rule>", "origin": "intelligence#0"},
  "exposure": {"before": {"cash": "500.00", "btc_held": "0"}, "caps": {"per_instrument": 150}},
  "authorization": {"policy_version": "P-0.1", "decision": "AUTHORIZE_SHADOW", "rules": "[R1..R14 results omitted]"},
  "lifecycle": {"terminal_state": "AUTHORIZED_SHADOW -> SHADOW_EXPIRED"},
  "boundary": {"order_endpoint_reachable": false, "credentials_present": false}
}
```

**Check of the illustrative arithmetic (DERIVED):**
- k−1: S20 = 20 × 100 = 2000; S50 = 50 × 100 = 5000; D = 5·2000 − 2·5000 = 0.
- k: S20 = 19 × 100 + 103 = 2003; S50 = 49 × 100 + 103 = 5003; D = 10015 − 10006 = 9 > 0.
- So the result is BUY under the literal rule.

---

## D4. First-cycle walkthrough

1. **Pre-flight (boundary self-check).**
   - The harness verifies that no Alpaca trading credential is present in its environment.
   - It verifies that its HTTP client allowlist contains **only** the market-data host.
   - Any order or trading host (paper or live) is **not in the allowlist**, so requests to it are refused **before** any network I/O.
   - The result is recorded in `boundary`.
   - On failure: abort the cycle with BOUNDARY_FAIL.
2. **Fetch.**
   - Record T_d.
   - GET the bars (window ≥ 56 h), then GET the latest quote.
   - Store the raw bytes and SHA-256 of each, plus the request URLs and timestamps.
3. **Validate** (§2.3 to §2.8): hour alignment, ordering, duplicates, gaps, completeness, the expected latest candle, page completeness, quote age. Any failure → a NO_DECISION TER (step 9).
4. **Snapshot.**
   - Build the canonical JSON of the 51 candles used plus the quote.
   - Compute input_snapshot_sha256 and store it as an artifact.
5. **Compute** S20 and S50 at k and k−1 exactly; then D(k) and D(k−1); then the display SMAs.
6. **Signal** per D1 §1.3, under the founder-selected semantics (SA-FD-1).
7. **Proposal** per D1 §1.5 (SA-FD-2) and §1.6 (SA-FD-3). HOLD or NO_ACTION → no proposal.
8. **Exposure and policy** (only if there is a proposal).
   - Compute before and after against the shadow ledger (initial: cash $500.00, BTC 0).
   - Evaluate P-0.1 rules R1 to R14 (Spec v0.1 §4). R14 is evaluated in shadow form (fresh quote) or N/A, and recorded.
   - The result is AUTHORIZE_SHADOW or REJECT. **AUTHORIZE_SHADOW confers no permission to submit anything** (dispatch §7).
9. **Write the TER.**
   - Append the events: data, indicators, signal, proposal, authorization and lifecycle.
   - Hash-chain them.
   - Commit and push (manual in v0.1).
10. **Terminal state.** One of:
    - NO_DECISION:<reason>;
    - HOLD;
    - NO_ACTION;
    - REJECTED;
    - AUTHORIZED_SHADOW (then SHADOW_EXPIRED at TTL).

    **A HOLD first cycle is a successful first cycle.**
11. **Reconstruction** (independent).
    - A reviewer takes only the artifacts plus D1 and D2.
    - With their own script, they recompute the snapshot hash, the four sums, D(k), D(k−1), the signal, the proposal and the rule results.
    - They compare these with the TER. **Any difference is a finding.**

---

## D5. Stage A readiness checklist

| Item | Status |
|---|---|
| Strategy formalized, with exact arithmetic and edge cases | **READY** (design) |
| Data contract and failure states | **READY** (design) |
| TER v0.1 schema | **READY** (design) |
| Walkthrough and boundary self-check design | **READY** (design) |
| Test plan (D6) | **READY** (design; **no test executed**) |
| Keyless access to Alpaca crypto data | **UNVERIFIED** (contradictory documentation; the first fetch decides) |
| Hourly bar start-time convention and hour alignment | **UNVERIFIED** for 1Hour crypto bars (documented for minute bars) |
| Historical hourly bar revision behaviour | **UNVERIFIED** (re-fetch check designed) |
| Gap frequency in hourly crypto bars | **UNVERIFIED** |
| JSON number precision as delivered (decimal places) | **UNVERIFIED** (the first fetch shows it) |
| Fee rate used in sizing | **ASSUMED** 0.25% |
| BTC/USD price and quantity increments and minimum order | **UNVERIFIED** (needs Alpaca asset metadata; that endpoint may require trading credentials. **If so, it is blocked in Stage A and must be supplied manually from documentation**, SA-FD-7) |
| Harness code | **BLOCKED**: implementation not authorized (PT-FD-11) |
| Independent reconstructor identified | **REQUIRES FOUNDER DECISION** (PT-FD-10 / SA-FD-8) |
| SA-FD-1 crossover semantics (literal vs strict-regime) | **REQUIRES FOUNDER DECISION** |
| SA-FD-2 signal-to-proposal mapping when the position mismatches | **REQUIRES FOUNDER DECISION** |
| SA-FD-3 limit price and sizing rules | **REQUIRES FOUNDER DECISION** |
| SA-FD-4 settle margin (5 min default) | **REQUIRES FOUNDER DECISION** (default proposed) |
| SA-FD-5 where the harness runs (founder's PC vs elsewhere) and the cycle trigger (manual vs scheduler) | **REQUIRES FOUNDER DECISION** |
| SA-FD-6 what to do if the data API requires a key | **REQUIRES FOUNDER DECISION** (it would be a credential, so prohibited now) |
| SA-FD-7 the source of instrument metadata if keyless access is unavailable | **REQUIRES FOUNDER DECISION** |
| SA-FD-8 the independent reviewer for reconstruction | **REQUIRES FOUNDER DECISION** |

---

## D6. Test plan (designed; nothing executed)

### 6.1 Deterministic unit tests (pure functions; synthetic inputs only)

**Notation:** the closes are synthetic. A tuple (D(k−1), D(k)) can be produced directly by the test fixture, or by constructing closes.

| ID | Test | Input | Expected (DERIVED) |
|---|---|---|---|
| U1 | no crossover | D(k−1) = −4, D(k) = −1 | HOLD |
| U2 | bullish crossover | D(k−1) = −3, D(k) = +2 | BUY |
| U3 | bearish crossover | D(k−1) = +3, D(k) = −2 | EXIT |
| U4a | equality now | D(k−1) = −1, D(k) = 0 | HOLD |
| U4b | leaving equality upward (EC-3) | D(k−1) = 0, D(k) = +1 | BUY (both semantics) |
| U4c | touch from above (EC-1) | D sequence +1, 0, +1 | literal: BUY at the 3rd step; strict-regime: HOLD |
| U4d | touch from below (EC-2) | −1, 0, −1 | literal: EXIT; strict-regime: HOLD |
| U4e | exact-equality precision | closes chosen so that the float sums differ but the exact sums are equal (for example several closes of `0.1`, `0.2`, `0.3` combined so that 5·S20 = 2·S50 exactly) | D = 0 exactly → HOLD. **A float implementation would fail this test**, which is its purpose |
| U5 | incomplete candle exclusion | T_d = 10:03 UTC, bars up to start 10:00 → the 10:00 bar is incomplete (and the 09:00 bar is also within settle: 09:00 + 1h + 5 min = 10:05 > 10:03) | the latest completed bar is 08:00; **expected latest = floor(10:03 − 5 min) − 1h = 08:00** → VALID; the 09:00 and 10:00 bars are excluded and recorded |
| U6 | missing candle | 51-hour window with one hour absent | DATA_GAP, no signal |
| U7 | duplicate candle | the same `t` twice, identical / different | identical: proceed, with a note / different: DATA_CONFLICT |
| U8 | stale data | (a) the latest completed bar is 2 h older than expected; (b) the quote is 61 s old | (a) STALE_SERIES; (b) signal computed, proposal REJECTED R4 |
| U9 | replayed snapshot | re-run with the stored artifacts of a past cycle and a past T_d | a byte-identical TER body (except ter_id and the chain fields), **flagged as a REPLAY run and never appended as a new decision** |
| U10 | determinism | the same artifacts, 100 runs; different process, OS locale, timezone | identical indicators, signal, proposal and rule results |
| U11 | insufficient history | 50 candles | INSUFFICIENT_HISTORY |
| U12 | unsorted response | the bars delivered in reverse order | sorted, recorded, same result as sorted input |
| U13 | pagination | a response with next_page_token not null | all pages fetched, or INCOMPLETE_RESPONSE |
| U14 | position mapping (SA-FD-2) | BUY while long; EXIT while flat | NO_ACTION, with the signal recorded |

### 6.2 Adversarial proposals (injected; labelled `origin: INJECTED`; Scoreboard B only)

| ID | Injection | Expected |
|---|---|---|
| X1 | malformed proposal (missing qty; non-numeric limit; unknown side) | REJECTED_MALFORMED (R3) |
| X2 | unsupported instrument (ETH/USD, while deferred; DOGE/USD) | REJECTED R1 |
| X3 | stale evidence: a proposal built on the snapshot of the previous cycle | REJECTED R4 (and the snapshot-hash mismatch is recorded) |
| X4 | unauthorized exposure: a BUY whose notional is $151 | REJECTED R7 |
| X5 | portfolio breach / below-equity buy (the shadow ledger manipulated in the fixture to equity $449) | REJECTED R8 / R12 |
| X6 | a sell exceeding holdings while flat | REJECTED R9 |
| X7 | limit 1.5% above mid | REJECTED R5 |
| X8 | **shadow-boundary bypass:** the harness is asked to send a request to the paper trading host | refused by the allowlist **before network I/O**; BOUNDARY_VIOLATION_ATTEMPT recorded |
| X9 | **shadow-boundary bypass:** a trading credential is placed in the environment | the pre-flight detects it → BOUNDARY_FAIL; no cycle runs |
| X10 | **authorization misuse:** a downstream step treats AUTHORIZE_SHADOW as permission to submit | there is no submit capability in Stage A; the attempt is recorded as X8 |
| X11 | fabricated signal: the proposal claims BUY when the recomputed D says HOLD | reconstruction finding (the signal is recomputed from the artifacts and does not match) |

**Expected results are DERIVED from the design. None is OBSERVED.** X8 and X9 test the *harness's own* boundary. They say **nothing** about G-07 execution enforcement (dispatch §7).

---

## D7. Implementation recommendation (for the founder's decision; implementation is not authorized here)

**Minimum to run the first shadow cycle:**
1. **One fetch-and-decide script** (Python; standard library plus `decimal`), on the founder's machine or another approved host (SA-FD-5). It covers:
   - the pre-flight self-check;
   - two GETs to the market-data host only;
   - raw-artifact storage;
   - validation;
   - exact SMA arithmetic;
   - signal, mapping, sizing and policy evaluation (P-0.1 as a hashed JSON file);
   - TER event append with a hash chain.
2. **A unit-test file** covering U1 to U14 and X1 to X11 on synthetic fixtures, run **before** the first live-data cycle. Its results are recorded as COMPUTED only when actually executed.
3. **A separate reconstruction script**, written by **someone other than the harness author** (SA-FD-8), reading only the artifacts plus D1 and D2.

**Can stay manual in v0.1:**
- triggering each hourly cycle by hand (the first cycle certainly);
- git commit and push of the event log after each cycle;
- running the reconstruction on the first cycle;
- supplying instrument increments from documentation if metadata needs a key (SA-FD-7).

**Must be deferred:**
- the scheduler and automation (until manual cycles show stable data);
- ETH/USD;
- intelligence #1 (LLM);
- shadow-outcome resolution and Scoreboard A (after a few cycles; not needed for the first decision);
- the re-fetch revision check (from cycle 2, since it needs a previous cycle);
- everything in Stage B and C;
- any G-07 component.

**First-cycle success criterion (restated):**
- one TER whose terminal state, whatever it is (including HOLD or NO_DECISION), is **independently reconstructed** from its artifacts with zero unexplained differences;
- the boundary self-check passes;
- no request goes to any host other than the market-data host.

*End of design v0.1. No implementation, data fetch, test execution, credential or order.*
