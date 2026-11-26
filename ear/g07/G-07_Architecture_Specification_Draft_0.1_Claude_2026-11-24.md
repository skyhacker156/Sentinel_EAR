# G-07 Architecture Specification, Draft 0.1: Execution Enforcement Boundary

**Date:** 2026-11-24 | **Author:** Claude, Specification Lead | **Workstream:** G-07 (separate from EAR)
**Classification:** SPECIFICATION ONLY / NOT IMPLEMENTED / NOT VERIFIED / NO EXECUTION AUTHORITY. Not frozen. **Every design element is a proposal**, not a capability of Sentinel.
**EAR boundary:** EAR Rev 3.1 (frozen) and Rev 3.2 Draft 4 (candidate) are **not modified** and are **not integrated** with G-07. Section 7.3 states only the *interface assumptions* G-07 makes about EAR.
**Labels:** DERIVED / ASSUMED / CONDITIONAL / UNVERIFIED / UNBOUNDED. **Nothing here is COMPUTED.**

> **Input gap (blocking for traceability, not for the architecture).** The dispatch lists Gemini's Independent Hostile Architectural Review (including G7-I1 to G7-I7, 31 scenarios and F.1 to F.3) and GPT's assessment of it as inputs. **Neither was attached.** This draft uses only the dispatch text: GPT corrections G7-R01 to R07, the G7-I8 text, the 12 mandatory sequences, and the founder-decision list. To avoid collisions, this draft's own invariants are **G7-S01…** and its scenarios **G7-F01…**. The traceability rows for Gemini's material are marked **NOT RECEIVED** (§23). Draft 0.1a will map them once supplied.

---

## 1. Executive verdict and scope

1. **The strongest achievable claim (DERIVED, CONDITIONAL):** under the threat model of §4, Sentinel can technically prevent a *compromised intelligence component or adapter* from causing an unauthorized consequential action through the declared interface. It needs three things together:
   - (a) the broker credential exists only inside a minimal **Egress Gate**;
   - (b) network egress to the broker is possible only from the Egress Gate;
   - (c) the broker credential itself carries no permission beyond the governed action domain (§6).
2. **Not achievable within Sentinel (DERIVED):**
   - prevention against compromise of the component that holds the broker credential;
   - prevention against an administrator with control of that host;
   - prevention against compromise of the broker account through other channels: web login, phone, a second API key.

   Under those compromises, the only remaining *preventive* controls are **broker-side restrictions**, an external dependency (§20). Without them, the consequence is **UNBOUNDED** within the account's broker permissions.
3. **Gateway compromise defeats the internal design** (DERIVED). Detection survives only through reconciliation of broker statements against the independent audit (§14).
4. **No exactly-once external execution is claimed.** The design gives:
   - at-most-once **authorization consumption**;
   - at-most-once **dispatch commitment** per authorization (both local, DERIVED);
   - at most one **broker order** per authorization only CONDITIONAL on broker deduplication by client order id (B-DEDUP), or on a no-blind-retry policy plus a broker status query (B-QUERY).
5. **Initial action scope (a proposal, pending founder decision FD-G8):**
   - in: NEW order and CANCEL;
   - out: MODIFY and REPLACE, expressed as CANCEL then NEW;
   - out: account-level instructions and transfers. These must be made **technically impossible** through the credential's broker permissions, not merely ungoverned (§6).

## 2. Architectural objective

Every consequential external action that reaches the broker through Sentinel's credentials corresponds to **exactly one** live, unconsumed, unrevoked, unexpired authorization for **exactly that action**. Any action that does not is either impossible through Sentinel's credentials or, outside the threat model, detected and contained.

## 3. Center-of-gravity alignment

| Question | G-07 answer |
|---|---|
| Authority | an authorization consumed at the Consumption Authority's linearization point (§10). A signature, a status, a log entry or an adapter request is not authority |
| Evidence | the consumption record, the dispatch write-ahead record, broker acknowledgements and statements |
| Uncertainty | ambiguous dispatch outcomes are first-class states (§13 B). They keep exposure counted (EAR interface §7.3) |
| Enforcement | credential isolation plus egress control plus broker-side permission scoping (§12). Policy alone is never counted |
| Reconstruction | every dispatch is reconstructable from the audit and reconcilable against broker statements (§14) |

---

## 4. Threat model

| ID | Adversary or fault | In scope for **prevention**? | In scope for **detection**? |
|---|---|---|---|
| T1 | intelligence or strategy component: arbitrary proposals, prompt-injected or adversarial | **yes** | yes |
| T2 | adapter process fully compromised (arbitrary code, its own credentials) | **yes**, if §12 holds | yes |
| T3 | network attacker between components, or toward the broker | yes, via authenticated channels (ASSUMED: TLS and the key handling are correct) | yes |
| T4 | crash, restart, partition, lost or duplicated messages, clock skew | **yes**: no unauthorized action; availability may be lost | yes |
| T5 | Consumption Authority (EAR store) compromised | **no**: it can authorize anything up to broker-side limits | partial: via the independent risk check (alternative D) and reconciliation |
| T6 | Egress Gate compromised (code execution in the credential holder) | **no** | yes, via reconciliation of broker statements against the audit (if the audit is outside the gate's control) |
| T7 | administrator or host root on the gate host | **no** | as T6 |
| T8 | audit store tampered with or unavailable | n/a | tampering is detected via external anchoring; unavailability is a founder policy (FD-G4) |
| T9 | broker account accessed outside Sentinel (web, phone, other keys) | **no** | yes: an unknown order (EAR E20); **broker-side controls only** |
| T10 | broker error (duplicate execution, wrong fills, lost orders) | no | yes: reconciliation |
| T11 | signing key compromise (if a signed capability is used) | no: forged capabilities | depends on consumption-ledger custody (§17 B) |

**Threat-model claim (DERIVED):** prevention holds for T1 to T4. For T5 to T7 and T9 to T11, Sentinel offers detection and containment only, and the bound is the broker-side permission scope (UNVERIFIED, §20).

---

## 5. Trust and authority map

| # | Component | Authority | Secrets | Trusts as input | Can output | If compromised | Containment |
|---|---|---|---|---|---|---|---|
| K1 | Intelligence / strategy | none | none | — | proposals | arbitrary proposals | EAR Π evaluation; no credentials or egress |
| K2 | Adapter | none (messenger) | **none** (no broker credential) | proposals, gate replies | proposal translation; authorization ids | can drop, delay, replay or alter **its own messages only** | gate binds the payload from K3, not from K2; no egress (§12) |
| K3 | Consumption Authority (CA; the EAR store) | issues and consumes authorizations | its signing or attestation key (if B) | evidence log | consumption records; authorized payloads | **authorizes anything** within broker limits (T5) | the independent risk check (D); broker-side limits; reconciliation |
| K4 | Signer (only under alternative B) | attests to K3's records | signing key (HSM optional) | K3 records | signatures | forges capabilities (T11) | signing proves only that the key signed, not correctness. The ledger stays authoritative |
| K5 | Egress Gate: verifier plus dispatcher, **one minimal process** | the only holder of the broker credential | **broker API credential** | K3 consumption replies (authenticated); K2 requests (untrusted) | broker requests; dispatch records | **everything within broker permissions** (T6) | broker-side permission scope; independent audit; reconciliation |
| K6 | Network egress control (firewall, VPC or namespace rules) | permits broker endpoints from K5 only | rule configuration | — | — | bypass from any host (T2 → T6-equivalent) | configuration attested and tested (§19); dual control on changes |
| K7 | Host OS and administrator of K5 | total over K5 | everything on the host | — | — | = T6 | separate host and account; minimal admins; audited access. **Not a technical prevention** |
| K8 | Audit store (append-only, external anchoring) | records | its own write key | K3 and K5 records | entries | rewrite or deletion | hash-chain heads anchored to a third party; broker-statement reconciliation |
| K9 | Broker | executes | — | its authentication | acks, fills, statements | out of scope (T10) | — |
| K10 | Human broker access | full account power | broker web login | — | anything | T9 | **broker-side only**: separate credentials, 2FA, no API key sharing (environmental) |
| K11 | Independent risk check (alternative D only) | veto over dispatch | its own view source | broker positions (read-only credential) | ALLOW / VETO | veto withdrawn | must itself be compromised **together with** K3 for an over-limit order to pass |

**Separation-of-duties finding (DERIVED):**
- Compromising K1 or K2 (the ordinary application components) is prevented from granting execution authority **iff** K2 holds no broker credential and has no egress path, because K5 accepts payloads only from K3, by id.
- Compromising K3 *does* grant authority unless a second, independent veto (K11) is required at K5.
- Compromising K5 grants everything that the credential permits. **No internal separation can remove this, because K5 must hold the credential to act at all** (DERIVED from the bearer-credential model; CONDITIONAL on the broker offering no multi-party authorization, B-MPA).

**On HSMs, enclaves, containers and segmentation:**

| Mechanism | What it gives | Where it fails |
|---|---|---|
| HSM-held signing key | the key cannot be *exported* | whoever can call the HSM can sign. A compromised K3 or K4 host signs freely |
| Enclave holding the broker credential | the credential is hidden from the host OS | (a) the enclave code is the gate, so a gate bug is the same as compromise; (b) side channels; (c) the broker sees TLS from the enclave's host, so the egress rules are still required |
| Containers or namespaces | process and network separation | shared kernel; escape equals the host (T7) |
| Network segmentation | path restriction | misconfiguration; second interfaces; DNS; the administrator changes the rules (T7) |

**None of these is counted as prevention without the §19 tests and external review** (UNVERIFIED).

---

## 6. Consequential action domain

| Action | Consequence | Governed how | Initial scope |
|---|---|---|---|
| NEW order | creates exposure | EAR authorization → consumption → dispatch | **IN** |
| CANCEL | removes a working order. It can remove *protective* orders, and it races with fills | its own authorization: bound to broker_order_id or client_order_id, single-use, consumed like NEW. EAR keeps counting the order until the broker confirms the cancel | **IN** |
| MODIFY / REPLACE | changes quantity, price or side in place; the broker often performs it as cancel-and-new | **excluded**: expressed as CANCEL then NEW, each governed. The gate rejects any modify endpoint | OUT (FD-G8) |
| Account-level instructions (margin, options level, settings) | changes the meaning of every other limit | **must be impossible**: the credential lacks the permission (B-PERM) | OUT, made impossible |
| Transfers or withdrawals | moves assets out | **must be impossible**: the credential lacks the permission (B-PERM) | OUT, made impossible |
| API-key management, session or IP settings | can create a bypass credential | **must be impossible** via the credential (B-PERM) | OUT, made impossible |
| Read-only queries (positions, orders, statements) | none directly; they feed evidence | separate **read-only** credential, preferably at another host, for reconciliation and K11 | IN (read-only) |

**Rule G6-1:** the gate holds an **allowlist of broker endpoints and methods** (NEW, CANCEL, the status query) and rejects everything else **before** any network call. Admin endpoints never pass, whatever the authorization says.

**Where the claim stops:** the allowlist prevents misuse only of *Sentinel's* credential. If the credential *can* call admin endpoints at the broker, then a compromised gate can call them (T6). **B-PERM is therefore load-bearing.**

---

## 7. Authorization model

### 7.1 Authorization record (in K3)

Fields:
- auth_id (= EAR reservation_id = order_id);
- kind ∈ {NEW, CANCEL};
- account, instrument, side, quantity, order type, limit price, time-in-force;
- the target (for CANCEL);
- payload_hash (canonical, §8);
- issued_at, expires_at;
- the basis reference (the EAR L1 commit record);
- state (§13 A).

### 7.2 What an authorization is not

It is not a signature, not an adapter message, and not an EAR evaluation. It is authority only **at the consumption linearization point** (§10).

### 7.3 Interface assumptions about EAR (not integration)

- **G-EAR-1:** EAR counts the commitment from the commit until G-07 reports a terminal *local* dispatch outcome that excludes transmission (NOT_DISPATCHED), or until broker state reconciles it.
- **G-EAR-2:** EAR's "consume" corresponds to G-07's authorization consumption. G-07's *dispatch* layer has no EAR counterpart today, and the gap is recorded as G7-C05.
- **G-EAR-3:** ambiguous dispatch outcomes are reported to EAR as "possibly transmitted". EAR's world set then includes them (EIVI CP-1 B-28).

These are **assumptions G-07 states about EAR**, not changes to EAR.

---

## 8. Capability and record representation

- **Canonical payload:** the EAR Draft 4 typed encoding (schema-versioned, length-prefixed, injective identifiers). It is reused **by reference** only.
- **payload_hash:** SHA-256 of that encoding.
- **The gate never re-serializes a payload received from K2.** It obtains the authorized payload **from K3 by auth_id** (the pull model), builds the broker request from K3's canonical fields with a pinned, version-recorded mapper, and checks that the request it built maps back to the same canonical fields (a round-trip check).
- **Why the pull model (DERIVED):** the adapter can no longer alter the action. Serialization ambiguity is confined to one mapper whose input is K3's canonical form (§18 F10). **The residual risk is the mapper itself** (UNVERIFIED; it needs the §19 mutation tests).
- **A signed capability (alternative B)** is **optional** in the recommended hybrid (§17). A signature adds offline verifiability, which in turn reintroduces revocation staleness. It does not prove the authorization is correct.

---

## 9. Revocation and expiry semantics

- **Revocation:** a K3 state transition, ACTIVE → REVOKED. It takes effect for dispatch **iff it is linearized in K3 before the consumption point** (§10). After consumption but before the dispatch commitment, revocation is still effective under the abort rule (§10, R01-Q4). After the dispatch commitment, revocation **cannot prevent** transmission; it becomes a request to cancel (a new governed CANCEL).
- **Expiry:** checked **in K3 at the consumption point** against K3's clock. The gate additionally refuses to begin the dispatch commitment if its own clock exceeds `expires_at − skew_margin`.
  - **Clock assumption (ASSUMED):** |clock(K3) − clock(K5)| ≤ skew_margin.
  - **Bounds:** FD-G7.
  - **Skew beyond the margin:** an expired authorization could be dispatched late. This is **not** an exposure-accounting error, because EAR still counts it, but it is a **policy** violation.
- **Revocation-service outage:**
  - In the pull model, K3 *is* the revocation service. If K3 is down, nothing is consumed: no dispatch, fail-closed.
  - Under alternative B with offline verification, the gate must choose between refusing and proceeding on stale revocation state. That is founder decision **FD-G3**.

---

## 10. Consumption and dispatch semantics (G7-R01, G7-R02)

### 10.1 The ten lifecycle points and their linearization points (LP)

| # | Point | Where | Linearization point | Locally atomic? |
|---|---|---|---|---|
| 1 | authorization evaluation | K3 | none (a read) | — |
| 2 | issuance (EAR commit) | K3 | LP-ISSUE: the K3 commit record | yes |
| 3 | presentation (adapter sends auth_id to the gate) | K2 → K5 | none | no |
| 4 | validity and revocation check | K3 (called by K5) | part of LP-CONSUME | yes |
| 5 | consumption commitment | K3 | **LP-CONSUME**: one K3 fold checks ACTIVE ∧ ¬revoked ∧ ¬expired ∧ Π, then sets CONSUMED and binds dispatch_id | yes (in K3) |
| 6 | dispatch commitment | K5 | **LP-DISPATCH**: a durable write-ahead record DISPATCHING(dispatch_id, client_order_id), acknowledged by the audit sink (FD-G4) | yes (in K5) |
| 7 | first outbound byte | K5 → network | **none.** Not atomic with anything local | no |
| 8 | broker acknowledgement | K9 → K5 | observation only | no |
| 9 | broker acceptance | K9 | external | no |
| 10 | fills, corrections, busts | K9 | external; observed via EAR evidence | no |

### 10.2 The R01 questions

**Q1. When can revocation reliably prevent transmission?** (DERIVED; CONDITIONAL on the abort rule)
- If it is linearized in K3 **before LP-CONSUME**, it always prevents transmission.
- If it falls between LP-CONSUME and LP-DISPATCH, it prevents transmission **if** K5 re-queries K3's revocation state as part of the LP-DISPATCH step and aborts.
- After LP-DISPATCH, it never does.

**Q2. When is an authorization irrevocably consumed?** At LP-CONSUME. It can never be consumed again, and recovery never "un-consumes" it (G7-S02).

**Q3. Can state change after consumption but before transmission?** Yes. Evidence may arrive, governance may act, time passes, and the gate may crash. The window LP-CONSUME → LP-DISPATCH is **bounded** by `dispatch_deadline = LP-CONSUME + δ_d`.
- Past the deadline, K5 must not dispatch. The authorization becomes CONSUMED_NOT_DISPATCHED (dead).
- The window LP-DISPATCH → the first byte is not bounded locally. It is assumed short, and a crash inside it produces AMBIGUOUS.

**Q4. Governance invalidates during that interval?**
- Before LP-DISPATCH: K5's LP-DISPATCH step re-reads K3's state. If it is REVOKED or INVALIDATED → abort → NOT_DISPATCHED, reported to EAR, and the commitment ends.
- After LP-DISPATCH: the invalidation is recorded, EAR keeps the order counted, and a CANCEL authorization may be issued. **Prevention is impossible.**

**Q5. Locally guaranteed** (DERIVED; CONDITIONAL on correct K3 and K5 and durable storage):
- at most one consumption per auth_id;
- at most one dispatch commitment per consumption;
- at most one client_order_id per dispatch;
- no dispatch without consumption;
- no dispatch after the deadline;
- no dispatch whose payload differs from K3's record.

**Q6. Not guaranteed once the first byte is sent:**
- whether the broker received it;
- whether the broker accepted it;
- whether it was executed once or more than once (without B-DEDUP);
- when it executes;
- the outcome of a cancel race.

### 10.3 Identifiers (R02)

| Id | Scope | Uniqueness | Reuse |
|---|---|---|---|
| auth_id | one authorization | K3 | never |
| dispatch_id | the single dispatch commitment of one auth_id | K5 | never |
| client_order_id (COID) | sent to the broker | deterministic: COID = H(account, auth_id, "G07-v1"), truncated to the broker's format (B-COID) | **only** for a retry of the same dispatch |
| broker_order_id | assigned by the broker | broker | — |
| exec_id | fills | broker (EAR E-1) | — |

### 10.4 Crash and ambiguity handling (R02)

| Event | Local state found at restart | Rule |
|---|---|---|
| crash after LP-CONSUME, before LP-DISPATCH | CONSUMED, no dispatch record | if `now ≤ dispatch_deadline` and K3 still shows ¬revoked: dispatch may resume **under the same dispatch_id** [FD-G5 alternative (a)]. Otherwise CONSUMED_NOT_DISPATCHED (dead). **Never** a fresh authorization (G7-S02) |
| crash after LP-DISPATCH, before or during the send | DISPATCHING | **AMBIGUOUS**: query the broker by COID (B-QUERY). If it is found → reconcile. If not found → see FD-G5: retry with the **same** COID only if B-DEDUP holds; otherwise wait for the broker query to stabilize, then declare NOT_RECEIVED_PROBABLE. EAR keeps counting throughout |
| sent; acknowledgement lost | DISPATCHING | the same as above |
| duplicate COID rejected by the broker | — | evidence that a prior submission was received → reconcile, do not retry |
| the broker does not deduplicate (¬B-DEDUP) | — | **no blind retry, ever.** A retry could produce two orders (CONDITIONAL failure mode, F04) |

---

## 11. Gateway and adapter separation

- **The adapter (K2) is a messenger.** It sends `DISPATCH(auth_id)` and receives a result. It never holds a broker credential, never constructs the broker request, and has no route to the broker.
- **The gate (K5) is one minimal process** containing the verifier, the request mapper, the dispatcher, the write-ahead log and the credential.
  - *Separating the verifier from the credential holder moves trust rather than removing it:* the credential holder would have to trust the verifier's result, so compromising the verifier would equal compromising the gate.
  - The gate's code must be small and reviewable, with no plugin or strategy logic, a pinned build, and an attested hash (UNVERIFIED).

## 12. Credential and egress custody (G7-R07, G7-I8)

**Five layers.** Each is counted separately; **none is counted from documentation alone.**

| Layer | Mechanism | Prevents | Does not prevent |
|---|---|---|---|
| L-a documented restriction | policy | nothing technically | everything |
| L-b application permission | gate allowlist (G6-1) | misuse of the credential through the gate's interface | gate compromise |
| L-c OS enforcement | the credential is readable only by the gate's user; a separate host | other local processes reading it | root, kernel escape (T7) |
| L-d credential isolation | the credential exists only on the gate host, or in its enclave or secret store. It is issued for the gate's IP only (B-IPALLOW) | use of a copied credential from elsewhere (only with B-IPALLOW) | gate-host compromise |
| L-e network egress | only the gate host can reach the broker's API endpoints (and any DNS used for them) | adapter or strategy hosts calling the broker even with a stolen credential | gate-host compromise; the administrator changing the rules |
| L-f broker-side restriction | trade-only key scope; no withdrawals or admin; IP allowlist; per-order and position limits at the broker | **the only layer that survives gate compromise** | anything the broker permits; human channels if they are not separately locked |

**G7-I8 refined (proposal):** *No principal other than the Egress Gate holds a credential, permission or network path that the broker would accept for a consequential action on the account. The gate's own credential permits only the governed action domain (§6). Every other broker access channel is either disabled or held by a human under a documented, separately audited procedure, and excluded from the automated authority model.*

**Status:** CONDITIONAL on B-PERM, B-IPALLOW and the human-channel procedure. UNVERIFIED.

**How the single egress path could be established and tested:**
1. Inventory every broker credential issued for the account. Broker evidence is needed; we cannot rely on our own records alone.
2. From every non-gate host and namespace, attempt broker authentication and API calls with (a) no credential and (b) a copied gate credential. Both must fail.
3. Scan the hosts and configuration for credential material outside the gate.
4. Test for second interfaces, IPv6, proxies, DNS alternatives and alternate broker hostnames.
5. Check the broker's IP allowlist from an off-list address.
6. Repeat after every infrastructure change. Configuration drift is the dominant real failure.

**A diagram proves none of this.** The tests show only what they test, at the time they are run.

---

## 13. State machines (G7-R01, R02; §6 of the dispatch)

### A. Authorization lifecycle (K3; every transition is **locally atomic** in K3)

```
ISSUED_ACTIVE ──suspend──▶ SUSPENDED ──reactivate (new basis)──▶ ISSUED_ACTIVE
ISSUED_ACTIVE / SUSPENDED ──revoke──▶ REVOKED          (terminal)
ISSUED_ACTIVE / SUSPENDED ──expire──▶ EXPIRED          (terminal)
ISSUED_ACTIVE / SUSPENDED ──invalidate──▶ INVALIDATED  (terminal)
ISSUED_ACTIVE ──consume (LP-CONSUME)──▶ CONSUMED       (terminal for authorization; dispatch continues in B)
recovery: no transition leaves CONSUMED, REVOKED, EXPIRED or INVALIDATED. No path from CONSUMED to ACTIVE exists.
```

### B. Dispatch lifecycle (K5; transitions marked * are **local atomic writes**; the others are **observations**)

```
(none) ──*LP-DISPATCH──▶ DISPATCHING
(none) ──abort (revoked / expired / deadline)──▶ NOT_DISPATCHED*          (terminal; reported to EAR: not transmitted)
DISPATCHING ──send ok, ack received──▶ ACKED                             (observation)
DISPATCHING ──explicit broker reject──▶ REJECTED                         (observation; terminal)
DISPATCHING ──crash / timeout / no ack──▶ AMBIGUOUS*
AMBIGUOUS ──broker query: found──▶ ACKED                                 (observation)
AMBIGUOUS ──broker query: not found, stable (FD-G5)──▶ NOT_RECEIVED_PROBABLE*   (still counted by EAR until broker statements confirm)
AMBIGUOUS ──retry same COID (only if B-DEDUP)──▶ DISPATCHING*
ACKED / NOT_RECEIVED_PROBABLE ──statement reconciliation──▶ RECONCILED*  (terminal)
```

### C. External order lifecycle (broker truth; **every transition is an observation**)

```
UNKNOWN ──ack──▶ ACKNOWLEDGED ──accept──▶ WORKING ──fill──▶ PARTIAL ──fill──▶ FILLED
WORKING / PARTIAL ──cancel confirmed──▶ CANCELLED
(any) ──reject──▶ REJECTED
FILLED / PARTIAL ──correction / bust──▶ (EAR evidence; quantities change, identity does not)
(any) ──no information──▶ UNKNOWN
```

**Interaction (DERIVED):**
- A local status never asserts an external state. "ACKED" means "an acknowledgement was observed", not that the order exists.
- EAR exposure counts the order whenever B ∉ {NOT_DISPATCHED, REJECTED} or C ∉ {REJECTED, CANCELLED, FILLED-and-reconciled}.
- **The three machines are joined only by identifiers** (auth_id → dispatch_id → COID → broker_order_id). No combined status exists.

---

## 14. Audit and reconstruction model (G7-R03)

| Property | Meaning | How obtained | What it does not give |
|---|---|---|---|
| Append-only | records cannot be modified through the store's interface | storage permissions, write-once storage | protection against the storage administrator |
| Tamper-evident | modification is **detectable** | hash chain; chain heads anchored periodically to an external party | **prevention**; detection only if someone checks |
| Authenticated | we know **which key** wrote an entry | per-writer signatures | truth of the content |
| Complete | **every** dispatch has an entry | WAL-before-send inside K5 (LP-DISPATCH) | completeness if K5 is compromised |
| Independently verifiable | a third party can check the audit against the world | reconciliation against broker statements via a **separate read-only credential** | real-time prevention; it is retrospective |

- **Prerequisite (proposal):** a durable dispatch record **before** the first byte. The record's durability level (local WAL only, or acknowledged by an external sink) is **FD-G4**.
- **Audit store unavailable:** under the strict option of FD-G4, nothing is dispatched (fail-closed).
- **Partial write:** detected by the chain; treated as absent, so no dispatch.
- **Crash between the audit write and the send:** AMBIGUOUS, per §10.4.
- **Send followed by a failure to record the outcome:** AMBIGUOUS. Reconciliation resolves it.
- **Tampered history:** detected at the next anchor check. Recovery restores from the replica and reconciles with the broker, and the incident is a stop condition (FD-G11).

**Reconstruction claim (CONDITIONAL):** for every broker order on the account, one of the following holds:
- (a) a dispatch record with a matching COID exists; or
- (b) it is flagged as an **unmediated order** (G7-S09).

This holds iff statements are complete (B-STMT) and the reconciliation runs. **It is detection, not prevention.**

---

## 15. Failure and recovery semantics

- **Fail-closed default (proposal; the posture is FD-G2):** any of the following stops dispatch:
  - K3 unreachable;
  - audit not durable;
  - clock skew beyond the bound;
  - a mapper round-trip mismatch;
  - an unknown broker response.
- **Recovery never mints authority.** On restart, K5 reads its write-ahead log and treats every DISPATCHING record as AMBIGUOUS. K3 never returns CONSUMED to ACTIVE.
- **Backup restore hazard (DERIVED):** restoring K3 or K5 storage from an older backup could resurrect authorizations already consumed, or erase dispatch records.
  - **Rule:** a restore is a governance operation. After a restore, every authorization issued before the backup point is treated as consumed-unknown (dead), and AMBIGUOUS is set for any dispatch it might have covered.
  - Single-use relies on **storage not rolling back** (ASSUMED otherwise).
- **Resume after an ambiguous outcome:** only once broker reconciliation has completed, or under an explicit founder posture (FD-G11).

---

## 16. Security invariants (proposals)

| ID | Statement | Enforcement point | Preconditions | Failure response | Counterexample | Verification | Status |
|---|---|---|---|---|---|---|---|
| G7-S01 | No broker request is sent except for an auth_id that K3 has consumed at LP-CONSUME | K5 | K5 uncompromised; K3 channel authenticated | refuse; alarm | a compromised K5 sends at will (T6) | local interleaving and fault tests (§19 V-1, V-2) | DERIVED; CONDITIONAL |
| G7-S02 | Each auth_id is consumed at most once and never returns to a consumable state, including after a crash or restore | K3 | durable, non-rolled-back storage | refuse | restoring a backup resurrects it (F14) | concurrency, crash and restore tests | DERIVED; CONDITIONAL (storage) |
| G7-S03 | At most one dispatch commitment per consumption, and at most one COID per dispatch | K5 | as S01 | refuse | a K5 bug writing two records | crash and replay tests | DERIVED; CONDITIONAL |
| G7-S04 | The broker request is built only from K3's canonical record, and its fields round-trip exactly | K5 mapper | mapper correct | refuse | mapper defect (F10) | mutation and fuzz tests (V-6) | UNVERIFIED |
| G7-S05 | Revocation linearized before LP-DISPATCH prevents transmission | K3 + K5 | the abort rule; δ_d bounded | abort | revocation arriving after LP-DISPATCH (no prevention, by design) | interleaving tests | DERIVED; CONDITIONAL |
| G7-S06 | No dispatch after `expires_at − skew_margin` or after `dispatch_deadline` | K3 + K5 | the clock-skew bound | abort | skew exceeds the bound | clock-skew injection | CONDITIONAL; ASSUMED (clocks) |
| G7-S07 | No request outside the action allowlist (§6) leaves K5 | K5 | K5 uncompromised | refuse | gate compromise; a broker endpoint alias | endpoint fuzzing | DERIVED; CONDITIONAL |
| G7-S08 | A durable dispatch record precedes every first byte | K5 | storage durability; FD-G4 | refuse | the OS acknowledges an fsync it did not perform | crash at every write point | CONDITIONAL; UNVERIFIED |
| G7-S09 | Every broker order on the account is either matched to a dispatch record or flagged UNMEDIATED within the reconciliation period | reconciler (separate read-only credential) | B-STMT; the reconciler independent of K5 | quarantine: stop all dispatch (FD-G11) | the broker omits an order from statements | mock broker with hidden orders | CONDITIONAL; detection only |
| G7-S10 | An ambiguous dispatch is never retried with a new COID, and never retried at all without B-DEDUP | K5 | — | hold AMBIGUOUS | — | ack-loss tests | DERIVED |
| G7-S11 | Exposure accounting counts every dispatch not proven untransmitted (G-EAR-1, G-EAR-3) | K3/EAR interface | EAR implements the interface | — | EAR drops an AMBIGUOUS order | joint harness | ASSUMED (interface) |
| **G7-I8** (refined, §12) | no principal other than K5 holds a broker-accepted path to consequential action; K5's credential is limited to the domain | K6, L-f (broker) | B-PERM, B-IPALLOW, the human-channel procedure | quarantine; rotate credentials | a second API key; web login; an IPv6 path | §12 test list; broker evidence | CONDITIONAL; UNVERIFIED |
| G7-S12 | With alternative D: an order exceeding the independent limit requires compromise of **both** K3 and K11 | K5 (requires both) | K11 independent of K3 (separate code, data and credential) | refuse | a common-mode bug; both views fed from the same faulty data | dual-fault tests | CONDITIONAL; UNVERIFIED |

---

## 17. Architectural alternatives (G7-R05)

| | **A. Centralized state** (K3 holds the authorization; consumption is K3's atomic transition; the gate calls K3 synchronously, the pull model) | **B. Signed capability** (K3/K4 sign a capability; the gate verifies offline; consumption and revocation are separate services) | **C. Egress boundary** (credential and network isolation) | **D. Dual control** (an independent risk check K11 must also allow) |
|---|---|---|---|---|
| Trust assumptions | K3 and K5 correct; an authenticated channel | the key is secure; the consumption ledger is authoritative; revocation propagation | K6 and L-f configured and tested | K11 is truly independent |
| Security properties | no revocation staleness; payload from K3 | offline verifiability; the payload is bound by the signature | **makes A or B non-bypassable by K1 and K2** | survives a single compromise of K3 |
| Availability cost | K3 is a dependency on the dispatch path | lower (offline), **at the cost of staleness** | none at run time; operational burden | a second dependency; false vetoes |
| Compromise behavior | K3 compromise = authority; K5 compromise = everything | key compromise = forgery (if the ledger is also offline, unlimited) | without C, **A and B are both bypassable** by anything holding the credential | needs two compromises |
| Revocation | immediate (linearized in K3) | stale up to the propagation delay (FD-G3) | n/a | n/a |
| Replay | the K3 single-use state | needs a ledger anyway, **so B does not remove the stateful component** | n/a | n/a |
| Recovery | K3 durability | ledger and key rotation | rule drift | K11 state |
| Residual | K3 is a high-value target | complexity; staleness | the administrator; configuration drift | common-mode data |

**Proposal (DERIVED reasoning, not a security claim):** **C is mandatory.** Without it, A or B constrains only well-behaved components. The core is **C + A**: the pull model, with no offline capabilities. **D is recommended** if residual-risk acceptance (FD-G10) rejects "K3 compromise = authority". B is **not** recommended in Draft 0.1:
- its offline benefit conflicts with immediate revocation;
- it still needs a stateful ledger;
- a signature adds no proof of correctness.

Property sources in C + A (+ D):
- non-bypassability comes from C;
- single-use, revocation and expiry come from A;
- payload integrity comes from A's pull model and the mapper;
- single-compromise resistance comes from D;
- detection comes from §14.

---

## 18. Adversarial scenarios (the 12 mandatory sequences plus additions)

Outcome classes:
- **P** prevents;
- **Co** contains;
- **D** detects;
- **R** supports recovery;
- **N** cannot address.

| ID | Scenario | Outcome | Notes |
|---|---|---|---|
| G7-F01 | two concurrent requests consume the same authorization | **P** (one wins at LP-CONSUME) | DERIVED; needs the V-1 tests |
| G7-F02 | revocation after verification but before transmission | **P** if before LP-DISPATCH (the abort rule); **N/Co** after (a cancel request; EAR counts) | the window is explicit |
| G7-F03 | compromised adapter attempts direct egress | **P** iff C (L-c to L-e) holds; **N** otherwise | the §12 tests |
| G7-F04 | broker accepts, acknowledgement lost | **D/R** (AMBIGUOUS → query by COID). A retry is safe only with B-DEDUP; without it, a **duplicate order is possible** if the policy retries | FD-G5 |
| G7-F05 | gateway compromised | **N** for prevention within the credential's broker permissions; **Co** only via L-f; **D** via S09 | stated in §1 |
| G7-F06 | crash after consumption, before dispatch | **P** (no transmission); **R** (resume within the deadline under the same dispatch_id, or dead) | never fresh authority |
| G7-F07 | crash after dispatch, before the outcome is recorded | **D/R** (AMBIGUOUS) | EAR keeps counting |
| G7-F08 | audit fails immediately before transmission | **P** (no durable record → no dispatch) under the FD-G4 strict option | availability cost |
| G7-F09 | a correction or bust invalidates the authorization basis | **P** if invalidation precedes LP-DISPATCH; after it, **D** plus a CANCEL authorization; the exposure effect is EAR's | EIVI R-8 readings apply |
| G7-F10 | an authorization is altered through serialization ambiguity | **P** for K2-side alteration (the pull model); **mapper defects are N until the V-6 tests are passed** | UNVERIFIED |
| G7-F11 | cancellation or modification bypasses the submission path | **P**: CANCEL is governed; MODIFY is allowlist-blocked; **N** if the credential can still call those endpoints and K5 is compromised | B-PERM |
| G7-F12 | second network interface or alternate endpoint bypasses the gate | **P** iff L-e covers every interface and hostname, and B-IPALLOW holds; otherwise **N** | the §12 tests, repeated |
| G7-F13 | human places an order via the broker website | **N** (prevention); **D** (S09 unmediated) | T9 |
| G7-F14 | backup restore resurrects consumed authorizations | **P** under the §15 restore rule; **N** if a restore is done outside governance | operational |
| G7-F15 | clock skew lets an expired authorization dispatch | **Co** (EAR still counts); a policy breach | FD-G7 |
| G7-F16 | the broker does not deduplicate COIDs and the operator retries manually | **N** (duplicate order); **D** | procedure; B-DEDUP |
| G7-F17 | K3 compromised and issues an over-limit authorization | **N** under A alone; **P** under D unless K11 is also compromised | FD-G10 |
| G7-F18 | gate credential copied to another host | **P** with B-IPALLOW; **N** without | broker evidence |
| G7-F19 | a broker endpoint alias (a new API version path) performs a modify | **P** if the allowlist is exact-match and default-deny; **N** under K5 compromise | V-7 |
| G7-F20 | a cancel races a fill | **N** (an external race); **Co** (EAR counts the order until the cancel is confirmed) | inherent |
| (Gemini 1–31, F.1–F.3) | **NOT RECEIVED** | — | Draft 0.1a |

## 19. Synthetic verification plan (design only; nothing executed)

**Harness:** an isolated network namespace containing:
- K3 (an EAR stub with a real state machine);
- K5;
- a mock broker;
- an adapter;
- a reconciler with a read-only mock credential;
- an audit store.

**No real broker, credentials or internet egress.**

**Mock broker modes:**
- deduplicates COIDs / does not;
- drops acknowledgements;
- duplicates acknowledgements;
- delays acceptance;
- rejects;
- hides an order from statements;
- accepts a modify via an alias endpoint;
- IP allowlist on / off.

| Test group | Examples | Pass criterion |
|---|---|---|
| V-1 concurrency | N parallel DISPATCH(auth_id), with revoke interleaved at every step | at most 1 consumption; at most 1 broker request; a revoke before LP-DISPATCH always aborts |
| V-2 crash and restart | kill at every write and LP boundary (systematically enumerated) | no second COID; no request for a dead authorization; AMBIGUOUS where required |
| V-3 fault injection | audit unavailable, fsync lies, K3 timeout, clock skew | fail-closed per the chosen FD postures |
| V-4 credential | search every non-gate host for the credential; use a copied credential from the adapter host | none found; the mock broker (allowlist on) rejects |
| V-5 network bypass | from the adapter namespace: direct IP, DNS, IPv6, a proxy, a second interface | every attempt fails |
| V-6 replay and mutation | replay old requests; fuzz the canonical record → mapper → broker request round trip; Unicode and numeric edge cases | no accepted request differs from the K3 record; replays are refused |
| V-7 action domain | call every non-allowlisted endpoint and method through the gate, with valid authorizations of other kinds | all are refused before any network I/O |
| V-8 audit | partial writes; chain tamper; restore from backup | detected; no dispatch on an incomplete record; the restore rule enforced |
| V-9 external ambiguity | lost acknowledgement × dedup on/off × retry policy | never two orders when dedup is off; reconciled state matches the mock's truth |
| V-10 reconciliation | a mock-broker order without a dispatch record | flagged UNMEDIATED within the period; dispatch stops (FD-G11) |

| Property class | Members |
|---|---|
| **Local** (demonstrable in the harness) | S01 to S08, S10, S12's logic; V-1 to V-10 against the mock |
| **Environmental** (needs broker documentation, infrastructure evidence or external review) | B-DEDUP, B-QUERY, B-COID, B-PERM, B-IPALLOW, B-STMT, B-MPA; real egress configuration; the host hardening of K5 |
| **Unprovable or conditional** | security under T5 to T7 (outside the model); absence of unknown broker channels; the K5 code being bug-free (only reviewable and testable, never proven) |

**A passing harness shows behavior against a mock**, not broker guarantees.

---

## 20. Environmental assumptions (all UNVERIFIED)

| ID | Assumption | Needed for |
|---|---|---|
| B-DEDUP | the broker rejects or ignores a second order with the same COID | safe retry (F04) |
| B-QUERY | order status is queryable by COID | resolving AMBIGUOUS |
| B-COID | COID format and length allow the deterministic scheme, unique per account | §10.3 |
| B-PERM | API credentials can be scoped to trade-only (no withdrawal, no admin, no key management) | §6, G7-I8 |
| B-IPALLOW | credentials can be bound to source IPs | F18, G7-I8 |
| B-STMT | statements and order lists are complete, including orders from any channel | S09 |
| B-MPA | whether the broker offers multi-party approval (if it does, gate compromise may be containable) | §5 |
| B-LIMITS | broker-side per-order and position limits exist and can be set | L-f containment |
| H-CHAN | human broker channels can be separately credentialed and locked | T9 |

## 21. Open founder decisions (none is assumed)

| ID | Decision | Alternatives | Security | Availability | Evidence that would help |
|---|---|---|---|---|---|
| FD-G1 | credential and egress custody | (a) a dedicated gate host; (b) an enclave; (c) a managed secret store with IP-bound use; (d) a broker-side sub-account | (a) to (c) all fail under gate-host compromise; (d) limits the blast radius | (b) and (c) add dependencies | broker sub-account and permission options (B-PERM) |
| FD-G2 | fail-closed versus availability | strict fail-closed; a degraded mode that allows only CANCEL; a time-boxed override | an override is an authority-expanding transition (founder invariant) | strict = outages block trading | the outage frequency of K3 and the audit store |
| FD-G3 | revocation-service outage (relevant only under B) | refuse; proceed within staleness δ | proceeding = authorization on stale state | refusing = no dispatch | — (moot under A) |
| FD-G4 | audit-store failure policy | (a) local WAL only; (b) external sink acknowledgement required; (c) WAL plus asynchronous with bounded lag | (b) is strongest for completeness | (b) adds a dependency per order | the audit sink's reliability |
| FD-G5 | retry after an ambiguous transmission | (a) never retry; query only; (b) retry with the same COID only under B-DEDUP; (c) a human decides | (a) safest | (a) may lose intended orders | broker dedup documentation |
| FD-G6 | client order id policy | deterministic from auth_id (proposed); random plus a mapping | deterministic aids dedup and reconciliation | — | B-COID |
| FD-G7 | clock and expiry bounds | skew_margin, δ_d, TTLs | tighter = fewer late dispatches | tighter = more aborts | measured clock drift |
| FD-G8 | consequential action scope | NEW + CANCEL (proposed); add MODIFY; add account actions | every addition widens the attack surface | — | strategy needs |
| FD-G9 | threat model for administrators and host compromise | out of scope (proposed Draft 0.1); in scope (needs B-MPA or a hardware root of trust plus external attestation) | in scope may be **impossible** without broker support | — | B-MPA; attestation options |
| FD-G10 | acceptable residual risk | accept "K3 compromise = authority within broker limits"; require D | D needs two compromises | D costs a second system | the cost of K11 |
| FD-G11 | resumption after an ambiguous or unmediated outcome | automatic after reconciliation; founder sign-off | sign-off avoids normalizing anomalies | slower | incident frequency in the harness |

## 22. Residual risks and explicit limitations

1. Gate compromise, gate-host administrator compromise and broker-account compromise outside Sentinel are **not preventable by Sentinel**. They are bounded only by broker-side controls. That bound is **UNVERIFIED and possibly UNBOUNDED** (T5 to T7, T9).
2. No exactly-once external execution. A duplicate order is possible under ¬B-DEDUP whenever any retry happens.
3. Detection (S09) depends on statement completeness and is retrospective. The exposure between an unmediated order and its detection is **UNBOUNDED** unless broker limits apply.
4. The request mapper is a single point of semantic error.
5. Configuration drift in egress controls can silently reopen bypass paths. Only repeated testing counters it.
6. G-07 assumes EAR's interface (G-EAR-1 to G-EAR-3). EAR has no dispatch layer today (G7-C05).

**Conflict register:**

| ID | Conflict | Status |
|---|---|---|
| G7-C01 | immediate revocation (A) versus offline availability (B) | open: FD-G3 / alternative choice |
| G7-C02 | audit completeness requires K5 honesty, yet K5 is the main threat target | open: mitigated by S09 (detection only) |
| G7-C03 | fail-closed (FD-G2) versus the founder invariant: an availability override *is* an authority-expanding transition | open |
| G7-C04 | CANCEL is exposure-reducing in EAR terms, yet it can remove protective orders | governed as consequential (§6); the protective-order semantics are undefined |
| G7-C05 | EAR consume corresponds to G-07 consumption; G-07's dispatch states have no EAR counterpart | open: an interface only, by directive |
| G7-C06 | Gemini's findings are not received, so possible conflicts with this draft are unknown | open |

## 23. Recommendation for independent review, and traceability

**Review order (per the dispatch):** GPT hostile review → Gemini challenge with GPT's review → Claude's revision record → founder decision. **Before GPT reviews, attach Gemini's review and GPT's assessment so that Draft 0.1a can complete the mapping.** A specification that survives model review is not thereby authorized for implementation.

| Source item | Treatment |
|---|---|
| G7-R01 authorization-to-transmission race | §10.1, §10.2 (Q1 to Q6), §13 A/B, S05, S06, F02 |
| G7-R02 consumption vs dispatch vs execution | §10.3, §10.4, §13, S02, S03, S10, F04, F06, F07, F16 |
| G7-R03 audit commitment | §14, §15, S08, F08, FD-G4 |
| G7-R04 trust-boundary decomposition | §5 (K1 to K11), the separation-of-duties finding, HSM / enclave / container analysis |
| G7-R05 alternatives | §17 (A, B, C, D, hybrid with property sources) |
| G7-R06 action scope | §6, G6-1, S07, F11, F19, FD-G8 |
| G7-R07 G7-I8 | §12 (layers L-a to L-f, refined text, test list), the G7-I8 row of §16 |
| Mandatory sequences 1–12 | G7-F01 to G7-F12 |
| Founder-decision list (11 items) | FD-G1 to FD-G11 |
| **Gemini review: findings, G7-I1 to G7-I7, scenarios 1–31, F.1 to F.3** | **NOT RECEIVED: mapping pending (Draft 0.1a)** |
| **GPT assessment: beyond R01 to R07 as quoted in the dispatch** | **NOT RECEIVED** |

*End of G-07 Draft 0.1. Specification only. Nothing implemented, tested or executed.*
