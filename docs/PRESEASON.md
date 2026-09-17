# Pre-season board

Generated before the premiere, from bios only. No episode has aired.
These priors are weak. Re-run `python3 -m fsb board` after episode 1.

## Draft board

Draft from the top. The engine values survival time, because the
league pays for each week a castaway stays in the game.

| # | Castaway | Age | Occupation | E[pts] | P(win) | Weeks |
|---|---|---|---|---|---|---|
| 1 | Brady Booker | 27 | Professional wrestler | 46 | 0.021 | 11.9 |
| 2 | Ori Jean-Charles | 27 | Personal trainer | 46 | 0.033 | 12.0 |
| 3 | Lewis Kelly | 28 | Farmer | 43 | 0.042 | 11.8 |
| 4 | Carter Krull | 24 | Livestock farmer | 42 | 0.028 | 11.5 |
| 5 | Eric Macksoud | 34 | Mental health counselor | 38 | 0.085 | 12.1 |
| 6 | Devin Way | 33 | Actor | 38 | 0.061 | 11.8 |
| 7 | Sharonda Cox | 34 | OB-GYN resident physician | 36 | 0.067 | 11.6 |
| 8 | Patt Cannaday | 33 | Navy attorney / federal prosecutor | 36 | 0.032 | 11.2 |
| 9 | Cristian Chavez | 25 | Human resources | 35 | 0.065 | 11.4 |
| 10 | Maggie Nestor | 40 | Farmer | 35 | 0.046 | 10.4 |
| 11 | Angelica "Jelly" Loblack | 29 | Sociology professor | 34 | 0.056 | 11.6 |
| 12 | Jenna Doore | 30 | Wedding photographer | 34 | 0.069 | 11.3 |
| 13 | Aaliyah Puglia | 24 | Chef | 34 | 0.046 | 10.9 |
| 14 | Mike Pinsky | 32 | Asst. director, baseball ops | 33 | 0.033 | 10.9 |
| 15 | Linnea Capobianco | 25 | Entrepreneur | 33 | 0.058 | 11.1 |
| 16 | Ana Sani | 34 | Voice actor | 33 | 0.072 | 11.2 |
| 17 | Alexis Levine | 34 | Criminal defense attorney | 32 | 0.047 | 11.1 |
| 18 | An "Thien An" Nguyen | 24 | Medical student | 30 | 0.045 | 10.4 |
| 19 | Danny "Kilby" Kilby | 30 | Game designer | 30 | 0.034 | 10.5 |
| 20 | Rob Antonson | 40 | Airline gate agent | 27 | 0.049 | 9.6 |
| 21 | Kristin Flickinger | 49 | Crisis management | 13 | 0.011 | 5.7 |

## Sole Survivor pick

**Eric Macksoud** — P(win) 0.085

The bonus pays only for an outright win. So this pick maximises the
probability of a win. It does not maximise points.

Top five by win probability:

| Castaway | P(win) | Draft rank |
|---|---|---|
| Eric Macksoud | 0.085 | 5 |
| Ana Sani | 0.072 | 16 |
| Jenna Doore | 0.069 | 12 |
| Sharonda Cox | 0.067 | 7 |
| Cristian Chavez | 0.065 | 9 |

Note the gap between the two lists. The draft leaders are physical
players. They last a long time before the merge. Then they become
targets. The win-probability leaders are social players. Draft the
first group for points. Pick your MVP from the second group.

## Warning

The tribe rosters were not public before the premiere. The engine
prices all 21 castaways as one pool. The pre-merge numbers are
therefore wrong. Add the tribes after episode 1:

```
python3 -m fsb tribe <name> Savu
```
