Prior exposure: I reviewed R4.1; I have not seen any other reviewer's review of R4.1.

---

### 1. Section-by-Section Closure Evaluation

#### A. §5.6 Clock Source (R4-11)

* **(1) Internal consistency & implementability:** Internally consistent and implementable as written, provided `D` is parsed to exact integer nanoseconds (`Date_epoch_seconds × 10^9`) and `t_send` / `t_recv` use a wall-clock source (`CLOCK_REALTIME` in ns) rather than a monotonic clock, since `θ = data-host clock − harness clock` requires comparing epoch-anchored wall clocks. The interval math is sound: if server time $t_s \in [D, D + 1\text{ s})$ and $t_{\text{send}} \le t_s \le t_{\text{recv}}$, then $D - t_{\text{recv}} < t_s - t_s' \le \theta < (D + 1\text{ s}) - t_{\text{send}}$.


* **(2) False or misclassified results:** Under `A-CLK` (no caching/rewriting proxy), no false pass is possible; slow HTTP round trips ($\ge 3\text{ s}$) cleanly fail closed via $\theta_{\text{high}} - \theta_{\text{low}} = 1\text{ s} + (t_{\text{recv}} - t_{\text{send}}) > 4\text{ s}$. One minor edge defect (**B3-01**): §5.6 does not explicitly state what happens when `D` is missing, malformed, or `t_recv < t_send` (backward wall-clock NTP step during the HTTP call)—though `t_recv < t_send` should fail closed (`BOUNDARY_FAIL`), if `t_recv < t_send` occurs while `D` happens to satisfy $\theta_{\text{low}} \ge -2\text{ s}$ and $\theta_{\text{high}} \le +2\text{ s}$, a backward clock step would pass `V12b` silently.


* **(3) Stage B dependency:** None. Stage B timing (`FD-G18`) is cleanly isolated and deferred.


* **(4) Claim strength vs. stated assumptions:** Properly scoped. It explicitly states that `V12b` bounds the harness clock against the *data host's* clock only and marks Stage A timing claims `CONDITIONAL` on data-host UTC accuracy (`§15 U-T2`).



#### B. §8.1.1 Stage A Sizing and Shadow Reservation

* **(1) Internal consistency & implementability:** Mostly implementable, with two internal/cross-reference gaps (**B3-02**, **B3-03**):
1. `L` (limit price) is used in `q = floor(budget / (L × (1 + f_res)))` and `R = ceil(q × L × (1 + f_res))`, and `price_increment` is listed under Increment values, yet §8.1.1 never defines `L` or states its rounding rule (e.g., ask rounded down to `price_increment` for BUY, bid rounded up for EXIT).


2. `shadow reserved BTC` appears in `q_exit = floor to qty_increment of (shadow BTC − shadow reserved BTC)`, whereas the reservation rules only specify creating a USD reservation `R` on a passing proposal (and never define a BTC reservation object or when `shadow reserved BTC` is non-zero in EXIT fixtures).




* **(2) False or misclassified results:** Yes, if `L` is unrounded or rounded in the wrong direction before computing `q` and `R`, `q` and `R` become non-deterministic across implementations (**B3-02**). Also, the prose claim *"R ≤ budget ≤ $150.00 holds by construction (DERIVED: q × L × (1 + f_res) ≤ budget, and budget is on the cent grid)"* assumes `shadow_cash` is on the cent grid; if a manifest specifies `shadow_cash` with sub-cent decimals (e.g., `$500.005`), `budget` would not be on the cent grid.


* **(3) Stage B dependency:** The final bullet references *"The Stage B ledger (§8.2) reuses the formulas for q and R"*, which is a forward reference to Stage B text, though Stage A execution itself does not depend on §8.2.


* **(4) Claim strength vs. stated assumptions:** The derivation *"R ≤ budget ≤ $150.00 holds by construction"* is slightly stronger than its stated premises because it omits the premise that `shadow_cash` is an exact cent-grid USD value (and `L > 0`, `1 + f_res > 0`).



#### C. §11.2 Slot Classification

* **(1) Internal consistency & implementability:** Precedence ordering is clear and eliminates the `OVERRUN` vs `MISSING` ambiguity, **except for a structural contradiction between the classification table and the Invocation Consistency (`U77`) rule** (**B3-04**) and a precedence gap when both a `CYCLE_OVERRUN` and a `CYCLE` record exist for slot `i` (**B3-05**).
* **(2) False or misclassified results:**
* Under **B3-04**, row 2 classifies a slot with *"no CYCLE record, and an invocation-log line for slot i"* as `INCOMPLETE`, while `U77` states *"each invocation-log line must correspond to a chain record for its slot (a CYCLE, CONCURRENT_INVOCATION, CYCLE_OVERRUN or OFF_RUN record)... any mismatch is a finding"*. If a process crashes mid-cycle after writing an invocation-log line and before writing any chain record, row 2 classifies it as `INCOMPLETE` (already non-qualifying), while `U77` simultaneously flags it as an invocation-consistency mismatch finding—unclear whether `U77` intends to catch *unexplained* invocation lines (which row 2 already captures) or whether row 2 lacks an `OFF_RUN` / `CONCURRENT_INVOCATION` check.


* Under **B3-05**, row 1 (`a CYCLE_OVERRUN record for slot i → OVERRUN`) takes unconditional precedence over row 4 (`more than one CYCLE record → DUPLICATE`) and row 6 (`fails the schema, the chain...`). If a slot emits *both* a valid/invalid `CYCLE` record and a `CYCLE_OVERRUN` record (e.g., a race at the slot boundary), row 1 masks the `DUPLICATE` / schema fault as `OVERRUN`.




* **(3) Stage B dependency:** None.
* **(4) Claim strength vs. stated assumptions:** The header states *"The auditor runs this per manifest and per slot i = 0 … N − 1, once now ≥ T_d(N)"*. In Stage A, `now` is the unverified harness/auditor wall clock (`§5.6`), so boundary completeness for slot `N − 1` depends on the same clock assumption (`A-CLK` / UTC accuracy).



---

### 2. Disposition of R4.1 Findings B2-01 and B2-02

* **B2-01 (Uncommitted cycle at the slot boundary): CLOSED CONDITIONALLY.**
* *Why closed:* §11.2 now explicitly requires waiting until `now ≥ T_d(N)` (past the end of slot `N − 1`, since slot `N − 1` ends at `T_d(N)`) before running the audit, and row 2 of §11.2 explicitly classifies a slot with an invocation-log line and no committed `CYCLE` record (such as an uncommitted cycle killed or stalled at the boundary) as `INCOMPLETE` (non-qualifying) rather than `MISSING`.


* *Condition:* Remains conditional on fixing the `U77` overlap (**B3-04**) and defining the exact boundary rule for how a cycle still running at `T_d(i+1)` transitions to `CYCLE_OVERRUN` vs. leaving no chain record (`INCOMPLETE`).


* **B2-02 (OVERRUN versus MISSING precedence): CLOSED.**
* *Why closed:* §11.2 explicitly specifies *"Rows are applied in this order of precedence; the first matching row decides"*, placing `a CYCLE_OVERRUN record for slot i → OVERRUN` (row 1) strictly ahead of `no CYCLE record, and an invocation-log line → INCOMPLETE` (row 2) and `no CYCLE record, and no invocation-log line → MISSING` (row 3).





---

### 3. New Findings (B3-nn)

#### B3-01 — Missing Monotonicity / Sanity Guard on `(t_send, t_recv)` and Missing `Date` Header in §5.6

* **Section:** §5.6 (`V12b`)


* **Mechanism:** §5.6 computes `θ_low = D − t_recv` and `θ_high = D + 1 s − t_send` and checks `θ_low ≥ −2 s and θ_high ≤ +2 s`. If the harness wall clock steps backward during the HTTP request (`t_recv < t_send`), `θ_high − θ_low = 1 s − (t_send − t_recv)` shrinks below `1 s` (or becomes negative if `t_send − t_recv > 1 s`), allowing `V12b` to pass even though the wall clock jumped backward mid-measurement. Additionally, §5.6 does not state the handling when `D` is absent or unparseable.


* **Consequence:** A backward NTP step during the bars HTTP GET can produce a false `V12b` pass (or vacuous interval `θ_low > θ_high`), and missing `Date` handling relies on implicit error propagation.
* **Smallest correction:** Add to `V12b` in §5.6: *"fail closed (`BOUNDARY_FAIL`) if `D` is absent/unparseable or if `t_recv < t_send`."*


* **Severity:** **LOW**

#### B3-02 — `L` (Limit Price) and `price_increment` Undefined in §8.1.1

* **Section:** §8.1.1


* **Mechanism:** §8.1.1 defines `q` and `R` as functions of `L` and notes under Increment values that `price_increment` comes from the policy file, but `L` is absent from the symbol table and no formula defines `L` (e.g., whether `L` is `ask` rounded down to `price_increment` for BUY and `bid` rounded up to `price_increment` for EXIT, or unrounded).


* **Consequence:** Two independent implementations (the harness and the FD-6 blind reconstructor) cannot deterministically compute `q` or `R` from §8.1.1 alone if `ask` or `bid` is not already an exact multiple of `price_increment`.


* **Smallest correction:** Add `L` to the §8.1.1 symbol table: `L = floor to price_increment of ask (BUY) or ceil to price_increment of bid (EXIT), from the checkpoint (a) fresh quote`.


* **Severity:** **HIGH**

#### B3-03 — `shadow reserved BTC` Referenced in `q_exit` Formula Without Lifecycle Definition

* **Section:** §8.1.1


* **Mechanism:** §8.1.1 defines `q_exit = floor to qty_increment of (shadow BTC − shadow reserved BTC)`, noting *"Shadow BTC is always 0 on live data, so EXIT proposals arise only from fixtures (§3.3)"*. However, the reservation rule immediately below defines only a USD shadow reservation `R` for BUY proposals and never defines `shadow reserved BTC` (or whether an EXIT fixture proposal creates a BTC shadow reservation until `SHADOW_EXPIRED`).


* **Consequence:** Fixture-driven EXIT tests in Stage A have an undefined input variable (`shadow reserved BTC`), risking divergence between harness and reconstructor on EXIT fixtures.


* **Smallest correction:** Add `shadow_reserved_btc` to the §8.1.1 symbol table (`0` before step 3 of §7.1; set to `q_exit` if an EXIT proposal passes checkpoint (a) and released at `SHADOW_EXPIRED` in the same cycle).


* **Severity:** **LOW**

#### B3-04 — Redundancy / Contradiction Between §11.2 Row 2 (`INCOMPLETE`) and `U77` (Invocation Consistency)

* **Section:** §11.2


* **Mechanism:** Row 2 of §11.2 classifies a slot with *"no CYCLE record, and an invocation-log line for slot i"* as `INCOMPLETE`. Immediately below, `U77` states: *"each invocation-log line must correspond to a chain record for its slot (a CYCLE, CONCURRENT_INVOCATION, CYCLE_OVERRUN or OFF_RUN record)... any mismatch is a finding"*. Whenever a slot falls into Row 2 (an invocation line exists, and no `CYCLE`, `CYCLE_OVERRUN`, `CONCURRENT_INVOCATION`, or `OFF_RUN` chain record was written), it is simultaneously a standard `INCOMPLETE` slot classification and an `U77` protocol-violation finding.


* **Consequence:** Ambiguity in audit reporting: an expected crash/abort before chain commit (`INCOMPLETE`) triggers an `U77` finding, or conversely an `OFF_RUN` / `CONCURRENT_INVOCATION` chain record without a `CYCLE` record falls into Row 2 (`INCOMPLETE`) unless `U77` overrides it.


* **Smallest correction:** Clarify in §11.2 that `U77` checks 1-to-1 correspondence between invocation-log lines and chain records *outside* `INCOMPLETE` crashed slots (or distinguish `INCOMPLETE` as an invocation line with zero chain records, which is logged as an `U77` completeness finding).


* **Severity:** **LOW**

#### B3-05 — §11.2 Row 1 (`CYCLE_OVERRUN`) Unconditionally Precedes `DUPLICATE` and Integrity Checks

* **Section:** §11.2


* **Mechanism:** In §11.2, row 1 (`a CYCLE_OVERRUN record for slot i → OVERRUN`) is evaluated before row 4 (`more than one CYCLE record → DUPLICATE`) and row 6 (`fails the schema, the chain, artifact hashes or recomputation → NON-QUALIFYING (a finding)`). If a slot has a malformed `CYCLE_OVERRUN` record (failing schema or hash-chain verification) or both a `CYCLE` record and a `CYCLE_OVERRUN` record, row 1 still classifies the slot cleanly as `OVERRUN` rather than flagging a chain/schema or duplicate fault.


* **Consequence:** A corrupted `CYCLE_OVERRUN` record or a scheduler bug emitting both `CYCLE` and `CYCLE_OVERRUN` for the same slot is masked as a routine `OVERRUN` instead of an integrity/duplicate finding.


* **Smallest correction:** Insert a top-precedence integrity row in §11.2: *"any record for slot i failing schema or hash-chain verification → NON-QUALIFYING (integrity finding)"*, and restrict row 1 to *"a valid CYCLE_OVERRUN record and zero CYCLE records for slot i → OVERRUN"*.


* **Severity:** **MEDIUM**

---

### 4. Verdict

**CLOSED WITH CONDITIONS**

* **§5.6 Clock source:** Closed (add `t_recv ≥ t_send` and missing-`Date` guard per **B3-01**).
* **§8.1.1 Stage A sizing and shadow reservation:** Conditional on adding the explicit `L` definition/rounding rule (**B3-02**) and `shadow_reserved_btc` definition (**B3-03**) so the blind reconstructor has an unambiguous specification.
* **§11.2 Slot classification:** Conditional on tightening row 1 against malformed/duplicate `CYCLE_OVERRUN` records (**B3-05**) and harmonizing row 2 (`INCOMPLETE`) with `U77` (**B3-04**).