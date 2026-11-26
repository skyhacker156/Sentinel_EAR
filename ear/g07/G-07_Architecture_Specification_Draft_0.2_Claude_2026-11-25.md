# G-07 Architecture Specification, Draft 0.2 (amendment to Draft 0.1)

**Date:** 2026-11-25 | **Author:** Claude, Specification Lead | **Dispatch:** "G-07 Review Synthesis and SL-PT-001 Integration" (2026-11-25)
**Classification:** ARCHITECTURAL DESIGN ONLY. Not implemented, not tested, not frozen. **No code, credentials or orders are created by this document. SL-PT-001's authorization status is unchanged.**
**Form:** an **amendment**. Draft 0.1 (`ear/g07/G-07_Architecture_Specification_Draft_0.1_Claude_2026-11-24.md`, SHA-256 `55141ae6…`) stays in force wherever this document does not replace it. Every replacement is marked **[A0.2-n]**, so the record of what changed stays visible.
**Labels:** DERIVED / OBSERVED / ASSUMED / CONDITIONAL / UNVERIFIED / UNBOUNDED. **Nothing is COMPUTED.**

## 0. Inputs and their limits (read first)

| Input | Received? | Consequence |
|---|---|---|
| Dispatch text (the four failure classes; the G7-I8 text; the three assurance layers; the SL-PT-001 map; the matrix columns) | **yes** | used verbatim |
| Hostile review record, including **G7-I1 to G7-I7** and its attack-surface inventory (31 scenarios plus F.1 to F.3 in the earlier dispatch) | **no** (requested twice; the two attachments to this dispatch were the same file) | **G7-I1 to G7-I7 below are Claude's reconstruction** from the four failure classes and Draft 0.1. They are labelled **RECONSTRUCTED** and are subject to replacement by the review text wherever they differ. **The completeness of the matrix against the review's inventory cannot be certified** (§5, row Z) |
| Founder observations, 2026-11-25 | yes | a $500 Alpaca paper account exists (OBSERVED, screenshot); MFA is enabled on the Alpaca login (OBSERVED, founder statement); buying power and multiplier are **not yet observed** |

---

## 1. [A0.2-1] Three assurance layers (replaces Draft 0.1 §1's single verdict)

| Layer | What it claims | What it does **not** claim | Where it is enforced | Its own compromise assumption |
|---|---|---|---|---|
| **A. Authorization correctness** | dispatch happens only for an authorization that was: (a) produced by correct policy evaluation on current state; (b) current (unexpired, unrevoked, not stale); (c) consumed exactly once, atomically; (d) bound to exactly the approved parameters | that nothing else can act on the account | Consumption Authority K3; gate checks in K5 | K3 and K5 code correct and uncompromised |
| **B. Execution mediation** | every consequential action on the account passes through the enforcement boundary K5; nothing outside K5 holds a working credential or path | correctness of what K5 lets through (that is layer A) | **the deployment** (OS, credential custody, network egress) **and the broker** (credential scope, IP binding, human channels) | the boundary host and its administrators are uncompromised. **This assumption is outside the application's control** |
| **C. External outcome knowledge** | submission, acceptance, rejection, partial fill, cancellation and *ambiguity* are separately represented; retries never create uncontrolled duplicates; reconciliation against the broker's records | exactly-once external execution | K5 dispatch machine (Draft 0.1 §13 B); the reconciler with an independent read path | broker records are complete and truthful (B-STMT) |

**Rule L-1:** a result in one layer is never cited as evidence for another. In particular, a passing single-use test (A) says nothing about bypass (B) or duplicates at the venue (C). **DERIVED.**

---

## 2. [A0.2-2] The direct answer (dispatch §7)

> *If application-level authorization logic is correct, but the execution adapter, the host, or an alternate credential path is compromised, what prevents an unauthorized consequential external action?*

| Compromised element | What prevents it | Kind | Status for Alpaca / SL-PT-001 |
|---|---|---|---|
| **Adapter only** (no broker credential, not on the gate host) | the adapter has no credential (credential isolation) **and** no route to the broker (egress control) | **deployment property** (OS and network), not application logic | **Not established in SL-PT-001**: the founder's machine runs everything. **UNVERIFIED** generally |
| **Gate host** (K5, the credential holder) | **nothing inside Sentinel.** Only broker-side limits on what the credential can do, and only for actions outside those limits | **environmental** (broker) | Alpaca's Trading API authenticates by key, not source IP [S1, S2], so a stolen key works from anywhere. No per-key permission scoping was found (**UNVERIFIED**). **The remaining bound is the account itself:** a segregated $500 cash account with margin multiplier 1 and shorting off limits loss to roughly the account value (CONDITIONAL on that configuration, which is not yet observed) |
| **Alternate credential path** (a second API key; the dashboard login; key-generation rights) | broker-side credential inventory and human-channel controls (MFA; no shared logins) | **environmental and procedural** | MFA: OBSERVED on. Key inventory: **not yet performed**. The dashboard can place orders by hand, so the bypass **exists by design** in SL-PT-001 and is *detected* (reconciliation L-3), not prevented |

**Narrowed claim (DERIVED):**
- G-07 can **prevent** unauthorized consequential actions only by **unprivileged components** (strategy, intelligence, adapter), and only **in a deployment where credential isolation and egress control are actually in place and tested**.
- Against compromise of the boundary host, the broker credential or the account's human channels, G-07 provides **detection** (reconciliation) and relies on **broker-side and account-level containment**.
- For Alpaca's Trading API, the available broker-side containment appears to be **account segregation, account size, the margin multiplier and shorting configuration**, not key-level restrictions. Loss under compromise is therefore **bounded by the account's assets and configuration**, and is **UNBOUNDED** where the account permits more.

---

## 3. [A0.2-3] Invariant register G7-I1 to G7-I8

**Columns:**
- *Origin* says whether the text is RECONSTRUCTED (Claude) or GIVEN (dispatch).
- *Class* is one of: derived requirement (D-REQ), assumption (ASM), or environmental property (ENV).
- *Draft 0.1 map* links to the S-invariants, which remain as sub-requirements.

| ID | Statement | Layer | Origin | Class | Enforcement mechanism | Testable by | Cannot be established by application tests alone | Draft 0.1 map | Status |
|---|---|---|---|---|---|---|---|---|---|
| **G7-I1** | No consequential action is dispatched unless an authorization was issued by the current policy version, evaluated on state that includes every item received before the issuance point | A | RECONSTRUCTED | D-REQ | K3 evaluation inside the fold; the policy hash bound into the record | replaying a decision from logged inputs; injected policy and state changes | that the policy expresses the intended risk limits (a governance question) | S01; EAR Π | DERIVED; UNVERIFIED |
| **G7-I2** | Each authorization is consumed at most once, atomically. Consumption never reverts, including after a crash or a restore | A | RECONSTRUCTED | D-REQ | the K3 single-use transition (LP-CONSUME); the restore-as-governance rule | concurrency, crash and restore tests | that storage never rolls back silently (ASSUMED) | S02, S03 | DERIVED; CONDITIONAL |
| **G7-I3** | No dispatch begins after expiry, after revocation, or after a state change that would deny it under G7-I1 (the stale-authorization / TOCTOU boundary is LP-DISPATCH) | A | RECONSTRUCTED | D-REQ | re-check at consume (SL-PT R14); the abort rule before LP-DISPATCH; the dispatch deadline | injected expiry, revocation and state change at every step | clock security across deployments (ASSUMED skew bound) | S05, S06 | DERIVED; CONDITIONAL |
| **G7-I4** | The submitted external action is exactly the approved action; the parameters are taken from the authority, not from the requester | A | RECONSTRUCTED | D-REQ | the pull model; a pinned mapper; a round-trip check | parameter mutation and canonicalization fuzzing; L-1 comparison of approved vs submitted | correctness of the mapper on inputs not tested | S04 | UNVERIFIED |
| **G7-I5** | Every consequential action type on the account passes through the boundary's action allowlist (NEW, CANCEL). REPLACE and MODIFY, admin and transfer requests are refused before network I/O | B | RECONSTRUCTED | D-REQ (the allowlist) + ENV (whether the credential can reach those endpoints at all) | the K5 allowlist; broker-side permission scope | calling every non-allowlisted endpoint through K5 | that the credential cannot call them **outside** K5 (that is G7-I8) | S07 | DERIVED (allowlist); UNVERIFIED (ENV) |
| **G7-I6** | External outcomes are represented as distinct states, and AMBIGUOUS is never converted to success or failure without broker evidence | C | RECONSTRUCTED | D-REQ | the Draft 0.1 §13 B machine; query by client order id | lost-ack, crash and timeout injection | that broker query results are complete (B-QUERY, B-STMT) | §13 B, S11 | DERIVED; UNVERIFIED |
| **G7-I7** | Retries never create an uncontrolled duplicate: at most one client order id per authorization; a retry only reuses that id, and only under confirmed broker deduplication; every broker order is reconciled to exactly one authorization | C | RECONSTRUCTED | D-REQ + ENV (B-DEDUP) | deterministic COID; the no-blind-retry rule; reconciliation L-3 | duplicate-COID submission on Alpaca paper (Stage C); ambiguity tests | the broker's deduplication semantics in live trading | S09, S10 | DERIVED (rule); UNVERIFIED (B-DEDUP) |
| **G7-I8** | No component outside the enforcement boundary possesses credentials, permissions or alternate paths sufficient to perform consequential external action | B | **GIVEN** (independent challenge) | **ENV**: a property of the **deployment and the broker account**, required by design but **not derivable** from any application property | credential custody (only K5 holds it); OS-level access control; network egress control to the broker endpoints; broker-side controls (credential inventory, scope, IP binding where offered, MFA on human channels) | credential inventory (broker-side list of keys and logins); scanning hosts for secrets; egress attempts from every non-boundary host; attempts with a copied key from another network | **everything that matters:** application tests cannot show that no second key exists, that the dashboard is unused, that a copied key would fail elsewhere (**on Alpaca it would not fail**, [S1, S2]), or that egress rules have not drifted | Draft 0.1 §12 refined text | **UNVERIFIED in general; known NOT SATISFIED in the SL-PT-001 deployment** (one machine holds the dashboard session and the keys; Alpaca keys are not IP-bound) |

**Explicit assumption (not an invariant), G7-A1:** the components inside the boundary (K3, K5 and the K5 host) are uncompromised. Every Layer A invariant is CONDITIONAL on G7-A1. Gateway compromise (failure class 4) **defeats G7-I1 to G7-I7** and is countered only by G7-I8's broker-side part and by detection (Draft 0.1 S09).

---

## 4. [A0.2-4] Trust-boundary, credential and egress assumptions (explicit)

| ID | Assumption | Basis | Status |
|---|---|---|---|
| TB-1 | K3 and K5 code uncompromised (G7-A1) | — | ASSUMED |
| TB-2 | the K5 host and its administrators uncompromised | — | ASSUMED; outside the threat model for prevention |
| TB-3 | the broker credential exists only on K5 | deployment | UNVERIFIED; **false in SL-PT-001 Stage B** (founder's machine) |
| TB-4 | only K5 can reach the broker's order endpoints | egress rules | UNVERIFIED; **false in SL-PT-001** |
| TB-5 | the broker rejects a credential used from an unregistered IP | broker | **Appears unavailable for Alpaca's Trading API** (key-based authentication; an open feature request for IP allowlisting) |
| TB-6 | the broker credential cannot call admin, transfer or key-management endpoints | broker | UNVERIFIED for Alpaca Trading API keys |
| TB-7 | human channels are protected (MFA) and not used to trade | founder | MFA: OBSERVED on. "Not used to trade": procedural; detected by L-3 |
| TB-8 | client order id is unique per account, and the order is queryable by it | broker | the query endpoint exists ([S3]; OBSERVED in docs); **rejection of duplicates: UNVERIFIED** |
| TB-9 | broker statements and order lists are complete across all channels | broker | UNVERIFIED |
| TB-10 | account configuration enforces no leverage and no shorting | broker | the configuration fields exist ([S4]); **this account's values: not yet observed** |

---

## 5. [A0.2-5] Attack-surface traceability matrix

Columns:
1. surface;
2. invariant;
3. required mechanism;
4. test or falsification;
5. evidence artifact;
6. assurance boundary;
7. residual risk;
8. status.

The *SL-PT* column refers to the stage that can test the row (A / B / C, or —).

| # | Surface / failure scenario | Inv. | Mechanism | Test / falsification | Evidence artifact | Assurance boundary | Residual | Status | SL-PT |
|---|---|---|---|---|---|---|---|---|---|
| **Class 1: bypass** |||||||||
| B1 | compromised adapter calls the broker directly | I8, I5 | no credential in the adapter; egress control | from the adapter process: call the broker with no key, then with a copied key | process logs; HTTP results | the tested host and network only | config drift; any host holding the key | UNVERIFIED | C (expected: **succeeds** on a shared machine → detected by L-3) |
| B2 | a second API key or credential path exists | I8 | broker-side key inventory; revoke extras | list keys in the broker console; attempt with a revoked key | inventory record; rejection | broker console truthfulness | keys generated after the inventory | UNVERIFIED | B (inventory once) |
| B3 | human places an order in the dashboard | I8, I7 | procedure; MFA; reconciliation L-3 | place a dashboard order in Stage C | an UNMEDIATED event | detection only | anything done before detection | UNVERIFIED | C |
| B4 | alternate endpoint, network interface or proxy | I8 | egress control on every interface and hostname | attempt via IPv6, a proxy and alternate hostnames | network logs | tested paths only | untested paths | UNVERIFIED | — (not testable on the founder's machine meaningfully) |
| B5 | cancel, replace or admin used as a bypass route | I5 | K5 allowlist; REPLACE excluded | call each non-allowlisted endpoint through K5 | refusal records | K5 only | the same calls made outside K5 (B1) | DERIVED; UNVERIFIED | C |
| B6 | copied credential used from elsewhere | I8 | broker IP binding (**not offered by Alpaca's Trading API, [S1, S2]**) | use the key from a second network | HTTP result | — | **UNBOUNDED within account limits** | UNVERIFIED (expected: succeeds) | C (optional; founder decision) |
| **Class 2: TOCTOU and stale authorization** |||||||||
| T1 | two concurrent consumes | I2 | atomic LP-CONSUME | parallel consume of one auth_id | consume log | local store | storage bugs | UNVERIFIED | B / C |
| T2 | replay of a consumed authorization | I2, I7 | single-use; COID = auth_id | resubmit the same auth; resubmit the same COID at the venue | refusal; venue response | local + Alpaca paper | live venue semantics | UNVERIFIED | C |
| T3 | use after TTL | I3 | expiry checked at consume and dispatch | consume at TTL + ε | refusal | the harness clock | clock skew in other deployments | UNVERIFIED | A (shadow) / C |
| T4 | revocation inside the consume → dispatch window | I3 | the abort rule at LP-DISPATCH | revoke at injected points | abort record | local | after LP-DISPATCH: no prevention (by design) | DERIVED | C |
| T5 | relevant state change before consume | I3, I1 | R14 re-check on a fresh snapshot | change the snapshot or policy between authorize and consume | rule results | input coverage | untested state changes | UNVERIFIED | A / C |
| T6 | serialization or canonicalization alters the action | I4 | pull model; mapper round trip | fuzz mapper inputs; compare approved vs submitted | L-1 diff | mapper inputs tested | untested encodings | UNVERIFIED | B / C |
| T7 | a restore from backup resurrects authorizations | I2 | the restore-as-governance rule | restore an old store; attempt consume | refusal | local | an operator bypassing the rule | DERIVED | C |
| **Class 3: external ambiguity** |||||||||
| X1 | the broker accepts but the ack is lost | I6, I7 | AMBIGUOUS; query by COID | drop the response after send (injected in the harness) | AMBIGUOUS → query result | Alpaca paper | live behaviour | UNVERIFIED | C |
| X2 | crash after dispatch, before the outcome is recorded | I6 | write-ahead record; recovery treats DISPATCHING as AMBIGUOUS | kill after send | recovery log | local + paper | — | UNVERIFIED | C |
| X3 | crash after consume, before dispatch | I2, I3 | dead or resume under the deadline; never fresh authority | kill between the two LPs | recovery log | local | — | UNVERIFIED | C |
| X4 | retry produces a duplicate order | I7 | no blind retry; reuse the COID only under B-DEDUP | retry with the same COID on Alpaca paper | venue response | **paper only** | live deduplication | UNVERIFIED | C |
| X5 | duplicate COID accepted by the venue | I7 | depends on B-DEDUP | submit the same COID twice | venue response | paper only | — | UNVERIFIED (finding either way) | C |
| X6 | replace race fills both the old and the new order | I5 | REPLACE excluded; cancel-confirm then new | (no test; excluded) | — | — | if REPLACE is ever allowed: the reported duplicate fill [S5] | DERIVED (exclusion) | — |
| X7 | a cancel races a fill | I6 | count the order until the cancel is confirmed | cancel near a fill (timing on paper is unreliable) | order history | paper | inherent | UNVERIFIED | C (best effort) |
| X8 | audit fails just before transmission | I6 / audit | write-ahead before send; fail-closed (FD-G4) | make the audit store unavailable | refusal | local | an fsync that lies | UNVERIFIED | C |
| X9 | partial fills | I6 | pro-rata reservation; tracking | natural (Alpaca paper injects random partial fills) | fill records | paper | — | UNVERIFIED | B |
| **Class 4: compromise inside the boundary** |||||||||
| C1 | gateway (K5) code compromised | (defeats I1 to I7) | none internal; broker-side containment; detection S09 | inject a "malicious K5" mode that skips checks in the harness → expect detection, not prevention | UNMEDIATED / mismatch events | **detection only** | **UNBOUNDED** within account limits | DERIVED (no prevention) | C (modelled) |
| C2 | host administrator / root | (defeats I8) | none internal | — (not testable without real separation) | — | — | UNBOUNDED within account limits | stated limitation | — |
| C3 | authority K3 compromised, issuing over-limit authorizations | I1 | alternative D (independent risk check) if adopted (FD-G10) | inject a K3 that authorizes over the limit | refusal (with D) / L-2 breach detected (without) | harness | common-mode data | UNVERIFIED | C (modelled) |
| C4 | signing key compromise | (only if alternative B is adopted) | not used in Draft 0.1's hybrid | — | — | — | — | n/a | — |
| C5 | audit record tampered with | audit | hash chain + git anchor (detection) | edit a past event; run the verifier | verifier failure | after anchoring | before the first push | UNVERIFIED | A |
| C6 | the venue itself misreports (paper anomalies) | I6 | reconciliation L-2; no silent correction | (observed if it happens) | DISCREPANCY events | detection | — | UNVERIFIED | A / B |
| **Z** | **hostile-review inventory (31 + F.1 to F.3): rows not received** | — | — | — | — | — | **the completeness of this matrix against the review is unknown** | **OPEN** | — |

---

## 6. [A0.2-6] SL-PT-001 integration map

| Stage | Credentials | What it **can** test | What it **cannot** test | Rows above |
|---|---|---|---|---|
| **A: shadow** | none | policy evaluation (I1), stale data and TTL in shadow (I3), the approved-record completeness that I4 later compares against, record tamper detection (C5), venue-data anomalies (C6) | anything about mediation (B), venue behaviour (C), consumption under concurrency | T3, T5, C5, C6 |
| **B: paper execution** | **paper** API keys on the founder's machine | the binding of approved vs submitted order (I4, L-1); single-use at the harness (I2); reconciliation with Alpaca's independent records (L-2, L-3); partial fills (X9); key inventory (B2) | **production mediation** (I8 is known not to hold on one machine); live venue behaviour; fill realism | T1, T6, X9, B2 |
| **C: adversarial** | paper keys | replay, expiry, revocation windows (T2 to T4, T7); ambiguity and crash (X1 to X3, X7, X8); duplicate client order id on Alpaca paper (X4, X5); **bypass attempts whose expected result is "succeeds and is detected"** (B1, B3, B6); modelled compromise (C1, C3) | resistance to real host compromise (C2); live deduplication; the absence of unknown channels | T2–T7, X1–X8, B1, B3, B5, B6, C1, C3 |

**Stage B is not a local simulator.** It is an external paper API. Its results are evidence about **Alpaca paper's** behaviour and about Sentinel's handling of it, not about live execution. **Running Stage B on the founder's machine is a deliberate deployment in which G7-I8 does not hold.** The experiment's job there is to show that the violation is *detected*, and to expose what production would need.

---

## 7. [A0.2-7] Claim-status separation

The status scale has seven columns:
1. specified;
2. implemented;
3. local tests passed;
4. adversarial tests passed;
5. external integration tested;
6. independently reconstructed;
7. production assumptions validated.

**None may be inferred from another.**

| Item | Specified | Implemented | Local tests | Adversarial tests | External integration | Independently reconstructed | Production assumptions |
|---|---|---|---|---|---|---|---|
| G7-I1 to G7-I7 | **yes** (I1 to I7 reconstructed) | no | no | no | no | no | no |
| G7-I8 | yes (as a deployment requirement) | no | n/a | no | no | no | **no; known false in SL-PT-001** |
| K5 allowlist, pull model, COID rule | yes | no | no | no | no | no | no |
| Reconciliation L-1 to L-3 | yes (SL-PT-001 §8) | no | no | no | no | no | no |
| SL-PT-001 Stage A harness | yes (Spec v0.1) | **no (PT-FD-11 pending)** | no | no | no | no | n/a |

**Reminders:**
- Paper execution is not live execution.
- Simulated fills are not market evidence.
- A hash chain shows that a record has not been changed since anchoring, not that its inputs were true.
- Model agreement is not verification.
- A passing harness does not prove that the harness cannot be bypassed.

---

## 8. [A0.2-8] Founder decisions (separated from technical requirements)

**Technical requirements (no decision needed; they follow from the invariants):**
- **TR-1:** the executor pulls the approved parameters from the authority by auth_id.
- **TR-2:** COID = auth_id; on ambiguity, query by COID; never resubmit under a new id.
- **TR-3:** REPLACE and MODIFY are excluded; the allowlist is NEW and CANCEL.
- **TR-4:** reconciliation L-1 to L-3 every cycle; no silent correction.
- **TR-5:** at harness start, **read back** the account configuration (multiplier, shorting, buying power) and refuse to run if it differs from policy.
- **TR-6:** the write-ahead dispatch record precedes any send.
- **TR-7:** record every venue response raw.

**Founder decisions:**

| ID | Decision | Note |
|---|---|---|
| FD-G1 to FD-G11 | carried from Draft 0.1 §21, unchanged | |
| **FD-G12** | accept that, on Alpaca's Trading API, **key compromise is contained only by account segregation and size**, not by key restrictions | evidence above; verify with Alpaca support if it matters for anything beyond paper |
| **FD-G13** | proceed to SL-PT-001 Stage B **knowing that G7-I8 does not hold** in that deployment (detection only) | this is the honest framing of Stage B |
| **FD-G14** | supply the hostile-review record so that G7-I1 to G7-I7 can be confirmed or replaced, and row Z closed | blocking for a claim of matrix completeness |
| **FD-G15** | whether to run B6 (use a copied paper key from a second network) to OBSERVE the absence of IP binding | low cost on paper; it produces direct evidence |
| PT-FD-11 | authorize the Stage A harness build | unchanged; still required before any code |

---

## 9. [A0.2-9] Claims that remain UNVERIFIED or UNBOUNDED (concise)

**UNVERIFIED:**
- every invariant G7-I1 to G7-I8 (nothing is implemented);
- B-DEDUP (duplicate-COID rejection);
- per-key permission scope (TB-6);
- statement completeness (TB-9);
- this account's multiplier and shorting configuration (TB-10);
- mapper correctness;
- egress isolation on any host;
- whether the reconstructed G7-I1 to G7-I7 match the review;
- the completeness of the attack-surface inventory.

**UNBOUNDED (within the account's assets and configuration):**
- loss under K5-host, administrator or credential compromise (C1, C2, B6);
- exposure between an unmediated order and its detection (B3).

**Known not to hold:** G7-I8 in the SL-PT-001 deployment (TB-3, TB-4).

## Sources

- [S1] Alpaca community forum: "[Feature Request] API Key IP Allowlisting", https://forum.alpaca.markets/t/feature-request-api-key-ip-allowlisting/19087. A user request stating that an algo trading key has full order-submission permission and can be used from anywhere if leaked. This is evidence that the feature is absent; it is not official confirmation.
- [S2] QuotaGuard: "Give Your Alpaca Trading Bot a Static Outbound IP", https://www.quotaguard.com/blog/alpaca-trading-bot-static-outbound-ip. A third party stating that Alpaca authenticates by API key, not source IP. Not official.
- [S3] Alpaca API reference: "Get Order by Client Order ID", https://docs.alpaca.markets/reference/getorderbyclientorderid. Official.
- [S4] Alpaca API reference: "Account Configurations" (patch), https://docs.alpaca.markets/us/reference/patchaccountconfig-1. Official.
- [S5] Alpaca forum: "Replace order creates a new order successfully but the old order is filled later", https://forum.alpaca.markets/t/replace-order-creates-a-new-order-successfully-but-the-old-order-is-filled-later-thus-creating-duplicate-order/5794. A user report on paper.

TB-5 and FD-G12 rest on S1 and S2, which are **not** official Alpaca statements. They are **UNVERIFIED** until Alpaca confirms them, or until test B6 observes the behaviour.

*End of Draft 0.2 amendment. Nothing implemented, tested or executed. No credentials were created and no orders were placed.*
