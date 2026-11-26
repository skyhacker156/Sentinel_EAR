### Exposure Statement

I previously reviewed SL-PT-001 R4.1 and performed a closure check on the R4.2 excerpts. I have not seen any other reviewer's review.

---

### Closure Classification of R4.2 Findings (B3-01 to B3-05)

* **B3-01 (Clock offset bound / latency ceiling ambiguity in §5.6): CLOSED.**
Section 5.6 now explicitly states all four conditions for check V12b: (1) `D` is present and parses, (2) $t_{\text{recv}} \ge t_{\text{send}}$, (3) $t_{\text{recv}} - t_{\text{send}} < 3\text{ s}$, and (4) $\theta_{\text{low}} \ge -2\text{ s}$ and $\theta_{\text{high}} \le +2\text{ s}$. It explicitly derives that condition 3 excludes an exact 3 s round trip that condition 4 alone would admit.


* **B3-02 (Undefined symbol $L$ in §8.1.1): CLOSED.**
Section 8.1.1 explicitly defines $L$ by cross-referencing §7.2 ("the checkpoint-(a) ask rounded down to `price_increment` (BUY), or the bid rounded up (EXIT)").


* **B3-03 (Missing `shadow_reserved_btc` release / definition in §8.1.1): CLOSED.**
Section 8.1.1 now defines `shadow_reserved_btc` as 0 before step 3 of §7.1, set to `q_exit` when an EXIT proposal passes every rule at checkpoint (a), and released at `SHADOW_EXPIRED` in the same cycle, and defines `q_exit` as `floor` to `qty_increment` of `(shadow BTC − shadow_reserved_btc)`.


* **B3-04 (TER schema vs. `null` / `NOT_EVALUATED` ambiguity for unevaluated paths): CLOSED.**
The "Unevaluated checks and absent artifacts" block and accompanying table explicitly mandate that every field is always present, `null` is the only non-string value permitted in a TER, and every `NOT_EVALUATED` check carries one of four enumerated reason codes (`V12A_FAILED`, `V12B_FAILED`, `DATA_INVALID`, `NO_PROPOSAL`).


* **B3-05 (Slot classification precedence gaps in §11.2): CLOSED.**
Section 11.2 provides a strict 9-row precedence table applied top-to-bottom where the first matching row decides, explicitly resolving schema/hash failures (Row 1), `CYCLE_OVERRUN` + `CYCLE` conflicts (Row 2), `INCOMPLETE` vs. `MISSING` via invocation-log presence (Rows 4–5), `DUPLICATE` (Row 6), and `CONCURRENT_INVOCATION` anomalies (Row 7).



---

### Verification of R4.2a Changed Text

#### 1. Internal consistency of V12b (§5.6) with U79, U98, U106, and U107

The V12b rule and the four unit tests are **internally consistent**:

* **U79:** With $t_{\text{recv}} - t_{\text{send}} = 1\text{ s}$ ($< 3\text{ s}$, satisfying condition 3), $\theta_{\text{high}} = +2\text{ s}$ and $\theta_{\text{low}} = -2\text{ s}$ satisfy condition 4 ($\theta_{\text{low}} \ge -2\text{ s}$ and $\theta_{\text{high}} \le +2\text{ s}$) $\rightarrow$ `pass`. Shifting by $+1\text{ ns}$ on $\theta_{\text{high}}$ or $-1\text{ ns}$ on $\theta_{\text{low}}$ violates condition 4 $\rightarrow$ `BOUNDARY_FAIL`.


* **U98:** For an interval centered on $0$, $\theta_{\text{low}} = -\theta_{\text{high}}$. Since width $= \theta_{\text{high}} - \theta_{\text{low}} = 1\text{ s} + (t_{\text{recv}} - t_{\text{send}})$, $\theta_{\text{high}} = 0.5\text{ s} + 0.5(t_{\text{recv}} - t_{\text{send}})$.
* At round trip $3\text{ s} - 1\text{ ns}$: condition 3 holds ($< 3\text{ s}$), and $\theta_{\text{high}} = 2\text{ s} - 0.5\text{ ns} \le 2\text{ s}$, $\theta_{\text{low}} = -2\text{ s} + 0.5\text{ ns} \ge -2\text{ s}$ $\rightarrow$ `pass`.


* At round trip $= 3\text{ s}$: condition 4 holds ($\theta_{\text{low}} = -2\text{ s}, \theta_{\text{high}} = +2\text{ s}$), but condition 3 ($t_{\text{recv}} - t_{\text{send}} < 3\text{ s}$) fails $\rightarrow$ `BOUNDARY_FAIL (condition 3)`.


* At round trip $= 3\text{ s} + 1\text{ ns}$: fails both condition 3 and condition 4 $\rightarrow$ `BOUNDARY_FAIL`.




* **U106 & U107:** $t_{\text{recv}} < t_{\text{send}}$ fails condition 2; absent or unparseable `Date` fails condition 1.



#### 2. Exact recomputation of sizing vectors in U105

Parameters: $\text{qty\_increment} = 0.0001$, $f_{\text{res}} = 0.0025$ ($1 + f_{\text{res}} = 1.0025$), $\text{price\_increment} = 1$.

* **(a) $L = 59850$, $\text{budget} = 150.00$:**
* $\text{budget} / (L \times 1.0025) = 150 / (59850 \times 1.0025) = 150 / 59999.625 \approx 0.002500015625$
* $q = \lfloor 0.002500015625 \rfloor_{0.0001} = 0.0025$
* Exact cost $= 0.0025 \times 59850 \times 1.0025 = 149.9990625$
* $R = \lceil 149.9990625 \rceil_{0.01} = 150.00$. Matches U105(a) exactly.




* **(b) $L = 59850$, $\text{budget} = 149.99$:**
* $\text{budget} / (L \times 1.0025) = 149.99 / 59999.625 \approx 0.002499848957$
* $q = \lfloor 0.002499848957 \rfloor_{0.0001} = 0.0024$
* Exact cost $= 0.0024 \times 59850 \times 1.0025 = 143.9991$
* $R = \lceil 143.9991 \rceil_{0.01} = 144.00$. Matches U105(b) exactly.




* **(c) $\text{ask} = 60663.76 \rightarrow L = \lfloor 60663.76 \rfloor_1 = 60663$, $\text{budget} = 150.00$:**
* $\text{budget} / (L \times 1.0025) = 150 / (60663 \times 1.0025) = 150 / 60814.6575 \approx 0.002466510644$
* $q = \lfloor 0.002466510644 \rfloor_{0.0001} = 0.0024$
* Exact cost $= 0.0024 \times 60663 \times 1.0025 = 145.955178$
* $R = \lceil 145.955178 \rceil_{0.01} = 145.96$. Matches U105(c) exactly.




* **(d) $L = 100000$, $\text{budget} = 150.00$:**
* $\text{budget} / (L \times 1.0025) = 150 / (100000 \times 1.0025) = 150 / 100250 = 0.0014962593516...$
* $q = \lfloor 0.0014962593516... \rfloor_{0.0001} = 0.0014$
* Exact cost $= 0.0014 \times 100000 \times 1.0025 = 140.35$
* $R = \lceil 140.35 \rceil_{0.01} = 140.35$. Matches U105(d) exactly.





#### 3. TER table for unevaluated checks and closed-schema consistency

The table covers all five terminal paths (`V12a fails`, `V12b fails`, `a V1 to V11 failure`, `HOLD or NO_ACTION`, and `a proposal (REJECTED, SHADOW_EXPIRED) or QUOTE_INVALID`). Every field is required to be present, non-existent artifacts/clock fields/computed values are strictly JSON `null`, and unevaluated checks take `NOT_EVALUATED` with one of four exhaustive reason codes (`V12A_FAILED`, `V12B_FAILED`, `DATA_INVALID`, `NO_PROPOSAL`). However, two minor clarity defects exist in the table (see **B4-01** and **B4-02** below).

#### 4. Completeness and unambiguity of the 9-row precedence table in §11.2

Every slot $i$ has $c \in \{0, 1, \ge 2\}$ `CYCLE` records, $o \in \{0, \ge 1\}$ `CYCLE_OVERRUN` records, $k \in \{0, \ge 1\}$ `CONCURRENT_INVOCATION` records, and $l \in \{0, \ge 1\}$ invocation-log lines.

* **Row 1** traps any schema or hash-chain failure across `CYCLE`, `CYCLE_OVERRUN`, or `CONCURRENT_INVOCATION`.


* For remaining valid records:
* If $o \ge 1$: $c \ge 1 \rightarrow$ **Row 2** (`CONFLICT`); $c = 0 \rightarrow$ **Row 3** (`OVERRUN`).


* If $o = 0$ and $c = 0$: $l \ge 1 \rightarrow$ **Row 4** (`INCOMPLETE`); $l = 0 \rightarrow$ **Row 5** (`MISSING`).


* If $o = 0$ and $c \ge 2$: **Row 6** (`DUPLICATE`).


* If $o = 0$ and $c = 1$: $k \ge 1 \rightarrow$ **Row 7** (`NON-QUALIFYING` scheduler fault); artifact/recomputation failure $\rightarrow$ **Row 8** (`NON-QUALIFYING` finding); otherwise $\rightarrow$ **Row 9** (`QUALIFYING`).
The partition is mathematically exhaustive and mutually exclusive. However, there is a terminology mismatch between Row 1 and the "Invocation consistency (U77)" sub-section regarding `OFF_RUN` records (see **B4-03** below).





---

### New Findings

* **B4-01**
* **Section:** §8.1.1 / §10.4 ("Unevaluated checks and absent artifacts" table, Row 3: `a V1 to V11 failure`)


* **Mechanism:** Row 3 states that when a V1 to V11 check fails, "both artifacts" are present and "V results as evaluated". Unlike Rows 1, 2, and 4—which explicitly specify the state of every check group—Row 3 does not explicitly state whether remaining V1–V11 checks after a short-circuit failure (if short-circuiting occurs) are `NOT_EVALUATED (DATA_INVALID)` or if all V1–V11 checks are always evaluated to `PASS`/`FAIL`.


* **Consequence:** Implementers could diverge on whether V1–V11 short-circuit (leaving subsequent V checks `NOT_EVALUATED (DATA_INVALID)`) or evaluate all 11 checks unconditionally.
* **Smallest correction:** In Row 3, specify either `"all V1 to V11 evaluated (PASS/FAIL)"` or `"V1 to V11 evaluated up to failure (remaining V checks NOT_EVALUATED with DATA_INVALID)"` to match §7.
* **Severity:** Minor
* **Blocks Stage A freeze:** No


* **B4-02**
* **Section:** §8.1.1 / §10.4 ("Unevaluated checks and absent artifacts" table, Row 5: `a proposal (REJECTED, SHADOW_EXPIRED) or QUOTE_INVALID`)


* **Mechanism:** Row 5 states `"everything evaluated"` and `"proposal null if QUOTE_INVALID"`. Because a proposal object is not formed when `QUOTE_INVALID` occurs (and thus Q1–Q5 sizing/proposal checks have no proposal to evaluate against), `"everything evaluated"` is slightly ambiguous as to whether Q1–Q5 are `PASS`/`FAIL` or `NOT_EVALUATED` under `QUOTE_INVALID`.


* **Consequence:** Potential ambiguity in U108 test vector construction for the `QUOTE_INVALID` terminal path.
* **Smallest correction:** Split Row 5 into two rows or clarify: `"Q1 to Q5 NOT_EVALUATED (DATA_INVALID) and proposal null if QUOTE_INVALID"` (or state which Q checks run before quote validation).
* **Severity:** Minor
* **Blocks Stage A freeze:** No


* **B4-03**
* **Section:** §11.2 ("Slot classification", Row 1 vs. "Invocation consistency (U77)")


* **Mechanism:** "Invocation consistency (U77)" lists four valid chain record types that can correspond to an invocation-log line: `(a CYCLE, CONCURRENT_INVOCATION, CYCLE_OVERRUN or OFF_RUN record)`. However, Row 1 of the slot classification table enumerates `(CYCLE, CYCLE_OVERRUN or CONCURRENT_INVOCATION)` and omits `OFF_RUN`.


* **Consequence:** If an `OFF_RUN` record is associated with a slot and fails schema or hash-chain validation, Row 1 does not explicitly capture it, potentially falling through to Row 4 (`INCOMPLETE`) or Row 5 (`MISSING`) instead of triggering a Row 1 integrity finding.
* **Smallest correction:** Add `OFF_RUN` to Row 1's parenthetical list: `(CYCLE, CYCLE_OVERRUN, CONCURRENT_INVOCATION or OFF_RUN)` (or clarify that `OFF_RUN` records never carry a slot index $i \in \{0 \dots N-1\}$).
* **Severity:** Minor
* **Blocks Stage A freeze:** No



---

### Verdict

**CLOSED WITH CONDITIONS** — All five R4.2 findings (B3-01 through B3-05) are closed, and the arithmetic and boundary logic in §5.6, §8.1.1, §11.2, U79, U98, U105–U107, and U109–U110 are exact. Stage A freeze can proceed once the three minor table clarifications (B4-01, B4-02, B4-03) are applied so U108 and U77 have zero schema-level ambiguity.