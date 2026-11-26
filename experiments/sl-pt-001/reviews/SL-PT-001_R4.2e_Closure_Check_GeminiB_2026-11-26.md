### Delta Items (D-1 to D-8)

* **D-1 (Single-page fetch; V2 strict `null` check): CLOSED**
* §4.2, §4.7 (V2), and §14.1 (U13, U94) remove multi-page pagination and require `next_page_token` to be JSON `null` (failing even on `""` or missing key) with no second request issued. Consistent with §4.1 ("Two keyless GETs per cycle").




* **D-2 (V12a credential scope & evidence): CLOSED**
* §6.4 step 1 defines the checked credential scope (`APCA_` / `ALPACA_` prefix case-insensitively in env vars; any key other than `client_allowlist` in the closed JSON config `{"client_allowlist": [...]}`), requires exact allowlist match `["data.alpaca.markets"]`, logs env var names (never values), config SHA-256, and client allowlist in TER (§10.4), and omits config bytes on failure. §11.1, §13, and §15 (U-I3) explicitly limit V12a claims to `HARNESS-ATTESTED` within the checked scope.




* **D-3 (`lock_clock_at` and append completion/durability): CLOSED**
* §5.4, §6.4 step 8, §10.4, §11.1, §14.8 (U117), and §15 (U-I3, U-T5) define `lock_clock_at` as the harness wall-clock sample taken under the append lock immediately before writing, distinguish it from write completion and `fsync` durability, bound completion order via lock release after `fsync`, and classify pre-`fsync` loss fail-closed as `INCOMPLETE` or `OVERRUN`.




* **D-4 (Stage A BUY-only injections, reachability, and EXIT rules): CLOSED**
* §6.5, §7.3 (R3), §8.1.1, §10.1, §10.2, §10.4, §11.4, and §14.8 (U118, U121) restrict M1-1 runtime injections to BUY fixtures, derive single-rule reachability (R1, R4, R5, R10, R12, R13 for flat BUY; R2, R3, R6, R7, R8, R11, R16, R9, R15 covered via U121 unit tests), exclude R6/R7/R8/R12 from EXIT, and require pre-committed plans/fixtures with unique fixtures per counted injection.




* **D-5 (Stage A R2 limit-order check): CLOSED**
* §11.6 and §14.8 (U119) align the pre-live test gate with §7.3 by including R2's limit-order check in Stage A while keeping TIF and `partial_fill_accepted` in Stage B.




* **D-6 (Bar store gated on V1, V2, V3, V4, and V9): CLOSED**
* §4.9 and §14.8 (U115) prevent responses failing V1, V2, V3, V4, or V9 from mutating the bar store while preserving their raw artifacts in the TER.




* **D-7 (FD-6 commit-reveal seed and evidence custody): CLOSED**
* §11.5 and §14.8 (U120) specify the three-step pushed-commit order (SHA-256 of 64-char hex seed before T_d0 -> audit-scope record fixing evidence commit, chain head, manifests, and eligible `SCHEDULED` `CYCLE` population after `RUN_CLOSE` -> cleartext seed reveal), forbid resampling/substitution, and preserve `07f43e0` (`SL-PT-001_FD6_Seed.txt`) as superseded.




* **D-8 (Body and header artifact definitions): CLOSED**
* §4.3 item 1 specifies post-transfer-decoded body bytes (enforcing `Accept-Encoding: identity`) and the HTTP-client-reported header artifact format (`HTTP/<version> <status> <reason>` CRLF + `Name: value` CRLF + CRLF), noting non-wire-capture status (`UNVERIFIED`) and grounding V1 and V12b reads.





---

### Closure Conditions (CL-01 to CL-04)

* **CL-01: CLOSED**
* §11.5 enforces pushed-commit ordering (seed hash before T_d0; evidence commit, chain head, manifests, and `SCHEDULED` `CYCLE` count/first `seq`/last `seq` after `RUN_CLOSE` and before reveal; seed reveal last), forbids multiple seed commitments or resampling on failure, and marks `07f43e0` superseded (tested in U120).




* **CL-02: CLOSED**
* §6.4 step 1, §11.1, §13, and §15 (U-I3) explicitly state that V12a name/config-key matching defines the checked scope only, recomputation is conditional on harness-attested observations, and no process-level, host-level, or broader credential-absence claim is made.




* **CL-03: CLOSED**
* §6.5 and `sl_pt_001_cl03_fixture_check.py` confirm that at least five single-rule BUY injection fixtures (R1, R4, R5, R10, R12, R13) are constructible under exact rational arithmetic, while R6/R7/R8/R12 dependencies are accurately stated (R6/R7 unreachable by §8.1.1 construction; R8 unreachable while flat; R12 reachable via equity < $450). §6.5, §8.1.1, §11.6, and U121 preserve EXIT and long-position coverage as mandatory pre-live executed unit tests.




* **CL-04: CLOSED**
* §5.4, §6.4 step 8, §10.4, §11.1, §14.8 (U117), and §15 (U-I3, U-T5) explicitly separate `lock_clock_at` (pre-write clock sample under the append lock, `HARNESS-ATTESTED`) from append completion and `fsync` durability, noting that completion after T_d(i+1) is not excluded and that durable evidence rests on pushed chain commits.





---

### Newly Introduced Defects

None in the Stage A normative specification, schema, tests, or registers. (Note: §0 header metadata retains a stale pointer to R4.2c in the provenance/end-line text outside the Stage A freeze scope per §0.2.)

---

### Final Verdict

**FREEZE-READY**