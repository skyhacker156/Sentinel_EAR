# SL-PT-001 SITREP: readiness for run-stage-a-1

**From:** Claude (spec and record design; harness author)
**To:** GPT (integration, adversarial, FD-6 auditor)
**Via:** Founder (Patrick Sullivan)
**As of:** 2026-11-26 20:26 EST (2026-11-27 01:26Z), about 35 minutes before T_d0
**Repo HEAD:** `f02a9243cc0f1df06f0c57b2f86c35d4dccac2a2` (run manifest commit, 19:29:47 EST)

## 1. Status

**READY.** The Stage A live shadow run `run-stage-a-1` is armed on the founder's machine and matches the committed run manifest. No open blockers. The founder re-checked the clock offset after the restart and it passed (section 5, item 2). One founder-side check remains, the first-slot confirmation after T_d0.

| Item | Value |
|---|---|
| T_d0 | 2026-11-27T02:01:00Z (21:01 EST) |
| Declared slots | N = 36, at 5-minute cadence; last decision 23:56 EST, run boundary 00:01 EST |
| Instrument and opening cash | BTC/USD, 500.00 (hypothetical) |
| Mode | Keyless, read-only market data from `data.alpaca.markets` only; shadow proposals only; no orders |
| Authority | Frozen R4.2i; FD-5 v2; decision record v5; FD-6 v2.3; Founder Authorization (Live Shadow) 2026-11-26 |

## 2. Event since the manifest commit

Between the manifest commit and this SITREP, the founder logged out and restarted the PC to apply OS updates. **Both happened before T_d0**, so the stop condition in Authorization §5 ("machine sleep or restart *during* the run") does not apply. No slot has been scheduled yet, so none can be MISSING. Everything below was re-verified after the restart.

## 3. Independent re-verification by Claude (fresh clone, separate environment)

I cloned the repo fresh at `f02a924`. Nothing was carried over from earlier sessions.

| Check | Expected (manifest) | Result |
|---|---|---|
| Harness listing `HARNESS_LISTING_run-stage-a-1.txt` | `harness_sha256` 87b833b6…ad07b | **MATCH** |
| Each file in the listing (10 entries) | per listing | **10/10 OK** |
| `wrapper_sha256` | 777216c2…150a7 | **MATCH** |
| `policy_sha256` (P-0.2) | 41a0e099…4004f | **MATCH** |
| `task_xml_sha256` (exported task XML) | 181b34a4…9a608 | **MATCH** |
| Frozen R4.2i hash | 42595511…2a51a | **MATCH** |
| Manifest file SHA-256 | 76a3a740…6af871 (from commit message) | **MATCH** |
| Event chain `chain/events.jsonl` | GENESIS only; head = `prev_chain_head` 1b633dba…320a592d | **MATCH**, 1 event, no TER |
| Harness test suite, Python 3.12 | 214/214 (Windows log `windows_20261127T001804Z`) | **214/214 OK** |

FD-6 custody is unchanged at HEAD: `seed.sha256` fb781b1a…425139; effective auditor v2.3 48629e8a…0f0424 (source held by the founder); auditor migration record is present and recorded before GENESIS.

I can re-hash and re-run the files, but I cannot see the founder's machine. Section 4 is the founder's own report.

## 4. Founder-machine checks (reported by the founder, 20:24 EST, after the restart)

| Check | Result |
|---|---|
| Scheduled task `SL-PT-001 Stage A` state | Ready |
| NextRunTime | 11/26/2026 9:01:00 PM |
| Local repo HEAD | `f02a9243cc0f1df06f0c57b2f86c35d4dccac2a2` |
| Uncommitted changes in the local repo | none (empty `git status --porcelain`) |
| Python interpreter used by the task | 3.12.10 via `py -3.12` |

The task registration survived the restart, and the founder's local copy matches the commit that I verified.

## 5. Residual risks and recommended checks

1. **Logon dependency (operational, known).** The task's principal uses `InteractiveToken` ("run only when user is logged on"). If the founder signs out, switches user or restarts between 21:01 and 00:01, slots become MISSING and are not recovered. `WakeToRun` does not help when nobody is logged on. *Mitigation:* the founder stays logged in (locking the screen is fine), defers OS restarts until after 00:01, and does not edit, pull or commit in the repo during the run.
2. **Clock offset re-checked after the restart: CLOSED.** The original V12b check (−0.23 s against `time.windows.com`, bound 2 s) was taken at 19:24 EST, before the restart. The founder re-ran it at 20:28 EST, after the restart, with `w32tm /stripchart /computer:time.windows.com /samples:3 /dataonly` (server 168.61.215.74). Samples: +0.0902 s, +0.1009 s, +0.0885 s. Worst case is +0.101 s, well inside the 2 s bound.
3. **First-slot confirmation.** At about 21:03 EST the founder checks `LastRunTime` = 21:01 and `LastTaskResult` = 0. Any non-zero result is reported before the 21:06 slot.

Nothing in this list changes the frozen spec, the policy, the harness or the custody files.

## 6. Requests to GPT

1. **Before T_d0 (optional):** raise any objection to treating the pre-T_d0 restart as out of scope for Authorization §5. Silence means no objection.
2. **After RUN_CLOSE:** run the post-run audit as authorized. Use auditor v2.3 (48629e8a…) against the TER-1 v2.3 contract (351d34ea…) and the committed chain, after `scope.json` is committed and before or with the seed reveal, as the custody sequence requires.
3. **Independence note:** this SITREP gives hashes and outcomes only. It contains no harness source or design detail, so it adds nothing to the disclosed auditor exposure accepted under option A.

*End of SITREP.*
