# SL-PT-001 R4: consolidated specification candidate

**Author:** Claude (Specification Lead / ARBITER). **Date:** 2026-11-25.
**Responds to:** the founder dispatch "R4 CONSOLIDATION" (2026-11-25).
**Classification:** design documentation only.
- **CANDIDATE. NOT FROZEN. NOT IMPLEMENTED. NOT VERIFIED.**
- No test has been executed.
- No implementation, credential, trading-host connection or order is authorized by this document.

**What R4 is:** one complete specification for SL-PT-001.
- It integrates R3 (blob `203b4bf5…`), the R3 review reconciliation (corrections R4-1 to R4-16), the founder decision record and the probe evidence.
- A reader needs no other SL-PT-001 document to follow the system.
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

## 1. Founder decision register (deliverable D3)

**Source limitation:** R4 uses the decision text Claude gave the founder for commit (`experiments/sl-pt-001/SL-PT-001_Founder_Decision_Record_2026-11-25.txt`). Claude **has not inspected the committed blob.** The founder should confirm that the committed text matches this table (§16, OI-01).

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
| FD-5 | the Stage A harness build: **CONDITIONAL**, not authorized | §16 |
| FD-8 | paper-key custody: **DEFERRED** | §16 |
| FD-9 | Stage B (FD-G13, FD-G16, FD-G17, FD-G18): **DEFERRED** | §9 |

### 1.2 Pending founder decisions (open; R4 does not decide them)

| ID | Item | R4 treatment |
|---|---|---|
| RC-25a | R8 portfolio cap **$300** | CANDIDATE value in §7.3 |
| RC-25b | R12 drawdown stop **$450** | CANDIDATE value in §7.3 |
| RC-25c | settle interval **60 s** | CANDIDATE value in §4.6 |
| RC-25d | opening shadow cash **$500.00** | CANDIDATE value in §8.1 |
| R4-9 | Stage A host-firewall egress restriction and process-boundary test | both branches specified (§2.3); none chosen |
| R4-11 | Stage A clock bound \|offset\| ≤ 2 s | CANDIDATE in §5.6 |
| FD-4 TIF | GTC with a Sentinel cancel, or IOC | DEFERRED to Stage B (§9.5) |
| Coverage | the areas reviewed by GPT only (§17) | open |

---

## 2. Scope and stage boundary

### 2.1 Stages

| Stage | What it is | Status |
|---|---|---|
| **A** (shadow) | keyless, read-only market data; the full decision and policy pipeline; shadow proposals only; no orders, no credentials | specified here; **not built** (FD-5) |
| **B** (paper) | governed paper orders through G-07 controls | rules specified here **for review only**; DEFERRED (FD-9) |
| **C** | corrections, busts, duplicate-COID tests | out of scope |

### 2.2 Stage A properties (normative)

- **No credential:** no broker credential exists in the harness environment. The pre-flight verifies this (V12).
- **Allowlisted hosts:** the harness HTTP client contacts only `data.alpaca.markets`. Requests to any other host are refused before network I/O.
- **No submit capability:** Stage A has no code path that submits, cancels or queries orders.
- **Claim limit:** Stage A results never establish any G-07 property (G7-I1 to I10).

### 2.3 Network isolation boundary (R4-9; **OPEN**, founder disposition)

R4 specifies both branches. Neither is chosen.

**Branch H (host-level):**
- a host firewall outbound rule for the harness process allows only the market-data host;
- at each RUN_OPEN, the harness attempts a TCP connection to the trading host; it must be **refused by the host firewall**, which is recorded (test U92);
- feasibility on the founder's machine (hostname versus IP-based rules, DNS changes) is **UNVERIFIED**.

**Branch C (client-level only):**
- isolation is enforced only by the harness's own HTTP allowlist and the absence of credentials;
- every Stage A result then carries this limitation: *"Disconnection from trading is asserted at the HTTP-client level only. Alternate egress paths in the process or host (other libraries, raw sockets, proxies, inherited handles) were not excluded."*
- **Consequence:** Stage A shows that the intended code path is read-only; it does not show that the process could not reach a trading host.

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
- **Settle** = 60 s (**CANDIDATE**, RC-25c).
- A bar with start t is **completed** iff t + 300 s + settle ≤ T_d.
- Every other bar is **excluded**. It is recorded with its token text and never used.
- **Expected newest completed bar:** t_exp = floor₃₀₀ₛ(T_d − settle) − 300 s. With settle = 60 s this equals T_d − 360 s (DERIVED, since T_d − 60 s lies on a 300 s boundary; §6.2).

### 4.7 Validation set V (all must pass)

| ID | Check | Failure → NO_DECISION sub-reason |
|---|---|---|
| V1 | HTTP 200; well-formed JSON; required fields present (bars: t, o, h, l, c, v, n, vw; response: next_page_token) | FETCH_FAILED / INCOMPLETE_RESPONSE |
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
| V12 | pre-flight passed (§6.4) | BOUNDARY_FAIL, a separate terminal state |

- V12 (pre-flight) runs **first**, before any fetch. Its failure → BOUNDARY_FAIL, and no fetch happens.
- V1 to V11 are then evaluated, and **all failures are recorded**.
- The NO_DECISION sub-reason is the **first** failing check, in the order listed.
- The quote is not in V (see §4.11).

### 4.8 Zero-volume bars

- **zero_volume ⇔ the exact value of v = 0.** This covers `0`, `0.0`, `0e0` and `-0`. Text matching is not used.
- Zero-volume bars are DOCUMENTED as quote-derived. They are **retained in the signal window** and flagged with their token text. They are never filtered or interpolated.
- Changing this changes the strategy and is a founder decision.

### 4.9 Revision handling (R4-1)

**Bar store.** The bar store maps (instrument, t) to the **current confirmed** token tuple (o, h, l, c, v, vw, n) and its state.
- It is **not a separate mutable file.** It is the deterministic fold of every CYCLE record in the global chain (§10), across all cycles and runs.
- Any reviewer can rebuild it from the chain.

**Per cycle, for every completed bar fetched:**

| Situation | Action |
|---|---|
| t not in the store | add it as CONFIRMED (a first observation) |
| tuple equals the store's | no change |
| tuple differs from the store's, and no change is pending for t | record a SOURCE_REVISION event (old and new tuples, both kept); t becomes PENDING with the new tuple |
| t is PENDING, and the tuple equals the pending tuple | t becomes CONFIRMED with the new tuple; the revision is recorded once; **not re-counted** |
| t is PENDING, and the tuple differs from both | a new SOURCE_REVISION; PENDING with the newest tuple |
| t was CONFIRMED and is **absent** from this response, while inside the requested range | a SOURCE_REVISION note (disappearance); if inside the 51-bar window, V8 already fails (DATA_GAP) |

**Rules:**
- Comparison is by **token text**, so `60000.0` versus `60000.00` is a revision (U85).
- **V11:** any PENDING bar inside the current 51-bar window → NO_DECISION (SOURCE_REVISION).
- Original bytes are never replaced. Every observation remains in the chain.
- **Anti-lockout (DERIVED):** a revision costs at least one slot. It cannot block more than one slot while the source keeps returning the same bytes.
- **Stage B:** at checkpoints (b) and (c) (§9.3), the 51-bar window is re-fetched and compared with the store. Any difference from the bytes bound in the proposal invalidates the authorization (U86).

**What CONFIRMED means — and does not mean:**
- It means only that **the source returned the same bytes on two fetches.**
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
- the harness wall clock;
- each cycle records `offset_estimate` = (the HTTP `Date` header of the bars response) − (the harness receipt instant). The header has 1 s resolution and truncates, so the estimate's error is in (−1 s, 0] (DERIVED);
- **proposed bound (CANDIDATE, OPEN):** |offset_estimate| ≤ 2 s; otherwise BOUNDARY_FAIL;
- **until the founder disposes of R4-11:** the offset is recorded, and every Stage A timing claim is **CONDITIONAL on an unbounded harness clock** (GPT G-02).

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

*Interpretation beyond the record (self-review D5):* the founder decision says "invoke and log only". R4 places the logging in a minimal wrapper, because Task Scheduler itself writes no per-invocation log suitable for audit.

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
- **SKIPPED is removed.** A slot with no CYCLE record is classified MISSING by the auditor (§11.2). No component writes MISSING.

### 6.4 Cycle procedure (per slot)

1. **Pre-flight (V12):**
   - no credential in the environment;
   - the client allowlist is exactly the market-data host;
   - offset measurable and, if R4-11 is adopted, within its bound;
   - (Branch H only) firewall state as recorded at RUN_OPEN.
   - Failure → a BOUNDARY_FAIL CYCLE record.
2. **Fetch** bars, then the quote (§4.2). Store the raw artifacts (§10.2).
3. **Validate** V1 to V11 (§4.7). Update the bar store observations (§4.9).
4. **Compute** S20 and S50 at k and k−1, then D(k−1) and D(k); then the signal (§3.2) and the mapping (§3.3).
5. **Propose** (only if mapped to a proposal): §7.
6. **Commit** the CYCLE record (§10.4):
   - for HOLD, NO_ACTION, NO_DECISION and BOUNDARY_FAIL: immediately;
   - for a proposal: at REJECTED, or at SHADOW_EXPIRED when the ceiling is reached.
   - The commit must happen before T_d(i+1).

### 6.5 Injections

- Injected proposals (`origin: INJECTED`) are run only on the founder's command.
- They use fixture inputs, never live slots. They take the run lock token as an INJECTION. They may not start within 30 s of the next T_d. They are aborted by any slot invocation (§6.3).
- They are recorded as INJECTION records and **never occupy or satisfy a slot**.

---

## 7. Proposal construction and policy (normative)

### 7.1 Evaluation order (deterministic; all failures recorded)

1. Quote validity Q1 to Q5 (§4.11). Failure → NO_DECISION (QUOTE_INVALID); no proposal record.
2. Sample checkpoint (a) → `created`.
3. Construct the proposal: side; L (§7.2); q and R (§8.2) or q_exit (§8.3); `partial_fill_accepted` (Stage B; §9.5).
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
| R8 | BTC notional at bid + R ≤ $300.00 | $300 | A, B | **CANDIDATE** (RC-25a) |
| R9 | q_exit ≤ held BTC − reserved BTC | — | A, B | — |
| R10 | q ≥ min_order_size; q on qty_increment; L on price_increment | policy file (§7.4) | A: CONDITIONAL; B: metadata | UNVERIFIED |
| R11 | at most one open authorization or order per instrument | — | A, B | — |
| R12 | equity < $450.00 → reject BUY (equity = cash + BTC × bid) | $450 | A, B | **CANDIDATE** (RC-25b) |
| R13 | cutoff (§5.3); clock rules (§5.4) | W = 90 s | A, B | founder (W) |
| R14 | re-check at (b), (c) and (d): §9.3 | — | B | — |
| R15 | EXIT only while long; q_exit per §8.3 | — | A, B | — |
| R16 | **FD-3** | — | A (vacuous), B | **FD-3** |

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

- **Opening cash** is declared in the manifest. **CANDIDATE: $500.00** (RC-25d). BTC opens at 0.
- **Shadow fills are not simulated.** Doing so would mean inventing venue behaviour, which the dispatch prohibits.
- A shadow reservation R is created when a proposal passes policy at checkpoint (a), and released at SHADOW_EXPIRED **in the same cycle**. A shadow reservation therefore never crosses a slot (DERIVED).
- Consequence: shadow cash and BTC never change. R8 and R12 never bind on live data (§16, OI-08).

### 8.2 Stage B typed ledger (specified; DEFERRED)

**Balances:**
- **USD:** cash and reserved_usd, in exact cents.
- **BTC:** held_btc and reserved_btc, exact, on the quantity increment.

**cash_available** = cash − reserved_usd. **btc_available** = held_btc − reserved_btc.

**BUY reservation:**
- R = ceil to the cent of q × L × (1 + f_res), where f_res = 0.0025 is a DOCUMENTED tier-1 taker rate. Whether it applies on paper, and whether maker or taker, is UNVERIFIED.
- f_res is a **reservation bound, not a booked fee.**
- With Q_f = the **cumulative** filled quantity: outstanding_usd = max(0, R − floor to the cent of (Q_f × L × (1 + f_res))).
- This is computed from the cumulative quantity, **never by per-fill decrements** (S2-2, Gemini B-06).

### 8.3 EXIT reservation (Stage B)

- q_exit = floor to the quantity increment of btc_available.
- reserved_btc increases by q_exit.
- outstanding_btc = q_exit − Q_f.

### 8.4 Fill events (Stage B)

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

### 8.5 Atomicity (Stage B)

- The ledger has a **single writer**.
- Each transition is **one append-only ledger event** under the ledger lock, citing its trigger: the authorization, the fill event id, the terminal evidence or the death event.
- No transition is inferred.

### 8.6 Invariants and falsifiers (DERIVED; DESIGNED tests)

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

## 9. Approval, authorization and execution boundary (Stage B; DEFERRED; FD-9)

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
| RUN_CLOSE | the harness, on the founder's command after T_d(N) | invocation-log SHA-256; task-XML SHA-256 |

### 10.2 Artifacts

- Raw responses are stored at `artifacts/<sha256>`. They are written by the harness before parsing and referenced by hash from CYCLE records.
- The **invocation log** (`chain/invocations/<manifest_sha256>.log`) is owned and written **only by the wrapper**; it is append-only.
- **Manifests** (`runs/<name>.json`) are owned by the **founder**.
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
- invocation instant; T_d; checkpoint-(a) instant; offset estimate;
- request URLs and instants; artifact hashes (bars, quote, headers);
- per-bar token tuples for every completed bar fetched; excluded bars;
- bar-store transitions (§4.9);
- V1 to V12 results; Q1 to Q5 results (if evaluated);
- S20 and S50 at k and k−1; D(k−1) and D(k); signal; mapping;
- proposal (if any), with L, q, R and the rounding inputs;
- every rule result with its rule code;
- `terminal_state`, from the closed set (§11.1);
- policy hash; displayed sizes; Branch H/C marker (§2.3).

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
| HOLD | V1 to V12 pass; D(k−1) and D(k) are recomputed from the artifacts; signal = HOLD |
| NO_ACTION | V pass; D recomputed; signal ∈ {BUY, EXIT}; mapped to NO_ACTION by §3.3 |
| REJECTED | V pass; D recomputed; Q1 to Q5 pass; a proposal constructed; ≥ 1 rule fails on recomputation (including the R13 cutoff) |
| SHADOW_EXPIRED | V pass; D recomputed; Q pass; all rules pass on recomputation; recorded at the ceiling |

### 11.2 Slot classification

The auditor runs this per manifest and per slot i = 0 … N − 1, once now ≥ T_d(N):

| Evidence for slot i | Classification |
|---|---|
| no CYCLE record with this manifest, slot and cycle_id(i) | **MISSING** |
| more than one CYCLE record | **DUPLICATE** |
| exactly one CYCLE record **and** a CONCURRENT_INVOCATION anomaly | **NON-QUALIFYING** (a scheduler fault) |
| exactly one CYCLE record that fails the schema, the chain, artifact hashes or recomputation | **NON-QUALIFYING** (a finding) |
| a CYCLE_OVERRUN for slot i | **NON-QUALIFYING** |
| exactly one valid CYCLE record meeting §11.1 | **QUALIFYING** |

**Findings that never qualify:**
- **OFF_GRID:** a CYCLE record matching no slot of its manifest;
- an INJECTION presented as SCHEDULED (U68);
- the same cycle_id appearing under two manifests (U69).

**Invocation consistency (U77):**
- each invocation-log line must correspond to a chain record for its slot (a CYCLE, CONCURRENT_INVOCATION, CYCLE_OVERRUN or OFF_RUN record);
- each CYCLE record must correspond to an invocation line;
- any mismatch is a finding.

### 11.3 Completeness of the run set (U66, U70, U72)

The auditor:
1. verifies the chain from GENESIS (contiguous `seq`, every `prev_hash` and `hash`);
2. lists every RUN_OPEN manifest hash in the chain and every manifest file in the repository;
3. reports any manifest that appears in one list but not the other;
4. checks each manifest's `prev_chain_head` against the chain.

**The exit report lists every manifest.** Its denominator is every slot of every manifest: **missing slots stay in the denominator.**

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

**Test coverage (pre-live gate):** before the first live-data cycle, at least one **EXECUTED** pass case and fail case per rule R1 to R16, plus every Stage A test in §14, with the evidence retained.

---

## 12. Reconciliation (Stage B; DEFERRED)

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
- Under Branch C, not even process-level read-only isolation.

Thirty slots are not thirty trades.

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
| U7 | duplicate t, identical / differing | proceed with a note / DATA_CONFLICT | A |
| U8 | (a) the newest completed bar is 10 min older than t_exp; (b) a valid quote 16 s old with a BUY signal | (a) STALE_SERIES; (b) REJECTED (R4) | A |
| U9 | replay of stored artifacts | byte-identical TER body, flagged REPLAY, never appended | A |
| U10 | 100 runs; other process, locale, timezone | identical results | A |
| U11 | 50 completed bars | INSUFFICIENT_HISTORY | A |
| U12 | bars in reverse order | sorted; recorded; same result | A |
| U13 | next_page_token not null | all pages fetched, or INCOMPLETE_RESPONSE | A |
| U14 | BUY while long; EXIT while flat (fixture ledger) | NO_ACTION (CF-2) | A |
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
| U35 | first cycle ever (empty store) | all bars CONFIRMED on first observation; decision proceeds | A |
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
| U79 | offset at the bound / beyond it (if R4-11 is adopted) | pass / BOUNDARY_FAIL | A |
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
| X5 | fixture ledger with equity $449 / notional over R8 | REJECTED (R12 / R8) | A |
| X6 | sell exceeding holdings | REJECTED (R9) | A |
| X7 | limit 1.5% off mid | REJECTED (R5) | A |
| X8 | request to a trading host | refused before network I/O; BOUNDARY_VIOLATION_ATTEMPT recorded | A |
| X9 | a credential placed in the environment | BOUNDARY_FAIL | A |
| X10 | a downstream step treats a passed shadow proposal as permission to submit | no submit path exists; recorded | A |
| X11 | a fabricated signal | reconstruction finding | A |
| U92 | Branch H: TCP connect to the trading host from the harness process | refused by the host firewall | A (if Branch H) |

**Reserved and unused IDs:**
- U49 is subsumed by U30.
- The R3 IDs U44 to U53 are reused here with the recovery-document meanings.

---

## 15. UNVERIFIED / CONDITIONAL / UNBOUNDED register

| ID | Item | Label | Blocks |
|---|---|---|---|
| U-D1 | keyless access over repeated requests | OBSERVED once | — (Stage A evidence) |
| U-D4 | 5Min bar revision behaviour; finality | UNVERIFIED | bounds claims |
| U-D5 | how bar prices with 3 or 4 decimals are derived | UNVERIFIED | — |
| U-D6 | gap frequency; behaviour under load | UNVERIFIED | — |
| U-D7 | bar labelling (start vs end) | DOCUMENTED; not established by the probe | — (conservative rule) |
| U-D8 | `end` parameter semantics | UNVERIFIED | — (handled by V2, V6, V7) |
| U-T1 | Task Scheduler settings and behaviour | UNVERIFIED | the first run (U73 to U77) |
| U-T2 | Stage A clock accuracy | CONDITIONAL until R4-11 | timing claims |
| U-I1 | Stage A host-level egress (Branch H feasibility) | UNVERIFIED | R4-9 |
| U-V1, U-V2 | price increment; quantity increment and minimum | UNVERIFIED | the first paper order |
| U-V3 | paper fee rate, asset and maker/taker; the fill/activity id field | UNVERIFIED | the first paper order |
| U-V4 | paper fills relative to displayed size | UNVERIFIED | — |
| U-V5, U-V6 | account configuration; metadata readable with paper keys | UNVERIFIED | the first paper order |
| U-V7 | COID semantics | DOCUMENTED | the first paper order (CF-7 sequence) |
| U-G1, U-G2 | approver authentication; σ and δ_send | UNVERIFIED | Stage B |
| U-G3 | G7-I8 known false; G7-I5 not established | disclosed limitation | claim language |
| U-O1 | Stage B reconstruction plus review within W = 90 s | UNVERIFIED | Stage B |
| U-O2 | slots needed to reach run_length ≥ 30 | UNBOUNDED | — |
| U-O3 | time to the first BUY | UNBOUNDED | — |
| U-O4 | a shared misreading of R4 by the harness and the FD-6 script | UNBOUNDED (common mode) | — |

---

## 16. Open items register (deliverable D4)

| ID | Issue | Why it matters | If unresolved | Decision-maker | Blocks |
|---|---|---|---|---|---|
| OI-01 | the committed founder decision record has not been inspected by Claude | R4 §1.1 depends on its exact text | R4 may misstate a decision | founder: confirm the blob or text | **freeze** |
| OI-02 | RC-25a, R8 $300 | portfolio exposure cap | stays CANDIDATE; does not bind in Stage A | founder | **freeze** (policy must be fixed in the frozen set) |
| OI-03 | RC-25b, R12 $450 | drawdown stop | as OI-02 | founder | **freeze** |
| OI-04 | RC-25c, settle 60 s | completed-candle rule | the data contract is not fixed | founder | **freeze** |
| OI-05 | RC-25d, opening shadow cash $500 | Stage A sizing | the manifest value is unfixed | founder | **freeze** |
| OI-06 | R4-9, Branch H vs Branch C | strength of the Stage A isolation claim | the claim stays client-level only | founder | **freeze** (the harness scope differs) |
| OI-07 | R4-11, clock bound 2 s | timing validity of Stage A | timing claims stay CONDITIONAL | founder | **freeze** (V12 content) |
| OI-08 | Stage A never exercises long-position branches or R8/R12 on live data (no shadow fills) | coverage of the policy on live inputs | those branches are evidenced only by tests and injections | founder: accept the limitation (simulating fills would invent venue behaviour) | implementation |
| OI-09 | single-reviewer coverage (§17) | review independence | those areas rest on one reviewer | founder | freeze (accept or obtain a review) |
| OI-10 | FD-4 TIF | order lifetime; the $1-increment BUY-below-ask consequence (§7.2) | Stage B text incomplete | founder | Stage B only |
| OI-11 | FD-G13, FD-G16, FD-G17, FD-G18 | Stage B controls | Stage B cannot be authorized | founder (FD-9) | Stage B only |
| OI-12 | FD-8 paper-key custody | the Stage B pre-flight needs keys | no pre-flight | founder | Stage B only |
| OI-13 | the wrapper as the logging component of FD-7 (§6.1) | the founder decision says "invoke and log only" | if rejected, another logging mechanism is needed | founder: confirm | freeze |
| OI-14 | FD-5 harness build | implementation authority | no Stage A evidence | founder, after review and freeze | implementation |

---

## 17. Review integrity and coverage record

- **Incidents:** RI-2026-11-25-01 (SF-1 to SF-3 disclosed to both reviewers before review) and RI-2026-11-25-02 (annex S2 disclosed to GPT). Recorded in the recovery document; nothing is removed.
- **R3 reviews:** GPT, the full set, exposed to the sealed findings; Gemini account B, **R3 text only**, unexposed. Gemini account A was blocked by its filter.
- **Areas reviewed by GPT only** (Gemini B did not review them):
  - the G-07 claims;
  - the closure-package register;
  - R1 §3 and §6 retention (now integrated as §9.1, §9.7 and §9.8);
  - the Stage A Design references (now integrated as §3, §6.4 and §14.7);
  - the stage boundary (§2).
- **Not reviewed by anyone yet:** all R4 text. R4 integrates and changes material, so it needs its own hostile review.

*End of R4 candidate.*
