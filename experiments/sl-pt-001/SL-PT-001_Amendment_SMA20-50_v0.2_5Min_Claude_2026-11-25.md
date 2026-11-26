# SL-PT-001 Amendment: SMA-20/50 v0.2 (5-minute candles) and the reduced Stage A milestone

**Date:** 2026-11-25 | **Author:** Claude | **Founder decision:** 5-minute candles (2026-11-25, 22:08 ET); a shorter shadow run.
**Amends:** Stage A Design v0.1 (`3444db48…`) and First-Trade Readiness D1 to D8 (`e45c82a2…`). Neither is overwritten. Every change is listed here.
**Classification:** specification amendment. Nothing is implemented, fetched, tested or traded.
**Labels:** DERIVED / DOCUMENTED / ASSUMED / UNVERIFIED. Nothing is COMPUTED or OBSERVED.

## 1. Strategy: SMA-20/50 v0.2

**Unchanged from v0.1 (Stage A design D1):**
- the exact-sum comparison (5·S20 vs 2·S50);
- the crossover rule (literal, pending FD-2);
- the failure states (data failure ≠ HOLD);
- no interpolation;
- the signal-to-proposal mapping (EXIT only while holding; FD-3 for the rest);
- limit orders only;
- no leverage or shorting.

**Changed:**

| Parameter | v0.1 | **v0.2** | Reason |
|---|---|---|---|
| Candle timeframe | 1Hour | **5Min** | founder decision |
| Indicator windows | 20 / 50 candles (= 20 h / 50 h) | 20 / 50 candles (= **100 min / 250 min**) | the same counts on the shorter candle. **v0.2 is a different strategy, not a faster v0.1** |
| History required | 51 candles | 51 candles (255 min); the fetch window is ≥ 60 candles (300 min) | — |
| Settle margin | 5 min | **60 s** | DOCUMENTED: late trades cause an updated bar about 30 s after the close (minute bars, stream). 60 s gives 2× margin. **Revision of historical 5Min bars remains UNVERIFIED** |
| Decision time T_d | HH:05 | **every 5 minutes at :MM:00 + 60 s** (MM ∈ {00, 05, …, 55}) | — |
| Latest completed candle | floor_hour(T_d − settle) − 1h | **floor_5min(T_d − settle) − 5 min** | — |
| Quote freshness (R4) | 60 s | **15 s** | 60 s is a fifth of a candle; too stale for limit pricing |
| Authorization TTL (R13) | 5 min | **180 s** | must expire before the next decision (T_d + 300 s) with margin |
| Founder approval window (first order, runbook D7 step 5) | within the TTL | **within 180 s of issuance**, otherwise EXPIRED and the next signal is awaited | the human-in-the-loop limit |
| Re-check at consume (R14) | fresh snapshot | fresh quote, ≤ 15 s old | — |
| Shadow-outcome window (Spec v0.1 §6 step 6) | the TTL | the TTL (180 s) | — |

**Known costs of v0.2 (recorded; not mitigated):**
- **Quote-derived bars** (volume 0, with prices from quotes; DOCUMENTED source behaviour) will be more frequent on 5-minute bars than on hourly bars. The TER flags each one. More of the signal then reflects quote levels rather than trades.
- **Crossovers will be more frequent and noisier.** Round-trip taker fees are 0.50% (DOCUMENTED tier 1), so Scoreboard A is expected to deteriorate. **This is irrelevant to the governance milestone and must not be presented as strategy evidence.**
- **The approval window is 180 s.** A missed approval expires the order by design; it is not a failure.

## 2. Stage A milestone M1 (replaces Spec v0.1 §9 M1-1 only)

| Criterion | v0.1 | **v0.2** |
|---|---|---|
| M1-1 duration and volume | ≥ 7 days; ≥ 30 non-injected cycles; ≥ 5 injected | **≥ 30 consecutive non-injected cycles (≈ 2.5 h at 5Min); ≥ 5 injected; no calendar minimum** |
| M1-2 to M1-7 | completeness, integrity, look-ahead, governance, independent reconstruction of ≥ 5 random trades, honesty | **unchanged** |

**Limitation recorded with the reduced milestone (DERIVED):**
- a 2.5-hour run will not observe multi-day conditions: data-source outages, weekend liquidity, history revisions over days, clock or DST issues;
- M1 under v0.2 therefore shows **short-run** reproducibility and governance only;
- the re-fetch revision check (Stage A design §2.7) runs from cycle 2 and is reported, but a clean result over 2.5 hours **does not establish** that 5Min bars are never revised.

## 3. Test-plan changes (Stage A design D6)

| Test | Change |
|---|---|
| U5 (incomplete candle) | T_d = 10:05:30, bars up to start 10:05 and 10:00. The 10:00 bar is completed iff 10:00 + 5 min + 60 s ≤ 10:05:30, which is false. So the latest completed bar is **09:55**; expected latest = floor_5min(10:04:30) − 5 min = **09:55** → VALID; the 10:00 and 10:05 bars are excluded |
| U8 (stale) | (a) the latest completed bar is 10 minutes older than expected → STALE_SERIES; (b) the quote is 16 s old → proposal REJECTED R4 |
| U6, U11 | windows in 5-minute steps; 51 candles = 255 min |
| new U15 | **cadence drift:** a cycle started late (T_d = :MM:00 + 200 s) still selects the correct latest candle, and a cycle that would overlap the next one is skipped and recorded (CYCLE_OVERRUN), never run twice |
| new U16 | **TTL vs cadence:** an authorization issued at T_d expires before T_d + 300 s, and no two authorizations for the instrument are ever live together (R16) |

## 4. Changes to First-Trade Readiness D1 to D8

| Item | Change |
|---|---|
| D1 2.3 | the milestone is per §2 above (≈ 2.5 h, not ≥ 7 days) |
| D1 5.2 | waiting for a genuine BUY is still **not schedulable**, but expected to be much shorter at 5Min (UNVERIFIED; it depends on the market) |
| D2 | the timeframe decision is **closed** (5Min). The shadow-run minimum is set at 30 cycles **by default**; the founder may change it |
| D7 step 5 | approval within 180 s |
| D8 | unchanged: the Stage A-0 probe is still the first action; it now fetches **5Min** bars (≥ 60 candles) plus the latest quote |

*End of amendment.*
