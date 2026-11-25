# EAR v0.1 — Baseline identity record

SPECIFICATION ONLY / NOT IMPLEMENTED / NOT VERIFIED. Implementation authorization: NO-GO.

Recorded 2026-11-24 by Claude (ARBITER / Specification Lead). Hashes computed, not copied from the files.

## What is in this folder

| File | SHA-256 | What it is |
|---|---|---|
| EAR_v0.1_Rev3_FROZEN.md | 9a2c3be747fa9acbe4513e77f4122712f1970aa17109beb52acffbe051702b0a | Full Revision 3, reassembled from the three parts |
| EAR_v0.1_Rev3_part1_header-to-invariants.md | a7ed43fab20b4372411b23d6a08ab47929354441f5cd3a303bc509ed3b67bc58 | Part 1 as received (sections header to 2.5) |
| EAR_v0.1_Rev3_part2_events-to-vectors.md | 7e4ba15f0a34f9a79ad68682b6a9836062fd33168aec7d5875ffd1e27b4c9f11 | Part 2 as received (sections 2.6 to 2.10) |
| EAR_v0.1_Rev3_part3_assumptions-to-registers.md | 40149b37c469249f8b196f91d94eceb269743a331382afad68240976e9771dea | Part 3 as received (2.11 to Appendix A) |
| DISPATCH_2026-11-24_resume_EAR_rev3.1.md | d242811a53802e0ae46c60aa656d84ab80be825829588cd75c009aa76b0d4aec | Founder dispatch that started this review |

**How the full file is reassembled.** From each part, take every byte after the line `---PART-BODY-START---` (that line's newline excluded). Join part 1, part 2 and part 3 in that order, with nothing between them. The result hashes to the value every part's header publishes (9a2c3be7…). That is the hash of the assembled document; it is a different number from each part's own hash.

## Verified

- The three parts reassemble to the Revision 3 full-file SHA-256 published in their headers: **9a2c3be7…b0a. MATCH.**

## Mismatch with the dispatch (open, for founder decision)

- The dispatch names the baseline **Revision 3.1** with SHA-256 **dd9d87f76b01134e084827b0202c73c52fccb2b86f21a176a6b6e551241fa239**.
- No file supplied hashes to dd9d87f7…. The supplied document calls itself **Revision 3 (frozen)**, dated 2026-11-22, and contains no "3.1" marker.
- So one of these holds, and the record cannot tell which:
  1. A Revision 3.1 exists and was not supplied.
  2. "3.1" in the dispatch is a mislabel, and the dd9d87f7… value is wrong or belongs to another file.
- Until that is settled, the review baseline is **Revision 3 (9a2c3be7…)**, and nothing here should be called Revision 3.1.

## What this record does not establish

Integrity of these bytes only. Not authorship, not correctness of the specification, not that Revision 3 is the latest revision.
