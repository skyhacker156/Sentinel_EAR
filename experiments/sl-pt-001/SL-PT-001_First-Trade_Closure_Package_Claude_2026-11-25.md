# SL-PT-001 First-Trade Closure Package (companion to Revision R3)

**Author:** Claude (Specification Lead / ARBITER). **Date:** 2026-11-25.
**Responds to:** the founder dispatch "SL-PT-001 FIRST-TRADE CRITICAL PATH", §10 items 2, 3, 6, 7 and 8. Items 1, 4 and 5 are in R3 (`b9952600…`): §1, §13 and the body.

**Classification:** planning and specification closure.
- **NOT FROZEN.**
- No harness, no reconstruction script, no Alpaca connection, no credential, no order.
- **The first paper trade is not authorized.**

**Labels** are as in R3. **Model agreement is not verification:** every resolution below names the evidence that would falsify it.

---

## 1. Section-level supersession register (deliverable 2)

### 1.1 Classes and backstop rule

| Class | Meaning |
|---|---|
| **RETAINED** | in force as written |
| **REPLACED** | not in force; the named R3 section governs |
| **SUPERSEDED** | not in force; no successor (withdrawn, historical or answered) |
| **UNVERIFIED** | in force as a statement of an open fact. It is not a settled fact, and it is tracked in R3 §13 |

**Backstop (normative):** in any pre-R3 document, these values are never in force, whether or not a row below lists them:
- `1Hour` or hourly cadence; a 56-hour or 51-hour window;
- `floor_hour`, HH:05, a 5-minute settle;
- a 5-minute or single 180 s TTL;
- 60 s quote freshness;
- AUTHORIZED_SHADOW.

A sentence that depends on one of these values is void. If it cannot be read with the R3 value substituted, it is a finding.

### 1.2 Stage A Design v0.1 (`experiments/sl-pt-001/SL-PT-001_Stage_A_Design_v0.1_SMA20-50_Claude_2026-11-25.md`)

| Section | Class | Governs instead | Note |
|---|---|---|---|
| Header; SA-FD-1 to SA-FD-8 | SUPERSEDED | R3 §1 | map: SA-FD-1→FD-2 (ACCEPTED); SA-FD-2→FD-3 (ACCEPTED, residual CANDIDATE); SA-FD-3→FD-4 (ACCEPTED); SA-FD-4→settle 60 s (CANDIDATE); SA-FD-5→FD-7 (OPEN); SA-FD-6→moot (keyless OBSERVED); SA-FD-7→R3 §3.9; SA-FD-8→FD-6 (ACCEPTED) |
| D1 §1.1 Inputs | REPLACED | R3 §2.1 | 5Min |
| D1 §1.2 Indicators | RETAINED | — | exact sums |
| D1 §1.3 Crossover | REPLACED | R3 §2.2 | FD-2 accepted (same literal rule; the OPEN label removed) |
| D1 §1.4 Edge cases | RETAINED | — | — |
| D1 §1.5 Signal to proposal | REPLACED | R3 §2.3 | — |
| D1 §1.6 Price and size | REPLACED | R3 §6 | FD-4 |
| D2 §2.1 Source | REPLACED | R3 §3.1 | — |
| D2 §2.2 Required fields | RETAINED | — | parsing per R3 §3.2 |
| D2 §2.3 Timestamps and completed candles | REPLACED | R3 §3.3, §3.4 | — |
| D2 §2.4 Missing and duplicate | REPLACED | R3 §3.5 V4, V8 | — |
| D2 §2.5 Precision | REPLACED | R3 §3.2 | — |
| D2 §2.6 Quote-derived bars | REPLACED | R3 §3.6 | — |
| D2 §2.7 Revision | REPLACED | R3 §3.7 | now fail-closed (CF-3) |
| D2 §2.8 Failure behaviour | REPLACED | R3 §3.5, §3.8, §8 R4 | — |
| D3 §3.1 Storage | RETAINED | — | — |
| D3 §3.2 Schema | RETAINED, with the R3 §12 delta applied | R3 §12 | hourly fields void (backstop) |
| D3 §3.3 Illustrative example | SUPERSEDED | — | invented hourly values; never a fixture |
| D4 Walkthrough | RETAINED for step order and the boundary self-check; REPLACED for validation, timing and states | R3 §3.5, §4, §9.1 | AUTHORIZED_SHADOW removed |
| D5 Readiness checklist | SUPERSEDED | R3 §1, §13 | its hourly UNVERIFIED rows are answered or restated in R3 §13 |
| D6 §6.1 U1–U4e, U7, U9, U10, U12–U14 | RETAINED | — | U4c and U4d: literal results expected |
| D6 U5, U6, U8, U11 | REPLACED | amendment v0.2 §3 (RETAINED there) | 5Min values |
| D6 §6.2 X1–X11 | RETAINED with the R3 values | R3 §4, §8 | — |
| D7 "Minimum to run" 1 to 3 | RETAINED | — | not authorized (FD-5) |
| D7 "Can stay manual": hourly hand trigger | REPLACED | R3 §5.4 (FD-7, OPEN) | — |
| D7 "Can stay manual": increments from documentation | REPLACED | R3 §3.9 | Stage A only, CONDITIONAL |
| D7 "Must be deferred": scheduler | REPLACED | R3 §5.4 (FD-7, OPEN) | — |
| D7 "Must be deferred": ETH, LLM, Scoreboard A, Stages B/C, G-07 components | RETAINED | — | the re-fetch check is no longer deferred; it runs from cycle 2 (R3 §3.7) |
| D7 first-cycle success criterion | RETAINED | — | — |

### 1.3 First-Trade Readiness D1–D8, including the older D7 runbook (`experiments/sl-pt-001/SL-PT-001_First-Trade_Readiness_D1-D8_Claude_2026-11-25.md`)

| Section | Class | Governs instead | Note |
|---|---|---|---|
| Bottleneck section (1Hour probe plan) | SUPERSEDED | probe report | FD-1 exercised at 5Min |
| D1 dependency map | REPLACED | §4 below (critical path) | — |
| D2 founder register | REPLACED | R3 §1 | — |
| D3 A-1 to A-3, A-8 | RETAINED | — | — |
| D3 A-4 (TIF) | REPLACED | R3 §6.5 | DEFERRED to Stage B |
| D3 A-5 (increments) | REPLACED | R3 §3.9 | P-1 |
| D3 A-6, A-7 (R15, R16) | REPLACED | R3 §8 | — |
| D3 A-9 | REPLACED | R3 §3, §5 | — |
| D4 build plan | RETAINED | — | not authorized |
| D5 venue report (DOCUMENTED rows) | UNVERIFIED | R3 §13 U-V1 to U-V7 | documentation, not venue fact |
| D6 G-07 readiness matrix | RETAINED, with the TTL row REPLACED by R3 §4.2 and §7 | — | — |
| D7 preconditions | RETAINED, plus one added: metadata read and matching, otherwise STOP (R3 §3.9) | — | the Stage C paper-test precondition is flagged CF-7 |
| D7 step 1 (hourly cycle) | REPLACED | R3 §5 | — |
| D7 step 2 (reconstruction before approval) | RETAINED / UNVERIFIED | R3 §13 U-O1 | it must fit in 120 s |
| D7 step 3 (policy on the reconciled ledger) | RETAINED | R3 §8 | — |
| D7 step 4 (expires_at = issued + 5 min) | REPLACED | R3 §4.2, §7 | — |
| D7 step 5 (approve within the TTL) | REPLACED | R3 §7 | the approval precedes issuance |
| D7 step 6 ($1 / 0.0001 increments) | REPLACED | R3 §3.9, §6 | — |
| D7 step 7 | RETAINED, plus checkpoints (c) and (d) | R3 §7 | — |
| D7 steps 8, 9, 11, 12 | RETAINED | — | — |
| D7 step 10 (TTL cancel) | REPLACED | R3 §4.3, §6.5, §6.6 | — |
| D7 stop conditions | REPLACED | R1 §6 STOP table (RETAINED) and R3 §5.3 | — |
| D7 "keep running hourly shadow cycles" | REPLACED | R3 §5 | 5-minute cycles |
| D8 Go/No-Go | SUPERSEDED | §4 and §5 below | — |

### 1.4 Other documents

| Document / section | Class | Note |
|---|---|---|
| Spec v0.1 §0 (venue) | RETAINED | equity figures: SUPERSEDED by R1 §4 |
| Spec v0.1 §1 (scope, threat model) | RETAINED | ETH: SUPERSEDED |
| Spec v0.1 §2 (TER) | REPLACED | by Stage A Design D3 plus the R3 §12 delta |
| Spec v0.1 §3 (state machine) | RETAINED for Stage B | ordering per R3 §7 |
| Spec v0.1 §4 (P-0.1) | REPLACED | by R3 §8 (P-0.2) |
| Spec v0.1 §5 (exposure) items 2, 4, 6 | RETAINED | — |
| Spec v0.1 §5 items 1, 5 | REPLACED | by R3 §6.6 |
| Spec v0.1 §5 item 3 (fee) | UNVERIFIED | R3 U-V3 |
| Spec v0.1 §6 (shadow procedure) | REPLACED | by Stage A Design D4 (as classified) |
| Spec v0.1 §7 (paper execution) | REPLACED | by Readiness D7 (as classified) plus R3 §7; DEFERRED (FD-9) |
| Spec v0.1 §8 (reconciliation L-1 to L-4) | RETAINED | — |
| Spec v0.1 §9 M1-1 | REPLACED | by R3 §9 |
| Spec v0.1 §9 M1-6 ("≥ 5 trades") | REPLACED | by R3 §9.4: five cycles (FD-6) |
| Spec v0.1 §9 M1-2 to M1-5, M1-7; Stage B exit; Scoreboard B | RETAINED | — |
| Spec v0.1 §10 (limitations) | RETAINED where open; SUPERSEDED where the probe answered | — |
| Spec v0.1 §11 (founder decisions) | REPLACED | by R3 §1 |
| Amendment v0.2 §1 | RETAINED, except the TTL, approval-window and shadow-window rows | those rows are REPLACED by R3 §4.2 |
| Amendment v0.2 §2 | REPLACED | by R3 §9 |
| Amendment v0.2 §3 | RETAINED | U16 re-expressed in R3 §11 |
| Amendment v0.2 §4 | REPLACED | by this register |
| R1 §0 to §8 | REPLACED | by R3, except **R1 §3 (A0.3-13 text)** and **§6 (STOP table, claim language)**, which are RETAINED by reference |
| R2 (all) | SUPERSEDED | absorbed into R3; never reviewed; not in the freeze set |
| Probe report | RETAINED as evidence | not normative |

---

## 2. GPT finding-to-resolution matrix (deliverable 3)

**Source limits (stated):**
- Rows G5-* come from GPT's 5-minute review, as dispositioned in R1 §0.
- Rows GC-* come from GPT's R1 closure review **as summarized in the founder's R1 TARGETED CLOSURE dispatch**. Claude does not hold GPT's original text, so **GPT must check these rows against its own wording.**
- Rows FC-* come from this dispatch §3 A–F.

| ID | Finding | Status | Where | Evidence that would falsify the resolution |
|---|---|---|---|---|
| G5 T-1 | approval deadline vs TTL conflated | RESOLVED IN SPEC | R3 §4.2, §4.3 | any timeline in which an authorization is live after the ceiling, or is issued after approval_deadline (U16, U29, U30) |
| G5 T-2 | the quote goes stale during approval | RESOLVED IN SPEC | R3 §7 item 2 | an authorization consumed without a ≤ 15 s quote at (c) and (d) |
| G5 T-3 | overrun and duplicate processing | RESOLVED IN SPEC | R3 §5 | two records for one cycle_id; a proposal from an overrun cycle (U15, U19) |
| G5 A-1 | approval is not a G-07 predicate | RESOLVED IN SPEC (A0.3-13, CONDITIONAL on the freeze) | R1 §3; R3 §7 | an ACTIVE or CONSUMED authorization without a matching, timely approval (U21, U22) |
| G5 A-2 | the first trade cannot show full mediation | RESOLVED IN SPEC (claim language) | R1 §6; R3 §7 item 7 | any document presenting the first trade as satisfying I5 or I8 |
| G5 D-1 | conflicts with v0.1 | RESOLVED IN SPEC | §1.4 above | a v0.1 provision with no class in §1 |
| G5 D-2 | one probe is not recurring reliability | RESOLVED IN SPEC | R3 §13 U-D1, U-D6 | any claim generalizing from the probe |
| G5 M-1 | narrow milestone claims | RESOLVED IN SPEC | R3 §10 | an exit report claiming beyond R3 §10 |
| G5 M-2 | 5 injections is not coverage | RESOLVED IN SPEC | R3 §9.4 | any rule R1 to R16 without an executed pass and fail test before live data |
| G5 R-1 | reconstruction contamination | **FOUNDER-DECIDED** (FD-6) | R3 §9.3, §9.4 | the script hash recorded after any TER exists; the script authored with harness access |
| G5 FD-G18 | missing from the Stage B register | RESOLVED (DEFERRED with FD-9) | R3 §1 | — |
| GC-1 | supersession incomplete | RESOLVED IN SPEC | §1 above | any pre-R3 hourly, settle, TTL or freshness instruction readable as current |
| GC-2 | counter: broad terminal rule; no missing-cycle detection | RESOLVED IN SPEC | R3 §9 | a non-allowlisted state counted; a missing slot not reported (U26, U27, U34) |
| GC-3 | probe data contract (decimal tokens, zero volume, quote-derived bars, 7/72, increment) | RESOLVED IN SPEC; the 7/72 count is UNVERIFIED | R3 §3.2, §3.6, §3.9; §13 U-D3 | a float in any signal or price path (U25); a `0.0` volume not flagged (U24) |
| GC-4 | FD-4 and displayed size | **FOUNDER-DECIDED**, with CF-1 open for Stage B | R3 §6 | an order sized against displayed size; a reservation above $150 |
| GC-5 | freeze manifest | RESOLVED IN FORM; **blob SHAs need founder confirmation** | §3 below | any manifest hash not matching `git ls-tree` |
| FC-A | founder register | RESOLVED IN SPEC | R3 §1 | an OPEN label left on FD-2, FD-3, FD-4 or FD-6 |
| FC-B | allowlist; HOLD only after validation; denominator | RESOLVED IN SPEC | R3 §9.2, §9.3 | a HOLD qualifying without V1 to V12 evidence (U34); a dropped manifest |
| FC-C | section register; no hourly in force | RESOLVED IN SPEC | §1 above | as GC-1 |
| FC-D | per-bar probe verification | **CONDITIONAL**: not performed (Claude has no copy of the raw file) | R3 U-D2; §4 step P3 | the local check showing non-unique, unordered or gapped `t` |
| FC-E | reservation without double allocation | RESOLVED IN SPEC | R3 §6.6 | two unreleased reservations; a release without terminal evidence (U32) |
| FC-F | exact comparisons; fail-closed | RESOLVED IN SPEC | R3 §4.3, §5.3 | a boundary test failing at ±1 ns (U28 to U30) |
| — | CF-1 to CF-8 (raised by Claude) | **OPEN for review** | R3 §14 | — |

**Critical items not resolved in the specification:**
- **FD-7** (blocks the freeze);
- **CF-1** (blocks Stage B text);
- **FC-D** (conditional; does not block the freeze if the founder accepts it as conditional).

---

## 3. Candidate freeze manifest (deliverable 6; NOT FROZEN)

**Hash columns:**
- **SHA-256** is COMPUTED by Claude over the bytes it delivered.
- **Blob SHA (local)** is `git hash-object` over the same bytes. It equals the repository blob **only if** the committed file is byte-identical with LF line endings.
- **Neither is authoritative until the founder pastes the output of** `git ls-tree -r HEAD -- experiments/sl-pt-001 ear/g07` (§3.4).

### 3.1 Governing specifications, in precedence order

**SL-PT-001 chain:**

| # | Path | SHA-256 | Blob SHA (local) |
|---|---|---|---|
| 1 | `experiments/sl-pt-001/SL-PT-001_Revision_R3_Consolidated_Candidate_Claude_2026-11-25.md` | `b995260029df2b6ef8c811ee8355191e5e6670d63f8756ea8f2437ee1bdb5a85` | `203b4bf5d0d5f2cba124a0ea693b796ecd38c7bd` |
| 2 | `experiments/sl-pt-001/SL-PT-001_Revision_R1_GPT-Reconciliation_Claude_2026-11-25.md` (§3 and §6 only, by reference) | `8cc5168b41fc90323f22bc59ebabcccbfa323c1b3cda826702a06744e34ce8fc` | `1df18f6e12fcc016b913a58ca08bacb1e2d29745` |
| 3 | `experiments/sl-pt-001/SL-PT-001_Amendment_SMA20-50_v0.2_5Min_Claude_2026-11-25.md` | `2df7fb74b1aaf3992cf13ae5a4a71a9bf299f2f1dd3bc189b539de443de4b38b` | `1d9b6c4b0bd06f088af3f4f33999fa928bb3d5ae` |
| 4 | `experiments/sl-pt-001/SL-PT-001_First-Trade_Readiness_D1-D8_Claude_2026-11-25.md` | `e45c82a2cd401a3b6d2878c3aa154c24dcb9ea7a6870ac76a830ba4ed1dc80df` | `0b8d6c7b084b6148e95e26b1864aef48d14af98b` |
| 5 | `experiments/sl-pt-001/SL-PT-001_Stage_A_Design_v0.1_SMA20-50_Claude_2026-11-25.md` | `3444db48fad8623acb2c6e15350b89abac8e6534809deb9f67f15ed1600c2ff3` | `daf5421e4cfb5ff8e0febc4da8ce58b2aec05f0c` |
| 6 | `experiments/sl-pt-001/SL-PT-001_Paper_Trading_Experiment_Specification_v0.1_Claude_2026-11-25.md` | `260f4f4fead2ec3d9f40256ef3d76499258db16ddf8cb975e1e3814e66c17edb` | `5d25faefdeb3874baef3fa95adff2e6260039eac` |
| 7 | `experiments/sl-pt-001/SL-PT-001_First-Trade_Closure_Package_Claude_2026-11-25.md` (this document: register and manifest) | recorded at push (a document cannot carry its own hash) | recorded at push |

**G-07 chain** (governs execution-boundary semantics; SL-PT-001 governs strategy, data, policy and milestone):

| # | Path | SHA-256 | Blob SHA (local) |
|---|---|---|---|
| G1 | `ear/g07/G-07_Architecture_Specification_Draft_0.3_Claude_2026-11-25.md`, plus A0.3-13 as stated in R1 §3 | `f22ee85bb4cb642b14ab7ede6a187e4af0183c09fb0914b6a1dc1e8f884fe1ef` | `1cdbd7d390d07fcb69b12c19eebc9ef266454802` |
| G2 | `ear/g07/G-07_Architecture_Specification_Draft_0.2a_Claude_2026-11-25.md` | `b87ac1c0820698f4cd86eb35757ae4dd041b9c1e3bfeccb20f95cd82a7ab6aa1` | `c518b4442f7b69b3e768bd96feb4336bef9f149a` |
| G3 | `ear/g07/G-07_Architecture_Specification_Draft_0.2_Claude_2026-11-25.md` | `f0404b719f44c5beca12e6ad4a3cc4e58e50aca3da0046393419e9c812606c82` | `32feadfad38877f38e2615f5c5095a6bb9d398b8` |
| G4 | `ear/g07/G-07_Architecture_Specification_Draft_0.1_Claude_2026-11-24.md` | `55141ae662579251e1426a8029f38a9a816d983f23573e8da460f4e03f8bf4a5` | `c44c4ddef17a81109f48b6e1e62c55afe0c189eb` |

**Policy and test inventory:**
- These are R3 §8 (P-0.2) and §11 (U1–U34, X1–X11), inside document 1.
- `policy/P-0.2.json` does not exist yet. It is a build artifact that must match R3 §8 and is hashed at build.

**A0.3-13 trace:**
- R1 §3 → LP-ISSUE (Draft 0.1 §10.1 point 2) → LP-CONSUME (Draft 0.3 §1) → I9 provenance (Draft 0.3 §4).
- Nothing else in G-07 changes.

### 3.2 Supporting evidence (not normative)

| Path | SHA-256 (founder, PowerShell) | Blob SHA |
|---|---|---|
| `experiments/sl-pt-001/SL-PT-001_Stage_A-0_Probe_Report_Claude_2026-11-25.md` | `F6642894CCC9C6526AEA4EBFC73DB4C5DBDC5F94BF984039BB0B7E68B7742782` | local `1095013eac7e5dbd1522b190ce72852f39c2435f` |
| `experiments/sl-pt-001/probe-A0/bars_body.json` | `E3640E5C904B2442913F0511046E9BCF536E4F1B685D73CAF6586CBC0736BADF` | **pending ls-tree** (Claude has no copy) |
| `experiments/sl-pt-001/probe-A0/bars_headers.txt` | `5A6A76FB67CA4B5D1B57A0D7AD7947F24B8E455ED87275187590F87F1396D30E` | pending (CRLF normalization may make the blob differ from the file hash) |
| `experiments/sl-pt-001/probe-A0/quote_body.json` | `D9C34B0D4CD6D210C13F2C2204BDEF03007C33B1E27A3AD47BAEB80953103B5C` | pending |
| `experiments/sl-pt-001/probe-A0/quote_headers.txt` | `741DFAD8A2C72A2DC8DC807D71EB7DA82D95C42F3DE08DFA51EAFB018F094A4D` | pending |
| `experiments/sl-pt-001/probe-A0/probe_meta.txt` | `40CA026FD4B767F832E1895BD57505359909A4485C6DF868BFDEAB46A116450E` | pending |

**Evidence never overrides normative text.** It can only make a statement OBSERVED, or contradict it, which is a finding.

**Excluded:**
- dispatches;
- R2;
- EAR and EIVI-1;
- sealed files (never pushed).

### 3.3 Decisions and assumptions carried into the freeze

- **Accepted decisions:** R3 §1.
- **Unresolved assumptions:** R3 §13 and §14.
- **Freeze preconditions (dispatch §5):**
  1. FD-7 decided;
  2. GPT and Gemini reviews reconciled;
  3. criticals resolved or founder-accepted in writing;
  4. the founder authorizes the freeze;
  5. the freeze record, with the final blob SHAs, is committed **before** the harness exists.

### 3.4 Founder commands (read-only, local; no network, no credentials)

**Authoritative blob SHAs** (paste the output back):
```powershell
cd <your Sentinel_EAR clone>
git ls-tree -r HEAD -- experiments/sl-pt-001 ear/g07
```

**Per-bar probe check** (closes FC-D, U-D2 and U-D3). It reads only the committed file.
```powershell
$p = "experiments\sl-pt-001\probe-A0\bars_body.json"
"sha256=" + (Get-FileHash $p -Algorithm SHA256).Hash
$j = Get-Content $p -Raw | ConvertFrom-Json
$b = @($j.bars.'BTC/USD')
$ts = foreach ($x in $b) { if ($x.t -is [datetime]) { [DateTimeOffset]::new($x.t.ToUniversalTime()).ToUnixTimeSeconds() } else { [DateTimeOffset]::Parse($x.t).ToUnixTimeSeconds() } }
"first=" + [DateTimeOffset]::FromUnixTimeSeconds($ts[0]).ToString('u') + " last=" + [DateTimeOffset]::FromUnixTimeSeconds($ts[-1]).ToString('u')
"bars=$($ts.Count) unique=$(@($ts | Sort-Object -Unique).Count) offgrid=$(@($ts | Where-Object { $_ % 300 -ne 0 }).Count)"
$nonasc = 0; $gaps = 0; for ($i = 1; $i -lt $ts.Count; $i++) { $d = $ts[$i] - $ts[$i-1]; if ($d -le 0) { $nonasc++ }; if ($d -gt 300) { $gaps++ } }
"nonascending=$nonasc gaps=$gaps"
"zero_volume_numeric=" + @($b | Where-Object { [decimal]$_.v -eq 0 }).Count
"next_page_token=" + $j.next_page_token
```

**Reading the result:**
- The expected first and last values are 2026-11-25 21:15:00Z and 2026-11-26 03:10:00Z. A mismatch means the timestamp conversion is wrong; stop and report it.
- Pass: 72 bars, 72 unique, 0 off-grid, 0 non-ascending, 0 gaps.
- The numeric zero-volume count replaces 7/72.
- **Label of the result:** COMPUTED on the founder's machine, one file. The count is a zero test on parsed numbers, so it is exact for zero. This is evidence about one response, not a generalization.

---

## 4. Critical path to the first paper order (deliverable 7)

| # | Dependency | Evidence required | Owner | Blocks freeze? | Blocks first paper order? |
|---|---|---|---|---|---|
| P1 | **FD-7: cycle trigger** (timer vs hand) | a written founder decision | Founder | **yes** | **yes** |
| P2 | push R3 and this package; paste `git ls-tree` | the commit plus the ls-tree output | Founder | yes | yes |
| P3 | per-bar probe check (§3.4), or accept FC-D as conditional | the pasted output, or a written acceptance | Founder | no, if accepted as conditional | no |
| P4 | FD-6 scope: the blind script also performs the slot audit | a written founder decision | Founder | yes (it defines the auditor) | yes |
| P5 | GPT hostile review of R3 against the R1 findings and accepted FDs | review document | GPT | yes | yes |
| P6 | Gemini independent review (counter, decimals and time, timing, reservations, assumptions) | review document | Gemini | yes | yes |
| P7 | finding-by-finding reconciliation register | document | Claude | yes | yes |
| P8 | GPT closure check (resolved, founder-accepted or blocking) | document | GPT | yes | yes |
| P9 | founder written acceptance of residual criticals; **freeze authorized**; freeze record committed with blob SHAs | the commit | Founder | — (this *is* the freeze) | yes |
| P10 | **FD-5** build authorization | a written founder decision | Founder | — | yes |
| P11 | GPT writes the blind reconstruction and slot-audit script from the frozen set; its hash committed before any TER | the hash commit | GPT, Founder | — | yes |
| P12 | Stage A harness built (keyless, read-only) | source revision and hash | harness author (not GPT; FD-5) | — | yes |
| P13 | the test suite **executed**, with evidence retained (R1–R16 pass and fail; U1–U34; X1–X11) | test records, observed vs expected | harness author; Founder runs | — | yes |
| P14 | shadow run: run_length ≥ 30; ≥ 5 runtime injections | run manifests, TERs, injection ledger | Founder | — | yes |
| P15 | blind reconstruction of 5 seeded cycles, plus the slot audit | the script's output; finding list | Founder runs GPT's script | — | yes |
| P16 | Stage A exit report (dispatch §7, items 1 to 10) | document | Claude drafts; Founder | — | yes |
| P17 | CF-1 (FD-4 price timing) confirmed | a written founder decision | Founder | no | **yes (Stage B)** |
| P18 | Stage B package: FD-G13, FD-G16, FD-G17, FD-G18; TIF; CF-7; account configuration; increments; fee; order and partial-fill semantics; I5/I8 limitations | package plus decisions | team; Founder | no | yes |
| P19 | FD-9 Stage B authorization; FD-8 key custody | written founder decisions | Founder | no | yes |
| P20 | Stage B build; G-07 minimum controls implemented **and locally tested** | source, test evidence | team | no | yes |
| P21 | pre-flight read: account (1×, shorting off, buying power) and asset metadata matching the policy | the observed records | Founder | no | yes |
| P22 | first-trade acceptance package (dispatch §9) | package | Claude drafts; Founder | no | yes |
| P23 | **founder approval of the specific order parameters** inside approval_deadline | an approval record bound per R3 §7 | Founder | no | yes (this is the last gate) |

**Order:** P1 to P9 are sequential, except that P3 and P4 can run in parallel with P5 and P6. P10 to P16 are strictly sequential. P17 and P18 can be prepared during P14, but are **decided only after P16**.

---

## 5. The single most important remaining blocker (deliverable 8)

**FD-7, the cycle trigger.**
- It is the only open decision that blocks the specification freeze, and everything downstream of the freeze waits on it: the reconstruction script, the harness, test evidence, Stage A, Stage B and the first order.
- It also decides whether the milestone is reachable at all. A strict 30-slot run with missing slots counted against it cannot realistically be met by hand-triggering every 300 s for 2.5 hours. A timer is a harness-scope change, so it has to be decided before the freeze fixes that scope.
- CF-1 also needs the founder, but it constrains only Stage B text and can wait until after Stage A.

*End of closure package.*
