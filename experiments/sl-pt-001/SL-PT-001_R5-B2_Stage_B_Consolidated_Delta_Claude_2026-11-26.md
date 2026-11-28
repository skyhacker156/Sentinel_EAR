# SL-PT-001 R5-B2: Stage B consolidated delta (against frozen R4.2i)

**From:** Claude (Implementation Lead) | **To:** Founder; GPT | **Responds to:** Strike 7.3 (G-B1-01 to G-B1-09; the market-data revalidation dependency; IOC compression)
**Date:** 2026-11-26 | **Base:** R4.2i SHA-256 `4259551121fa3d271074fb13da51fb270ae859b0b516a953752731f20972a51a`; G-07 Draft 0.3
**Supersedes:** R5-B0 and R5-B1 entirely. This document is self-contained; the earlier two are drafts of record only.
**Status:** DRAFT, not a freeze candidate (the gates are in §6). Nothing is authorized, built, keyed or sent.

**Evidence boundary:**
- No Stage A run evidence from `run-stage-a-1` is used or quoted here.
- The one empirical input is the **pre-run** Stage A-0 probe quote (committed 2026-11-26, `probe-A0/quote_body.json`).
- No harness code or harness internals appear; harness reuse is stated only by R4.2i section.

**Scope rule:**
- Every change is confined to the R4.2i Stage B draft sections (§8.2–§8.6, §9, §12, the B-only tests, and the B rows of §15 and §16) or to new Stage B-only sections.
- **No Stage A section changes.**
- Where frozen Stage A text already binds Stage B, this delta **complies** with it rather than amending it: §7.3 R4 freshness "B: (a)–(d)"; §4.9 "Stage B: at checkpoints (b) and (c) the window is re-fetched"; §7.2 limit rounding.

**Labels:** DERIVED, DOCUMENTED, OBSERVED, UNVERIFIED and ASSUMED, as in R4.2i. Each unresolved item is typed as **[DESIGN]**, **[AUTH]** (founder authorization), **[VENUE]** (needs venue observation) or **[EXEC]** (needs executed verification).

---

## 1. Finding-closure matrix

| Finding | Mechanism (as raised) | Resolution | Where | Residual |
|---|---|---|---|---|
| **G-B1-01** cancel timing: zero margin | GTC cancel not_before = T_d+170 s = expires_at − δ_send, so the LP-PRESEND window has zero width | **IOC is the milestone branch, so there is no cancel path on the critical path.** GTC moves to Annex A as deferred, with a corrected window that has a 20 s positive margin | §2.5, Annex A | none on the critical path |
| **G-B1-02** session close vs reconciliation | closing the session would either allow late sends or abandon open reconciliation | **Two-phase close.** SESSION_CLOSING immediately removes eligibility for approval, issuance, consumption and sending; tracking, queries and L-2/L-3 continue. SESSION_CLOSE is written only when nothing is open | §2.3 | an AMBIGUOUS order keeps the session in CLOSING indefinitely (fail-closed, intended) |
| **G-B1-03** lock ≠ crash-atomic | a crash between two records written under one lock hold leaves an authorization without its reservation | **One transition = one record.** The reservation is a field of AUTHORIZATION; booking and release are fields of ORDER_TERMINAL; death and release are one AUTH_DEATH. A torn final line is never eligible and halts the session | §2.4, §3 | file-system honesty of fsync (R4.2i U-T5, carried) |
| **G-B1-04** temporal enforcement; freeze vs stub sequencing | (i) bounds not all assigned a clock and a check point; (ii) R5-B1 set δ_send "at the freeze from S6", but S6 runs after the freeze | (i) the complete temporal table, §2.6. (ii) **δ_send is fixed at the freeze** (10 s) and checked against **pre-flight** round-trip times, which precede the freeze. S6 verifies it; an S6 failure is a test failure needing a spec amendment, never a silent retune | §2.6, §5 | the real send duration of a POST is observed only at the first order (UB-T3 logs it) |
| **G-B1-05** ambiguous vs WAL; transport retry | L-3 matched broker orders to SEND records, but a crash after the WAL and before the SEND record leaves a real order looking UNMEDIATED | **L-3 matches on COIDs from WAL records.** Every WAL record without a terminal record is "possibly at venue". The HTTP layer makes **exactly one attempt per WAL**: fresh connection, no retry, no redirect following, no idempotent replay | §2.7, §2.8 | dashboard COID visibility **[VENUE]** (fallback match rule given) |
| **G-B1-06** ledger arithmetic | dedup, precision, fee handling, recovery and release were not closed | **Book once at the reconciled terminal state** from cumulative order state; exact decimals; three-case fee rule with no inference; an explicit broker-rounding comparison; the release formula; the recovery fold | §2.9 | paper fee presence and fields **[VENUE]**, resolved by the first terminal order, not by assumption |
| **G-B1-07** anchor to real M1 | the anchor pinned RUN_CLOSE, which shows a run ended, not that it passed | GENESIS_B pins the **founder Stage A exit record** (stating M1 MET), the auditor report, the hand cross-check, scope.json, the auditor hash and the chain head. RUN_OPEN_B is refused unless all of them verify | §2.2 | origin ancestry is checked by a founder script (Git), not by the harness |
| **G-B1-08** pre-flight vs build authority; credentials; response coverage | R5-B1 ran the pre-flight from the executor, so authorizing it implied executor code | **A separate GET-only pre-flight tool**, authorizable without FD-9; key hygiene rules; per-endpoint expected-status and expected-field coverage | §2.10, §2.11 | field names DOCUMENTED, not observed **[VENUE]** (the pre-flight observes them) |
| **G-B1-09** confirmation claims; material fields | "shows the founder saw the proposal" overclaims; the display omitted economically material fields | Claim corrected (§2.12). A **complete approval view**: every economically material field, including maximum loss | §2.12 | none |
| **Revalidation dependency** | checkpoints (c) and (d) need fresh market data (frozen §7.3, §4.9), but the executor was barred from the data host and the decision process holds no keys | **The executor holds two clients.** A trading client (keys; paper trading host only) and a keyless data client (data host only; built without access to the key object; no credential headers). The decision process is unchanged and keyless | §2.1 | the executor process contains keys while it fetches data (disclosed; G7-I5 is not claimed) |

---

## 2. Consolidated delta

### 2.1 Processes and egress (replaces R5-B1 Δ1)

| Process | Role | Credentials | Clients and allowlist | Writes |
|---|---|---|---|---|
| **Decision** (R4.2i pipeline, reused) | K2+K3 | none; V12a unchanged | data client → `data.alpaca.markets` | PROPOSAL, CYCLE_B, AUTHORIZATION, AUTH_DEATH (unconsumed) |
| **Approval CLI** (part of the decision codebase) | K3 input | none | none | APPROVAL, APPROVAL_REFUSED |
| **Executor** | K5 | paper key pair, **in memory only** (§2.11) | trading client → `paper-api.alpaca.markets`: `POST /v2/orders`, `GET /v2/orders:by_client_order_id`, `GET /v2/account`, `GET /v2/positions`, `GET /v2/account/activities`. Data client → `data.alpaca.markets`: bars and latest quote only | SESSION_OPEN, SESSION_CLOSING, SESSION_CLOSE, CONSUME, WAL, PRESEND, NOT_SENT, SEND_RESULT, QUERY, AMBIGUOUS, ORDER_TERMINAL, RECONCILE_L2, AUTH_DEATH (consumed, not sent), DISCREPANCY |
| **Founder CLI** | records only | none | none | RECONCILE_L3, RUN_STOPPED_B |
| **Session console** | display and alert | none | none | none |

**Rules:**
1. There is no call path from the decision process to the executor. The executor polls the Stage B chain at 1 s monotonic intervals.
2. **Each client refuses non-allowlisted hosts and routes before I/O.** The data client is constructed without a reference to the key object; it sends no `APCA-*` or `Authorization` header (UB-C2).
3. **Linearizable reads:** the executor evaluates eligibility, (c) and (d) on state read **under the chain append lock** (R4.2i §6.3), which satisfies G7-A2 by construction.
4. **Same-host clock:** σ = 0 by construction, void if the processes are split. The venue clock relationship uses the R4.2i §5.6 interval method on every data response, as in V12b.
5. **Disclosed (U-G4):** both processes run as the same OS user and write one file. Record authorship by role is not provable, so a compromised executor can forge any record. This falls under G7-A1 and is no stronger than G7-I8, which is already false.

### 2.2 Stage B chain and the M1 anchor (G-B1-07)

- **Chain:** `chain-b/events.jsonl`, with the R4.2i §10.1 envelope and §10.5 canonical serialization. Stage B code never writes the Stage A chain.
- **GENESIS_B body:**
  - `stage_b_frozen_set_hashes`;
  - `policy_sha256` (P-0.3);
  - `stage_a_anchor` = {
    - `exit_record` (path and SHA-256 of the founder's Stage A exit decision record, which must state **M1 MET** and the OI-08 decision);
    - `audit_report_sha256` (the auditor's committed output for the run);
    - `hand_crosscheck_sha256`;
    - `scope_commit` and `scope_sha256`;
    - `auditor_sha256`;
    - `manifest_sha256`;
    - `stage_a_chain_head_at_run_close` }.
- **RUN_OPEN_B is refused** unless every file named in the anchor exists locally with the pinned hash, and the Stage A chain contains a RUN_CLOSE for `manifest_sha256` whose hash equals `stage_a_chain_head_at_run_close` (UB-A1).
- **Origin ancestry:** a founder `.ps1` verifies that the anchor commit is an ancestor of `origin/main` before the Stage B task is registered (UB-A2). This is a Git check, outside the harness.

### 2.3 Sessions: two-phase close (G-B1-02)

**States:**
- **OPEN:** set by SESSION_OPEN, after the open checks pass.
- **CLOSING:** set by SESSION_CLOSING, written on the founder's `session close`, on any halt condition (§2.13), or on executor shutdown.
- **CLOSED:** set by SESSION_CLOSE.

| Action | OPEN | CLOSING |
|---|---|---|
| decision process issues an AUTHORIZATION | allowed (if the rules pass) | **refused**; the cycle ends EXPIRED_UNAPPROVED or AUTHORIZATION_DIED (SESSION_CLOSING) |
| approval CLI writes APPROVAL | allowed | **refused** (APPROVAL_REFUSED, SESSION_CLOSING) |
| executor CONSUME | allowed (eligibility) | **refused** |
| executor PRESEND | allowed | **fails**: NOT_SENT (SESSION_CLOSING); full release |
| query by COID; tracking; L-2; L-3 | allowed | **allowed and required** |

**SESSION_OPEN preconditions:**
- the previous session is CLOSED;
- the executor's account, positions and orders reads match the ledger fold (§2.9), and the open orders list is empty;
- no record in the chain is torn (§2.4).

**SESSION_CLOSE preconditions:**
- every WAL has a terminal record (ORDER_TERMINAL, NOT_SENT or NOT_ACCEPTED);
- every AUTHORIZATION has a CONSUME or an AUTH_DEATH;
- every terminal order has RECONCILE_L2 = PASS and a RECONCILE_L3 attestation;
- no reservation remains unreleased.

**If any precondition fails, the session stays in CLOSING.** A restarted executor in a CLOSING session runs **recovery only** (§2.9.6): queries, terminal booking and reconciliation, never a send.

### 2.4 Crash atomicity (G-B1-03)

1. **Each state transition is exactly one record**, written by one `write + flush + fsync` under the append lock before the lock is released (R4.2i §6.4 step 8, reused).

| Transition | Record | Carries |
|---|---|---|
| authorization issued | AUTHORIZATION | the reservation (R, f_res, the cash it reserves) |
| an unconsumed authorization dies | AUTH_DEATH | the full release |
| local consumption | CONSUME | — |
| send intent | WAL | — |
| final validity | PRESEND | — |
| local non-send after the WAL | NOT_SENT | the full release |
| venue terminal | ORDER_TERMINAL | the booking and the release |

   A crash can therefore never leave half a transition.
2. **Torn tail:** if the final line fails to parse or fails its hash, then:
   - nothing after the last valid record is acted on;
   - the executor writes nothing except, after founder action, a DISCREPANCY (TORN_TAIL);
   - the session stays CLOSING.

   Repairing a torn file is a founder act, recorded in a decision record. No code truncates the chain.
3. **Recovery** (§2.9.6) derives all state by folding valid records. No state is held outside the chain except the in-memory key.

### 2.5 Execution branch: IOC (compression; G-B1-01)

- **TIF = IOC** for the milestone `[DESIGN, founder adoption: D-10]`.
  - GTC and its cancel path are **removed from the critical path** and moved to Annex A as deferred.
  - The policy P-0.3 TIF allowlist = {`ioc`}.
- **Why IOC is suitable (DERIVED from the pre-run probe; the fill rate is UNVERIFIED):**
  - The probe ask (60663.76) sits on a $0.01 grid. With the policy price increment of $1, §7.2 sets L up to $0.99 below the ask, $0.76 at the probe.
  - At an assumed annualized BTC volatility of about 50%, the 60 s price move is roughly ±$40 at that level. The rounding offset is therefore about 2% of one minute's typical move.
  - **The fill probability of one IOC attempt is dominated by the price drift between checkpoint (a) and the send**, which spans up to about 140 s of approval and checks, not by the rounding. Under a driftless random-walk assumption it is somewhat below one half.
  - It is UNVERIFIED and is not a design target.
- **If the pre-flight shows a finer price increment** (for example $0.01), §7.2 makes L equal to the ask and the conclusion is unchanged. **The pre-flight cannot make IOC unsuitable, except** if the asset record contradicts crypto IOC support. Crypto IOC support is DOCUMENTED and is verified only by the first order: a VENUE_REJECTED for an unsupported TIF is a valid governed attempt, followed by a spec amendment.
- **Do not force a fill.**
  - A zero-fill IOC terminal (canceled with filled_qty = 0) is a **valid governed attempt**: it is booked, released and reconciled.
  - It is **not** the milestone (§0.1).
  - The next BUY signal in an attended session is the next attempt, with no retry or resubmission.
  - The milestone is met only by an attempt with Q_f > 0.
- **Partial fill:** `partial_fill_accepted = true` (R2). An IOC that fills partly is terminal (`canceled` with filled_qty > 0), and that meets the milestone.
- **§7.2 is unchanged** (it is frozen).

### 2.6 Temporal enforcement: the complete table (G-B1-04)

**Clocks:** W = OS wall clock (UTC ns). M = OS monotonic clock (process-local ns, recorded with the pid). All bounds are inclusive or exclusive exactly as written.

| Bound | Value | Clock | Checked where | On violation |
|---|---|---|---|---|
| completed bar; settle | R4.2i §5.4 (frozen) | W | decision (a); executor (c) | NO_DECISION / AUTH_DEATH (BAR_INVALID) |
| cutoff | T_d + 120 s − created ≥ 90 s | W | decision (a) | REJECTED (R13) |
| quote fresh | 0 ≤ c − quote.t ≤ 15 s, at each of (a), (b), (c), (d) | W, against the venue `Date` interval (§5.6) | decision (a), (b); executor (c), (d) | REJECTED (a) / AUTH_DEATH (b, c) / NOT_SENT (d) |
| venue clock offset | ≤ 2 s (§5.6 method) | W | every data response, both processes | BOUNDARY_FAIL / AUTH_DEATH / NOT_SENT |
| approval timely | approved_at ≤ approval_deadline = T_d + 120 s | W | approval CLI; decision (b) | APPROVAL_REFUSED (LATE) / EXPIRED_UNAPPROVED |
| issuance timely | approved_at ≤ issued ≤ T_d + 120 s | W | decision (b) | AUTH not issued; cycle EXPIRED_UNAPPROVED |
| authorization window | not_before = issued; expires_at = issued + 60 s (≤ T_d + 180 s) | W | executor eligibility, (c), (d) | not eligible / AUTH_DEATH |
| PRESEND margin | W(d) ≤ expires_at − δ_send, **δ_send = 10 s** (fixed at the freeze) | W | executor (d) | NOT_SENT (LATE) |
| send start | the first byte begins within δ_send of the (d) sample | M | executor | NOT_SENT if not begun (certain); SEND_OVERRAN → AMBIGUOUS if begun late |
| send response | ≤ 10 s from the first byte | M | executor | AMBIGUOUS (no retry) |
| clock adjustment | \|ΔW − ΔM\| ≤ ε_step = 250 ms between consecutive checkpoints (b)→(c)→(d)→send-end, and between consecutive 1 s executor polls | W and M | executor; decision (b) | AUTH_DEATH (CLOCK_ADJUSTED) before the send; AMBIGUOUS after; session CLOSING |
| executor poll | every 1 s (M); an eligible authorization is consumed in issuance order | M | executor | — |
| tracking | query by COID every 2 s (M) from the SEND result until a venue-terminal status | M | executor | not terminal by T_d + 300 s → ORDER_UNRESOLVED (counts as AMBIGUOUS for R16); queries continue every 30 s |
| terminal settle | account, positions and activities re-read every 5 s for ≤ 60 s after the terminal status, until they reflect the order | M | executor | L-2 DISCREPANCY (NOT_SETTLED) |
| slot handoff | an order open at T_d(i+1) → slot i+1 NO_ACTION / BLOCKED_OPEN_ORDER (U51) | W | decision (a) | — |

**Timing margin on the critical path (DERIVED):**
- The worst case is issued = T_d + 120 s, so expires_at − δ_send = T_d + 170 s. That leaves **≥ 50 s** for one poll, checkpoint (c) (a quote plus the bar re-fetch), the WAL, and checkpoint (d) (one quote).
- Margin stays positive as long as those take < 50 s. The pre-flight round-trip times (§2.10) supply the evidence before the freeze.
- The send ends by T_d + 180 s at the latest, which is ≪ T_d + 300 s.

**Sequencing (G-B1-04 ii):**
- δ_send and ε_step are fixed values at the Stage B freeze.
- Before the freeze, the pre-flight's observed GET round-trip times must satisfy p_max < δ_send / 2, which is 5 s. Otherwise δ_send is reconsidered *before* the freeze.
- After the freeze, S6 stub tests verify enforcement (not the value). The first real send's duration is logged (UB-T3).
- Any later evidence that the value is wrong is a finding that requires a spec amendment and a new Stage B freeze.

### 2.7 Submission: exactly one attempt (G-B1-05)

1. **Sequence at the executor for one eligible authorization:**
   1. CONSUME at (c);
   2. **WAL** {auth_id, COID, `request_body_sha256` of the exact bytes to send}, fsynced;
   3. checkpoint (d) and the PRESEND record;
   4. **one** HTTPS `POST /v2/orders` with exactly the WAL's bytes.
2. **Transport:**
   - a new connection for the POST;
   - the client's retry count is 0;
   - redirects are not followed;
   - no automatic replay on a connection reset or timeout.

   Any transport error after the first byte → AMBIGUOUS. **No code path re-sends a WAL's bytes** (UB-S3, UB-S4).
3. **The request body (IOC):** `{"symbol":"BTC/USD","qty":"<q>","side":"buy","type":"limit","limit_price":"<L>","time_in_force":"ioc","client_order_id":"<COID>"}`, serialized canonically. q and L are decimal strings on the policy grid.
4. **COID** = `slpt001-` + the first 48 hex characters of auth_id. One per authorization; never reused.
5. **Outcomes:**

   | Response | Then | Result |
   |---|---|---|
   | 2xx with an order object | L-1 (§2.8) → tracking | — |
   | 4xx with a body | query by COID | not found → NOT_ACCEPTED (terminal; full release). Found → tracking, plus DISCREPANCY (CONTRADICTORY_RESPONSE) |
   | timeout, 5xx, transport error, or malformed 2xx | query by COID | found → tracking. Not found → **stays AMBIGUOUS**: no new authorization (R16), no resubmission (D-1), queries continue every 30 s, founder notified |

### 2.8 Reconciliation L-1 to L-4 (G-B1-05)

- **L-1:** the echoed order object is decoded by a decoder separate from the request builder, and compared field by field with the AUTHORIZATION: symbol, side, qty, type, limit_price, TIF and COID. Any difference → governance failure, halt (SESSION_CLOSING).
- **L-2:** at every terminal and at every SESSION_OPEN (§2.9.5).
- **L-3, independent of the executor (founder):** after each terminal and at session close, the founder compares the Alpaca dashboard order history with **the set of COIDs in WAL records**.
  - **Match key:** the COID if the dashboard shows it **[VENUE]**. Otherwise (side, qty, limit price, and submission time within [WAL instant, WAL instant + 30 s]).
  - A dashboard order matching no WAL → UNMEDIATED, halt.
  - A WAL with no dashboard order and no NOT_SENT/NOT_ACCEPTED record → AMBIGUOUS remains.
  - Recorded via the founder CLI as RECONCILE_L3, with the counts and the attestation text.
- **L-4:** after the milestone attempt, the blind Stage B auditor (D-7) reconstructs the lifecycle from the committed chain-b and artifacts, with 0 unexplained differences.

### 2.9 Ledger (G-B1-06; replaces R4.2i §8.2–§8.5 draft text for the IOC milestone)

**2.9.1 Units and precision.**
- All values are exact decimals (R4.2i §5.1).
- USD amounts held by Sentinel are on the cent grid; BTC amounts are held **exactly as reported**. The quantity increment constrains order quantities only, not held balances, because a BTC fee can leave a sub-increment balance.
- Venue decimal strings are parsed by the §4.10 rules; a malformed value → DISCREPANCY.

**2.9.2 Reservation** (in AUTHORIZATION).
- q and R per §8.1.1 with the reconciled cash_available.
- reserved_usd += R, at most one unreleased reservation (R11, R16).

**2.9.3 Booking** (once per COID, in ORDER_TERMINAL).
- Taken from the **terminal** order object (cumulative `filled_qty` Q_f, `filled_avg_price` P̄) and the settled account reads.
- **No per-fill streaming booking.** Intermediate order states are QUERY observations only.
- **Dedup:** a second ORDER_TERMINAL for one COID is refused (UB-L1). The booking is cumulative, so no fill can be counted twice.
- **Fee, exactly three cases, no inference:**
  - **(F1)** the account activities return fee record(s) for the order, with asset and amount stated: book them as reported.
  - **(F2)** no fee record exists, **and** the position delta = Q_f, **and** the cash delta = −Q_f × P̄ under one of the broker-rounding rules below: fee = 0, recorded as FEE_NONE_OBSERVED.
  - **(F3)** anything else → DISCREPANCY (FEE_UNRESOLVED), halt.
- **Gross cost:** G = Q_f × P̄ (exact).
- **Sentinel cash after:** cash − G − fee_usd, compared to the broker under the broker-rounding rule.
- **BTC after:** held + Q_f − fee_btc (exact).
- **L-2 fee bound** (R4.2i §8.4): Σ fee_usd_equiv ≤ Q_f × L × (1 + f_res) − G. Otherwise DISCREPANCY.

**2.9.4 Release** (in the same ORDER_TERMINAL record).
- reserved_usd −= R, in full. The booked amounts above replace it.
- **Check:** G + fee_usd_equiv ≤ R. This follows from P̄ ≤ L, IOC limit semantics and the fee bound; a violation → DISCREPANCY.
- An AUTH_DEATH or NOT_SENT or NOT_ACCEPTED releases R in full, with no booking.
- **AMBIGUOUS keeps R reserved.**

**2.9.5 Broker comparison (L-2), the rounding rule.**
- **USD:** the broker's cash must equal Sentinel's exact cash rounded to the cent under **one** of {floor, ceiling, half-even}. The rule that matches is recorded. No match → DISCREPANCY.
- After the first terminal order, the observed rule is pinned in a founder record. Later comparisons use that rule only **[VENUE]**.
- **BTC:** the broker's position quantity must equal Sentinel's exact value.
- **Open orders:** the broker must show none that Sentinel does not show as open.

**2.9.6 Recovery** (executor start, any session state).
1. fold chain-b;
2. a torn tail → stop (§2.4);
3. each WAL without a terminal record → query by COID (§2.7 rules), **never send**;
4. each CONSUME without a WAL → NOT_SENT (LOCAL_CERTAIN: no WAL means no bytes were sent), with full release;
5. each AUTHORIZATION without a CONSUME and past expires_at → AUTH_DEATH (EXPIRED), with full release;
6. then L-2.

Recovery runs before any polling for eligibility. In a CLOSING session, polling never starts.

### 2.10 Pre-flight tool (G-B1-08; separate authority D-9)

**A separate, minimal tool.** It is not the executor, and it shares no code path that can submit.

**Rules:**
- **GET only.** The HTTP method is fixed in the request builder, and any other method raises before I/O.
- The five paths are hard-coded. Host: `paper-api.alpaca.markets` only.
- **Authorizable under D-9 without FD-9.**

**Endpoint coverage:**

| # | Request | Expected status | Required fields (DOCUMENTED names, to be OBSERVED) | Pass condition |
|---|---|---|---|---|
| P1 | `GET /v2/account` | 200 | `status`, `crypto_status`, `cash`, `buying_power`, `multiplier`, `shorting_enabled`, `trading_blocked`, `account_blocked` | status and crypto_status ACTIVE; multiplier "1"; shorting false; both blocked flags false; cash ≥ 450.00 |
| P2 | `GET /v2/positions` | 200 | array | contains no BTC/USD (or BTCUSD) position |
| P3 | `GET /v2/orders?status=all&limit=500` | 200 | array | empty |
| P4 | `GET /v2/assets/BTC%2FUSD` (or `BTCUSD`, whichever the venue resolves; both recorded) | 200 | `tradable`, `status`, `min_order_size`, `min_trade_increment`, `price_increment` | tradable true; status active; values recorded for P-0.3 |
| P5 | `GET /v2/orders:by_client_order_id?client_order_id=slpt001-preflight-<UTC>` | 404 | — | 404 = not found (recorded); any other status → FAIL |

- **Every response is recorded:** method, path, status, the `Date` and request-id headers, body bytes and hash, and t_send/t_recv (W and M).
- **Any unexpected status** (401, 403, 429, 5xx, or a 200 on P5) or a missing required field → that item FAILS. The tool still completes the others, then exits non-zero.
- **Round-trip times** of P1–P5 are recorded; they are the δ_send evidence (§2.6).
- **Output:** a committed pre-flight record and artifacts. **The tool decides nothing.** The founder issues P-0.3 from the observed values, in a decision record.

### 2.11 Credential hygiene (G-B1-08; FD-8 proposal)

1. Keys are typed at the start of the pre-flight tool or executor (a no-echo prompt) and held **in process memory only**:
   - never in an environment variable, file, command line, scheduled-task XML, chain record, artifact or log;
   - never in the decision process (V12a still checks this).
2. **Request headers are never recorded.** Artifacts store response data, plus the request **body** only for POST (needed for L-1).
3. Error messages and exceptions are scrubbed of the header values before they are recorded or printed (UB-C3).
4. **Key rotation:**
   - the founder regenerates the paper key pair if it was ever pasted anywhere other than the prompt;
   - **optional:** regenerate after the pre-flight and before the first Stage B session, so that the executor's key has never been used by another tool.
5. Paper keys only. A live key in either tool's prompt is a misuse that the tools cannot detect. It is disclosed, and the founder attests to it in the session record.

### 2.12 Approval: view and claim (G-B1-09)

**The approval view shows every economically material field.** Each is computed from the PROPOSAL record, not re-derived:

| Group | Fields |
|---|---|
| order | instrument; side; type LIMIT; TIF IOC; `partial_fill_accepted` = true; q (BTC); L (USD); COID-to-be (shown after issuance) |
| money | notional q × L; fee reservation q × L × f_res; **R = the maximum cash that can leave the account**; cash before and cash_available after the reservation; equity (R12 basis); BTC held |
| market | bid, ask, mid; quote time and age; \|L − mid\| / mid; L − ask (the rounding offset) |
| signal | D(k−1), D(k); signal BUY; bar-window hash |
| policy | every rule R1–R16 with its result; policy hash; configuration hash |
| context | account (paper) id; venue; executor_id; session id |
| time | T_d; created; approval_deadline with a live countdown; the expected expires_at range |
| identity | the full `proposal_sha256`, with the 12-character confirmation prefix highlighted |

**Confirmation:**
- The founder types the 12 hex characters.
- The APPROVAL record binds the **full** 64-hex `proposal_sha256`, plus every bound field of R4.2i §9.1 and the context fields. Issuance requires exact equality (U63).

**Claim, corrected:** a valid APPROVAL shows that, at approved_at, an approval was entered in the session's interactive console by someone who had the displayed prefix of that proposal's hash. **It does not show:**
- that the fields were read or understood;
- who the person was;
- that the host was uncompromised.

### 2.13 Halt conditions (Stage B additions to R4.2i §9.7)

Each halt writes SESSION_CLOSING and DISCREPANCY (reason), and blocks the next SESSION_OPEN until a founder decision record clears it:
- L-1 mismatch; UNMEDIATED (L-3); FEE_UNRESOLVED; an L-2 mismatch; NOT_SETTLED;
- a torn tail; CLOCK_ADJUSTED;
- a contradictory response;
- a host or route refusal in either process;
- a GENESIS_B anchor failure;
- an attempt to run Stage B while a Stage A manifest is open.

---

## 3. TER-2 schema candidate (complete for the IOC milestone)

**Envelope:** `{seq, prev_hash, type, body, hash}`.
- `hash` = SHA-256 of the canonical serialization (R4.2i §10.5) of `{seq, prev_hash, type, body}`.
- `seq` starts at 0 (GENESIS_B) and increases by 1; `prev_hash` is null only at seq 0.
- **Value encoding:**
  - instants: decimal-string ns, W unless the field ends in `_mono`;
  - money and quantities: decimal strings;
  - hashes: 64 lowercase hex;
  - booleans: JSON booleans;
  - no floats anywhere.
- **The record set is closed.** Unknown types or fields → the record is invalid.

**Common body fields (every type except GENESIS_B):**
- `writer_role` ∈ {DECISION, APPROVAL_CLI, EXECUTOR, FOUNDER_CLI}
- `manifest_sha256`
- `session_id` (null outside a session)
- `instant`
- `pid`
- `instant_mono` (null for founder CLI records)

| Type | Writer | Body fields (beyond the common set) |
|---|---|---|
| GENESIS_B | DECISION (once) | experiment_id; stage_b_frozen_set_hashes; policy_sha256; stage_a_anchor {exit_record_path, exit_record_sha256, audit_report_sha256, hand_crosscheck_sha256, scope_commit, scope_sha256, auditor_sha256, manifest_sha256, stage_a_chain_head_at_run_close} |
| RUN_OPEN_B | DECISION | anchor_verification {each anchor item: PASS} |
| SESSION_OPEN | EXECUTOR | founder_attestation_paper_key (bool); account_artifact_sha256; positions_artifact_sha256; orders_artifact_sha256; observed {cash, buying_power, multiplier, shorting_enabled, btc_position_qty, open_order_count}; ledger_fold {cash, reserved_usd, held_btc}; match (bool) |
| SESSION_CLOSING | EXECUTOR or FOUNDER_CLI | reason ∈ {FOUNDER, HALT, SHUTDOWN}; halt_ref (seq or null) |
| SESSION_CLOSE | EXECUTOR | open_wal_count = 0; open_auth_count = 0; unreleased_reservations = 0; l2_refs; l3_refs |
| PROPOSAL | DECISION | slot_index; T_d; created; signal {D_prev, D_curr, signal}; bar_window_sha256; quote_sha256; quote {bid, ask, t}; proposal {instrument, side, q, L, tif, partial_fill_accepted, R, f_res, fee_estimate}; ledger_at_a {cash, reserved_usd, cash_available, held_btc, equity}; rule_results [{rule, result}] (all PASS); policy_sha256; config_sha256; approval_deadline; proposal_sha256 (of this body without the field) |
| APPROVAL | APPROVAL_CLI | proposal_seq; proposal_sha256 (full); confirm_prefix; bound {all R4.2i §9.1 fields, plus executor_id, account, venue, action_type NEW}; approved_at; approver_statement "founder (interactive console; not cryptographically authenticated)" |
| APPROVAL_REFUSED | APPROVAL_CLI | proposal_seq; reason ∈ {PREFIX_MISMATCH, LATE, SESSION_CLOSING, NO_SUCH_PROPOSAL, ALREADY_APPROVED} |
| AUTHORIZATION | DECISION | proposal_seq; approval_seq; auth_id; coid; issued; not_before; expires_at; checkpoint_b {quote_sha256, quote_age_ns, bars_refetch_sha256, bars_match (bool), rules [{rule, result}], clock {W, M}}; context {executor_id, account, venue, action_type}; reservation {R, f_res, reserved_usd_after} |
| AUTH_DEATH | DECISION or EXECUTOR | auth_seq; reason ∈ {EXPIRED, CHECK_B_FAILED, CHECK_C_FAILED, CLOCK_ADJUSTED, SESSION_CLOSING, RECOVERY_EXPIRED}; evidence_refs; release {R, reserved_usd_after} |
| CYCLE_B | DECISION | the slot's TER fields as in R4.2i §10.4, except the terminal set: terminal_state ∈ {HOLD, NO_ACTION, REJECTED, NO_DECISION(sub-reason), BOUNDARY_FAIL, EXPIRED_UNAPPROVED, AUTHORIZATION_DIED, AUTHORIZED}; refs to PROPOSAL, APPROVAL, AUTHORIZATION where they apply |
| CONSUME | EXECUTOR | auth_seq; checkpoint_c {quote_sha256, quote_age_ns, bars_refetch_sha256, bars_match, rules, clock {W, M}} |
| WAL | EXECUTOR | auth_seq; coid; request_body_sha256; request_body (canonical bytes as a string) |
| PRESEND | EXECUTOR | auth_seq; checkpoint_d {quote_sha256, quote_age_ns, rules [R4, R5], margin_ns = expires_at − δ_send − W(d), clock {W, M}}; config_sha256 |
| NOT_SENT | EXECUTOR | auth_seq; reason ∈ {LATE, CHECK_D_FAILED, CLOCK_ADJUSTED, SESSION_CLOSING, SEND_NOT_BEGUN, LOCAL_CERTAIN_RECOVERY}; release {R, reserved_usd_after} |
| SEND_RESULT | EXECUTOR | wal_seq; first_byte_mono; end_mono; outcome ∈ {RESPONSE, TIMEOUT, TRANSPORT_ERROR}; http_status (or null); response_artifact_sha256 (or null); l1 {result PASS / FAIL / NOT_APPLICABLE, field_diffs} |
| QUERY | EXECUTOR | wal_seq; coid; http_status; response_artifact_sha256; observed {status, filled_qty, filled_avg_price} or NOT_FOUND |
| AMBIGUOUS | EXECUTOR | wal_seq; coid; cause ∈ {TIMEOUT, TRANSPORT_ERROR, 5XX, MALFORMED, SEND_OVERRAN, CLOCK_ADJUSTED_AFTER_SEND, ORDER_UNRESOLVED}; last_query_seq |
| NOT_ACCEPTED | EXECUTOR | wal_seq; http_status; response_artifact_sha256; not_found_query_seq; release {R, reserved_usd_after} |
| ORDER_TERMINAL | EXECUTOR | wal_seq; coid; venue_status ∈ {filled, canceled, expired, rejected}; Q_f; P̄; gross G; fee {case F1 / F2, asset, amount, fee_usd_equiv, activity_artifact_sha256 or null}; ledger_after {cash, reserved_usd, held_btc}; release {R}; settle_artifact_shas {account, positions, activities}; milestone_fill (bool = Q_f > 0) |
| RECONCILE_L2 | EXECUTOR | at ∈ {TERMINAL, SESSION_OPEN}; ref_seq; broker {cash, btc_qty, open_orders}; sentinel {cash_exact, btc_exact, open_orders}; rounding_rule_matched (or null); result PASS / FAIL |
| RECONCILE_L3 | FOUNDER_CLI | wal_coids_checked; dashboard_order_count; match_key ∈ {COID, FIELDS}; unmatched_dashboard_orders; unmatched_wals; attestation_text; result PASS / FAIL |
| DISCREPANCY | EXECUTOR or FOUNDER_CLI | kind (from §2.13); refs; details |
| CYCLE_OVERRUN, CONCURRENT_INVOCATION, OFF_RUN, RUN_STOPPED_B, RUN_CLOSE_B | as R4.2i §10.1, re-declared for chain-b | as R4.2i, plus the common fields |

**Artifacts:** the R4.2i §10.2 pattern. Every HTTP exchange is stored as `artifacts/<sha256>`, holding the method, host, path, status, the Date and request-id headers, the body, t_send and t_recv (W and M), and **no request headers** (§2.11).

---

## 4. Minimum mandatory acceptance tests (Stage B gate; stub venue unless marked)

**Carried B-only tests from R4.2i §14, IOC-relevant subset:** U20, U21, U22, U23, U29, U30, U48, U50, U51, U63, U64, U65, U86, U90, U93.

**Dropped from the critical path with GTC:** R5-B1 UB15, UB16 (moved to Annex A).

| ID | Test | Expected | Closes |
|---|---|---|---|
| UB-C1 | the decision process attempts the trading host; the executor's data client attempts the trading host; the trading client attempts the data host | each refused before I/O | §2.1 |
| UB-C2 | inspect every data-client request at the stub | no `APCA-*` or `Authorization` header | revalidation |
| UB-C3 | force an exception during a trading request | no key material in records, artifacts or stdout | G-B1-08 |
| UB-C4 | keys present in the decision process's environment or configuration | BOUNDARY_FAIL (V12a) | §2.1 |
| UB-P1 | the pre-flight tool is asked for any non-GET method or any unlisted path | raises before I/O | G-B1-08 |
| UB-P2 | the stub returns 401 / 429 / 500 / a missing field / a 200 on P5 | each item FAILS; the tool completes the rest and exits non-zero | G-B1-08 |
| UB-A1 | an anchor file is missing or has the wrong hash; the RUN_CLOSE hash differs; the exit record lacks "M1 MET" | RUN_OPEN_B refused | G-B1-07 |
| UB-A2 | the anchor commit is not an ancestor of origin | the founder script refuses | G-B1-07 |
| UB-W1 | approval: wrong prefix; late by 1 ns; during CLOSING; second approval | APPROVAL_REFUSED with each reason | §2.12, §2.3 |
| UB-W2 | approval mismatch on each bound field and context field in turn | not issued (extends U63) | §2.12 |
| UB-T1 | wall clock steps by ±(ε_step + 1 ms) between checkpoints, and by exactly ε_step | AUTH_DEATH (CLOCK_ADJUSTED) / AUTH_DEATH / pass | §2.6 |
| UB-T2 | (d) at expires_at − δ_send exactly, and + 1 ns | send / NOT_SENT (LATE) | §2.6 |
| UB-T3 | the real first send (live paper, at S7) | first-byte and end monotonic times recorded; margin_ns > 0 | §2.6 (observational) |
| UB-T4 | the order is still open at T_d(i+1) | slot i+1 BLOCKED_OPEN_ORDER (= U51) | §2.6 |
| UB-S1 | crash injected after CONSUME, after the WAL, after PRESEND, after the first byte, after the response, before ORDER_TERMINAL | recovery: NOT_SENT (LOCAL_CERTAIN) / query only / query only / query only / query only / booking once; **the stub records exactly one POST per COID in every case** | G-B1-03, G-B1-05 |
| UB-S2 | the stub times out; 5xx; resets the connection mid-body; returns malformed 2xx | AMBIGUOUS; query by COID only; R16 blocks; **one POST seen** | G-B1-05 |
| UB-S3 | the stub resets the connection before any response | the client makes no second attempt (one connection, one request) | G-B1-05 |
| UB-S4 | the stub answers the POST with a 307 redirect | not followed; AMBIGUOUS | G-B1-05 |
| UB-S5 | 4xx with a body, then the COID query is not found / is found | NOT_ACCEPTED with full release / tracking plus DISCREPANCY | §2.7 |
| UB-S6 | the echoed order differs on one field | L-1 FAIL, halt | §2.8 |
| UB-S7 | two executor instances poll one authorization | exactly one CONSUME (= U65) | §2.1 |
| UB-L1 | a second ORDER_TERMINAL for one COID | refused | G-B1-06 |
| UB-L2 | IOC terminal with Q_f = 0 / partial / full | booked; release exact; milestone_fill false / true / true | G-B1-06, §2.5 |
| UB-L3 | fee cases F1 (BTC fee), F1 (USD fee), F2, F3 | booked / booked / FEE_NONE_OBSERVED / DISCREPANCY | G-B1-06 |
| UB-L4 | broker cash equals the exact value under floor / ceiling / half-even / none | PASS with the rule recorded ×3 / DISCREPANCY | G-B1-06 |
| UB-L5 | G + fee > R in a stub fill | DISCREPANCY | G-B1-06 |
| UB-L6 | the settle reads lag for 30 s, then reflect the order; they never reflect it within 60 s | PASS / NOT_SETTLED halt | §2.6 |
| UB-R1 | a torn final line | nothing acted on; session stays CLOSING | G-B1-03 |
| UB-R2 | recovery fold after each crash point of UB-S1 equals a clean-run fold | equal (no double release, no lost reservation) | G-B1-06 |
| UB-X1 | session close requested with an order in tracking | CLOSING; no new consume or send; tracking and L-2 complete; then SESSION_CLOSE | G-B1-02 |
| UB-X2 | session close with an AMBIGUOUS order | stays CLOSING; the next SESSION_OPEN is refused | G-B1-02 |
| UB-X3 | an authorization consumed, then CLOSING before (d) | NOT_SENT (SESSION_CLOSING); full release | G-B1-02 |
| UB-X4 | a Stage B task while a Stage A manifest is open | refused | §2.13 |
| UB-L3S | founder L-3: a dashboard order matching no WAL (simulated) | UNMEDIATED, halt (procedure test, executed by the founder on the stub record) | G-B1-05 |

**Every result records** the G-07 §9 fields: invariant, environment, credential arrangement, expected, observed, artifact and residual. The tests are builder-written. GPT checks their **scope** against this table, but they are not independent verification.

---

## 5. Dependency register (genuine blockers only)

| # | Blocker | Type | Gate | Can proceed in parallel? |
|---|---|---|---|---|
| 1 | M1 met on run-stage-a-1: auditor v2.3 run, seed reveal, hand cross-check | **[EXEC]** | after RUN_CLOSE and scope.json | — |
| 2 | Stage A exit record (M1 MET; OI-08 decided) | **[AUTH]** | after 1 | — |
| 3 | adoption of Decision Record v6 plus D-10 to D-13 (§6) | **[AUTH]** (decisions) | any time | yes, now |
| 4 | FD-8 key custody (proposal §2.11) | **[AUTH]** | before 5 | yes |
| 5 | D-9 pre-flight authorization, and the pre-flight tool (GET-only) built and reviewed. **Building this tool is itself under D-9, not FD-9** | **[AUTH]** then **[EXEC]** | after 2 (the founder chose to hold D-9 until after M1) | the spec of the tool, yes |
| 6 | pre-flight executed: P1–P5 pass; increments observed; RTT p_max < 5 s | **[VENUE]** | after 5 | — |
| 7 | P-0.3 policy issued (TIF ioc; observed increments) | **[AUTH]** | after 6 | — |
| 8 | GPT and Gemini B closure round on R5-B2 (this diff only) | **[DESIGN]** review | any time after 3 | yes, now |
| 9 | Stage B freeze record and FD-9 | **[AUTH]** | after 2, 7 and 8 | — |
| 10 | build plus the §4 tests executed with retained evidence | **[EXEC]** | after 9 | — |
| 11 | Stage B auditor (GPT, blind), its hash committed; Gemini B challenge | **[EXEC]** | after 9, parallel with 10 | yes |
| 12 | first-order authorization (P23) | **[AUTH]** | after 10 and 11 | — |
| 13 | an attended session with a BUY that passes policy | **[VENUE]** (market) | after 12 | UNBOUNDED wait (U-O3) |
| 14 | L-2 rounding rule and fee case observed and pinned | **[VENUE]** | at the first terminal | — |
| 15 | L-3 COID visibility on the dashboard | **[VENUE]** | at the first terminal | fallback match rule ready |
| 16 | L-4 reconstruction PASS | **[EXEC]** | after the milestone attempt | — |

**Not blockers:**
- GTC (Annex A);
- the duplicate-COID test;
- the EXIT path;
- R-d email;
- signatures;
- host isolation;
- a remote approval channel;
- G7-I5 and G7-I8 compliance (disclosed by FD-G13).

---

## 6. New decisions raised by R5-B2 (to be added to the decision record)

| ID | Decision | Type | Recommendation |
|---|---|---|---|
| D-10 | the milestone TIF is IOC; GTC deferred (Annex A) | [DESIGN] | adopt; P-0.3 is issued only after the pre-flight |
| D-11 | the executor holds a keyless data client for checkpoints (c) and (d) | [DESIGN] | adopt (the only option compliant with frozen §7.3 and §4.9 and G-07 §1) |
| D-12 | ε_step = 250 ms; δ_send = 10 s fixed at the freeze, subject to pre-flight RTT p_max < 5 s | [DESIGN] | adopt |
| D-13 | L-2 broker-rounding rule: match under {floor, ceiling, half-even}, then pin the observed rule | [DESIGN] + [VENUE] | adopt |

---

## Annex A. GTC branch (deferred; not on the milestone's critical path)

Kept only so that a later switch away from IOC does not reopen G-B1-01.

- **Corrected windows:**
  - NEW order: expires_at = issued + 60 s, as before.
  - CANCEL_AUTHORIZATION: not_before = T_d + 150 s; expires_at = T_d + 180 s; PRESEND requires W ≤ T_d + 170 s.
  - Positive consumption window: **20 s**.
- **Additional requirements if it is ever activated:**
  - a CANCEL in its own WAL, PRESEND and SEND path, with AMBIGUOUS handling;
  - an ambiguous cancel keeps the order counted as open (R16);
  - tests UB15 and UB16 from R5-B1, plus a cancel-AMBIGUOUS test;
  - a new Stage B freeze.

*End of R5-B2.*
