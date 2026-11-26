# SL-PT-001 Review Recovery and R4 Requirements

**Author:** Claude. **Date:** 2026-11-25 (UTC 2026-11-26).
**Responds to:** the founder dispatch "SL-PT-001 REVIEW RECOVERY AND R4 PREPARATION".
**Classification:** recovery / design / evidence control.
- No freeze, implementation, credentials, trading connection or order authority.
- **R3 (blob `203b4bf5…`) is unchanged.**

**Distribution:**
- Founder.
- §1 (the incident record) may be shared with GPT and Gemini now.
- **§6.2 row P4 refers to sealed annex S2. Do not share §6.2 or the annex with either reviewer until both standalone reviews are delivered.**

---

## 1. Review-integrity incident record (deliverable 1)

| Field | Record |
|---|---|
| Incident ID | RI-2026-11-25-01 |
| Artifact | `sealed/SL-PT-001_R3_Claude_Self-Findings_SEALED_2026-11-25.md` |
| SHA-256 | `bbe76a1ac0fb1c9c708bb0d096a4da7db9d9a1e8f7e5c34fc341a451f6a006f5` |
| Created | 2026-11-25 22:52:49 −05:00 (03:52:49Z), Claude workspace file time |
| Content | SF-1 (revision baseline), SF-2 (declared run end), SF-3 (slot-anchored timing) |
| Intended holder | the founder only, with the hash recorded and the content withheld from reviewers until both reviews were delivered |
| What happened | the note's content reached both reviewers **before** either standalone R3 review was delivered. One reply reproduced it verbatim; the other assessed each finding. Relayed to Claude at 2026-11-25 22:53 −05:00 |
| Effect | both reviewers had prior exposure to SF-1, SF-2 and SF-3. **Their later identification or assessment of those findings cannot establish independent detection.** The commit-before-reveal sensitivity measurement is **invalid for SF-1 to SF-3** |
| Unaffected | the GPT-versus-Gemini comparison for every finding **outside** SF-1 to SF-3, provided neither reviewer receives the other's review before submitting |
| Preservation | the original note is kept **unchanged**, with its hash and file time. Nothing is deleted or rewritten. The original blind conditions are **not** represented as intact |
| Remediation | (a) the reconciliation separates disclosed findings (§2, category 2); (b) new Claude findings are sealed in annex S2, **founder only**, with the hash recorded before any review is delivered; (c) future sealed artifacts go only to the founder; reviewers receive the hash, never the content |
| Annex S2 | `sealed/SL-PT-001_R3_Claude_Sealed_Annex_S2_2026-11-25.md`, SHA-256 `e0d0703ebb00d1ccd2652d2402ed35b27eab8d103a460e59d3aca85348d1ba8c`, 2 findings. **Founder action:** record this hash in a commit message now; do not forward the content |
| **Addendum RI-2026-11-25-02** | at 2026-11-25 23:03 −05:00 the founder confirmed that annex S2 had been passed to **GPT**, which acknowledged it, tried to commit the hash and returned a hash-commitment file. GPT is a standalone R3 reviewer, and its exposure is treated as exposure of the reviewing instance (shared chat or account memory cannot be excluded). **S2-1 and S2-2 are therefore exposed to GPT and not to Gemini** (as far as is known). Exposure is now asymmetric: GPT has seen SF-1 to SF-3 and S2; Gemini has seen SF-1 to SF-3 only. The S2 hash commitment remains valid as proof of Claude's priority |
| Process rule (from RI-02) | sealed content never passes through any A-Team model conversation, **including as a request to record its hash**. The founder computes or commits hashes directly (`Get-FileHash`; `git commit`). Only the hash string may be given to a model |
| Disposition of the original note | it may be committed to the repository unchanged **after** reconciliation, as incident evidence. It is no longer secret, but committing it changes nothing about review conditions until then. Founder's choice |

---

## 2. R3 review reconciliation template (deliverable 2)

One row per finding. A finding raised by both reviewers gets one row, with both sources.

| Field | Content |
|---|---|
| ID | RC-nn |
| Category | **1** independent: outside SF-1 to SF-3 and not in annex S2 / **2** disclosed: SF-1 to SF-3 / **3** disagreement / **4** new: neither Claude nor the dispatches identified it / **2S** sealed: annex S2 items, scored after unsealing |
| Raised by | GPT · Gemini · both (each one's ID) |
| R3 section | — |
| Mechanism | the exact failure, as each reviewer stated it |
| Severity | GPT / Gemini (both kept if they differ, which makes it category 3) |
| Detection status | independent (category 1 or 4) · not independent (category 2) · sealed match (2S: the reviewer found an S2 item without exposure) |
| Claude disposition | accept / reject (with a reason) / partial |
| R4 action | the targeted correction, or "none" |
| Falsifier | the evidence that would show the correction fails |
| Founder decision needed | yes / no |
| Minority preserved | yes, if one reviewer dissents; their text is quoted, not summarized |

**Rules:**
- Agreement is recorded as **agreement**, never as verification.
- A category-2 match counts zero toward reviewer sensitivity.
- **Category 2S is scored per reviewer (RI-02):** a Gemini match on S2-1 or S2-2 is independent detection; a GPT match is **not** (it was exposed).
- Sensitivity is reported separately for categories 1, 4 and 2S.

---

## 3. R4 correction requirements (deliverable 3)

R4 is written **only after** reconciliation. These are mandatory targets, together with whatever the reconciliation adds.

### 3.1 SF-1: revision baseline

1. **Accepted window** := the 51-candle input of a cycle that passed V1 to V10 and V12. Its bars are recorded with their token text.
2. The **baseline** for cycle c is the accepted window of the most recent cycle (any slot, any run, same instrument) whose accepted window overlaps c's fetched bars. TER field: `revision_baseline_cycle_id`.
   - With no prior accepted window, the field records `NONE` and `revision_overlap = 0`.
   - With no overlap, it records the baseline id and `revision_overlap = 0`.
3. A revision is any overlapping bar whose token text differs from the baseline's.
4. **Correction to the required behaviour (a new defect, category 4, found by Claude):** if "most recent accepted window" were applied literally, a SOURCE_REVISION cycle would never become accepted. Every later cycle would compare against the same old baseline, see the same revision, and fail forever: a **lockout**. R4 must therefore add a stability rule:
   - a revised bar's new bytes become **pending**;
   - a later cycle that observes the **same** bytes again accepts them. That cycle's baseline for this bar becomes the pending bytes, and the revision is not counted twice;
   - a further change produces a new SOURCE_REVISION.
   - Net effect: one revision costs at least one NO_DECISION slot and never causes a permanent lockout.
5. The fail-closed rule is otherwise unchanged:
   - a new revision inside the current 51-candle window → NO_DECISION (SOURCE_REVISION);
   - outside it → recorded only;
   - Stage B pending proposals and authorizations depending on the bar are invalidated.

### 3.2 SF-2: declared run end

1. The run manifest gains `declared_slots` = N, an **integer slot count** (not an instant), with N ≥ 30. The slots are i = 0 … N − 1. The derived end instant is T_d(0) + 300 s · N.
   - *Why a count:* an integer has no clock or zone interpretation, so it is unambiguous.
2. **No open-ended run is milestone-eligible.** A manifest without `declared_slots`, or with N < 30, is recorded and reported, but cannot satisfy M1-1.
3. The run is judged once now ≥ T_d(0) + 300 s · N. Every slot 0 … N − 1 is classified (R3 §9.3). **Slots without a record are MISSING**, including every slot after an early stop.
4. Early stop: the harness may write RUN_STOPPED. It neither removes slots nor shortens N.
5. **Selective omission:**
   - all runs share **one global hash chain** from a genesis record;
   - each manifest's hash is the first chained record of its run;
   - the audit verifies chain continuity from genesis, so an omitted run, record or manifest breaks the chain and is reported;
   - the exit report lists every manifest in the chain.
6. **Limitation (stated):**
   - git commit timestamps are self-asserted, so the "manifest before T_d(0)" ordering is evidenced by the chain position plus the GitHub push record. It is **not** proven by the commit date.
   - The chain proves completeness *relative to the genesis record* only.

### 3.3 SF-3: slot-anchored timing

| Symbol | R4 definition |
|---|---|
| T_d | slot decision instant (close + 60 s) |
| created | proposal creation instant; always ≥ T_d (R3 §5.2) |
| W | the **founder-defined minimum remaining approval window** (§5.3) |
| cutoff | a proposal is created only if T_d + 120 s − created ≥ W. Otherwise the proposal record is **REJECTED (R13)**: computed, sized and recorded, **never presented for approval** |
| approval_deadline | min(created + 120 s, T_d + 120 s) |
| issued | must be ≥ approved_at and ≤ approval_deadline |
| expires_at | min(issued + 60 s, T_d + 180 s) |
| Stage A ceiling | SHADOW_EXPIRED at T_d + 180 s |
| Stage B order | any unfilled remainder has its cancel requested no later than T_d + 180 s |

**Non-contradiction (DERIVED; must hold for every created ∈ [T_d, T_d(i+1))):**
1. created ≥ T_d ⇒ created + 120 s ≥ T_d + 120 s ⇒ **approval_deadline = T_d + 120 s** always. The min never selects the creation-relative term, and the deadline cannot pass the next slot.
2. issued ≤ approval_deadline = T_d + 120 s ⇒ issued + 60 s ≤ T_d + 180 s ⇒ **expires_at = issued + 60 s** always. Every authorization gets its full 60 s, and every authorization dies by T_d + 180 s < T_d(i+1) = T_d + 300 s.
3. The cutoff guarantees at least W of approval time for any proposal that exists. A proposal that cannot get W never exists, so no proposal is ever created with an already-expired or unusable window.
4. LP-PRESEND requires **0 < δ_send < 60 s**. Otherwise no authorization could ever pass. A configuration violating this is refused at start-up as BOUNDARY_FAIL.
5. Stage A: SHADOW_EXPIRED at T_d + 180 s commits before T_d + 300 s, so a proposal alone cannot force CYCLE_OVERRUN.

**Counter consequence:**
- R3 §9.2's REJECTED row reads "a proposal constructed". For R13 cutoff rejections it is amended to "a proposal record computed and rejected at creation".
- Such a slot still **qualifies**, because the data was valid and the policy outcome is correct.

---

## 4. Regression-test requirements (deliverable 4)

The IDs continue R3 §11. Times are relative to T_d. **None of these is executed.**

| ID | Case | Input | Pass | Fail case that must also be tested |
|---|---|---|---|---|
| U35 | first cycle of a run | no prior accepted window | `revision_baseline_cycle_id = NONE`, overlap 0, decision proceeds | the field absent → TER invalid |
| U36 | baseline across NO_DECISION | slots 1 OK, 2 NO_DECISION, 3; a bar revised between 1 and 3 | slot 3 baseline = 1; revision detected | baseline = 2, or detection skipped |
| U37 | baseline across MISSING | as U36, with slot 2 having no record | same | same |
| U38 | baseline across SKIPPED / overrun | slot 2 CYCLE_OVERRUN, slot 3 SKIPPED, slot 4 | slot 4 baseline = 1 | same |
| U39 | **anti-lockout** | revision detected at slot 3 (NO_DECISION); same bytes at slot 4 | slot 4 accepts and proceeds; revision recorded once | slot 4 fails again, or the revision is counted twice |
| U40 | flip-flop | bar bytes A → B → A over three cycles | two SOURCE_REVISION events | the second change is missed |
| U41 | early termination | N = 40; records for slots 0 to 24 only | slots 25 to 39 MISSING; run_length ≤ 25 | slots after the stop dropped from the denominator |
| U42 | no declared_slots / N < 30 | manifest lacking the field; and N = 29 | not milestone-eligible; reported | M1-1 marked met |
| U43 | selective omission | three runs; run 2's records removed from the chain | chain break reported; run 2 listed as omitted | the audit passes |
| U44 | on-time proposal | created = T_d + 5 s | proposal; deadline T_d + 120 s | deadline computed from created |
| U45 | late, sufficient | created = T_d + 120 s − W (exactly) | proposal (inclusive) | rejected |
| U46 | late, insufficient | created = T_d + 120 s − W + 1 ns | REJECTED (R13); slot QUALIFYING | a proposal shown for approval; or the slot non-qualifying |
| U47 | very late (Stage A) | created = T_d + 250 s | REJECTED (R13); no SHADOW_EXPIRED after T_d + 180 s | SHADOW_EXPIRED at created + 180 s |
| U48 | approval at the inclusive deadline | approved_at = T_d + 120 s; and + 1 ns | valid; then EXPIRED_UNAPPROVED | inverted |
| U49 | expiry at the strict boundary | issued = T_d + 120 s; probes at T_d + 180 s − 1 ns and at T_d + 180 s | live; then not live | live at T_d + 180 s |
| U50 | LP-PRESEND margin | δ_send = d, 0 < d < 60 s; probes at expires_at − d and − d + 1 ns; configurations d = 0 and d = 60 s | pass; fail; BOUNDARY_FAIL at start-up for both configurations | any send after expires_at − d |
| U51 | cycle transition with something unresolved | an order from slot i still resting at T_d(i+1) | slot i+1 → NO_ACTION / BLOCKED_OPEN_ORDER; no authorization of slot i live at T_d(i+1) | a new proposal at slot i+1 |
| U52 | slot boundary invocation | invocation at exactly T_d(i+1) | belongs to slot i+1 | it processes slot i |
| U53 | **property test** (not just an example) | random created ∈ [T_d, T_d + 300 s), random approval and issuance times within the rules | invariants 1 to 5 of §3.3 hold in every sample, and the sample seed is recorded | any counterexample |

U53 is the only test above that tests a *property*; the others are examples. The property it checks is also DERIVED analytically in §3.3. The test can falsify it but cannot prove it.

---

## 5. Founder decision register (deliverable 5; recommendations only, nothing accepted)

### 5.1 FD-6 scope: does the blind script also perform the slot audit?

| Option | For | Against |
|---|---|---|
| **(a) yes, in GPT's blind script** (founder recommendation) | one isolated author; the audit is mechanical (an enumeration of the manifest and chain) | **common-mode risk:** if GPT misreads the slot rules, both reconstruction and audit inherit the error |
| (b) a separate auditor | removes that common mode | a second independent author is needed, and none is identified |

**Claude recommendation: (a), plus one cheap cross-check that is not a script:** for one manifest, the founder enumerates the expected cycle_ids by hand (N rows) and compares them with the audit's slot list. Isolation: GPT gets the frozen set only, and its hash is committed before any TER (FD-6, unchanged).

### 5.2 FD-7 scheduling

| Option | Effect on M1-1 | Risk |
|---|---|---|
| **(i) a minimal local timer** (founder recommendation) | reachable; misses become MISSING slots, visibly | the timer must not suppress, retry or batch (below) |
| (ii) hand trigger | **practically UNBOUNDED**: 30 consecutive invocations, each inside its 300 s slot | operator fatigue; every miss restarts the run |
| (iii) change the milestone | reopens a founder decision and GPT's adopted strict rule | weakens the evidence |

**Claude recommendation: (i)**, realized with the operating system's scheduler (Windows Task Scheduler) rather than new code, because then the timer contains no logic of its own. Required constraints:
- trigger every 5 minutes at minutes 1, 6, 11, …, 56 of each hour, second 0 (that is, T_d = candle close + 60 s);
- "if the task is already running": **run a new instance in parallel**. The harness lock then records CONCURRENT_INVOCATION; the timer never suppresses silently;
- "run as soon as possible after a missed start": **off**. A catch-up launch would be a late invocation, which the slot rules handle, but it hides why the slot was missed;
- no retry on failure;
- the machine must not sleep during a run;
- the **task's exported XML definition is hashed into the run manifest**;
- each invocation writes one line (the instant and the process id) to an append-only invocation log, outside the harness. The audit compares that log with the slot records: an invocation with no record is a finding, and a slot with neither is MISSING.

These Task Scheduler setting names and behaviours are recalled from documentation and are **UNVERIFIED**. They must be checked against the exported XML before the first run.

### 5.3 SF-3 minimum remaining approval window W

The approval time available is at most 120 s, because approval_deadline = T_d + 120 s.

| W | Proposal cutoff (created ≤) | Founder review time | Implication |
|---|---|---|---|
| 30 s | T_d + 90 s | ≥ 30 s | tolerant of a late invocation; too short to review a TER and a reconstruction diff (Readiness D7 step 2) |
| 60 s | T_d + 60 s | ≥ 60 s | balanced; review is tight |
| **90 s** | T_d + 30 s | ≥ 90 s | the most review time; requires the timer (§5.2), since a hand trigger often misses 30 s |

**Claude recommendation: W = 90 s, applied identically in Stage A and Stage B** so that the shadow behaviour equals the live behaviour.
- In Stage A, a late slot still qualifies (as REJECTED under R13), so the milestone is unaffected.
- **Caveat:** whether the Stage B reconstruction plus a review fits in 90 s is **UNVERIFIED** (R3 U-O1). If a dry run shows it does not, W cannot fix that, because the 120 s ceiling binds first. That would be a Stage B finding.

### 5.4 CF-7: first-order circularity

**Problem:** Readiness D7 requires query-by-COID and duplicate-COID tests executed **on paper** before the first order. Those tests need paper orders, which would precede the controls meant to govern them.

**Non-circular sequence (Claude proposal):**
1. **Before any order:** local tests against a stub venue for every G-07 minimum control and the AMBIGUOUS path (Stage B build evidence).
2. **Stage B pre-flight, read-only with paper keys, no order:**
   - list orders (expect none open);
   - query a **never-used** COID (expect not-found; the response is recorded). This establishes the not-found branch without an order.
3. **The first order is itself the first governed order,** under full approval and G-07 controls. After it reaches a terminal state, query it by its COID. That establishes the found branch.
4. **The duplicate-COID test** becomes a later, separately authorized test order (Stage C). The first order does not depend on it, because FD-G16's candidate is "no same-COID resubmission": ambiguity is handled by query-then-stay-AMBIGUOUS, which needs only the two branches above.

**Founder decision:** adopt this sequence (it amends the Readiness D7 preconditions), or keep the original and accept pre-governance test orders.

---

## 6. Verification instructions (deliverable 6)

**Run in your `Sentinel_EAR` clone. All of this is read-only and local** (`git fetch` only contacts GitHub). Paste back the full output. **Nothing is verified until the output is supplied.**

### 6.1 Repository identity

```powershell
git fetch origin
"HEAD=" + (git rev-parse HEAD); "origin/main=" + (git rev-parse origin/main); git status --porcelain
git config --get core.autocrlf; Get-Content .gitattributes -ErrorAction SilentlyContinue
$r3  = "experiments/sl-pt-001/SL-PT-001_Revision_R3_Consolidated_Candidate_Claude_2026-11-25.md"
$pkg = "experiments/sl-pt-001/SL-PT-001_First-Trade_Closure_Package_Claude_2026-11-25.md"
git ls-tree origin/main -- $r3 $pkg
git log origin/main --format="%H %cI %s" -- $r3
git log origin/main --format="%H %cI %s" -- $pkg
git hash-object $r3 $pkg
git log origin/main --oneline -8
```

| Check | Expected |
|---|---|
| R3 blob in `ls-tree` | `203b4bf5d0d5f2cba124a0ea693b796ecd38c7bd` |
| Closure package blob | `ce2a6feb22645675a64fa98bfe8cc94bea901466` (Claude's local value) |
| `git log -- $r3` | **exactly one** commit; any later commit means the review target changed |
| `hash-object` | equals the ls-tree blob; a difference means line-ending conversion in the working copy, which is reported but does not invalidate the blob |
| HEAD = origin/main; status empty | yes |

### 6.2 Stage A-0 probe (one file, one response; establishes nothing beyond it)

```powershell
$d = "experiments\sl-pt-001\probe-A0"; $inv = [Globalization.CultureInfo]::InvariantCulture; $sty = [Globalization.NumberStyles]::Float
foreach ($f in "bars_body.json","quote_body.json") { "$f sha256=" + (Get-FileHash "$d\$f" -Algorithm SHA256).Hash }
$raw = Get-Content "$d\bars_body.json" -Raw
$tt = [regex]::Matches($raw, '"t":\s*"([^"]+)"') | ForEach-Object { $_.Groups[1].Value }
$ts = $tt | ForEach-Object { [DateTimeOffset]::ParseExact($_, "yyyy-MM-dd'T'HH:mm:ss'Z'", $inv, [Globalization.DateTimeStyles]::AssumeUniversal).ToUnixTimeSeconds() }
"P1 bars=$($ts.Count) unique=$(@($ts | Sort-Object -Unique).Count) first=$($tt[0]) last=$($tt[-1])"
$na = 0; $gp = 0; for ($i = 1; $i -lt $ts.Count; $i++) { $x = $ts[$i] - $ts[$i-1]; if ($x -le 0) { $na++ }; if ($x -ne 300) { $gp++ } }
"P2 nonascending=$na non300steps=$gp offgrid=$(@($ts | Where-Object { $_ % 300 -ne 0 }).Count)"
$vt = [regex]::Matches($raw, '"v":\s*(-?[0-9][0-9.eE+-]*)') | ForEach-Object { $_.Groups[1].Value }
$z = @($vt | Where-Object { [decimal]::Parse($_, $sty, $inv) -eq 0 })
"P3 v_tokens=$($vt.Count) zero_volume_exact=$($z.Count) zero_forms=" + (($z | Sort-Object -Unique) -join ',')
$ct = [regex]::Matches($raw, '"c":\s*(-?[0-9][0-9.eE+-]*)') | ForEach-Object { $_.Groups[1].Value }
"P4 c_tokens=$($ct.Count) max_fraction_digits=" + (($ct | ForEach-Object { if ($_ -match '\.(\d+)') { $matches[1].Length } else { 0 } } | Measure-Object -Maximum).Maximum) + " exponent_tokens=" + @($ct + $vt | Where-Object { $_ -match '[eE]' }).Count
$q = Get-Content "$d\quote_body.json" -Raw; $qt = ([regex]::Match($q, '"t":\s*"([^"]+)"')).Groups[1].Value
"P5 quote_t=$qt last_bar_t=$($tt[-1])"
```

| Check | What it shows | Label of the result | Limit |
|---|---|---|---|
| P1 uniqueness, P2 ordering and 5-minute continuity | from the raw `t` text, with no JSON date conversion | COMPUTED, one response | says nothing about other windows |
| P3 zero volume | exact decimal parse of each `v` token; replaces 7/72 | COMPUTED | the `v` token count must equal the bar count, otherwise the extraction is wrong: stop and report |
| P4 decimal preservation | the token literals are intact in the artifact (fraction digits, exponents) | COMPUTED | it checks **the artifact**. Exactness in the harness is a Stage A test (U25), not this check |
| P5 forming bar | the gap between the quote time and the last bar's `t` | COMPUTED arithmetic | **its interpretation is founder-only: see annex S2** |
| Quote vs bar observations | ask/bid/size and closes as recorded | OBSERVED once | the price increment, fee and fill behaviour remain **UNVERIFIED** (R3 §13) |

**If you choose not to run it:** accept FC-D in writing as CONDITIONAL. Stage A's checks V3 to V8 re-establish these properties for every cycle.

---

## 7. First-trade critical path (deliverable 7)

No dates are given; every step waits on the one before.

| # | Stage | Required input | Party | Acceptance condition | Evidence artifact | Founder authorization | Can proceed now? | Most consequential blocker |
|---|---|---|---|---|---|---|---|---|
| 1 | R3 standalone reviews | R3, the package, R1, the amendment, Stage A Design, G-07 0.3 | GPT, Gemini (separately) | both delivered; neither has seen the other's | two review documents | no | **yes** | cross-exposure of the reviews (a repeat of the incident) |
| 2 | reconciliation and containment | both reviews; this incident record; annex S2 unsealed | Claude | every finding categorized (§2); minorities preserved | reconciliation matrix | no | after 1 | reviewer disagreement on a critical item |
| 3 | R4 and regression specification | §3, §4 and the reconciliation actions | Claude, then GPT closure check | every critical finding resolved, or listed for founder acceptance | R4, updated package and manifest | no | after 2 | new defects introduced by the corrections |
| 4 | founder decision closure | §5 options | Founder | FD-6 scope, FD-7, W, CF-7, CF-1 and CF-2 decided in writing | decision record | **yes** | **yes** (in parallel) | **FD-7** |
| 5 | freeze authorization | R4; decisions; ls-tree output; FC-D result or acceptance | Founder | dispatch §5 conditions met | freeze record with blob SHAs, committed | **yes** | after 3 and 4 | unresolved criticals |
| 6 | FD-5 harness authorization | the freeze record | Founder | written authorization | decision record | **yes** | after 5 | — |
| 7 | blind script and hash | the frozen set only | GPT; the founder commits the hash | hash committed before any TER exists | script hash commit | yes (FD-6) | after 6 | isolation breach |
| 8 | Stage A harness | the frozen set; FD-7 timer definition | harness author (not GPT) | keyless; read-only; source hashed | source revision and hash; task XML hash | covered by FD-5 | after 6 | scope creep beyond the frozen set |
| 9 | tests executed | harness; U1–U53, X1–X11, S2 tests; R1–R16 pass and fail | harness author; founder runs | observed results retained; failures reported | test records | no | after 8 | a test passing "by specification" rather than by execution |
| 10 | shadow milestone | runs with declared_slots ≥ 30 | Founder (timer) | run_length ≥ 30; ≥ 5 injections; blind reconstruction of 5 seeded cycles; slot audit clean | TERs, manifests, chain, audit output | no | after 9 | data failures breaking runs (UNBOUNDED) |
| 11 | Stage A exit decision | dispatch §7 items 1–10 | Claude drafts; Founder decides | exit report accepted | exit report | **yes** | after 10 | an unexplained reconstruction difference |
| 12 | Stage B design and authorization | FD-G13, G16, G17, G18; TIF; CF-1; CF-7 sequence; I5/I8 limitation text | team; Founder | package complete; FD-9 and FD-8 decided | Stage B package and decisions | **yes** | after 11 (design work can start earlier, but decisions wait) | **FD-G13** (authenticated approval) |
| 13 | G-07 minimum controls and pre-flight | Stage B build | team; Founder runs the pre-flight | controls locally tested; account 1×, no shorting, buying power; increments; fee | test evidence; pre-flight records | covered by FD-9 | after 12 | metadata contradicting the policy (P-1) |
| 14 | per-order founder approval | first-trade package (dispatch §9) | Founder | approval bound to every parameter within approval_deadline; no open, partial or ambiguous order | approval record | **yes, for this order** | after 13 | the approval window (W) versus review time |
| 15 | first paper order and independent reconciliation | the approved authorization | executor; Founder; independent reconstruction | L-1 to L-3 exact; lifecycle reconstructed | raw request and response; reconciliation; reconstruction report | no | after 14 | an AMBIGUOUS outcome |

---

## 8. Single most important current blocker (deliverable 8)

**FD-7.**
- The two reviews are the immediate gate, but they are already running and need no decision.
- FD-7 is the one open founder decision that the rest of the path cannot proceed without:
  - it sets the harness scope, which is fixed at the freeze;
  - it determines whether M1-1 is reachable;
  - it sets how late a proposal can be (W = 90 s assumes the timer).

---

## 9. Authorization boundaries (deliverable 9)

| Boundary | Status |
|---|---|
| R3 edit | **prohibited** until reconciliation |
| Specification freeze (R3 or R4) | **not authorized** |
| FD-5 Stage A harness build | **CONDITIONAL**: not met |
| Blind reconstruction script | **not authorized** (after the freeze, FD-6) |
| Stage A timer (FD-7) | **not decided** |
| Alpaca market data (keyless, read-only) | used once under FD-1; **no further fetch is authorized** |
| Alpaca paper credentials (FD-8) | **deferred** |
| Trading-host connection | **not authorized** |
| Stage B design work | permitted as documents only |
| Stage B implementation and authorization (FD-9) | **deferred** |
| Paper or live order | **not authorized**; the per-order approval mechanism does not exist |
| Frozen EAR baselines | untouched; **no change authorized** |
| G-07 | Draft 0.3 plus the scoped A0.3-13. **Not passed; not implemented** |
| First paper trade | **not authorized** |
