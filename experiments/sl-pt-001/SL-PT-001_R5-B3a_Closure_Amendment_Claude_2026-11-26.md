# SL-PT-001 R5-B3a: closure amendment to R5-B3

**Responds to:** Strike 7.5 (G-B3-01 to G-B3-06) | **Base:** R5-B3 (and R5-B2 where cited) | **Status:** DRAFT; no freeze, nothing authorized. No Stage A run evidence; no harness internals.
**Form:** exact replacement text only. Unlisted text stands.

## 1. Finding-closure matrix

| Finding | Defect | Correction | Replaces |
|---|---|---|---|
| G-B3-01 | AMBIGUOUS_RESOLUTION (NOT_SUBMITTED) let a founder declaration end an ambiguous order and release its reservation | The NOT_SUBMITTED outcome is removed. An ambiguous order ends **only on venue evidence**. Without it, the reservation, the R16 block and the CLOSING state persist. **Disclosed consequence:** Stage B cannot progress until that evidence exists. Any other path would mean changing frozen R16 (§7.3, a Stage A section) and is out of scope | R5-B3 §D last row; §G.2; §G.5 AMBIGUOUS_RESOLUTION |
| G-B3-02 | (a) the expiry derivation ignored the allowed clock adjustment: W(t_resp) can exceed W(t_d) + δ_send by up to ε_step; (b) UB-T2′ treated exactly 10 s as a failure while the rule is inclusive; (c) UB-T1′ assumed 5 checkpoints after CONSUME, but there are 3 | Release margin includes ε_step; inclusive boundaries stated once and tests aligned; UB-T1′ rewritten | R5-B3 §C table; UB-T1′; UB-T2′ |
| G-B3-03 | PRESEND was called "commencement of transmission" | PRESEND = **logical execution release**. Physical transmission begins after it (at or after t_tx0). Close semantics disclosed | R5-B3 §B.1 to §B.3 |
| G-B3-04 | G_fills was "authoritative when present" without completeness; there was no dedup rule for fill records; ROUNDING_RESIDUAL as a separate record could be applied twice across a crash | Completeness: Σq_i = Q_f exactly. Dedup by activity id. Paginated retrieval recorded. **The residual becomes a field of RECONCILE_L2**, so it is one record with at most one per terminal: exactly-once by construction | R5-B3 §A.2, §A.4; §G.5 ROUNDING_RESIDUAL |
| G-B3-05 | The attempt count and expiry were checked at issuance only; they were not robust across sessions, manifests and restarts | Count over **all of chain-b by campaign_ref**. Campaign validity checked at issuance, CONSUME and PRESEND | R5-B3 §H.2 |
| G-B3-06 | (a) L-3 counted only orders "observed by SEND or QUERY", so a WAL'd order the executor never observed broke the count; (b) the pre-flight COID shared the live `slpt001-` prefix; (c) P4a/P4b: "any unexpected status FAILS" conflicted with "pass if one returns 200"; (d) the custody order omitted the audit commit; (e) SESSION_CLOSE `unreleased_reservations = 0` and the writer table still referenced removed types | Each corrected below | R5-B3 §F.3; §G.4; §G.7; R5-B2 §2.10 P5; §3 TER-2 SESSION_CLOSE |

## 2. Replacement text

**R5-B3 §D, last table row → replace with:**
> | any other status (including 404, 408, 409, 429, 5xx); timeout; transport error; malformed or unparseable body | query by COID (2 s, then every 30 s, indefinitely while the executor runs) | found → tracking + L-1 (venue evidence). Not found → **AMBIGUOUS, permanently, until venue evidence exists**. Venue evidence = an order object for the COID from a query, or a dashboard order conclusively identified with the WAL (§F). **No founder record, elapsed time or count of not-found queries ends an AMBIGUOUS order or releases its reservation.** While it lasts, R16 blocks every proposal (R4.2i §7.3, frozen), the reservation stays in the ledger, and the session stays CLOSING. *Disclosed:* a permanently ambiguous order stops Stage B. Removing that stop would require changing frozen R16, which is outside this experiment. |

**R5-B3 §B.1–§B.3 → replace with:**
> 1. **PRESEND is the logical execution release.** It is the last local decision that the order may go. Physical transmission begins at or after t_tx0 (§C) and is not otherwise observed.
> 2. SESSION_CLOSING and PRESEND are both appended under the append lock, and **chain order decides eligibility for release:** a CLOSING earlier in the chain means the (d) check, read in the same lock hold, writes NOT_SENT (SESSION_CLOSING); a CLOSING later in the chain does not affect an already-released order.
> 3. **Disclosed close semantics:** SESSION_CLOSING prevents new releases. It does not recall a released order. After it is appended, at most one released order can still be physically transmitted, within δ_start and δ_send of its (d) sample, and it is tracked and reconciled like any other. "Session closed" never means "nothing was sent after the close request".

**R5-B3 §C → replace the "release margin" and "expiry consistency" rows, and add the boundary rule:**
> | release margin | W(t_d) ≤ expires_at − δ_send − ε_step | NOT_SENT (LATE) |
> | expiry consistency (DERIVED) | the release margin, the total budget and the cumulative bound \|ΔW − ΔM\| ≤ ε_step give W(t_resp) ≤ W(t_d) + δ_send + ε_step ≤ expires_at | — |
>
> **Boundaries:** every "≤" in this table is inclusive at equality, and every limit is violated at limit + 1 ns. The worst-case consumption window becomes ≥ 49.75 s (issued = T_d + 120 s).

**R5-B3 §A.2 → replace with:**
> **G_fills** is authoritative only if **all** of these hold:
> - every fill record (the venue's fill-type account activities) is retrieved by following pagination to its end, with each page recorded as an artifact;
> - records are deduplicated by activity id: identical duplicates are collapsed, and the same id with differing content → DISCREPANCY (FILL_CONFLICT);
> - every record references the order's broker order id;
> - **Σ q_i = Q_f exactly** (Q_f from the terminal order object) after the settle window.
>
> If no fill records exist for the order, the basis is **G_avg** (flagged AVG_PRICE). If records exist but are incomplete or inconsistent (Σ q_i ≠ Q_f), the result is **DISCREPANCY (FILLS_INCOMPLETE)**; there is no fallback to G_avg. The field names and the availability of fill records are **[VENUE] V-3**.

**R5-B3 §A.4 → replace with:**
> When L-2 at a terminal passes with residual r ≠ 0, the **RECONCILE_L2 record itself** carries `residual_applied = r`. The ledger fold applies it.
> - At most one RECONCILE_L2 with at = TERMINAL may exist per ORDER_TERMINAL; a second is refused, and recovery skips it if one exists. Exactly-once application follows by construction.
> - At SESSION_OPEN, r must be 0. Otherwise DISCREPANCY (no residual is applied without a new trade).

**R5-B3 §H.2 → replace with:**
> **Counting and validity, across all sessions, manifests and restarts:**
> - attempts = the number of AUTHORIZATION records in **all of chain-b** with this `campaign_ref`. The count is recomputed from the chain on every check, never cached;
> - **the campaign is valid** iff its record hash equals the pin in the RUN_OPEN_B of the current manifest, now < its expiry, and no ORDER_TERMINAL with Q_f > 0 exists under it.
>
> **Checked at:**
> - (i) issuance: refused if attempts + 1 > K or the campaign is invalid;
> - (ii) CONSUME: AUTH_DEATH (CAMPAIGN_INVALID) if invalid;
> - (iii) PRESEND: NOT_SENT (CAMPAIGN_INVALID) if invalid.
>
> **Further rules:**
> - A new manifest may pin the same campaign. Its attempts keep counting.
> - An authorization that dies before release still counts as an attempt. That is conservative: an executor outage can use up K, and it is disclosed.

**R5-B3 §F.3 → replace with:**
> L-3 PASS requires all of:
> - every dashboard order in the session window is conclusively identified (COID or broker order id) with a **WAL record** of chain-b, whether or not the executor ever observed it;
> - the dashboard order count in the window equals the number of WAL COIDs matched;
> - every WAL that has an ORDER_TERMINAL is present on the dashboard.
>
> A WAL without a dashboard order and without NOT_SENT or NOT_ACCEPTED stays AMBIGUOUS (no conclusion).

**R5-B2 §2.10 P5 and R5-B3 §G.4 → replace with:**
> P5 COID = `slptpf-<UTC stamp>`, a namespace disjoint from order COIDs (`slpt001-<hex>`). **P4a and P4b each expect status ∈ {200, 404}.** P4 passes iff at least one returns 200 with the required fields. Any other status on either → FAIL.

**R5-B3 §G.7, custody order → replace "commitment < scope < reveal" with:**
> seed commitment < scope.json < seed reveal < audit report. Each is a pushed commit, checked by the founder script. The audit report's recorded scope and seed hash must equal the committed ones.

**R5-B2 §3 TER-2 and R5-B3 §G.2/§G.5 → replace with:**
> - **Removed types:** ROUNDING_RESIDUAL; AMBIGUOUS_RESOLUTION.
> - **RECONCILE_L2** adds `residual_applied`.
> - **SESSION_CLOSE** requires `open_wal_count = 0, ambiguous_count = 0, unreleased_reservations = 0`. A session with an AMBIGUOUS order cannot close (§D).
> - **NOT_SENT reasons** add CAMPAIGN_INVALID. **AUTH_DEATH reasons** add CAMPAIGN_INVALID.
> - **PRESEND** adds `campaign_check {attempts, K, expiry, valid}`.
> - **Founder CLI writes:** RECONCILE_L3, SESSION_CLOSING, DISCREPANCY, RUN_STOPPED_B.

## 3. Amended acceptance-test rows

| ID | Status | Test | Expected |
|---|---|---|---|
| UB-T1′ | replaces | cumulative drift from (c): +100 ms at (d), +100 at t_tx0, +100 at t_resp (300 cumulative); +250 ms exactly at (d); +251 ms at (d) | AMBIGUOUS (CLOCK_ADJUSTED_AFTER_RELEASE) at t_resp / release proceeds / NOT_SENT (CLOCK_ADJUSTED) |
| UB-T2′ | replaces | W(t_d) = expires_at − δ_send − ε_step / + 1 ns; t_tx0 − t_d = 2 s / 2 s + 1 ns; t_resp − t_d = 10 s / 10 s + 1 ns | release / NOT_SENT (LATE); send / NOT_SENT (SEND_NOT_BEGUN); terminal path / AMBIGUOUS (SEND_OVERRAN) |
| UB-B1 | new | AMBIGUOUS with 1,000 not-found queries; then a founder attempts to close the session or start a new one | reservation retained; R16 blocks; SESSION_CLOSE refused; SESSION_OPEN refused |
| UB-B2 | new | AMBIGUOUS, then a later query finds the order (terminal, filled) | L-1 on that object; ORDER_TERMINAL; reservation released by booking; session may close after L-2 and L-3 |
| UB-L7′ | replaces UB-L7 | L-2 PASS with r ≠ 0; crash after RECONCILE_L2; recovery | one RECONCILE_L2 with residual_applied; the fold applies r exactly once; a second RECONCILE_L2 is refused |
| UB-L8 | new | fill records: two pages; a duplicate id with identical content; a duplicate id with different content; Σq_i < Q_f; no records | G_fills complete / collapsed / FILL_CONFLICT / FILLS_INCOMPLETE / basis AVG_PRICE |
| UB-K3 | new | campaign K = 2: attempt 1 in session 1, manifest 1; executor and decision restart; attempt 2 in session 2, manifest 2 (same campaign pin); attempt 3 | issued / issued / refused at issuance |
| UB-K4 | new | campaign expiry falls between issuance and CONSUME; between CONSUME and PRESEND | AUTH_DEATH (CAMPAIGN_INVALID) / NOT_SENT (CAMPAIGN_INVALID) |
| UB-X5′ | replaces UB-X5 | CLOSING appended before / after PRESEND | NOT_SENT (SESSION_CLOSING) / released order sent, tracked, reconciled; the close record notes one post-close transmission |
| UB-L3S″ | replaces UB-L3S′ | a dashboard order matching a WAL COID that the executor never observed (crash after the WAL) | conclusive identity; counted; not UNMEDIATED |
| UB-P2′ | replaces UB-P2 | P4a 404 + P4b 200; both 404; P4a 500 | PASS / FAIL / FAIL |
| UB-A1″ | extends UB-A1′ | the audit report commit precedes the seed reveal | founder script refuses |

## 4. Remaining gates

**Authorization [AUTH]:**
- v6 adoption;
- Stage A exit record (M1 MET; OI-08);
- FD-8;
- D-9;
- P-0.3;
- the Stage B freeze and FD-9;
- P23 (K and expiry).

**Executed verification [EXEC]:**
- M1 audit on the Stage A audit scope;
- the pre-flight run;
- the Stage B test suite (R5-B2 §4 as amended by R5-B3 and R5-B3a);
- the blind Stage B auditor, its hash committed;
- L-4 after the attempt.

**Venue [VENUE]:**
- V-1 dashboard identifiers;
- V-2 crypto IOC accepted;
- V-3 fill records and completeness;
- V-4 fee presence and fields;
- V-5 rounding residuals;
- account and asset field names (pre-flight);
- market: a policy-passing BUY in an attended session (UNBOUNDED).

**Design:** none open. GPT's closure check of R5-B3a against G-B3-01 to G-B3-06 is the last design step. After it, refinement is suspended unless a concrete blocker appears.

*End of R5-B3a.*
