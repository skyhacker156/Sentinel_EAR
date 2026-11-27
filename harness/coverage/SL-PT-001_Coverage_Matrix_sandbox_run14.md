# SL-PT-001 | §11.6 coverage matrix (Stage A) | generated

Spec SHA-256 `4259551121fa3d271074fb13da51fb270ae859b0b516a953752731f20972a51a`; test log `sandbox_run14_gate_py3.12.txt` SHA-256 `60a0b0108f0c6bcccf8ffeeb114c271bf7f0b45d4fc1cfed7064ecc7c754a580`; 210 test results parsed.

| id | §14 input (abridged) | harness evidence (tests, result) | auditor half | status |
|---|---|---|---|---|
| U1 | D(k−1) = −4, D(k) = −1 | `Crossover.test_U1_minus4_to_minus1_hold` ok | - | HARNESS-EXECUTED |
| U2 | −3 → +2 | `Crossover.test_U2_minus3_to_plus2_buy` ok | - | HARNESS-EXECUTED |
| U3 | +3 → −2 | `Crossover.test_U3_plus3_to_minus2_exit` ok | - | HARNESS-EXECUTED |
| U4a | −1 → 0 | `Crossover.test_U4a_minus1_to_0_hold` ok | - | HARNESS-EXECUTED |
| U4b | 0 → +1 | `Crossover.test_U4b_0_to_plus1_buy` ok | - | HARNESS-EXECUTED |
| U4c | +1, 0, +1 | `Crossover.test_U4c_plus1_0_plus1_buy_at_third_step` ok | - | HARNESS-EXECUTED |
| U4d | −1, 0, −1 | `Crossover.test_U4d_minus1_0_minus1_exit_at_third_step` ok | - | HARNESS-EXECUTED |
| U4e | closes whose float sums differ but whose exact sums are equal | `Indicators.test_U4e_exact_equality_where_binary_arithmetic_differs` ok | - | HARNESS-EXECUTED |
| U5 | T_d = 10:05:30 (a late invocation in the slot whose T_d = 10:01); bars up to t = 10:00 | `CompletedCandles.test_U5_late_invocation_keeps_slot_and_rule` ok | - | HARNESS-EXECUTED |
| U6 | one bar absent in the 51-bar window | `BarValidation.test_U6_one_bar_absent_in_window_DATA_GAP` ok | - | HARNESS-EXECUTED |
| U7a | duplicate t, byte-identical | `BarValidation.test_U7a_identical_duplicate_collapses_with_note` ok | - | HARNESS-EXECUTED |
| U7b | duplicate t, differing content | `BarValidation.test_U7b_differing_duplicate_DATA_CONFLICT` ok | - | HARNESS-EXECUTED |
| U8 | (a) the newest completed bar is 10 min older than t_exp; (b) a valid quote 16 s old with a | `BarValidation.test_U8a_newest_completed_10_min_old_STALE_SERIES` ok<br>`IntegratedPath.test_PATH_U8b_stale_quote_REJECTED_R4` ok | - | HARNESS-EXECUTED |
| U9 | replay of stored artifacts | `FullCycle.test_U9_replay_identical` ok<br>`TERPaths.test_U9_replay_byte_identical_TER` ok | - | HARNESS-EXECUTED |
| U10 | 100 runs; other process, locale, timezone | `Determinism.test_U10_identical_across_runs_processes_locale_timezone` ok | - | HARNESS-EXECUTED |
| U11 | 50 completed bars ending at t_exp | `BarValidation.test_U11_CONFLICT_50_bars_first_failure_is_V8_not_V10` ok<br>`Indicators.test_U11_history_precondition` ok | - | HARNESS-EXECUTED |
| U12 | bars in reverse order | `BarValidation.test_U12_reverse_order_sorted_same_result` ok | - | HARNESS-EXECUTED |
| U13 | next_page_token not null (a string, including `""`) | `V1V2.test_U13_page_token_not_null_INCOMPLETE_no_second_request` ok | - | HARNESS-EXECUTED |
| U14 | BUY while long; EXIT while flat (**fixture-backed**) | `Mapping.test_U14_flat_boundary` ok | - | HARNESS-EXECUTED |
| U15 | invocation at T_d + 200 s | `Section14Rows.test_U15_invocation_at_T_d_plus_200s_same_cycle_id_R13` ok | - | HARNESS-EXECUTED |
| U17 | the response includes a bar with t + 360 s > T_d | `BarValidation.test_U17_forming_bar_excluded_and_recorded` ok<br>`CompletedCandles.test_U17_bar_past_settle_is_excluded` ok | - | HARNESS-EXECUTED |
| U18 | identical candles, varied quotes | `Indicators.test_U18_quote_independence` ok<br>`IntegratedPath.test_PATH_U18_quote_does_not_change_signal` ok | - | HARNESS-EXECUTED |
| U19 | a slot-i cycle that has **not begun** its CYCLE append by T_d(i+1) (still computing, or wa | `TokenTable.test_U19_U83_overrun_successor_writes_and_old_append_refused` ok | REQUIRED (GPT) | HARNESS-EXECUTED + auditor half pending |
| U24 | v tokens `0`, `0.0`, `0e0`, `-0`, `0.00000001` | `BarValidation.test_U24_zero_volume_bar_retained_in_window` ok<br>`NumberTokens.test_U24_zero_volume_by_exact_value` ok | - | HARNESS-EXECUTED |
| U25 | tokens whose float sums differ from the exact sums; exponents | `NumberTokens.test_U25_exact_sums_where_binary_sums_differ` ok | - | HARNESS-EXECUTED |
| U78 | bar with t + 360 s = T_d, and with T_d one ns earlier | `CompletedCandles.test_U78_boundary_inclusive_then_one_ns_earlier` ok | - | HARNESS-EXECUTED |
| U84 | a confirmed bar disappears from the response | `BarStore.test_U84_disappearance_in_window_DATA_GAP_and_note` ok | - | HARNESS-EXECUTED |
| U85 | `60000.0` → `60000.00` | `BarStore.test_U85_token_text_change_is_a_revision` ok<br>`BarValidation.test_U85_token_text_difference_is_a_difference` ok | - | HARNESS-EXECUTED |
| U87 | inexact operation; long mantissa; large and small exponents; NaN or Infinity token | `NumberTokens.test_U87_long_mantissa_and_extreme_exponents_are_exact` ok<br>`NumberTokens.test_U87_malformed_tokens` ok<br>`Purity.test_U87_no_float_literal_or_call` ok<br>`Purity.test_U87_no_true_division_by_or_of_an_int_literal` ok | - | HARNESS-EXECUTED |
| U89 | an end-labelled fixture | `CompletedCandles.test_U89_end_labelled_bars_never_used_before_close` ok | - | HARNESS-EXECUTED |
| U94 | `next_page_token` key absent | `V1V2.test_U94_missing_page_token_key_and_bar_field_INCOMPLETE` ok | - | HARNESS-EXECUTED |
| U31 | revision outside the 51-bar window / inside it | `BarStore.test_U31_revision_outside_window_recorded_only` ok | - | HARNESS-EXECUTED |
| U35 | first cycle ever (empty store) | `BarStore.test_U35_first_cycle_all_BASELINED` ok | - | HARNESS-EXECUTED |
| U36 | slot 1 OK, slot 2 NO_DECISION, slot 3; a bar revised between 1 and 3 | `BarStore.test_U36_detection_against_slot_1_after_a_NO_DECISION_slot` ok | - | HARNESS-EXECUTED |
| U37 | as U36, with slot 2 MISSING | - | REQUIRED (GPT) | AUDITOR-ONLY: pending GPT table |
| U38 | slot 2 CYCLE_OVERRUN | - | REQUIRED (GPT) | AUDITOR-ONLY: pending GPT table |
| U39 | revision at slot 3 (pending → NO_DECISION); the same bytes at slot 4 | `BarStore.test_U39_revision_pending_then_confirmed_next_slot` ok | - | HARNESS-EXECUTED |
| U40 | A → B → A over three cycles | `BarStore.test_U40_A_B_A_is_two_revisions` ok | - | HARNESS-EXECUTED |
| U28 | quote dated 1 ns after the checkpoint; age exactly 15 s; age 15 s + 1 ns | `Policy.test_U28_freshness_boundaries` ok | - | HARNESS-EXECUTED |
| U44 | created = T_d + 5 s | `Section14More.test_U44_created_T_d_plus_5s_proposal_and_deadline` ok | - | HARNESS-EXECUTED |
| U45 | created = T_d + 30 s exactly | `IntegratedPath.test_PATH_U45_cutoff_inclusive_passes` ok | - | HARNESS-EXECUTED |
| U46 | created = T_d + 30 s + 1 ns | `IntegratedPath.test_PATH_U46_authorization_window_REJECTED_R13` ok | - | HARNESS-EXECUTED |
| U47 | created = T_d + 250 s | `IntegratedPath.test_PATH_U47_created_late_REJECTED_R13` ok | - | HARNESS-EXECUTED |
| U52 | invocation at exactly T_d(i+1) | `SlotIdentity.test_U52_invocation_exactly_at_next_T_d` ok | - | HARNESS-EXECUTED |
| U53 | **property:** random created ∈ [T_d, T_d + 300 s) and lawful approval and issuance times | `SlotIdentity.test_U53_cutoff_boundaries` ok<br>`SlotIdentity.test_U53_property_slot_anchored_clocks` ok | - | HARNESS-EXECUTED |
| U79 | with t_recv − t_send = 1 s: θ_high = +2 s exactly / + 1 ns; θ_low = −2 s exactly / − 1 ns  | `ClockCheck.test_U79_theta_boundaries` ok | - | HARNESS-EXECUTED |
| U33 | a budget exactly divisible; a budget one cent short | `Policy.test_U33_budget_divisible_and_one_cent_short` ok | - | HARNESS-EXECUTED |
| U80 | Q1, Q2, Q3, Q4 and Q5 each failing; and a valid but stale quote | `IntegratedPath.test_PATH_U80_invalid_quote_on_BUY_NO_DECISION_QUOTE_INVALID` ok<br>`IntegratedPath.test_PATH_U80_stale_but_valid_quote_REJECTED_not_QUOTE_INVALID` ok<br>`QuoteValidation.test_U80_each_Q_check_failing` ok<br>`QuoteValidation.test_U80_missing_or_malformed_fields_and_absent_quote` ok | - | HARNESS-EXECUTED |
| U81 | q < min_order_size | `IntegratedPath.test_PATH_U81_insufficient_quantity_REJECTED_R10` ok | - | HARNESS-EXECUTED |
| U82 | cash_available < $150 | `Policy.test_U82_cash_available_below_150` ok | - | HARNESS-EXECUTED |
| U26 | states `"hold"`, `"HOLD "`, absent, two states, `"OK"` | - | REQUIRED (GPT) | AUDITOR-ONLY: pending GPT table |
| U27 | slot 17 absent; slot 23 duplicated; an off-grid record; harness counter falsely 41 | - | REQUIRED (GPT) | AUDITOR-ONLY: pending GPT table |
| U34 | a HOLD record whose recomputation from artifacts fails V | - | REQUIRED (GPT) | AUDITOR-ONLY: pending GPT table |
| U41 | N = 40; records for slots 0 to 24 only | - | REQUIRED (GPT) | AUDITOR-ONLY: pending GPT table |
| U42 | manifest without `declared_slots`, or N = 29 | `PolicyAndManifest.test_U42_U72_and_schema` ok | - | HARNESS-EXECUTED |
| U43 | run 2's records removed from the chain | `Chain.test_U43_record_removed_reported` ok | - | HARNESS-EXECUTED |
| U66 | a manifest in the repository but not in the chain, and the reverse | - | REQUIRED (GPT) | AUDITOR-ONLY: pending GPT table |
| U67 | a TER with an unknown or missing field | `TERSchema.test_U67_unknown_or_missing_field` ok | - | HARNESS-EXECUTED |
| U68 | an injection with origin SCHEDULED and a valid cycle_id | - | REQUIRED (GPT) | AUDITOR-ONLY: pending GPT table |
| U69 | the same cycle_id under two manifests | - | REQUIRED (GPT) | AUDITOR-ONLY: pending GPT table |
| U70 | one byte of a chain record altered | `Chain.test_U70_one_byte_altered_breaks_chain` ok | - | HARNESS-EXECUTED |
| U71 | a V-pass asserted against the wrong raw artifact | - | REQUIRED (GPT) | AUDITOR-ONLY: pending GPT table |
| U72 | manifest edited after the run | `PolicyAndManifest.test_U42_U72_and_schema` ok | - | HARNESS-EXECUTED |
| U73 | missed tick (no invocation) | `TokenTable.test_U73_U75_U76_missed_slots_leave_no_record` ok | REQUIRED (GPT) | HARNESS-EXECUTED + auditor half pending |
| U74 | duplicate wake in the same slot | `TokenTable.test_U74_duplicate_after_completion` ok<br>`TokenTable.test_U74_second_invocation_while_running` ok | REQUIRED (GPT) | HARNESS-EXECUTED + auditor half pending |
| U75 | harness restart mid-run | `TokenTable.test_U73_U75_U76_missed_slots_leave_no_record` ok | REQUIRED (GPT) | HARNESS-EXECUTED + auditor half pending |
| U76 | machine sleep, then resume late in a slot | `TokenTable.test_U73_U75_U76_missed_slots_leave_no_record` ok | REQUIRED (GPT) | HARNESS-EXECUTED + auditor half pending |
| U77 | an invocation without a record / a record without an invocation | `TokenTable.test_U77_every_invocation_leaves_a_record` ok | REQUIRED (GPT) | HARNESS-EXECUTED + auditor half pending |
| U83 | an overrunning old process tries to append after takeover | `TokenTable.test_U19_U83_overrun_successor_writes_and_old_append_refused` ok<br>`TokenTable.test_U83_lost_token_refused_even_inside_the_slot` ok | REQUIRED (GPT) | HARNESS-EXECUTED + auditor half pending |
| U88 | a TER containing a JSON number | `TERSchema.test_U88_json_number_anywhere` ok<br>`TERSchema.test_U88_numbers_only_the_general_guard_can_see` ok | - | HARNESS-EXECUTED |
| U91 | an injection running at a slot boundary | `Injections.test_U91_slot_invocation_aborts_injection` ok | REQUIRED (GPT) | HARNESS-EXECUTED + auditor half pending |
| U95 | a bars or quote response keyed by a symbol other than `BTC/USD`, or containing an extra sy | `V1V2.test_U95_quote_wrong_symbol_fails_V1` ok | - | HARNESS-EXECUTED |
| U96 | the first-ever cycle: the V12a → bars fetch → V12b → quote fetch sequence | `Section14Rows.test_U96_order_V12a_bars_V12b_quote_and_no_quote_after_V12b_fail` ok | - | HARNESS-EXECUTED |
| U97 | clock masking: a data-host offset of +4 s with 2 s of response transit (a point estimate n | `Section14Pure.test_U97_clock_masking_plus_4s_with_2s_transit` ok | - | HARNESS-EXECUTED |
| U98 | relative to D = 0: t_send = −1 s with t_recv = 2 s − 1 ns (round trip 3 s − 1 ns; θ_high = | `Section14Pure.test_U98_round_trip_boundaries` ok | - | HARNESS-EXECUTED |
| U99 | crash injected after each boundary: invocation-log append; bars stored; V12b; quote stored | `Section14Rows.test_U99_crash_before_append_leaves_no_CYCLE_orphans_kept` ok<br>harness half: no CYCLE, orphans kept, chain verifies; classification INCOMPLETE is auditor's. Finding F-3: §6.3 row 3 makes the successor write CYCLE_OVERRUN for a crashed slot (U103 precedence -> OVERRUN), while U99 expects INCOMPLETE; reading requested from GPT (waypoint 5) | REQUIRED (GPT) | HARNESS-EXECUTED + auditor half pending |
| U100 | a bar BASELINED, then a changed tuple, then the same changed tuple again | `Section14More.test_U100_baselined_changed_same_changed_confirmed` ok | - | HARNESS-EXECUTED |
| U101 | a bar changing on every fetch, A → B → C → D | `Section14Pure.test_U101_A_B_C_D_pending_throughout` ok | - | HARNESS-EXECUTED |
| U102 | the last slot of a run still holding the token at RUN_CLOSE | `Section14Rows.test_U102_last_slot_token_at_RUN_CLOSE` ok | REQUIRED (GPT) | HARNESS-EXECUTED + auditor half pending |
| U103 | a slot with both a CYCLE_OVERRUN record and no CYCLE record | - | REQUIRED (GPT) | AUDITOR-ONLY: pending GPT table |
| U104 | a proposal whose SHADOW_EXPIRED append is delayed past T_d(i+1) | `Section14Rows.test_U104_shadow_expired_delayed_past_next_boundary` ok | REQUIRED (GPT) | HARNESS-EXECUTED + auditor half pending |
| U105 | sizing vectors, with qty_increment 0.0001, f_res 0.0025 and price_increment 1 (the Stage A | `Section14Pure.test_U105_sizing_vectors` ok | - | HARNESS-EXECUTED |
| U106 | t_recv < t_send | `Section14Pure.test_U106_t_recv_before_t_send` ok | - | HARNESS-EXECUTED |
| U107 | `Date` absent; `Date` unparseable | `Section14Pure.test_U107_Date_absent_or_unparseable` ok | - | HARNESS-EXECUTED |
| U108 | one TER per terminal-path row of §10.4's table, scheduled and injected: every scheduled ro | `Injections.test_U108_injected_rows` ok<br>`TERPaths.test_U108_every_scheduled_path` ok | - | HARNESS-EXECUTED |
| U109 | (a) a malformed CYCLE_OVERRUN record; (b) a CYCLE record and a CYCLE_OVERRUN record for th | - | REQUIRED (GPT) | AUDITOR-ONLY: pending GPT table |
| U110 | an EXIT fixture: shadow BTC 0.0030, passing proposal | `Section14Pure.test_U110_EXIT_fixture_reservation` ok | - | HARNESS-EXECUTED |
| U111 | (a) V1 fails; (b) V2 fails; (c) V7 fails with V1 and V2 passing | `BarValidation.test_U111c_non_short_circuit_all_failures_recorded` ok<br>`V1V2.test_U111a_V1_http_encoding_json_symbol_FETCH_FAILED` ok | - | HARNESS-EXECUTED |
| U112 | the bars request ends with no HTTP response | `TransportAndClock.test_U112_bars_no_response` ok | - | HARNESS-EXECUTED |
| U113 | the quote request ends with no HTTP response: (a) signal HOLD; (b) signal BUY, flat | `TransportAndClock.test_U113a_quote_no_response_HOLD` ok<br>`TransportAndClock.test_U113b_quote_no_response_BUY_QUOTE_INVALID_all_Q_fail` ok | - | HARNESS-EXECUTED |
| U114 | an OFF_RUN record with an altered byte, or an unknown field | `Chain.test_U114_off_run_unknown_field_and_crlf` ok | - | HARNESS-EXECUTED |
| U122 | timestamps `2016-12-31T23:59:60Z` and `2016-12-31T23:59:59.999999999Z` | `Section14Pure.test_U122_leap_second_malformed_and_9_fraction_digits_exact` ok | - | HARNESS-EXECUTED |
| U115 | a bars response failing V9 (one `c` token `"NaN"`), followed next slot by a valid response | `BarStore.test_U115_V9_failing_response_not_admitted` ok<br>`BarStore.test_U115b_bare_NaN_body_is_V1_not_V9` ok | - | HARNESS-EXECUTED |
| U116 | V12a: environment variable `APCA_API_KEY_ID` set (any value); separately, a configuration  | `BoundaryV12a.test_U116_config_extra_key_allowlist_mismatch_missing_config` ok<br>`BoundaryV12a.test_U116_env_credential_name_recorded_not_value` ok | - | HARNESS-EXECUTED |
| U117 | (a) a CYCLE append attempted with `lock_clock_at` ≥ T_d(i+1); (b) a SHADOW_EXPIRED record  | `TokenTable.test_U117a_append_at_or_after_next_boundary_refused` ok<br>`TokenTable.test_U117b_shadow_expired_refused_if_clock_reads_before_ceiling` ok<br>`TokenTable.test_U117c_append_begun_in_slot_is_not_an_overrun` ok<br>(a)(b)(c) harness-executed; (d)(e) kill-before/after-fsync not executable in-process: harness half is U99 crash test; durability itself is not claimed (§10.4) | REQUIRED (GPT) | HARNESS-EXECUTED + auditor half pending |
| U118 | injections: (a) plan or fixture committed after the INJECTION record; (b) a second rule al | `Injections.test_U118_second_rule_also_fails_is_recorded_whole` ok | REQUIRED (GPT) | HARNESS-EXECUTED + auditor half pending |
| U119 | R2: the policy evaluator given a proposal whose order type is not LIMIT | `Section14Pure.test_U119_R2_not_limit` ok | - | HARNESS-EXECUTED |
| U121 | evaluator-level cases with directly constructed inputs, over every rule applicable to the  | `Section14More.test_U121_evaluator_exact_failing_sets` ok | - | HARNESS-EXECUTED |
| U120 | seed custody: (a) the revealed seed's SHA-256 differs from step 1; (b) evidence commit or  | - | REQUIRED (GPT) | AUDITOR-ONLY: pending GPT table |

**Totals:** AUDITOR-ONLY: pending GPT table: 13; HARNESS-EXECUTED: 73; HARNESS-EXECUTED + auditor half pending: 13; rows: 99

Auditor results are synthetic classification checks only: they are not evidence of real scheduler, concurrency, crash-recovery or filesystem-durability behavior (GPT dispatch, 2026-11-26).
