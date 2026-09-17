# Pre-season board

Generated before the premiere, from bios only. No episode has aired.
These priors are weak. Re-run `python3 -m fsb board` after episode 1.

`E[pts]` uses the real scoring constants read from the site on 2026-09-17
(see `docs/RULES.md`), not the earlier guess. It is lower than an earlier
version of this table because the real Sole Survivor bonus tops out at 13
points on a streak, not a flat 30-point placement payout.

## Draft board

Draft from the top. The engine values survival time, because the
league pays for each week a castaway stays in the game, plus a smaller
trickle after elimination (see `docs/RULES.md` — that trickle is one of
the two facts still unconfirmed against a real scored episode).

| # | Castaway | Age | Occupation | E[pts] | P(win) | Weeks |
|---|---|---|---|---|---|---|
| 1 | Brady Booker | 27 | Professional wrestler | 29.5 | 0.021 | 11.9 |
| 2 | Ori Jean-Charles | 27 | Personal trainer | 28.6 | 0.033 | 12.0 |
| 3 | Carter Krull | 24 | Livestock farmer | 26.9 | 0.028 | 11.5 |
| 4 | Lewis Kelly | 28 | Farmer | 26.1 | 0.042 | 11.8 |
| 5 | Maggie Nestor | 40 | Farmer | 21.8 | 0.046 | 10.4 |
| 6 | Patt Cannaday | 33 | Navy attorney / federal prosecutor | 21.2 | 0.032 | 11.2 |
| 7 | Devin Way | 33 | Actor | 20.7 | 0.061 | 11.8 |
| 8 | Aaliyah Puglia | 24 | Chef | 20.0 | 0.046 | 10.9 |
| 9 | Eric Macksoud | 34 | Mental health counselor | 19.9 | 0.085 | 12.1 |
| 10 | Mike Pinsky | 32 | Asst. director, baseball ops | 19.9 | 0.033 | 10.9 |
| 11 | Sharonda Cox | 34 | OB-GYN resident physician | 19.5 | 0.067 | 11.6 |
| 12 | Cristian Chavez | 25 | Human resources | 19.3 | 0.065 | 11.4 |
| 13 | Angelica "Jelly" Loblack | 29 | Sociology professor | 18.3 | 0.056 | 11.6 |
| 14 | Jenna Doore | 30 | Wedding photographer | 18.2 | 0.069 | 11.3 |
| 15 | Linnea Capobianco | 25 | Entrepreneur | 18.1 | 0.058 | 11.1 |
| 16 | Alexis Levine | 34 | Criminal defense attorney | 18.0 | 0.047 | 11.1 |
| 17 | An "Thien An" Nguyen | 24 | Medical student | 17.7 | 0.045 | 10.4 |
| 18 | Danny "Kilby" Kilby | 30 | Game designer | 17.6 | 0.034 | 10.5 |
| 19 | Ana Sani | 34 | Voice actor | 17.2 | 0.072 | 11.2 |
| 20 | Rob Antonson | 40 | Airline gate agent | 16.6 | 0.049 | 9.6 |
| 21 | Kristin Flickinger | 49 | Crisis management | 14.2 | 0.011 | 5.7 |

Draft roster size is not yet confirmed — `docs/RULES.md` question 1. Take
the top of this list up to whatever size the site's draft page shows.

## Sole Survivor pick

**Eric Macksoud** — P(win) 0.085

The bonus pays 1 point per consecutive episode, counted back from the
final, that you hold the eventual winner as your pick — up to 13 points if
held from week one. There is no separate payout for second or third place.
So this pick maximises P(win), same as before, but the underlying reward
is a streak, not a one-time placement bonus, and **you may change this pick
at any time for free**. Re-run `python3 -m fsb mvp` whenever the standings
or edit signals move, and switch the moment a clearly stronger candidate
emerges — see `docs/RULES.md`.

Top five by win probability:

| Castaway | P(win) | Draft rank |
|---|---|---|
| Eric Macksoud | 0.085 | 9 |
| Ana Sani | 0.072 | 19 |
| Jenna Doore | 0.069 | 14 |
| Sharonda Cox | 0.067 | 11 |
| Cristian Chavez | 0.065 | 12 |

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

Draft roster size and the out-of-game point rule are also unconfirmed —
see the open items in `docs/RULES.md`. Correct `data/scoring.json` again
once a real, signed-in session can read the account and draft pages.
