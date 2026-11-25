# EAR v0.1 Revision 3.1: Targeted Hostile Review

SPECIFICATION REVIEW ONLY. No implementation authorization. The frozen baseline is not modified; proposed corrections are in section 9 and need founder review before any new revision.

Reviewer: Claude (Specification Lead / ARBITER). Counter-review: GPT. Date: 2026-11-24.
Claim labels used throughout: **verified** (checked by computation or hashing in this review), **derived** (hand derivation by this reviewer, not executed), **assumed** (stated assumption of the spec), **conditional** (holds only if named assumptions hold), **unverified** (no evidence either way).
Line numbers refer to `ear/spec/EAR_v0.1_Rev3.1_FROZEN.md` at commit d4c9e66 (1,026 lines).

---

## 1. Baseline identity and hash confirmation

| Item | Value | Label |
|---|---|---|
| Artifact | `ear/spec/EAR_v0.1_Rev3.1_FROZEN.md` | |
| SHA-256 | `dd9d87f76b01134e084827b0202c73c52fccb2b86f21a176a6b6e551241fa239` | verified (fresh clone, this review) |
| Repository | github.com/skyhacker156/Sentinel_EAR, branch main | |
| Commits | `767f2369ef1336c513e5c59f5251913be67ce74d` (Rev 3 baseline), `d4c9e660bcba8875723820326993e377de960d7c` (Rev 3.1 added) | verified |
| Manifest | `sha256sum -c SHA256SUMS.txt`: 6 of 6 OK | verified |
| Recovery step | Supplied copy had CRLF line endings and no final newline; CRLF→LF plus one final LF reproduces the dispatch hash; no text changed | verified; recorded in BASELINE_IDENTITY.md |

The baseline recovery confirms the bytes. It says nothing about whether the specification is correct.
Arithmetic re-run in this review (**verified**): per-slot order combinations 5, 8, 11 (25 with absent); 612,500 generated ledger states; 4,900,000 and 14,700,000 proposal cases; 16,104 event sequences; CAS counts 140, 1,120, 560; V57's d set {-4, -2, 0, +2} giving d_plus 2, d_minus 4. Hand checks of V53, V60, V62, B2 and B5 agree with the spec (**derived**).

---

## 2. Executive verdict

**Rev 3.1 is not ready for a bounded reference implementation as frozen. Verdict: NO-GO, with a short, named path to CONDITIONAL GO.**

The accounting core holds up. Within W1 to W7, I found no false permission from the sum rule, the D19 mismatch permission or the commit protocol (**derived**, not executed). The blocking problems are definitional: a careful implementer following the text would have to invent a rule that decides safety.

1. **A-2 promises a *monotone* sequence (lines 200, 708), but GAP, RECONCILED, MISMATCH, D19 precondition 1, the terminal rule and snapshot replacement all depend on *contiguity*.** That word is used (lines 418, 494, 496, 342, 486, 518) but never defined or promised. Under the monotone-only reading, a lost economic event is accepted silently, and a false permission follows (CX-02). **Blocking.**
2. **A sequence reset is admitted silently.** The "stale" rule (lines 419, 523) *applies* an unseen event whose sequence number is below the watermark if it is "consistent". After a broker sequence reset, every new event takes this path, GAP can never fire again, and every newer snapshot is rejected as REPLAY. Permission continues on the old snapshot until S_lim expires (CX-04). **Blocking.**
3. **The evidence model (2.8) cannot be evaluated in v0.1 as written.** v0.1 has one evidence source (2.8 line 593; D24 line 839), so Consistency would read NO_INDEPENDENT_EVIDENCE, and Authenticity needs keys that D23 defers. Under a literal reading every evaluation is a failure state, so every ALLOW in vectors V01 to V62 is wrong (CX-20). The alternative, recording these checks as passed, is what 2.8 forbids ("A failed or unavailable check is never a pass"). **Blocking.**
4. **Three oracle defects would corrupt the first run.** G3 is missing from the gap classification in I4 and 5.1(c), so real G3 gaps would be reported as UNEXPLAINED counterexamples. The oracle domain omits the side choice for an unknown-side working order (requirement F). And the grid supplies position status as an *input*, so the status derivation, where A-2 lives, is never independently checked. **Major; must be fixed before any run.**

A-12 is stated correctly as a boundary (R31-03'): an undelivered event after the last snapshot can produce a false permission in RECONCILED (CX-01). The spec does not claim otherwise. That is a correct limitation, not a defect, and it rules out any live or broker use. A related point the spec acknowledges only in I8 and the safety scope: a **later bust of an already-applied fill** (CX-12) makes an earlier ALLOW an oversell. That event type, E14, is *inside* the model, not an environmental failure.

---

## 3. A-2: sequence semantics

### 3.1 What A-2 actually promises (exact text)

Line 708, 2.11: "where broker_seq is present it is one **monotone** sequence per account, and a watermark W means the snapshot contains exactly the executions with broker_seq <= W (absent sequence numbers mean unknown timing). Not established for any real broker." Class **E**, an input contract.

So A-2 is a **declared assumption (input contract)**. It is not a broker guarantee and not an inference. It promises:
- (a) **monotonicity** where a sequence number is present;
- (b) **scope**: one sequence per **account**;
- (c) **watermark exactness**.

It does **not** promise:
- (d) contiguity, i.e. each successor is predecessor + 1;
- (e) coverage: which message classes consume sequence numbers (executions only, or order events, admin messages and other instruments in the same account too);
- (f) that every sequenced message is delivered to the model;
- (g) stability across sessions or reconnects;
- (h) that sequence numbers are present at all (they are optional: lines 121, 122, 123).

### 3.2 What the rules need

| Rule | Text | Property it needs | Label |
|---|---|---|---|
| GAP on arrival | 2.6, line 418: "broker_seq beyond **next expected**" | a successor function, which means contiguity (d), coverage (e) and delivery (f) | derived |
| GAP status | 2.6.2, line 499: "a sequence number missing at or below W" | "missing" is only defined under (d) and (e) | derived |
| RECONCILED, MISMATCH | lines 494, 496: "**contiguous** through W" | (d), (e), (f) | derived |
| D19 precondition 1 | line 342: "contiguous events through W" | same | derived |
| Terminal-transition rule | line 486: "every execution up to the event has been applied" | checkable only through contiguity | derived |
| Snapshot replacement (3) | line 518: "events are contiguous through W'" | same | derived |
| Stale rule | lines 419, 523: "below the **applied watermark**, event_id unseen: applied if consistent" | "applied watermark" is undefined; the rule is only safe if (g) holds | derived |

**Finding A2-1 (blocking, derived).** Contiguity is used in six normative rules and is neither defined nor part of any assumption. Monotonicity alone gives no "next expected": the sequence `100, 101, 104` is monotone and has no gap under A-2 as written.
**Finding A2-2 (major, derived).** The scope is "per account", but the envelope (2.1) limits only the *model* to one instrument. It does not say the account trades only that instrument. Under an account-wide sequence, another instrument's events either appear as foreign instruments (D13 quarantine, UNBOUNDED) or are filtered out and appear as gaps. Either way, all activity blocks, possibly permanently.
**Finding A2-3 (major, derived).** GAP clearance is defined only as "the missing event arrives, or the broker gives an explicit authoritative resolution of that specific sequence" (line 527). No evidence item for such a resolution exists in 2.2, the event table or the uncertainty inventory. So a legitimate discontinuity (an admin message, another instrument's event) has no defined way to clear.
**Finding A2-4 (informational, derived).** Detection is not proof of completeness. Even under a contiguity contract, GAP detects a missing number only once a *later* sequenced event or a snapshot with a higher watermark arrives. A loss at the tail of the stream is invisible until then (CX-01). This is A-12, correctly stated at line 202. No rule in Rev 3.1 claims more.

**Can the spec tell a missing event from a legitimate discontinuity?** No. Without the coverage clause (e) and a resolution evidence item, every discontinuity must be treated as missing. That is conservative but leaves no path to clear.
**Permissions while a gap is unresolved:** UNBOUNDED, so increases are DENY and reductions UNRESOLVED (line 499, 2.7). This is unambiguous once a GAP is detected.
**Does clearance need reconciliation against an authoritative source?** Yes. Line 527 requires the missing event itself or an authoritative broker resolution; a later snapshot never clears a GAP (V48). This is correct but unimplementable without A2-3.
**Other rules that implicitly assume gap-free delivery:** W2 (line 178: "a missing sequence number is a GAP"), D19 precondition 1, the terminal rule, and snapshot replacement, all listed above.

### 3.3 A-2 counterexamples

Each counterexample's full fields are in the register (section 8). Summary:

- **CX-02, monotone sequence with a missing economic event.** RECONCILED at W=101, F=100, a working buy O1 of 10. Sequence 102 is a sell of 50 placed outside EAR (lost), 103 is a bust of an earlier buy of 20 (lost), and 104 is the acknowledgement for O1 (delivered).
  - *Contiguity reading:* 104 is beyond the next expected number, 102, so the status is GAP and reductions are UNRESOLVED. **Safe.**
  - *Monotone reading:* 104 is valid, the event is applied, the status is AWAITING with A=100, and a sell of 80 is ALLOWed. The true position is 30 (100 - 50 - 20), so this is an **oversell of 50**.
  - **Rev 3.1 is ambiguous here, and the ambiguity decides safety.**
- **CX-03, apparent gap from legitimate stream behaviour.** The account-wide sequence also numbers a fill on instrument Y (number 102), or an admin or heartbeat message.
  - If it is delivered, D13 quarantine makes the band UNBOUNDED for all activity.
  - If it is filtered out, 103 arrives and the status is GAP.
  - Either way the result is safe, but no clearance path exists (A2-3). Rev 3.1 is unambiguous that it blocks, but **incomplete on how to clear**.
- **CX-04, reconnect with sequence reset, wrongly concluding the history is complete.** The ledger is bootstrapped from snapshot S0 at W=500 (as in V38). Events 501 and 502 are applied. During a disconnect, a sell of 50 placed outside EAR occurs as number 503 and is never resent. On reconnect the broker restarts numbering at 1.
  - New events numbered 1, 2, … are "below the applied watermark, event_id unseen" (line 419), so they are **applied if consistent**.
  - No event is ever "beyond next expected", so **GAP never fires**.
  - The broker's next snapshot has W'=7, which is below the accepted 500, so it is **rejected as REPLAY** (2.6.2 case table) and the old snapshot is kept.
  - The status stays AWAITING until S_lim expires. A sell of 80 is ALLOWed against a true position of 50.
  - In addition, F_d(W=500) now includes events numbered below 500 from the new session, which corrupts d.
  - **Rev 3.1 is unambiguous, and its rules turn an A-2 violation into silent acceptance.**
  - Mitigation in the text: a post-reset sequence number that collides with one already seen is a CONFLICT (line 523). That only helps if the ledger has seen those low numbers, which a snapshot-bootstrapped ledger has not.

---

## 4. Decision ledger

Classes: UPHELD, UPHELD WITH LIMITATION (UWL), REVISE, REOPEN, DEFERRED, FOUNDER DECISION (FD). "Blocks" means blocks a bounded reference implementation; nothing here authorizes broker contact.

| Entry | Ref | Existing | Assessment | Reasoning / counterexample | Proposed correction | Blocks |
|---|---|---|---|---|---|---|
| D01 sum rule | 2.4, 3.1 | Approved | UPHELD | Soundness against W1-T and W1-F re-derived (line 195); over-denial G1/G2/G3 is the accepted cost. Derived | none | no |
| D02 world model | 2.3, 3.2 | Approved with additions | UWL | Sound only within W1–W7; the W1 classes are scoped correctly by R31-01'. W6 makes later busts "new events", so the world model never represents non-final fills (CX-12). Derived | State in 2.3 limits that W6 treats applied fills as final until a bust event; see FD-4 | no |
| D03 TTL | 2.9 | Approved | UPHELD | Expiry is a logged event (T05); CAS orders expiry against consume | none | no |
| D04 one counter | 2.9 | Approved | UPHELD | Item hash is a second check | none | no |
| D05 state-keeper trust | 2.8 | Approved default | UWL | A-7 stated plainly; no in-model protection (CX-18) | none | no (blocks broker contact) |
| D06 NO_INDEPENDENT_EVIDENCE for reductions | 2.8, line 590 | Approved | **REVISE + FD** | The trigger is undefined. Read as "one source", it holds for every v0.1 evaluation, so all reductions are denied, and by 2.8 ("any failure state blocks increases") all increases too, contradicting every ALLOW vector (CX-20). Read as "no accepted snapshot" (2.7, line 542), it is consistent | R-02, FD-1 | **yes** |
| D07 staleness limit | 2.6.2 | Approved | UPHELD | Parameter | none | no |
| D08 wait limits | 2.6.1 | Approved | UPHELD | Parameter | none | no |
| D09 retry K=3 | 2.9 | Approved | UPHELD | none | none | no |
| D10 cancel authority | 2.6 | Amended | UPHELD | Arithmetic only; G-07 | none | no |
| D11 no override | 2.13 | Approved | UPHELD | none | none | no |
| D12 Q_MAX | 2.1 | Approved | UPHELD | V52 | none | no |
| D13 foreign instrument | 2.12 | Approved | UWL | Correct for a single-instrument account; with an account-wide sequence and a multi-instrument account it blocks all activity indefinitely (CX-03) | R-08 coverage clause | no |
| D14 superseded max rule | 2.13 | Done | UPHELD | F-1 retained | none | no |
| D15 DENIED | 2.6.1 | Approved | UPHELD | none | none | no |
| D16 UNRESOLVED vs DENY | 2.4 | Approved | UPHELD | none | none | no |
| D17 U_unknown = A_unknown = 0 | 2.4, 2.4.2 | Approved with modification | UPHELD | The inventory gives every class one home; the "no home" row is honest | none | no |
| D18 AWAITING-BEHIND unbounded | 2.6.2 | Approved | UPHELD | F-4 sound; CX-07 confirms safe | none | no |
| D19 mismatch reductions | I2, 3.2 | Conditional candidate | UWL (conditional) | No in-model false permission found (section 6). Precondition 1 depends on A2-1. Preconditions 3 and 5 restate the decision rule | R-01; R-13 wording | via R-01 |
| D20 log-position order | 2.6.3 | Approved with limits | UWL | Deterministic processing only; two logs of one history can differ (V49, CX-16); no false permission (both orders conflict) | none | no |
| D21 decision age, commit re-evaluation | 2.9, I5 | Approved | UWL | Coherent. "Commit time" is read at step 3 but used at step 4; the interval between them is unbounded (CX-17) | R-12 | no |
| D22 E24 | 2.12 | Approved | UWL | "Until the broker reconciles under the new version": snapshots carry no master-version field (line 123), so nothing in the spec can clear R_MASTER_CHANGE | R-11 | no |
| D23 keys | 3.3 | Deferred | DEFERRED, but see D06 | Authenticity (2.8) needs a key decision v0.1 does not have; the reference model needs an evidence profile (R-02) | R-02 | via R-02 |
| D24 independent evidence | 3.3 | Deferred | DEFERRED | Correctly blocks live use; also sharpens the D06 ambiguity | FD-1 | via R-02 |
| D25 master ownership | 3.3 | Deferred | DEFERRED | Not needed for one fixed instrument | none | no |
| D26 identity-changing CORRECT | 2.2, 3.2.1 | Approved | UPHELD | Fails closed (V59); availability cost acknowledged | none | no |
| D27 correction contract | 2.2, 3.2.1 | Approved | UWL | Internally sound (V49, V60, V61 re-derived). Operational realism: brokers typically send a referenced exec id, not a version number, so prior_version would be synthesized by the state keeper (A-7) | Note under A-14 | no |
| A-1 single instrument | 2.11 | M | UWL | See D13 / A2-2 | R-08 | no |
| A-2 sequence contract | 2.11, 2.3 | E | **REVISE** | Findings A2-1 to A2-3; CX-02, CX-03, CX-04 | R-01, R-03, R-08 | **yes** |
| A-3 atomic CAS | 2.11 | I | UPHELD | Implementable in-memory | none | no |
| A-4 independent clock | 2.11 | O | UWL | Clock compromise uncovered (O-3) | none | no |
| A-5 adapter uses token | 2.11 | O | UWL | O-2 window acknowledged | none | no |
| A-6 W1–W7 | 2.11 | E | UWL | As D02 | none | no |
| A-7 honest state keeper | 2.11 | O | UWL | Any omission by the state keeper is indistinguishable from A-12 (CX-18) | none | no (blocks broker contact) |
| A-8 config pinned | 2.11 | I | UPHELD | none | none | no |
| A-9 explicit as_of | 2.11 | I | UPHELD | See R-12 | R-12 | no |
| A-10 master as evidence | 2.11 | I | UPHELD | none | none | no |
| A-11 event identity | 2.11, 2.6.3 | E | **REVISE** | The fallback "hash of canonical content" (line 717) is undefined and fails either way (CX-19) | R-07 | no |
| A-12 delivery completeness | 2.11, 2.3 | E | UWL (boundary) | Correctly stated, including RECONCILED (R31-03'). CX-01 shows the false permission | R-14 adds limitation vectors | no (blocks any live use) |
| A-13 integers | 2.11 | M | UPHELD | none | none | no |
| A-14 correction fields | 2.11 | E | UWL | See D27 realism | none | no |
| G-A proposal hash | 2.2, 2.9 | Resolved (R31-06B) | UPHELD | V58 re-derived; binding includes account and instrument | none | no |
| G-B pre-commit ALLOW | 2.9 (R31-06A) | Resolved | UPHELD | Only `authorize` and `consume` are public; diagnostics never returned | none | no |
| G-C identity correction | D26 | Resolved | UPHELD | as D26 | none | no |
| G-D correction contract | D27 | Resolved | UPHELD | as D27; enumeration obligations to add (R-13) | R-13 | no |
| G-E CAS scenario declarations | 5.4, 5.7 | Resolved | UPHELD | 140, 1,120 and 560 verified | none | no |
| RQ1–RQ12 | 2.14 | Various | UPHELD where they map to D decisions above | No new defect beyond D06, D13, D22 | as above | no |
| R31-01' to R31-11 | change log | Incorporated | UPHELD except as noted | R31-07' rule correct (V62 re-derived); R31-08 domain incomplete (R-05); R31-10 claim levels correct | R-05 | via R-05 |

Inconsistencies found inside the text (all **verified** by reading the cited lines):
- **I4 (line 359) and 5.1(c) (line 884)** classify gaps as "G1, G2 or UNEXPLAINED", omitting G3. Lines 292 and 904 mention G1/G2 only. Lines 197, 356 and 364 include G3. → R-04.
- **2.5 (line 323)**: "within the model" means A-1 to A-11, omitting A-12 to A-14. → R-13.
- **Section 7 (line 968)**: "56 hand vectors", but Rev 3.1 has V01 to V62 less withdrawn V09, so 61. → R-13.
- **net_cum_at (line 139)** sums executions' *current versions* with broker_seq <= s. F_d(W) (line 141) sums *events* by their own broker_seq. So after a CORRECT numbered above s, net_cum_at(order, s) already reflects it while F_d(s) does not. → R-09.

---

## 5. A-12: event completeness

The spec's own distinction, assessed. Received, processed, persisted and replayed events are covered by the log, I9 and D20 (**assumed** via A-7). Events economically executed at the broker but omitted are **not representable** (2.4.2 "no home" row, line 317). Deterministic replay establishes consistency relative to the log only (line 529). Rev 3.1 says this correctly.

| Case | Sequence | Rev 3.1 result | Conservative? | Label |
|---|---|---|---|---|
| Fill occurred, never delivered, **known working order** (CX-06) | F=100, working sell 60; fill 60 lost | A=40 unchanged (W4: x in [0, R] cancels in A_w); a later cancel confirmation with cum 60 against net_cum 0 is a CONFLICT | **yes** | derived |
| Fill occurred, never delivered, **no known order** (CX-01) | RECONCILED W=100, F=100; sell 50 placed outside EAR, lost; no later event | RECONCILED, A=100, sell 80 ALLOW; true position 50 | **no: false permission of 30 in RECONCILED** | derived; spec acknowledges (line 202) |
| Delayed fill after a snapshot (CX-07) | fill 102 delayed; snapshot W=103 arrives first | AWAITING-BEHIND, UNBOUNDED; unsequenced variant uses the interval | yes | derived |
| Duplicate under a new id (CX-08, V56) | buy 10 resent with a new id | reductions: false permission of 10 (V56); sell variant: increases false permission | **no** | derived; acknowledged (line 522) |
| Cancel/fill race (CX-09) | CANCEL_PENDING sell 60; fill 10 (102) lost; cancel confirm cum 10 (103) | GAP and terminal-rule CONFLICT; unsequenced variant still a CONFLICT on cum | yes | derived |
| Omitted between valid snapshots (CX-10) | S1 W=100; 101 lost; 102 delivered; S2 W=102 | under contiguity: GAP, persisting through S2 (V48) | yes **only under R-01**; under the monotone reading, as CX-02 | derived |
| Broker internally consistent but wrong (CX-11) | broker omits a fill from both stream and snapshot | RECONCILED, wrong position | **no**; common mode, out of scope (W1, D24) | assumed |
| Later bust of an applied fill (CX-12) | buy 100 FILLED, sell 100 committed, buy busted | OVER_RESERVED raised (I8), but the sell is already authorized | **no**: in-model event, detection only | derived; acknowledged (I8, safety scope 3) |

**Plain statement.** Rev 3.1 cannot establish safety under event-delivery incompleteness, in any status, including RECONCILED. Freshness bounds the *age* of evidence, not its completeness. Monotonicity does not detect omissions. Reconciliation detects them after the fact. Replay reproduces whatever log it is given. The spec says this itself (lines 79, 202, 718). This review confirms it with concrete sequences and finds no text claiming more.

---

## 6. D19: conditional permission during a quantified MISMATCH

**Sufficiency inside the model (derived).**
- Under W1-T, P = F_b + (F_d - F_d(W)) + T4 orphans + post-W fills.
- Since F_d + d = F_b + (F_d - F_d(W)), P >= F_d - d_minus - Q3_sell - Q3_unk.
- Under W1-F, P = F_d + orphans, which is >= the same bound.
- Unreported sell fills cancel in A_w = P - (R - x).
- So A_raw <= A_w in every admitted world, and no in-model false permission exists.
- One useful consequence: events missing *at or before W* are absorbed by d under W1-T. D19 is therefore no weaker than RECONCILED against early losses, and equally exposed to losses after W.

**The five preconditions (I2, line 342), each failing alone:**
1. GAP, AWAITING-BEHIND or AWAITING-UNVERIFIED → UNBOUNDED → UNRESOLVED. Specified, but it **depends on contiguity (A2-1)**.
2. A structural failure or pending correction → UNRESOLVED (2.7). Specified.
3. "Unsequenced executions handled by the interval" is how d is computed, not a condition of the state. It can fail only through an implementation defect, so it is testable only by mutation. **Restates the rule.**
4. A stale snapshot → status UNKNOWN or R_DECISION_STALE (I5, V44). Specified.
5. Q <= A, never clipped → DENY otherwise. **Restates the decision rule.**

**Several failing together:** the outcome is the most restrictive, UNRESOLVED (2.4 decision rules). Specified.

**Other D19 cases:**
- *Precondition apparently satisfied because delivery was incomplete (CX-13):* MISMATCH with d=-5, working sell 20, A=45. A sell of 30 placed outside EAR after W is lost. A sell of 45 is ALLOWed, while the true position is 35 against reservations of 65, an **oversell of 30**. This is the A-12 boundary, not something D19 adds.
- *Change between evaluation and commit (CX-14):* the revision moves, so re-evaluation gives A=40 and a sell of 45 is DENY. Safe (I5).
- *A newly received correction:* the revision bumps and the order is re-evaluated. After commit, I8 detects only (CX-12 shape).
- *Actual state outside the oracle envelope (CX-15):* MISMATCH plus an unknown-side working order plus a T1u orphan plus two unsequenced executions. Derived sound, but outside the static grid (one orphan, no unknown-side order, one unsequenced execution), and the oracle domain omits unknown-side order choices (R-05). "No false permission in the grid" would therefore say nothing about this state.

**Assessment: UPHELD WITH LIMITATION, still conditional.** No reason found to revert to blocking reductions during MISMATCH. The pre-declared rollback stays. D19 must not be called safe: its safety is **conditional** on W1 to W7, A-2 (with R-01), A-7, A-11 and A-12, and the oracle has never been executed (**unverified**).

---

## 7. Oracle assessment

No oracle code, enumeration or output exists (V-1, line 964). **Nothing has passed. Nothing has been inspected or reproduced.** This assessment covers the design in 5.1 to 5.7.

| Question | Assessment | Label |
|---|---|---|
| Upper and lower bounds justified? | U_oracle = max U_w and A_oracle = min A_w over admitted worlds; the world values (line 187) follow from W1 and W7 | derived |
| Soundness comparisons oriented correctly? | U >= U_oracle, A_raw <= A_oracle; decision soundness (b) correctly defines false permission; flag check (c) correct | derived |
| W1-T/F, T1u, T2, T3/T4, fills represented? | Yes for these. **Missing: the side choice for an unknown-side working order (W3, requirement F)**; 5.1 step 2 lists T1u and T2 only, and the 5.2 grid has no unknown-side slot | verified by reading lines 878–881, 891 |
| Boundary values and combinations? | Integer x in {0..R} with both placements and the full product (R31-08) is correct. The grid caps (one orphan, two orders, quantities up to 3, one unsequenced execution) are declared. The validity predicate removes "a MISMATCH d impossible for the chosen F_d" (line 896), which also removes the negative-snapshot path that V54 *defines*. That should be tested, not excluded | derived |
| Same semantics as the normative spec? | **No, in two places.** (1) The grid *enumerates position status as an input dimension* (line 892), so the status derivation of 2.6.2 (contiguity, AWAITING-BEHIND, quiescence, snapshot replacement) is never compared with an independent derivation. That is where A-2's risk lives. (2) Gap classes omit G3 in I4 and 5.1(c), so known G3 gaps (B2, B5) would be logged as UNEXPLAINED counterexamples | verified by reading |
| Can it miss counterexamples its own assumptions exclude? | Yes, by construction: A-12, A-11, A-7, common mode, later busts (W6), sequence resets. It shares W1–W7 with the model and so cannot detect an error *in* the world model | derived |
| Independent? | Structural separation only (no imports). Same author for spec, planned model and planned oracle (I-1). Not independent verification | assumed per spec |
| Evidence-property failures and D26/D27 payloads covered? | Evidence results are not grid dimensions; the E13 sequence parameters predate D26/D27 and are not declared | verified by reading |

**What a genuinely independent reproduction needs:**
1. A second author derives the world enumeration from 2.3 and the raw-fact schema alone, without seeing this oracle, the model or Claude's derivations.
2. That author also derives position status from raw sequence and snapshot facts.
3. The generator is written separately from both.
4. Source hashes are recorded before either side sees the other's output.
5. Both outputs are diffed per ledger, and every disagreement is adjudicated in a public register.
6. A third party reruns from one command and obtains identical result hashes.
Until then the label is "same-author, structurally separated".

---

## 8. Adversarial counterexample register

Severity: B = blocking (for a bounded reference implementation), Maj = major, Min = minor, Inf = informational / documented limitation. Every Inf item still blocks broker contact and live use.

| ID | Rule challenged | Initial state | Event sequence (✗ = occurred but not delivered) | Conservative expectation | Rev 3.1 result | Failure | Sev | Resolution |
|---|---|---|---|---|---|---|---|---|
| CX-01 | A-12 (line 202, 718) | RECONCILED, W=100, F=100, no orders, fresh snapshot | 101 ✗ external sell 50; no later event | cannot know; any reduction is a risk | RECONCILED, A=100, sell 80 ALLOW | **False permission 30** | Inf | Documented; add vector V63 (R-14) |
| CX-02 | A-2 vs GAP (lines 418, 708) | RECONCILED W=101, F=100, working buy O1 10 | 102 ✗ external sell 50; 103 ✗ bust of buy 20; 104 ack O1 | GAP, reductions UNRESOLVED | **Ambiguous**: GAP (contiguity) or AWAITING with A=100, sell 80 ALLOW, true position 30 (monotone) | **False permission 50** under the literal A-2 | **B** | R-01 |
| CX-03 | A-2 coverage, D13, line 527 | RECONCILED; account also trades instrument Y | 102 = Y fill (delivered → T2-U, or filtered → gap) | block, with a defined clearing path | UNBOUNDED; no clearing path defined | Availability (indefinite block) | Maj | R-08 |
| CX-04 | Stale rule (lines 419, 523), REPLAY rule (2.6.2) | Ledger bootstrapped at S0 W=500, F=100; 501, 502 applied | 503 ✗ external sell 50; reconnect; seq restarts at 1; events 1..n; snapshot W'=7 | sequence-contract failure: UNKNOWN or structural | events 1..n applied as "stale, consistent"; GAP never fires; snapshot rejected as REPLAY; AWAITING until S_lim; sell 80 ALLOW | **False permission 30** inside the S_lim window; d corrupted | **B** | R-03, FD-2 |
| CX-06 | W4 | F=100, working sell 60 | 101 ✗ fill 60 | conservative | A=40 unchanged; later cancel with cum 60 is a CONFLICT | none | Inf | none |
| CX-07 | D18 | applied through 101 | 102 delayed; snapshot W=103 arrives | UNBOUNDED | AWAITING-BEHIND | none | Inf | none |
| CX-08 | A-11 (V56, line 522) | F=100, L=150 | sell 10 applied, then resent with a new id: F_d=80, true 90 | detect | buy 70 ALLOW (U=150); true U=160 > L | **False permission (increase)** | Inf | Documented; add the sell-side vector (R-14) |
| CX-09 | Terminal rule (line 486) | sell 60 CANCEL_PENDING | 102 ✗ fill 10; 103 cancel confirm cum 10 | block | GAP + CONFLICT (unsequenced variant: CONFLICT) | none | Inf | none |
| CX-10 | A-2, V48 | S1 W=100 RECONCILED | 101 ✗; 102 delivered; S2 W=102 | GAP persists | GAP under R-01 only | as CX-02 if not | via CX-02 | R-01 |
| CX-11 | W1 common mode, D24 | RECONCILED | broker omits a fill from both stream and snapshot | cannot know | RECONCILED, wrong | False permission | Inf | D24 (second channel) |
| CX-12 | W6, I8 | F=0; buy 100 FILLED; RECONCILED F=100 | sell 100 committed (A=100); then E14 busts the buy | the reduction should not have been fully available while the fill could still be busted | I8: OVER_RESERVED after the fact; sell already authorized → short 100 if it executes | **Economic oversell from an in-model event** | Maj | FD-4; at minimum, state it in the 2.3 limits and add V64 |
| CX-13 | D19 + A-12 | MISMATCH d=-5 (F_d=70, F_b=65), working sell 20, A=45 | 101 ✗ external sell 30 | cannot know | sell 45 ALLOW; true position 35 against 65 reserved | False permission 30 | Inf | none beyond CX-01 |
| CX-14 | I5 | MISMATCH, sell 45 evaluated at rev 7 | new snapshot d=-10 → rev 8, then commit | reject | R_STALE_REVISION, re-evaluate, DENY | none | Inf | none |
| CX-15 | Oracle envelope (5.2) | MISMATCH + unknown-side UNKNOWN order R=5 + T1u orphan 3 + two unsequenced executions | none | sound and tested | derived sound; not in grid; oracle lacks the unknown-side choice | coverage gap | Maj | R-05, plus generative cases |
| CX-16 | D20 | E1 buy 5 applied | C1 and C2 corrections arrive in different orders at two state keepers | consistent | V49: each log conflicts at a different correction | none (both block) | Inf | none |
| CX-17 | D21 / I5 (2.9 steps 3–4) | snapshot age S_lim − 1 ms at step 3 | store latency before atomic step 4 | reject if stale at the actual commit | unspecified which time step 4 uses | possible commit 1 tick stale | Min | R-12 |
| CX-18 | A-7 | any status | state keeper drops one event | cannot know | as CX-01 | False permission | Inf | D23, D24 |
| CX-19 | A-11 fallback (line 717) | no broker ids; two genuine sell executions of 10 for an unknown order, identical content | both delivered | count both | if content excludes received_at: second deduplicated → Q3_sell 10 instead of 20 → A overstated by 10. If it includes received_at: resends never deduplicated (V56) | **False permission** either way | Maj | R-07 |
| CX-20 | 2.8, D06, D23, D24 | V01 (F=100, working sell 60, RECONCILED) | probe sell 10 / buy 10 | ALLOW / ALLOW per V01 | literal 2.8: Consistency NO_INDEPENDENT_EVIDENCE and Authenticity KEY_UNKNOWN → DENY / UNRESOLVED. Contradicts V01 | spec inconsistent | **B** | R-02, FD-1 |
| CX-21 | 2.2 unsequenced interval | RECONCILED W=100; applied buy 5 with no seq | any later snapshots | eventually reconcile | every inclusion choice set has a nonzero d_k, so MISMATCH forever; no rule resolves timing; increases blocked permanently | Availability | Min | FD-3 |
| CX-22 | I4, 5.1(c) | B2 (gap 3 on U, class G3) | oracle run | classified G3 | classified UNEXPLAINED → logged as a counterexample | false counterexample, corrupts the result | Maj | R-04 |

---

## 9. Required revisions, ranked

All of these alter the frozen baseline and would form a **Rev 3.2 candidate** only after founder review. None is applied here.

**R-01 (Blocking). The A-2 sequence contract (2.11 line 708; 2.3 line 200; 2.6 lines 418, 419; 2.6.3).**
- *Current:* "one monotone sequence per account".
- *Proposed:* "Where present, broker_seq is one **contiguous** integer sequence per account and per stream epoch: each sequenced message's number is exactly its predecessor's plus one. Every message that consumes a sequence number is delivered to the model (coverage, R-08). The ledger is initialized from an accepted snapshot at watermark W0, and the next expected number is W0 + 1. *Highest contiguous sequence* (H) = the largest h such that every number from W0 + 1 to h has been received. 'Contiguous through W' means W <= H. A number above H + 1 is out of order (GAP)."
- *Reason:* A2-1, CX-02.
- *Consequence:* GAP becomes definable; the monotone-only acceptance path is removed.
- *Tests:* CX-02 and CX-10 as frozen vectors; enumerate seq patterns `{contiguous, one gap, tail gap, duplicate number, out of order}` as raw facts (see R-06).

**R-02 (Blocking). Evidence profile for v0.1 (2.8; D06, D23, D24).**
- *Proposed:* "In the v0.1 reference model the five property results are **explicit inputs** to `evaluate`, one result per property per evaluation, recorded in the Decision. They are enumerated as test parameters and never computed as passes. Vectors V01 to V62 assume all five acceptable unless stated." Plus a definition of NO_INDEPENDENT_EVIDENCE, chosen under FD-1:
  - (a) "no accepted snapshot is available to cross-check the execution ledger"; or
  - (b) "single evidence source". Under (b), v0.1 can authorize nothing, and the vectors must be rewritten.
- *Reason:* CX-20.
- *Consequence:* the gating logic becomes testable without faking passes.
- *Tests:* each property × each failure state × {increase, reduction} must give DENY or UNRESOLVED.

**R-03 (Blocking). Sequence-contract violation (2.6 line 419, 2.6.3 line 523, 2.6.2 REPLAY row).**
- *Proposed alternatives (FD-2):*
  - (a) An unseen event_id with broker_seq <= H that does not fill a recorded gap is a **structural sequence-contract failure**: UNBOUNDED, both sides blocked, cleared only by authoritative reconciliation.
  - (b) As (a), and in addition the contract carries a stream-epoch id; a change of epoch puts the status to UNKNOWN until a snapshot of the new epoch is accepted.
  - In both cases, a snapshot whose W is below the accepted watermark but whose received_at is newer is flagged as a sequence-contract failure rather than silently ignored as REPLAY.
- *Reason:* CX-04.
- *Consequence:* a reset fails closed at once instead of after S_lim.
- *Tests:* CX-04 as a vector; the reset-after-bootstrap sequence in the event enumeration.

**R-04 (Major, fix before any run). Add G3 to the gap classification.**
- *Where:* I4 line 359, 5.1(c) line 884, 5.2 line 904, 2.4.2 line 292.
- *Change:* every "G1, G2 or UNEXPLAINED" becomes "G1, G2, G3 or UNEXPLAINED"; every "G1 and G2" becomes "G1, G2 and G3".
- *Reason:* CX-22. *Tests:* B2 and B5 as vectors classified G3.

**R-05 (Major). The oracle domain must include unknown-side working orders.**
- *Change:* add to 5.1 step 2: "for each working order of unknown side: side buy or sell, per W3"; add an unknown-side slot to the 5.2 grid.
- *Reason:* requirement F is untested; CX-15.

**R-06 (Major). Position status must be derived, not supplied.**
- *Change:* in 5.2, replace the status dimension with raw sequence and snapshot facts (sequence patterns, watermark position relative to H, quiescence, number of unsequenced executions). Require the oracle, or a separately written status checker, to derive status from those facts.
- *Reason:* the status derivation (and A-2) is otherwise outside every comparison.

**R-07 (Major). The A-11 fallback identity (line 717, 2.6.3).**
- *Proposed:* "Without a broker-unique event id, content-hash identity is **not** an idempotency key. Each delivery of an unassociated execution is a separate orphan item (counting both is conservative on both bounds). A content-identical second delivery for an associated execution is a structural conflict, not a no-op."
- *Reason:* CX-19.

**R-08 (Major). Sequence coverage and gap-resolution evidence (A-2, line 527).**
- *Change:* the contract names which message classes consume sequence numbers. Add an evidence item, *sequence resolution* (broker_seq, classification `non-economic` or `foreign-instrument`, authority, raw_hash), with a row in 2.4.2 and a transition in 2.4.1 item 6. This is the only non-arrival way a GAP can clear.
- *Reason:* CX-03.

**R-09 (Minor).** Redefine net_cum_at(order, s) over execution *events* with their own broker_seq <= s, consistent with F_d(W) (C-04). Test: V60 with a terminal event between seq 90 and seq 110.

**R-10 (Minor, FD-3).** Unsequenced applied executions. Either declare streams that mix sequenced and unsequenced executions out of contract, or accept permanent MISMATCH (increases blocked) as the stated cost, recorded in 2.4.2. CX-21.

**R-11 (Minor).** Add master_version and content hash to the snapshot schema (2.2 line 123). E24's UNKNOWN clears only on an accepted snapshot of the new version. V35.

**R-12 (Minor).** In 2.9, read the commit time once (t_c) and use it for both step 3 and step 4. Step 4 must complete before t_c + ε, where ε is a declared parameter; S_lim is checked against t_c + ε. CX-17.

**R-13 (Minor, editorial).**
- Section 7: "56" becomes "61 (V01 to V62 less withdrawn V09)".
- 2.5: "A-1 to A-11" becomes "A-1 to A-14".
- I2: label preconditions 3 and 5 as consequences of the decision rule, testable by mutation only.
- 5.2: the validity predicate routes envelope violations (negative F_b) to the V54 path instead of excluding them.
- 5.7(4): add the D26/D27 payload variants (identity change × 3, stale prior_version, prior_qty mismatch, missing field) as test obligations.

**R-14 (Informational).** Add documented-limitation vectors, in the style of V56:
- V63: CX-01, tail loss in RECONCILED;
- V64: CX-12, later bust after an authorized reduction;
- V65: CX-08, a duplicated sell giving an increase false permission.

---

## 10. Founder decisions required

- **FD-1:** The meaning of NO_INDEPENDENT_EVIDENCE in v0.1: (a) no accepted snapshot to cross-check, or (b) single source, under which v0.1 authorizes nothing (R-02).
- **FD-2:** The handling of a sequence-contract violation: (a) a structural failure, or (b) structural plus a stream-epoch field (R-03).
- **FD-3:** Unsequenced executions: out of contract, or a permanent-MISMATCH availability cost (R-10).
- **FD-4:** Later-bust exposure (CX-12): accept it as a documented limitation (I8 detection only), or schedule a fill-finality rule as a post-v0.1 research item. The reviewer recommends the first for v0.1, stated explicitly in the 2.3 limits.
- **FD-5:** Whether R-01 to R-08 are drafted together as one controlled Rev 3.2 candidate (5.7 item 1), with R-09 to R-14 included or deferred.

---

## 11. Implementation-readiness verdict

**NO-GO for a bounded reference implementation of Rev 3.1 as frozen.** Three blocking defects (R-01, R-02, R-03) each force the implementer to invent a rule that decides permission. Three major oracle defects (R-04 to R-06) would corrupt the first run's results.
**Path to CONDITIONAL GO:** a Rev 3.2 candidate containing R-01 to R-08, FD-1 to FD-3 decided, GPT's counter-review of that candidate, and then the 5.7 prerequisites. None of this authorizes broker contact, paper or live trading, or real capital.

| Dimension | Assessment | Label |
|---|---|---|
| 1. Internal coherence | Equations, inventory, lifecycle and commit protocol cohere. Defects: contiguity undefined, the evidence profile contradicts the vectors, G3 classification omitted, the net_cum_at basis, stale counts | verified by reading |
| 2. Mathematical soundness within the model | Sum rule and D19 sound against W1–W7 (hand derivation); vectors checked agree | derived, not executed |
| 3. Assumption adequacy | A-12, A-11, A-7 stated honestly as boundaries. A-2 is too weak for the rules that rely on it. W6's finality of fills is unstated | derived |
| 4. Counterexample coverage | 22 cases here: 4 false-permission paths inside the spec's own text or ambiguity (CX-02, CX-04, CX-19, CX-12), the rest boundaries or safe | derived |
| 5. Oracle adequacy | Correct orientation; domain incomplete (unknown side); status not independently derived; G3 misclassified; nothing executed | verified by reading; unverified as code |
| 6. Independent verification readiness | Not ready: same author throughout; no second-author oracle; no run exists | assumed per spec |
| 7. Operational realism | A-2 contiguity, A-11 broker-unique ids and A-14 prior_version are unvalidated for any real broker; D27's version number would likely be synthesized by the state keeper | unverified |

---

## 12. Questions for GPT's independent hostile review

1. Can you build a false permission *inside* W1–W7 (not using A-12, A-11 or A-7) against the sum rule or D19? This review found none (derived). Attack the n > 1 unsequenced interval together with an unknown-side order.
2. Is R-01's definition of H sufficient, or can out-of-order buffering plus a snapshot at W > H still produce RECONCILED wrongly?
3. Does R-03 option (a) over-trigger on legitimate late redelivery of an event that does fill a recorded gap? Write the precise predicate.
4. Under FD-1 option (a), is a snapshot from the same broker and channel genuinely "independent" enough to justify reductions, given the common-mode clause in W1?
5. Is CX-12 (later bust) correctly classified as an in-model economic limitation rather than a soundness defect, given W6?
6. Is R-07 conservative in every case, or does counting each delivery of an associated execution as a conflict create a new availability trap?
7. Check the oracle world values (line 187) for CANCEL_PENDING orders under W5 with both placements: is any world missing?
8. Independently re-derive V57, V60, V62, B2 and B5 without seeing this review's numbers.

*End of review. Nothing here has been executed except hashing and integer arithmetic. Agreement between this review and any later GPT review is not independent verification.*
