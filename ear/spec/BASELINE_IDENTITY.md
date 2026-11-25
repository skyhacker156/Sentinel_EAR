# EAR v0.1 — Baseline identity record

SPECIFICATION ONLY / NOT IMPLEMENTED / NOT VERIFIED. Implementation authorization: NO-GO.

First recorded 2026-11-24 (commit 767f236, Revision 3 only). Updated 2026-11-24, when Revision 3.1 was located. Recorded by Claude (ARBITER / Specification Lead). Hashes computed, not copied from the files.

## Current review baseline

**Revision 3.1, SHA-256 dd9d87f76b01134e084827b0202c73c52fccb2b86f21a176a6b6e551241fa239. MATCH** with the hash the founder dispatch names.

Revision 3.1 states in its own header that it supersedes Revision 3 (9a2c3be7…b0a). It is dated 2026-11-23 and is frozen for targeted final review.

## Files in this folder

| File | SHA-256 | What it is |
|---|---|---|
| EAR_v0.1_Rev3.1_FROZEN.md | dd9d87f76b01134e084827b0202c73c52fccb2b86f21a176a6b6e551241fa239 | **Revision 3.1, the current baseline** |
| EAR_v0.1_Rev3_FROZEN.md | 9a2c3be747fa9acbe4513e77f4122712f1970aa17109beb52acffbe051702b0a | Revision 3, superseded, kept as history |
| EAR_v0.1_Rev3_part1_header-to-invariants.md | a7ed43fab20b4372411b23d6a08ab47929354441f5cd3a303bc509ed3b67bc58 | Rev 3 part 1, as received |
| EAR_v0.1_Rev3_part2_events-to-vectors.md | 7e4ba15f0a34f9a79ad68682b6a9836062fd33168aec7d5875ffd1e27b4c9f11 | Rev 3 part 2, as received |
| EAR_v0.1_Rev3_part3_assumptions-to-registers.md | 40149b37c469249f8b196f91d94eceb269743a331382afad68240976e9771dea | Rev 3 part 3, as received |
| DISPATCH_2026-11-24_resume_EAR_rev3.1.md | d242811a53802e0ae46c60aa656d84ab80be825829588cd75c009aa76b0d4aec | Founder dispatch that started this review |

`SHA256SUMS.txt` lists the same six hashes, so a script can check them.

## How Revision 3.1 was recovered (one byte-level transformation, disclosed)

The copy the founder supplied had Windows CRLF line endings and no final newline. Its SHA-256 was 6ab8c8117bb8c7d0c38cd90950094184b4b03d04f43f6f02a64c4369bcab1fb6, which did not match.

The only change made: each CRLF was replaced with LF, and one final LF was added. The result hashes exactly to dd9d87f7…, the published value. No character of text was changed. The original was therefore an LF file ending in a newline, the same form as Revision 3, and the copy was altered in transit, not edited.

To reproduce: take the supplied copy, replace every `\r\n` with `\n`, append `\n`, then hash.

## Resolved

- The earlier record (commit 767f236) listed the missing Revision 3.1 as open. **That is now resolved.** Revision 3.1 exists, matches the dispatch hash, and is the baseline.

## What this record does not establish

Integrity of these bytes only: that this file is the one whose hash the dispatch names. Not authorship, not that the specification is correct, not that any review of it was done.
