# EIVI-1 Construction Pack CP-3: Scenario Inputs

**Inputs only. No expected results.** Run every scenario under its stated profile. Report every query, and report both R-8 readings for every S1/S2 query (CP-1 §1). Report assumption dependence as specified in CP-2 §3. Some scenarios are traps, and none are identified. Freeze and hash your results before receiving any expected values.

## Log entry language

| Entry | Meaning |
|---|---|
| `SNAP pos=P e=E W=N` | attributed broker snapshot reporting position P at epoch E, watermark N. The first SNAP is the opening (CP-1 B-00) |
| `EXEC e=E #N exec=ID order=O SIDE NEW vK qty=Q` | stream execution at epoch E, sequence N |
| `CORR e=E #N exec=ID vA->vB prior_qty=Q1 qty=Q2` | stream correction naming its prior version (`?` = field missing) |
| `BUST e=E #N exec=ID vA->vB prior_qty=Q1` | stream bust (new quantity 0) |
| `LIST …` | list-path report with the stated fields; `(no seq)` = no sequence number; `exec=?` = no exec_id |
| `MSG e=E #N[..#M] non-economic` | attributed stream messages that carry no economic content |
| `ORDER order=O state=S …` | attributed broker order-state report |
| `PROPOSE p SIDE Q [expires=t]` | internal proposal; the order id of a committed proposal is p |
| `COMMIT p`, `CONSUME p`, `RELEASE p`, `EXPIRE p`, `INVALIDATE p` | internal operations (CP-1 B-21 to B-27); judged at their own log position |
| `ADAPTER p outcome=…` | attributed adapter report |
| `TICK t` | time passes to t (or by +Δ) |
| `GOV set L=… founder_record=yes|no` | governance record (CP-1 B-31) |
| `(UNATTRIBUTED)` | the item failed attribution (CP-1 B-02) |
| `t=…` on an entry | broker occurrence time (meaningful only under E-12 or E-9) |

**Query positions:** `@k` = after the k-th log entry (1-based); `@end` = after the last entry. **Config:** L = 150 unless a GOV entry changes it; the enumeration limit is set by the builder and reported.

### S-01

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 BUY 30`
3. `COMMIT p1`
4. `MSG e=1 #12 non-economic`
5. `MSG e=1 #11 non-economic`
6. `PROPOSE p2 BUY 25`
7. `PROPOSE p3 BUY 20`

**Queries:**

- Q1 @4 STATE
- Q2 @end COMMIT?(p2)
- Q3 @end COMMIT?(p3)

### S-02

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 BUY 40`
3. `COMMIT p1`
4. `CONSUME p1`
5. `PROPOSE p2 BUY 10`
6. `CORR e=1 #11 exec=Y BUY v3->v4 prior_qty=5 qty=25 (Y unknown since bootstrap)`
7. `COMMIT p2`

**Queries:**

- Q1 @5 JUSTIFIED?(buy 10)
- Q2 @7 COMMIT?(p2) (as logged)

### S-03

**Profile:** A0 + E-9(T_f=60)

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p0 BUY 50`
3. `COMMIT p0`
4. `CONSUME p0`
5. `EXEC e=1 #11 exec=X order=p0 BUY NEW v0 qty=50 t=0`
6. `ORDER order=p0 state=FILLED`
7. `TICK t=61`
8. `PROPOSE p1 SELL 120`
9. `COMMIT p1`
10. `LIST BUST exec=X v0->v1 prior_qty=50 (no seq, occurrence time unknown)`

**Queries:**

- Q1 @9 COMMIT?(p1) (as logged)
- Q2 @end BASIS(p1)
- Q3 @end STATE

### S-04

**Profile:** A0

**Log:**

1. `SNAP pos=135 e=1 W=10`
2. `PROPOSE p1 BUY 10`
3. `COMMIT p1`
4. `CONSUME p1`
5. `EXEC e=1 #11 exec="a1B" order=p1 BUY NEW v0 qty=5`
6. `EXEC e=1 #12 exec="A1b" order=p1 BUY NEW v0 qty=5`

**Queries:**

- Q1 @end JUSTIFIED?(buy 5)
- Q2 @end JUSTIFIED?(buy 6)

### S-05

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=0`
2. `PROPOSE p1 BUY 10`
3. `COMMIT p1`
4. `CONSUME p1`
5. `MSG e=1 #1..#10 non-economic`
6. `SNAP pos=100 e=1 W=10`
7. `LIST exec=X9 order=p1 BUY NEW v0 qty=10 (no seq)`

**Queries:**

- Q1 @end JUSTIFIED?(buy 40)
- Q2 @end JUSTIFIED?(buy 41)

### S-06

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p0 BUY 30`
3. `COMMIT p0`
4. `CONSUME p0`
5. `EXEC e=1 #11 exec=X order=p0 BUY NEW v0 qty=30`
6. `LIST exec=X order=p0 BUY NEW v0 qty=30 (no seq)`

**Queries:**

- Q1 @end JUSTIFIED?(buy 20)
- Q2 @end JUSTIFIED?(buy 21)

### S-07

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `ORDER order=f7 (unknown to Sentinel) side=BUY remaining=? state=WORKING`

**Queries:**

- Q1 @end JUSTIFIED?(buy 1)

### S-08

**Profile:** A0

**Log:**

1. `SNAP pos=0 e=1 W=2`
2. `PROPOSE p1 BUY 60`
3. `COMMIT p1`
4. `CONSUME p1`
5. `EXEC e=1 #3 exec=X order=p1 BUY NEW v0 qty=60`
6. `ORDER order=p1 state=FILLED`
7. `LIST CORR exec=X v0->v1 prior_qty=60 qty=10 (no seq)`
8. `MSG e=1 #4 #5 non-economic`
9. `CORR e=1 #6 exec=X v1->v2 prior_qty=10 qty=35`
10. `MSG e=1 #7 #8 non-economic`
11. `SNAP pos=85 e=1 W=8`

**Queries:**

- Q1 @end JUSTIFIED?(buy 115)
- Q2 @end JUSTIFIED?(buy 116)

### S-09

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p0 BUY 50`
3. `COMMIT p0`
4. `CONSUME p0`
5. `EXEC e=1 #11 exec=X order=p0 BUY NEW v0 qty=50`
6. `ORDER order=p0 state=FILLED`
7. `PROPOSE p1 SELL 120`
8. `COMMIT p1`
9. `LIST BUST exec=X v0->v1 prior_qty=50 (no seq, timing unknown)`

**Queries:**

- Q1 @8 COMMIT?(p1) (as logged)
- Q2 @end BASIS(p1)
- Q3 @end REACTIVATE?(p1)

### S-10

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 BUY 30`
3. `COMMIT p1`
4. `CONSUME p1`
5. `ADAPTER p1 outcome=NOT_TRANSMITTED (attributed)`

**Queries:**

- Q1 @4 STATE
- Q2 @end STATE

### S-11

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `SNAP pos=102 e=1 W=10`

**Queries:**

- Q1 @end JUSTIFIED?(buy 1)

### S-12

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p0 BUY 40`
3. `COMMIT p0`
4. `CONSUME p0`
5. `EXEC e=1 #11 exec=X order=p0 BUY NEW v0 qty=40`
6. `ORDER order=p0 state=FILLED`
7. `LIST CORR exec=X v1->v2 prior_qty=30 qty=20 (no seq)`
8. `CORR e=1 #12 exec=X v0->v1 prior_qty=40 qty=30`

**Queries:**

- Q1 @7 JUSTIFIED?(buy 30)
- Q2 @end JUSTIFIED?(buy 30)
- Q3 @end JUSTIFIED?(buy 31)

### S-13

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p0 BUY 10`
3. `COMMIT p0`
4. `CONSUME p0`
5. `EXEC e=1 #11 exec=Z order=p0 BUY NEW v0 qty=10`
6. `ORDER order=p0 state=FILLED`
7. `BUST e=1 #12 exec=Z v0->v1 prior_qty=10`
8. `BUST e=1 #13 exec=Z v0->v1' prior_qty=10`

**Queries:**

- Q1 @end JUSTIFIED?(buy 10)

### S-14

**Profile:** A0

**Log:**

1. `SNAP pos=90 e=1 W=10`
2. `PROPOSE p1 BUY 30`
3. `COMMIT p1`
4. `PROPOSE p2 BUY 30`
5. `COMMIT p2`
6. `CORR e=1 #11 exec=Y BUY v3->v4 prior_qty=5 qty=15 (Y unknown since bootstrap)`
7. `EXPIRE p2`

**Queries:**

- Q1 @6 REACTIVATE?(p1)
- Q2 @6 REACTIVATE?(p2)
- Q3 @end REACTIVATE?(p1)

### S-15

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 BUY 30`
3. `PROPOSE p2 BUY 30`
4. `COMMIT p1`
5. `COMMIT p2`

**Queries:**

- Q1 @4 COMMIT?(p1) (as logged)
- Q2 @5 COMMIT?(p2) (as logged)

### S-16

**Profile:** A0

**Log:**

1. `SNAP pos=140 e=1 W=10`
2. `PROPOSE p1 BUY 10`
3. `COMMIT p1`
4. `CONSUME p1`
5. `EXEC e=1 #11 exec="007" order=p1 BUY NEW v0 qty=5`
6. `EXEC e=1 #12 exec="7" order=p1 BUY NEW v0 qty=5`

**Queries:**

- Q1 @end JUSTIFIED?(buy 1)
- Q2 @end JUSTIFIED?(sell 150)

### S-17

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p0 SELL 30`
3. `COMMIT p0`
4. `CONSUME p0`
5. `EXEC e=1 #11 exec=X1 order=p0 SELL NEW v0 qty=15`
6. `LIST exec=? order=p0 SELL NEW qty=15 (no exec_id, no seq)`

**Queries:**

- Q1 @end JUSTIFIED?(buy 65)
- Q2 @end JUSTIFIED?(buy 66)
- Q3 @end JUSTIFIED?(sell 70)
- Q4 @end JUSTIFIED?(sell 71)

### S-18

**Profile:** A0 − E-8a

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `ORDER order=f1 (foreign) side=? remaining=20 state=WORKING`

**Queries:**

- Q1 @end JUSTIFIED?(buy 30)
- Q2 @end JUSTIFIED?(sell 80)
- Q3 @end JUSTIFIED?(sell 81)

### S-19

**Profile:** A0

**Log:**

1. `SNAP pos=90 e=1 W=10`
2. `PROPOSE p1 SELL 70`
3. `COMMIT p1`
4. `PROPOSE p2 SELL 25`
5. `PROPOSE p3 SELL 20`

**Queries:**

- Q1 @end COMMIT?(p2)
- Q2 @end COMMIT?(p3)

### S-20

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 BUY 40`
3. `COMMIT p1`
4. `GOV set L=120 founder_record=yes`

**Queries:**

- Q1 @end REACTIVATE?(p1)

### S-21

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`

**Queries:**

- Q1 @end JUSTIFIED?(buy 50)
- Q2 @end JUSTIFIED?(buy 51)
- Q3 @end JUSTIFIED?(sell 100)
- Q4 @end JUSTIFIED?(sell 101)

### S-22

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 BUY 5`
3. `COMMIT p1`
4. `CONSUME p1`
5. `EXEC e=1 #12 exec=X2 order=p1 BUY NEW v0 qty=5`
6. `MSG e=1 #11 non-economic`

**Queries:**

- Q1 @5 JUSTIFIED?(buy 1)
- Q2 @5 JUSTIFIED?(sell 1)
- Q3 @end JUSTIFIED?(buy 45)
- Q4 @end JUSTIFIED?(buy 46)

### S-23

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p0 BUY 60`
3. `COMMIT p0`
4. `CONSUME p0`
5. `EXEC e=1 #11 exec=X order=p0 BUY NEW v0 qty=60`
6. `ORDER order=p0 state=FILLED`
7. `PROPOSE p1 SELL 150`
8. `BUST e=1 #12 exec=X v0->v1 prior_qty=60`
9. `COMMIT p1`

**Queries:**

- Q1 @7 JUSTIFIED?(sell 150)
- Q2 @end COMMIT?(p1) (as logged)

### S-24

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 BUY 50`
3. `COMMIT p1`
4. `CONSUME p1`
5. `EXEC e=1 #11 exec=X order=p1 BUY NEW v0 qty=50`
6. `ORDER order=p1 state=FILLED`
7. `CORR e=1 #13 exec=X v1->v2 prior_qty=40 qty=30`
8. `CORR e=1 #12 exec=X v0->v1 prior_qty=50 qty=40`

**Queries:**

- Q1 @7 JUSTIFIED?(buy 1)
- Q2 @end JUSTIFIED?(buy 20)
- Q3 @end JUSTIFIED?(buy 21)

### S-25

**Profile:** A0

**Log:**

1. `SNAP pos=0 e=1 W=4`
2. `PROPOSE p1 BUY 100`
3. `COMMIT p1`
4. `CONSUME p1`
5. `EXEC e=1 #5 exec=X order=p1 BUY NEW v0 qty=100`
6. `ORDER order=p1 state=FILLED`
7. `LIST CORR exec=X v0->v1 prior_qty=100 qty=40 (no seq)`
8. `MSG e=1 #6 #7 non-economic`
9. `CORR e=1 #8 exec=X v1->v2 prior_qty=40 qty=70`
10. `MSG e=1 #9 #10 non-economic`
11. `SNAP pos=130 e=1 W=10`

**Queries:**

- Q1 @end JUSTIFIED?(buy 80)

### S-26

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 BUY 30`
3. `COMMIT p1`
4. `CONSUME p1`
5. `EXEC e=1 #11 exec=X1 order=p1 BUY NEW v0 qty=30`
6. `CORR e=1 #12 exec=X1 v0->v1 prior_qty=30 qty=10`
7. `CORR e=1 #13 exec=X1 v0->v1 prior_qty=30 qty=20`

**Queries:**

- Q1 @end JUSTIFIED?(buy 1)

### S-27

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 BUY 20`
3. `COMMIT p1`
4. `CONSUME p1`
5. `EXEC e=1 #11 exec=X1 order=p1 BUY NEW v0 qty=10`
6. `EXEC e=1 #12 exec=X2 order=p1 BUY NEW v0 qty=10`

**Queries:**

- Q1 @end JUSTIFIED?(buy 30)
- Q2 @end JUSTIFIED?(buy 31)

### S-28

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 BUY 30`
3. `COMMIT p1`
4. `CONSUME p1`

**Queries:**

- Q1 @2 STATE
- Q2 @3 STATE
- Q3 @4 STATE

### S-29

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p0 BUY 20`
3. `COMMIT p0`
4. `CONSUME p0`
5. `EXEC e=1 #11 exec=X order=p0 BUY NEW v0 qty=20`
6. `CORR e=1 #12 exec=X v0->v1 prior_qty=20 qty=15`
7. `CORR e=1 #13 exec=X v1->v2 prior_qty=18 qty=10`

**Queries:**

- Q1 @end JUSTIFIED?(sell 1)

### S-30

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `CORR e=1 #11 exec=Y BUY v3->v4 prior_qty=20 qty=5 (Y unknown since bootstrap)`

**Queries:**

- Q1 @end JUSTIFIED?(sell 85)
- Q2 @end JUSTIFIED?(sell 86)

### S-31

**Profile:** A0

**Log:**

1. `SNAP pos=80 e=1 W=10`
2. `PROPOSE p1 BUY 35`
3. `COMMIT p1`
4. `PROPOSE p2 BUY 35`
5. `COMMIT p2`
6. `CORR e=1 #11 exec=Y BUY v3->v4 prior_qty=10 qty=15 (Y unknown since bootstrap)`
7. `RELEASE p2`

**Queries:**

- Q1 @6 REACTIVATE?(p1)
- Q2 @6 REACTIVATE?(p2)
- Q3 @end REACTIVATE?(p1)

### S-32

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p0 BUY 50`
3. `COMMIT p0`
4. `CONSUME p0`
5. `EXEC e=1 #11 exec=X order=p0 BUY NEW v0 qty=50`
6. `ORDER order=p0 state=FILLED`
7. `BUST e=1 #12 exec=X v0->v1 prior_qty=50 (UNATTRIBUTED)`

**Queries:**

- Q1 @end JUSTIFIED?(sell 100) [posture BLOCK]
- Q2 @end JUSTIFIED?(sell 100) [posture IGNORE]

### S-33

**Profile:** A0 − E-5

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `CORR e=1 #11 exec=Y BUY v3->v4 prior_qty=? qty=10 (Y unknown since bootstrap)`

**Queries:**

- Q1 @end JUSTIFIED?(buy 40)
- Q2 @end JUSTIFIED?(sell 1)

### S-34

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 BUY 40`
3. `COMMIT p1`
4. `CONSUME p1`
5. `PROPOSE p2 BUY 30`
6. `PROPOSE p3 BUY 10`

**Queries:**

- Q1 @end COMMIT?(p2)
- Q2 @end COMMIT?(p3)

### S-35

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 SELL 20`
3. `COMMIT p1`
4. `CONSUME p1`
5. `EXEC e=1 #11 exec=X1 order=p1 SELL NEW v0 qty=20`
6. `LIST exec=X1 order=p1 SELL NEW v0 qty=25 (no seq)`

**Queries:**

- Q1 @end JUSTIFIED?(buy 10)
- Q2 @end JUSTIFIED?(sell 10)

### S-36

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 SELL 60`
3. `COMMIT p1`
4. `PROPOSE p2 BUY 40`
5. `COMMIT p2`
6. `CONSUME p2`

**Queries:**

- Q1 @end JUSTIFIED?(buy 10)
- Q2 @end JUSTIFIED?(buy 11)
- Q3 @end JUSTIFIED?(sell 40)
- Q4 @end JUSTIFIED?(sell 41)

### S-37

**Profile:** A0

**Log:**

1. `SNAP pos=110 e=1 W=10`
2. `PROPOSE p1 BUY 40`
3. `COMMIT p1`
4. `CONSUME p1`
5. `PROPOSE p2 BUY 1`

**Queries:**

- Q1 @3 STATE
- Q2 @4 STATE
- Q3 @end COMMIT?(p2)

### S-38

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `MSG e=1 #11..#50 non-economic`
3. `MSG e=1 #1 non-economic`

**Queries:**

- Q1 @end JUSTIFIED?(buy 1)

### S-39

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p0 BUY 50`
3. `COMMIT p0`
4. `CONSUME p0`
5. `EXEC e=1 #11 exec=X1 order=p0 BUY NEW v0 qty=50`
6. `ORDER order=p0 state=FILLED`
7. `PROPOSE p2 SELL 140`
8. `COMMIT p2`
9. `CONSUME p2`
10. `BUST e=1 #12 exec=X1 v0->v1 prior_qty=50`

**Queries:**

- Q1 @8 COMMIT?(p2) (as logged)
- Q2 @end SAFETY

### S-40

**Profile:** A0 + E-9(T_f=60)

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p0 BUY 50`
3. `COMMIT p0`
4. `CONSUME p0`
5. `EXEC e=1 #11 exec=X order=p0 BUY NEW v0 qty=50 t=0`
6. `ORDER order=p0 state=FILLED`
7. `TICK t=61`
8. `PROPOSE p1 SELL 150`
9. `COMMIT p1`
10. `CORR e=1 #12 exec=X v0->v1 prior_qty=50 qty=20 t=70`

**Queries:**

- Q1 @9 COMMIT?(p1) (as logged)
- Q2 @end JUSTIFIED?(sell 1)

### S-41

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 BUY 40`
3. `COMMIT p1`
4. `GOV set L=200 founder_record=yes`

**Queries:**

- Q1 @end JUSTIFIED?(buy 60)

### S-42

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p0 BUY 20`
3. `COMMIT p0`
4. `CONSUME p0`
5. `EXEC e=1 #11 exec=X order=p0 BUY NEW v0 qty=20`
6. `ORDER order=p0 state=FILLED`
7. `LIST order=p0 complete=yes items=[] (bust semantics undeclared)`

**Queries:**

- Q1 @end JUSTIFIED?(sell 120)
- Q2 @end JUSTIFIED?(sell 100)
- Q3 @end JUSTIFIED?(buy 30)

### S-43

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 BUY 40`
3. `COMMIT p1`
4. `CONSUME p1`
5. `EXEC e=1 #11 exec=X1 order=p1 BUY NEW v0 qty=20`
6. `LIST exec=? order=p1 BUY NEW qty=20 (no exec_id, no seq)`

**Queries:**

- Q1 @end JUSTIFIED?(buy 10)
- Q2 @end JUSTIFIED?(buy 11)

### S-44

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 BUY 20`
3. `COMMIT p1`
4. `CONSUME p1`
5. `TICK +3600s`

**Queries:**

- Q1 @end JUSTIFIED?(buy 30)

### S-45

**Profile:** A0 + E-9(T_f=60)

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p0 BUY 50`
3. `COMMIT p0`
4. `CONSUME p0`
5. `EXEC e=1 #11 exec=X order=p0 BUY NEW v0 qty=50 t=0`
6. `ORDER order=p0 state=FILLED`
7. `TICK t=30`
8. `TICK t=61`

**Queries:**

- Q1 @7 JUSTIFIED?(sell 100)
- Q2 @7 JUSTIFIED?(sell 150)
- Q3 @end JUSTIFIED?(sell 150)

### S-46

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 BUY 30 expires=t5`
3. `COMMIT p1`
4. `CONSUME p1 at t5`
5. `TICK t5`

**Queries:**

- Q1 @end STATE

### S-47

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 BUY 30`
3. `COMMIT p1`
4. `RELEASE p1`
5. `EXEC e=1 #11 exec=X5 order=p1 BUY NEW v0 qty=30`

**Queries:**

- Q1 @end JUSTIFIED?(buy 1)

### S-48

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `MSG e=1 #11..#50 non-economic`

**Queries:**

- Q1 @end JUSTIFIED?(buy 50)

### S-49

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 BUY 30`
3. `COMMIT p1`
4. `CONSUME p1`
5. `TICK +3600s`
6. `PROPOSE p2 BUY 20`
7. `PROPOSE p3 BUY 21`

**Queries:**

- Q1 @end COMMIT?(p2)
- Q2 @end COMMIT?(p3)

### S-50

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 SELL 50`
3. `COMMIT p1`
4. `INVALIDATE p1`

**Queries:**

- Q1 @end JUSTIFIED?(sell 60)

### S-51

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 BUY 40`
3. `COMMIT p1`
4. `GOV set L=200 founder_record=no`

**Queries:**

- Q1 @end JUSTIFIED?(buy 60)

### S-52

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 BUY 5`
3. `COMMIT p1`
4. `CONSUME p1`
5. `EXEC e=1 #12 exec=X2 order=p1 BUY NEW v0 qty=5`
6. `SNAP pos=105 e=1 W=12`

**Queries:**

- Q1 @end JUSTIFIED?(buy 45)
- Q2 @end JUSTIFIED?(buy 40)

### S-53

**Profile:** A0

**Log:**

1. `SNAP pos=60 e=1 W=10`
2. `PROPOSE p1 BUY 50`
3. `COMMIT p1`
4. `CONSUME p1`
5. `PROPOSE p2 BUY 45`
6. `PROPOSE p3 BUY 40`

**Queries:**

- Q1 @end COMMIT?(p2)
- Q2 @end COMMIT?(p3)

### S-54

**Profile:** A0 with E-4I

**Log:**

1. `SNAP pos=0 e=1 W=2`
2. `PROPOSE p1 BUY 80`
3. `COMMIT p1`
4. `CONSUME p1`
5. `EXEC e=1 #3 exec=X order=p1 BUY NEW v0 qty=80`
6. `ORDER order=p1 state=FILLED`
7. `MSG e=1 #4 non-economic`
8. `SNAP pos=30 e=1 W=4`
9. `CORR e=1 #5 exec=X v0->v1 prior_qty=80 qty=30`

**Queries:**

- Q1 @end JUSTIFIED?(buy 120)

### S-55

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p0 BUY 20`
3. `COMMIT p0`
4. `CONSUME p0`
5. `EXEC e=1 #11 exec=X order=p0 BUY NEW v0 qty=20`
6. `CORR e=1 #12 exec=X v0->v1 prior_qty=20 qty=20 side=SELL`

**Queries:**

- Q1 @end JUSTIFIED?(buy 1)

### S-56

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 BUY 30`
3. `COMMIT p1`
4. `CONSUME p1`
5. `EXEC e=1 #11 exec=X1 order=p1 BUY NEW v0 qty=30`
6. `ORDER order=p1 state=FILLED`
7. `CORR e=1 #12 exec=X1 v0->v1 prior_qty=30 qty=10`

**Queries:**

- Q1 @end JUSTIFIED?(buy 40)
- Q2 @end JUSTIFIED?(buy 41)

### S-57

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p1 SELL 20`
3. `COMMIT p1`
4. `CONSUME p1`
5. `EXEC e=1 #11 exec=X1 order=p1 SELL NEW v0 qty=20`
6. `LIST exec=X1 order=p1 SELL NEW v0 qty=20 (no seq)`

**Queries:**

- Q1 @end JUSTIFIED?(buy 70)
- Q2 @end JUSTIFIED?(buy 71)

### S-58

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`

**Queries:**

- Q1 @end JUSTIFIED?(buy 50)

### S-59

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `MSG e=1 #11..#14 non-economic`
3. `PROPOSE p1 BUY 5`
4. `COMMIT p1`
5. `CONSUME p1`
6. `EXEC e=2 #1 exec=X3 order=p1 BUY NEW v0 qty=5`
7. `SNAP pos=110 e=2 W=1`

**Queries:**

- Q1 @6 JUSTIFIED?(buy 1)
- Q2 @end JUSTIFIED?(buy 40)
- Q3 @end JUSTIFIED?(buy 41)

### S-60

**Profile:** A0

**Log:**

1. `SNAP pos=100 e=1 W=10`
2. `PROPOSE p0 BUY 30`
3. `COMMIT p0`
4. `CONSUME p0`
5. `EXEC e=1 #11 exec=X order=p0 BUY NEW v0 qty=30`
6. `ORDER order=p0 state=FILLED`
7. `CORR e=1 #12 exec=X v0->v2 prior_qty=30 qty=20`
8. `CORR e=1 #13 exec=X v2->v5 prior_qty=20 qty=25`

**Queries:**

- Q1 @end JUSTIFIED?(buy 25)
- Q2 @end JUSTIFIED?(buy 26)

*End of CP-3. 60 scenarios. Nothing has been executed.*
