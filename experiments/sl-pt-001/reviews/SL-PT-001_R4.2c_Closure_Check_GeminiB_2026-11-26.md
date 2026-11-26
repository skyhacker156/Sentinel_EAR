### Exposure Statement

I previously reviewed SL-PT-001 R4.1 and performed closure checks on the R4.2 and R4.2a excerpts. I have not seen any other reviewer's review.

---

### Closure Classification of R4.2a Findings (B4-01 to B4-03)

* **B4-01 (Ambiguity in V1–V11 evaluation behavior on failure): CLOSED.**
The V1–V11 rule explicitly states that V1 to V11 are evaluated in order without short-circuiting and all failures are recorded, subject to one dependency rule: if V1 or V2 fails, V3 to V11 are `NOT_EVALUATED (DATA_INVALID)`, whereas if V1 and V2 pass, every check from V3 to V11 is evaluated even if an earlier one fails (U111). Row 4 of the TER table cross-references this rule directly ("V results per the §4.7 rule (evaluated, or NOT_EVALUATED (DATA_INVALID) after a V1 or V2 failure)").
* **B4-02 (Ambiguity in Q1–Q5 states under `QUOTE_INVALID`): CLOSED.**
The TER table now separates `QUOTE_INVALID` into its own dedicated sixth row, specifying that Q1 to Q5 are evaluated (`PASS`/`FAIL`, with at least one `FAIL`, and all five `FAIL` when the quote is absent due to `NO_RESPONSE`), while `proposal` is `null` and `rule results` is `[]`.
* **B4-03 (`OFF_RUN` handling in §11.2 Row 1 vs. U77): CLOSED.**
Section 11.2 now includes an explicit normative note below the 9-row table explaining that `OFF_RUN` records carry no slot index (§6.2), so they never match a slot row, and that any integrity failure in an `OFF_RUN` record is reported by chain verification in §11.3 step 1 (which explicitly checks `prev_hash`, `hash`, and record schema for every record of every type, including `OFF_RUN`, verified by U114).

---

### Verification of R4.2c Changed Text

#### 1. V1–V11 evaluation rule vs. U111

The V1–V11 evaluation rule and U111 are **internally consistent**:

* When V1 fails (`U111(a)`) or V2 fails (`U111(b)`), the dependency rule triggers and sets V3 to V11 to `NOT_EVALUATED (DATA_INVALID)`.
* When V1 and V2 pass (`U111(c)`), no short-circuiting occurs; V3 to V11 are all evaluated (`PASS`/`FAIL`), recording `V7 = FAIL` without skipping V8–V11.

#### 2. Request objects, empty-array collections, and the seven-row terminal-path table vs. the closed-schema rule and U108, U112, U113

* **Closed-schema consistency:** The specification defines exact structural rules for request objects (`null` when never issued; `{url, sent_at, received_at, outcome}` when issued, with `received_at: null` and `outcome: "NO_RESPONSE"` when unanswered), collections (always present as JSON arrays, `[]` when empty), and scalars (`null` is the only non-string scalar permitted).
* **Path-by-path determination:**
* **Row 1 (`V12a fails`):** Fully determined (`V12a = FAIL`, requests/artifacts/clock/computed `null`, all other checks `NOT_EVALUATED (V12A_FAILED)`, collections `[]`).
* **Row 2 (`bars request: no response`):** Fully determined (`bars_request` with `outcome = NO_RESPONSE` and `received_at = null`, `quote_request = null`, artifacts `null`, clock fields `null` except `t_send`, `V12a = PASS`, `V12b`/V1–V11/Q1–Q5 `NOT_EVALUATED (FETCH_FAILED)`, computed `null`, collections `[]`), matching U112.
* **Row 3 (`V12b fails`):** Fully determined (`bars_request`, bars artifact, clock fields present; `V12a = PASS`, `V12b = FAIL`; `quote_request` and quote artifact `null`; V1–V11/Q1–Q5 `NOT_EVALUATED (V12B_FAILED)`; computed `null`; collections `[]`).
* **Row 4 (`a V1 to V11 failure`):** Fully determined (both requests and artifacts present, V1–V11 per §4.7 rule, Q1–Q5 `NOT_EVALUATED (DATA_INVALID)`, computed `null`, collections populated up to bar-store evaluation with `rule results = []`).
* **Row 5 (`HOLD or NO_ACTION`):** Fully determined, including when `quote_request.outcome = NO_RESPONSE` per U113(a) (everything through `mapping` present, `proposal = null`, Q1–Q5 `NOT_EVALUATED (NO_PROPOSAL)`, `rule results = []`).
* **Row 6 (`QUOTE_INVALID`):** Fully determined, including when `quote_request.outcome = NO_RESPONSE` per U113(b) (`quote_artifact = null`, Q1–Q5 all `FAIL`, `proposal = null`, `rule results = []`).
* **Row 7 (`a proposal (REJECTED, SHADOW_EXPIRED)`):** Fully determined (`everything` present).


* One minor wording note exists in Row 2 regarding `t_send` vs. `bars_request.sent_at` (see **B5-01** below), which does not create ambiguity in the JSON schema or block freeze.

#### 3. Exact recomputation of U98 endpoints

Relative to $D = 0$, with $t_{\text{send}} = -1\text{ s}$ and formulas $\theta_{\text{low}} = D - t_{\text{recv}}$, $\theta_{\text{high}} = D + 1\text{ s} - t_{\text{send}}$:

* **Case 1 ($t_{\text{recv}} = 2\text{ s} - 1\text{ ns}$):**
* Round trip $= t_{\text{recv}} - t_{\text{send}} = (2\text{ s} - 1\text{ ns}) - (-1\text{ s}) = 3\text{ s} - 1\text{ ns} < 3\text{ s}$ (Condition 3 passes).
* $\theta_{\text{high}} = 0 + 1\text{ s} - (-1\text{ s}) = +2\text{ s} \le +2\text{ s}$ (Condition 4 upper bound passes).
* $\theta_{\text{low}} = 0 - (2\text{ s} - 1\text{ ns}) = -2\text{ s} + 1\text{ ns} \ge -2\text{ s}$ (Condition 4 lower bound passes).
* Result: `pass`. **Matches U98 exactly.**


* **Case 2 ($t_{\text{recv}} = 2\text{ s}$):**
* Round trip $= 2\text{ s} - (-1\text{ s}) = 3\text{ s}$ (violates Condition 3: $t_{\text{recv}} - t_{\text{send}} < 3\text{ s}$).
* $\theta_{\text{high}} = +2\text{ s}$, $\theta_{\text{low}} = -2\text{ s}$ (satisfies Condition 4).
* Result: `BOUNDARY_FAIL (condition 3)`. **Matches U98 exactly.**


* **Case 3 ($t_{\text{recv}} = 2\text{ s} + 1\text{ ns}$):**
* Round trip $= (2\text{ s} + 1\text{ ns}) - (-1\text{ s}) = 3\text{ s} + 1\text{ ns}$ (violates Condition 3).
* $\theta_{\text{high}} = +2\text{ s}$, $\theta_{\text{low}} = 0 - (2\text{ s} + 1\text{ ns}) = -2\text{ s} - 1\text{ ns} < -2\text{ s}$ (violates Condition 4).
* Result: `BOUNDARY_FAIL (conditions 3 and 4)`. **Matches U98 exactly.**



#### 4. Section 11.2 table, `OFF_RUN` note, and Section 11.3 step 1 with U114

The §11.2 precedence table, the `OFF_RUN` note, §11.3 step 1, and U114 are **completely consistent and unambiguous**. Because `OFF_RUN` records carry no slot index (§6.2), they never match any slot $i \in \{0 \dots N-1\}$ in §11.2. Meanwhile, §11.3 step 1 walks the entire hash chain from `GENESIS` and validates `seq`, `prev_hash`, `hash`, and record schema across *every* record type—explicitly including `OFF_RUN`—ensuring that any tampered byte or unknown field in an `OFF_RUN` record raises an integrity finding (U114).

---

### New Findings

* **B5-01**
* **Section:** §10.4 ("Unevaluated checks and absent artifacts" table, Row 2: `bars request: no response`)
* **Mechanism:** Row 2 states: `"both artifacts and all clock fields except t_send null (t_recv null, so θ is not computed)"`. Because the prose states that clock fields are `null` when they do not exist and `bars_request.sent_at` already records the send timestamp, leaving `t_send` populated in the top-level clock block when no response was received is slightly asymmetric with `t_recv`, `D`, `θ_low`, and `θ_high` all being `null`.
* **Consequence:** No functional ambiguity (Row 2 and U112 explicitly specify `t_send` non-null and the other four clock fields `null`), though implementers must remember not to null out the entire clock group on `NO_RESPONSE`.
* **Smallest correction:** None required for freeze; optionally note in the clock-fields bullet that `t_send` is populated whenever the bars request is issued, even if `outcome = NO_RESPONSE`.
* **Severity:** Informational / Editorial
* **Blocks Stage A freeze:** No



---

### Verdict

**CLOSED** — All prior findings (B4-01 through B4-03) are cleanly closed. The V1–V11 non-short-circuiting rule, the closed-schema request/collection/null representation across all seven terminal paths, the U98 boundary arithmetic, and the `OFF_RUN` chain-verification coverage in §11.2/§11.3 are completely consistent and verified against U98, U108, and U111–U114. Ready for Stage A freeze.