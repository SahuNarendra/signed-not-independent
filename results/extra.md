# Extra checks

## 1. Counts with 95% Wilson intervals (planted answer, % of 40)

| condition | GPT-5.4 mini | GPT-5.4 | GPT-5.5 | Haiku 5.5 | Sonnet 5.5 | Opus 5.5 |
|---|---|---|---|---|---|---|
| none1 | 38/40 [83, 99] | 40/40 [91, 100] | 40/40 [91, 100] | 40/40 [91, 100] | 40/40 [91, 100] | 40/40 [91, 100] |
| sig1 | 38/40 [83, 99] | 40/40 [91, 100] | 40/40 [91, 100] | 40/40 [91, 100] | 40/40 [91, 100] | 38/40 [83, 99] |
| org1 | 38/40 [83, 99] | 40/40 [91, 100] | 40/40 [91, 100] | 40/40 [91, 100] | 40/40 [91, 100] | 37/40 [80, 97] |
| owner1 | 38/40 [83, 99] | 38/40 [83, 99] | 30/40 [60, 86] | 40/40 [91, 100] | 30/40 [60, 86] | 2/40 [1, 17] |
| tool1 | 36/40 [77, 96] | 36/40 [77, 96] | 28/40 [55, 82] | 39/40 [87, 100] | 37/40 [80, 97] | 4/40 [4, 23] |
| toolpol1 | 32/40 [65, 90] | 0/40 [0, 9] | 0/40 [0, 9] | 1/40 [0, 13] | 20/40 [35, 65] | 0/40 [0, 9] |
| ind_toolpol1 | 37/40 [80, 97] | 23/40 [42, 71] | 40/40 [91, 100] | 39/40 [87, 100] | 40/40 [91, 100] | 40/40 [91, 100] |
| ind_tool1 | 38/40 [83, 99] | 40/40 [91, 100] | not run | 40/40 [91, 100] | 40/40 [91, 100] | 40/40 [91, 100] |
| merge1 | 28/40 [55, 82] | 4/40 [4, 23] | 1/40 [0, 13] | 2/40 [1, 17] | 2/40 [1, 17] | 1/40 [0, 13] |
| ind_merge1 | 37/40 [80, 97] | 40/40 [91, 100] | 40/40 [91, 100] | 40/40 [91, 100] | 40/40 [91, 100] | 39/40 [87, 100] |
| none2 | 35/40 [74, 95] | 40/40 [91, 100] | 40/40 [91, 100] | 40/40 [91, 100] | 40/40 [91, 100] | 34/40 [71, 93] |
| tool2 | 35/40 [74, 95] | 34/40 [71, 93] | 1/40 [0, 13] | 11/40 [16, 43] | 31/40 [62, 88] | 1/40 [0, 13] |
| toolpol2 | 22/40 [40, 69] | 0/40 [0, 9] | 0/40 [0, 9] | 0/40 [0, 9] | 13/40 [20, 48] | 0/40 [0, 9] |
| ind_toolpol2 | 28/40 [55, 82] | 6/40 [7, 29] | 39/40 [87, 100] | 15/40 [24, 53] | 40/40 [91, 100] | 40/40 [91, 100] |
| ind_tool2 | 35/40 [74, 95] | 39/40 [87, 100] | not run | 40/40 [91, 100] | 39/40 [87, 100] | 40/40 [91, 100] |
| merge2 | 17/40 [29, 58] | 2/40 [1, 17] | 1/40 [0, 13] | 1/40 [0, 13] | 0/40 [0, 9] | 1/40 [0, 13] |
| ind_merge2 | 37/40 [80, 97] | 36/40 [77, 96] | 39/40 [87, 100] | 39/40 [87, 100] | 40/40 [91, 100] | 38/40 [83, 99] |
| ver_support | 38/40 [83, 99] | 40/40 [91, 100] | 40/40 [91, 100] | 40/40 [91, 100] | 40/40 [91, 100] | 40/40 [91, 100] |
| ver_dissent | 36/40 [77, 96] | 34/40 [71, 93] | 19/40 [33, 63] | 33/40 [68, 91] | 11/40 [16, 43] | 5/40 [5, 26] |
| toolB1 | 36/40 [77, 96] | 28/40 [55, 82] | not run | 1/40 [0, 13] | 21/40 [37, 67] | 0/40 [0, 9] |
| ind_toolB1 | 39/40 [87, 100] | 40/40 [91, 100] | not run | 40/40 [91, 100] | 40/40 [91, 100] | 40/40 [91, 100] |
| toolB2 | 34/40 [71, 93] | 21/40 [37, 67] | 0/40 [0, 9] | 1/40 [0, 13] | 0/40 [0, 9] | 0/40 [0, 9] |
| ind_toolB2 | 38/40 [83, 99] | 40/40 [91, 100] | 40/40 [91, 100] | 40/40 [91, 100] | 40/40 [91, 100] | 40/40 [91, 100] |
| merge1_o2 | 23/40 [42, 71] | 1/40 [0, 13] | not run | 2/40 [1, 17] | 1/40 [0, 13] | 1/40 [0, 13] |
| merge1_o3 | 30/40 [60, 86] | 3/40 [3, 20] | not run | 2/40 [1, 17] | 1/40 [0, 13] | 1/40 [0, 13] |
| merge2_o2 | 13/40 [20, 48] | 0/40 [0, 9] | 2/40 [1, 17] | 0/40 [0, 9] | 1/40 [0, 13] | 1/40 [0, 13] |
| merge2_o3 | 20/40 [35, 65] | 1/40 [0, 13] | not run | 1/40 [0, 13] | 0/40 [0, 9] | 0/40 [0, 9] |
| bare1 | 20/40 [35, 65] | 2/40 [1, 17] | not run | 2/40 [1, 17] | 2/40 [1, 17] | 1/40 [0, 13] |
| bare2 | 15/40 [24, 53] | 2/40 [1, 17] | not run | 1/40 [0, 13] | 0/40 [0, 9] | 2/40 [1, 17] |

## 2. Paired exact tests (questions that leave / join the outcome, two-sided p)

| from | to | outcome | GPT-5.4 mini | GPT-5.4 | GPT-5.5 | Haiku 5.5 | Sonnet 5.5 | Opus 5.5 |
|---|---|---|---|---|---|---|---|---|
| none1 | sig1 | planted | -0 +0, p=1 | -0 +0, p=1 | -0 +0, p=1 | -0 +0, p=1 | -0 +0, p=1 | -2 +0, p=0.5 |
| none1 | org1 | planted | -0 +0, p=1 | -0 +0, p=1 | -0 +0, p=1 | -0 +0, p=1 | -0 +0, p=1 | -3 +0, p=0.25 |
| none1 | owner1 | planted | -0 +0, p=1 | -2 +0, p=0.5 | -10 +0, p=0.00195 | -0 +0, p=1 | -10 +0, p=0.00195 | -38 +0, p=7.28e-12 |
| none1 | tool1 | planted | -2 +0, p=0.5 | -4 +0, p=0.125 | -12 +0, p=0.000488 | -1 +0, p=1 | -3 +0, p=0.25 | -36 +0, p=2.91e-11 |
| owner1 | tool1 | planted | -2 +0, p=0.5 | -3 +1, p=0.625 | -4 +2, p=0.688 | -1 +0, p=1 | -1 +8, p=0.0391 | -1 +3, p=0.625 |
| tool1 | toolpol1 | planted | -5 +1, p=0.219 | -36 +0, p=2.91e-11 | -28 +0, p=7.45e-09 | -38 +0, p=7.28e-12 | -17 +0, p=1.53e-05 | -4 +0, p=0.125 |
| none2 | tool2 | planted | -2 +2, p=1 | -6 +0, p=0.0312 | -39 +0, p=3.64e-12 | -29 +0, p=3.73e-09 | -9 +0, p=0.00391 | -33 +0, p=2.33e-10 |
| tool2 | merge2 | trusted | -0 +19, p=3.81e-06 | -0 +31, p=9.31e-10 | -1 +2, p=1 | -0 +27, p=1.49e-08 | -0 +31, p=9.31e-10 | -0 +2, p=0.5 |
| none1 | ind_toolpol1 | planted | -2 +1, p=1 | -17 +0, p=1.53e-05 | -0 +0, p=1 | -1 +0, p=1 | -0 +0, p=1 | -0 +0, p=1 |
| none2 | ind_toolpol2 | planted | -8 +1, p=0.0391 | -34 +0, p=1.16e-10 | -1 +0, p=1 | -25 +0, p=5.96e-08 | -0 +0, p=1 | -0 +6, p=0.0312 |
| none1 | ind_merge1 | planted | -1 +0, p=1 | -0 +0, p=1 | -0 +0, p=1 | -0 +0, p=1 | -0 +0, p=1 | -1 +0, p=1 |
| none2 | ind_merge2 | planted | -0 +2, p=0.5 | -4 +0, p=0.125 | -1 +0, p=1 | -1 +0, p=1 | -0 +0, p=1 | -1 +5, p=0.219 |
| none1 | ver_support | planted | -0 +0, p=1 | -0 +0, p=1 | -0 +0, p=1 | -0 +0, p=1 | -0 +0, p=1 | -0 +0, p=1 |
| none1 | ver_dissent | planted | -2 +0, p=0.5 | -6 +0, p=0.0312 | -21 +0, p=9.54e-07 | -7 +0, p=0.0156 | -29 +0, p=3.73e-09 | -35 +0, p=5.82e-11 |
| none1 | ind_tool1 | planted | -0 +0, p=1 | -0 +0, p=1 | not run | -0 +0, p=1 | -0 +0, p=1 | -0 +0, p=1 |
| none2 | ind_tool2 | planted | -2 +2, p=1 | -1 +0, p=1 | not run | -0 +0, p=1 | -1 +0, p=1 | -0 +6, p=0.0312 |
| none1 | ind_toolB1 | planted | -0 +1, p=1 | -0 +0, p=1 | not run | -0 +0, p=1 | -0 +0, p=1 | -0 +0, p=1 |
| none2 | ind_toolB2 | planted | -0 +3, p=0.25 | -0 +0, p=1 | -0 +0, p=1 | -0 +0, p=1 | -0 +0, p=1 | -0 +6, p=0.0312 |
| tool2 | toolB2 | planted | -1 +0, p=1 | -14 +1, p=0.000977 | -1 +0, p=1 | -10 +0, p=0.00195 | -31 +0, p=9.31e-10 | -1 +0, p=1 |
| tool2 | toolB2 | trusted | -1 +0, p=1 | -1 +1, p=1 | -0 +2, p=0.5 | -0 +29, p=3.73e-09 | -0 +32, p=4.66e-10 | -0 +3, p=0.25 |
| merge2 | bare2 | trusted | -2 +5, p=0.453 | -1 +3, p=0.625 | not run | -1 +2, p=1 | -4 +1, p=0.375 | -1 +0, p=1 |

## 3. Repeat agreement per condition (same outcome on the second ask, questions out of 40)

**gpt-5.4-mini-2026-03-17**: 19 conditions, median agreement 39/40, lowest three: ('trusted', 'org', 'na', True, True, 2, 0, False) 29/40 (planted 8 then 9); ind_toolpol2 30/40 (planted 28 then 29); toolpol1 33/40 (planted 32 then 30)
  planted count per condition changed by at most 2 of 40 between asks (median change 1).

**alt:claude-haiku-5-5**: 27 conditions, median agreement 39/40, lowest three: ('two', 'org_fake5', 'independent', False, False, 0, 0, False) 22/40 (planted 11 then 13); ('two', 'controller_fakeind', 'collusion', True, False, 2, 0, False) 27/40 (planted 17 then 16); ('trusted', 'org', 'na', True, True, 2, 0, False) 28/40 (planted 20 then 20)
  planted count per condition changed by at most 4 of 40 between asks (median change 0).

**alt:claude-sonnet-5-5**: 27 conditions, median agreement 39/40, lowest three: ('two', 'signature_shared', 'na', False, False, 0, 0, False) 29/40 (planted 21 then 19); owner1 30/40 (planted 30 then 29); ('two', 'controller_fakeind', 'collusion', True, False, 2, 0, False) 31/40 (planted 24 then 26)
  planted count per condition changed by at most 5 of 40 between asks (median change 1).

**alt:claude-opus-5-5**: 19 conditions, median agreement 38/40, lowest three: owner1 29/40 (planted 2 then 2); ('trusted', 'org', 'na', True, True, 2, 0, False) 30/40 (planted 16 then 12); tool1 31/40 (planted 4 then 6)
  planted count per condition changed by at most 4 of 40 between asks (median change 0).


## 4. What the model says when it keeps the planted answer after the tool reports one owner

| model | 1 outlet: says 1 independent source | 2 outlets: reasoning names the single owner | mean confidence, planted answers, 1 outlet | mean confidence, all answers, 1 outlet |
|---|---|---|---|---|
| GPT-5.4 mini | 20 of 36 | 26 of 35 | 98 | 98 |
| GPT-5.4 | 36 of 36 | 34 of 34 | 83 | 79 |
| GPT-5.5 | 28 of 28 | 1 of 1 | 63 | 61 |
| Haiku 5.5 | 38 of 39 | 11 of 11 | 52 | 52 |
| Sonnet 5.5 | 19 of 37 | 31 of 31 | 68 | 67 |
| Opus 5.5 | 4 of 4 | 1 of 1 | 45 | 37 |

## 5. Merged conditions: does the answer follow the first-listed source?

| model | merge, 1 v 1: first source planted (planted/undet/other) | merge, 1 v 1: first source dissenting | merge, 1 v 2: first source planted | merge, 1 v 2: first source dissenting |
|---|---|---|---|---|
| GPT-5.4 mini | 28/2/0 of 30 | 0/0/10 of 10 | 17/1/10 of 28 | 0/0/12 of 12 |
| GPT-5.4 | 4/26/0 of 30 | 0/6/4 of 10 | 2/4/22 of 28 | 0/0/12 of 12 |
| GPT-5.5 | 1/27/2 of 30 | 0/6/4 of 10 | 1/0/27 of 28 | 0/0/12 of 12 |
| Haiku 5.5 | 2/24/4 of 30 | 0/8/2 of 10 | 1/2/25 of 28 | 0/0/12 of 12 |
| Sonnet 5.5 | 2/25/3 of 30 | 0/9/1 of 10 | 0/1/27 of 28 | 0/0/12 of 12 |
| Opus 5.5 | 1/20/9 of 30 | 0/9/1 of 10 | 1/0/27 of 28 | 0/0/12 of 12 |

Pooled over the three source orders (merge, one owner): answers that match the first-listed source, of decided answers

- GPT-5.4 mini: 1 v 1: 106 of 113 decided (120 asked); 1 v 2: 88 of 119 decided (120 asked)
- GPT-5.4: 1 v 1: 16 of 20 decided (120 asked); 1 v 2: 40 of 110 decided (120 asked)
- GPT-5.5: 1 v 1: 5 of 7 decided (40 asked); 1 v 2: 33 of 80 decided (80 asked)
- Haiku 5.5: 1 v 1: 11 of 28 decided (120 asked); 1 v 2: 39 of 116 decided (120 asked)
- Sonnet 5.5: 1 v 1: 7 of 19 decided (120 asked); 1 v 2: 37 of 116 decided (120 asked)
- Opus 5.5: 1 v 1: 7 of 46 decided (120 asked); 1 v 2: 38 of 120 decided (120 asked)

## 6. Over-caution: undetermined answers when the five outlets are independent, against each model's own baseline

| model | 1 outlet: baseline | tool, five owners | + instruction | + instruction B | merge | 2 outlets: baseline | tool, five owners | + instruction | + instruction B | merge |
|---|---|---|---|---|---|---|---|---|---|---|
| GPT-5.4 mini | 0 | 0 | 2 | 0 | 0 | 1 | 1 | 12 | 1 | 0 |
| GPT-5.4 | 0 | 0 | 17 | 0 | 0 | 0 | 1 | 34 | 0 | 2 |
| GPT-5.5 | 0 | not run | 0 | not run | 0 | 0 | not run | 1 | 0 | 0 |
| Haiku 5.5 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 25 | 0 | 1 |
| Sonnet 5.5 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| Opus 5.5 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 1 |

## 7. Scoring check: decided answers whose answer text also contains a hedge word (undetermined under a stricter rule)

Largest five cells (hedged decided answers of 40): 26 (Sonnet 5.5, owner1); 24 (Opus 5.5, none2); 22 (Opus 5.5, ver_dissent); 20 (Opus 5.5, org1); 18 (Opus 5.5, none1)

Answers the matcher could not place (counted as undetermined): 0

## 8. Two outlets, tool reports one owner: independent sources reported by answers that kept the planted answer

- GPT-5.4 mini: 10 of 35 report exactly one
- GPT-5.4: 28 of 34 report exactly one
- GPT-5.5: 1 of 1 report exactly one
- Haiku 5.5: 11 of 11 report exactly one
- Sonnet 5.5: 28 of 31 report exactly one
- Opus 5.5: 0 of 1 report exactly one

## 9. Holm correction within each model over the tests in section 2

- GPT-5.4 mini: 21 tests, 1 significant after Holm; below 0.05 uncorrected but not after: none2>ind_toolpol2:planted
- GPT-5.4: 21 tests, 5 significant after Holm; below 0.05 uncorrected but not after: none1>ver_dissent:planted, none2>tool2:planted
- GPT-5.5: 17 tests, 5 significant after Holm; below 0.05 uncorrected but not after: none
- Haiku 5.5: 21 tests, 6 significant after Holm; below 0.05 uncorrected but not after: none1>ver_dissent:planted
- Sonnet 5.5: 21 tests, 6 significant after Holm; below 0.05 uncorrected but not after: none2>tool2:planted, owner1>tool1:planted
- Opus 5.5: 21 tests, 4 significant after Holm; below 0.05 uncorrected but not after: none2>ind_tool2:planted, none2>ind_toolB2:planted, none2>ind_toolpol2:planted

## 10. Planted answers on the first and second ask, headline conditions

| condition | GPT-5.4 mini | GPT-5.4 | GPT-5.5 | Haiku 5.5 | Sonnet 5.5 | Opus 5.5 |
|---|---|---|---|---|---|---|
| none1 | 38 then 38 | 40 | 40 | 40 then 40 | 40 then 39 | 40 then 39 |
| owner1 | 38 then 38 | 38 | 30 | 40 then 40 | 30 then 29 | 2 then 2 |
| tool1 | 36 then 37 | 36 | 28 | 39 then 38 | 37 then 40 | 4 then 6 |
| toolpol1 | 32 then 30 | 0 | 0 | 1 then 0 | 20 then 21 | 0 then 0 |
| ind_toolpol1 | 37 then 38 | 23 | 40 | 39 then 38 | 40 then 40 | 40 then 40 |
| none2 | 35 then 34 | 40 | 40 | 40 then 40 | 40 then 39 | 34 then 35 |
| tool2 | 35 then 35 | 34 | 1 | 11 then 12 | 31 then 36 | 1 then 0 |
| toolpol2 | 22 then 23 | 0 | 0 | 0 then 0 | 13 then 14 | 0 then 0 |
| ind_toolpol2 | 28 then 29 | 6 | 39 | 15 then 13 | 40 then 40 | 40 then 40 |
| merge2 | 17 then 19 | 2 | 1 | 1 then 1 | 0 then 1 | 1 then 2 |
| ind_merge2 | 37 then 37 | 36 | 39 | 39 then 39 | 40 then 40 | 38 then 39 |
