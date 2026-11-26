# SL-PT-001 Stage A-0 Data Probe Report

**Date:** 2026-11-25 (probe at about 2026-11-26T03:13Z) | **Author:** Claude (analysis of the founder's console output) | **Authorization:** FD-1 (founder)
**What ran:** two keyless, read-only HTTPS GETs to `data.alpaca.markets`, run by the founder from his machine with `curl.exe`. **No credentials, no trading host, no code.**
**Labels:** OBSERVED = seen in the founder's console output from this probe; COMPUTED = arithmetic on that output; UNVERIFIED = not established. **One probe; nothing is generalized beyond it.**

## Artifacts (`experiments/sl-pt-001/probe-A0/`; SHA-256 as reported by the founder)

| File | SHA-256 |
|---|---|
| bars_body.json | `E3640E5C904B2442913F0511046E9BCF536E4F1B685D73CAF6586CBC0736BADF` |
| bars_headers.txt | `5A6A76FB67CA4B5D1B57A0D7AD7947F24B8E455ED87275187590F87F1396D30E` |
| quote_body.json | `D9C34B0D4CD6D210C13F2C2204BDEF03007C33B1E27A3AD47BAEB80953103B5C` |
| quote_headers.txt | `741DFAD8A2C72A2DC8DC807D71EB7DA82D95C42F3DE08DFA51EAFB018F094A4D` |
| probe_meta.txt | `40CA026FD4B767F832E1895BD57505359909A4485C6DF868BFDEAB46A116450E` |

**Requests:**
- bars: `/v1beta3/crypto/us/bars?symbols=BTC%2FUSD&timeframe=5Min&start=<probe−6h>&limit=1000`;
- quote: `/v1beta3/crypto/us/latest/quotes?symbols=BTC%2FUSD`.

## Results against the data contract (Stage A design D2; amendment v0.2)

| Item | Finding | Label |
|---|---|---|
| Keyless access | HTTP 200 on both requests | **OBSERVED** |
| Timestamp convention | bar `t` values at exact 5-minute boundaries, RFC-3339 in UTC to the second (`2026-11-25T21:15:00Z` …) | **OBSERVED** (consistent with the documented start-labelling) |
| Coverage | 72 bars, first `21:15:00Z`, last `03:10:00Z`; (03:10 − 21:15) / 5 min + 1 = 72 | **COMPUTED**: no gap or duplicate *if* the timestamps are unique and ordered. **The per-bar check is pending on the full file** |
| Pagination | `next_page_token: null` | **OBSERVED** |
| In-progress bar | the last bar (`03:10Z`) started about 3 minutes before the quote timestamp (`03:13:20Z`), so it was **incomplete** when returned | **OBSERVED**: the API returns the forming bar. The completed-candle rule (amendment v0.2: latest = floor_5min(T_d − 60 s) − 5 min) is **required**; here the latest usable bar = `03:05Z` (COMPUTED) |
| Price literal format | closes with up to 4 decimals (`60161.85`, `60208.035`, `60274.125`, `60275.3015`, `60248.18`) | **OBSERVED**: exact decimal parsing is required. The values look like averages or midpoints (not trade prints); **their derivation is UNVERIFIED** |
| Quote-derived bars | 7 of 72 bars match `"v":0` | **OBSERVED** (a regex on raw text; a bar whose volume is encoded as `0.0` would not match, so this may undercount) |
| Quote | ask 60663.76 (size 0.0009933), bid 60644.2 (size 0.00099479), t `03:13:20.445036299Z` | **OBSERVED**. The spread is 19.56, about 0.032% of mid (COMPUTED) |
| History sufficiency | 71 completed bars ≥ 51 required | **COMPUTED** |

## Findings that change later stages

| ID | Finding | Effect |
|---|---|---|
| P-1 | **The quote prices have cents**, while Alpaca's support table documents a BTC/USD price increment of **1**. These are inconsistent | the limit-price increment is **UNVERIFIED**. The Stage B pre-flight must read the asset metadata and refuse on mismatch (amendment A-5). Policy must not hard-code $1 |
| P-2 | **Top-of-book size is about 0.00099 BTC (≈ $60 at this price) on each side**, below the planned order size of about $145 | a BUY limited at the ask may only partly fill against displayed size, or need to walk the book. Paper-fill behaviour relative to displayed size is **UNVERIFIED**. This is recorded for FD-4 (price rule) and Stage B; it does not block Stage A |
| P-3 | the API returns the forming bar | confirms the completed-candle rule. **Add test U17:** a fixture with the forming bar included must exclude it |

## Not established by this probe

- the revision of historical bars (needs a re-fetch);
- gap behaviour over other windows or times of day;
- the API's behaviour under load or error;
- whether results repeat on a second request;
- paper order behaviour of any kind.

**No SMA, signal or decision was computed from this data** (Stage A is not built; independent reconstruction does not exist yet).

## Status change (First-Trade Readiness D1)

- 1.1 probe: **COMPLETE**.
- 1.2 keyless access: **OBSERVED (one probe)**.
- 1.3 timestamp, precision and pagination: **OBSERVED (one probe)**; revision still UNVERIFIED.
- **Stage A is no longer at risk of being blocked by credentials.**
- Remaining gates before the build: FD-2, FD-3, FD-4, FD-6, then FD-5.

*End of probe report.*
