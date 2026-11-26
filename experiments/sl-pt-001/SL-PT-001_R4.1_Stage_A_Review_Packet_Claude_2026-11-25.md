# SL-PT-001 R4.1 Stage A Review Packet

**Author:** Claude. **Date:** 2026-11-25.
**Responds to:** the founder dispatch "R4.1 CLOSURE STRIKE".
**Status:** specification correction and review preparation only. **NOT FROZEN.** No harness, no test executed, no credential, no order.

---

## 0. Verification (who verified what)

| Item | Value | Verified by |
|---|---|---|
| R4 blob | `38b1de639a7ecea842269f8f48a2638363cb4871` | Claude: local `git hash-object` equals the founder's `ls-tree` output |
| R4 review packet blob | `ee277bc8a9347904fcac5cf2ea29028143502554` | same |
| Decision record v1 blob | `eb76d8a21521ad02e2c5530bf3bc30cafe583169` | Claude reproduced it byte-exactly from the founder's `Get-Content` output (LF line breaks, CRLF ending) |
| **Decision record v2 blob** | `801f7a57f5a87220a44f0bbc3e262e2704fdf77b` | Claude reproduced it byte-exactly from the committed text (same line-ending pattern), so **v2's content is exactly the text R4.1 synchronizes to** |
| v2 commit | `b856ff2031bbbafd325a75059db0c841a851514d` | **reported by the founder; not seen by Claude** |
| Current HEAD | — | **not verified.** The repository cannot be inspected from Claude's environment, and no HEAD output since `f3ba4734` has been supplied |
| **R4.1** | SHA-256 `012fdcfffdc223399aeba4d5255adb7877ed7b3b4a48eb04334da4fba0256660`; git blob (local) `a653252a8b184f0e184c7f2b42b4dbba6ff49d3f` | Claude, local file. **Not committed.** |

---

## 1. D2: decision synchronization matrix (v2 → R4.1)

| v2 decision | R4.1 section | Synchronized text |
|---|---|---|
| MISSION endpoint | §0.1 | one governed BUY: at least one confirmed fill; terminal status; L-1 to L-3; independent reconstruction; remaining BTC exposure recorded; not a round trip; EXIT outside |
| FD-5 clarified (two freezes) | §0.2; §1.1 FD-5 row | the Stage A freeze covers exactly the v2 list; Stage B findings go to a Stage B freeze, which is a precondition of FD-9 with the Stage A exit; a Stage B change touching Stage A requires a new Stage A freeze; evidence stays tied to its hash |
| RC-25a R8 $300 | §1.1, §7.3 | accepted |
| RC-25b R12 $450 buy gate | §1.1, §7.3 (rule plus notes) | relabelled "buy gate, not a loss limit"; can block the first BUY if reconciled cash is below $450; the loss bound is R7 |
| RC-25c settle 60 s | §1.1, §4.6 | accepted |
| RC-25d shadow cash $500 | §1.1, §8.1 | accepted |
| R4-9 Branch C | §1.1, §2.3, §6.4, §13, §14 U92, §15 U-I1 | Branch C selected; the limitation statement is verbatim and required in every Stage A result; Branch H is retained only as "not selected"; U92 not applicable |
| R4-11 2 s bound | §1.1, §5.6, §6.4 (V12), §14 U79 | accepted; otherwise BOUNDARY_FAIL |
| OI-13 wrapper | §1.1, §6.1 | the wrapper is the "log" part of invoke-and-log; no other logic |
| OI-09 coverage | §1.1, §16 OI-09, §17 | to be closed by Gemini B's review of §2, §13 and the claim limits |
| v1 decisions (FD-2, FD-3, FD-4, CF-1, CF-2, FD-6 with dissent, FD-7, W, CF-7) | §1.1, unchanged from R4 | no change |

---

## 2. D3: change log (R4 → R4.1)

| # | Location | Change | Basis |
|---|---|---|---|
| C-1 | title, header | renamed R4.1; base blob and decision-record blobs recorded; "R4.1 replaces R4" | dispatch §3 |
| C-2 | **new §0** | §0.1 mission endpoint; §0.2 freeze map with the rules | v2 MISSION, FD-5 |
| C-3 | §1 sources | "commit unverified" replaced by blob-verified v1 and v2 | OI-01 closed |
| C-4 | §1.1 | rows added: FD-5 clarified; MISSION; RC-25a to d; R4-9; R4-11; OI-13; OI-09 | v2 |
| C-5 | §1.2 | pending table reduced to Stage B items only; "no Stage A founder decision is pending" | v2 |
| C-6 | §2.3 | Branch C selected; Branch H marked NOT SELECTED; limitation verbatim; why it's acceptable (no credentials) | v2 R4-9 |
| C-7 | §4.6 | settle accepted | v2 RC-25c |
| C-8 | §5.6 | the 2 s bound accepted. **Narrowing added:** the bound is relative to the data host's `Date` header, so timing claims are CONDITIONAL on that header's accuracy (U-T2) | v2 R4-11; consistency |
| C-9 | §6.1 | wrapper status per OI-13; Branch C note | v2 OI-13, R4-9 |
| C-10 | §6.4 step 1 | V12: the Branch H firewall check is removed; the offset bound is applied | v2 R4-9, R4-11 |
| C-11 | §7.3 | R8 and R12 accepted; R12 relabelled; **notes on R7, R8 and R12 added**: buy gate; first-BUY blocking condition; R8 cannot bind on the first BUY; loss bound is R7; worst-case equity $350 | v2 RC-25 |
| C-12 | §8.1 | opening cash accepted | v2 RC-25d |
| C-13 | §8.2 to §8.6, §9, §12 headings | labelled **STAGE B DRAFT: not in the Stage A freeze**; §8.3 also labelled outside the milestone | v2 FD-5, MISSION |
| C-14 | §10.4 | the TER isolation marker is now always "C" | v2 R4-9 |
| C-15 | §11.6 | **pre-live test gate narrowed** to the rules applicable in Stage A (R1, R3 to R13, R15, R16) and to tests whose Stage column contains "A". R2 and R14 move to the Stage B gate | **consistency correction:** R2 and R14 cannot be exercised in Stage A. Flagged for review |
| C-16 | §13 | the claims exclusion now names process-level and host-level isolation, and requires the limitation statement | v2 R4-9 |
| C-17 | §14 | freeze-scope note; U79 made concrete at ±1 ns; U92 not applicable | v2 R4-9, R4-11 |
| C-18 | §15 | Scope column (A/B); U-T2 restated; U-I1 "not established"; U-O3 marked B and "not a gate"; dashboard cash noted as OBSERVED by screenshot only | v2 |
| C-19 | §16 | split into closed (OI-01 to OI-07, OI-13) and open. **New items:** OI-15 (who reconstructs the BUY lifecycle; FD-6 covers Stage A only), OI-16 (the R4.1 review itself) and OI-17 (Stage B findings unreviewed) | v2; consistency |
| C-20 | §17 | coverage-by-area table for the R3 and R4.1 rounds | v2 OI-09 |

**No Stage A rule, state, threshold or test semantics changed other than C-8, C-10, C-11 (notes only), C-15 and C-17,** each traced above.

---

## 3. D4: Stage A review packet

### 3.1 What reviewers receive

- **R4.1**, SHA-256 `012fdcff…6660`. Gemini B receives the Stage A sections as six text chunks (`R41_chunk1of6` to `R41_chunk6of6`). §8.2 to §8.6, §9 and §12 are omitted from the chunks and marked as Stage B draft.
- **Decision record v2**, blob `801f7a57…`. Its text is summarized in R4.1 §1.1; reviewers may be given the full text.
- **This packet's §2** (change log) and **§3.3** (open issues).
- **Nothing else.** Gemini B must not receive GPT's reviews, the reconciliation, R4, this packet's §4 or any Claude finding.

### 3.2 Review scope

§2 to §7, §8.1, §10, §11, §13, the §14 tests whose Stage column contains "A", and the A rows of §15 and §16.

**Out of scope:** Stage B draft sections, unless a Stage A section depends on them. If it does, that dependency is itself a finding.

### 3.3 Open Stage A issues reviewers should test

| ID | Issue |
|---|---|
| OI-08 | Stage A never exercises the long-position branches, R8 or R12 on live data. Is the test- and injection-only coverage adequate? |
| C-8 | the 2 s bound is relative to an unverified `Date` header. Is "CONDITIONAL" the right status for Stage A timing claims? |
| C-15 | is narrowing the pre-live gate correct and complete? |
| §6.3 | the lock and takeover protocol: Windows file-lock exclusivity is UNVERIFIED; the termination request is not enforced |
| §10, §11 | completeness depends on the founder pushing the chain. An unpushed chain cannot be audited |
| §4.9 | "confirmed" means two identical fetches, not finality. Is the anti-lockout argument sound? |

### 3.4 Claim limits reviewers must challenge

1. **Branch C:** "Disconnection from trading is asserted at the HTTP-client level only…" Does any R4.1 text imply more?
2. **No Stage A result establishes any G-07 property** (§2.2, §13).
3. **M1 claims** (§13): is each one supportable from the artifacts the audit actually recomputes (§11)?
4. **Probe claims** (§4.13): the labelling convention and the forming candle are **not** established.
5. **R12** is a buy gate, not a loss limit. The loss bound is R7.
6. **Timing claims** are CONDITIONAL on the data host's clock (§5.6).

### 3.5 Review requests (paste-ready)

**Gemini account B.** Use a new chat. Paste chunks 1 to 6 in order, waiting for each "Received chunk n of 6", then send:
```
Independent technical review of the attached SL-PT-001 R4.1 Stage A specification text (simulated-money paper-trading research; nothing executed). Start with: "Prior exposure: I have seen SL-PT-001 R3 only; no reconciliation, no R4, no other reviewer's review."
Scope: R4.1 sections 2-7, 8.1, 10, 11, 13, Stage A tests in 14, Stage A rows in 15-16. Pay particular attention to section 2 (stage boundary, client-level isolation) and section 13 (claims): does any text claim more than the evidence supports?
Then examine, as implemented literally: (1) the lock, manifest, global chain, invocation log and auditor as one system (sections 6, 10, 11): can a slot be lost, double-counted, forged or omitted without detection? (2) revision handling (4.9): can a changed bar escape detection or cause lockout? (3) timing (5.3-5.6): can any window cross the next slot? (4) shadow ledger (8.1); (5) whether each Stage A test in 14 can falsify its property.
Output: verdict (FREEZE-READY / CONDITIONALLY FREEZE-READY / NOT FREEZE-READY for the Stage A scope); findings with IDs B2-01, B2-02, ..., each with section, exact mechanism, consequence, smallest correction and severity; test gaps; residual UNVERIFIED/UNBOUNDED items; the single most important Stage A blocker. Do not promote anything to a founder decision. Do not reference any other review.
```

**GPT.** Use a new chat. Give it the full R4.1 file, decision record v2 and this packet's §2 and §3. Send:
```
Hostile consistency review of SL-PT-001 R4.1 (SHA-256 012fdcff...6660), Stage A scope only: sections 2-7, 8.1, 10, 11, 13, Stage A tests in 14, Stage A rows of 15-16. Begin with your exposure statement (you have seen SF-1..3, S2, the R3 reconciliation and R4).
Attack specifically: (1) the lock, manifest, chain, invocation log and auditor as ONE system: concurrency, takeover, omission, forgery, OFF_RUN and CONCURRENT_INVOCATION handling; (2) revision confirmation and anti-lockout (4.9); (3) timing and slot-boundary invariants (5.3-5.6, 6.2-6.3), including the 2 s bound relative to the Date header; (4) shadow-ledger behaviour (8.1) and its effect on what Stage A can claim; (5) whether every Stage A claim (2, 13, 11.6) is supported by evidence the auditor actually recomputes; (6) the change log's C-8, C-15 and C-17.
Output: verdict for the Stage A scope; findings G2-nn with section, mechanism, consequence, smallest correction and severity; the status of each Stage A item from your R3 review (G-02 to G-07); missing Stage A tests; the single blocker. Stage B draft sections are out of scope unless a Stage A section depends on them.
```

**Sequence:** do not forward GPT's findings to Gemini B before Gemini B has delivered. Then send both reviews to Claude for reconciliation.

---

## 4. D5: remaining blockers

**Blocking the Stage A freeze:**

| ID | Item | Closes when |
|---|---|---|
| OI-16 | the R4.1 Stage A review (Gemini B and GPT), its reconciliation and a GPT closure check | every Stage A critical is resolved or accepted by the founder in writing |
| OI-09 | the clean review of §2, §13 and the claim limits | Gemini B delivers (part of OI-16) |
| — | committing R4.1 and recording the Stage A freeze | the founder commits after OI-16 |

**Stage A, after the freeze:** OI-14 (FD-5), and OI-08 accepted at the Stage A exit.

**Stage B freeze (before the first order; not now):** OI-10 (TIF), OI-11 (FD-G13, FD-G16, FD-G17, FD-G18), OI-12 (FD-8), OI-15 (the BUY-lifecycle reconstructor) and OI-17 (G-01 and the other Stage B findings).

**After the milestone:** the EXIT path; corrections and busts beyond halt-and-stop; the duplicate-order-ID test; Stage C.

---

## 5. D6: recommendation

**READY FOR INDEPENDENT STAGE A HOSTILE REVIEW**

**Why:**
- Every v2 decision is synchronized (§1), with no Stage A founder decision left pending.
- Every change from R4 is logged and traced (§2).
- The Stage A scope is marked in the document itself (§0.2), and the Stage B sections are labelled as draft, not removed.
- The only Stage A blockers left are the review itself (OI-16 and OI-09). Those cannot close without this step.

**Conditions:**
1. **Commit R4.1 first.** Reviewers then target a blob, not a local file. If you push it, confirm with `ls-tree` that the R4.1 blob is `a653252a8b184f0e184c7f2b42b4dbba6ff49d3f`.
2. **Two consistency corrections need reviewers' attention:** C-8 (timing claims conditional on the `Date` header) and C-15 (the narrowed test gate). Neither is a founder decision, and both are flagged rather than buried.

**What this recommendation does not say:** that R4.1 is correct, that it is freeze-ready, or that anything should be built.
