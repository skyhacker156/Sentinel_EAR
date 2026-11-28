# SL-PT-001 R5-B3: bounded delta against R5-B2

**From:** Claude | **To:** Founder; GPT | **Responds to:** Strike 7.4 (G-B2-01 to G-B2-07; v6 amendment dispositions)
**Base:** `SL-PT-001_R5-B2_Stage_B_Consolidated_Delta_Claude_2026-11-26.md` (§ numbers below are R5-B2's). Unaffected R5-B2 sections stand and are not reproduced.
**Status:** DRAFT. No freeze, nothing authorized, built, keyed or sent.
**Evidence boundary:** no Stage A run evidence and no harness internals.
**Convergence:**
- This delta closes the seven named defects and adds only the tests that verify them.
- Venue facts remain **venue gates** (§6); execution questions remain **acceptance tests**.
- No new architecture is introduced. One new mechanism, the executor lease (§E), is the smallest correction for G-B2-05.

---

## 1. Finding-closure matrix

| Finding | Concrete defect in R5-B2 | Smallest correction | R5-B3 § | Tests |
|---|---|---|---|---|
| **G-B2-01** rounding and exact arithmetic | (a) §2.9.1 holds Sentinel USD "on the cent grid", while §2.9.3 computes cash − G − fee exactly (not on the grid): a contradiction. (b) §2.9.5 picks one rule that matches and "pins" it after one observation: a unique rule is inferred from insufficient evidence. (c) G = Q_f × P̄ uses the broker's **rounded** average price, so G is not the true gross. (d) "P̄ ≤ L by IOC semantics" ignores rounding of P̄ | Sentinel cash is **exact**. Gross is computed on predeclared bases; L-2 evaluates a predeclared set of rounding comparisons and records **every** consistent one with exact residuals; nothing is pinned. An explicit ROUNDING_RESIDUAL ledger event brings the ledger to the broker figure only inside a predeclared bound | §A | UB-L4′, UB-L5′, UB-L7 |
| **G-B2-02** close vs transmission race | CLOSING is checked at (d), but a SESSION_CLOSING appended after PRESEND and before the first byte is ignored or races | **Linearize by chain order.** "Commencement of transmission" := the PRESEND record append. A CLOSING earlier in the chain than a PRESEND blocks it; one later than a PRESEND is post-release (like G-07 §1 revocation) and the send proceeds, tracked. The executor never re-reads session state between PRESEND and the send | §B | UB-X5 |
| **G-B2-03** send timing arithmetic | (a) "first byte" is not observable in the client; (b) the response timeout of 10 s after the first byte plus up to δ_send of start delay lets a send end **after** expires_at, contradicting G-07 §1's "expiry cannot occur in that window"; (c) clock-adjustment detection was pairwise only, so slow drift in steps below ε_step is missed | A defined transmission boundary t_tx0; **one total budget**: the response by t_d + δ_send; start by t_d + δ_start; **cumulative** \|ΔW − ΔM\| from CONSUME to send end; fail-closed outcomes per instant | §C | UB-T1′, UB-T2′, UB-T5 |
| **G-B2-04** definitive rejection vs ambiguous; L-1 on recovered orders | (a) "4xx with a body" treats 408, 409 and 429 as definitive; (b) one not-found query right after a rejection does not exclude delayed creation; (c) L-1 runs only on the SEND response, so an order found later by query (after an ambiguous send) is never L-1-checked | A closed definitive set {400, 401, 403, 422} **and** two not-found queries ≥ 10 s apart; everything else is AMBIGUOUS. **L-1 applies to the first order object observed for the COID, from any source** | §D | UB-S5′, UB-S8 |
| **G-B2-05** exclusive executor; crash recovery | R5-B2 allowed two executor instances ("exactly one CONSUME", UB-S7). Two instances can both run recovery, query and book, or one can recover while the other sends | **An executor lease:** an OS-exclusive lock on `chain-b/executor.lock`, held for the process's lifetime (released by the OS on death), and an EXECUTOR_START record. A second instance refuses at start. Recovery, eligibility and every executor write require the lease. Recovery is idempotent | §E | UB-E1, UB-E2 (replace UB-S7) |
| **G-B2-06** reconciliation identity | §2.8 accepted a field-only match (side, qty, price, time) as a match; an ambiguous match was treated as conclusive | **Conclusive identity = COID or broker order id.** A field-only correspondence is UNRESOLVED, never PASS. Dashboard order count in the session window must equal the chain's count. A WAL with no dashboard order is not proof of non-submission | §F | UB-L3S′ |
| **G-B2-07** internal contradictions | (1) SESSION_OPEN needs an open-orders read, but `GET /v2/orders` is absent from the executor allowlist (§2.1). (2) §2.1 says the founder CLI writes only RECONCILE_L3 and RUN_STOPPED_B, while the schema has it writing SESSION_CLOSING and DISCREPANCY; the decision process raises halts but is not a DISCREPANCY writer. (3) §2.1 "AUTH_DEATH (consumed, not sent)" conflicts with §2.4, where post-CONSUME death is NOT_SENT. (4) NOT_ACCEPTED is missing from the executor's write list. (5) The pre-flight claims "five paths" but P4 has two path variants (six requests). (6) UB-T3 runs only at the first real order, yet sits in the gate **for** that order. (7) TER-2 RECONCILE_L2 records one `rounding_rule_matched` (see G-B2-01). (8) GENESIS_B omits seed-reveal custody and audit-result consistency (D-8 amendment). (9) There is no distinction between the per-attempt approval and the permission for later attempts after a zero fill | Each corrected in §G; attempt permission in §H | UB-C5, UB-A1′, UB-K1, UB-K2; UB-T3 moved |

---

## 2. Corrections

### §A. Exact arithmetic and broker rounding (replaces R5-B2 §2.9.1, §2.9.3 gross, §2.9.4 check, §2.9.5)

1. **Exact values.** Sentinel holds cash, reserved_usd, held_btc, G and fees as **exact decimals**. There is no cent-grid requirement on held values. R is on the cent grid by its definition (§8.1.1, ceiling to the cent).
2. **Predeclared gross bases** (recorded with every booking):
   - **G_fills** = Σ (q_i × p_i) over the order's individual fill records, if the venue returns them (account activities of fill type, with per-fill qty and price) **[VENUE]**;
   - **G_avg** = Q_f × P̄ from the terminal order object.

   Both are computed when available. If both exist and differ, the difference is recorded. **G_fills is authoritative when present** (it does not depend on a rounded average); otherwise G_avg is used, flagged `basis = AVG_PRICE`.
3. **Predeclared comparison set for L-2 cash:**
   - For each available basis, compute Sentinel's exact post-trade cash C_exact.
   - Compare with the broker cash C_broker under each of {exact, floor-to-cent, ceiling-to-cent, half-even-to-cent}.
   - **Record every rule under which they are equal, and the exact residual r = C_broker − C_exact for every basis.**
   - **PASS** iff at least one predeclared (basis, rule) pair is consistent **and** |r| < $0.01 for the authoritative basis.
   - Otherwise DISCREPANCY (L2_CASH).
   - **No rule is pinned or inferred as the broker's rule.** Each terminal order is evaluated against the full predeclared set.
4. **ROUNDING_RESIDUAL ledger event.**
   - When L-2 passes with r ≠ 0, the executor appends ROUNDING_RESIDUAL {r, basis, consistent_rules, ref}. The ledger fold applies r to cash, so the ledger now equals the broker figure.
   - This is an explicit event with evidence, not an automatic correction.
   - It is permitted only inside the PASS condition above.
5. **BTC.** The broker position must equal Sentinel's exact held_btc. No rounding comparison is allowed for BTC. Any difference → DISCREPANCY (L2_BTC).
6. **Reservation bound** (replaces "P̄ ≤ L by IOC semantics").
   - Check G_auth + fee_usd_equiv ≤ R, using the authoritative basis.
   - Separately record whether P̄ ≤ L and whether every p_i ≤ L.
   - **Any p_i > L, or the bound failing → DISCREPANCY (LIMIT_OR_RESERVATION).** A P̄ > L caused only by rounding of P̄ while every p_i ≤ L is recorded, not a discrepancy. If no fill records exist, P̄ > L is a discrepancy.

### §B. Session closure versus transmission (amends R5-B2 §2.3)

1. **Commencement of transmission** := the append of the PRESEND record (under the append lock).
2. SESSION_CLOSING and PRESEND are both appended under the append lock. **Chain order decides:**
   - **CLOSING precedes PRESEND:** the executor's (d) read, taken under the lock in the same hold that appends PRESEND, sees CLOSING, so it appends NOT_SENT (SESSION_CLOSING) instead of PRESEND.
   - **PRESEND precedes CLOSING:** the send is released. It proceeds within §C's bounds and is tracked and reconciled. CLOSING applies to every later authorization.
3. After PRESEND, the executor performs **no** further session-state read before the send. This removes the race by construction (DERIVED from the lock: one read-check-append hold).
4. SESSION_CLOSE preconditions are unchanged (R5-B2 §2.3). A released send must be terminal and reconciled first.

### §C. Send timing (replaces R5-B2 §2.6 rows "PRESEND margin", "send start", "send response", "clock adjustment")

**Instants:**
- **t_d** (W and M): the checkpoint-(d) sample, taken under the lock immediately before the PRESEND check.
- **t_tx0** (M): sampled immediately before the HTTP client opens the connection for the POST. This is the **transmission boundary**: Sentinel claims nothing about bytes before it and treats everything after it as possibly transmitted.
- **t_resp** (M): the complete response received.

| Bound | Rule | On violation |
|---|---|---|
| release margin | W(t_d) ≤ expires_at − δ_send | NOT_SENT (LATE) instead of PRESEND |
| start | M(t_tx0) − M(t_d) ≤ δ_start = 2 s | not begun → NOT_SENT (SEND_NOT_BEGUN; locally certain, because nothing was opened) |
| total budget | M(t_resp) − M(t_d) ≤ δ_send = 10 s. **The client timeout for connect + send + response is set to δ_send − (M(t_tx0) − M(t_d))** | exceeded or no response → AMBIGUOUS (SEND_OVERRAN or TIMEOUT); never retried |
| expiry consistency (DERIVED) | from the first two rows and the absence of clock adjustment: W(t_resp) ≤ W(t_d) + δ_send ≤ expires_at | — |
| cumulative clock adjustment | at every executor checkpoint (c), (d), t_tx0 and t_resp: \|(W_now − W_c) − (M_now − M_c)\| ≤ ε_step = 250 ms, measured **cumulatively from the CONSUME sample** (c), not between consecutive samples. The decision process applies the same rule cumulatively from (a) to (b) | before PRESEND → AUTH_DEATH or NOT_SENT (CLOCK_ADJUSTED); after PRESEND → AMBIGUOUS (CLOCK_ADJUSTED_AFTER_RELEASE). The session moves to CLOSING either way |

**Status of the values (D-12, amended):**
- δ_send = 10 s, δ_start = 2 s and ε_step = 250 ms are **provisional engineering constraints**. They are fail-closed bounds, not predictions.
- A POST slower than δ_send produces AMBIGUOUS, which is safe but blocks the session. **Pre-flight GET latency is recorded as context only. It does not establish a POST bound and is not a gate** (this replaces R5-B2 §2.6's "p_max < δ_send / 2" condition).
- The real POST duration is an observation of the first send (§G item 6).

### §D. Definitive rejection, ambiguity, and L-1 on recovered orders (replaces R5-B2 §2.7 item 5; amends §2.8 L-1)

| Response to the POST | Then | Classification |
|---|---|---|
| 2xx with a parseable order object | L-1 on that object → tracking | — |
| status ∈ **{400, 401, 403, 422}** with a parseable error body | query by COID at t_resp + 2 s and again ≥ 10 s later | **both** not found → NOT_ACCEPTED (terminal; full release). Any found → tracking + L-1 + DISCREPANCY (CONTRADICTORY_RESPONSE) |
| any other status (including 404, 408, 409, 429, 5xx); a timeout; a transport error; a malformed or unparseable body | query by COID (2 s, then every 30 s) | found → tracking + L-1. Not found → **stays AMBIGUOUS**. It is never reclassified automatically; it is resolved only by a founder record citing queries and L-3 (§F) |

**L-1 (amended):** L-1 is evaluated on **the first order object observed for the COID**, whether it comes from the SEND response or a QUERY. It compares symbol, side, qty, type, limit_price, TIF and COID with the AUTHORIZATION. A mismatch → governance failure, halt. Later observations are tracking only; a later change in a bound field is also a DISCREPANCY (BOUND_FIELD_CHANGED).

### §E. Executor lease and crash recovery (amends R5-B2 §2.1 rule 1, §2.9.6; replaces UB-S7)

1. **Lease:**
   - At start, the executor takes an OS-exclusive lock on `chain-b/executor.lock` and holds it for its whole life; the OS releases it when the process ends.
   - Failure to take it → the executor exits without writing anything.
   - Holding it, the executor appends **EXECUTOR_START** {instance_id (random 128-bit), pid, executor_id}.
2. **Every executor write** carries `instance_id`. A record from an instance other than the latest EXECUTOR_START is invalid, and the fold rejects it (U-G4 still applies: this guards against accidents, not malice).
3. **Recovery** (R5-B2 §2.9.6) runs only under the lease, before any eligibility poll.
   - It is **idempotent**: every recovery action first checks the chain for an existing terminal record for the same WAL or authorization, and skips if one exists. ORDER_TERMINAL remains refused if a duplicate exists (UB-L1).
   - A crash during recovery is followed by a full re-run of recovery.
4. The decision process does not need the lease. It never writes executor record types.

### §F. Independent reconciliation identity (replaces R5-B2 §2.8 L-3)

1. **Conclusive identity:** a dashboard order is conclusively identified with a chain order only by an equal **COID**, or an equal **broker order id** (the id the broker assigned, recorded from the first observed order object, §D). **[VENUE: which identifiers the dashboard shows]**
2. **Field-only correspondence** (side, qty, price, time) is recorded as **UNRESOLVED**. It never yields PASS and never clears AMBIGUOUS.
3. **L-3 PASS requires all of:**
   - every dashboard order in the session's time window is conclusively identified with a chain order;
   - the dashboard order count in that window equals the number of chain orders observed (by SEND or QUERY) in it;
   - no chain order is missing from the dashboard.
4. **Outcomes:**
   - a dashboard order with no conclusive identity and no field correspondence → UNMEDIATED, halt;
   - a dashboard order with only a field correspondence → UNRESOLVED; SESSION_CLOSE blocked;
   - a WAL with no dashboard order → no conclusion (it is not proof of non-submission). The AMBIGUOUS state stays.
5. **Venue gate:** if the dashboard shows neither identifier, L-3 cannot pass, so the milestone cannot be claimed. The founder then decides on another independent identity source; R-d confirmation emails, for example, would need verification. That is not designed here (convergence rule).

### §G. Internal corrections (G-B2-07)

1. **Executor allowlist** (R5-B2 §2.1) adds `GET /v2/orders?status=open` (SESSION_OPEN, recovery). **Complete executor route set:**
   - `POST /v2/orders`;
   - `GET /v2/orders?status=open`;
   - `GET /v2/orders:by_client_order_id`;
   - `GET /v2/account`;
   - `GET /v2/positions`;
   - `GET /v2/account/activities`;
   - data client: bars and latest quote.

   Any other route → refused before I/O.
2. **Writer table** (R5-B2 §2.1) is aligned with the schema:
   - **founder CLI:** RECONCILE_L3, SESSION_CLOSING, DISCREPANCY, RUN_STOPPED_B, AMBIGUOUS_RESOLUTION (§D);
   - **decision process:** additionally DISCREPANCY (for its own route refusals and anchor failures);
   - **executor:** additionally EXECUTOR_START, NOT_ACCEPTED, ROUNDING_RESIDUAL.
3. **Death records:**
   - AUTH_DEATH = death **before** CONSUME (decision: EXPIRED, CHECK_B_FAILED, SESSION_CLOSING; executor: CHECK_C_FAILED, CLOCK_ADJUSTED, RECOVERY_EXPIRED);
   - NOT_SENT = death **after** CONSUME and before t_tx0.
   - The R5-B2 §2.1 phrase "AUTH_DEATH (consumed, not sent)" is deleted.
4. **Pre-flight paths:** P4 is split into **P4a** `GET /v2/assets/BTC%2FUSD` and **P4b** `GET /v2/assets/BTCUSD`. The tool has **six** fixed GETs. P4 passes if at least one returns 200 with the required fields; both responses are recorded.
5. **TER-2 changes:**

   | Record | Change |
   |---|---|
   | RECONCILE_L2 | `rounding_rule_matched` → `bases [{basis, C_exact, residual}]`, `consistent_pairs [{basis, rule}]`, `authoritative_basis` |
   | EXECUTOR_START | new: {instance_id, pid, executor_id} |
   | every executor record | adds `instance_id` |
   | ROUNDING_RESIDUAL | new: {ref_seq, residual, basis, consistent_pairs} |
   | AMBIGUOUS_RESOLUTION | new, founder CLI: {wal_seq, resolution ∈ {NOT_SUBMITTED, FOUND}, query_refs, l3_ref, statement}. It is the only way an AMBIGUOUS order ends without a venue order |
   | ORDER_TERMINAL | adds `broker_order_id`, `G_fills`, `G_avg`, `authoritative_basis`, `max_fill_price` |
   | SEND_RESULT | adds `t_d_mono`, `t_tx0_mono`, `t_resp_mono`, `budget_ns` |
   | NOT_SENT | reasons now {LATE, CHECK_D_FAILED, CLOCK_ADJUSTED, SESSION_CLOSING, SEND_NOT_BEGUN, LOCAL_CERTAIN_RECOVERY} (unchanged set; "consumed" wording removed) |
   | AMBIGUOUS | `cause` adds CLOCK_ADJUSTED_AFTER_RELEASE |
   | GENESIS_B | `stage_a_anchor` per item 8 |
   | AUTHORIZATION | adds `attempt_index`, `campaign_ref` (§H) |

6. **UB-T3 moved** out of the acceptance gate. It becomes an **observation** recorded at the first real send (SEND_RESULT timing fields). It informs later revisions; it gates nothing.
7. **GENESIS_B anchor (D-8, amended)** adds:
   - `seed_commitment` {commit, file, sha256_of_seed} and `seed_reveal` {commit, file};
   - verification: SHA-256(revealed seed ASCII) = the committed hash, and the commit order is commitment < scope < reveal;
   - `audit_result` {report_sha256, verdict, audited_chain_head, audited_scope_sha256, auditor_sha256}.

   **RUN_OPEN_B is refused unless:**
   - verdict = M1 MET;
   - the exit record states M1 MET and cites `report_sha256`;
   - audited_chain_head = stage_a_chain_head_at_run_close for the audited scope;
   - audited_scope_sha256 = scope_sha256;
   - auditor_sha256 = the pinned auditor hash.

   Git ancestry and commit order are checked by the founder script (R5-B2 §2.2), and the hashes by the harness.

### §H. Per-attempt approval versus permission for later attempts

1. **Two distinct authorities:**
   - **Per-attempt:** the APPROVAL record (R5-B2 §2.12) authorizes **one** order: one authorization, one COID, one send. It never carries over.
   - **Campaign permission (P23, amended):** a founder record authorizing attended Stage B sessions with **max_attempts = K** (founder-chosen) and an expiry date. It **does not** approve any order. Each attempt still needs its own APPROVAL.
2. **Attempt counting:**
   - an attempt = an AUTHORIZATION issued under the campaign. `attempt_index` = 1, 2, …;
   - the decision process refuses issuance when attempt_index would exceed K, or after the campaign's expiry, or if the campaign record's hash does not match the one pinned at RUN_OPEN_B.
3. **After a zero-fill outcome** (ORDER_TERMINAL with Q_f = 0, or NOT_ACCEPTED, or a NOT_SENT): the next attempt is permitted **only if**:
   - K is not exhausted;
   - the previous attempt is fully terminal with L-2 PASS and L-3 PASS (§F);
   - no halt is uncleared;
   - a new BUY signal passes policy in an attended session.

   **No resubmission of the same order**, and no relaxation of any parameter between attempts. **If K = 1**, a zero fill ends the campaign and a new founder record is needed.
4. **The first fill ends the campaign's milestone purpose.** Later attempts under the same campaign are refused once an ORDER_TERMINAL with Q_f > 0 exists. The milestone is one governed BUY, and a round trip or EXIT is outside scope.
5. **Do not force a fill:** K bounds attempts. It is not a target, and nothing in the design increases fill probability.

---

## 3. Changed acceptance-test rows (delta to R5-B2 §4)

| ID | Status | Test | Expected |
|---|---|---|---|
| UB-L4′ | replaces UB-L4 | broker cash vs C_exact on each basis, under each predeclared rule; cases: exact equality; equality under several rules; equality under one rule only; residual 0.004 with no consistent rule; residual 0.01 | records all consistent pairs and residuals; PASS / PASS / PASS / DISCREPANCY / DISCREPANCY; **no rule is pinned** |
| UB-L5′ | replaces UB-L5 | one fill at p_i > L; P̄ > L only through rounding, with all p_i ≤ L; no fill records and P̄ > L; G + fee > R | DISCREPANCY / recorded, PASS / DISCREPANCY / DISCREPANCY |
| UB-L7 | new | L-2 PASS with r ≠ 0 | ROUNDING_RESIDUAL appended; the fold equals broker cash; a second L-2 at the next SESSION_OPEN passes with r = 0 |
| UB-X5 | new | SESSION_CLOSING appended before PRESEND / after PRESEND | NOT_SENT (SESSION_CLOSING) / send proceeds, tracked, reconciled; SESSION_CLOSE only after the terminal |
| UB-T1′ | replaces UB-T1 | wall clock drifts +60 ms at each of 5 checkpoints (each step < ε, cumulative 300 ms); one step of exactly 250 ms; a step after PRESEND | CLOCK_ADJUSTED at the 5th / pass / AMBIGUOUS (CLOCK_ADJUSTED_AFTER_RELEASE) |
| UB-T2′ | replaces UB-T2 | W(t_d) = expires_at − δ_send / + 1 ns; t_tx0 at t_d + 2 s / + 2 s + 1 ns; response at t_d + 10 s − 1 ns / exactly 10 s | send / NOT_SENT (LATE); send / NOT_SENT (SEND_NOT_BEGUN); terminal path / AMBIGUOUS (SEND_OVERRAN) |
| UB-T5 | new | the stub stalls the connection; check the client timeout actually applied | timeout = δ_send − (t_tx0 − t_d) ± 50 ms; one connection; AMBIGUOUS |
| UB-S5′ | replaces UB-S5 | statuses 400, 401, 403, 422 (two not-found queries); 422 then found on the 2nd query; 404, 408, 409, 429, 500 (not found) | NOT_ACCEPTED ×4 / tracking + L-1 + DISCREPANCY / AMBIGUOUS ×5 (no reclassification) |
| UB-S8 | new | send times out; the order is later found by query with a bound field differing / equal | L-1 FAIL, halt / L-1 PASS, tracking |
| UB-E1 | replaces UB-S7 | start a second executor while the first holds the lease | the second exits with no write; the stub sees no request from it |
| UB-E2 | new | kill the executor mid-recovery at each recovery step; restart | final fold identical to an uninterrupted recovery; exactly one ORDER_TERMINAL per COID; zero extra POSTs |
| UB-E3 | new | a record carrying a stale instance_id | rejected by the fold; DISCREPANCY |
| UB-L3S′ | replaces UB-L3S | founder L-3 procedure on stub records: COID match; broker-id match; field-only match; an extra dashboard order; count mismatch | PASS / PASS / UNRESOLVED (close blocked) / UNMEDIATED halt / UNRESOLVED |
| UB-C5 | new (supersedes the executor half of UB-C1) | each route in §G.1 allowed; any other route on the trading host refused before I/O | as stated |
| UB-P1′ | amends UB-P1 | the tool issues exactly the six fixed GETs and nothing else | six requests at the stub |
| UB-A1′ | extends UB-A1 | revealed seed hash ≠ commitment; verdict ≠ M1 MET; exit record cites another report hash; audited chain head ≠ anchor head; audited scope hash ≠ scope.json | RUN_OPEN_B refused in each case |
| UB-K1 | new | campaign K = 2: attempt 1 zero-fill fully reconciled → attempt 2 issued; attempt 3 → refused; expired campaign → refused; attempt 2 while attempt 1's L-3 is UNRESOLVED → refused | as stated |
| UB-K2 | new | an attempt after a filled attempt under the same campaign | refused |
| UB-T3 | **removed from the gate** | becomes an observation at the first send | — |

---

## 4. Remaining mandatory dependencies

**Typed:** [AUTH] founder authorization · [DESIGN] review · [VENUE] venue observation · [EXEC] executed verification.

| # | Dependency | Type |
|---|---|---|
| 1 | M1 met on the audit scope (one or more Stage A manifests): auditor run, seed reveal, hand cross-check | [EXEC] |
| 2 | founder Stage A exit record (M1 MET; OI-08) | [AUTH] |
| 3 | v6 adoption (the updated record accompanies this delta) | [AUTH] |
| 4 | FD-8 key custody | [AUTH] |
| 5 | D-9: build and run the six-GET pre-flight tool | [AUTH] → [EXEC] |
| 6 | pre-flight results: account, positions, orders, asset fields | [VENUE] |
| 7 | P-0.3 policy (TIF ioc; observed increments) | [AUTH] |
| 8 | GPT closure check of R5-B3 against G-B2-01 to G-B2-07 only | [DESIGN] |
| 9 | Stage B freeze; FD-9 | [AUTH] |
| 10 | build; the §4 R5-B2 tests as amended here, executed with retained evidence | [EXEC] |
| 11 | blind Stage B auditor; hash committed; Gemini B challenge | [EXEC] |
| 12 | P23 campaign permission with K and an expiry | [AUTH] |
| 13 | an attended session with a policy-passing BUY | [VENUE] (market; UNBOUNDED) |

**Venue gates, observed at the first order or the first terminal; no prose resolves them:**
- V-1: the dashboard shows COID or broker order id (§F; if neither, the milestone cannot be claimed);
- V-2: crypto IOC accepted (a rejection is a valid attempt and leads to a spec amendment);
- V-3: fill records available (which gross basis is authoritative);
- V-4: fee presence and fields (F1/F2/F3);
- V-5: the rounding residuals observed.

**Not dependencies:** GTC (Annex A of R5-B2), duplicate-COID, EXIT, R-d email, signatures, host isolation, remote approval.

*End of R5-B3.*
