Prior exposure: none. Before this review I had not seen any Claude self-finding or any other reviewer's review.

---

### Part 1: Review of R3 §9 (Milestone Counter and Slot Audit) and §5 (Cycle Identity and Scheduling)

#### Answers to Specific Questions (§5 & §9)

* **Can a malformed or incomplete record count as qualifying?** No, under the literal text of §9.2, provided the auditor verifies the underlying data rather than trusting summary fields: §9.2 explicitly disqualifies records outside the closed terminal-state set, records with absent/multiple/misspelled states, records failing hash-chain checks, or records missing a required condition field. However, **B-02** below identifies a concrete vulnerability where a truncated or unverified TER passes if the auditor does not independently recompute the hash chain and `V1`–`V12` / `D(k)` predicates from raw inputs.


* **Can a HOLD hide a missing cycle?** Not in the audit ledger, because §9.3(2)–(3) builds the scheduled-candle ledger independently from `T_d(0) + 300 s · i` and classifies any slot `i` lacking a record with `cycle_id(i)` as `MISSING` (non-qualifying). However, if the harness emits a synthetic `HOLD` record without executing `V1`–`V12` or `D(k)`, it can only be caught if the auditor verifies the cryptographic binding to raw fetched artifacts (**B-02**).


* **Can injected proposals affect the denominator?** No. §9.2 states `origin: INJECTED` records are not slot records, never qualify, and never occupy a slot, while §9.3(4) defines the denominator strictly as every slot `0 … n` of every committed run manifest. (Note: if an injected proposal lacks `origin: INJECTED` or uses a valid `cycle_id(i)`, it collides with the real slot record and causes a `DUPLICATE` classification under §9.3(3), which is non-qualifying.)


* **Can a run be left out of the audit?** §9.3(1) mandates that a run manifest be committed to the repository *before* a run's first slot and that every committed manifest appear in the Stage A exit report. However, because "committed to the repository" is undefined (local git commit vs. pushed remote) and no pre-run hash-chain anchor or external witness is required, a local unpushed run could be discarded (`git reset`) before reporting (**B-04**).


* **Can a timer miss, duplicate or drift slots without detection?** A timer can miss or duplicate slots, and both are detected by §9.3(3) (`MISSING` and `DUPLICATE`). Timer drift within `[T_d(i), T_d(i+1))` is absorbed into the same `cycle_id(i)` by §5.2 (`t_exp = T_d(i) − 360 s`). However, if timer drift crosses `T_d(i+1)`, slot `i` is `MISSING` and slot `i+1` is executed—which is detected, *unless* the invocation occurs at `T_d(i+1) − ε` and overruns `T_d(i+1)` (**B-03**), or no timer invocation log exists to distinguish a missed timer firing from a suppressed harness run (**B-01**).


* **Is the run's end defined?** **No.** §9.3(2) references *"the run's declared end"* (`n is the last slot with T_d(n+1) ≤ the run's declared end`), yet §9.3(1) omits `declared_end` (or `slot_count`) from the required fields of the run manifest, and no lifecycle rule specifies when or how a run's end is declared (**B-01**).

---

#### Findings (§5 and §9)

##### B-01 — Undefined Run End and Missing Manifest Schema Field

* **Section:** §9.3(1) and §9.3(2)


* **Exact mechanism:** §9.3(2) defines the upper slot index `n` of the scheduled-candle ledger as *"the last slot with T_d(n+1) ≤ the run's declared end. A slot still in progress is not judged."* However, §9.3(1) enumerates the contents of the Run Manifest as containing only: (1) instrument, (2) `T_d(0)`, (3) opening shadow cash, and (4) hashes of the frozen specification set, harness, and policy file. Neither `declared_end` nor a terminal `RUN_END` record format/commit rule is specified anywhere in §5 or §9.


* **Consequence:** The auditor cannot deterministically compute `n` or the denominator (§9.3(4)). Worse, if `declared_end` is chosen post-hoc rather than fixed pre-run (or bound by a signed stop event), trailing `MISSING` slots after a crash or stopped timer can be excluded from the denominator by declaring the run ended immediately after the last qualifying slot.


* **Smallest correction:** Require `declared_end` (or fixed `max_slots`) to be recorded in the pre-run manifest (§9.3(1)), OR define an explicit, hash-chained `RUN_STOPPED` terminal manifest event with a mandatory timestamp `T_stop`, setting `n` to the largest integer with `T_d(n+1) ≤ T_stop`.
* **Severity:** **HIGH**

##### B-02 — §9.2 Qualifying Conditions Rely on Self-Reported TER Fields Without Mandatory Raw-Artifact Re-Verification

* **Section:** §9.2 and §9.3(3)


* **Exact mechanism:** §9.2 specifies that a record qualifies if `V1 to V12 passed ∧ D(k−1) and D(k) computed from 51 validated candles ∧ ...` and disqualifies a record *"that fails its hash-chain check"* or *"missing a required condition field"*. However, §9.3 does not define what the hash chain covers (e.g., whether it links consecutive TERs across slots and binds the raw HTTP response SHA-256 from §3.2(1)), nor does §9.3 require the slot audit to verify `V1`–`V12` and `D(k)` against the stored raw bytes rather than checking boolean flags in the TER.


* **Consequence:** A buggy or non-compliant harness that writes `V1..V12: true` and a fabricated `HOLD` TER without fetching valid bars (or while violating `V8`/`V11`) satisfies the literal field-presence check in §9.2 unless the audit script validates the raw artifact hashes and recomputes `V1`–`V12` across all slots, not just the 5 M1-6 sample cycles.


* **Smallest correction:** Specify in §9.2/§9.3 that the TER hash chain must link `prev_ter_hash` across sequential records and bind the raw response SHA-256s (§3.2(1)), and require the §9.3 audit to verify `V1`–`V12` and signal derivation from raw artifacts for every slot in `0 … n`.


* **Severity:** **HIGH**

##### B-03 — Overrun Detection Race and Dual-Record Collision Across Slot Boundaries

* **Section:** §4.3, §5.1, §5.2, and §9.3(3)


* **Exact mechanism:** Under §5.2, an invocation at `T_d(i+1) − 1 ms` selects `t_exp = T_d(i) − 360 s` (slot `i`). Under §4.3, `cycle overrun` occurs iff *"the cycle has no terminal record committed before T_d(i+1)"*. Under §5.1, *"Overrun (§4.3) → CYCLE_OVERRUN, and any proposal from that cycle is blocked. The next cycle processes only its own t_exp; intervening slots are recorded SKIPPED."* Two defects arise:


1. If slot `i` is invoked at `T_d(i+1) − 1 ms`, it cannot commit a terminal record before `T_d(i+1)` (two HTTP GETs take > 1 ms), so it transitions to `CYCLE_OVERRUN` after `T_d(i+1)` while slot `i+1` is simultaneously triggered at `T_d(i+1)`. §5.1 enforces *"One active cycle per instrument. A second invocation → CONCURRENT_INVOCATION"*, causing slot `i+1` to fail with `CONCURRENT_INVOCATION` even though slot `i` has already passed its `T_d(i+1)` deadline.


2. §5.1 says *"intervening slots are recorded SKIPPED"*, yet §9.3(3) defines a slot with zero records as `MISSING`. R3 never specifies *which* component writes a `SKIPPED` record (the overrunning cycle, the next cycle, or the auditor) or when `SKIPPED` vs `MISSING` applies.




* **Consequence:** A single late invocation at the end of slot `i` cascades into killing slot `i+1` via `CONCURRENT_INVOCATION`, and `SKIPPED` in §9.1 is unreachable or ambiguously produced compared to `MISSING` in §9.3(3).


* **Smallest correction:** (a) Hard-abort an active cycle at `T_d(i+1)` (committing `CYCLE_OVERRUN` and releasing the single-instance lock at `T_d(i+1)` so slot `i+1` is never blocked by an expired slot `i`); (b) specify explicitly that the next active cycle `j > i` writes `SKIPPED` records for any `k` with `last_recorded_slot < k < j` before processing slot `j`, or remove `SKIPPED` and treat all unrecorded slots as `MISSING`.
* **Severity:** **MEDIUM**

##### B-04 — Pre-Run Manifest Commitment Lacks Anti-Suppression / Tamper-Evident Anchor

* **Section:** §9.3(1) and §5.4


* **Exact mechanism:** §9.3(1) states *"Run manifest: committed to the repository before a run's first slot... Every committed manifest must appear in the Stage A exit report. A run cannot be dropped."* In a local git repository without a remote push requirement or append-only external ledger, a failed run manifest committed locally can be dropped via `git reset` or branch deletion without leaving a trace in the repository history. Additionally, §5.4(i) mentions a timer that *"logs every invocation"*, but §9.3 does not include the timer invocation log in the audit inputs.


* **Consequence:** Selective run omission ("cherry-picking" a clean 30-slot run while discarding failed runs) is undetectable from repository inspection alone, and suppressed/crashed timer invocations cannot be distinguished from manual non-triggering.
* **Smallest correction:** Require the pre-run manifest hash (and `T_d(0)`) to be pushed to a remote or recorded in an append-only external/founder log prior to `T_d(0)`, and mandate inclusion of the raw timer invocation log (if FD-7 selects option (i)) in the §9.3 audit inputs.


* **Severity:** **MEDIUM**

---

### Part 2: Review of R3 §3 (Data Contract), §4 (Time Arithmetic), and §6 (Sizing, Reservations, Partial Fills)

#### Answers to Specific Questions (§3, §4, §6)

* **Is every calculation exact from JSON token text through sizing, fees and reservations?** Almost, with two arithmetic gaps:
1. §3.2(2) mandates exact decimal/rational arithmetic and §4.1 prohibits floating-point comparisons, while §6.2 defines `q = floor(budget / (L × (1 + f_res)))` and `R = ceil(q × L × (1 + f_res))`. Exact rational division handles `budget / (L × (1 + f_res))` without precision loss.


2. However, **B-06** below identifies that §6.6 reduces a reservation upon fill by `ceil to the cent of q_f × L × (1 + f_res)` while booking spend as `q_f × p_f + fee_usd`—when `p_f < L` (price improvement on a limit BUY), the reservation reduction exceeds the booked spend, leaving unspent reserved cash trapped until terminal reconciliation, whereas if the exchange charges a fee in BTC (§6.4) vs USD (§6.6), unit handling between USD reservations and BTC asset fees is underspecified (**B-07**).


* **Are there rounding ambiguities or unit mismatches?** Yes:
* **Unit mismatch in fee accounting (§6.4 vs §6.6):** §6.4 notes *"DOCUMENTED: the buy fee is taken in the received asset [BTC]"*, whereas §6.6 computes `R` in USD with `1 + f_res` and books spend as `q_f × p_f plus any reported USD fee`. If the fee is taken in BTC, `q_f` gross vs. `q_f − fee_btc` net is not distinguished in §6.6, creating a mismatch between cash spent and reconciled BTC held (**B-07**).


* **Rounding direction of `budget`:** `budget = min($150.00, cash_available)` is exact to cents if `cash_available` is exact to cents, which holds because opening cash is USD and every reservation/spend delta is rounded to cents.




* **Can a revised bar escape detection?** **Yes**, in two ways (**B-05**):
1. Across a run restart or after a `NO_DECISION` / `MISSING` cycle, §3.7 only compares *"every bar it has in common with the previous cycle's accepted window"*. If cycle `k` fails `V8` (`DATA_GAP`) or is `MISSING`, its window is not an "accepted window", or if a bar falls out of the 51-bar window before the next accepted cycle, a revision is never checked against earlier cycles' raw bars.


2. §3.7 compares bars *"by token text"*. If a bar's timestamp `t` itself is revised (shifted by 300 s or dropped/replaced), there is no bar *"in common"* by `t` with the previous cycle's window—if `t` was at the trailing edge (`t_exp − 250 min`), shifting it escapes §3.7 completely.




* **Can partial fills, cancel requests or ambiguous outcomes cause double allocation or premature release?**
* *Double allocation / premature release on cancel or ambiguous:* No—§6.6 keeps `R` unchanged on `cancel requested` and keeps `AMBIGUOUS` fully reserved while `R16` blocks new proposals.


* *However*, **B-06** shows that on a partial fill where `p_f < L` (limit price improvement), `R` is reduced by `ceil(q_f × L × (1 + f_res))` (which is greater than actual spend `q_f × p_f + fee`), artificially depressing `cash_available` during the order's life; conversely, if a partial fill is followed by `AMBIGUOUS` or venue-specific fee rounding, the remaining reservation `R_rem` can become negative if `Σ ceil(q_f × L × (1 + f_res)) > R` due to per-fill ceiling rounding (**B-06**)!


* **Can any clock window extend past the next slot?**
* Under §4.2, `ceiling = created + 180 s` and `expires_at = min(issued + 60 s, created + 180 s)`.


* If `created ≈ T_d(i)`, `ceiling ≈ T_d(i) + 180 s < T_d(i) + 300 s = T_d(i+1)` (120 s margin).
* **However**, §4.2 defines `created` only as `≈ T_d` (an approximation, not a bound!), and §5.2 allows an invocation anywhere in `[T_d(i), T_d(i+1))`. If a cycle is invoked at `T_d(i) + 121 s`, then `created = T_d(i) + 121 s`, so `ceiling = created + 180 s = T_d(i) + 301 s > T_d(i+1)`! Thus **yes, a clock window can extend past the next slot** (**B-08**), directly falsifying test `U16` (`expires_at < T_d + 300 s; no two authorizations live together`).





---

#### Findings (§3, §4, and §6)

##### B-05 — §3.7 Bar Revision Check Only Compares Against Immediately Preceding Accepted Window and Misses Cross-Gap or Historical Revisions

* **Section:** §3.7 and §3.5 (`V11`)


* **Exact mechanism:** §3.7 states: *"Each cycle compares, by token text, every bar it has in common with the previous cycle's accepted window. A difference → a SOURCE_REVISION event... The current cycle returns NO_DECISION (SOURCE_REVISION) if the revised bar lies inside its own 51-candle window (V11)."* Because the comparison is strictly pairwise against *"the previous cycle's accepted window"*:


1. If cycle `i` fails (`NO_DECISION`, e.g., `STALE_SERIES` or `FETCH_FAILED`), it has no accepted window. If cycle `i` *did* accept a window at `i−1`, and cycle `i` had a transient revision that reverted by `i+1`, or if multiple cycles failed (`i .. i+50`), bars from `i−1` are no longer in common with `i+51`.


2. More critically, in Stage B, §3.7 states *"Any Stage B proposal or authorization whose input contains the revised bar is invalidated"*, yet §3.7 only inspects bars in the *current* cycle's fetched window. If a bar used in an open Stage B authorization is revised at the API *outside* the current cycle's window (or if no new cycle has run yet before LP-CONSUME / LP-PRESEND), the revision is never detected.




* **Consequence:** A revised bar can escape detection across multi-cycle outages or prior to Stage B order execution, violating the fail-closed data integrity invariant.
* **Smallest correction:** Maintain a persistent append-only `canonical_bars` store keyed by `(instrument, t)` recording the first-accepted token tuple `(o, h, l, c, v, vw)` for every bar ever accepted in the run; compare every fetched bar in every cycle against `canonical_bars[t]` (not just the prior cycle's window), and re-verify the bar window against `canonical_bars` at Stage B checkpoints `(b)`, `(c)`, and `(d)`.


* **Severity:** **HIGH**

##### B-06 — Per-Fill Ceiling Rounding in §6.6 Can Cause Remaining Reservation Underflow (`R_rem < 0`)

* **Section:** §6.2 and §6.6


* **Exact mechanism:** In §6.2, total initial reservation `R` for quantity `q` is computed once as:

$$R = \lceil q \cdot L \cdot (1 + f_{\text{res}}) \rceil_{\text{cent}}$$



In §6.6, on each partial fill of quantity $q_f$, the reservation is reduced by:

$$\Delta R_f = \lceil q_f \cdot L \cdot (1 + f_{\text{res}}) \rceil_{\text{cent}}$$



Because the ceiling function is subadditive ($\lceil a + b \rceil \le \lceil a \rceil + \lceil b \rceil$), for a sequence of $m$ partial fills where $\sum_{f=1}^m q_f = q$, the sum of per-fill reductions $\sum_{f=1}^m \Delta R_f$ can exceed $R$ by up to $(m - 1)$ cents.


* **Consequence:** On the final partial fill (or prior to terminal confirmation), `R − Σ ΔR_f` becomes negative (e.g., `-$0.01` to `-$0.05`), violating the reservation accounting invariant (`reservation.amount ≥ 0` and `Σ unreleased reservations + booked spend ≤ opening cash`) and potentially overstating `cash_available` before terminal reconciliation.


* **Smallest correction:** Define remaining reservation on partial fill as `R_rem = max($0.00, R − Σ_f ceil_cent(q_f × L × (1 + f_res)))`, or compute `R_rem = ceil_cent((q − Σ_f q_f) × L × (1 + f_res))` directly from the remaining unfilled quantity `q − Σ_f q_f`.


* **Severity:** **MEDIUM**

##### B-07 — Fee Asset Unit Mismatch Between USD Reservation (§6.2/§6.6) and Received-Asset BTC Fee (§6.4)

* **Section:** §6.2, §6.4, and §6.6


* **Exact mechanism:** §6.2 reserves USD equal to `ceil_cent(q × L × (1 + f_res))`. §6.6 states *"the booked spend is the reported q_f × p_f plus any reported USD fee"* and sets the falsifier *"a booked fee greater than its reserved fee. This is a DISCREPANCY (L-2): halt."* Meanwhile, §6.4 notes *"DOCUMENTED: the buy fee is taken in the received asset [BTC]"* (and §13 `U-V3` marks fee asset as `UNVERIFIED`). If Alpaca paper takes the BUY fee in BTC (e.g., `fee_asset = BTC`, `fee = 0.00001 BTC`, `usd_fee = 0`):


1. §6.6's falsifier (*"a booked fee greater than its reserved fee"*) has no conversion rule to compare a BTC-denominated fee against a USD-denominated `R − q × L` reserve.


2. In Stage A (shadow ledger), §6.1–§6.4 never specifies how shadow BTC is credited on a shadow fill (whether `q` or `q × (1 − f_res)`), nor does §6.6 define how `cash` and `BTC` ledgers are updated upon fills.




* **Consequence:** When `fee_asset = BTC` in Stage B, the §6.6 fee-bound check either vacuously passes (`0 USD > reserved USD` is false, allowing an arbitrary BTC fee to bypass L-2) or crashes on a unit mismatch (`BTC` vs `USD`), and reconciled BTC (`q_f − fee_btc`) diverges from expected ordered quantity `q_f`.


* **Smallest correction:** Explicitly specify in §6.6 that if `fee_asset == BTC`, the effective USD fee equivalent for the L-2 falsifier is `fee_btc × p_f` (verified against `R − ceil_cent(q_f × p_f)`), and state that reconciled `BTC` increments by `q_f − fee_btc` (or `q_f` if `fee_asset == USD`).


* **Severity:** **HIGH**

##### B-08 — Clock Ceiling `created + 180 s` Can Exceed Next Slot `T_d(i+1)` Because `created` Is Unbounded Within `[T_d(i), T_d(i+1))`

* **Section:** §4.2, §4.3, §5.2, and §11 (`U16`)


* **Exact mechanism:** §4.2 defines `created` as `proposal_created_at: when the proposal is computed (≈ T_d)`, `approval_deadline = created + 120 s`, and `ceiling = created + 180 s`. However, §5.2 permits a valid cycle invocation anywhere in `[T_d(i), T_d(i+1))`, where `T_d(i+1) = T_d(i) + 300 s`. If a cycle is invoked at `T_d(i) + 121 s` (or if HTTP fetches take > 120 s), `created > T_d(i) + 120 s`, which implies:



$$\text{ceiling} = \text{created} + 180\text{ s} > T_d(i) + 300\text{ s} = T_d(i+1)$$



Yet §11 test `U16` asserts the derived invariant: `expires_at = min(issued + 60 s, created + 180 s) < T_d + 300 s; no two authorizations live together`.


* **Consequence:** Whenever `created ≥ T_d(i) + 120 s`, the authorization window and `SHADOW_EXPIRED` ceiling bleed into slot `i+1`. In Stage B, an authorization from slot `i` can remain live while slot `i+1` executes (triggering `R11`/`R16` collisions across slots), and `U16` fails as an invariant.


* **Smallest correction:** Anchor `ceiling` (and `approval_deadline`) to `T_d(i)` rather than `created`: set `approval_deadline = T_d(i) + 120 s` and `ceiling = T_d(i) + 180 s` (and reject/fail-closed if `created ≥ approval_deadline`), which guarantees `expires_at ≤ ceiling = T_d(i) + 180 s < T_d(i+1)` for every invocation in `[T_d(i), T_d(i+1))`.


* **Severity:** **HIGH**

##### B-09 — §3.1/§3.4 Bar Fetch Boundary Ambiguity (`ending at T_d` vs `t + 360 s ≤ T_d`)

* **Section:** §3.1 and §3.4


* **Exact mechanism:** §3.1 specifies fetching *"BTC/USD 5Min bars, with a window of at least 60 candles ending at T_d"*, while §3.4 defines a completed bar as `t + 360 s ≤ T_d` and notes the API returns a forming bar. On Alpaca's `/v1beta3/crypto/us/bars` endpoint, the `end` query parameter filters by bar start timestamp `t ≤ end` (inclusive). If a harness passes `end = T_d` (e.g., `12:01:00Z`), the API returns the forming bar `t = 12:00:00Z` (which V6 excludes), leaving `t_exp = 11:55:00Z` as the newest completed bar. However, if a harness passes `end = t_exp` or `end = T_d − 60 s` (`12:00:00Z`) and clock skew exists, or if a harness fetches only 60 bars without `end` specified, paging (`V2`) may be triggered unnecessarily or miss `t_exp`. More importantly, §3.1 says *"at least 60 candles"* without specifying an upper bound on `limit` or `start`, leaving the request window unbounded if `start` is omitted.


* **Consequence:** Ambiguous query construction (`start` / `end` / `limit`) across harness and independent reconstructor (`M1-6`) could fetch different bar sets or fail `V2`/`V7`.


* **Smallest correction:** Specify the exact deterministic query parameters in §3.1: `start = t_exp − 59 × 300 s` (60 slots) and `end = T_d` (in RFC-3339 UTC), with `limit` ≥ 100 so all bars fit in a single page.


* **Severity:** **LOW**

---

### Part 3: Test Adequacy, Residual Items, and Freeze Verdict (§11, §13–§14)

#### 1. Test Adequacy Table (§11)

Note: Per R3 §0 and §11, **zero tests have been executed**; all entries below evaluate the specification's designed test definitions.

| Critical Invariant | Test ID(s) | Pass Case (Designed) | Fail Case (Designed) | Proves Property or Example Only? |
| --- | --- | --- | --- | --- |
| **Exact decimal arithmetic & float exclusion** (§3.2, §4.1) | `U25` | JSON tokens (including exponents and high-precision decimals) parsed directly to exact decimal/rational; `D(k)`, sizing, and fees match exact rational reference.

 | Any intermediate IEEE-754 float conversion introduces rounding drift and fails equality check.

 | **Example only** — tests specific fixture tokens; static/AST inspection or runtime type-guard is needed to prove no `float` exists anywhere in the codebase. |
| **Zero-volume bar retention & numeric classification** (§3.6) | `U24` | Bars with `v` in `{"0", "0.0", "0e0", "-0"}` are retained in the 51-candle window and flagged `zero_volume: true`.

 | Text-only check (`v == "0"`) misses `"0.0"`/`"0e0"` or filters zero-volume bars out of `S20`/`S50`.

 | **Example only** — exercises the four listed string representations; property holds if implementation parses to decimal first. |
| **Completed bar boundary & forming bar exclusion** (§3.4, `V6`, `V7`) | `U5`, `U6`, `U11`, `U17` | Bar with `t + 360 s == T_d` is included; forming bar with `t + 360 s > T_d` is excluded and logged.

 | Bar at `t + 360 s == T_d + 1 ns` included in `D(k)`, or newest completed bar `t != t_exp` accepted.

 | **Example only** — checks boundary fixture values; needs nanosecond off-by-1 ns boundary vectors (currently only `U28`–`U30` test 1 ns offsets, not bar settle).

 |
| **Bar revision fail-closed behavior** (§3.7, `V11`) | `U31` | Revision of bar outside the current 51-candle window is logged (`SOURCE_REVISION`) and cycle proceeds.

 | Revision of bar inside the current 51-candle window returns `NO_DECISION (SOURCE_REVISION)` and invalidates affected Stage B proposal/auth.

 | **Example only (and incomplete)** — only tests single-step comparison against prior window; does **not** falsify multi-cycle gap bypass (**B-05**). |
| **Quote independence of signal** (§2.4) | `U18` | Identical 51 candles with missing, stale, or wildly altered quotes produce identical `S20`, `S50`, `D(k)`, and signal.

 | Any quote field altering `D(k)` or signal classification.

 | **Example only** — exercises fixture perturbation; architectural isolation (passing only bars to signal function) is needed for full proof. |
| **Quote freshness & future-quote rejection** (§4.3, `R4`, `CF-4`) | `U8(b)`, `U28` | Quote age `0 ns` and `15,000,000,000 ns` (`15 s`) at checkpoint passes `R4`.

 | Quote dated `c + 1 ns` (future) or `c − 15 s − 1 ns` (16 s in `U8(b)`) fails `R4`.

 | **Example only** — tests exact nanosecond boundaries (`-1 ns`, `0`, `15 s`, `15 s + 1 ns`), which tightly pins the boundary condition on deterministic inputs.

 |
| **Approval deadline & authorization lifetime bounds** (§4.2, §4.3, `CF-5`) | `U16`, `U29`, `U30` | `approved_at == approval_deadline` and `issued ≤ approval_deadline` pass; `LP-PRESEND` at `expires_at − δ_send` passes.

 | `approved_at == approval_deadline + 1 ns` yields `EXPIRED_UNAPPROVED`; `now == expires_at` is expired; `LP-PRESEND` at `expires_at − δ_send + 1 ns` fails.

 | **Example only (and currently falsified by B-08)** — `U16` asserts `expires_at < T_d + 300 s`, which fails if `created ≥ T_d + 120 s` (**B-08**); `U30` cannot execute until `δ_send` (`FD-G18`) is defined.

 |
| **Approval-to-authorization field binding** (§7, `A0.3-13`) | `U21`, `U22` | Authorization issued only when approval record exists, is unrevoked, and matches all bound fields (`L`, `q`, `R`, `TIF`, `partial_fill_accepted`, fee estimate).

 | Missing approval, revoked approval, or 1-tick/1-field mismatch between approval and authorization is rejected.

 | **Example only** — exercises specific tampered fields; exhaustive field-by-field mutation testing is required to prove complete binding. |
| **Exact BUY sizing & `$150.00` cap** (§6.2, `R7`) | `U33` | `budget` exactly divisible by `L × (1 + f_res)` and `budget` 1 cent short both floor `q` to quantity increment and satisfy `R ≤ $150.00`.

 | `q` rounded up or `R > $150.00` or `R > cash_available`.

 | **Example only** — tests two boundary budgets; does not test `q < min_order_size` (`R10` rejection) or `cash_available < $150.00`.

 |
| **Reservation lifecycle, partial fills, cancel & AMBIGUOUS lock** (§6.6, `R11`, `R16`) | `U32` | 40% partial fill reduces reservation; `cancel requested` leaves remainder reserved; second proposal blocked (`BLOCKED_OPEN_ORDER`); terminal confirmation releases remainder.

 | Premature release on `cancel requested`, second concurrent reservation created, or `AMBIGUOUS` order unblocking new proposals.

 | **Example only (and misses B-06/B-07)** — tests a single 40% partial fill, which does not expose multi-fill ceiling underflow (**B-06**) or BTC-denominated fee mismatch (**B-07**).

 |
| **Milestone counter allowlist & independent slot audit** (§9.2, §9.3) | `U26`, `U27`, `U34` | Only `{HOLD, NO_ACTION, REJECTED, SHADOW_EXPIRED}` with complete `V1`–`V12` and `D(k)` evidence count; missing slots counted as `MISSING` in denominator.

 | `HOLD` missing V-pass evidence (`U34`), `NO_DECISION` counted as qualifying (`U26`), or missing slot omitted from denominator (`U27`).

 | **Example only (and incomplete)** — does not test undefined `declared_end` (**B-01**), hash-chain tampering across slots (**B-02**), or overrun/concurrent cascade (**B-03**).

 |

---

#### 2. Residual UNVERIFIED / CONDITIONAL / UNBOUNDED Items

* **UNVERIFIED (Stage A & Venue Data):**
* `U-D3`: True zero-volume bar count in the Stage A-0 probe (`bars_body.json` numeric recount still pending).


* `U-D4`, `U-D5`, `U-D6`: Alpaca 5Min bar revision behavior, 3/4-decimal bar price derivation, and gap/load frequency.




* **UNVERIFIED (Stage B Execution, Venue Rules, & G-07 Controls — all block first paper order):**
* `U-V1`, `U-V2`: Venue price increment (contradicted by P-1) and quantity increment / minimum order size (contradicted by `1/price` note).


* `U-V3`, `U-V4`: Paper fee rate, maker/taker classification, fee asset (`USD` vs `BTC`), and fill behavior relative to displayed top-of-book size.


* `U-V5`, `U-V6`, `U-V7`, `U-V8`: Paper account buying power (`1×`, shorting disabled), asset metadata readability via paper keys, client order ID (`COID`) uniqueness/query support, and trade busts/corrections.


* `U-G1`, `U-G2`: Approver authentication (`FD-G13`) and Stage B time source, skew bound `σ`, and send margin `δ_send` (`FD-G18`).


* `U-O1`: Whether Stage B pre-approval reconstruction fits within the 120 s `approval_deadline`.


* `G7-I8` & `G7-I5` (`U-G3`): `G7-I8` is **known false** on the founder's machine; `G7-I5` is not established.




* **CONDITIONAL:**
* `U-D2`: Stage A-0 probe 5Min start-labelling/uniqueness/gaps (computed only from first/last `t` and count; local check on `bars_body.json` pending).


* Stage A shadow sizing (`§3.9`): Conditional on unverified `support_table_DOCUMENTED` price/quantity increments.


* `FD-5`: Stage A harness build conditional on FD-1 record, reconciled reviews, resolved/accepted criticals, and freeze authorization.


* `FD-4`: Accepted with clarification (`CF-1` remains `CANDIDATE` and blocks Stage B text).




* **UNBOUNDED:**
* `U-O2`: Total slots required to reach `run_length ≥ 30` (depends on `FD-7` trigger reliability and live feed data quality; unbounded under manual triggering `§5.4(ii)`).


* `U-O3`: Wall-clock time until the first `BUY` signal (market-dependent).





---

#### 3. Verdict

**NOT FREEZE-READY**

---

#### 4. Freeze Conditions

Before SL-PT-001 R3 can be frozen for Stage A implementation:

1. **Founder Decision on `FD-7` (§5.4) [OPEN]:** The founder must select the Stage A execution environment and cycle trigger mechanism (e.g., minimal local timer vs. manual triggering), as R3 explicitly leaves `FD-7` open with no default.


2. **Founder Disposition of `CANDIDATE` Items (without auto-promotion):** Explicit written founder acceptance or modification of:
* `FD-6 (scope)` (§1, §9.3): whether the GPT blind script also performs the §9.3 milestone slot audit.


* `FD-3 (residual)` (§1, §2.3, `CF-2`): `BUY` while long → `NO_ACTION` and `EXIT` while flat → `NO_ACTION`.


* `Settle = 60 s` (§1, §3.4) and `Policy values` (`R8 = $300`, `R12 = $450`, opening shadow cash = `$500.00`) (§1, §6.1, §8).


* `Stage A offset estimate` (§4.4, `CF-8`).




3. **Closure of Technical Defects `B-01` through `B-09` in R3 Text:**
* **B-01:** Add `declared_end` (or `max_slots`) to the §9.3(1) pre-run manifest or define a signed terminal `RUN_STOPPED` event so `n` and the denominator are well-defined.


* **B-02:** Specify TER hash-chain linkage (`prev_ter_hash` + raw artifact SHA-256s) and mandate raw-artifact re-verification of `V1`–`V12` and `D(k)` in the §9.3 slot audit.


* **B-03:** Enforce hard cycle termination at `T_d(i+1)` so an overrun in slot `i` cannot cause `CONCURRENT_INVOCATION` in slot `i+1`, and explicitly define the writer and semantics of `SKIPPED` vs `MISSING`.


* **B-04:** Define an external/remote anti-suppression anchor for pre-run manifests and include timer invocation logs in the §9.3 audit.


* **B-05:** Replace pairwise previous-window bar comparison in §3.7 with a run-wide append-only `canonical_bars` store keyed by `(instrument, t)`.


* **B-06 & B-07:** Fix partial-fill reservation reduction in §6.6 to prevent per-fill ceiling underflow (`R_rem < 0`) and define BTC-denominated fee conversion for the L-2 falsifier and ledger updates.


* **B-08:** Anchor `approval_deadline` (`T_d(i) + 120 s`) and `ceiling` (`T_d(i) + 180 s`) to `T_d(i)` rather than `created` so clock windows never bleed into slot `i+1` and `U16` holds.


* **B-09:** Pin exact `start`, `end`, and `limit` query parameters for the §3.1 bars request.




4. **Closure-Package Local Evidence Checks (`U-D2`, `U-D3`):** Execute the pending local verification on `bars_body.json` for bar start-labelling, uniqueness, gaps, and exact numeric zero-volume count.


5. **Pre-Live-Data Test Execution Gate (§9.4):** Execute and pass all unit/adversarial tests (`U1`–`U34`, `X1`–`X11`) and `R1`–`R16` pass/fail cases before the first live-data Stage A cycle. (Note: `CF-1`, `CF-7`, `FD-4 TIF`, `FD-8`, and `FD-9` remain explicitly scoped as Stage B blockers and do not block a Stage A-only freeze once recorded.)



---

#### 5. Single Most Important Blocker

Unresolved `FD-7` (Cycle Trigger & Runtime Scope, §5.4) coupled with Undefined Run-End / Slot-Audit Completeness (`B-01`, `B-02`):
`FD-7` is explicitly marked **OPEN** by R3 itself because without deciding between a minimal local timer and manual triggering, the Stage A harness scope cannot be bounded and `M1-1` (`run_length ≥ 30` consecutive 5-minute slots) is unbounded (`U-O2`). Directly coupled to this, §9.3 leaves `"the run's declared end"` undefined in the run manifest (`B-01`) and omits mandatory raw-artifact/hash-chain verification across all audited slots (`B-02`), preventing the milestone audit from deterministically computing the denominator or proving slot-record authenticity.