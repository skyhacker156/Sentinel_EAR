# SL-PT-001 First-Trade Readiness (D1 to D8)

**Date:** 2026-11-25 | **Author:** Claude | **Dispatch:** "A-Team Dispatch: First-Trade Readiness"
**Classification:** planning and design only. **No implementation, broker connection, account change, credential or order is authorized or has occurred.**
**Labels:** DERIVED / COMPUTED / OBSERVED / **DOCUMENTED** (stated in Alpaca documentation; not tested by us) / ASSUMED / CONDITIONAL / UNVERIFIED / UNBOUNDED. **Nothing here is COMPUTED, and nothing about Alpaca is OBSERVED except the founder's own screenshots.**

**Baseline correction:** the dispatch names G-07 **Draft 0.2a** as the baseline. The current G-07 record is **Draft 0.3** (`f22ee85b…`, polling executor, LP-PRESEND, I1 to I10), and the Stage A design is **v0.1** (`3444db48…`). Both were delivered on 2026-11-25. **Whether they have been pushed is not confirmed** (the last push output seen was `ee03041`, before both). This document uses 0.3 and Stage A design v0.1 as its baseline.

---

## Bottleneck and smallest defensible next step (first, as requested)

- **Bottleneck:** no executable evidence exists. Every Stage A property is design-only, and five data-contract items are UNVERIFIED because nobody has seen one real response from the market-data API:
  - keyless access;
  - the hour alignment of 1Hour bars;
  - the price literal format;
  - gap frequency;
  - pagination.

  One of them (keyless access) **can block Stage A outright**: if the data API needs a key, Stage A needs a credential, which the dispatch prohibits.
- **Smallest defensible next step:** the founder authorizes a bounded **Stage A-0 data probe**.
  - Scope: **one manual, keyless, read-only GET** of BTC/USD 1Hour bars (a 56-hour window), plus one GET of the latest BTC/USD quote, from `data.alpaca.markets`.
  - Raw responses are saved byte-for-byte and hashed.
  - No code beyond the request itself, no credentials, no trading host.
  - It resolves or blocks five items in one step, and it is a precondition for writing correct harness code.
  - **It is not authorized by this dispatch.** It needs a founder decision (FD-1 below).

---

## D1. First-trade dependency map (ordered)

**Statuses:** COMPLETE / OPEN / UNVERIFIED / BLOCKED. "COMPLETE" means **design complete only**, unless it says otherwise.

| # | Prerequisite | Status | Depends on |
|---|---|---|---|
| 0.1 | strategy approved (SMA-20/50 v0.1) | COMPLETE (founder decision) | — |
| 0.2 | strategy formalized with exact arithmetic and edge cases | COMPLETE (design; Stage A design v0.1 D1) | 0.1 |
| 0.3 | crossover semantics at equality (literal vs strict-regime) | **OPEN** (FD-2) | 0.2 |
| 0.4 | signal-to-proposal mapping: EXIT only while holding | COMPLETE (founder text in this dispatch) | — |
| 0.5 | BUY while already long; behaviour with an open or AMBIGUOUS order | **OPEN** (FD-3) | — |
| 0.6 | limit-price and sizing rules | **OPEN** (FD-4) | D5 increments |
| 0.7 | SL-PT-001 spec amendment (D3) reviewed | OPEN (this document → GPT → Gemini) | 0.3–0.6 |
| 1.1 | data probe (Stage A-0) | **OPEN, needs authorization** (FD-1) | — |
| 1.2 | keyless market-data access | **UNVERIFIED** (contradictory docs; resolved by 1.1) | 1.1 |
| 1.3 | bar timestamp convention for 1Hour crypto; alignment; precision; pagination | UNVERIFIED (resolved by 1.1) | 1.1 |
| 1.4 | Stage A harness implementation | **BLOCKED** (not authorized; PT-FD-11 / FD-5) | 0.7, 1.2, 1.3 |
| 1.5 | unit tests and adversarial tests executed (Stage A design D6) | BLOCKED (needs 1.4) | 1.4 |
| 1.6 | independent reconstructor identified | **OPEN** (FD-6) | — |
| 2.1 | first shadow cycle run and recorded | BLOCKED | 1.4, 1.5 |
| 2.2 | first cycle independently reconstructed | BLOCKED | 2.1, 1.6 |
| 2.3 | Stage A milestone M1 (≥ 7 days, ≥ 30 cycles, ≥ 5 injected, reconstruction of ≥ 5 cycles) | BLOCKED | 2.1, 2.2 |
| 2.4 | revision check (re-fetch) observed over cycles | BLOCKED | 2.1 |
| 3.1 | $500 paper account exists | **OBSERVED** (founder screenshot) | — |
| 3.2 | account configuration (buying power 1×, shorting off) | **UNVERIFIED** (not yet observed) | founder dashboard check |
| 3.3 | BTC/USD tradable on paper; increments; minimum; TIF | DOCUMENTED (contradictions, D5) / UNVERIFIED on the account | Stage B probe |
| 3.4 | paper API keys created and held per custody rules | **BLOCKED** (not authorized; FD-8) | FD-8 |
| 3.5 | duplicate-COID and query-by-COID behaviour on paper | UNVERIFIED (Stage C test) | 3.4 |
| 4.1 | G-07 Draft 0.3 reviewed (GPT already reviewed 0.2a; 0.3 not yet reviewed) | OPEN | — |
| 4.2 | minimum G-07 control set for the first order implemented (D6) | BLOCKED | 4.1, FD-5 |
| 4.3 | FD-G16 (no retry), FD-G17 (reconciliation path), FD-G13 (proceed knowing I8 is false) | **OPEN** (founder) | — |
| 5.1 | Stage B authorization | **OPEN** (founder) | 2.3, 3.x, 4.x |
| 5.2 | a genuine BUY signal occurs while all gates hold | **not schedulable** (market-dependent) | 5.1 |
| 5.3 | founder per-order authorization | OPEN (runbook D7) | 5.2 |
| 5.4 | first paper order submitted, reconciled, reconstructed | BLOCKED | 5.3 |

**Critical path:** 1.1 → 1.4 → 1.5 → 2.1 → 2.2 → 2.3 → 5.1 → (wait for a signal) → 5.4. **The founder decisions 0.3, 0.5 and 0.6 must close before 1.4.**

---

## D2. Founder decision register (only genuine founder decisions)

| ID | Decision | Why it is the founder's | Proposed default |
|---|---|---|---|
| **FD-1** | authorize the Stage A-0 data probe (one keyless read-only fetch) | it is a connection to Alpaca's data host; the current dispatch prohibits broker connection | authorize |
| **FD-2** | crossover at equality: literal (as approved) vs strict-regime | it changes the strategy's signals (the touch case) | literal, as approved, unless the founder prefers to suppress touch re-entries |
| **FD-3** | BUY while long; any signal while an order is open or AMBIGUOUS | strategy and risk semantics | BUY while long → NO_ACTION. While an order is open or AMBIGUOUS → **no new proposal**; BLOCKED_OPEN_ORDER is recorded (an EXIT with an open BUY remainder → a governed CANCEL proposal first; the EXIT is evaluated next cycle) |
| **FD-4** | limit price and sizing | trading policy | BUY at the ask; EXIT at the bid (taker); size per Stage A design §1.6 with a **0.25% taker fee** (now DOCUMENTED, D5) |
| **FD-5** | authorize the Stage A harness build (PT-FD-11) | implementation authority | after FD-1 to FD-4 |
| **FD-6** | the independent reconstructor (not Claude, not the harness author) | independence assignment | GPT-authored script run by the founder, or a human; **not the harness author** |
| **FD-7** | where the harness runs, and the cycle trigger | operational | the founder's PC, manual trigger, for the first cycles |
| **FD-8** | paper-key custody for Stage B (later) | credential authority | environment variables, executor-only user; **not before Stage B authorization** |
| **FD-9** | Stage B authorization, including **FD-G13** (proceed knowing G7-I8 is false on the founder's machine), **FD-G16** (no same-COID retry; GPT and Claude recommend no), **FD-G17** (reconciliation path) | execution authority; risk acceptance | decided at Stage B entry, not now |

**Not founder decisions (technical; resolved by research or the probe):**
- keyless access;
- the timestamp convention;
- increments and minimums;
- TIF support;
- fee rate;
- COID semantics.

These are tracked in D5.

---

## D3. Specification amendment (proposed SL-PT-001 v0.2 changes; the baseline is not overwritten)

| ID | Section of v0.1 | Change |
|---|---|---|
| A-1 | §1.1 Intelligence | replace "#0: a deterministic rule" with "**#0: SMA-20/50 v0.1** as defined in the Stage A design v0.1 D1 (exact-sum comparison; literal or strict-regime per FD-2)" |
| A-2 | §1.1 Instruments | BTC/USD only; ETH/USD deferred (founder) |
| A-3 | §3 lifecycle | add the pre-proposal states: NO_DECISION:<reason>, HOLD, NO_ACTION, BLOCKED_OPEN_ORDER, so that the lifecycle distinguishes **data failure / no signal / signal without proposal / proposal** |
| A-4 | §4 R2 | TIF: **GTC only** for the first order, with Sentinel cancelling at TTL. **IOC as an alternative** (D5: documented support for gtc/ioc; fok support is contradictory). FD-4 can pick IOC to avoid resting orders |
| A-5 | §4 R10 | increments for BTC/USD: price $1, quantity 0.0001, minimum 0.0001 (DOCUMENTED in the support table). **Contradicted** by a docs statement that the USD-pair minimum is 1/price. The harness must read the asset metadata at Stage B and **refuse if it differs** from the policy file |
| A-6 | §4 new R15 | **position-state rule:** EXIT only while the shadow (Stage A) or reconciled (Stage B) position is > 0. EXIT quantity = the entire reconciled position, **after fees** (fees are deducted in the received asset on buys; DOCUMENTED) |
| A-7 | §4 new R16 | **open or AMBIGUOUS order rule** (FD-3): no proposal while any order for the instrument is open, partially filled, or AMBIGUOUS |
| A-8 | §5 fees | replace "ASSUMED 0.25%" with "**DOCUMENTED tier 1: maker 0.15%, taker 0.25%**; paper application UNVERIFIED (OQ-PT-1)". A limit at the ask/bid is marketable, so taker |
| A-9 | §6 shadow procedure | replace steps 1 to 4 with the Stage A design v0.1 D4 walkthrough (exact candle rules, settle margin, failure states, boundary self-check) |
| A-10 | §7 paper execution | apply the G-07 Draft 0.3 changes PT-A1 to PT-A6: the polling executor (no auth_id path), LP-PRESEND with δ_send, the context-bound authorization, the reconciliation path per FD-G17, the I2 independent decode via the echoed order, and per-test records |
| A-11 | §7 retry | add the **FD-G16 (a)** rule, if adopted: an ambiguous submission is resolved by query-by-COID only, and **never resubmitted** |
| A-12 | §0 / §1.1 leverage | add: BTC/USD is DOCUMENTED as `marginable: false`, `shortable: false` at the asset level. This is a venue-side control **for this pair**, distinct from the account-level multiplier. Both are **UNVERIFIED on the account** until observed |
| A-13 | §11 decisions | close PT-FD-1 (Alpaca paper: confirmed by the founder's actions), PT-FD-2 ($500 account: OBSERVED), PT-FD-3 (BTC/USD), PT-FD-4 (SMA-20/50). PT-FD-7, PT-FD-10 and PT-FD-11 stay open (→ FD-8, FD-6, FD-5) |
| A-14 | stale language | v0.1 §0: "PT-FD-1 asks the founder to confirm" → resolved. §1.1 "Intelligence #0 rule: PT-FD-4" → resolved. "Stage B … local simulator" never appears (correct). The "Trade Evidence Record" / "Trade Event Record" naming is unified to **TER** |

**Assumptions previously at risk of being read as facts:**
- the fee rate (now DOCUMENTED, still unverified on paper);
- the account at 1× (UNVERIFIED);
- containment by account size (CONDITIONAL; G-07 Draft 0.3 §6);
- keyless data (UNVERIFIED).

---

## D4. Minimum Stage A build plan (for FD-5; not authorized)

| Component | Inputs | Outputs | Acceptance (to be shown by execution, not claimed) |
|---|---|---|---|
| C1 boundary self-check | environment; HTTP allowlist config | a PASS/FAIL record | an allowlist containing only `data.alpaca.markets`; any Alpaca trading credential variable present → FAIL; adversarial tests X8 and X9 executed |
| C2 fetcher | symbol, window, T_d | raw bytes, SHA-256, request metadata | raw bytes stored before parsing; the hash recorded |
| C3 validator | raw bars, quote, T_d | a data_state (VALID or a failure) | U5 to U8, U11 to U13 executed against synthetic fixtures |
| C4 decision core (a pure function) | 51 validated candles, previous state | S20, S50, D(k), D(k−1), signal | U1 to U4e and U10 executed; **exact decimal arithmetic; no float in the path** |
| C5 mapper and policy | signal, shadow ledger, quote, the P-0.1 file | proposal or none; rule results; decision | X1 to X7 executed; U14 |
| C6 shadow ledger and lifecycle | decisions | ledger state; SHADOW_EXPIRED events | ledger invariants: cash ≥ 0, btc ≥ 0, reservations released at the terminal state |
| C7 event log | events | `events.jsonl` with a hash chain | the chain verifies; editing a past event breaks verification (test) |
| C8 reconstruction script (**separate author**, FD-6) | artifacts plus Stage A design D1 and D2 only | recomputed values; a diff report | it matches the TER for cycle 1, or reports a finding |

**Manual:** cycle trigger; commit and push; running the reconstruction.
**Deferred:** scheduler; ETH; LLM; shadow-outcome resolution (Scoreboard A); the re-fetch check (from cycle 2).

**Stage A completion evidence (Stage 2 of the dispatch; M1 criteria from Spec v0.1 §9 preserved):**
- deterministic replay (U9 and U10);
- independent reconstruction of at least 5 random cycles;
- hash-chain and artifact integrity;
- missing-data and stale-data rejection (executed);
- duplicate events and duplicate proposals: the same cycle replayed is never appended twice (U9), and a duplicate proposal_id is rejected;
- exposure limits enforced (X4 and X5);
- invalid or contradictory position states (shadow ledger negative, or an EXIT with no position) are rejected and recorded;
- at least 5 injected proposals;
- **every unexplained discrepancy is a stop condition: Stage A pauses until it is explained.**

**What Stage A results do not establish:** anything about Alpaca order handling, G-07 mediation, credential isolation, broker idempotency, or fill realism (G-07 Draft 0.3 §9 credit rule).

---

## D5. Paper venue verification report

| Item | DOCUMENTED (source) | OBSERVED | UNVERIFIED / to test |
|---|---|---|---|
| Paper account | $100k default; any starting amount at reset/creation (Alpaca docs, earlier) | **$500 account exists** (founder screenshot) | — |
| Account configuration | `max_margin_multiplier` "1"/"2"/"4"; `no_shorting`; accounts < $2,000 default to 1.0 (broker docs) | — | **actual buying power and shorting on the $500 account** (founder check); whether the trading key can change them (assume yes) |
| BTC/USD tradable; margin and short | the asset sample shows `marginable: false`, `shortable: false`, `fractionable: true` | — | the paper account's asset response (needs a key, so Stage B) |
| Minimum and increments | support table: minimum 0.0001, price increment 1, quantity increment 0.0001. **Docs also: the USD-pair minimum is 1/price. Contradictory.** Maximum 9 decimals | — | the actual asset metadata at Stage B; a refusal if it differs |
| Order types | market, limit, stop_limit | — | limit acceptance on paper |
| TIF | gtc and ioc (crypto orders doc); **fok also listed on one support page. Contradictory** | — | use gtc or ioc only |
| Per-order limit | $200k notional per order | — | irrelevant at $150 |
| Fees | tier 1: maker 0.15%, taker 0.25%; the buy fee is taken in the received asset | the forum report earlier (a 1 ETH buy → 0.9975) | **whether paper applies fees** (OQ-PT-1) |
| Fill model (paper) | fills at NBBO quotes (buys at the ask, sells at the bid); random partial fills about 10% of the time (Alpaca forum staff) | — | observed on the first orders |
| Order status / cancel | orders are queryable by id and client order id; cancel endpoint | — | cancel semantics on crypto paper |
| Client order ID | `client_order_id` up to 128 characters; query by COID endpoint exists | — | **duplicate-COID behaviour** (rejection vs idempotent return): a Stage C test; not to be generalized to live |
| Ambiguous submission | none specific | — | query-by-COID after a timeout: a Stage C test |
| Market data without credentials | SDK docs: "No keys required for crypto data"; REST reference lists 401 | — | **the Stage A-0 probe** |
| Credential separation | paper keys separate from live keys; Trading API keys authenticate by key, not IP (unofficial sources); no per-key scoping found | — | read-only key availability (G-07 FD-G17) |
| Broker-enforced limits | the asset flags above; the account multiplier | — | **not to be treated as enforced** until observed (dispatch §3 Stage 3) |

---

## D6. G-07 readiness matrix for the first paper order (G-07 Draft 0.3 numbering)

| First-order requirement | G-07 | Necessary for the first order? | Testable on paper? | Gap / status |
|---|---|---|---|---|
| authorization created with a TTL and context binding | I9, §2 | **yes** | yes (local) | design only |
| founder per-order approval bound to auth_id and payload hash | (SL-PT-001 runbook) | **yes** (first order) | yes | design only |
| executor polls; no requester trigger path | §2 | **yes** | partly (local) | design only |
| single-use consumption | I3 | **yes** | yes (local; Stage C) | design only |
| validity at release (LP-PRESEND, δ_send) | I4 | **yes** | yes (local injection) | design only; δ_send not set (FD-G18) |
| submitted == approved (plus the independent decode via the echoed order) | I2 | **yes** | **yes (paper API)** | design only |
| ambiguous outcome handling (query by COID; no retry) | I6, I10 | **yes** | yes (paper, injected timeout) | FD-G16 open; COID semantics unverified |
| audit lineage (LP-WAL before send) | I7 | **yes** | yes (local) | design only; FD-G4 open |
| reconciliation (L-1, L-2, L-3) | I10, §5 | **yes** | yes (paper records) | FD-G17 open (independent read path) |
| non-bypassable egress | I5 | desirable | **no**: the founder's machine is non-isolated | **known noncompliant**; accepted only via FD-G13 |
| no unmediated authority | I8 | (an acceptance condition) | negative tests only (expected: bypass succeeds and is detected) | **known false**; FD-G13 |
| credential custody | I8, FD-G1 | yes (minimal: executor-only environment) | partly | FD-8 |
| alternate paths (dashboard, second key) | I8 | detection required | yes (Stage C: expected success, then detection) | reconciliation path (FD-G17) |

**Necessary but unprovable on the founder's machine:** I5, I8, and resistance to host compromise. **The first paper order can proceed only as an explicitly accepted noncompliant deployment (FD-G13).**

---

## D7. First paper trade runbook (for eventual use; executes nothing now)

**Preconditions:**
- Stage A M1 complete, with independent reconstruction;
- Stage B authorized by the founder (FD-9);
- paper keys in place per FD-8;
- account configuration **observed** at 1× with shorting off, and recorded;
- asset metadata read and matching the policy file;
- G-07 minimum controls (D6 "yes" rows) implemented **and their local tests executed**;
- no open or AMBIGUOUS order;
- the reconciliation path working (FD-G17);
- the Stage C tests for query-by-COID and duplicate COID **executed** on paper.

| Step | Action | Evidence | Stop conditions |
|---|---|---|---|
| 1 | the hourly cycle runs as in Stage A | a TER | any data failure → NO_DECISION; **if the signal is HOLD or NO_ACTION, stop: no trade this cycle. There is never a forced entry** |
| 2 | **signal confirmation:** recompute D(k−1) and D(k) from the stored artifacts with the independent reconstruction script **before** approval | a reconstruction diff (must be empty) | any difference → stop; finding |
| 3 | policy and exposure: R1 to R16 on the reconciled (not shadow) ledger | rule results | any FAIL → REJECTED; stop |
| 4 | authorization record: auth_id; context (executor, account, venue, action); payload hash; not_before; expires_at = issued + 5 min | the K3 record | — |
| 5 | **founder approval:** the founder reviews the TER and the reconstruction diff, and records APPROVE(auth_id, payload_hash) **within the TTL** | an approval event (who, when, hash) | TTL lapses → EXPIRED; stop (a new cycle is needed) |
| 6 | order construction by the executor from K3: limit; qty on the 0.0001 increment; price on the $1 increment; TIF per FD-4; COID = auth_id | the canonical payload | the round trip or the policy re-check fails → stop |
| 7 | LP-CONSUME; LP-WAL; LP-PRESEND (validity, configuration identity, δ_send) | WAL records | any failure → NOT_SENT; stop |
| 8 | submit once | the raw request and response | — |
| 9 | **ambiguous response** (timeout, error, no body): state AMBIGUOUS → query by COID → found: continue; not found: **stay AMBIGUOUS, no resubmission** (FD-G16 a), and the founder is notified | query records | AMBIGUOUS unresolved → halt new authorizations |
| 10 | track to the terminal state; TTL cancel of the remainder | raw updates | — |
| 11 | reconcile: L-1 (approved vs echoed order); L-2 (ledger vs Alpaca positions and activities, exact after fees); L-3 (every Alpaca order ↔ one auth_id) | a reconciliation record | **any unexplained discrepancy → stop condition** |
| 12 | final TER; push; **independent reconstruction** of the whole order lifecycle from artifacts | the reconstruction report | a finding → it stays open until explained |

**If the system is ready and no BUY signal exists:** keep running hourly shadow cycles under Stage B rules (no orders) until one occurs. **The milestone waits for the market.** That expected wait is not schedulable and is not a defect.

---

## D8. Go / No-Go recommendation

- **No-Go** for the Stage A build, Stage B, and any order. Founder decisions FD-2 to FD-4 are open, the five data-contract items are unverified, and no code or test exists.
- **Go (recommended) for one bounded action: FD-1, the Stage A-0 data probe.** It is the single most important next action because:
  - (a) it is the only item that can **block** Stage A outright (if data needs a key);
  - (b) it resolves five UNVERIFIED items at once;
  - (c) the harness design depends on its results (timestamp convention, precision, pagination);
  - (d) it carries no trading capability, credential or order risk.
- **In parallel, at no execution risk:** the founder closes FD-2, FD-3 and FD-4 (strategy semantics) and FD-6 (who reconstructs). With those done, FD-5 (build authorization) becomes a well-defined decision.

*End of D1 to D8. Planning only. Nothing implemented, fetched, tested or traded.*
