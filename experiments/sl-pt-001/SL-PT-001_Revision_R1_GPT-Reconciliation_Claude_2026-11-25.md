# SL-PT-001 Revision R1: reconciliation of the GPT hostile review (5-minute revision)

**Date:** 2026-11-25 | **Author:** Claude | **Responds to:** "GPT hostile review: SL-PT-001 5-minute revision" (2026-11-25)
**Scope (per GPT's instruction):** a targeted revision. **Nothing is broadened, and G-07 is not redesigned.** Founder decisions stay open. The Stage A / Stage B separation is unchanged.
**Amends:** Amendment SMA-20/50 v0.2 (`SL-PT-001_Amendment_SMA20-50_v0.2_5Min`), Stage A Design v0.1, First-Trade Readiness D1 to D8, and (one predicate only) G-07 Draft 0.3. None is overwritten.
**Classification:** specification. Nothing is implemented. The only executed step so far is the FD-1 probe (separate report, `f6642894…`).
**Labels:** DERIVED / OBSERVED / DOCUMENTED / ASSUMED / UNVERIFIED.

## 0. Disposition

| GPT ID | Finding | Disposition | § |
|---|---|---|---|
| T-1 | the approval deadline and the authorization TTL were conflated | **ACCEPTED**: separate clocks defined | 1 |
| T-2 | the quote may go stale during approval | **ACCEPTED**: a fresh quote at authorization, LP-CONSUME and LP-PRESEND | 1 |
| T-3 | cycle overrun and duplicate processing | **ACCEPTED**: cycle identity, one active cycle, fail-closed overrun | 2 |
| A-1 | founder approval is not a G-07 predicate | **ACCEPTED**: a mandatory approval record becomes an LP-CONSUME eligibility condition (G-07 amendment A0.3-13, one predicate) | 3 |
| A-2 | the first trade cannot demonstrate full G-07 mediation | **ACCEPTED**: required claim language | 6 |
| D-1 | conflicts with v0.1 | **ACCEPTED**: explicit supersession table. **Correction:** the account inconsistency is partly resolved (the $500 account is OBSERVED; the old $100k figures described the earlier account); 1× and shorting remain UNVERIFIED | 4 |
| D-2 | one probe ≠ recurring reliability | **ACCEPTED**: already reflected in the probe report (one probe; nothing generalized). GPT reviewed before the probe ran | — |
| M-1 | the reduced milestone supports narrow claims only | **ACCEPTED**: claims table | 5 |
| M-2 | 5 injections ≠ coverage | **ACCEPTED**: the runtime minimum is separated from the test-suite coverage requirement | 5 |
| R-1 | reconstruction contamination | **ACCEPTED**: freeze-then-blind protocol | 5 |
| — | FD-G18 missing from the Stage B register | **ACCEPTED** | 7 |
| — | unchecked boxes in the dispatch | **ACCEPTED**: FD-1 recorded as **exercised**; FD-5 stays conditional, with its condition defined | 7 |
| — | D1 dependencies; D7 STOP conditions | **ACCEPTED** | 6 |

**Rejected:** none.

---

## 1. Timing contract (T-1, T-2; replaces the single 180 s window of amendment v0.2)

**Clocks:** all instants are UTC from the harness clock. Offset is measured per G7-A3 and recorded; **if the offset cannot be measured, there is no proposal**.

| Symbol | Definition | Value |
|---|---|---|
| close_t | end of the candle (start + 5 min) | — |
| T_d | the decision instant for that candle | close_t + 60 s (settle) |
| `proposal_created_at` | when the signal and proposal are computed | ≈ T_d |
| `approval_deadline` | the last instant the founder may approve | proposal_created_at + **120 s** |
| `authorization_issued_at` | when K3 issues the authorization, **only after a valid approval** | the approval instant (≤ approval_deadline) |
| `expires_at` | authorization expiry | min(authorization_issued_at + **60 s**, proposal_created_at + **180 s**) |
| LP-PRESEND bound | G-07: `now ≤ expires_at − δ_send` | δ_send per FD-G18 |
| `quote_valid_at` checks | a **new** quote, ≤ 15 s old, at: (a) proposal creation, (b) authorization issuance, (c) LP-CONSUME, (d) LP-PRESEND | 15 s |

**Rules (DERIVED):**
1. **No approval by the deadline → the proposal is EXPIRED_UNAPPROVED.** No authorization is ever issued for it.
2. **Every fresh-quote check re-evaluates** R4 (freshness), R5 (±1% band against the *new* mid) and the R6/R7 affordability and cap rules at the *new* price.
   - Any failure → stop. No re-pricing is allowed: **the approved limit price is immutable**.
   - If the band or the affordability check fails at the new quote, the authorization dies.
3. **The strategy signal never reads the quote.** It is a pure function of completed candle closes (§2; test U18).
4. **Hard ceiling:** everything for a proposal is finished by proposal_created_at + 180 s, which is before the next decision instant (T_d + 300 s).

**Stage A:** there is no approval and no authorization. The shadow lifecycle records PROPOSED → (policy result) → SHADOW_EXPIRED at proposal_created_at + 180 s. The approval clock is **not simulated** in Stage A.

---

## 2. Cycle identity, overrun, missing bars and revision (T-3; GPT §3)

- **Cycle identity:** cycle_id = (instrument, `t` of the latest completed candle). It is **unique**: a cycle_id already in the log is never processed again (U9 replay protection extends to this).
- **One active cycle per instrument** (a lock file or an in-process mutex). A second invocation while one is active → CONCURRENT_INVOCATION, recorded; it exits.
- **Overrun:** a cycle not finished by its next T_d (T_d + 300 s) → CYCLE_OVERRUN recorded. **Any proposal from that cycle is blocked.**
  - The next cycle processes **only the newest completed candle**; skipped candles are recorded as SKIPPED.
  - It never processes two candles in one run, and never back-fills decisions.
- **Expected candle:** at T_d, expected `t` = floor_5min(T_d − 60 s) − 5 min (OBSERVED in the probe: the forming bar is returned and must be excluded; P-3).
  - Expected bar absent → DATA_GAP (no interpolation).
  - Duplicate `t` with identical content → one copy kept, with a note.
  - Different content → DATA_CONFLICT.
- **Revision of an accepted bar:**
  - From cycle 2 onward, each cycle re-fetches the previous cycle's window and compares canonical bytes per bar.
  - A changed bar → SOURCE_REVISION event. **The original bytes are kept; nothing is replaced.**
  - **Effect:** (a) Stage A: the earlier TER is annotated through a new event; (b) Stage B: any **pending** proposal or authorization whose 51-candle input contains the revised bar is **invalidated**.
  - **Settle is a policy, not proof of finality** (GPT; adopted).

---

## 3. Founder approval as a mandatory authorization predicate (A-1)

**G-07 amendment A0.3-13 (proposal; one predicate, not a redesign).**

**Approval record** (append-only, in K3), bound to:
- proposal_id and cycle_id;
- strategy id and version; the input_snapshot_sha256;
- instrument, side, quantity, limit price, TIF;
- the policy hash and configuration hash;
- account, venue, executor_id;
- approved_at and approval_deadline;
- **approver identity** (the founder, authenticated by a mechanism defined at Stage B; **UNVERIFIED** until then).

**Rules:**
- K3 issues an authorization **only if** there is an approval record whose bound fields **exactly** match the proposal and which was recorded no later than approval_deadline.
- Any difference in a bound field → no authorization.
- At LP-CONSUME, the eligibility check additionally requires that the matching approval record still exists unrevoked.

**Falsifier:** an ACTIVE authorization with no matching, timely approval record.

**Scope:** Stage B for SL-PT-001; it is a G-07 predicate (I9 provenance gains the approval reference). **Stage A has no approvals.**

---

## 4. Explicit supersession of SL-PT-001 v0.1 (D-1)

| v0.1 requirement | Superseded by | Status |
|---|---|---|
| hourly bars and hourly cycle (§1.1 cadence; PT-FD-6) | 5Min bars and cycles (amendment v0.2) | **SUPERSEDED** |
| BTC/USD **and** ETH/USD (§1.1; PT-FD-3) | BTC/USD only | **SUPERSEDED** (ETH deferred) |
| R13 authorization TTL 5 min | §1 clocks (approval 120 s; authorization ≤ 60 s; ceiling 180 s) | **SUPERSEDED** |
| R4 data freshness 60 s | quote ≤ 15 s at four checkpoints (§1) | **SUPERSEDED** |
| M1-1 "≥ 7 days; ≥ 30 cycles; ≥ 5 injected per week" | §5 milestone | **SUPERSEDED** |
| §6 adversarial injection "≥ 5 per week" | ≥ 5 total at runtime, **plus** full test-suite coverage (§5) | **SUPERSEDED** |
| §0 "$100,000 equity / $200,000 buying power" | describes the **earlier** account. The $500 account is OBSERVED (founder screenshot); its buying power and shorting setting are **UNVERIFIED**; Stage B dependency | **CLARIFIED** |
| §2.2 field "freshness_s" and the hourly settle | Stage A Design D2 plus §2 above | **SUPERSEDED** |
| intelligence #0 "PT-FD-4 founder's choice" | SMA-20/50 v0.2 | **RESOLVED** |

**Rule:** where v0.1 and a later amendment conflict, **the later amendment governs**. v0.1 acceptance criteria that are not listed here (M1-2 to M1-7) **remain in force**.

---

## 5. Milestone, claims and independence (M-1, M-2, R-1)

**The consecutive-cycle counter (adopting GPT's strict rule):**
- every scheduled 5-minute candle must be accounted for by exactly one cycle record;
- the counter **increments** on a cycle that completes with any terminal state other than a failure (HOLD, NO_ACTION, REJECTED or SHADOW_EXPIRED);
- the counter **resets to 0** on NO_DECISION (any data failure), CYCLE_OVERRUN, SKIPPED, CONCURRENT_INVOCATION or BOUNDARY_FAIL;
- **M1-1 is met at 30.**

*Consequence (stated):* data-failure frequency directly lengthens the run. A correctly *detected* failure is still not a *successful* cycle.

**Injection vs coverage:**
- **≥ 5 injected proposals at runtime** is a runtime acceptance count.
- **Separately**, before any live-data cycle, the **unit and adversarial test suite** must contain at least one executed test per rule R1 to R16 (pass and fail sides) and per boundary condition listed in Stage A Design D6 plus U17 to U21 below.
- Five runtime injections are **not** coverage.

**Claims M1 can support** (when met, and only these):
- the harness processes distinct completed candles;
- the decision computation is deterministic on recorded inputs;
- the specified stale and malformed data were rejected in the cycles observed;
- the event record is complete and reproducible for the sampled cycles;
- the injected proposals were rejected by the intended rules;
- an independent reviewer reconstructed the sample.

**Claims M1 cannot support:**
- SMA-20/50 profitability or significance;
- returns or drawdown;
- robustness across regimes;
- reliability over days;
- the truth of market data;
- **any G-07 execution-enforcement property.**

**Thirty cycles are not thirty trades; all may be HOLD.**

**Blind reconstruction protocol (R-1; FD-6 default with safeguards):**
1. Freeze the specification set: the Stage A Design, amendment v0.2 and this R1. Record its SHA-256 list in the repository **before** the harness exists.
2. GPT writes the reconstruction script from the frozen set only. **No access to the harness code, tests or outputs.** It records its script's SHA-256 **before** seeing any TER.
3. The founder runs it against the artifacts of 5 random cycles (chosen by a seeded draw recorded in advance).
4. Any difference is a finding. Neither side's output is presumed correct.

---

## 6. D1 additions, D7 STOP table, claim language (A-2)

**D1 additions:**
- (a) R1 reconciled; critical findings resolved or explicitly founder-accepted;
- (b) Gemini review received and reconciled;
- (c) specification freeze plus GPT script hash (§5);
- (d) the test suite executed with evidence;
- (e) a **Stage A exit report**;
- (f) Stage B implementation **separately authorized**;
- (g) **G-07 minimum controls implemented** (Draft 0.3 is design-only, so a paper order cannot exercise an unimplemented boundary) **with their local tests executed**;
- (h) FD-G13, FD-G16, FD-G17 and **FD-G18** decided.

**D7 STOP conditions** (each one: stop, record, no new authorization until resolved):

| Condition | Where detected |
|---|---|
| missing, conflicting or revised candle in the signal window | cycle validation / revision check |
| stale quote (> 15 s) at any checkpoint | §1 checks a to d |
| clock offset unmeasured or > σ | pre-flight (G7-A3) |
| cycle overrun, skipped candle, concurrent invocation | §2 |
| approval missing or late; authorization expired | §1, §3 |
| any change to approved parameters (including price re-rounding) | approval binding (§3) |
| open, partial or AMBIGUOUS prior order; unresolved authorization | R16 |
| LP-PRESEND failure | G-07 §1 |
| missing durable LP-WAL record | G-07 I7 |
| submission timeout or uncertain response → query by the original COID only; **no replacement, no new authorization** until resolved | G-07 I6, I10 |
| an unmatched broker order in reconciliation | L-3 |

**Required claim language** for the first paper trade report:

> "A paper order was submitted through the Sentinel workflow under recorded approval and reconciled against Alpaca paper records. This deployment does not satisfy G7-I5 or G7-I8; it does not demonstrate that external actions on the account can occur only through Sentinel."

---

## 7. Register and dispatch corrections

- **FD-1:** recorded as **exercised** (probe completed, 2026-11-26T03:13Z; report `f6642894…`).
- **FD-5 condition defined:** the harness build may begin only when:
  - (a) R1 and the Gemini reconciliation are issued;
  - (b) every critical finding (T-1 to T-3, A-1, A-2, and any from Gemini) is either resolved in the specification or **explicitly accepted in writing by the founder**;
  - (c) the specification freeze is recorded (§5).
- **Stage B decision register:** FD-9 now includes FD-G13, FD-G16, FD-G17 and **FD-G18** (the time source, the skew bound σ, δ_send).
- **FD-4 refinement (GPT; proposed default, not decided):**
  - the $150 cap = the **maximum total reserved spend including fees**;
  - quantity rounded **down** to the venue increment;
  - the price is from a fresh quote at authorization issuance.
  - **Plus probe finding P-2:** displayed top-of-book size was about $60. The founder should decide whether a BUY that would exceed the displayed best-ask size is acceptable, or must be capped at it.
  - The fee is a DOCUMENTED schedule; whether it applies on paper, and as maker or taker, is UNVERIFIED.

## 8. New tests (added to Stage A Design D6)

| ID | Test | Expected |
|---|---|---|
| U17 | the response includes the forming bar | it is excluded and recorded (probe P-3) |
| U18 | **quote invariance:** identical candles, varied quotes | identical S20, S50, D and signal |
| U19 | overrun: cycle N still running at T_d(N+1) | CYCLE_OVERRUN; N's proposal blocked; N+1 processes only the newest candle; the counter resets |
| U20 | revision: a bar inside a pending proposal's window changes on re-fetch | SOURCE_REVISION; original bytes kept; (Stage B) the pending proposal is invalidated |
| U21 | an authorization without a matching approval (Stage B fixture) | refused at issuance and at LP-CONSUME |
| U22 | approval after approval_deadline | EXPIRED_UNAPPROVED; no authorization |
| U23 | the quote at LP-CONSUME moves the mid so that the approved limit is outside ±1% | the authorization dies; no re-pricing |

*End of R1. Specification only.*
