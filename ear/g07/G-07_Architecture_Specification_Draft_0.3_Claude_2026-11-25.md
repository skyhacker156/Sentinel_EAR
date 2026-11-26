# G-07 Architecture Specification, Draft 0.3: response to the GPT adversarial review

**Date:** 2026-11-25 | **Author:** Claude, Specification Lead
**Responds to:** "GPT Independent Adversarial Review: G-07 Draft 0.2a" (2026-11-25), §§1 to 9.
**Amends:** Draft 0.1 (`55141ae6…`), 0.2 (`f0404b71…`), 0.2a (`b87ac1c0…`). Changes are marked **[A0.3-n]**. The review IDs of Gemini (A.1 to F.3) and GPT are preserved.
**Classification:** DESIGN ONLY / NOT IMPLEMENTED / NOT VERIFIED. No code, credentials or orders. **SL-PT-001's authorization status is unchanged.** Implementation is NOT recommended (agreeing with GPT).
**Labels:** DERIVED / OBSERVED / ASSUMED / CONDITIONAL / UNVERIFIED / UNBOUNDED. **Nothing is COMPUTED.**

## 0. Disposition of GPT §9 (the required Draft 0.3 changes)

| # | GPT item | Disposition | Where |
|---|---|---|---|
| 1 | five "moot by design" mappings (A.2, B.6, B.7, C.4, F.3) | **ACCEPTED: "moot" withdrawn.** A.2, B.6 and B.7 are resolved by a design change (the polling executor, §2). C.4 and F.3 are made CONDITIONAL on K3 consistency (§3) | §2, §3, §8 |
| 2 | LP-DISPATCH vs first-byte inconsistency in I4 | **ACCEPTED, resolved** by defining a pre-send check point and an expiry margin (§1). The residual is stated, not removed | §1 |
| 3 | I3/I10 split; FD-G16 | **ACCEPTED.** The I3 falsifier is corrected and GPT's I10 text adopted. FD-G16 stays a founder decision; GPT recommends (a), and Claude concurs | §4, §10 |
| 4 | caller-trigger authority | **ACCEPTED; resolved more strongly than proposed.** K2 has **no** trigger path; K5 polls K3 for eligible authorizations | §2 |
| 5 | egress isolation in G7-C10 | **ACCEPTED.** "Moot" is withdrawn for signatures; a nine-dimension comparison is added | §7 |
| 6 | account containment is conditional | **ACCEPTED: GPT's replacement text adopted verbatim** | §6 |
| 7 | reconciler credential conflict (E.5) | **ACCEPTED as a design conflict.** Four options; founder decision FD-G17 | §5 |
| 8 | stale invariant numbering in the SL-PT-001 map | **ACCEPTED: a Claude defect.** Map rebuilt | §9 |
| 9 | I9 narrowed to provenance | **ACCEPTED: renamed and rewritten** (GPT text) | §4 |
| 10 | conditional broker semantics in I10 | **ACCEPTED** | §4 |

**Rejected:** none. **Where Claude adds to GPT:** §1 (closing the I4 window with a pre-send check) and §2 (removing K2 from the execution path, rather than authenticating it).

---

## 1. [A0.3-1] Release versus initiation (resolves GPT item 2; B.2, B.3, C.1, C.7)

**Defect:** Draft 0.2a set t_rel = LP-DISPATCH (the write-ahead record) and set initiation = the first outbound byte. Between them, expiry, revocation or new evidence could arrive, and nothing checked again.

**New lifecycle points** (replacing Draft 0.1 §10.1 points 5 to 7):

| Point | Name | What happens | Locally atomic? |
|---|---|---|---|
| 5 | **LP-CONSUME** | K3: ACTIVE ∧ ¬revoked ∧ ¬expired ∧ eligible ∧ Π → CONSUMED, bound to the dispatch_id | yes (K3) |
| 6 | **LP-WAL** | K5: a durable DISPATCHING(dispatch_id, COID, payload digest) record | yes (K5) |
| 6′ | **LP-PRESEND** (new) | K5: a **final synchronous validity check** against K3 (not revoked, not invalidated, `now ≤ expires_at − δ_send`) plus the configuration identity check (E.3). It is performed **after LP-WAL** and **immediately before the send call, with no other blocking operation in between**. On failure: write NOT_SENT and stop. Nothing was transmitted, so NOT_SENT is locally certain | yes (K5 decision; the K3 read is linearizable per §3) |
| 7 | first outbound byte (**initiation**, review term T2) | the send call begins | no |

**Definitions:**
- **t_rel := LP-PRESEND.** G7-I4 is evaluated at LP-PRESEND.
- **Initiation:** the first outbound byte (point 7).
- **Released:** a request that has passed LP-PRESEND.

**Residual, stated:**
- **The window from LP-PRESEND to point 7** contains only the send call itself. Revocation linearized in K3 after the LP-PRESEND read is **post-release**: it cannot be prevented, and it becomes a CANCEL authorization plus continued exposure counting.
- **Expiry cannot occur in that window** if the send completes within δ_send (CONDITIONAL on δ_send exceeding the send duration; a send exceeding δ_send is logged as SEND_OVERRAN).
- **A crash between LP-PRESEND and point 7** gives AMBIGUOUS, not NOT_SENT. The only state K5 can prove is "a pre-send check passed".
- **No claim is made that a local check is atomic with remote acceptance.** DERIVED.

**Revised G7-I4:** *No request is released (passes LP-PRESEND) if, at the LP-PRESEND read, the authorization is expired or within δ_send of expiry, or is REVOKED, SUSPENDED or INVALIDATED. Revocation linearized after that read is post-release and is handled by cancellation and exposure accounting, not prevention.*

**Falsifier:** a send whose LP-PRESEND record shows expired, revoked, suspended or invalidated state, or a send with no LP-PRESEND record.

---

## 2. [A0.3-2] Trigger authority: the polling executor (resolves GPT items 1 and 4; A.2, B.6, B.7, C.8)

**Defect:** in Draft 0.1, K2 sent `DISPATCH(auth_id)` to K5. Even with the payload pulled from K3, possession of an id plus the ability to call K5 made the id a **bearer selector**: unauthorized triggering, context rebinding and early redemption were all possible (GPT counterexamples on A.2, B.6, B.7).

**Change (proposal):**
1. **K2 has no interface to K5.** There is no `DISPATCH` call. K2 is removed from the execution path. Its remaining role, translating intelligence output into proposals, ends at the policy engine (K3).
2. **K5 polls K3** over K5's own authenticated channel for authorizations that are **eligible** and **assigned to this executor**: state ACTIVE, `not_before ≤ now ≤ expires_at − δ_send`, `executor_id = K5's identity`, `account` and `venue` = K5's configured context. K5 processes them in issuance order.
3. **Authorization records carry an execution-context binding** (new mandatory fields): executor_id, account, venue, action type (NEW / CANCEL), cancel target (for CANCEL), not_before, expires_at.
   - LP-CONSUME requires the context to match the consuming K5.
   - **A record cannot be consumed in another context** (closes B.6 context rebinding).
4. **Timing authority** belongs to the authorization's window [not_before, expires_at − δ_send], which K3 sets at issuance.
   - Dispatch anywhere in that window is authorized; finer timing intent must be expressed as a tighter window.
   - No caller can choose timing (closes B.7 early redemption, **except** by compromising K3 or K5: C3 / E.2).
5. **K2's identity:** GPT's proposed text (a least-privilege identity to K5) is **superseded**. K2 holds no credential to K5 and none to the broker. Where K2 must submit proposals to K3, it uses a K3-proposal-only identity that cannot create authorizations; only K3's policy evaluation creates them.

**New mapping:**

| Surface | Status after the change |
|---|---|
| A.2 | **payload forgery:** addressed by the pull model. **Unauthorized triggering:** addressed by the absence of any trigger path. Residual: K3 compromise (C3) |
| B.6 | **payload rebinding:** prevented by canonical lookup. **Context or caller rebinding:** prevented by the LP-CONSUME context check. Test: cross-account, cross-executor, cross-venue and cross-action consumption attempts |
| B.7 | **leak of an id:** confers nothing, because there is no redemption interface for non-K5 principals. **Early redemption:** impossible outside the window. Residual: K5 compromise |

**Status:** all three are DERIVED, CONDITIONAL on K3 and K5 integrity (G7-A1) and K5 identity authentication. UNVERIFIED.

**Cost (DERIVED):** latency up to one poll interval; K3 becomes a dependency of the dispatch path (fail closed if it is unreachable; FD-G2).

---

## 3. [A0.3-3] K3 consistency (resolves C.4 and F.3)

**Assumption G7-A2 (new, explicit):** reads of authorization state at LP-CONSUME and LP-PRESEND are **linearizable**. They observe every K3 write committed before the read.
- **Satisfied by design** if K3 is a single authoritative store whose reads at these points take the same serialization lock as writes (as in EAR's fold discipline).
- **If K3 is ever replicated,** reads at these points must go to the leader under a valid lease or a quorum. **Replicas, caches, proxies and middleware must never serve these reads.**
- A K5 that cannot obtain a linearizable read **fails closed**.

**Version check (new):** every K3 response carries {schema version, policy hash, configuration hash}. K5 refuses on any mismatch with its pinned expectations.

| Surface | New status |
|---|---|
| C.4 | **CONDITIONAL on G7-A2** (was "DERIVED / moot"). Test: stale-replica injection, split-brain, and a version mismatch, each expecting refusal |
| F.3 | **CONDITIONAL on G7-A2 and on no stale fallback anywhere in the path** (was "DERIVED / moot"). Test: partition with a reachable stale replica, expecting refusal |

---

## 4. [A0.3-4] Invariant register G7-I1 to G7-I10 (current; supersedes 0.2a §2 text where it differs)

| ID | Final text (summary) | Class | Verdict (GPT) → action | Status |
|---|---|---|---|---|
| **I1** No Unauthenticated Egress | every **consequential** request leaving the boundary (NEW, CANCEL; never read-only queries) has an authorization valid at t_rel = LP-PRESEND. Scope: egress *by the boundary* | D-REQ | RETAIN, NARROW → done | UNVERIFIED |
| **I2** Exact Scope & Payload Binding | the released request matches the authorization on account, venue, instrument, side, quantity **and units**, order type, price, **TIF**, **client order id**, **action type and cancel target**. Verified by (a) a mapper round trip **and (b) an independent decode**: the venue's echoed order object (Alpaca returns the order on submission) is compared field by field with the authorization, using decoding code separate from the mapper | D-REQ | RETAIN → fields expanded; independent comparison | UNVERIFIED |
| **I3** At-Most-Once Local Consumption | at most one successful transition to CONSUMED per authorization id, across concurrent callers, restarts and recovery. **Falsifier: two successful CONSUMED transitions for one id** | D-REQ | RETAIN → falsifier corrected | UNVERIFIED |
| **I4** Temporal & Revocation Validity at Release | revised text in §1 | D-REQ + ASM (clock, G7-A3) | REVISE → done | UNVERIFIED |
| **I5** Non-Bypassable Egress Path | the network and process topology prevents any process other than K5 from using the governed egress path, or an equivalent local path to the venue | D-REQ (deployment) | RETAIN → deployment-level test (§8) | UNVERIFIED |
| **I6** Ambiguous Outcome Non-Optimism | an unknown outcome stays AMBIGUOUS while broker evidence is incomplete. It is never inferred as rejected from a timeout and never re-authorized automatically | D-REQ | RETAIN | UNVERIFIED |
| **I7** Audit Lineage | every attempt **that reaches the boundary** (allowed, refused, NOT_SENT, ambiguous) has a durable record. **No send without a durable LP-WAL record.** Four failure cases are distinguished (§8, E.6). Out-of-boundary attempts are detected only by reconciliation | D-REQ | RETAIN, NARROW → done | UNVERIFIED |
| **I8** No Unmediated External Authority | **environmental acceptance condition**, not an application invariant: no other credential, permission, human channel or path can perform consequential actions on the account | ENV | RETAIN AS ACCEPTANCE CONDITION | UNVERIFIED; **false in the current SL-PT-001 deployment** |
| **I9** Evaluation Provenance and Input Cut | *(GPT text, adopted)* every authorization records the policy and configuration versions, the evaluation implementation identity, the input-state reference or event watermark, and the result. The decision is reconstructible and independently recomputable from those inputs. **This establishes provenance and reproducibility, not policy correctness, source truth, or completeness of unreceived information** | D-REQ | REVISE AND RENAME → done | UNVERIFIED |
| **I10** No Uncontrolled External Duplicate | *(GPT text, adopted)* one client order id per authorization; never a retry under a new id; a second submission with the same id is **prohibited** unless the broker's idempotency semantics are independently established for that venue and environment; every observed broker order reconciles to exactly one authorization; duplicates or uncorrelated orders cause a discrepancy and **halt further authorization** | D-REQ + ENV (B-DEDUP) | RETAIN AS CONDITIONAL | CONDITIONAL; UNVERIFIED |

**Assumptions:**
- **G7-A1:** K3, K5 and the K5 host are uncompromised.
- **G7-A2:** linearizable authorization reads (§3).
- **G7-A3 (new; GPT C.6):** a defined authoritative time source.
  - Expiry and not_before use **wall-clock time from K3's clock** at issuance and K5's clock at check, with |skew| ≤ σ measured at K5 start and periodically.
  - **Elapsed** intervals (δ_send, poll timeouts) use monotonic clocks.
  - After a restart, K5 re-establishes the skew before polling.
  - **If σ cannot be established, K5 fails closed.**

**I5 and I8 stay separate** (agreeing with GPT). I5 without I8 is insufficient; I8 without a tested deployment boundary is an unverified assertion.

---

## 5. [A0.3-5] Reconciler credential conflict (E.5)

**The conflict:** independent detection (S09, L-3, E.2's detection path) needs a read path to broker records that **K5 does not control**. Draft 0.1 assumed a "read-only credential". **Whether Alpaca offers read-only Trading API keys is UNVERIFIED.** A second trade-capable key is another external authority and **violates I8**, whatever the reconciler intends.

| Option | Independence from K5 | I8 impact | Cost |
|---|---|---|---|
| R-a: the reconciler reads through K5 | **none** (a compromised K5 can lie) | none | detection fails under E.2 |
| R-b: a second trade-capable key on an isolated reconciler host | high | **violates I8** (a new authority) | must then be governed as a second boundary |
| R-c: the founder reviews broker statements or the dashboard order history by hand at a fixed cadence | high (a human channel, read use) | the human channel already exists (I8 acknowledges it) | manual; slow; not automatable |
| R-d: broker-originated **out-of-band confirmations** (Alpaca's account configuration has a `trade_confirm_email` setting, all or none, per Draft 0.2 [S4]) delivered to the founder's mailbox and parsed by a reconciler with **no broker credential** | high, if the mailbox is not reachable from K5 | **none** | **UNVERIFIED** that crypto and paper orders generate confirmations; email delivery is not guaranteed (it detects, it is not complete) |

**Proposal:** R-d plus R-c for SL-PT-001, pending verification; **reject R-b** unless it is governed as a boundary itself. This is **founder decision FD-G17**.

**Consequence for E.2:** detection of a compromised K5 holds only under R-c or R-d (GPT E.2 finding, adopted).

---

## 6. [A0.3-6] Account containment (replaces Draft 0.2 §2, row 2 conclusion; GPT text adopted verbatim)

> Account segregation and account size may reduce the maximum exposure of a compromised execution environment, but they are not treated as a verified loss bound until the broker-enforced account type, buying power, margin multiplier, shorting permissions, funding paths, and account-level configuration permissions have been established. Application-level checks and startup read-backs do not constitute broker-enforced containment. For SL-PT-001, this is a paper-account containment assumption and does not establish live financial-risk bounds.

**Added:**
- Paper trading carries no direct financial loss. SL-PT-001 can still test whether simulated unauthorized activity is **detected and contained**.
- **The Trading API exposes account-configuration changes** (Draft 0.2 [S4]: a PATCH on the configurations endpoint). Unless shown otherwise, assume **a compromised K5 can change the multiplier and shorting settings**. That is a further reason the containment is not a verified bound (UNVERIFIED).

**Revised narrowed claim (Draft 0.2 §2):** prevention applies to components that:
- (i) hold no broker credential;
- (ii) cannot obtain one;
- (iii) have no broker egress;
- (iv) **have no trigger path to K5** (§2).

It also requires K5 and its host to be uncompromised and the account's other channels to be within assumptions. **"Unprivileged" means (i) to (iv).**

---

## 7. [A0.3-7] Alternatives comparison (G7-C10; replaces Draft 0.2a §4's "moot" conclusion)

| Dimension | Pull model (K5 reads the authorization from K3) | Signed capability (K5 verifies a signature; synchronous state checks) |
|---|---|---|
| 1. Authorization freshness | a linearizable read at LP-CONSUME and LP-PRESEND (G7-A2) | the same, **if** synchronous checks are kept; otherwise stale |
| 2. Revocation | immediate at the reads | immediate only with a synchronous check; otherwise bounded by propagation |
| 3. Payload integrity | the canonical record from K3 over an authenticated channel | the signature binds the payload, even across untrusted relays |
| 4. Caller authority | no caller (the polling executor, §2) | a holder of the capability can present it, so it **needs separate caller binding** |
| 5. Credential custody | K5 holds the venue key; K3 holds none | as pull, plus **signing-key custody** (a new high-value secret) |
| 6. Egress isolation | **required, orthogonal** | **required, orthogonal** |
| 7. Compromise domains | K3 compromise = authority; K5 compromise = everything | **adds** signing-key compromise = forgery; K3 compromise as pull |
| 8. Availability under partition | K3 unreachable → no dispatch | offline verification possible **only by giving up 1 and 2** |
| 9. Independent reconstruction | from the K3 log | the signature gives third-party-verifiable provenance **without trusting K3's log** (a real advantage) |

**Conclusion (DERIVED; replacing "moot"):** in this architecture, where K5 can reach K3 synchronously and freshness is mandatory, signatures add one real benefit, (9) provenance verifiable without K3, at the cost of a new secret and a new compromise domain. **Not adopted for Draft 0.3; not universally moot.** Reconsider if independent provenance becomes a requirement (I9 could use it).

---

## 8. [A0.3-8] Surface updates (only the rows GPT changed; everything else stands as in 0.2a §3)

| Surface | Update |
|---|---|
| A.1 | add an isolation test: K2 under its **own OS identity** cannot read K5's environment, files, process memory or inherited handles. **E.1 stays a separate residual** |
| A.2 | §2. Status: "payload forgery addressed; unauthorized triggering addressed by having no trigger path; CONDITIONAL on G7-A1" |
| A.3 | the I2 field set expanded; independent decode via the venue's echoed order (§4 I2) |
| A.4 | tests: environment variables, filesystem and secret store, process inspection, inherited handles and sockets, egress from the second process. **A same-host result does not transfer to a production host** |
| A.5 | on the founder's machine this is deliberately non-isolated. A clean-environment refusal is **not** generalized to it |
| B.1 | split: (1) repeated local consumption → I3; (2) repeated external submission with the same COID → I10 and broker semantics |
| B.2, B.3, C.1, C.7 | resolved per §1. The residual is the LP-PRESEND → first-byte window (revocation only; expiry is covered by δ_send) |
| B.4, B.5 | tests add storage rollback and restore paths |
| B.6, B.7 | §2 |
| C.2 | the reservation ledger stays conservative while outcomes are unknown: fills during the interval, other reservations, unmediated orders, partial fills, corrections and busts, and pending cancels all stay counted (EAR R-15″ and the SL-PT-001 §5 reservations) |
| C.4, F.3 | §3 |
| C.5 | crash points: after LP-CONSUME, after LP-WAL, after LP-PRESEND, after the first byte, after broker acceptance, before persisting the local ack |
| C.6 | G7-A3 |
| D.3 | **"duplicate COID rejected" ≠ "idempotent returning the original order"**: the exact semantics must be established before any I10 retry (FD-G16) |
| D.4 | renamed: "broker event arrives before the local send-outcome / ack record". **Added: a broker order with no matching LP-WAL record** → UNMEDIATED, halt (I10) |
| D.6 | a harness that hides a record tests the *reconciliation response*, not the broker's reporting completeness (B-STMT stays UNVERIFIED) |
| E.1 | to be verified **in the actual deployment** (SL-PT-001: known violated) |
| E.2 | detection holds only if the reconciliation path is independent of K5 (§5: R-c or R-d). A modelled malicious-K5 test shows harness behaviour only |
| E.3 | **configuration identity is verified at every LP-PRESEND**, not only at startup; a mismatch disables dispatch. Runtime configuration is immutable (a change requires restart plus a founder record). Residual: an administrator with write access to the running host (= G7-A1) |
| E.4 | a deployment-level inventory: interfaces, proxies, DNS, IPv6, alternate hosts |
| E.5 | §5 |
| E.6 | four cases: (1) durable LP-WAL unavailable → **no dispatch**; (2) refusal record unavailable → refuse anyway, and raise an alert through a secondary channel; (3) audit sink unavailable after a durable LP-WAL → dispatch allowed **only if FD-G4 = local-WAL option**, otherwise no dispatch; (4) external anchoring unavailable → dispatch allowed, anchoring backlog flagged (tamper-evidence is delayed, not lost). I7 is claimed only under the chosen FD-G4 option |
| F.1 | independent decode (I2 (b)) |
| F.2 | test at the network boundary (socket kill or packet drop mid-write), not only application exceptions. The result stays AMBIGUOUS; query by the original COID |

---

## 9. [A0.3-9] SL-PT-001 integration map, rebuilt with the current numbering (replaces Draft 0.2 §6)

| Stage | Can test (current IDs) | Cannot establish | Credit rule |
|---|---|---|---|
| **A: shadow** (no keys) | **I9** (provenance, input cut, recomputation); policy and configuration version recording; stale data and TTL in the shadow harness (the **I4** logic only, not release); log completeness and hash-chain verification (**I7** record keeping, not egress) | broker authorization; mediation; credential isolation; idempotency; external reconciliation | **no Stage A result is credited to I1, I2, I3 (external), I5, I6, I8 or I10** |
| **B: paper API** (paper keys, founder's machine) | **I2** (approved vs submitted, plus the independent decode via the echoed order); **I3** (if exercised); **I6** (lifecycle, partial fills); **I7** (the LP-WAL and LP-PRESEND records); reconciliation against Alpaca records; the **observed** Alpaca paper query-by-COID and duplicate-COID behaviour (input to I10) | production credential isolation; live broker behaviour; production egress; execution quality; absence of other channels | **Stage B is a known noncompliant deployment for I8 (and for I5).** It is not a demonstration of mediation |
| **C: adversarial** | **I3** (replay, concurrent and crash consumption); **I4** (expiry and revocation injection at every LP, including the LP-PRESEND window); **I6** (lost ack, partial write); **I10** (duplicate COID on Alpaca paper); **I1 and I8 negative results** (dashboard and alternate-key bypass: expected **success, then detection**); §2 context-rebinding tests; modelled compromise of K3 and K5 | resistance to real host compromise; production key isolation; live idempotency; absence of unknown channels | a modelled malicious-K5 result shows **harness behaviour under injection only** |

**Required record per test result** (GPT §8, adopted):
- the exact invariant;
- the environment (local / paper API / synthetic);
- the deployment and credential arrangement;
- the expected and observed results;
- the evidence artifact;
- the assurance boundary;
- the residual.

**"Passed G-07" is never used as a status.**

---

## 10. [A0.3-10] Founder decisions

| ID | Decision | Positions |
|---|---|---|
| **FD-G16** | same-COID retry | GPT recommends (a), no second submission, for SL-PT-001; **Claude concurs**. Not decided here. If (a): an ambiguous outcome is resolved by query only, otherwise it stays AMBIGUOUS, and I10's retry clause is inactive |
| **FD-G17** (new) | reconciliation path independent of K5 | options R-a to R-d (§5); proposal R-d + R-c; reject R-b |
| **FD-G18** (new) | the time source and skew bound σ (G7-A3); δ_send | — |
| FD-G1 to FD-G15 | carried | — |

## 11. [A0.3-11] Required changes to SL-PT-001 (listed for its v0.2; **not applied here**, as a separate workstream)

| ID | Change |
|---|---|
| PT-A1 | §7 Stage B: the executor **polls** for eligible, context-bound authorizations. There is no requester-supplied `auth_id` path (G-07 §2) |
| PT-A2 | add the LP-PRESEND check and δ_send to the paper-execution procedure (G-07 §1) |
| PT-A3 | authorization records gain executor_id, venue, not_before and the action type (G-07 §2) |
| PT-A4 | reconciliation path per FD-G17; enable and verify Alpaca trade-confirmation email if R-d is chosen |
| PT-A5 | the I2 independent decode: compare the echoed Alpaca order with the authorization |
| PT-A6 | the per-test record fields (§9), and the credit rule table |

## 12. [A0.3-12] UNVERIFIED / UNBOUNDED delta

- **Added, UNVERIFIED:**
  - G7-A2 (linearizable reads) for any real K3;
  - G7-A3 (time source);
  - Alpaca's read-only key availability;
  - Alpaca trade-confirmation emails for crypto and paper;
  - whether the Alpaca Trading API can change the account configuration (assumed yes);
  - whether the echoed order object reflects the venue's accepted state.
- **Changed:**
  - A.2, B.6, B.7 move from "DERIVED / moot" to "DERIVED under the §2 design change; CONDITIONAL on G7-A1";
  - C.4, F.3 move from "DERIVED / moot" to "CONDITIONAL on G7-A2".
- **UNBOUNDED (unchanged):** loss under compromise of K5, its host or a credential, now explicitly **not** bounded by account configuration, which a compromised K5 may be able to change (§6).

*End of Draft 0.3. Design only. Nothing implemented, tested or executed.*
