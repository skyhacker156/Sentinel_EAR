SPECIFICATION ONLY / NOT IMPLEMENTED / NOT VERIFIED
Exposure Accounting Reference Model v0.1, Revision 3 (frozen). Part 2 of 3. Full-file SHA-256: 9a2c3be747fa9acbe4513e77f4122712f1970aa17109beb52acffbe051702b0a
---PART-BODY-START---
### 2.6 Event and transition semantics [R]

Generic handling of malformed, duplicate, stale and conflicting events (item 8 of the dispatch). Exceptions are in the table.
- **Duplicate** (same event_id, identical canonical payload): idempotent no-op; no revision change; duplicate count recorded.
- **Same event_id, different payload:** CONFLICT evidence failure. Affected order treated as UNKNOWN (R kept at qty - net_cum). Blocks increases; reductions UNRESOLVED until an authoritative broker response resolves it.
- **Out of order (broker_seq beyond next expected):** not applied; buffered as evidence; position status GAP (UNBOUNDED).
- **Stale (broker_seq below the applied watermark, event_id unseen):** applied only if consistent with the order's recorded cum_qty and state; otherwise CONFLICT.
- **Malformed (schema, type, range, instrument):** not applied; raw evidence retained; treated as an orphan of unknown quantity (UNBOUNDED) until resolved by a broker query.

Columns: dF = changes F_d; dB, dS = changes B, S; band = changes uncertainty items; blk = blocks increases; red = can permit a reduction; ev = evidence retained (all events retain raw_hash, event_id, broker_seq, received_at; table lists only the extra).

| # | Event | dF | dB | dS | band | blk | red | Extra evidence / exceptions |
|---|---|---|---|---|---|---|---|---|
| E01 | Proposal created | no | no | no | no | no | n/a | Proposal record. Not a reservation. |
| E02 | Authorization committed (CAS) | no | +qty if buy | +qty if sell | no | no | yes (by A) | Decision hash, revision. Order becomes AUTHORIZED; counted once from this moment. |
| E03 | Order submitted (adapter reports) | no | no | no | no | no | yes | Requires live reservation token (A-5). Submit without a live reservation: order later appears as unknown order (E20). |
| E04 | Acknowledged | no | no | no | no | no | yes | Duplicate ack is a no-op; ack contradicting state is CONFLICT. |
| E05 | Partial fill (NEW exec) | yes (signed q) | -q if buy | -q if sell | no | no | yes | net_cum updated. q > R(o) is CONFLICT (overfill). |
| E06 | Full fill | yes | R to 0 | R to 0 | no | no | yes | Order FILLED (terminal). net_cum must equal qty else CONFLICT. |
| E07 | Cancel requested | no | no | no | no | no | yes | State CANCEL_PENDING; R unchanged (may still fill). Recorded as an event only: the model does not decide or imply who may issue a cancellation (D10, G-07). |
| E08 | Cancel confirmed | no | -R if buy | -R if sell | no | no | yes | Terminal. R is released only if the required broker evidence is present and cum_qty equals net_cum, all executions up to the event being applied; otherwise CONFLICT and the order stays working with R kept. Arithmetic effect only; no judgment that the cancellation is risk-reducing. |
| E09 | Rejected | no | -R | -R | no | no | yes | Terminal. cum_qty must be 0 for a never-filled order, else CONFLICT. |
| E10a | Broker expiry | no | -R | -R | no | no | yes | Terminal, cum_qty required as for E08. |
| E10b | Reservation expiry (internal) | no | -qty | -qty | no | no | yes | Only for AUTHORIZED never submitted. A later broker event for that order_id is T22 (order UNKNOWN, R re-reserved). |
| E11 | Order status UNKNOWN | no | R kept | R kept | no | **yes** | by A if BOUNDED | Order counted as working until broker-resolved (T20). |
| E12 | Duplicate execution report | no | no | no | no | no | n/a | No-op. Same exec_id different payload: CONFLICT. |
| E13 | Corrected execution | yes (new - old) | adjusts via net_cum | adjusts | no | no | by A | If new net_cum is outside [0, qty] or exceeds broker cum: CONFLICT. Applies to terminal orders too (T21). A CORRECT or BUST naming an unknown original is held pending: effect unknown, band UNBOUNDED until the original arrives or the broker resolves it (V31). |
| E14 | Busted / reversed execution | yes (-old) | none (terminal R stays 0; working order R rises) | same | no | no | by A | May produce OVER_RESERVED. Does not resurrect a terminal order. |
| E15 | Execution out of order | no (not applied) | no | no | GAP | **yes** | no (UNRESOLVED) | Buffered until the gap fills. |
| E16 | Execution after cancel request | yes | -q (buy) | -q (sell) | no | no | yes | Normal fill on CANCEL_PENDING; R after the fill continues until confirmation. |
| E17 | New execution after terminal status | not applied | no | no | pending item by side (Q3) | **yes** | no (UNRESOLVED) | T22: order UNKNOWN with R = qty - net_cum (re-reserved); structural evidence failure (conflicts with the terminal cum_qty). The execution moves to F_d only on authoritative reconciliation (V32). Modified from the addendum's IB3 (F-8). |
| E18 | Duplicate ack / cancel confirm | no | no | no | no | no | n/a | No-op if identical and state-consistent; otherwise CONFLICT. |
| E19 | Conflicting broker events | no | R kept | R kept | evidence failure | **yes** | no (UNRESOLVED) | Order frozen as UNKNOWN. |
| E20 | Unknown order identity | no | no | no | orphan (Q3 by side) | **yes** | by A if qty and side known | Orphan keyed by event_id. |
| E21 | Unknown execution side or quantity | no | no | no | side unknown: Q3_unk; qty unknown: UNBOUNDED | **yes** | side unknown: by A; qty unknown: no | |
| E22 | Execution not associable | no | no | no | as E20 | **yes** | as E20 | |
| E23 | Broker snapshot received | no | no | no | recomputes d, status | by status | by status | snapshot_id, W, F_b. Cases in 2.6.2. Older W than the last accepted: REPLAY, ignored with record. |
| E24 | Master semantic change (class B) | no | released if AUTHORIZED unsubmitted | released if AUTHORIZED unsubmitted | status UNKNOWN until reconciled | **yes** | **no** (R_MASTER_CHANGE) | Master version and hash; effects in 2.12, V35. |

**Cancellation semantics (D10 amended) [R].** The model represents a cancellation request (E07) and a broker-confirmed cancellation (E08, and unsolicited broker cancellations) as events. It does not decide, imply or enforce who has authority to issue a cancellation command; that question is outside v0.1 and reserved for G-07. A confirmation removes the remaining working-order reservation only when the required broker evidence and cumulative-quantity checks are satisfied. The model does not classify cancellation of a working sell as inherently risk-reducing: its only effect in the model is the arithmetic change to S (or B). OVER_RESERVED clears when A_raw >= 0 by whatever evidenced events occur; the model does not say who must act.

### 2.6.1 Order lifecycle with accounting effects [R]

States: PROPOSED, AUTHORIZED, SUBMITTED, ACKNOWLEDGED, PARTIALLY_FILLED, FILLED, CANCEL_PENDING, CANCELED, REJECTED, EXPIRED, UNKNOWN, DENIED. Terminal: FILLED, CANCELED, REJECTED, EXPIRED, DENIED. The table is exhaustive: a transition not listed is invalid. Evidence codes: EV-eval (evaluation record), EV-msg (broker message id and raw hash), EV-req (our outgoing request hash), EV-clk (independent clock reading), EV-rec (reconciliation result). Each transition is one revision step. R is the remaining reserved quantity of 2.2.

| ID | From to | Trigger and evidence | Accounting effect (F_d; B or S; band) | If invalid |
|---|---|---|---|---|
| T01 | none to PROPOSED | Strategy proposal (intent only); proposal hash | none; not in the ledger | IB1 |
| T02 | PROPOSED to AUTHORIZED | Authority ALLOW and successful commit (2.9); EV-eval | **R reserved**: B or S rises by qty; revision + 1 | stays PROPOSED, then T03 |
| T03 | PROPOSED to DENIED | Authority DENY or UNRESOLVED; EV-eval with codes | none | n/a |
| T04 | AUTHORIZED to SUBMITTED | Our submit with a live reservation token; EV-req, EV-clk | none (same order id, counted once) | IB2 |
| T05 | AUTHORIZED to EXPIRED | TTL (EV-clk), or master class-B change (2.12) | R released; revision + 1 | n/a |
| T06 | SUBMITTED to ACKNOWLEDGED | Broker ack; EV-msg | none | IB1 |
| T07 | SUBMITTED to REJECTED | Broker reject; net cum = 0 | R released | IB4 |
| T08 | SUBMITTED to PARTIALLY_FILLED or FILLED | Fill before ack | F_d +/- q; R -q (I1) | IB3/IB4 |
| T09 | ACKNOWLEDGED to PARTIALLY_FILLED | Execution | F_d +/- q; R -q | IB3/IB4 |
| T10 | ACKNOWLEDGED or PARTIALLY_FILLED to FILLED | Execution completes the order | F_d +/- q; R = 0 | IB3/IB4 |
| T11 | PARTIALLY_FILLED to PARTIALLY_FILLED | Further partial execution | F_d +/- q; R -q | IB3/IB4 |
| T12 | SUBMITTED, ACKNOWLEDGED or PARTIALLY_FILLED to CANCEL_PENDING | Cancel request recorded as an event (D10: the model does not decide who may issue it); EV-req | none; R kept in full | IB2 |
| T13 | CANCEL_PENDING to CANCEL_PENDING | Execution before confirmation | F_d +/- q; R -q | IB3/IB4 |
| T14 | CANCEL_PENDING to FILLED | Execution completes the order | F_d +/- q; R = 0 | IB3/IB4 |
| T15 | CANCEL_PENDING to CANCELED | Broker confirmation; **terminal rule** | R released | IB4 |
| T16 | CANCEL_PENDING to ACKNOWLEDGED or PARTIALLY_FILLED | Broker rejects the cancel | none | IB1 |
| T17 | working to EXPIRED | Broker time-in-force expiry; terminal rule | R released | IB4 |
| T18 | working to CANCELED (unsolicited: halt, broker limit) | Broker; terminal rule; alarm | R released | IB4 |
| T19 | working to UNKNOWN | No confirmation within the limit (value OPEN, D08), disconnect, contradictory reports | none; R kept; **blocks increases** | n/a |
| T20 | UNKNOWN to resolved state | Authoritative broker order-status response only; executions reconciled | R per the resolved state | stays UNKNOWN |
| T21 | terminal to the same state, attributes updated | BUST or CORRECT referencing a known execution | F_d and net_cum adjust; **R stays 0**; lifecycle state not rewritten; may raise OVER_RESERVED | IB4 |
| T22 | CANCELED, REJECTED or EXPIRED to UNKNOWN | An event arrives for a dead order | order UNKNOWN with **R = qty - net_cum (re-reserved)**. If the event is an execution: it is held as a pending item (by side) and a structural evidence failure is raised (modified from the addendum's IB3, F-8). If it is any other report: UNKNOWN only, no failure. | IB3 |

Invalid-transition classes (from the addendum, reconciled): **IB1** reject the event, state unchanged, log (malformed or unauthorized originators land here, E8). **IB2** block our own action, state unchanged, alarm. **IB3** event contradicts a terminal state: order UNKNOWN, any execution held as a pending item (not applied to F_d until reconciled). **IB4** data conflict: order UNKNOWN and a *structural* evidence failure (INCONSISTENT); the addendum set the position status to MISMATCH here, which is different from a snapshot mismatch and is not used (2.6.2).
No transition leaves a terminal state except T21 (attributes only) and T22 (anomaly).

**Terminal-transition rule [R].** A transition into a terminal state (T05 excepted, T07, T14, T15, T17, T18) requires that every execution up to the event has been applied and that the broker-reported cumulative quantity equals **net_cum_at(order, the event's broker_seq)**, i.e. the net quantity as of that event, not the latest net_cum. If an execution below that sequence is missing, the check fails closed (IB4). A later BUST or CORRECT is a separate event (T21): it changes net_cum and F_d, and does not retroactively falsify the earlier terminal report. This is the same principle as comparing a snapshot at its own watermark (RQ8).

### 2.6.2 Position status and snapshot rules [R]

A snapshot is compared with F_d(W) at the snapshot's own watermark, never with the latest derived position.

| Status | Definition | Bounded? | Blocks increases | Reductions |
|---|---|---|---|---|
| RECONCILED | contiguous through W; F_d(W) = F_b | yes | no | by A |
| AWAITING | executions applied after the latest snapshot, no gap, F_d(W) = F_b | yes | no | by A |
| MISMATCH | contiguous through W; F_d(W) != F_b under at least one inclusion choice of 2.2; d_plus and d_minus recorded | yes, by d | **yes** | by A (**D19**, conditional; preconditions in I2) |
| AWAITING-BEHIND | snapshot watermark above the highest applied sequence | **no** (D18) | yes | UNRESOLVED |
| AWAITING-UNVERIFIED | no watermark and the ledger is not quiescent | **no** | yes | UNRESOLVED |
| GAP | a sequence number missing at or below W | **no** | yes | UNRESOLVED |
| UNKNOWN | no snapshot, stale beyond the limit (D07), or conflicting snapshots | **no** | yes | UNRESOLVED |

AWAITING-BEHIND becomes GAP when the wait limit passes (value OPEN, D08). Quiescent means no working, authorized or unknown orders and no pending events.

| Snapshot case | Outcome |
|---|---|
| Valid watermark | Compare F_d(W) with F_b: RECONCILED, or MISMATCH with d recorded (case 1) |
| Gap at or below W | GAP; no comparison is made (it would produce a false MISMATCH) |
| Ahead of the highest applied sequence | AWAITING-BEHIND (F-4) |
| Stale or replayed (W below the latest accepted watermark) | Rejected; Freshness REPLAY; prior state kept |
| Equal watermark, different content | Conflict: Consistency INCONSISTENT (structural); both snapshots retained; status UNKNOWN until the broker resolves it |
| No watermark | Compared only if the ledger is quiescent; otherwise AWAITING-UNVERIFIED. No tolerance is invented. |
| Instrument id differs from the canonical id | Rejected (IB1) and logged; prior state kept |
| Snapshot quantity not a signed integer, or negative in the long-only envelope | Structural Consistency failure: UNRESOLVED (V54) |
| Discrepancy supplied as magnitude only | d_plus = d_minus = magnitude (2.2, V53) |
| Applied execution without broker_seq | d over all inclusion choices (2.2, V51) |
Time-only `as_of` is not used for comparison. Freshness and wait limits are parameters in the register (D07, D08), not values here.

### 2.6.3 Event ordering, idempotency and deterministic replay [R]
- **Canonical order is the log position.** Every accepted event is appended to the hash-chained log; the ledger is a pure fold over the log in that order (D20, F-7). broker_seq is used for gap detection and for watermark and as-of comparison, never to reorder the log.
- **Identity and economic uniqueness (requirement B).** **Idempotency by event ID does not establish economic-execution uniqueness.** The same real-world execution delivered under a different event id or exec_id is, to the model, a second execution; the model cannot detect it (V56). It is documented as an uncovered environmental failure that may create false permission before reconciliation: a duplicated buy overstates F_d (false permission for reductions), a duplicated sell understates it (false permission for increases). A later snapshot shows it as a discrepancy. event_id is broker-unique; if the broker supplies none, the hash of the canonical content. Identical event_id and identical content: apply once, count the duplicate (counters are outside the item hash). Same event_id, different content: structural conflict.
- **Sequence inconsistencies.** A broker_seq below the applied watermark with an unseen event_id is applied only if consistent with the order's recorded state, else a conflict. The same broker_seq with different event_id or content is a conflict.
- **Absent sequence numbers.** Events without broker_seq are ordered by log position, carry unknown timing (both T3 and T4 enumerated), and cannot establish a watermark.
- **Determinism.** Canonical serialization: sorted keys, integers only, no floats, UTF-8; the as_of time is an explicit input; no clock, randomness or unordered iteration in pure functions. Replaying the same log twice must give byte-identical ledgers and decisions.
- **Out of order.** Position is a sum, so arrival order does not change F_d for non-conflicting sets; an event whose prerequisite has not arrived is held as pending and applied in dependency order. This is **not** claimed for conflicting or state-dependent events.
- **Reconnection (C-05).** A missing sequence is GAP until the missing event arrives, or the broker gives an explicit authoritative resolution of that specific sequence. **A later snapshot never clears a GAP:** it does not supply the order-level accounting (net_cum, R) of the missing execution, and no comparison is made under GAP (V48). Resent events fall under idempotency.

**Limits of replay order (D20, C-13) [R].** The log-position order establishes a deterministic *processing* order only. It does not establish that the resulting state equals the state under any other arrival order; it does not establish that two logs of the same real-world history agree; non-commuting events (for example two corrections of one execution) give outcomes that depend on log position (V49); and it says nothing about economic uniqueness or completeness of delivery (A-11, A-12). Order-invariance is claimed only for sets of non-conflicting executions.

### 2.7 UNKNOWN semantics [R]

| Case | Effect on F_min / F_max | B | S | Blocks | Reduction allowed? |
|---|---|---|---|---|---|
| Unknown increase order | none | + full R | none | all increases | yes, by A, if BOUNDED |
| Unknown reduction order | F_min not lowered (not treated as having reduced) | none | + full R | all increases | yes, by A, if BOUNDED |
| Unknown working order of unknown side, known remaining quantity R (requirement F) | none | + full R | + full R | all increases | yes, by A, if BOUNDED |
| Unknown execution, known side and qty | buy: F_max + q; sell: F_min - q | none | none | all increases | yes, by A, if BOUNDED |
| Unknown execution side, known qty | F_max + q and F_min - q | none | none | all increases | yes, by A |
| Unknown quantity | UNBOUNDED | n/a | n/a | all increases | **no** (UNRESOLVED) |
| Unknown instrument | quarantined; treated as orphan of unknown side and quantity until resolved; UNBOUNDED | n/a | n/a | all activity | **no** |
| Unknown broker position (no or stale snapshot) | status UNKNOWN: UNBOUNDED | n/a | n/a | all increases | **no** (NO_INDEPENDENT_EVIDENCE is not tolerated for reductions, D06 approved) |
| Unknown sequence or watermark | status GAP: UNBOUNDED | n/a | n/a | all increases | **no** |

- Orphan and ambiguous items follow the treatments T1, T1u, T2, T2-U of section 2.3.
- An unknown increase is never treated as unable to fill. An unknown reduction is never treated as already executed. An unknown execution is neither discarded nor applied twice (event_id idempotency).
- Resume: each unknown item is resolved only by an authoritative broker response; then position status RECONCILED or AWAITING at a watermark not earlier than the resolution; then the evaluation shows no unknown item and no evidence failure. Timeouts, internal belief and the strategy never clear an item.
- A reduction during uncertainty is permitted only when the band is BOUNDED, with quantity limited by A. This is not a safe-exit guarantee; whether any exit is possible when the band is UNBOUNDED is the separate protective-intervention problem (G-06) and is out of scope.

**What blocks what [R].** Every unresolved item blocks increases. Only some also block reductions. "Structural evidence failure" means a conflict that cannot be quantified (2.8).

| Condition | Blocks increases | Blocks reductions |
|---|---|---|
| UNKNOWN order | yes | no (limited by A) |
| Orphan or pending item with known quantity (T1, T1u, T2) | yes | no (limited by A) |
| T2-U: unknown quantity, unknown instrument, correction naming an unknown original | yes | **yes** (UNBOUNDED; UNRESOLVED) |
| Position MISMATCH with known d | yes | no (limited by A, D19) |
| AWAITING-BEHIND, AWAITING-UNVERIFIED, GAP, UNKNOWN | yes | **yes** (UNBOUNDED; UNRESOLVED) |
| Structural evidence failure | yes | **yes** (UNRESOLVED) |
| OVER_RESERVED | yes | yes (A = 0) |
| Master class-B change pending reconciliation | yes | **yes** (status UNKNOWN until reconciled) |

When no reduction can be authorized (any "yes" in the last column), the model returns UNRESOLVED or DENY; it does not promise a safe exit. Protective intervention is the separate G-06 problem and is not solved here.

### 2.8 Evidence and trust model [R]

Five separate properties, never collapsed into one "verified" flag. A failed or unavailable check is never a pass.

| Property | Question | Established by | What it does NOT establish |
|---|---|---|---|
| Integrity | Unchanged since it was made? | hash of canonical bytes compared with a hash obtained through a trusted channel | who made it; that it is true |
| Provenance | Where from, how derived? | metadata: source, request, raw-payload hash, state-keeper version | only a claim by whoever wrote it |
| Authenticity | Did the claimed party produce it? | signature or MAC with that party's key | that the key holder is uncompromised; that the broker told the truth |
| Consistency | Does it agree with independent evidence and its own invariants? | cross-checks between position, snapshot and executions; fills never exceed order quantity | agreement of sources that share a failure (common mode) |
| Freshness | Recent enough, and not a replay? | independent clock; sequence and watermark monotonicity | content truth; a valid signed record can be stale |

Exactly one result per property, recorded in every evaluation. Only the first state is acceptable.

| Property | Acceptable | Failure states (distinct reason codes, written with the property prefix) |
|---|---|---|
| Integrity | MATCH | INTEGRITY.MISMATCH, HASH_MISSING, NO_TRUSTED_REFERENCE |
| Provenance | COMPLETE (fields present and well-typed; completeness, not truth) | INCOMPLETE, MALFORMED |
| Authenticity | VERIFIED | INVALID_SIGNATURE, SIGNATURE_MISSING, KEY_UNKNOWN, KEY_REVOKED |
| Consistency | CONSISTENT | INCONSISTENT, NO_INDEPENDENT_EVIDENCE |
| Freshness | FRESH | STALE, REPLAY, FROM_FUTURE, CLOCK_UNAVAILABLE |

- **Name collision resolved.** The addendum uses MISMATCH for both an integrity failure and a position status. Here they are INTEGRITY.MISMATCH and POSITION.MISMATCH.
- **Two kinds of Consistency failure (D19).** A *quantified* position mismatch (known d, contiguous events) is carried in the bounds and is a failure for increases only. A *structural* inconsistency (same id with different content, cumulative-quantity conflict, overfill, conflicting snapshots at one watermark) cannot be quantified and blocks increases and reductions.
- Any failure state blocks increases. The state-keeper cannot override a failure state. An unavailable check (for example CLOCK_UNAVAILABLE) is a failure state.
- NO_INDEPENDENT_EVIDENCE (one source, no second channel) is not tolerated for reductions (D06 approved). Whether it may be tolerated in a first replay for any other purpose, and what independent evidence any future live use requires, remain **OPEN** (D24).
- **Integrity is not truth.** A hash, a signature or a valid provenance record establishes at most integrity, provenance or authenticity of what the state-keeper reports. It does not establish that the broker's reported state is true. The raw broker payload and its hash are retained so the chain reaches the broker's own message.
- **State-keeper trust limitation (C-14).** Stated in the executive verdict and here: if the state keeper is compromised or wrong, no property of this model holds. D23 and D24 are blockers for any broker contact or live-use claim.
- **State-keeper compromise (OPEN, D05, D23).** When the state-keeper is the only evidence source, the model *can* establish: the derived values are a reproducible function of the ledger; the ledger is internally consistent; changes to a log are detectable if a reference hash is held outside the state-keeper; replay is deterministic. It *cannot* establish: that any event is true or complete, that no event was omitted or fabricated, or that signed state is honest; there is no independent consistency check (NO_INDEPENDENT_EVIDENCE). v0.1 therefore states assumption A-7 plainly (the ledger is honest and complete as given) and does not remove it.
- **Key management (OPEN, D23).** Who holds signing keys, how they are rotated and revoked, and what happens on suspected compromise are not decided and not mandated here. Hypothesis [H]: the authority holds only a verification key; the strategy never holds a signing key; on suspected compromise the system fails closed (denies increases). These are labelled hypotheses, not implementation assumptions of v0.1.

- **Observed versus derived.** Observed evidence (2.2) is never recomputed. Every derived value is a pure function of (log, configuration, model version, as_of) and is reproducible; each evaluation record stores the item hash, ledger revision, configuration hash, master version, model version and references to every item used.

### 2.9 Reservation and compare-and-set semantics [R]

**Pure function** `evaluate(ledger_snapshot, proposal, config) -> Decision`. It never mutates, never reserves, and accepts no derived quantity from the caller. Decision fields: outcome (ALLOW, DENY, UNRESOLVED), derived values (F_min, F_max, B, S, U, A_raw, A, status, flags), failure codes, ledger_revision, item_hash, model_version, config_hash, evidence references, explanation.

**Commit layer** `commit(decision, store)`:
1. read revision R, items;
2. evaluate against exactly R;
3. **re-validate freshness (requirement E):** call the pure `evaluate` again with as_of = the commit time on the store's current ledger; proceed only if it returns ALLOW for the same proposal; this re-checks snapshot age against S_lim (D07) and every other freshness check at commit time, using the same pure function, so the commit layer decides nothing itself;
4. in one atomic step: if store.revision == decision.ledger_revision and item_hash matches and outcome == ALLOW and no reservation exists for proposal_id and (commit time - decision.as_of) <= D_max: append the reservation and the AUTHORIZED order (one record, counted once) and set revision = R + 1;
5. otherwise change nothing; if the revision moved, re-evaluate from step 1 (retry bound K, decision D09; exhausting K ends in DENY).

The commit layer never decides permissibility; it commits only a decision the pure function returned for the exact revision. A stale decision never becomes authority. Applying a broker event uses the same serializer and advances the revision.

**Minimum reservation record:** reservation_id (= order_id), proposal_id, side, qty, evaluated_revision, committed_revision, decision hash, created_at and expires_at (independent clock), state in {ACTIVE, CONSUMED (submitted), RELEASED (reject, cancel, fill complete), EXPIRED}.
**Lifecycle relation:** commit creates AUTHORIZED (reserves B or S). Submit consumes the token. Reject, cancel confirmation or expiry releases it. A fill reduces R through net_cum. An order that reaches the broker without a live reservation is detected as an unknown order and then counted (the window before detection is a residual risk, section 6).
**Valid evaluation versus committed reservation:** a Decision is an evaluation record only. Authority exists only when a reservation commit succeeds.
**Required behaviours:** duplicate commit of the same proposal returns the existing reservation with no second one; commit failure after a valid decision leaves no reservation and no authority; serializer or store unavailable means DENY.

**Revision coverage and time (F-6, D21) [R].**
- The revision counter increases on every change to the derived ledger: each log append that changes an item (applied event, new or resolved orphan or pending item, status change, OVER_RESERVED change), each reservation made, released or expired, each master version change, each configuration change. Duplicates that change nothing do not increase it. As a second line of defense every decision also records the **item hash** (items, master version, configuration hash), so a change the counter missed still fails the commit check.
- Passage of time is not a ledger change. The pure function takes an explicit **as_of** time from the independent clock; freshness is evaluated at as_of. The decision records as_of, and the commit rejects a decision when (commit time - as_of) exceeds **D_max** (parameter, value OPEN, D21). Without this a snapshot fresh at evaluation could be stale at commit with the revision unchanged. **Freshness is re-validated at commit (step 3 of the commit layer); S_lim is not extended by D_max.** D_max is an additional cap on the age of the *decision*, not an allowance on the age of the *snapshot*.
- Reservation expiry (TTL, D03) is itself an event recorded in the log at an independent-clock time (T05), so it is covered by the counter.

**Reason codes [R].** Decision reasons: R_BLOCK_UNKNOWN_ORDER, R_BLOCK_ORPHAN, R_BLOCK_STATUS, R_BLOCK_PENDING_REFERENCE, R_UNBOUNDED, R_EVIDENCE_FAILURE, R_OVER_RESERVED, R_EXCEEDS_A, R_EXCEEDS_LIMIT, R_MASTER_CHANGE, R_MALFORMED_PROPOSAL, R_FOREIGN_INSTRUMENT. Commit reasons: R_STALE_REVISION, R_DECISION_STALE, R_DUPLICATE, R_STORE_UNAVAILABLE. Evidence codes are those of 2.8. A decision lists every applicable code.

### 2.10 Frozen numerical vectors (hand-calculated; not executed)

Unless stated: RECONCILED, single instrument, long-only, exposure limit L = 150. "Probe" decisions are a reduction (sell 10) and an increase (buy 10). Bounds are F_min and F_max of 2.4. "n/a" = UNBOUNDED, no bounds or values are computed. Codes use the reason-code set of 2.9. Where a vector exercises the oracle gap classes, the hand-derived oracle value is given and labelled.

| ID | Setup | F_min | F_max | U | A_raw | A | Probe: sell 10 / buy 10 | Codes |
|---|---|---|---|---|---|---|---|---|
| V01 | F=100, working sell 60 | 100 | 100 | 100 | 40 | 40 | ALLOW / ALLOW | none |
| V02 | F=100, working buy 20 | 100 | 100 | 120 | 100 | 100 | ALLOW / ALLOW | none |
| V03 | F=100, working buy 20 and sell 30 | 100 | 100 | 120 | 70 | 70 | ALLOW / ALLOW | none |
| V04 | F=100, working sell 120 (supplied ledger, not reachable by the authority) | 100 | 100 | 100 | -20 | 0 | DENY / DENY | R_OVER_RESERVED |
| V05 | F=100, working buy 20, fill 5: F=105, B=15 | 105 | 105 | 120 | 105 | 105 | ALLOW / ALLOW | none |
| V06 | F=100, working sell 30, fill 10: F=90, S=20 | 90 | 90 | 90 | 70 | 70 | ALLOW / ALLOW | none |
| V07 | Discrepancy, no orphan: F_d=70, F_b=65 at the same W (d=-5), MISMATCH, working sell 20 | 65 | 70 | 70 | 45 | 45 | ALLOW / DENY | R_BLOCK_STATUS |
| V08a | V07 plus orphan sell 5 (T1) known to be after W (T4) | 60 | 70 | 70 | 40 | 40 | ALLOW / DENY | R_BLOCK_STATUS, R_BLOCK_ORPHAN. Oracle A=40: tight |
| V08b | V07 plus orphan sell 5 (T1) with broker_seq <= W (T3, may already be in the snapshot) | 60 | 70 | 70 | 40 | 40 | ALLOW / DENY | same. Hand-derived oracle A=45: gap 5, class G1, accepted (D01) |
| V09 | withdrawn (it exercised H-LINK, not adopted) | | | | | | | |
| V10 | F=100, UNKNOWN sell 30, UNKNOWN buy 20 | 100 | 100 | 120 | 70 | 70 | ALLOW / DENY | R_BLOCK_UNKNOWN_ORDER |
| V11 | Orphan with no discrepancy: F=100, orphan buy 7 (T1) | 100 | 107 | 107 | 100 | 100 | ALLOW / DENY | R_BLOCK_ORPHAN |
| V12 | F=100, orphan of unknown side, quantity 7 (T1u) | 93 | 107 | 107 | 93 | 93 | ALLOW / DENY | R_BLOCK_ORPHAN |
| V13 | F=100, orphan of unknown quantity (T2-U) | n/a | n/a | n/a | n/a | n/a | UNRESOLVED / DENY | R_UNBOUNDED, R_BLOCK_ORPHAN |
| V14 | F=100, revision 7, two sell proposals of 60 evaluated on revision 7 | | | | | | first commits (revision 8, S=60); second fails the revision check, re-evaluates: A=40, 60 > 40, DENY; one reservation exists | R_STALE_REVISION, R_EXCEEDS_A |
| V15 | F=100, sell 60 CANCEL_PENDING | 100 | 100 | 100 | 40 | 40 | ALLOW / ALLOW | none. Fill first: F=40, S=0, A_raw=40. Cancel first (cum 0): F=100, A=100 |
| V16 | F=100, working sells 60 and 40; an earlier buy of 30 is busted: F=70 | 70 | 70 | 70 | -30 | 0 | DENY / DENY | R_OVER_RESERVED |
| V17 | Discrepancy d=+5: F_d=100, F_b=105, working buy 20 | 100 | 105 | 125 | 100 | 100 | ALLOW / DENY | R_BLOCK_STATUS. After applying the explaining 5-unit fill: F=105, B=15, RECONCILED: U=120, A_raw=105 (U falls, A_raw rises; I1 part 2) |
| V18 | F=100, working buy 20 | 100 | 100 | 120 | 100 | 100 | buy 30 ALLOW (U=150); buy 31 DENY | R_EXCEEDS_LIMIT |
| V19 | Duplicate execution report, identical content | no change | | | | | no change, no revision change | none |
| V20 | F=100, working buy 20, fill 8, cancel confirmed with cum 8 | 108 | 108 | 108 | 108 | 108 | ALLOW / ALLOW | none |
| V21 | F=100, sell 101 proposed | 100 | 100 | 100 | 100 | 100 | DENY (not clipped) | R_EXCEEDS_A |
| V22 | F=100, ambiguous event (T2), quantity 7 parseable | 93 | 107 | 107 | 93 | 93 | ALLOW / DENY | R_BLOCK_ORPHAN. Oracle also enumerates the "did not occur" world; bounds unchanged |
| V23 | F_d=100, F_b=105 (d=+5), orphan buy 5 (T1) with broker_seq <= W (T3) | 100 | 110 | 110 | 100 | 100 | ALLOW / DENY | R_BLOCK_STATUS, R_BLOCK_ORPHAN. Hand-derived oracle U=105: gap 5, class G1 |
| V24 | As V23, orphan has broker_seq > W (T4) | 100 | 110 | 110 | 100 | 100 | ALLOW / DENY | same. Hand-derived oracle U=110: tight |
| V25 | Relationship unproven: F_d=70, F_b=65, orphan sell 5 with no broker_seq, working sell 20 | 60 | 70 | 70 | 40 | 40 | ALLOW / DENY | R_BLOCK_STATUS, R_BLOCK_ORPHAN. Oracle A=min(40 for T4, 45 for T3)=40 |
| V26 | Duplicate delivery of exec E1 (buy 10 of a buy 20): F=100, R=10 | 100 | 100 | 110 | 100 | 100 | ALLOW / ALLOW | none. Second delivery: no change, duplicate counter 1, revision unchanged |
| V27 | Same event_id, conflicting content: E1 applied (buy 10); E1 arrives again with quantity 12 | | | | | | UNRESOLVED / DENY | R_EVIDENCE_FAILURE (Consistency INCONSISTENT), R_BLOCK_UNKNOWN_ORDER. Order UNKNOWN; bounds diagnostic only |
| V28 | Gap below the watermark: events 501 and 503 applied, 502 missing, snapshot W=503 | n/a | n/a | n/a | n/a | n/a | UNRESOLVED / DENY | R_UNBOUNDED, R_BLOCK_STATUS (GAP). When 502 arrives and F_d(503)=F_b: RECONCILED |
| V29 | Snapshot ahead: highest applied 502, snapshot qty 65 at W=504, F_d(502)=70 | n/a | n/a | n/a | n/a | n/a | UNRESOLVED / DENY | R_UNBOUNDED, R_BLOCK_STATUS (AWAITING-BEHIND, D18). After 503 and 504 arrive and F_d(504)=65: RECONCILED |
| V30 | Bust after a terminal state: buy 100 FILLED by E1 from F=0; E1 busted | 0 | 0 | 0 | 0 | 0 | DENY / ALLOW | R_EXCEEDS_A. History keeps FILLED plus a BUST record; net_cum=0; R=0 (no resurrection); F_d=0 |
| V31 | Correction naming an unknown execution X99 | n/a | n/a | n/a | n/a | n/a | UNRESOLVED / DENY | R_UNBOUNDED, R_BLOCK_PENDING_REFERENCE. Held pending until X99 arrives or the broker resolves it |
| V32 | Late fill after cancellation: F=100, sell 60 CANCELED (cum 0, confirmed); then execution sell 5 for that order arrives | 95 | 100 | 100 | 35 | 35 | UNRESOLVED / DENY | R_EVIDENCE_FAILURE, R_BLOCK_UNKNOWN_ORDER (bounds diagnostic). Order UNKNOWN with R=60, execution pending. After authoritative resolution (CANCELED, cum 5): F=95, R=0, A=95 |
| V33 | Reservation expiry: F=100, sell 60 AUTHORIZED (S=60, A=40); TTL passes | 100 | 100 | 100 | 100 | 100 | ALLOW / ALLOW | none. T05 releases R; revision + 1 |
| V34 | Late broker ack for the expired order of V33 | 100 | 100 | 100 | 40 | 40 | ALLOW / DENY | R_BLOCK_UNKNOWN_ORDER. T22: order UNKNOWN, R=60 re-reserved, no evidence failure |
| V35 | Master semantic change (class B, symbol mapping): F=100, sell 60 AUTHORIZED unsubmitted, sell 20 working at the broker | n/a | n/a | n/a | n/a | n/a | UNRESOLVED / DENY | R_MASTER_CHANGE, R_UNBOUNDED. The authorized sell expires (S: 80 to 20); status UNKNOWN until reconciled under the new version. After: F=100, A=80, ALLOW / ALLOW |
| V36 | Two simultaneous buys of 30 on the same revision, F=100 | | | | | | first commits (B=30, U=130); second fails the check, re-evaluates: U+30=160 > 150: DENY | R_STALE_REVISION, R_EXCEEDS_LIMIT |
| V37 | Buy 30 and sell 60 evaluated concurrently, F=100 | | | | | | one commits; the other retries and is ALLOW either way (buy first: A_raw=100; sell first: U=130). Cost: one retry, not a denial (D04) | R_STALE_REVISION on the retried one |
| V38 | Normal AWAITING: S0 qty 100 at W=500; E501 buy 20, E502 sell 50 applied: F_d=70, no new snapshot | 70 | 70 | 70 | 70 | 70 | ALLOW / ALLOW | none. Snapshot qty 70 at W=502 then gives RECONCILED |
| V39 | Intervening fill: F=100, working sell 30 (A=70); sell 60 evaluated on revision 7 (ALLOW); the sell 30 fills (F=70, S=0, revision 8) before the commit | 70 | 70 | 70 | 70 | 70 | commit rejected; re-evaluated on revision 8: A=70, ALLOW, new decision bound to revision 8 | R_STALE_REVISION |
| V40 | UNKNOWN event between evaluation and commit: buy 30 evaluated ALLOW on revision 7; an UNKNOWN order appears (revision 8) | | | | | | commit rejected; re-evaluated: DENY | R_STALE_REVISION, R_BLOCK_UNKNOWN_ORDER |
| V41 | Duplicate commit of the same decision | | | | | | second attempt returns the existing reservation; no second reservation; revision advanced once | R_DUPLICATE |
| V42 | Commit failure after a valid decision: store unavailable | | | | | | no reservation and no authority; the order may not be submitted | R_STORE_UNAVAILABLE |
| V43 | Partial fill then cancellation: F=100, sell 60 working; fill 20; cancel confirmed with cum 20 | 80 | 80 | 80 | 80 | 80 | after the fill: F=80, S=40, A_raw=40 (unchanged, I1b); after the cancel: S=0 | none |
| V44 | Decision age and commit-time freshness: evaluation with a snapshot younger than S_lim; at commit time the snapshot is older than S_lim (or the decision older than D_max), with no ledger change | | | | | | commit rejected: the re-evaluation at commit time returns STALE or D_max is exceeded; **a snapshot older than S_lim fails even when the decision age is within D_max** | R_DECISION_STALE |
| V45 | Release after confirmed rejection: F=100, buy 20 AUTHORIZED, SUBMITTED, REJECTED (cum 0) | 100 | 100 | 100 | 100 | 100 | ALLOW / ALLOW | none. B back to 0 |
| V46 | V01 base plus an earlier applied sell of 5 (seq 90 <= W) and a committed reduction of 40 (S = 100, A_raw was 0); a correction (own seq 110 > W) raises the sold amount to 7: F = 98, F_d(100) unchanged, d = 0 | 98 | 98 | 98 | -2 | 0 | DENY / DENY | R_OVER_RESERVED. Prior authorization invalidated in effect (I8); no new authorization possible; who cancels is G-07 |
| V47 | S0 qty 100 at W = 500; E501 buy 20, E503 sell 50 applied, E502 (buy 10) missing; snapshot W = 503, F_b = 80. Then E502 arrives | before: n/a; after: 80 | 80 | 80 | 80 | 80 | before: UNRESOLVED / DENY; after: ALLOW / ALLOW | before: R_UNBOUNDED, R_BLOCK_STATUS (GAP); after: none |
| V48 | As V47 before E502 arrives, and a later snapshot W = 510, F_b = 80 arrives while sequence 502 is still missing | n/a | n/a | n/a | n/a | n/a | UNRESOLVED / DENY | R_UNBOUNDED, R_BLOCK_STATUS (GAP persists; a later snapshot never clears it) |
| V49 | Execution E1 (buy 5) applied; correction C1 (5 to 4, seq 201) and C2 (5 to 3, seq 202), each valid alone. Log order C1, C2 | n/a | n/a | n/a | n/a | n/a | UNRESOLVED / DENY | R_EVIDENCE_FAILURE (C2 names a value no longer current: structural conflict). Reversed log order applies C2 and conflicts C1: outcomes depend on log position, by design (D20) |
| V50 | Reconnect resends E3 to E5, already applied | unchanged | unchanged | unchanged | unchanged | unchanged | unchanged | none. No revision change; duplicate counters only |
| V51 | F_base = 95 (all seq <= W = 100); one applied buy of 5 with no broker_seq (F_d = 100); snapshot W = 100, F_b = 100; no orders. Interpretations: inside F_d(W): d_1 = 0; outside: d_2 = +5 | 100 | 105 | 105 | 100 | 100 | ALLOW / DENY | R_BLOCK_STATUS (MISMATCH; d_plus = max(0, 0, 5) = 5, d_minus = max(0, 0, -5) = 0) |
| V52 | Proposals with qty True, 1.0, "1", -0, 10^30 (above Q_MAX), NaN, side "BUY " | n/a | n/a | n/a | n/a | n/a | DENY for every one; never ALLOW; no exception escapes | R_MALFORMED_PROPOSAL |
| V53 | F_d = 70; discrepancy supplied as magnitude 5 only; working sell 20 | 65 | 75 | 75 | 45 | 45 | ALLOW / DENY | R_BLOCK_STATUS (d_plus = d_minus = 5) |
| V54 | Snapshot with qty -3 in the long-only envelope | n/a | n/a | n/a | n/a | n/a | UNRESOLVED / DENY | R_EVIDENCE_FAILURE (Consistency INCONSISTENT: envelope violation) |
| V55 | Bust naming an unknown original X77 | n/a | n/a | n/a | n/a | n/a | UNRESOLVED / DENY | R_UNBOUNDED, R_BLOCK_PENDING_REFERENCE |
| V56 | **Uncovered failure, documented limitation.** True position 100 after buy E1 of 10; the broker re-sends E1 under a different event id and exec_id; both applied: F_d = 110; working sell 60 | 110 | 110 | 110 | 50 | 50 | The model ALLOWs sell 50. True A = 100 - 60 = 40, so **false permission of 10 units** | none: not detected (A-11, A-12). A later snapshot F_b = 100 gives d = -10: F_min = 100, A_raw = 40. A known limitation, never a passing result |

Vectors V46 to V56 were added in Revision 3. Hand-derived, not executed; V56 records a failure the model cannot prevent.

