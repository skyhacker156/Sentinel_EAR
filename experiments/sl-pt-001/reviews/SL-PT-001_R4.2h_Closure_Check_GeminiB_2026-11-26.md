### Targets (G7-01, G7-02, C-09)

* **G7-01 (U19 consistency with append-start deadline and U117(c)): CLOSED**
* §14.1 U19 now scopes `CYCLE_OVERRUN(i)` strictly to a slot-i cycle that has **not begun** its `CYCLE` append by $T_d(i+1)$, noting that the old process's later append is refused and explicitly cross-referencing U117(c) for an append begun before $T_d(i+1)$ that finishes after the boundary. This aligns cleanly with §6.4 step 8 ("Deadline") and U117(c).




* **G7-02 (INJECTED terminal paths in §10.4): CLOSED**
* §10.4 splits the single merged `INJECTED` row into a shared baseline row (explicitly narrowing the empty-array requirement to **bar collections** only and deferring `rule results` to each path row) plus three mutually exclusive path rows:
1. `V12a` fails $\rightarrow$ `BOUNDARY_FAIL` (`quote_sha256`, `displayed_sizes`, `created`, and `proposal` set to `null`; `V1`–`V11`, `V12b`, `Q1`–`Q5` `NOT_EVALUATED (V12A_FAILED)`; `rule results` `[]`);
2. `NO_DECISION (QUOTE_INVALID)` (`V12a = PASS`; `quote_sha256` present; `Q1`–`Q5` evaluated with $\ge 1$ `FAIL`; `displayed_sizes` populated where carried by the fixture quote; `created` and `proposal` `null`; `rule results` `[]`);
3. `REJECTED` or `SHADOW_EXPIRED` (`V12a = PASS`; `quote_sha256`, `Q1`–`Q5 = PASS`, `displayed_sizes`, `created`, `proposal`, and all applicable `rule results` present, with `SHADOW_EXPIRED` recorded immediately without the §5.3 ceiling).




* Every field's presence, nullability, and collection state is unambiguous across all four injection terminal outcomes.




* **C-09 (U11 expected sub-reason `DATA_GAP`): CLOSED**
* In §4.7, V8 checks that every 300 s step in $[t_{\text{exp}} - 250\text{ min}, t_{\text{exp}}]$ has a completed bar (51 bars total), while V10 checks for at least 51 completed candles. Because all completed candles must lie on 300 s grid steps (V3) and cannot exceed $t_{\text{exp}}$ (§4.6), any completed bar set with fewer than 51 candles (such as the 50 bars in U11) necessarily leaves at least one of the 51 grid steps in $[t_{\text{exp}} - 250\text{ min}, t_{\text{exp}}]$ empty, failing V8. Because §4.7 evaluates V1–V11 in listed order without short-circuiting and assigns the sub-reason from the **first** failing check, V8 (`DATA_GAP`) always precedes V10 (`INSUFFICIENT_HISTORY`), making U11's updated expectation ("V8 and V10 both FAIL; sub-reason **DATA_GAP**") exact.





---

### Non-Normative Freeze-Record Notes (E-1 to E-3)

* **E-1 (X8/X10 "recorded" = retained test output; `BOUNDARY_VIOLATION_ATTEMPT` not a chain/TER value): CLOSED**
* Accurate and helpful clarification. Neither `BOUNDARY_VIOLATION_ATTEMPT` nor any X10 downstream marker exists in §10.1's closed chain record types or §11.1's closed TER terminal states, matching the pattern established for `REPLAY` in U9.




* **E-2 (HOLD signal always maps to HOLD; §3.3 open/unresolved row applies to BUY and EXIT): CLOSED**
* Accurate derivation from §11.1, which defines qualifying `HOLD` solely by `V1`–`V12b` pass and `signal = HOLD` without checking open orders/authorizations, whereas §3.3's first row ("any | an open, partial, AMBIGUOUS or unresolved order or authorization exists") would otherwise create a literal tension for `HOLD`.




* **E-3 (RFC-3339 timestamp with `second = 60` is malformed under §4.4): CLOSED**
* Accurate. §4.4 maps timestamps to integer nanoseconds since the Unix epoch (UTC), which has no representation for a `:60` leap second; rejecting `second = 60` as `MALFORMED_VALUE` prevents implementation divergence across parsers.





---

### Newly Introduced Defects

None in any normative Stage A text. (Minor non-normative note: line 15 of R4.2h reads "**R4.2g proposes to replace frozen R4.2c**" instead of "**R4.2h proposes to replace frozen R4.2c**". This is in the §0 un-frozen provenance header per §0.2 and does not affect the Stage A freeze scope.)

---

### Final Verdict

**FREEZE-READY**