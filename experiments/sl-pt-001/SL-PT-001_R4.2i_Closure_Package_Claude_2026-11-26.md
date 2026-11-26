# SL-PT-001 | R4.2i Closure Package (G8-01, G8-02, G8-03, E-3)

**Date:** 2026-11-26 · **From:** Claude (Specification Lead / ARBITER) · **To:** Founder; GPT and Gemini B for one bounded closure round
**Authority:** none. **Nothing here is frozen.** R4.2c remains the frozen Stage A specification.
**Responds to:** R4.2h round. Gemini B: **FREEZE-READY** (noted the stale header identifier). GPT: **NOT FREEZE-READY**: G7-01 CLOSED, C-09 CLOSED, E-1 CLOSED; G7-02 NOT CLOSED pending G8-01 and G8-02; G8-03 low; E-2 acceptable if scoped; E-3 to be omitted or made normative.

**Scope:** R4.2i = R4.2h plus four corrections. The R4.2h → R4.2i diff is 79 lines (+10/−7).

## Disposition: all GPT findings accepted

| ID | Accepted? | Correction | Where |
|---|---|---|---|
| **G8-01** displayed sizes undefined | **Yes**, and wider than reported: the scheduled rows never defined it either | One rule for every TER. `{bs, as}`; each member is the token text when the key holds a JSON number token, and `null` otherwise. The whole object is `null` only when no quote is available (request never issued, NO_RESPONSE, or injected V12a FAIL). It is recorded whether or not Q is evaluated. The injected QUOTE_INVALID row points to that rule | §10.4 (new bullet; injected QUOTE_INVALID row) |
| **G8-02** U108 "seven paths" stale | **Yes** | U108 now covers one TER per terminal-path row, scheduled and injected, with both REJECTED and SHADOW_EXPIRED for a proposal, plus QUOTE_INVALID with one and with both sizes absent | §14 U108 |
| **G8-03** "R4.2g proposes to replace" | **Yes** (my edit miss; Gemini B saw it too) | now reads R4.2i | header (record) |
| **E-3** leap second | **Yes**: RFC 3339 does permit `:60`, so this cannot enter through an editorial note | made **normative**: a seconds field of 60 is malformed, stated as a Sentinel restriction rather than an RFC 3339 rule. New test U122 | §4.4; §14 U122 |

**E-2** stays a non-normative note, rescoped as GPT asks; see the freeze record below. **E-3 leaves the notes**, because it is now normative text.

**Why E-3 is made normative instead of omitted:** omitting it would leave leap-second handling unspecified. The harness and the independent auditor could then legitimately diverge on one input, and the outcome would be an unexplained M1-6 difference. One line removes that degree of freedom.

**Not changed:** every item closed so far (G7-01, C-09, E-1, and all earlier rounds), and every other line.

**Disclosure:** E-3 touches §4.4, one of the sections Strike 1a was built against while it was unchanged. Strike 1a's code already rejects `:60` and parses `23:59:59.999999999Z` exactly (COMPUTED). Its behaviour is unaffected.

## Proposed founder freeze record (draft; for use only after a clean round)

```
SL-PT-001 STAGE A SPECIFICATION FREEZE RECORD (AMENDED)
Status: FROZEN BY FOUNDER (Stage A scope only)
Frozen document: experiments/sl-pt-001/SL-PT-001_R4.2i_Stage_A_Amendment_Candidate_Claude_2026-11-26.md
  git blob 3549d2275ce3f5490f93802ff9eec1570f2fb48f
  SHA-256  4259551121fa3d271074fb13da51fb270ae859b0b516a953752731f20972a51a
Supersedes, for Stage A: R4.2c (blob 316d08c0..., freeze 030e7c0). Evidence produced under R4.2c stays tied to R4.2c.
Frozen scope: as R4.2i section 0.2 (Stage A sections and the Stage A rows of sections 14-16).
Review basis: R4.2d to R4.2i closure rounds (GPT, Gemini B), committed verbatim under experiments/sl-pt-001/reviews.
Editorial notes (non-normative; no change to frozen text):
  E-1 X8 and X10 "recorded" means recorded in the retained test output; BOUNDARY_VIOLATION_ATTEMPT is a test-output label, never a chain record type or TER value (cf. U9).
  E-2 Section 3.3 reading adopted for Stage A: a HOLD signal maps to HOLD. The "any signal + open/unresolved order or authorization" row is applied to BUY and EXIT signals. This is a founder-adopted reading consistent with the section 11.1 qualifying conditions; it is not derived from section 11.1 alone. In Stage A live operation no order or authorization is ever open (section 8.1; R16 vacuous), so the case arises only in unit tests.
Accepted residuals: those of the R4.2c freeze record, plus U-I3 (V12a and lock_clock_at HARNESS-ATTESTED), U-T5 (append completion and durability not timestamped; file order only), runtime injections limited to R1/R4/R5/R10/R12/R13 with other FAIL cases as unit tests (U121), header artifact client-reported (D-8), INSUFFICIENT_HISTORY unreachable as a first failure (C-09).
FD-5 synchronization: FD-5 (5252322) applies to R4.2i from this record. Unchanged: no credentials, no trading-host connection, no order, no Stage B.
Seed: the cleartext seed at 07f43e0 is superseded (section 11.5); a new seed hash is committed before the first audited run.
```

## Identifiers

| Artifact | SHA-256 | Git blob |
|---|---|---|
| Frozen R4.2c | `9d417fb5b22147eec6785816b239ad6b76215ea5f18e662432dc7e9cfb283d76` | `316d08c046dd7e1ea4a61be980c037b1c62037d5` |
| R4.2h (committed `b29410e`, superseded) | `ee4a8ceb40cbef5f31d30d08c94ef753b920fb68869e077af1876f43b80fc8ef` | `29e422a74bc50035f92594fc2251d672b4762786` |
| **R4.2i candidate** | `4259551121fa3d271074fb13da51fb270ae859b0b516a953752731f20972a51a` | `3549d2275ce3f5490f93802ff9eec1570f2fb48f` |
| **Diff R4.2h → R4.2i** (79 lines) | `424ff44a29d768f2d36453a2775ae165b04c50d71059134ffb1559d8c40bdc22` | `ae04c39db24854eb12f292bf758657f21e830c76` |
| Diff R4.2c → R4.2i (312 lines, complete) | `82389cb2cb90fa3daba8ab9c1149150cdec656ebeafa3db87059ee8126480088` | `3af5dc19e32538fe842fce2fae7ad1264d64c380` |

**Integrity (COMPUTED, Claude):** both diffs, applied with `git apply` to clean copies of R4.2c and R4.2h, reproduce R4.2i at `42595511…a51a`. Each of the 39 edits was asserted to match exactly once.

## Bounded round: what to send

Use **new chats**. Send each reviewer: frozen R4.2c, both R4.2i diffs, and **its own** R4.2h review. Do not send this package, the other reviewer's review, or anything from `harness/`.

```
Bounded closure review, SL-PT-001 R4.2i. Inputs: frozen R4.2c (SHA-256 9d417fb5b22147eec6785816b239ad6b76215ea5f18e662432dc7e9cfb283d76), diff R4.2h -> R4.2i and diff R4.2c -> R4.2i (git format; applying either must give R4.2i SHA-256 4259551121fa3d271074fb13da51fb270ae859b0b516a953752731f20972a51a), and your own R4.2h review.
Review ONLY the R4.2h -> R4.2i changes and any defect they introduce. Do not reopen closed items.
Targets: G8-01 (displayed sizes defined once for every TER: members null when absent or non-numeric; object null only when no quote is available; recorded whether or not Q is evaluated); G8-02 (U108 covers every scheduled and injected terminal-path row, both REJECTED and SHADOW_EXPIRED, and missing sizes); G8-03 (header identifier); E-3 (section 4.4 now normatively rejects a seconds field of 60 as a Sentinel restriction; U122).
Also confirm the rescoped non-normative note E-2: "A HOLD signal maps to HOLD; the any-signal open/unresolved row is applied to BUY and EXIT. A founder-adopted reading consistent with section 11.1, not derived from it alone; unreachable in Stage A live operation."
For each: CLOSED / NOT CLOSED with a concrete counterexample. Final verdict: FREEZE-READY or NOT FREEZE-READY.
No harness code, credentials, orders or TER output exist or may be requested.
```
