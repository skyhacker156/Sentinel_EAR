# SL-PT-001 | FD-6 Reconciliation and FD-5 Build Readiness

**Date:** 2026-11-26 · **From:** Claude (Specification Lead / ARBITER, harness author) · **To:** Founder; GPT (FD-6 auditor), through the Founder
**Responds to:** A-Team Dispatch "SL-PT-001 / FD-5 Readiness" (2026-11-26)
**Authority:** none. No harness code has been written. Nothing here is frozen.

---

## A. Exposure statement

**Read in full, from an anonymous clone of `github.com/skyhacker156/Sentinel_EAR` at `07f43e0`:**
- frozen R4.2c (blob `316d08c0…`, SHA-256 `9d417fb5…83d76`, both recomputed). Sections read: §§2, 3.3, 4.1–4.12, 5, 6, 7, 8.1, 10, 11, the §14 rows cited, and §§15–16;
- `SL-PT-001_Interface_Contract_TER-1_v1.md` (SHA-256 `ba5d316c…35e4`, recomputed: **MATCH**);
- `SL-PT-001_FD6_SHA256.txt` and `SL-PT-001_FD6_Seed.txt`;
- the Stage A-0 probe artifacts (`probe-A0/`);
- the dispatch, including GPT's five finding summaries. GPT's own findings text was **not** supplied; only the one-line table in the dispatch.

**Deliberately NOT read:** `sl_pt_001_audit.py`. Its SHA-256 was recomputed (`ac1779b0…246c`, **MATCH**) without reading its logic. As the harness author, I must build from the specification and the interface contract, not from the auditor. If I read its logic I could shape the harness to it, which is the common-mode failure FD-6 exists to prevent.

**Custody standing (OBSERVED):** `b2bbbbb` (contract and script, 16:12 −05:00) and `07f43e0` (hash record and seed, 16:14) are **pushed** to `origin/main`. The dispatch marked push status as unconfirmed; it is now confirmed. Two notes:
- the FD-6 files sit at the **repository root**, not under `experiments/sl-pt-001/audit/` as proposed. This is harmless and nothing needs moving;
- the seed is committed **in cleartext** (see C-06).

---

## B. FD-6 findings reconciliation

A finding **blocks M1-1** if, under frozen R4.2c, a strict auditor cannot establish M1-1 however well the harness behaves.

| ID | Valid? | Already resolved by frozen text? | Kind | Blocks M1-1? | Smallest correction | New freeze? |
|---|---|---|---|---|---|---|
| **FD6-01** V12a evidence | **Valid** | **No.** §11.1 requires every qualifying condition to be checked "by **recomputation**, never from fields", and V12a is a qualifying condition for every state. Yet §10.4 retains only V12a's result, and "credential" is never defined, so nothing can be recomputed. | **Normative contradiction** (§11.1 vs §10.4) plus missing evidence | **Yes.** Under strict reading, no slot can qualify | **D-2:** define "credential" (env names beginning `APCA_`/`ALPACA_`, case-insensitive; closed config file); record V12a evidence (matching variable names, never values; config SHA-256; the client-reported allowlist); store the config bytes only on PASS. Amend §11.1 so V12a is recomputed from that evidence and labelled **HARNESS-ATTESTED** | Yes |
| **FD6-02** commit instant | **Valid** | **No.** §5.4 defines "cycle within slot" as committed at an instant < T_d(i+1), and §11.1 requires SHADOW_EXPIRED "recorded at the ceiling". No TER field records the commit instant. Chain order bounds the commit only up to the successor's lock acquisition, which comes later than T_d(i+1) | **Missing evidence** | **Yes** for any slot with a live BUY proposal (SHADOW_EXPIRED or REJECTED), which on live data happens on every BUY crossover (§3.3) | **D-3:** add `committed_at`, read under the append lock; append only if < T_d(i+1), and for SHADOW_EXPIRED only if ≥ ceiling. HARNESS-ATTESTED, at the same evidential tier as `t_send` and `created`, which the spec already relies on | Yes |
| **FD6-03** injection intent | **Valid** | **No.** §11.4 counts injections "rejected by the intended rule", but §10.1 retains only "injected proposal and result". Nothing records the intended rule, the fixture inputs, or when either was fixed | **Missing evidence** (a normative criterion with no retained basis) | **Yes** (the second clause of M1-1) | **D-4:** a founder-committed injection plan and fixtures, pushed before the injections; the plan, fixture hash and intended rule in the INJECTION TER; "rejected by the intended rule" defined as the intended rule FAIL, every other applicable rule PASS, and distinct fixtures; Stage A injections are **BUY-only**. This also removes GPT's EXIT-fixture gap without specifying the Stage B EXIT reservation | Yes |
| **FD6-04** pagination | **Valid** | **No.** V2 permits fetching every page, but §10.4 allows exactly one bars request object and one artifact pair. A multi-page success is therefore unrepresentable | **Normative contradiction** (§4.7 V2 vs §10.4) | **No in practice** (`limit=1000` against a 59-bar window; the probe returned `null`, OBSERVED). But the harness would be required to do something it cannot record | **D-1:** V2 passes only on a JSON `null` token; any other value → INCOMPLETE_RESPONSE, and no page is fetched. U13/U94 rewritten | Yes |
| **FD6-05** R2 in Stage A | **Valid** | **No.** §7.3 lists R2 as "B (A: limit)", while §11.6 says "R2 and R14 exist only in Stage B" and omits R2 from the pre-live coverage list | **Normative contradiction** (§7.3 vs §11.6) | It decides whether the pre-live gate requires R2 tests | **D-5:** keep §7.3 and correct §11.6: R2's limit-order check applies in Stage A, its TIF and partial-fill parts in Stage B; R2 is added to the coverage list. This matches GPT's contract choice | Yes |

**Claude's additional findings (same test applied):**

| ID | Finding | Kind | Blocks | Correction |
|---|---|---|---|---|
| **C-06** seed custody | The seed (`51c36b3d…`) and GPT's sampling function (contract §7) are both public before any run. The harness author can therefore compute **which seqs will be reconstructed**, and the five-cycle reconstruction is no longer blind to the harness | Independence defect | **M1-6** integrity, not M1-1 | **D-7:** commit-reveal. The founder commits only SHA-256(new seed) before the first audited T_d0, and reveals the seed after the last RUN_CLOSE, never to the harness author before then. The current seed is **burned**: keep its file and mark it superseded |
| **C-07** bar-store fold on invalid responses | §4.9 folds "every completed bar fetched" with no validity condition. A response that fails V3 (unplaceable `t`) or V9 (a `"NaN"` token) would still enter the store and alter V11 for later slots. GPT's contract chose not to fold such responses, so the harness and the auditor could diverge | Normative ambiguity | Can make later slots disagree (M1-6, slot audit) | **D-6:** only responses passing V1–V4 and V9 contribute observations. This adopts GPT's rule **as specification**, so both sides derive it from the spec and not from each other |
| **C-08** header artifact | The contract requires the **exact wire** status line and header bytes. A standard HTTP client cannot capture those, and the contract itself says this needs founder resolution. §4.3 says only that headers are "stored" | Underspecification at the build boundary | **Blocks the build** (the artifact format) | **D-8:** the body is the bytes after transfer decoding, requested with `Accept-Encoding: identity`; the header artifact is a fixed client-reported serialization, explicitly **not a wire capture**. The probe's `bars_headers.txt` already has this shape |

**Disagreement with GPT:** none on validity. One point of framing. For FD6-01 the contract's strict outcome is "NON-QUALIFYING (unverified)" for every slot. That is the correct reading of R4.2c, but it is unsatisfiable by **any** harness under Branch C. The fix is therefore to state, in the specification, what tier of evidence V12a can reach, not to make the harness more elaborate.

---

## C. Interface compatibility findings (GPT contract v1)

Every material CONTRACT CHOICE was checked against R4.2c:

| Contract item | Classification | Note |
|---|---|---|
| Decimal strings without a slash (§1) | ACCEPTABLE | Every Stage A output terminates: sums ÷ 20 or ÷ 50, ÷ 2 for mid, and the named rounding points (DERIVED, §5.1, §8.1.1) |
| `cycle_id` as a 2-element array; `seq` and `declared_slots` as JSON safe integers | ACCEPTABLE | The string-only rule of §10.4 covers the TER only; both values sit outside it |
| TER key names and flat V/Q grouping; `S20_k` etc.; `T_d`, `created`, `invocation_instant` | ACCEPTABLE | |
| Request object; presence/precedence table (§2) | ACCEPTABLE | Matches the §10.4 table row by row |
| Bar shape incl. `zero_volume` | ACCEPTABLE | §4.8 requires the flag; this is not an added field |
| Transitions: events, PENDING count, confirmation count = 2, A→B→A = two revisions, ordering | ACCEPTABLE | Consistent with §4.9, U40, U85 |
| Fold suppression on V1/V2/V3/V4/V9 failure (§7.5) | UNDERSPECIFIED in R4.2c → **resolved by D-6** | |
| `NO_DECISION (REASON)`, `NO_ACTION (BLOCKED_OPEN_ORDER)` spellings | ACCEPTABLE | R16 is vacuous in Stage A |
| RuleResult incl. R2 limit-only | ACCEPTABLE → **made normative by D-5** | |
| Proposal / Rounding; no EXIT R convention | ACCEPTABLE given **D-4 (BUY-only injections)** | |
| Chain envelope; GENESIS `prev_hash` null; record-hash rule; JCS (§6) | ACCEPTABLE | |
| Overrun matched by slot, not PID | ACCEPTABLE | The wrapper starts the harness as a child, so their PIDs differ |
| Run attribution of records without a manifest hash | ACCEPTABLE | |
| Manifest closed object, `frozen_set_hashes` map | ACCEPTABLE | Content default: the frozen spec, its freeze record and correction notes. The founder sets this in each manifest; no separate decision is needed |
| Invocation line format; policy JSON shape and values | ACCEPTABLE | Values match §7.3 and §7.4 |
| Layout under `experiments/sl-pt-001/` | ACCEPTABLE; **contract v2 must add** `injections/` (D-4) | |
| Header artifact = exact wire bytes (§5) | **INCOMPATIBLE as a build requirement** (unattainable with an ordinary client; stricter than §4.3) → **resolved by D-8** | |
| Gaps §7.1–7.4 | → **resolved by D-2, D-3, D-4, D-1** | |
| Malformed-array recording; L rounded to 0 (§7.6) | UNDERSPECIFIED, **nonblocking** | Fail-closed in the auditor; L = 0 needs an ask below $1, unreachable for BTC/USD (DERIVED) |
| Sampling function (§7) | ACCEPTABLE function; **seed custody → D-7** | |

**Contract v2 (GPT authors it, after the freeze):** it must add `committed_at`, the V12a evidence object, the injection fields and the `injections/` layout, and adopt D-1, D-6, D-7 and D-8. I have not drafted any contract or auditor text.

---

## D. Minimum freeze delta: R4.2d (candidate, NOT frozen)

R4.2d = frozen R4.2c plus **D-1 to D-8 only**: 23 mechanical edits, each asserted to match R4.2c exactly once, giving 54 changed lines. Every unaffected line is byte-identical.

| Item | Sections | Summary |
|---|---|---|
| D-1 | §4.2, §4.7 V2, U13, U94 | null page token only; no pagination |
| D-2 | §6.4 step 1, §10.4, §11.1, §15 U-I3, U116 | V12a defined and evidenced; HARNESS-ATTESTED |
| D-3 | §5.4, §6.4 step 8, §10.4, §11.1, U117 | `committed_at` |
| D-4 | §6.5, §10.1, §10.2, §10.4, §11.4, U118 | injection plan, fixtures, intent; BUY-only |
| D-5 | §11.6, U119 | R2 limit check in Stage A |
| D-6 | §4.9, U115 | fold only valid responses |
| D-7 | §11.5, U120 | seed commit-reveal |
| D-8 | §4.3 | body and header artifact representation |

**Files:** `SL-PT-001_R4.2d_Stage_A_Amendment_Candidate_Claude_2026-11-26.md` (SHA-256 `68fe01e0f4d98fd575c13edb33c99030d54029a9b00723fedaf42f01ca059667`, git blob `b60327c673f19285813311b0ee343ac6596ed813`) and `SL-PT-001_R4.2d_Delta_vs_R4.2c.diff` (158 lines, SHA-256 `26387eed…efe7`).

**Review treatment (dispatch §7):** D-2 and D-3 are invariant and evidence-model changes, so they need hostile review; the rest are behavioural. Send **only the diff plus R4.2c** to GPT and Gemini B as one targeted closure round. Under dispatch §7, a review of the diff alone counts as targeted verification, not full-document verification.

**Path disposition:**
- **Path A (existing freeze sufficient): rejected.** FD6-01, -02 and -03 are normative requirements with no retained evidence, so no harness can satisfy a strict auditor under R4.2c.
- **Path C alone: rejected.** Accepting FD6-01 to -03 as limitations would make **M1-1 unattainable**, not merely weaker. That would trade the milestone for speed.
- **Recommended: Path B (R4.2d), with a residual Path C element** stated in the spec itself. V12a and `committed_at` are **HARNESS-ATTESTED**. The claims "credential absence independently verified" and "commit timing independently verified" become unavailable, as under Branch C they always were. Stage A exit remains possible.

---

## E. FD-5 build readiness plan (not started)

Language: Python 3.12, standard library only (`http.client`/`ssl`, `json` with token-preserving hooks, `fractions`, `hashlib`, `msvcrt` locking). Governing text: R4.2d once frozen.

| # | Component | Governs | Artifact | Acceptance | Depends on |
|---|---|---|---|---|---|
| 1 | Exact arithmetic and raw-token parsing | §4.3–4.4, §4.10, §5.1 | `sentinel_pt/exact.py` | no `float` anywhere (AST check); exponent and `-0` tokens; RFC-3339 → ns exact; named rounding points only | — |
| 2 | Time, slots, clock check | §5.2–5.6, §6.2 | `slots.py`, `clock.py` | U53 property test; V12b's 4 conditions incl. exactly 3 s; owning-slot and OFF_RUN boundaries | 1 |
| 3 | Keyless allowlisted client + V12a | §2.2–2.3, §4.1–4.3, §6.4 (1–4); D-2, D-8 | `client.py`, `boundary.py` | any non-allowlisted host refused before I/O; no auth header code path; U112, U113, U116; artifacts in the D-8 format | 1 |
| 4 | Raw artifact retention | §10.2 | `artifacts.py` | content-addressed write before parse; idempotent; no overwrite | 3 |
| 5 | Candle validation and revision store | §4.5–4.9, D-1, D-6 | `validate.py`, `barstore.py` | V1–V11 non-short-circuit rule (U111); U13, U40, U85, U94, U115; fold from chain only | 1, 2, 4 |
| 6 | SMA-20/50 signal | §3.1–3.2, §3.4 | `signal.py` | FD-2 equality semantics; quote independence (U18) | 1, 5 |
| 7 | Signal-to-action mapping | §3.3 | `mapping.py` | the full table; Stage A flat ⇒ EXIT → NO_ACTION | 6 |
| 8 | Proposal sizing + policy P-0.2 | §4.11, §7, §8.1–8.1.1; D-5 | `policy.py`, `policy/P-0.2.json` | executed pass and fail case per Stage A rule incl. R2 (U119); R ≤ budget invariant | 1, 2, 7 |
| 9 | Chain, TER-1, manifests | §6.3, §10.1, §10.3–10.5; D-3, D-4 | `chain.py`, `ter.py` | closed schema (U67); JCS hashes; append lock; `committed_at` gate (U117); RUN_CLOSE overrun | 1–8, **contract v2** |
| 10 | Wrapper, Task Scheduler XML, single writer | §6.1, §6.3 | `wrapper.py`, exported XML | U73–U77 against the exported XML; CONCURRENT_INVOCATION; overrun by successor | 9 |
| 11 | Stage A tests + controlled evidence | §14 (Stage "A"), §11.6 gate | test suite, retained run log | every Stage-A test EXECUTED with retained output **before** the first live cycle | 1–10 |
| 12 | Auditor run + founder cross-check | §11.2–11.5; D-7 | audit report (GPT script v2) | the founder runs it; the cycle_id hand cross-check matches; M1-6: 0 unexplained differences | 11, a live run, the seed reveal |

**Essential for the milestone:** 1–12. **Deferred (not built):** anything in Stage B (§§8.2–9, 12), Branch H, credentials, order code, the EXIT reservation, and a harness-side counter (§11.4 says it is never evidence).

**Environment:** install Python 3.12 from python.org beside 3.14 and invoke it as `py -3.12`. Both the harness and the auditor run on 3.12. This is environmental and needs no decision.

---

## F. Founder decision request

**One decision:** *Adopt Path B, and send R4.2d (diff plus R4.2c) to GPT and Gemini B for one targeted closure round?*

Approving it also means accepting the four choices inside the delta, which are yours to reject individually: the credential name pattern (`APCA_`/`ALPACA_`), BUY-only injections, the strict injection attribution (only the intended rule fails; distinct fixtures), and seed commit-reveal.

After a clean round, the second decision is the **R4.2d freeze**. Then GPT writes contract and auditor v2 from R4.2d only, and you commit the hash of a new seed. Code starts after that.

---

## G. Gate verdict

**FD-5 CONDITIONALLY READY.**

Conditions, all required before the first line of harness code:
- C1: R4.2d frozen by a founder record;
- C2: GPT's contract and auditor v2 committed with their hashes;
- C3: SHA-256 of the new seed committed, with the seed withheld from Claude;
- C4: Python 3.12 installed.

The existing FD-5 authorization (`5252322`) names R4.2c. When R4.2d is frozen, the freeze record should state that FD-5 now applies to R4.2d. **This verdict is not implementation authority.**
