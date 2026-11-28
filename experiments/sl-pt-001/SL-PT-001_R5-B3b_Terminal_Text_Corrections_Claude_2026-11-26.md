# SL-PT-001 R5-B3b: terminal text corrections

**Responds to:** Strike 7.6 | **Base:** R5-B3a over R5-B3 over R5-B2 | **Status:** DRAFT; no freeze, nothing authorized. Exact replacement text only. **Design iteration stops after this check.**

## 1. Closure matrix

| Finding | Defect | Correction | Location |
|---|---|---|---|
| G-B3a-01 | NOT_ACCEPTED released the reservation on a 4xx plus two not-found queries, which is not proof the venue refused the order | **NOT_ACCEPTED is removed.** Only a venue order object for the COID with a terminal status releases the reservation (via ORDER_TERMINAL). A 4xx with no order found → AMBIGUOUS (REJECTED_UNCONFIRMED), with the exposure retained | R5-B3 §D table rows 2–3; R5-B3 §H.3; schema; UB-S5′ |
| G-B3a-02 | the cumulative bound from CONSUME allows up to ε of drift by (d) and up to ε more by t_resp, so W(t_resp) − W(t_d) ≤ δ_send + 2ε. The margin used 1ε | Margin = **2 × ε_step**; worst-case window 49.5 s | R5-B3a §C rows; D-3; UB-T2′ |
| G-B3a-03 | L-2 PASS could rest on a non-authoritative basis | **PASS is evaluated on the authoritative basis only**; the other basis is diagnostic | R5-B3 §A.3 |
| G-B3a-04a | UB-S1 expected "exactly one POST" at crash points where no POST can have happened | Expectations per crash point (0, ≤ 1, or 1; never > 1); recovery rule for a WAL without PRESEND | R5-B2 UB-S1; R5-B2 §2.9.6 item 3 |
| G-B3a-04b | auth_id was defined as a hash of the AUTHORIZATION record, which contains the COID derived from auth_id: a circular definition | Explicit preimages that exclude every derived field | R5-B2 §2.7 item 4; R5-B3 §D; TER-2 PROPOSAL, AUTHORIZATION |
| G-B3a-04c | fee records were incompletely represented, with no conversion rule for several records or assets | Complete representation, dedup and conversion | R5-B2 §2.9.3 fee cases; ORDER_TERMINAL.fee |
| G-B3a-04d | L-3 identity matching was not one-to-one | Bijection required; duplicates and conflicting identifiers → halt | R5-B3a §F.3 |
| G-B3a-04e | the gate text "M1 on the audit scope (one or more manifests)" could be read as allowing a streak across manifests | M1-1's run_length is **within one manifest** (R4.2i §11.4, frozen); GENESIS_B names that manifest | R5-B3 §4 row 1; R5-B3a §4; R5-B2 §2.2 anchor |
| G-B3a-04f | UB-L3S″ dropped the earlier L-3 cases | All cases restored, plus the new ones | UB-L3S‴ |

## 2. Replacement text

**R5-B3 §D, rows 2 and 3 → replace with:**
> | status ∈ {400, 401, 403, 422} with a parseable error body | query by COID at t_resp + 2 s, then every 30 s | an order object found → tracking + L-1; a venue terminal status (including `rejected`) → ORDER_TERMINAL, Q_f as reported. **Not found → AMBIGUOUS (REJECTED_UNCONFIRMED):** reservation retained; R16 blocks; session stays CLOSING |
> | any other status; timeout; transport error; malformed body | as above | found → tracking + L-1. Not found → AMBIGUOUS (cause as observed), exposure retained |
>
> **Definitive venue non-acceptance** is established only by a venue order object for the COID with a terminal status. No HTTP status, query count or elapsed time establishes it. Whether a 4xx ever leaves an order uncreated without a queryable record is **[VENUE]**, and it is never assumed. *Disclosed:* a rejected order with no queryable record stops Stage B, by R16 (frozen).

**R5-B3 §H.3, first sentence → replace with:**
> After a zero-fill outcome (an ORDER_TERMINAL with Q_f = 0, or a NOT_SENT), the next attempt is permitted only if: …

**R5-B3a §C rows → replace with:**
> | release margin | W(t_d) ≤ expires_at − δ_send − 2·ε_step | NOT_SENT (LATE) |
> | expiry consistency (DERIVED) | the cumulative bound from (c) gives \|(W(t_resp) − W(t_d)) − (M(t_resp) − M(t_d))\| ≤ 2·ε_step. With the total budget: W(t_resp) ≤ W(t_d) + δ_send + 2·ε_step ≤ expires_at | — |
>
> The worst-case consumption window is ≥ 49.5 s (issued = T_d + 120 s).

**R5-B3 §A.3, the PASS sentence → replace with:**
> **PASS** iff, **on the authoritative basis**, C_broker equals C_exact under at least one predeclared rule, and |r| < $0.01. The other basis, where available, is computed and recorded as **diagnostic only**: a difference between the bases is recorded and never makes a failure pass.

**R5-B2 §2.9.6 item 3 → replace with:**
> 3. each WAL without a PRESEND → NOT_SENT (LOCAL_CERTAIN), with full release. A send is only ever made after its PRESEND is durable, so no bytes can have been sent. Each WAL **with** a PRESEND but without a SEND_RESULT or terminal → query by COID (R5-B3 §D rules), **never send**.

**R5-B2 §2.7 item 4, and the TER-2 rows → replace with:**
> - **proposal_sha256** := SHA-256 of the canonical serialization of the PROPOSAL body with the `proposal_sha256` field **removed**. The record's chain `hash` is a different value; both are recorded.
> - **auth_id** := SHA-256 of the canonical serialization of the **authorization preimage** {proposal_sha256, approval_record_hash (the APPROVAL record's chain `hash`), issued, not_before, expires_at, context, reservation.R, campaign_ref, attempt_index}. The preimage excludes `auth_id`, `coid` and every other derived field.
> - **coid** := `slpt001-` + the first 48 hex characters of auth_id.
> - The AUTHORIZATION record carries the preimage fields, auth_id and coid. A verifier recomputes auth_id from the preimage and coid from auth_id.

**R5-B2 §2.9.3 fee cases → replace with:**
> **Fee records** are the venue's fee-type account activities for the order (field names **[VENUE] V-4**), retrieved by following pagination to its end and deduplicated by activity id (same id with different content → DISCREPANCY).
>
> Each is represented as {activity_id, broker_order_id, asset, amount (exact; a debit is recorded as a positive amount), related_fill_id or null, p_ref, usd_equiv}.
>
> **Conversion:**
> - asset USD → usd_equiv = amount;
> - asset BTC → usd_equiv = amount × p_ref, where p_ref = the price of related_fill_id if linked, otherwise P̄;
> - any other asset → DISCREPANCY (FEE_ASSET).
>
> **Totals:** fee_usd = Σ amount over USD records; fee_btc = Σ amount over BTC records; fee_usd_equiv = Σ usd_equiv.
>
> **Cases:**
> - **(F1)** at least one fee record → book fee_usd against cash and fee_btc against held_btc;
> - **(F2)** no fee record, and the position delta = Q_f exactly, and the cash delta matches −G on the authoritative basis under a predeclared rule → fee = 0 (FEE_NONE_OBSERVED);
> - **(F3)** otherwise → DISCREPANCY (FEE_UNRESOLVED).
>
> ORDER_TERMINAL.fee = {case, records [ … ], fee_usd, fee_btc, fee_usd_equiv}.

**R5-B3a §F.3 → replace with:**
> L-3 PASS requires a **one-to-one** matching between the dashboard orders in the session window and chain-b WAL records:
> - each dashboard order is conclusively identified (COID, or broker order id) with exactly one WAL;
> - each WAL is matched by at most one dashboard order;
> - every WAL that has an ORDER_TERMINAL is matched.
>
> **Failures:**
> - two dashboard orders with one COID → DUPLICATE, halt;
> - a dashboard order whose COID and broker order id point to different WALs → DISCREPANCY (IDENTITY_CONFLICT), halt;
> - a field-only correspondence → UNRESOLVED;
> - no correspondence → UNMEDIATED, halt.
>
> A WAL with no dashboard order and no terminal stays AMBIGUOUS.

**R5-B3 §4 row 1 and R5-B3a §4 ([EXEC] M1) → replace with:**
> M1 audit: M1-1 per R4.2i §11.4 (frozen): run_length ≥ 30 consecutive qualifying slots **within one manifest**, and the injection condition. The audit scope may contain several manifests. The streak is never combined across them.

**R5-B2 §2.2 / R5-B3 §G.7 anchor → add to `stage_a_anchor`:**
> `qualifying_manifest_sha256` (the manifest carrying the ≥ 30 streak, as reported by the audit) and `scope_manifests` (every manifest in the audit scope). RUN_OPEN_B is refused unless the audit report states the streak for `qualifying_manifest_sha256`.

**Schema:**
- NOT_ACCEPTED is removed.
- AMBIGUOUS.cause adds REJECTED_UNCONFIRMED.
- The executor's write list drops NOT_ACCEPTED.

## 3. Changed test rows

| ID | Status | Test | Expected |
|---|---|---|---|
| UB-S1′ | replaces UB-S1 | crash after CONSUME; after WAL (no PRESEND); after PRESEND, before t_tx0; after t_tx0, before the response; after the response; before ORDER_TERMINAL | **POSTs seen at the stub: 0 / 0 / ≤ 1 / 1 / 1 / 1; never > 1.** Recovery: NOT_SENT (LOCAL_CERTAIN) / NOT_SENT (LOCAL_CERTAIN) / query only / query only / query only / booking once |
| UB-S5″ | replaces UB-S5′ | 400, 401, 403 and 422, each with (a) no order found, (b) an order found with status `rejected`, (c) found and filled; and 404, 408, 409, 429, 500 with no order found | (a) AMBIGUOUS (REJECTED_UNCONFIRMED), reservation retained; (b) ORDER_TERMINAL Q_f = 0, released; (c) tracking + L-1 + DISCREPANCY (CONTRADICTORY_RESPONSE); others AMBIGUOUS. **No release without an order object** |
| UB-T2″ | replaces UB-T2′ | W(t_d) = expires_at − δ_send − 2·ε_step / + 1 ns; with ε drift by (d) and a further ε by t_resp at maximum budget | release / NOT_SENT (LATE); W(t_resp) ≤ expires_at holds |
| UB-L4″ | replaces UB-L4′ | the authoritative basis fails every rule while the diagnostic basis matches | DISCREPANCY (the diagnostic basis cannot pass it) |
| UB-L9 | new | fee records: one USD; one BTC linked to a fill; one BTC unlinked; two pages; a duplicate id; an ETH fee | usd_equiv = amount / × fill price / × P̄ / complete / collapsed / FEE_ASSET DISCREPANCY |
| UB-H1 | new | recompute auth_id from the recorded preimage, and coid from auth_id; alter any preimage field | equal / mismatch → the record is invalid |
| UB-L3S‴ | replaces UB-L3S″ | **all of:** COID match; broker-id match; field-only; an extra dashboard order; count mismatch; a WAL never observed by the executor but on the dashboard; one COID on two dashboard orders; COID and broker id pointing to different WALs | PASS / PASS / UNRESOLVED / UNMEDIATED halt / UNRESOLVED / PASS / DUPLICATE halt / IDENTITY_CONFLICT halt |
| UB-A1‴ | extends | anchor names a qualifying manifest whose streak the audit report does not state; streak reported only across two manifests | RUN_OPEN_B refused in both |

*End of R5-B3b. Design iteration suspended.*
