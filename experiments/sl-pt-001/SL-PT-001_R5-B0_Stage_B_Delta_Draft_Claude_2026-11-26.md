# SL-PT-001 R5-B0: Stage B delta draft (against frozen R4.2i)

**From:** Claude (Implementation Lead) | **To:** Founder | **For review by:** GPT, Gemini B (after the founder decision batch)
**Date:** 2026-11-26 | **Base:** R4.2i, SHA-256 `4259551121fa3d271074fb13da51fb270ae859b0b516a953752731f20972a51a` | **Plan:** Strike 7 (`SL-PT-001_Strike7_Stage_B_Execution_Front_Claude_2026-11-26.md`)
**Status: DRAFT, step S0. Not a freeze candidate.** Nothing is authorized, built, keyed or sent.
**Form:** a diff packet. Each change names the base section, what changes, and the finding or decision behind it. This document does not reproduce R4.2i.

**Scope rule (check this first).** Every change is confined to R4.2i's **Stage B draft sections**: §8.2–§8.6, §9, §12, Stage B tests, and the B rows of §15 and §16. **No Stage A section (§2–§7, §8.1, §10, §11, §13) is changed.** Where Stage B needs something those sections define as closed (the record types in §10.1, the TER-1 schema in §10.4, the terminal set in §11.1), the draft puts it in a **separate Stage B chain and schema** (D-8 option ii), so the frozen Stage A text stays untouched and Stage A evidence stays tied to its hash. If any reviewer finds an implicit Stage A change, that is a blocking finding, not an editorial one.

**Pending markers.** `[PENDING D-n]` marks text that rests on a founder decision from the Strike 7 §7 batch. The recommended option is written in, so the draft reads end to end. A different decision replaces only the marked text.

---

## Δ1. New §9.0: deployment and process roles (G-07 §2, §6; PT-A1; B-6, B-7)

**Adds** a section before §9.1.

| Process | G-07 role | Holds | Network | Writes to the Stage B chain |
|---|---|---|---|---|
| **Decision process** (the Stage A pipeline, reused) | K2 + K3 | no broker credential; the V12a check is kept unchanged | `data.alpaca.markets` only | PROPOSAL, APPROVAL (via the approval command), AUTHORIZATION, CANCEL_AUTHORIZATION, terminal CYCLE_B records |
| **Executor** (new) | K5 | the **only** process with paper keys (FD-8) | `paper-api.alpaca.markets` only, by client allowlist; market-data host **refused** | SESSION_OPEN snapshot, CONSUME, WAL, PRESEND, SEND, ORDER_UPDATE, FILL, RELEASE, AMBIGUOUS |
| **Session console** (new) | none (read-only, plus the approval command) | nothing | none | none directly; approval goes through the decision process's CLI |

**Rules:**
1. **There is no call from the decision process to the executor.** The executor **polls** the chain for authorizations that are eligible and assigned to its executor_id, in issuance order. The chain is the K3 store.
2. **Linearizable reads (G7-A2), satisfied by construction:** the executor reads authorization state at LP-CONSUME and LP-PRESEND **while holding the chain append lock**. That is the same lock every write takes (R4.2i §6.3). No cache or replica exists.
3. **One host, one clock:** both processes read the same OS wall clock, so the K3–K5 skew is **σ = 0 by construction**. The venue relationship stays bounded by the §5.6 method. **This statement is void if the processes are ever split across hosts.** `[PENDING D-3]`
4. **Chain:** Stage B uses its own chain `chain-b/events.jsonl` with its own GENESIS, which pins the Stage B frozen set. The Stage A chain is never appended by Stage B code. `[PENDING D-8]`
5. **Disclosed limitation (new, U-G4):** the executor and the decision process run as the same OS user and append to the same file. The chain cannot prove which process wrote a record. A compromised executor could forge an APPROVAL. This falls under G7-A1 (K5 uncompromised) and is no stronger than the existing G7-I8 limitation. It is a disclosed residual, not a control.

## Δ2. New §9.0a: attended sessions (B-1; D-6)

**Adds:**
- Stage B proposals reach the founder **only inside an attended session**, opened with `session open` and closed with `session close`.
- **Session open:**
  - the executor performs the pre-flight reads (Δ8, items 1–3) and records a SESSION_OPEN snapshot: cash, BTC position, open orders, and the account flags;
  - the decision process refuses to issue any authorization unless the latest SESSION_OPEN snapshot is newer than the last terminal order event and matches the ledger fold (Δ6). On a mismatch: DISCREPANCY, halt.
- **Outside a session,** Stage B cycles still run and still construct proposals, but a proposal ends **EXPIRED_UNAPPROVED** at approval_deadline (U22). This is safe and expected.
- **Session console:**
  - polls the chain read-only;
  - on a PROPOSAL record it sounds a local alert and shows the approval view (Δ3) with a live countdown to approval_deadline.
- **No remote or mobile channel.** Out of scope (Strike 7 §6.2).
- **Stage B scheduling:** the same Task Scheduler pattern, with its own task, manifest and declared slots. The FD-7 rules apply unchanged (no catch-up, no retry, overlap refused by the lock). A Stage B task is never registered while a Stage A manifest is active on the same machine.

## Δ3. §9.1 approval record: amendments (PT-A3; B-2; B-4; D-5)

**Changes:**
1. **Bound fields gain** the G-07 §2 execution context: `executor_id`, `account`, `venue`, `action_type` (NEW), `not_before`, `expires_at_max` (= T_d + 180 s), and `proposal_sha256` (the canonical hash of the PROPOSAL record, R4.2i §10.5).
2. **Approver authentication (replaces the reference to "FD-G13", which pointed at the wrong decision: defect B-4).** A new founder decision ID, **FD-G19**:
   - The proposed minimum is **interactive presence**. The approval command runs in the founder's interactive console and requires the founder to type the first 12 hex characters of `proposal_sha256` shown in the approval view. A wrong prefix is refused and recorded.
   - The record states `approver: founder (interactive console; not cryptographically authenticated)`.
   - **Limitation:** this proves that the approval came from the session and that its author saw that hash. It does not prove identity against a compromised host (G7-A1). `[PENDING FD-G19]`
3. **What the founder sees before approving** `[PENDING D-5]`:
   - signal, D(k−1) and D(k);
   - side, q, L and R;
   - every rule result R1–R16;
   - quote time and age;
   - bar-window hash;
   - approval_deadline countdown.
   - **No independent reconstruction is required before approval.** That is done after the terminal state (Δ10, L-4). D7 step 2 is **REPLACED** by this item, and U-O1 is closed by scope, not by feasibility.
4. **Approval of a session is not approval of an order** (restates §9.1).

## Δ4. §9.2 issuance: amendments (PT-A1, PT-A3)

**Adds:**
- **auth_id** := SHA-256 of the canonical AUTHORIZATION record without its `auth_id` field.
- **COID** := `"slpt001-" + first 48 hex characters of auth_id` (56 characters, inside the 128-character limit). It is deterministic, one per authorization, and never reused (FD-G6, G7-I10).
- Issuance writes **one AUTHORIZATION** (action NEW) and **one reservation event** (RESERVE, amount R) under one lock hold. Either both are written or neither is (§8.5).
- **GTC branch only** `[PENDING OI-10]`: in the same lock hold, issuance also writes **one CANCEL_AUTHORIZATION** bound to the NEW authorization's COID:
  - not_before = T_d + 170 s; expires_at = T_d + 180 s; the same executor, account and venue;
  - it is valid only if the NEW order is non-terminal at its LP-PRESEND read.
  - No second policy evaluation happens. The cancel is authorized at issuance, as part of the bound order lifetime.

## Δ5. §9.4 and §9.5: values and TIF branches (FD-G18, OI-10)

- **δ_send = 10 s** `[PENDING D-3]`. The executor arms a monotonic timer at its LP-PRESEND sample. If the send hasn't begun by 10 s → NOT_SENT. If it began but exceeded the bound, or its outcome is uncertain → AMBIGUOUS (unchanged text).
- **Retry:** **none.** An AMBIGUOUS outcome is resolved by query by the original COID only. Found → continue tracking. Not found → it stays AMBIGUOUS, R16 blocks every proposal, and the founder is notified. FD-G16 = (a). `[PENDING D-1]`
- **TIF, two branches.** Chosen after the pre-flight observes `price_increment` (Δ8). `[PENDING OI-10]`
  - **IOC:** no cancel path. The order is terminal on the venue's response; a zero-fill result is a valid attempt (§0.1). Chosen if L − ask (§7.2) is essentially zero at the observed increment.
  - **GTC + governed cancel:** the CANCEL_AUTHORIZATION of Δ4 runs the same LP-CONSUME → LP-WAL → LP-PRESEND → send path, with its own δ_send and AMBIGUOUS handling. A cancel request changes nothing in the ledger (U56). Release happens only on a reconciled terminal state. Chosen if L sits materially below the ask.
  - **§7.2 is not changed in either branch** (it is a Stage A section).
- `partial_fill_accepted` = **true** is required (unchanged, R2).

## Δ6. §8.2 ledger: source of reconciled cash (OI-17 input)

**Adds:**
- **The ledger is a deterministic fold** of the Stage B chain's RESERVE, FILL and RELEASE events, starting from the **first SESSION_OPEN snapshot**. The fold follows the same discipline as the R4.2i §4.9 bar store.
- **No ledger value is written directly.** The append lock is the ledger lock (§8.5).
- **R6, R8 and R12** read cash_available, BTC held and equity from the fold at checkpoint (a). R12's $450 buy gate therefore uses the reconciled value, as R4.2i §7.3 already requires.
- **At every SESSION_OPEN,** the snapshot must equal the fold: cash in exact cents, BTC on the quantity increment, open orders. Otherwise DISCREPANCY: halt.
- **The first SESSION_OPEN must show:** no BTC position, no open orders, and cash ≥ $450.00. Otherwise the first BUY cannot pass R12, and the session refuses with a recorded reason.

## Δ7. §8.4 fills: venue fields stay branched (U-V3)

**Unchanged in substance.** The draft keeps both fee branches (BTC, USD) and leaves the fill-id field name UNVERIFIED.

**Adds:**
- The executor records the **raw** order and activity responses as artifacts (§10.2 pattern). FILL events cite the artifact hash and the venue's fill identifier, whichever field the venue returns.
- **The first order's fills determine which branch applies.** That observation is recorded and does not change the spec text afterwards.
- Unknown or extra fee fields → DISCREPANCY: halt, no inference.

## Δ8. §9.6 first-order sequence: pre-flight made concrete (CF-7, D-9)

**Replaces step 2's bullet list with a scripted, read-only pre-flight.** It runs from the executor with paper keys, before Stage B authorization (FD-9), and needs **D-9** to run.

1. `GET` account: cash, buying power, `multiplier`, shorting setting, crypto status. Expected: 1×, no shorting, cash ≥ $450.00.
2. `GET` positions: expected no BTC position.
3. `GET` orders (all statuses): expected empty.
4. `GET` asset BTC/USD: `price_increment`, `min_order_size`, `min_trade_increment`, tradable flag. Compared with the policy file. **A mismatch is not an error at pre-flight.** It is the input to a new policy version (P-0.3), which is issued only with a founder record.
5. `GET` order by client order id for a **never-used** COID (`slpt001-preflight-<UTC stamp>`). Expected: not found. Recorded.

**Rules:**
- **The executor's allowlist in pre-flight mode refuses every order-submission and order-cancel route before I/O.** Only the five reads above are permitted.
- Raw responses are committed as artifacts with their hashes.
- **CF-7 governs:** the duplicate-COID test is not a precondition. D7's Stage C precondition is **REPLACED** (B-5).

## Δ9. §9.7 STOP conditions: additions

| Condition | Where detected |
|---|---|
| SESSION_OPEN snapshot ≠ ledger fold | Δ6 |
| an approval with a wrong proposal-hash prefix | Δ3 |
| an executor request to a host outside its allowlist, or a submit route in pre-flight mode | Δ1, Δ8 |
| a Stage B task registered while a Stage A manifest is active | Δ2 |
| unknown fee or fill fields | Δ7 |
| CANCEL_AUTHORIZATION outcome AMBIGUOUS | Δ5 |

## Δ10. §12 reconciliation: path and cadence (FD-G17)

- **L-1:** at the SEND response. The executor decodes the echoed order with **decoder code separate from the request mapper** (G-07 I2(b)) and compares it field by field with the AUTHORIZATION. Mismatch → governance failure, halt.
- **L-2:** at every terminal order state and at every SESSION_OPEN (Δ6).
- **L-3, independent of the executor** `[PENDING D-2]`: **R-c.** After every terminal order state and at session close, the founder compares the Alpaca dashboard order history with the chain's SEND records and records RECONCILE_L3 through the CLI with a typed attestation (order count, COIDs seen).
  - Any order on the dashboard without a matching SEND → UNMEDIATED, halt (G-07 D.4).
  - This is a human channel the executor cannot alter. It detects; it does not prevent.
- **L-4:** after the terminal state, the D-7 reconstructor rebuilds the lifecycle from the committed Stage B chain and artifacts:
  - proposal → approval → authorization → consume → WAL → presend → send → updates → fills → ledger → release.
  - Zero unexplained differences are required for the milestone.
  - Custody follows the FD-6 pattern: a blind author, the auditor hash committed before the first order, a seed commit-reveal, and the founder's hand cross-check. `[PENDING D-7]`

## Δ11. Stage B schema and terminal set (TER-2; outside §10.4 and §11.1)

**Adds a Stage B-only schema, TER-2.** Field lists are given here; the closed schema text is written at the Stage B freeze.
- **Record types:** GENESIS_B, RUN_OPEN_B, SESSION_OPEN, SESSION_CLOSE, CYCLE_B, PROPOSAL, APPROVAL, APPROVAL_REFUSED, AUTHORIZATION, CANCEL_AUTHORIZATION, RESERVE, CONSUME, WAL, PRESEND, NOT_SENT, SEND, AMBIGUOUS, ORDER_UPDATE, FILL, RELEASE, RECONCILE_L3, DISCREPANCY, plus the Stage A anomaly types (CYCLE_OVERRUN, CONCURRENT_INVOCATION, OFF_RUN, RUN_STOPPED, RUN_CLOSE) re-declared for chain B.
- **CYCLE_B terminal states:**
  - the Stage A set, with these replacements:
    - SHADOW_EXPIRED is replaced by **EXPIRED_UNAPPROVED**, **AUTHORIZATION_DIED** (any checkpoint failure, with the death event) and **AUTHORIZED**;
    - AUTHORIZED is terminal for the cycle; the order then has its own lifecycle;
  - the order lifecycle is terminal at a reconciled **FILLED**, **CANCELED**, **EXPIRED** or **VENUE_REJECTED**, or stays AMBIGUOUS.
- **Every TER-2 record carries:** writer role (decision or executor), executor_id, the authorization and approval references where they apply, and the policy and configuration hashes (G-07 I9).

## Δ12. New tests (DESIGNED; Stage B only; numbered UB to avoid collision with U1–U122)

| ID | Test | Expected |
|---|---|---|
| UB1 | the decision process attempts a request to the trading host | refused before I/O |
| UB2 | the executor attempts a market-data or other non-allowlisted host | refused before I/O |
| UB3 | pre-flight mode: a submit or cancel route | refused before I/O |
| UB4 | broker credentials present in the decision process's environment or configuration | BOUNDARY_FAIL (V12a, unchanged) |
| UB5 | approval with a wrong proposal-hash prefix | APPROVAL_REFUSED; no authorization |
| UB6 | approval at approval_deadline / + 1 ns | valid / EXPIRED_UNAPPROVED (= U29, extended to the context fields) |
| UB7 | an authorization whose context names another executor, account or venue | not consumed (G-07 B.6) |
| UB8 | the executor polls before not_before / after expires_at − δ_send | not consumed / NOT_SENT |
| UB9 | two executors poll the same authorization concurrently | exactly one CONSUME (= U65) |
| UB10 | crash after CONSUME, after WAL, after PRESEND, after the send call | no second send; WAL-after-crash → AMBIGUOUS → query by COID (G-07 C.5) |
| UB11 | the stub venue times out on submit | AMBIGUOUS; query by COID only; no resubmission; R16 blocks new proposals |
| UB12 | the echoed order differs on any one bound field | L-1 failure, halt |
| UB13 | SESSION_OPEN snapshot differs from the fold by 1 cent / 1 increment | DISCREPANCY, halt |
| UB14 | a stub order on the account with no SEND record | UNMEDIATED on L-3, halt |
| UB15 | GTC branch: NEW filled before the CANCEL window opens | CANCEL_AUTHORIZATION not consumed (order terminal at LP-PRESEND) |
| UB16 | GTC branch: partial fill, then cancel | released remainder = outstanding_usd from cumulative Q_f (§8.2); no per-fill decrement |
| UB17 | fee reported in BTC / in USD / in an unknown field | branch applied / branch applied / DISCREPANCY |
| UB18 | a Stage B task registered while a Stage A manifest is active | refused at RUN_OPEN_B |

**All existing B-only tests in R4.2i §14** (U20–U23, U29, U30, U48, U50, U51, U63–U65, U86, U90, U93 and the others marked B) stay in the Stage B gate unchanged.

## Δ13. Register updates (B rows only)

**§15 additions:**
- **U-G4** (B; Δ1.5): same-user chain writers; APPROVAL forgeable by a compromised executor. Label: disclosed limitation (G7-A1).
- **U-G5** (B; Δ3): approver authentication is presence-based only. Label: disclosed limitation.

**§15 changes:**
- **U-O1:** closed by scope (Δ3.3). The reconstruction moves after the terminal state.
- **U-G2:** σ resolved by single-host construction; δ_send set. Label: CONDITIONAL on one host.

**§16 changes:**

| ID | Status in this draft |
|---|---|
| OI-10 | two branches drafted; decision after pre-flight |
| OI-11 | FD-G16, FD-G17 and FD-G18 drafted with recommendations; FD-G13 unchanged; FD-G19 new |
| OI-12 | FD-8 + D-9 needed for pre-flight |
| OI-15 | drafted as D-7 |
| OI-17 | ledger source made explicit (Δ6); **review still required** |
| **OI-19 (new)** | B-4 defect: §9.1 FD-G13 reference. Fixed in Δ3.2 |
| **OI-20 (new)** | B-5: D7 Stage C precondition. Replaced by CF-7 in Δ8 |

---

## What this draft does not do

- It decides nothing. Every `[PENDING]` item waits for the founder.
- It does not change policy P-0.2. A P-0.3 (TIF, observed increments) is issued only after pre-flight, with a founder record.
- It contains no harness code and describes no harness internals beyond the R4.2i sections it reuses.
- It is not reviewed. Review happens after the founder decision batch, as a closure round on this diff.

*End of R5-B0.*
