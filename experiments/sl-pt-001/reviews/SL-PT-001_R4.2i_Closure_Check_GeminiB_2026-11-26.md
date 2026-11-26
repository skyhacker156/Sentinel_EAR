Targets (G8-01, G8-02, G8-03, E-3)

* G8-01 (`displayed_sizes` object shape, nullability, and pre-Q1–Q5 recording): CLOSED
   * §10.4 defines `displayed_sizes` as `{bs, as}`, with each member carrying the original JSON number token text when present and numeric, and `null` otherwise (absent, non-numeric, or malformed).
   * The whole object is `null` if and only if no quote is available (quote request never issued, `NO_RESPONSE`, or `V12a` fail on an injection), and it is populated whether or not `Q1`–`Q5` are evaluated.
   * Consistent with the §10.4 scalar encoding rule (`null` is the only non-string scalar permitted; token texts are strings) and the `NO_DECISION (QUOTE_INVALID)` injection row.
* G8-02 (U108 coverage of all scheduled and injected terminal-path rows plus partial/absent `displayed_sizes`): CLOSED
   * §14.8 U108 now covers every scheduled row of §10.4's table (explicitly exercising both `REJECTED` and `SHADOW_EXPIRED` for a constructed proposal), all four injected rows (`V12a FAIL`, `QUOTE_INVALID`, `REJECTED`, `SHADOW_EXPIRED`), and a `QUOTE_INVALID` case with one and with both displayed sizes absent.
* G8-03 (Stale R4.2g pointer in §0 provenance header): CLOSED
   * Line 15 of R4.2i now reads "R4.2i proposes to replace frozen R4.2c (candidates R4.2d to R4.2h are superseded and were never frozen)", matching the document title, line 4 delta header, and closing line.
* E-3 (RFC-3339 leap second `second = 60` malformed under §4.4; U122): CLOSED
   * §4.4 explicitly specifies that a seconds field of `60` is malformed (restricting RFC 3339 because leap seconds have no exact Unix epoch-ns value), and §14.8 U122 tests `2016-12-31T23:59:60Z` (`MALFORMED_VALUE`) alongside `2016-12-31T23:59:59.999999999Z` (parses exactly).

Newly Introduced Defects
None.

Final Verdict
FREEZE-READY
