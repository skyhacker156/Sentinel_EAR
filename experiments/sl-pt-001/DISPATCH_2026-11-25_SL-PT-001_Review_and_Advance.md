# A-TEAM DISPATCH: SL-PT-001 REVIEW AND ADVANCE (5-minute strategy)

**From:** Founder | **To:** GPT (hostile review), Gemini (independent challenge), Claude (reconciliation) | **Date:** 2026-11-25
**Classification:** review plus **bounded authorizations as marked in §3**. No paper or live order is authorized by this dispatch.

## 1. Decisions recorded

- **Strategy timeframe: 5-minute candles.** SMA-20/50 v0.2 (amendment `SL-PT-001_Amendment_SMA20-50_v0.2_5Min`). This replaces hourly v0.1 as the strategy under test. It is a different strategy, not a faster v0.1.
- **Shadow milestone:** ≥ 30 consecutive non-injected cycles (≈ 2.5 h), ≥ 5 injected proposals, independent reconstruction of ≥ 5 random cycles. **No calendar minimum.** The short-run limitation is accepted and recorded.
- Venue remains Alpaca paper; BTC/USD only; limit orders only; no leverage, shorting or derivatives.

## 2. Review assignment (documents in the repo: experiments/sl-pt-001/ and ear/g07/)

Review together:
- Stage A Design v0.1;
- First-Trade Readiness D1 to D8;
- Amendment v0.2 (5Min);
- G-07 Draft 0.3.

**GPT (hostile review):**
1. Does 5Min break any assumption carried over from the hourly design? Look at the settle margin (60 s), TTL (180 s), quote freshness (15 s), cycle overrun, and the approval window.
2. Missing dependencies or premature readiness claims in D1 (the dependency map) and D7 (the runbook).
3. Authorization bypasses: any path from signal to order that skips the founder approval, single-use consumption, LP-PRESEND, or reconciliation.
4. Whether the reduced milestone still supports the claims made for it, and nothing more.

**Gemini (independent challenge):**
1. Ways a false, stale or quote-derived signal could be accepted as a valid BUY.
2. Edge cases in 5-minute candle handling (late bars, revisions, gaps, clock drift, cycle overrun).
3. Whether the Stage A-0 probe as specified can mislead (one fetch generalized to all fetches).
4. Adversarial proposals that the test plan does not yet cover.

**Claude:** reconcile both reviews, preserve the disagreements, and issue revised candidates. **Do not resolve founder decisions.**

**All reviewers:**
- separate defects from open questions;
- label every claim;
- do not report anything as tested unless it was executed.

## 3. Bounded authorizations

**Delete any line that is not granted.**

- [ ] **FD-1, Stage A-0 data probe: AUTHORIZED.**
  - One manual, keyless, read-only request each:
    - BTC/USD 5Min bars (≥ 60 candles) from `data.alpaca.markets`;
    - the latest BTC/USD quote.
  - Raw bytes saved and SHA-256 recorded; results reported to the team.
  - **No credentials, no trading host, no code beyond the requests.**
  - If a key is required, **stop and report**. Do not create one.
- [ ] **FD-5, Stage A harness build: AUTHORIZED after FD-1 succeeds and the reviews in §2 are reconciled.**
  - Scope: Stage A Design D4 components C1 to C7.
  - Market-data host only.
  - No credentials; no order endpoint reachable.
  - The unit and adversarial tests must be **executed**, with evidence kept.
  - C8 (reconstruction) is written by the reviewer named in FD-6, **not** the harness author.

**Not authorized:**
- paper keys or any credential;
- connection to any trading host;
- paper or live orders;
- G-07 implementation beyond the Stage A boundary self-check;
- changes to frozen EAR baselines.

## 4. Founder decisions still open (answer when ready; defaults in brackets)

| ID | Decision | Default |
|---|---|---|
| FD-2 | crossover semantics at equality | [literal, as approved] |
| FD-3 | BUY while long; any signal while an order is open or unresolved | [no proposal; recorded as NO_ACTION / BLOCKED_OPEN_ORDER] |
| FD-4 | price and size | [BUY at the ask, EXIT at the bid; size ≤ $150 after the 0.25% taker fee] |
| FD-6 | the independent reconstructor | [GPT writes the reconstruction script from the spec alone; the founder runs it] |
| FD-9 | Stage B (paper orders), including FD-G13, FD-G16 and FD-G17 | [decided after the Stage A milestone] |

## 5. Path to the first trade (for orientation; each step needs its own gate)

1. Probe (FD-1).
2. Reviews reconciled; FD-2, FD-3, FD-4, FD-6 answered.
3. Harness built; tests executed (FD-5).
4. Shadow milestone, about 2.5 h.
5. Stage B authorization (FD-9); paper venue checks and Stage C tests.
6. A genuine 5-minute BUY signal, with founder approval within 180 s.
7. One submission; reconciliation; independent reconstruction.

**A valid HOLD is preferable to an invalid BUY. An unexplained discrepancy is a stop condition.**

*Founder retains final authority.*
