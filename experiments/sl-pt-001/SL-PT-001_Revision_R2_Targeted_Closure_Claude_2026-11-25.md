# SL-PT-001 Revision R2: targeted closure of the R1 review (candidate for hostile review)

**Author:** Claude (Specification Lead / ARBITER). **Date:** 2026-11-25.
**Responds to:** the founder dispatch "SL-PT-001 R1 TARGETED CLOSURE", which incorporates GPT's R1 closure review.
**Classification:** specification candidate. **NOT FROZEN.** Nothing is implemented.

**What R2 does not do:**
- R2 writes no reconstruction script and builds no harness.
- No test has been executed, and R2 claims none.
- G-07 is not changed beyond tracing the already-scoped approval predicate A0.3-13 (§5.3).
- **No implementation authority is implied.**

**Precedence:** R2 changes only what it names. Everything else in R1 (`8cc5168b…`) stands. Where R2 and an earlier document conflict, R2 governs (§5.2).

**Labels:** DERIVED / COMPUTED / OBSERVED / DOCUMENTED / ASSUMED / CONDITIONAL / UNVERIFIED / UNBOUNDED, used as in every earlier document. Model agreement is not verification.

---

## 0. Disposition

| # | Required change (dispatch) | R2 result | Section |
|---|---|---|---|
| 1 | Supersession completeness | **DONE**: a section-level register for Stage A Design D1 to D7 and Readiness D1 to D8 (including the D7 runbook, step by step), plus a catch-all rule for residual hourly text | §1 |
| 2 | Milestone counter | **DONE**: a positive allowlist, an explicit treatment of unknown states, an independent slot-grid detector for missing records, and the resets preserved | §2 |
| 3 | Probe-derived data contract | **DONE**: exact token parsing; numeric zero-volume detection; quote-derived bars kept; the 7/72 caveat; the price increment kept UNVERIFIED | §3 |
| 4 | FD-4 clarification | **DONE**: three quantities distinguished; no $60 cap; options without a default; cap definition kept | §4 |
| 5 | Freeze manifest | **DONE (pre-freeze form)**: the document set, the precedence, the A0.3-13 trace and the probe evidence hashes. **No final hash list** | §5 |
| — | Conflicts found while doing 1 to 5 | **FLAGGED, not silently resolved**: S-1 to S-6 | §6 |

---

## 1. Supersession register (change 1)

### 1.1 Status vocabulary

| Status | Meaning |
|---|---|
| **RETAINED** | normative as written |
| **AMENDED** | normative, except the named values, which are replaced as stated |
| **REPLACED** | not normative; the named successor text governs in its place |
| **SUPERSEDED** | not normative and has no successor (the obligation is withdrawn) |
| **HISTORICAL** | a record of what was believed or planned at the time; never normative |

### 1.2 Catch-all rule for residual hourly text (normative)

In every document dated before R2, the following tokens are **non-normative wherever they occur**, whether or not this register lists the occurrence. Each has its replacement:

| Token or phrase | Replacement |
|---|---|
| `1Hour`, "hourly", "hour boundary", "hour-aligned" (`hour_aligned`) | `5Min`; aligned to a 5-minute boundary in UTC (`five_min_aligned`) |
| "56 hours", "51-hour window", "[t_k − 50h, t_k]" | ≥ 60 candles fetched; gap window [t_k − 250 min, t_k] |
| "t + 1h + settle", "floor_hour(…) − 1h", "HH:05" | t + 5 min + 60 s ≤ T_d; floor_5min(T_d − 60 s) − 5 min; T_d = :MM:00 + 60 s |
| settle "5 minutes" / `settle_min: 5` | 60 s / `settle_s: 60` |
| TTL "5 min", "issued + 5 min", single TTL "180 s" | the R1 §1 clocks: approval_deadline = created + 120 s; expires_at = min(issued + 60 s, created + 180 s) |
| quote freshness "60 s" / "61 s old" | 15 s / "16 s old" |
| "AUTHORIZED_SHADOW" (Stage A) | **removed**: Stage A has no authorization (R1 §1). The lifecycle is PROPOSED → policy result → SHADOW_EXPIRED at created + 180 s |

A pre-R2 sentence that contains one of these tokens is read with the replacement substituted. **If the substitution leaves the sentence incoherent, the sentence is void and a finding must be raised.** It must not be interpreted.

### 1.3 Stage A Design v0.1 (`3444db48…`)

| Section | Status | Governing text | Note |
|---|---|---|---|
| Header, SA-FD-1 to SA-FD-8 | **REPLACED** | Readiness D2 register (FD-1 to FD-9), via the S-4 map | SA-FD numbers are not used for decisions |
| D1 §1.1 Inputs | **AMENDED** | Amendment v0.2 §1 | "1-hour" → 5Min. Everything else retained |
| D1 §1.2 Indicators | **RETAINED** | — | exact sums; D = 5·S20 − 2·S50 |
| D1 §1.3 Crossover semantics | **RETAINED** | — | literal; pending FD-2 |
| D1 §1.4 Edge cases | **RETAINED** | — | — |
| D1 §1.5 Signal to proposal | **RETAINED** | — | pending FD-3 |
| D1 §1.6 Price and size | **REPLACED** | R2 §4 (and §3.5 for increments) | the fee 0.25% becomes DOCUMENTED (tier 1 taker), still UNVERIFIED on paper; the limit-price timing is corrected (S-2) |
| D2 §2.1 Source | **AMENDED** | Amendment v0.2; probe report | `1Hour` → `5Min`; window ≥ 60 candles; keyless access **OBSERVED** working (one probe, 200 OK), so the "blocked" branch is HISTORICAL |
| D2 §2.2 Required fields | **AMENDED** | R2 §3.2 | parsing rule replaced; fields retained |
| D2 §2.3 Timestamp and completed-candle rules | **REPLACED** | R1 §2 "Expected candle"; R2 §3.1 | start-label convention OBSERVED for 5Min (one probe); forming-bar exclusion (P-3) |
| D2 §2.4 Missing and duplicate | **AMENDED** | R1 §2 | window in 5-minute steps; rules retained |
| D2 §2.5 Precision | **REPLACED** | R2 §3.2 | — |
| D2 §2.6 Quote-derived bars | **AMENDED** | R2 §3.3 | detection becomes numeric; kept in the input |
| D2 §2.7 Revision | **REPLACED** | R1 §2 "Revision of an accepted bar" | — |
| D2 §2.8 Failure behaviour | **AMENDED** | R1 §1; R2 §3.4 | quote 60 s → 15 s, at four checkpoints; malformed numeric value added (§3.4) |
| D3 §3.1 Storage | **RETAINED** | — | — |
| D3 §3.2 Schema | **AMENDED** | R2 §1.5 field delta | — |
| D3 §3.3 Illustrative example | **HISTORICAL** | — | invented hourly values; never a fixture |
| D4 Walkthrough | **AMENDED** | R1 §1, §2; R2 §1.2 | step 3 validation as in R1 §2; the AUTHORIZED_SHADOW state removed |
| D5 Readiness checklist | **SUPERSEDED** | Readiness D1 and D2; R2 §5.4 | its hourly UNVERIFIED rows are HISTORICAL; the 5Min equivalents are in §3 |
| D6 §6.1 U1 to U4e, U7, U9, U10, U12, U13, U14 | **RETAINED** | — | — |
| D6 U5, U8 | **REPLACED** | Amendment v0.2 §3 | 5Min values |
| D6 U6, U11 | **AMENDED** | Amendment v0.2 §3 | 5-minute steps |
| D6 U15, U16 | **AMENDED** | Amendment v0.2 §3; R1 §1 | U16 now tests the R1 clocks, not a single 180 s TTL |
| D6 U17 to U23 | **RETAINED** (added by R1 §8) | — | — |
| D6 U24 to U27 | **NEW** | R2 §7 | — |
| D6 §6.2 X1 to X11 | **AMENDED** | R1 §1 | any X case using a 60 s quote age or a 5-minute TTL uses the R1 values |
| D7 "Minimum to run" items 1 to 3 | **RETAINED** | — | still not authorized (FD-5) |
| D7 "Can stay manual": hourly manual trigger | **REPLACED (flagged)** | **S-1 / FD-7** | not viable for 30 consecutive 5-minute cycles |
| D7 "Must be deferred": scheduler | **REPLACED (flagged)** | **S-1 / FD-7** | conflicts with the strict counter |
| D7 "Must be deferred": all other items | **RETAINED** | — | — |
| D7 "Can stay manual": increments from documentation | **AMENDED** | R2 §3.5 | Stage A only, labelled UNVERIFIED |

### 1.4 First-Trade Readiness D1 to D8 (`e45c82a2…`)

| Section | Status | Governing text | Note |
|---|---|---|---|
| Bottleneck / next step (1Hour probe plan) | **HISTORICAL** | probe report `f6642894…` | the probe was run at 5Min (FD-1 exercised) |
| D1 dependency map | **AMENDED** | R1 §6 | rows 1.3 and 3.3: see §3.1 and §3.5 |
| D2 founder register | **RETAINED** | — | FD-4 is clarified by R2 §4; FD-7 is reopened by S-1 |
| D3 A-4 (TIF) | **AMENDED** | R2 §4 option (c) | FOK stays contradictory and unused |
| D3 A-5 (increments) | **REPLACED** | R2 §3.5 | P-1 |
| D3 A-9 | **RETAINED** | — | with R1 §2 |
| D3 other rows | **RETAINED** | — | — |
| D4 build plan | **RETAINED** | — | not authorized |
| D5 venue report, increment row | **AMENDED** | R2 §3.5 | the DOCUMENTED values are kept as documentation, **not** as verified venue facts |
| D6 G-07 readiness matrix | **AMENDED** | R1 §3 | the "authorization with TTL" row reads "with the R1 §1 clocks and the A0.3-13 approval predicate" |
| D7 preconditions | **RETAINED**, plus one added | R2 §3.5 | added: asset metadata read **and** each increment matches the policy file, otherwise STOP |
| D7 step 1 | **AMENDED** | R1 §2 | "the hourly cycle" → the 5-minute cycle (cycle_id, overrun rules) |
| D7 step 2 | **RETAINED** | — | it must also finish within the approval clock (S-1 note) |
| D7 step 3 | **RETAINED** | — | at the proposal-time quote (R1 §1 checkpoint a) |
| D7 step 4 | **REPLACED** | R1 §1, §3 | the authorization is issued only after approval; expires_at = min(issued + 60 s, created + 180 s) |
| D7 step 5 | **REPLACED** | R1 §1, §3 | the approval is recorded **before** issuance, by approval_deadline = created + 120 s, and bound to the A0.3-13 fields |
| D7 step 6 | **AMENDED** | R2 §3.5, §4 | increments from the metadata read at Stage B; TIF per FD-4 option |
| D7 step 7 | **AMENDED** | R1 §1 | fresh-quote checks (c) and (d) added |
| D7 steps 8, 9, 11, 12 | **RETAINED** | — | — |
| D7 step 10 | **AMENDED** | R2 §4 | the remainder is cancelled at expires_at (GTC) or immediately by the venue (IOC) |
| D7 stop conditions | **REPLACED** | R1 §6 STOP table | — |
| D7 "keep running hourly shadow cycles" | **AMENDED** | §1.2 | 5-minute cycles |
| D8 Go/No-Go | **HISTORICAL** | R2 §5.4 | — |

### 1.5 TER schema field delta (Stage A Design D3 §3.2)

| Field | Change |
|---|---|
| `params.interval` | `"5Min"` |
| `params.settle_min` | replaced by `settle_s: 60` |
| `checks.hour_aligned` | replaced by `five_min_aligned` |
| `checks.forming_bar_excluded` | new (t, and the raw token text of the excluded bar) |
| `cycle_id`, `slot_index`, `run_manifest_sha256` | new (§2) |
| `terminal_state` | new: one value from the §2.1 closed set |
| `raw_tokens` | new: for each bar, the original token text of o, h, l, c, v, vw (§3.2) |
| `zero_volume` | becomes a numeric test (§3.3) |
| `increment_source`, `increment_status` | new (§3.5) |
| `proposal_created_at`, `quote_checks[]` | new (R1 §1). Stage A records checkpoint (a) only |

### 1.6 Amendment v0.2 (`2df7fb74…`) and Spec v0.1 (`260f4f4f…`)

- **Amendment v0.2 §1:**
  - the rows for authorization TTL, founder approval window and shadow-outcome window are **REPLACED** by R1 §1;
  - the shadow-outcome window is now created + 180 s;
  - every other row is RETAINED.
- **Amendment v0.2 §2 and §3:** RETAINED as amended by R1 §5 and §8.
- **Spec v0.1:** the R1 §4 table is RETAINED and complete for v0.1. Its rule stands: v0.1 criteria not listed there (M1-2 to M1-7) remain in force.

---

## 2. Milestone counter (change 2)

### 2.1 Closed terminal-state set and counter effect (normative)

Every scheduled-cycle record has exactly one `terminal_state`, drawn from this closed set:

| terminal_state | Counter effect | Basis |
|---|---|---|
| HOLD | **+1** | R1 §5 |
| NO_ACTION | **+1** | R1 §5 |
| REJECTED | **+1** | R1 §5 (a correct policy rejection is a successful cycle) |
| SHADOW_EXPIRED | **+1** | R1 §5 |
| NO_DECISION, with a sub-reason in {FETCH_FAILED, INCOMPLETE_RESPONSE, INSUFFICIENT_HISTORY, DATA_GAP, DATA_CONFLICT, STALE_SERIES} | **reset to 0** | R1 §5 |
| CYCLE_OVERRUN | **reset to 0** | R1 §5 |
| SKIPPED | **reset to 0** | R1 §5 |
| CONCURRENT_INVOCATION | **reset to 0** | R1 §5 |
| BOUNDARY_FAIL | **reset to 0** | R1 §5 |

**Positive allowlist (normative):** only the four states marked +1 increment the counter. No other value increments it, under any spelling, case or sub-reason.

**Unknown or malformed states:** an absent `terminal_state`, a value outside the set, more than one value, an unparseable record, or a record failing its hash-chain check.
- **Does not increment** (required by the dispatch).
- **Resets to 0 and raises a finding.** *This is R2's proposal for hostile review, not a dispatch requirement.* It is flagged as S-5.
  - Rationale (DERIVED): a slot whose outcome cannot be determined is not a successful cycle.
  - Treating it as neutral, neither incrementing nor resetting, would let a corrupted record bridge two halves of a run into one "consecutive" sequence.

**Injected proposals** (`origin: INJECTED`) are not scheduled-cycle records. They neither increment nor reset the counter, and they never occupy or satisfy a slot.

### 2.2 Independent detection of missing scheduled-cycle records (normative)

The counter is a **derived quantity**. It is computed by the reconstructor from the run manifest and the records. **The harness's own counter value, if it writes one, is never evidence.** It is compared with the derived value, and a mismatch is a finding.

1. **Run manifest:** before the first cycle of a run, the founder commits `run_manifest` (instrument; T_d0; the planned number of slots N or "open-ended"; the harness hash) to the repository. Its SHA-256 is referenced in every TER of the run.
2. **Slot grid (DERIVED):** T_d(i) = T_d0 + 300·i seconds, for i = 0, 1, …. The expected candle is t_i = T_d(i) − 360 s.
   - T_d0 must equal :MM:00 + 60 s.
   - The expected cycle_id is cycle_id(i) = (BTC/USD, t_i).
   - Any invocation in [T_d(i), T_d(i+1)) selects t_i under the R1 §2 formula, so lateness within a slot does not change the identity (DERIVED).
3. **Accounting rule:** for each slot i up to the last slot whose T_d(i+1) has passed:

| Records with cycle_id(i) | Classification | Counter |
|---|---|---|
| exactly one, with a valid terminal_state | that state | per §2.1 |
| none | **MISSING_CYCLE_RECORD** (assigned by the reconstructor, never by the harness) | **reset to 0**; M1-2 completeness finding |
| more than one | **DUPLICATE_CYCLE_RECORD** | **reset to 0**; finding (it violates R1 §2 uniqueness) |

4. **Off-grid records:** a record whose cycle_id matches no slot → **OFF_GRID_RECORD**. It is a finding and does not increment.
5. **M1-1 is met** iff some 30 consecutive slots each classify as one of the four +1 states.
6. **End of the run:** a final slot is accounted for only after T_d(i+1) has passed. A slot still in progress is not counted.

**What this does not establish (stated):** the grid proves only that a record exists for each slot. It does not prove that the record's content is true. Content is checked by the blind reconstruction (R1 §5).

### 2.3 Consequence for operations (flagged, S-1)

A strict grid with a reset on MISSING_CYCLE_RECORD means that a hand-triggered run must hit 30 consecutive 5-minute slots, about 2.5 hours, with no miss. See S-1. **The counter rule is not relaxed to accommodate this.**

---

## 3. Probe-derived data contract (change 3)

### 3.1 Forming-bar exclusion (RETAINED; U17)

- The probe **OBSERVED** that the response includes the forming bar (P-3; one probe).
- Any bar with t + 5 min + 60 s > T_d is excluded, and is recorded with its raw token text. It is never used.
- The expected-candle rule is R1 §2.
- **U17 is retained unchanged.**

### 3.2 Exact decimal parsing from the original tokens (normative)

1. The raw response bytes are the artifact. They are stored before parsing, and their SHA-256 is recorded.
2. **Every numeric value is converted to an exact decimal from the original JSON number token text.**
   - No binary floating-point value may exist at any point in the path: harness, policy evaluation or reconstructor.
   - ILLUSTRATIVE, not an implementation instruction: a JSON parser hook that hands the token string to a decimal constructor, such as Python's `json.loads(…, parse_float=Decimal, parse_int=Decimal)`.
3. Exponent forms (for example `1.2e-05`) are valid tokens and are converted exactly.
4. The TER records each token's text (`raw_tokens`) alongside the decimal.
   - Canonical comparison for the revision check (R1 §2) uses the **token text**, not a re-serialized value.
   - So `0` and `0.0` in the same position count as a **difference** in bytes. **Whether that is a SOURCE_REVISION or a representation change is recorded, not assumed.**
5. A display value may be rounded (8 dp, round-half-even). Decisions use exact sums (Stage A Design D1 §1.2).

### 3.3 Zero-volume bars (normative)

- **zero_volume ⇔ decimal(v) = 0, compared numerically.** This covers `0`, `0.0`, `0.00000000`, `0e0` and `-0`. A textual or regex match is not an acceptable test.
- The TER records zero_volume for each of the 51 candles, with the raw token.
- **Quote-derived bars stay in the strategy input** (Stage A Design §2.6, retained). They are flagged, never filtered. **Only the founder can change this,** because filtering would change the strategy.
- **The probe's 7/72 figure:**
  - it was a pattern count over the raw text, not a numeric count;
  - if any zero volume was written in another form (for example `0.0`), it was missed;
  - so **7/72 may be an undercount**. The true count in that sample is **UNVERIFIED**;
  - R2 does not compute it (no execution was authorized). Its correction is an item for the eventual executed test record, not for this document.

### 3.4 Malformed numeric values (AMENDED: a new row in §2.8; proposed, flagged in S-5)

- Conditions: a non-numeric or non-finite token where a number is required; a close ≤ 0; v < 0.
- Result: **NO_DECISION (sub-reason FETCH_FAILED, detail MALFORMED_VALUE)**. The counter resets (§2.1).
- *Rationale:* Stage A Design §2.8 already maps "malformed JSON" to FETCH_FAILED. This row extends it to well-formed JSON that carries impossible values. No new terminal state is added.

### 3.5 Price and quantity increments (normative)

- **Price increment: UNVERIFIED.**
  - DOCUMENTED: the support table gives 1.
  - OBSERVED (P-1): quote prices with cents (2 dp) and bar closes with up to 4 dp.
  - The two are inconsistent.
- **No order increment may be inferred from quote or bar precision.** Market-data precision is evidence about the data feed, not about the venue's order rules.
- **Quantity increment and minimum:** DOCUMENTED 0.0001 and contradicted (1/price). **UNVERIFIED.**
- **Stage A** (shadow; no orders): proposals are rounded using the support-table values.
  - Every TER records `increment_source: "support_table_DOCUMENTED"` and `increment_status: "UNVERIFIED"`.
  - Shadow figures computed this way carry the label CONDITIONAL on those increments.
- **Stage B:**
  - the pre-flight reads the BTC/USD asset metadata with the paper credentials (FD-8);
  - it records the price increment, quantity increment and minimum order size as OBSERVED;
  - it compares them with the policy file;
  - **any mismatch or absent field → STOP; no order.** This is a precondition added to the Readiness D7 runbook (§1.4).
- **Consequence noted, not decided (S-6):** if the increment really is $1 and a BUY limit is rounded **down** (Stage A Design §1.6), the limit sits below the ask. The order may then rest rather than execute against the ask. This bears on FD-4 (§4).

---

## 4. FD-4 clarification (change 4)

### 4.1 Three different quantities (normative definitions)

| Quantity | What is known | Label |
|---|---|---|
| **Displayed top-of-book size** | about 0.00099 BTC (≈ $60) on each side, at one instant | **OBSERVED, one probe** (P-2); not a distribution |
| **Total available liquidity** (depth beyond the top level) | **not observed.** The probe fetched the latest quote only | **UNVERIFIED** |
| **Paper-fill behaviour** | paper fills are simulated against the NBBO quote, with random partial fills | **DOCUMENTED** |
| Whether the paper simulator caps a fill at the displayed size | unknown | **UNVERIFIED** |
| Planned BUY size | ≈ $145 (≈ $150 cap less fee) | DERIVED from the cap |

**Displayed size is not total liquidity, and neither one is paper-fill behaviour.** The ≈ $60 observation shows only that an order of ≈ $145 *may* be larger than the displayed best ask.

### 4.2 Rules (normative)

- **No $60 cap is imposed.** R2 does not turn one OBSERVED snapshot into a sizing limit.
- **The $150 cap** = the **maximum total reserved spend including fees** (R1 §7, retained):
  - qty × limit × (1 + fee_rate) ≤ min($150 − current BTC exposure, available cash);
  - qty is rounded **down** to the quantity increment;
  - fee_rate is DOCUMENTED (tier 1 taker 0.25%); whether it applies on paper is UNVERIFIED. The higher (taker) rate is used for the reservation.
- **The limit price is fixed at proposal creation** from the proposal-time fresh quote (checkpoint a), and is **immutable** afterwards (R1 §1 rule 2).
  - At issuance, LP-CONSUME and LP-PRESEND, the fresh quote is a **check only**.
  - This corrects the R1 §7 FD-4 wording "price from a fresh quote at authorization issuance" (see S-2).
- **The EXIT quantity is the reconciled held quantity** (L-2), not the BUY's ordered quantity.
  - DOCUMENTED: the buy fee is taken in the received asset, so the held quantity is less than the filled quantity.
  - This refines Stage A Design §1.6 "the entire held quantity" by stating its source; it is not a new rule.

### 4.3 The founder decision (preserved; no default proposed by R2)

| Option | Behaviour | Consequence |
|---|---|---|
| **(a)** full size, partial fills accepted | GTC limit; any unfilled remainder cancelled by Sentinel at expires_at | the position can be smaller than planned; R16 one-live rule unaffected |
| **(b)** cap at the displayed best-ask size | qty = min(cap qty, displayed ask size at checkpoint a) | the order may be below the venue minimum → **no order (REJECTED)**; size then depends on a single quote snapshot |
| **(c)** full fill or nothing | IOC, where a partial IOC fill is still possible; FOK is not used because its support is contradictory | the order may fill partially or not at all; nothing rests |

- **FD-4 remains OPEN.** The earlier proposed default (Readiness D2) is retained as a record, but no R2 default is set between (a), (b) and (c), as the dispatch requires.
- The founder's decision on larger-than-displayed orders and on partial fills is preserved as the founder's.

---

## 5. Freeze manifest (change 5; pre-freeze form)

### 5.1 Document set

Hashes are SHA-256 of the files as pushed, recomputed for R2 (COMPUTED). **They are not a freeze list** (§5.4).

**Normative documents (SL-PT-001):**

| Document | SHA-256 |
|---|---|
| Spec v0.1 | `260f4f4fead2ec3d9f40256ef3d76499258db16ddf8cb975e1e3814e66c17edb` |
| Stage A Design v0.1 | `3444db48fad8623acb2c6e15350b89abac8e6534809deb9f67f15ed1600c2ff3` |
| First-Trade Readiness D1 to D8 | `e45c82a2cd401a3b6d2878c3aa154c24dcb9ea7a6870ac76a830ba4ed1dc80df` |
| Amendment v0.2 (5Min) | `2df7fb74b1aaf3992cf13ae5a4a71a9bf299f2f1dd3bc189b539de443de4b38b` |
| Revision R1 | `8cc5168b41fc90323f22bc59ebabcccbfa323c1b3cda826702a06744e34ce8fc` |
| Revision R2 (this document) | recorded by the push (a document cannot carry its own hash) |

**Normative documents (G-07):**

| Document | SHA-256 |
|---|---|
| Draft 0.1 | `55141ae662579251e1426a8029f38a9a816d983f23573e8da460f4e03f8bf4a5` |
| Draft 0.2 | `f0404b719f44c5beca12e6ad4a3cc4e58e50aca3da0046393419e9c812606c82` |
| Draft 0.2a | `b87ac1c0820698f4cd86eb35757ae4dd041b9c1e3bfeccb20f95cd82a7ab6aa1` |
| Draft 0.3 | `f22ee85bb4cb642b14ab7ede6a187e4af0183c09fb0914b6a1dc1e8f884fe1ef` |

**Evidence only, not normative.** The probe artifacts in `probe-A0/` and the probe report are OBSERVED evidence; they define nothing. Hashes are as recorded by the founder's PowerShell (upper case; compare case-insensitively).

| Artifact | SHA-256 |
|---|---|
| Probe report | `f6642894ccc9c6526aea4ebfc73db4c5dbdc5f94bf984039bb0b7e68b7742782` |
| bars_body.json | `E3640E5C904B2442913F0511046E9BCF536E4F1B685D73CAF6586CBC0736BADF` |
| bars_headers.txt | `5A6A76FB67CA4B5D1B57A0D7AD7947F24B8E455ED87275187590F87F1396D30E` |
| quote_body.json | `D9C34B0D4CD6D210C13F2C2204BDEF03007C33B1E27A3AD47BAEB80953103B5C` |
| quote_headers.txt | `741DFAD8A2C72A2DC8DC807D71EB7DA82D95C42F3DE08DFA51EAFB018F094A4D` |
| probe_meta.txt | `40CA026FD4B767F832E1895BD57505359909A4485C6DF868BFDEAB46A116450E` |

**Excluded from the set:**
- dispatches, which are instructions to reviewers and not specification;
- EAR and EIVI-1 documents, which are separate workstreams;
- sealed EIVI files, which are never pushed.

### 5.2 Precedence (normative)

- **SL-PT-001 chain:** R2 > R1 > Amendment v0.2 > Readiness D1 to D8 > Stage A Design v0.1 > Spec v0.1.
- **G-07 chain:** Draft 0.3, together with A0.3-13 as stated in R1 §3, > 0.2a > 0.2 > 0.1.
- **Between the chains:**
  - G-07 governs **execution-boundary semantics**: lifecycle points, K3 and K5 duties, invariants I1 to I10, and LP-ISSUE, LP-CONSUME, LP-WAL and LP-PRESEND;
  - SL-PT-001 governs **strategy, data and policy**: signals, the data contract, R1 to R16, the milestone and sizing.
  - Where a passage touches both, the SL-PT-001 text must be read as an instance of the G-07 semantics. **If it cannot be, that is a finding, not a precedence question.**
- **Evidence never overrides normative text.** It can only make a statement in it OBSERVED, or contradict it, which is a finding.

### 5.3 A0.3-13 trace (the approval predicate; no G-07 redesign)

| Item | Where |
|---|---|
| Defined | SL-PT-001 R1 §3 (a proposed G-07 amendment) |
| Issuance predicate | G-07 lifecycle point 2, **LP-ISSUE** (Draft 0.1 §10.1, unchanged by 0.3). K3 commits an authorization only if a matching, timely, unrevoked approval record exists |
| Consumption predicate | point 5, **LP-CONSUME** (Draft 0.3 §1). The eligibility term additionally requires that approval record to still exist unrevoked |
| Provenance | **I9** (Draft 0.3 §4): the authorization's provenance record includes the approval-record reference |
| Point 3 (presentation from K2) | already superseded by the polling executor (Draft 0.3 §2). A0.3-13 adds nothing there |
| Not touched | LP-WAL, LP-PRESEND, I1 to I8, I10, the FD-G decisions |
| Falsifier | an ACTIVE authorization without a matching, timely approval record (R1 §3); tests U21, U22 |
| Status | **CONDITIONAL**: proposed text; it enters G-07 only at the founder's freeze; approver authentication is UNVERIFIED until Stage B |

### 5.4 Freeze status and gating

**Status: NOT FROZEN. No final hash list is published.** The freeze list is published only when each item below is resolved, or explicitly deferred by the founder with its consequence recorded:

| FD | Open question | Consequence if deferred (to be recorded at deferral) |
|---|---|---|
| FD-2 | crossover at equality: literal vs strict-regime | Stage A runs on the literal reading. U4c and U4d expect literal results. Any later change makes the shadow record non-comparable for touch cases |
| FD-3 | BUY while long; signals while an order is open or AMBIGUOUS | Stage A uses the Readiness D2 proposed default (NO_ACTION / BLOCKED_OPEN_ORDER) *as a labelled assumption*. **Stage B cannot start under a deferral** |
| FD-4 | options (a), (b) or (c) (§4.3) | Stage A shadow sizing uses option (a) arithmetic, labelled ASSUMED; no fill semantics are exercised. **Stage B cannot start under a deferral** |
| FD-6 | the independent reconstructor | the R1 §5 blind-reconstruction protocol cannot start, so **M1-6 cannot be met**. The harness may still run, but M1 is not claimable |
| FD-7 *(R2 recommends adding)* | where the harness runs and the cycle trigger (S-1) | under a manual trigger, M1-1 may be unreachable in practice. That is not a defect of the counter |

When the gating is satisfied, the freeze record lists (a) every §5.1 hash, including R2's and those of any later revision, and (b) the decision record for each gated FD. **It is committed before the harness exists** (R1 §5 step 1; FD-5 condition c).

---

## 6. Conflicts found (flagged; none resolved silently)

| ID | Conflict | R2 position | Who decides |
|---|---|---|---|
| **S-1** | **Scheduler versus the strict counter.** Stage A Design D7 defers the scheduler and keeps hand triggering (FD-7 default: manual). Thirty consecutive 5-minute slots (≈ 2.5 h) with a reset on any missing record are impractical to hit by hand. Readiness D7 step 2 (reconstruction before approval) must also fit inside the 120 s approval clock at Stage B | **Flagged.** Options for the founder, with no R2 default: (i) authorize a minimal local timer as part of the FD-5 harness scope, a *trigger only* with no logic of its own and its invocations logged; (ii) keep hand triggering and accept that M1-1 may take many attempts; (iii) change the milestone, which is a founder decision against GPT's adopted strict rule. Separately: Stage B feasibility of reconstruction within 120 s is **UNVERIFIED** | founder (FD-7; FD-5 scope) |
| **S-2** | R1 §7 FD-4 text "price from a fresh quote at authorization issuance" conflicts with R1 §1 rule 2 and §3: the approval binds the limit price, and approval precedes issuance | **Corrected in R2 §4.2:** the price is fixed at proposal creation; later quotes are checks only. Open to hostile review | reviewers; founder at freeze |
| **S-3** | Stage A Design D3 and D4 use an AUTHORIZED_SHADOW state; R1 §1 says Stage A has no authorization | **Removed** (§1.2) | — (follows R1) |
| **S-4** | Two numbering schemes: SA-FD-1 to 8 (Stage A Design) and FD-1 to 9 (Readiness) | Map: SA-FD-1→FD-2; SA-FD-2→FD-3; SA-FD-3→FD-4; SA-FD-4 (settle)→carried in amendment v0.2 as **60 s**. The founder chose the 5Min cadence; the 60 s value itself is a Claude proposal and is **confirmed only at freeze**; SA-FD-5→FD-7; SA-FD-6→**moot** (keyless OBSERVED); SA-FD-7→superseded by §3.5; SA-FD-8→FD-6. **Only FD numbers are used from R2 onward** | — |
| **S-5** | Two R2 proposals go beyond the dispatch text: unknown states **reset** (the dispatch requires only no increment), and the malformed-value row | **Proposed and flagged.** Reviewers may reject either | reviewers; founder |
| **S-6** | With a $1 increment, rounding a BUY limit down puts it below the ask (Stage A Design §1.6) | **Recorded, not decided.** It interacts with FD-4 and with P-1 | founder (FD-4), after the Stage B metadata read |

---

## 7. New tests (added to Stage A Design D6; designed, none executed)

| ID | Test | Expected (DERIVED) |
|---|---|---|
| U24 | **zero-volume representations:** bars with v tokens `0`, `0.0`, `0e0`, `-0`, `0.00000001` | zero_volume true for the first four, false for the last; all bars kept in the input; tokens recorded |
| U25 | **decimal tokens:** closes with tokens such that binary float sums differ from exact sums, including exponent forms | D computed from tokens equals the hand-derived exact value; no float anywhere (checked by an injected float-trap fixture) |
| U26 | **counter allowlist:** a sequence of records with states from §2.1, plus `"hold"` (wrong case), `"HOLD "`, an absent state, two states, and an unknown `"OK"` | only the exact four allowlisted values increment; every other value does not increment and (if S-5 is accepted) resets, with a finding |
| U27 | **missing-record detection:** a run manifest with a slot grid; records for slots 0 to 40 with slot 17 absent, slot 23 duplicated and one off-grid record; the harness's own counter falsely reports 41 | the reconstructor classifies 17 as MISSING_CYCLE_RECORD and 23 as DUPLICATE_CYCLE_RECORD, both resetting the count; the off-grid record is a finding; the harness counter is reported as a mismatch; M1-1 is met only if 30 consecutive valid slots exist elsewhere |

---

## 8. Change log (for hostile review)

| # | Location | Change | Type | Driver |
|---|---|---|---|---|
| CL-1 | §1.1 to §1.2 | status vocabulary; catch-all token rule for residual hourly text, with a void-and-flag rule | new normative | dispatch item 1 |
| CL-2 | §1.3 | section-level register for Stage A Design D1 to D7 | new | item 1 |
| CL-3 | §1.4 | section-level register for Readiness D1 to D8, D7 runbook step by step | new | item 1 |
| CL-4 | §1.5 | TER field delta | new | items 1 to 3 |
| CL-5 | §1.6 | amendment v0.2 TTL, approval and shadow rows replaced by R1 §1 | clarification | item 1 |
| CL-6 | §2.1 | closed terminal-state set; positive allowlist; unknown state → no increment (+ proposed reset) | new normative | item 2; S-5 |
| CL-7 | §2.2 | run manifest; slot grid; MISSING / DUPLICATE / OFF_GRID classifications; the harness counter is non-evidentiary | new normative | item 2 |
| CL-8 | §3.1 | forming-bar exclusion and U17 retained | retained | item 3 |
| CL-9 | §3.2 | exact decimal from token text; token-text comparison for revision | replaces Stage A Design §2.5 | item 3 |
| CL-10 | §3.3 | numeric zero-volume test; quote-derived bars kept; 7/72 possible undercount | amends Stage A Design §2.6 | item 3 |
| CL-11 | §3.4 | malformed numeric values → NO_DECISION / FETCH_FAILED | proposed | S-5 |
| CL-12 | §3.5 | increment UNVERIFIED; no inference from quote precision; Stage A labelled rounding; Stage B metadata STOP | replaces Readiness D3 A-5 | item 3; P-1 |
| CL-13 | §4.1 | displayed size / total liquidity / paper-fill behaviour distinguished | clarification | item 4; P-2 |
| CL-14 | §4.2 | no $60 cap; $150 reserved spend including fees retained; the price fixed at proposal creation; EXIT quantity is the reconciled holding | clarification + correction | item 4; S-2 |
| CL-15 | §4.3 | FD-4 options (a), (b), (c), no default; FD-4 stays open | preserved | item 4 |
| CL-16 | §5.1 to §5.2 | document set, evidence hashes, precedence within and between chains | new | item 5 |
| CL-17 | §5.3 | A0.3-13 traced to LP-ISSUE, LP-CONSUME and I9; nothing else in G-07 touched | trace only | item 5 |
| CL-18 | §5.4 | gating table with deferral consequences; FD-7 recommended for gating | new | item 5; S-1 |
| CL-19 | §6 | S-1 to S-6 flagged | flags | — |
| CL-20 | §7 | U24 to U27 designed | tests (not executed) | items 2, 3 |

---

## 9. Preserved, unchanged

- **Epistemic labels:**
  - every prior label stands;
  - R2 changes a label only where new evidence or a contradiction is cited: keyless access → OBSERVED; 5Min start-label convention → OBSERVED (one probe); price increment stays UNVERIFIED.
- **Open founder decisions:** FD-2, FD-3, FD-4, FD-6; FD-5 (conditional, per R1 §7); FD-7 (reopened by S-1); FD-8; FD-9, including FD-G13, FD-G16, FD-G17 and FD-G18.
- **Unresolved disagreements:**
  - R1's recorded positions stand;
  - S-2 and S-5 are R2 positions open to rejection;
  - the Gemini challenge on R1 is **still pending**, and R2 does not anticipate it.
- **Standing constraints:**
  - no implementation, credentials, trading connection or orders without explicit founder authorization;
  - sealed files stay off GitHub;
  - no change to frozen baselines;
  - the founder retains final authority.
