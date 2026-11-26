# G-07 Architecture Specification, Draft 0.2a: hostile-review integration amendment

**Date:** 2026-11-25 | **Author:** Claude, Specification Lead
**Integrates:** "Independent Hostile Architectural Review: G-07 Authorization-to-Execution Enforcement" (Gemini, 2026-11-24; Parts I to X; received 2026-11-25). The review itself is preserved as the underlying record and is **not reproduced** here.
**Amends:** Draft 0.1 (`55141ae6…`) and Draft 0.2 (`f0404b71…`). Every change is marked **[A0.2a-n]**.
**Classification:** DESIGN ONLY. Nothing implemented, tested or executed. No credentials were created and no orders were placed. SL-PT-001's authorization status is unchanged.
**Labels:** DERIVED / OBSERVED / ASSUMED / CONDITIONAL / UNVERIFIED / UNBOUNDED. **Nothing is COMPUTED.**

**Supersedes:**
- Draft 0.2 §3: the RECONSTRUCTED G7-I1 to G7-I7 are withdrawn and replaced by the review's text.
- Draft 0.2 §5 row Z: the inventory gap is closed by §3 below.

Everything else in Draft 0.2 stands.

---

## 1. [A0.2a-1] Definitions of the eight loaded terms

The review's definitions (Part I) are adopted. Each is bound to the Draft 0.1 lifecycle points.

| # | Term | Review definition (summary) | Binding to Draft 0.1 §10 | Refinement |
|---|---|---|---|---|
| T1 | consequential external action | any action that alters external state or creates external liability: submissions, cancels, modifications, transfers, instructions | §6 action domain | **Adopted.** The *governed* scope (NEW, CANCEL) is narrower than the *consequential* scope. Everything consequential but ungoverned must be **technically impossible**, not merely out of scope (§6 of Draft 0.1, G7-I5, G7-I8) |
| T2 | initiated | the first external side effect, or the first outbound frame | **LP point 7** (first outbound byte) | adopted |
| T3 | currently valid | a point-in-time predicate evaluated at enforcement, never cached | evaluated at **LP-CONSUME** and re-checked at **LP-DISPATCH** | adopted. "Release time" t_rel in G7-I1 and G7-I4 is defined as **LP-DISPATCH**. The window from LP-DISPATCH to LP 7 is the residual noted in review C.1 |
| T4 | independently verified | the boundary uses its own trusted state, never a caller's claim | the pull model: K5 fetches the authorization by id from K3 | adopted |
| T5 | non-replayed | at most one acceptance per token; **not** exactly-once external execution | LP-CONSUME (G7-I3) | adopted, with the G7-I3 falsifier conflict in §2 |
| T6 | enforcement boundary | from authenticated ingress at the gate to the external egress point | K5 | adopted. *Note:* on bearer-credential venues, the boundary is real only if no other holder of the credential exists (G7-I8) |
| T7 | ambiguous external behaviour | maps to uncertainty states, never to success or a blind retry | Draft 0.1 §13 B, AMBIGUOUS | adopted |
| T8 | required assumptions | isolation, key custody, clock bounds, non-bypassable routing | Draft 0.2 §4 TB-1 to TB-10 | adopted. **Broker-side assumptions are added** (TB-5, TB-6, TB-8, TB-9), which the review's list does not name |

---

## 2. [A0.2a-2] Invariant register G7-I1 to G7-I8 (replaces Draft 0.2 §3)

**Columns:**
- *Text*: the review's statement, verbatim in substance;
- *Class*: D-REQ (derived requirement), ASM (assumption) or ENV (environmental property);
- *Draft 0.2 reconstructed #*: which withdrawn row covered it.

| ID | Text (review Part IV) | Layer | Class | Mechanism | Falsifier (review) and refinement | Not establishable by application tests | Draft 0.2 reconstructed # | Status |
|---|---|---|---|---|---|---|---|---|
| **G7-I1** No Unauthenticated Egress | every external request leaving the boundary has a verifiable authorization valid at t_rel | A + B | D-REQ | the pull model; K3 consumption; K5 is the only sender | "any send without a valid auth". **Refinement:** detectable only for sends *by the boundary*. A send by a non-boundary credential holder (E.1) is G7-I8's domain | sends outside K5 | (#1 partly) | UNVERIFIED |
| **G7-I2** Exact Scope & Payload Binding | every released request matches the authorization on instrument, account, side, qty, order type/price, venue | A | D-REQ | the pull model (parameters come from K3); a pinned mapper with a round-trip check; the typed canonical encoding | "any released request differing". **Add TIF and client_order_id** to the bound fields (both change external effect or identity) | mapper correctness on untested inputs | #4 | UNVERIFIED |
| **G7-I3** At-Most-Once Local Consumption | at most one transition to CONSUMED per tid, across callers, threads and restarts | A | D-REQ | K3 LP-CONSUME (atomic CAS, durable) | "two distinct external submissions authorized by the same tid". **⚠ CONFLICT (G7-C07):** a retry that reuses the same client order id after AMBIGUOUS (Draft 0.1 §10.4, permitted only under B-DEDUP) *is* two submissions for one tid. **Proposed refinement:** split the falsifier into (a) two CONSUMED transitions for one tid (local; G7-I3) and (b) two **external orders** for one tid (venue; the new G7-I10). The choice is founder decision FD-G16 | storage rollback (ASSUMED none) | #2 | UNVERIFIED |
| **G7-I4** Temporal & Revocation Validity at Release | no release if t_rel > expires_at, or the authorization is REVOKED / SUSPENDED / INVALIDATED as of t_rel | A | D-REQ (+ ASM: clock bound) | a synchronous K3 read at LP-DISPATCH; the dispatch deadline; skew_margin | "any release of expired, revoked or suspended". Adopted | clock integrity across deployments | #3 | UNVERIFIED |
| **G7-I5** Non-Bypassable Egress Path | no process outside the boundary can invoke external execution egress | B | D-REQ (topology) + ENV | OS and IPC isolation; network egress control | "any successful external call originating outside the boundary". **Relation to G7-I8:** I5 concerns *invoking the boundary's path or an equivalent local path*; I8 concerns *holding independent authority* (credentials, human channels, broker-side). **On bearer-credential venues, I5 without I8 is ineffective:** any credential holder bypasses I5 with a different path | that no second credential exists; that egress rules hold on every host | #5 | UNVERIFIED |
| **G7-I6** Ambiguous Outcome Non-Optimism | an unknown outcome is never marked confirmed or rejected, and never re-authorized automatically without reconciliation | C | D-REQ | Draft 0.1 §13 B; query by client order id | "blind re-authorization or false state assertion". Adopted | completeness of the broker query (B-QUERY, B-STMT) | #6 | UNVERIFIED |
| **G7-I7** Audit Lineage for Every Attempt | every allowed, denied or ambiguous egress attempt has an append-only audit record (tid, payload digest, time or sequence, outcome) | A/C | D-REQ | write-ahead dispatch record before send; refusal records | "an attempt with no record, barring declared audit-failure behaviour". **Refinement:** (a) scope it to attempts *that reach the boundary*, since out-of-boundary attempts cannot be logged by the boundary and are detected only by reconciliation (L-3); (b) the escape clause must be **closed** by the fail-closed rule (no send without a durable record; FD-G4), or I7 is unfalsifiable | attempts outside the boundary | (Draft 0.2 #7 covered duplicates, not audit: **renumbered to G7-I10**) | UNVERIFIED |
| **G7-I8** No Unmediated External Authority | no component outside the boundary possesses credentials, permissions or alternate paths sufficient to perform consequential external action | B | **ENV** (deployment and broker account) | credential custody; OS access; egress control; **broker-side** inventory, scope, IP binding where offered; MFA on human channels | an inventory finding a second credential path; a successful action from outside. **On Alpaca's Trading API, key-holders are not IP-bound** (Draft 0.2 [S1, S2], unofficial), so the only containment is account segregation and size | everything that matters (Draft 0.2 §3) | GIVEN | UNVERIFIED in general; **not satisfied in SL-PT-001** |

**Proposed additions (Claude; not in the review; flagged as proposals):**

| ID | Statement | Why it is needed | Status |
|---|---|---|---|
| **G7-I9** Correct Evaluation Basis | an authorization is issued only by the current, hashed policy version, evaluated on a state containing every item received before the issuance point | the review's I1 to I7 assume the authorization is *right* and check only that it is *used* correctly. Nothing falsifies a wrong authorization (Layer A, "correct policy evaluation", dispatch §4) | proposal; UNVERIFIED |
| **G7-I10** No Uncontrolled External Duplicate | per tid, at most one client order id is ever sent; a retry reuses it only under confirmed broker deduplication; every venue order is reconciled to exactly one tid | the review covers duplicates as surface D.3 but has no invariant for them. Needed to resolve G7-C07 | proposal; CONDITIONAL on B-DEDUP |

**Explicit assumption G7-A1** (unchanged from Draft 0.2): K3, K5 and the K5 host are uncompromised. The review's E.2 and Part V counterexample 5 confirm that its compromise defeats G7-I1 to G7-I7.

---

## 3. [A0.2a-3] Review inventory → architecture traceability (closes Draft 0.2 row Z)

**Columns:**
1. review surface;
2. invariant;
3. mechanism;
4. test or falsification;
5. evidence artifact;
6. assurance boundary;
7. residual;
8. status, with the SL-PT-001 stage that can test it.

*Draft 0.2 row* points to the row it maps onto, or **NEW** where the row is added here.

| Review | Draft 0.2 row | Inv. | Mechanism | Test / falsification | Evidence | Boundary | Residual | Status · SL-PT |
|---|---|---|---|---|---|---|---|---|
| **A.1** adapter transmits without authorization | B1 | I1, I5, I8 | the adapter has no credential and no egress | the adapter calls the venue with no key | refusal / HTTP error | tested host | **E.1 if the adapter holds a key** | UNVERIFIED · C (on the founder's machine, expect **success → detection**) |
| **A.2** adapter forges an authorization | **NEW A2** | I1 | the pull model: K5 never accepts an authorization *from* the adapter, only an id it looks up in K3; nothing to forge | present a fabricated id or record | refusal | K5 + K3 | forging becomes **K3 compromise** (C3) | DERIVED (moot by design) · C |
| **A.3** adapter mutates qty, price, side, account or instrument | T6 | I2 | the pull model; mapper round trip | field-mutation matrix over every bound field | L-1 diff | mapper inputs tested | the canonicalization residual (F.1) | UNVERIFIED · B/C |
| **A.4** second process uses the credentials | **NEW A4** (with B1) | I5, I8 | OS file permissions; a separate user; a secret store | a second process reads the key / opens the egress | access denied | tested host | shared user (**true on the founder's machine**) | UNVERIFIED · C (expect success) |
| **A.5** intelligence calls the broker directly | **NEW A5** | I5, I8 | the intelligence process has no key and no egress | the intelligence calls the venue | refusal | tested host | co-residence | UNVERIFIED · C |
| **B.1** replay of a valid authorization | T2 | I3, I10 | single-use; COID = tid | resubmit after consumption and after a crash | refusal | local + Alpaca paper | lost-ack external duplicate (D.2) | UNVERIFIED · C |
| **B.2** expired before transmission | T3 | I4 | expiry checked at LP-CONSUME and LP-DISPATCH | consume at TTL + ε | refusal | harness clock | skew (C.6) | UNVERIFIED · A/C |
| **B.3** revoked before transmission | T4 | I4 | synchronous K3 read at LP-DISPATCH | revoke at every injected point | abort | local | after LP-DISPATCH: none (by design) | UNVERIFIED · C |
| **B.4** consumed twice (sequentially) | T1 (extended) | I3 | durable CAS | consume, then consume again | refusal | local store | rollback | UNVERIFIED · B/C |
| **B.5** concurrent consumption | T1 | I3 | atomic CAS | parallel consume (counterexample 1 as a test) | one success | local store | storage bugs | UNVERIFIED · C |
| **B.6** capability rebound to another order or account | **NEW B6r** | I2 | the pull model: the id resolves to exactly one record, so there is nothing to rebind | present the id with other parameters | the parameters are ignored; the K3 record is used | K5 | — | DERIVED (moot by design) · C |
| **B.7** adapter steals or leaks a capability | **NEW B7r** | I3, I1 | an id is not a bearer credential; only K5 can redeem it, and it redeems exactly the approved order | leak an id; redeem it early | the approved order only | K5 | **early redemption changes timing, not content** (contained) | DERIVED · C |
| **C.1** EAR state changes after authorization, before transmission | T5 | I4, I9 | re-check at consume (SL-PT R14); LP-DISPATCH re-read | inject a state change between the points | refusal | input coverage | the LP-DISPATCH → first-byte window | UNVERIFIED · A/C |
| **C.2** exposure changes before execution | T5 | I4, I9 | EAR suspension; re-check | inject a fill in between | refusal | as above | as above | UNVERIFIED · C |
| **C.3** correction or bust after authorization | **NEW C3r** | I4, I9 | EAR suspension/invalidation (R-8 readings, EIVI) | a bust between authorization and consume, buy and sell sides | refusal or suspension | before release only | **after release: detection only** | UNVERIFIED · C (synthetic; OQ-PT-3) |
| **C.4** gateway and EAR disagree | **NEW C4r** | I4 | the pull model: K5 keeps **no authorization cache**, so disagreement reduces to K3 being unreachable → fail closed | make K3 unreachable at dispatch | refusal | K5 | availability (FD-G2) | DERIVED · C |
| **C.5** gateway restarts with outstanding capabilities | X2, X3, T7 | I3, I6 | durable WAL; recovery treats DISPATCHING as AMBIGUOUS; CONSUMED is never fresh | kill at every LP | recovery log | local | restore without governance (T7) | UNVERIFIED · C |
| **C.6** clock drift or manipulation | **NEW C6r** | I4 | monotonic clock; a skew bound; fail closed on anomaly | clock jumps | refusal | harness | tampering beyond the bound | UNVERIFIED · C |
| **C.7** delayed request arrives after validity | T3 | I4 | validity at enforcement, not at queue entry | delay across expiry | refusal | local | delay after LP-DISPATCH | UNVERIFIED · C |
| **D.1** sent, no acknowledgement | X1 | I6 | AMBIGUOUS; query by COID | drop the response | AMBIGUOUS → query | Alpaca paper | — | UNVERIFIED · C |
| **D.2** broker accepts, ack lost | X1 | I6, I10 | as D.1 | as D.1 | as D.1 | paper | the window before reconciliation | UNVERIFIED · C |
| **D.3** retry creates a duplicate | X4 | **I10** | no new id; reuse only under B-DEDUP | retry with the same COID on Alpaca paper | venue response | paper only | live deduplication | UNVERIFIED · C |
| **D.4** broker reports before the local record | **NEW D4r** | I6, I7 | the WAL record precedes the send, so every report finds its DISPATCHING record | deliver the report before the send-confirmation write | correlation by COID | local | crash between write and send (F.2) | DERIVED · C |
| **D.5** accepted, then rejected, cancelled, corrected or busted | X7, X9 | I6 | full lifecycle machine (Draft 0.1 §13 C); EAR evidence | inject each transition | state history | paper (bust: synthetic) | late events | UNVERIFIED · B/C |
| **D.6** broker state differs from reconstructed state | C6 | I6 | reconciliation L-2; restricted mode until reconciled | hide or alter a venue record (harness) | DISCREPANCY | detection | unobserved divergence | UNVERIFIED · A/B |
| **E.1** adapter holds broker credentials | B1, B6 | **I8** | none inside the application; credential custody | inventory; a copied key used from elsewhere | the inventory record | **broker-side** | **UNBOUNDED within account limits** on Alpaca (no IP binding) | UNVERIFIED · C |
| **E.2** gateway compromised | C1 | (defeats I1 to I7) | none internal; broker-side containment; reconciliation detection | a "malicious K5" mode in the harness | UNMEDIATED events | detection | UNBOUNDED within account limits | DERIVED · C (modelled) |
| **E.3** gateway configuration altered | **NEW E3r** | I9 | the policy and configuration hash is bound into every authorization; a read-back at start (TR-5); a founder record for any change | edit the config or limits; run | refusal at start / hash mismatch | local | an insider with write access (review T8) | UNVERIFIED · C |
| **E.4** alternate endpoint bypasses verification | B4, B5 | I5 | single egress; the allowlist; no debug paths | an endpoint and port inventory; call each | refusal | tested surface | forgotten paths | UNVERIFIED · C (partial) |
| **E.5** credentials shared across components | **NEW E5r** | I5, I8 | per-component identity; **only K5 holds the venue key**; read-only reconciliation via a separate key (if the venue offers read-only keys: **UNVERIFIED for Alpaca**) | use another component's credential | refusal | tested host | **Alpaca: one key type, so the reconciler's key could also trade** (UNVERIFIED) | UNVERIFIED · B |
| **E.6** logging disabled while execution remains possible | X8 | I7 | fail-closed: no send without a durable WAL record (FD-G4 strict) | disable the audit sink | refusal | local | fail-open if FD-G4 chooses availability | UNVERIFIED · C |
| **F.1** canonicalization ambiguity | T6 | I2 | the typed canonical encoding (EAR Draft 4, by reference); the pull model | encoding fuzzing (number formats, aliases, Unicode) | L-1 diff | encodings tested | untested encodings | UNVERIFIED · C |
| **F.2** partial or truncated egress write | **NEW F2r** | I6 | an interrupted send is AMBIGUOUS; query by COID | kill mid-write (harness) | AMBIGUOUS → query | local + paper | — | UNVERIFIED · C |
| **F.3** stale revocation cache during a partition | **NEW F3r** | I4 | no revocation cache in the pull model; K3 unreachable → fail closed | partition K3 | refusal | K5 | availability (FD-G2) | DERIVED · C |

**Draft 0.2 rows with no review counterpart (Claude additions, kept):**
- B2: a second API key on the broker side;
- B3: a human order placed in the dashboard;
- B6: a copied key used from another network;
- T7: a restore resurrecting authorizations;
- X5: a duplicate COID accepted by the venue;
- X6: the replace race;
- X7: the cancel-fill race;
- C3: authority compromise;
- C4: signing-key compromise (n/a);
- C5: audit record tampering.

The review's trust map treats the broker as authenticated "outside the boundary" (Part II). **These rows are where that assumption fails on a bearer-credential venue.**

**Coverage:** 31 required surfaces + 3 added = **34 of 34 mapped** (DERIVED by enumeration of this table). The mapping is Claude's. **Whether each mapping is faithful to the review's intent is unverified**, and that is a check for GPT.

---

## 4. [A0.2a-4] Disagreements with the review (preserved, not resolved by Claude)

| ID | Review position | Specification position | Basis | Resolution path |
|---|---|---|---|---|
| G7-C07 | G7-I3's falsifier: "two distinct external submissions for one tid" | this conflicts with a permitted same-COID retry. Split into I3 (local consumption) and I10 (external orders) | DERIVED | **FD-G16** |
| G7-C08 | Part II: the adapter may hold "scoped transport/session material" | on bearer-credential venues (Alpaca keys), any credential material can trade, so **the adapter holds none**. Draft 0.1's "messenger" design stands | DERIVED + Draft 0.2 [S1, S2] | GPT review |
| G7-C09 | A.1: "Prevented (at enforcement boundary)" | prevented only if E.1 and G7-I8 hold; **not in SL-PT-001** | DERIVED | none needed; recorded |
| G7-C10 | Part VI compares Approach 1 and Approach 2 | Approach 2 with *synchronous* revocation and consumption needs the same stateful store as Approach 1, so its offline advantage disappears and the signature adds integrity only when the payload transits an untrusted party (moot under the pull model). **Egress isolation (Draft 0.1 C) is the missing dimension:** without it, neither approach is non-bypassable | DERIVED | GPT review |
| G7-C11 | Part X: "Do not add live/paper broker adapters" to the initial G-07 design | the founder's 2026-11-25 dispatch maps G-07 onto Alpaca paper (SL-PT-001 Stages B and C). **The founder's dispatch governs.** G-07 itself still specifies no adapter implementation | founder authority | recorded |
| G7-C12 | Part IX lists 5 decisions | Draft 0.1 has 11 (FD-G1 to FD-G11). Mapping: review 1 → FD-G1; 2 → FD-G2 (+FD-G3, FD-G4); 3 → FD-G5 (+FD-G6); 4 → FD-G8; 5 → FD-G7 | — | none |

---

## 5. [A0.2a-5] Founder decisions added

| ID | Decision | Options |
|---|---|---|
| **FD-G16** | resolve G7-C07: may an authorization ever lead to a second submission with the same client order id? | (a) **never**: an ambiguous outcome is resolved by query only, and G7-I3's falsifier stands as written; (b) yes, under confirmed broker deduplication: adopt the I3/I10 split. Option (a) is simpler and safer; (b) keeps more intended orders alive |
| FD-G14 | (from Draft 0.2) supply the review | **closed**: received |

---

## 6. [A0.2a-6] Changes to the UNVERIFIED / UNBOUNDED list (Draft 0.2 §9)

- **Removed:** "whether the reconstructed G7-I1 to G7-I7 match the review" (they did not; replaced); "the completeness of the attack-surface inventory against the review" (34 of 34 mapped).
- **Added, UNVERIFIED:**
  - the faithfulness of the §3 mapping to the review's intent;
  - whether Alpaca offers read-only keys (E.5);
  - the resolution of G7-C07.
- **UNBOUNDED, unchanged:** loss under gateway, host or credential compromise, bounded only by the account's assets and configuration.

*End of Draft 0.2a. Nothing implemented, tested or executed.*
