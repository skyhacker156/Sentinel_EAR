Prior exposure: I have seen SL-PT-001 R3 only. I have not seen the R3 reconciliation, R4, R4.1, GPT's review, or Claude's review findings.

---

## Stage A Hostile Review Findings (R4.1 Candidate)

### B2-01

* **Exact section and rule:** §5.3 (Slot-anchored clocks, item 4), §5.4 (Comparison table: `cycle within slot`), §5.6 (Clock source), §6.3 (Single writer, lock and hard slot boundary), and §6.4 step 6 (Cycle procedure).


* **Concrete failure mechanism:** A cycle that constructs a valid proposal and passes policy waits until `ceiling = T_d + 180 s` to record `SHADOW_EXPIRED` (§5.3 item 4, §6.4 step 6). Meanwhile, §6.3 requires an appender to hold the run lock token and find `now < T_d(its slot + 1)` (`T_d + 300 s`), or else the append is refused and the process exits. In addition, §5.6 only checks `|offset_estimate| <= 2 s` during V12 pre-flight against the HTTP `Date` header (which has 1 s truncation error, giving an error bound of `(-1 s, 0]` relative to the data host's clock, not UTC). If local clock drift, OS scheduling delay, or I/O latency pushes `now` at `SHADOW_EXPIRED` to or past `T_d(i+1)`, the append is refused and no `CYCLE` record is written.


* **Consequence:** A valid qualifying proposal at `SHADOW_EXPIRED` fails to commit its `CYCLE` record and is classified as `MISSING` under §11.2 rather than `QUALIFYING` (`SHADOW_EXPIRED`), corrupting the consecutive run counter (`run_length` in §11.4).


* **Severity:** HIGH
* **Smallest sufficient correction:** Specify exact handling if `now >= T_d(i+1)` is reached before or at `SHADOW_EXPIRED` (e.g., whether `SHADOW_EXPIRED` must be evaluated/recorded strictly prior to `T_d(i+1)` or how a post-boundary expiration is recorded and audited without conflating a late commit refusal with a missing invocation).


* **Blocks Stage A freeze:** Yes.

### B2-02

* **Exact section and rule:** §6.3 (Single writer, lock and hard slot boundary — run lock token table) and §11.2 (Slot classification table).


* **Concrete failure mechanism:** When slot `j` (`j > i`) acquires the append lock while slot `i` holds the run lock token without a terminal `CYCLE` record, slot `j` appends `CYCLE_OVERRUN` for slot `i`, requests termination of process `i`, and takes the run lock token (§6.3). Any later append attempt by old process `i` is refused because it no longer holds the token (§6.3). In §11.2, the slot classification table lists `"no CYCLE record with this manifest, slot and cycle_id(i)" -> MISSING` as the first row, and `"a CYCLE_OVERRUN for slot i" -> NON-QUALIFYING` as the fifth row. When an overrun old process is prevented from appending a `CYCLE` record, both conditions (`no CYCLE record` and `a CYCLE_OVERRUN for slot i`) can hold simultaneously.


* **Consequence:** Ambiguous classification between `MISSING` and `NON-QUALIFYING` for an overrun slot `i` when the prior process never committed a `CYCLE` record.


* **Severity:** MEDIUM
* **Smallest sufficient correction:** Define explicit precedence in §11.2 so `CYCLE_OVERRUN` takes precedence over `MISSING` for slot `i` (while still flagging any orphan/uncommitted work as a finding if expected).


* **Blocks Stage A freeze:** Yes.

### B2-03

* **Exact section and rule:** §4.9 (Revision handling — Bar store, per-cycle table, and "What CONFIRMED means — and does not mean").


* **Concrete failure mechanism:** Under "What CONFIRMED means — and does not mean," §4.9 states that `CONFIRMED` "means only that the source returned the same bytes on two fetches." However, the per-cycle table immediately above it states that when `t` is not in the store, the system adds it as `CONFIRMED (a first observation)`. Thus a bar is marked `CONFIRMED` on its *first* observation (single fetch), not after two fetches of the same bytes. Additionally, if a bar changes on every cycle (`A -> B -> C -> D`), each new tuple triggers a new `SOURCE_REVISION` and sets `PENDING` with the newest tuple, meaning a continuously mutating bar can block consecutive slots across multiple cycles rather than only a single slot.


* **Consequence:** Internal contradiction in the specification's definition of `CONFIRMED` and potential overstatement of single-slot lock-out boundedness when upstream bar values mutate repeatedly.


* **Severity:** MEDIUM
* **Smallest sufficient correction:** Reconcile the `CONFIRMED` definition in §4.9 with the first-observation table row (e.g., distinguish initial `OBSERVED`/`CONFIRMED` baseline entry from post-revision re-confirmation) and clarify that the single-slot bound holds only when subsequent fetches repeat the revised bytes without further mutation.


* **Blocks Stage A freeze:** No (can be clarified cleanly prior to or at freeze without altering core logic).

### B2-04

* **Exact section and rule:** §3.3 (Signal-to-action mapping — Stage A consequence), §8.1 (Stage A shadow ledger), and §11.1 (Terminal states — qualifying conditions for `NO_ACTION`).


* **Concrete failure mechanism:** In Stage A, the shadow ledger never acquires BTC (§8.1), so position is always flat (§3.3). Under §3.3, any `EXIT` signal while flat maps to `NO_ACTION` (via CF-2), and §11.1 treats `NO_ACTION` as a **qualifying** terminal state for `M1-1` (`run_length >= 30`). Consequently, `EXIT` signals generated on live 5-minute data in Stage A map to `NO_ACTION` and count toward the 30-slot qualifying streak even though no real position exists to exit and no trade occurs.


* **Consequence:** Live Stage A `EXIT` signals inflate the `NO_ACTION` qualifying streak under a zero-BTC shadow ledger, potentially masking whether `HOLD` or `BUY` (rejected/expired) behavior was actually exercised across the 30 consecutive slots.


* **Severity:** MEDIUM
* **Smallest sufficient correction:** State explicitly in §11.1 / §11.4 / §13 that `NO_ACTION` from `EXIT`-while-flat on a zero-BTC Stage A shadow ledger is a qualifying `NO_ACTION` under the current rules, and report `NO_ACTION` counts by underlying signal (`BUY` vs. `EXIT`) in audit summaries so reviewers can see how many qualifying slots came from `EXIT`-while-flat.


* **Blocks Stage A freeze:** No.

### B2-05

* **Exact section and rule:** §10.1 (Global chain), §10.3 (Run manifest), §11.3 (Completeness of the run set), and §11.5 (Auditor and reconstruction).


* **Concrete failure mechanism:** §10.1 directs the founder to push `chain/events.jsonl` "at least at every RUN_OPEN and RUN_CLOSE," and §11.3 explicitly notes that completeness is relative to `GENESIS` and to what the founder pushed ("A chain that was never pushed cannot be audited.") Meanwhile, §11.5 has the founder run GPT's combined reconstruction and slot-audit script locally. If a run or push is omitted or delayed, the audit only covers pushed chain history up to what is present in the audited environment, and a single script performing both reconstruction and slot audit shares common-mode assumptions with the audit check itself (§11.5, U-O4).


* **Consequence:** Potential blind spots in cross-run chain completeness if pushes are missed or delayed, and common-mode audit/reconstruction risk (`U-O4`).


* **Severity:** MEDIUM
* **Smallest sufficient correction:** Require the audit exit report in §11.3 to explicitly record the exact git commit/push SHA and chain head hash audited, and keep `U-O4` flagged as an unbounded common-mode limitation on any Stage A audit report.


* **Blocks Stage A freeze:** No.

### B2-06

* **Exact section and rule:** §2.2 (Stage A properties), §2.3 (Network isolation boundary — Branch C), §10.4 (TER schema v1), and §13 (Claims).


* **Concrete failure mechanism:** §2.3 establishes Branch C (client-level HTTP allowlist and absence of credentials only; no OS/host firewall isolation) and requires a verbatim limitation statement. However, §10.4 names the TER field `isolation-branch marker, always "C" (§2.3)`. Naming a client-level HTTP allowlist an "isolation-branch marker" in the schema risks inviting "isolation" shorthand in tooling or summaries even though §2.3 and §13 state Stage A does not establish process- or host-level isolation.


* **Consequence:** Subtle terminology drift ("isolation" label) in telemetry/TER fields that could be misread as stronger isolation than HTTP-client allowlisting + credential absence provides.


* **Severity:** LOW
* **Smallest sufficient correction:** Ensure audit/report templates generated from TERs always attach the §2.3 verbatim Branch C limitation alongside any `"C"` marker output.


* **Blocks Stage A freeze:** No.

### B2-07

* **Exact section and rule:** §11.6 (Test coverage — pre-live gate) and §14.1, §14.4, §14.6, §14.7 (Stage A test inventory).


* **Concrete failure mechanism:** §11.6 requires executing at least one pass and fail case for applicable Stage A rules and every §14 test marked `A` or `A, B` before the first live-data cycle. Several Stage A tests (`U14` for `EXIT` while flat / `BUY` while long, `X5` for equity `$449` / `R8`, `X6` for sell exceeding holdings) depend on fixture ledgers because the live Stage A shadow ledger is static (`$500` cash, `0` BTC, no fills). Additionally, test `U7` groups two distinct outcomes (`proceed with a note / DATA_CONFLICT`) for identical vs. differing duplicate `t` into a single row.


* **Consequence:** Without explicit separation between live-pipeline tests and synthetic-fixture tests (and splitting `U7`'s pass/note vs. fail/conflict cases), test execution reports could blur fixture coverage with live-data coverage.


* **Severity:** LOW
* **Smallest sufficient correction:** Annotate fixture-only Stage A tests in §14 as fixture-backed and split `U7` into `U7a` (identical duplicate `t` -> note) and `U7b` (differing duplicate `t` -> `DATA_CONFLICT`).


* **Blocks Stage A freeze:** No.

---

## Required Summary Sections

### Overall Verdict

**CONDITIONALLY FREEZE-READY** — The Stage A specification is structurally coherent, explicit about non-execution and Branch C limits, and separates Stage A from Stage B drafts. However, **B2-01** (ceiling / `SHADOW_EXPIRED` vs. `T_d(i+1)` append refusal and clock drift) and **B2-02** (`CYCLE_OVERRUN` vs. `MISSING` precedence in §11.2) should be resolved before locking the Stage A freeze.

### Stage A Test Gaps

* **Live vs. fixture reachability:** Long-side and balance-mutation rules (`R8`, `R9`, `R12`, `CF-2` long/flat cases) are only reachable via fixtures/injections in Stage A because §8.1 holds shadow cash at `$500.00` and BTC at `0` with no simulated fills.


* **Compound test row (`U7`):** Combines identical duplicate `t` (with note) and differing duplicate `t` (`DATA_CONFLICT`) in one test entry.


* **Post-pre-flight clock drift / boundary straddle at `SHADOW_EXPIRED`:** Tests cover `U79` (`offset_estimate` around `±2 s`) and `U47` (`created = T_d + 250 s`), but explicit testing of a qualifying proposal whose `T_d + 180 s` ceiling nears or crosses a slow/skewed slot boundary is worth making explicit.



### Residual UNVERIFIED and UNBOUNDED Items

* **UNVERIFIED (Stage A):** `U-D4` (5Min bar revision behavior/finality), `U-D5` (3–4 decimal price derivation), `U-D6` (gap frequency and load behavior), `U-D7` (bar start vs. end labelling in practice), `U-D8` (`end` parameter semantics), `U-T1` (Task Scheduler configuration/behavior prior to XML check), and `U-T2` (data host `Date` header accuracy vs. UTC).


* **UNBOUNDED (Stage A):** `U-O2` (number of slots needed to achieve `run_length >= 30`) and `U-O4` (shared misreading of R4.1 between harness and the FD-6 reconstruction/audit script).



### Areas Where the Specification is Sound

* **Strict non-trading and Branch C disclosure:** Stage A excludes credentials and order submission paths, and §2.3 / §13 candidly state that Branch C is client-level only and establishes neither process/host isolation nor G-07 properties.


* **Exact rational arithmetic and canonical JSON string encoding:** Requiring exact rationals (or decimal with Inexact trap enabled) and string-encoded numbers in `TER-1` (§5.1, §10.4, §10.5) avoids IEEE-754 float drift and RFC 8785 number coercion.


* **Explicit `MISSING` vs. no-`SKIPPED` rule and append-only artifact hashing:** Requiring raw artifacts to be hashed before parsing and treating uninvoked/missing slots as `MISSING` rather than inventing `SKIPPED` creates a clear audit baseline (§4.3, §6.3, §10.2, §11.2).



### Single Most Important Stage A Blocker

**B2-01:** Ensuring a proposal that passes policy and waits for `SHADOW_EXPIRED` at `T_d + 180 s` cannot be silently turned into a `MISSING` slot if local clock skew or execution delay pushes the commit to or past `T_d(i+1)` where §6.3 refuses the chain append.

### Issues Investigated and Rejected

* **Whether Stage A simulates fills to test `R8` / `R12` / `EXIT`:** Rejected as a defect — §8.1 explicitly prohibits simulating fills so venue behavior is not invented, and the dispatch restricts Stage A to shadow proposals without orders.


* **Whether Stage A lacks broker order-execution or fill-reconciliation rules (§8.2–§8.6, §9, §12):** Rejected as out of scope for the Stage A freeze per §0.2 and the dispatch boundary (Stage B draft items do not block FD-5 unless they alter a Stage A section).