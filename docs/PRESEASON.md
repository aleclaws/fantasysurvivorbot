# Pre-season board

Generated before the premiere. No episode has aired. Re-run
`python3 -m fsb board` after episode 1 - real edit signals should always
win over anything on this page.

## How draft value works under the real rules

Each player drafts **2** castaways in an exclusive snake draft (two
rounds, random order, run automatically on Sep 23 at 8:00 PM EDT from
each player's preference order). See `docs/RULES.md`.

A drafted castaway earns points per named action while in the game, and
**1 point per episode after leaving** (the standings "Out" column). So an
early boot still banks about 13 points. An episode in the game is worth
only its gameplay points minus the 1 point the castaway would earn anyway
once out:

- **Before the merge** the margin is large: tribe challenge points go to
  every member of the winning tribe.
- **After the merge** it is small: one individual winner per challenge.

So draft value is mostly "reaches the merge", and the board is compressed:
the top ten are within about 2 points. **The weekly vote, not the draft,
decides this league** - one correct all-in is worth 10.

The hazard model blends three weak priors: a read from age and
occupation; `preseason_buzz`, cited pundit predictions (`data/priors.json`);
and event-frequency assumptions in `data/priors.json` -> `draft_model`,
all confidence low. **No Survivor 51 prediction-market odds exist yet**
(Polymarket and Kalshi checked), and there is no screen time to analyse
before the season airs.

## Draft board

Ranked by expected points as a draft pick. `P(merge)` is the chance of
reaching the merge; `Eps` is expected episodes in the game (of 13).

| # | Castaway | Age | Occupation | E[pts] | P(merge) | Eps | P(win) |
|---|---|---|---|---|---|---|---|
| 1 | Ori Jean-Charles | 27 | Personal trainer | 29.9 | 0.73 | 9.1 | 0.040 |
| 2 | Brady Booker | 27 | Professional wrestler | 29.6 | 0.70 | 8.7 | 0.018 |
| 3 | Carter Krull | 24 | Livestock farmer | 28.8 | 0.66 | 8.7 | 0.031 |
| 4 | Devin Way | 33 | Actor | 28.7 | 0.66 | 9.0 | 0.075 |
| 5 | Lewis Kelly | 28 | Farmer | 28.6 | 0.65 | 8.6 | 0.035 |
| 6 | Eric Macksoud | 34 | Mental health counselor | 28.4 | 0.64 | 8.9 | 0.090 |
| 7 | Patt Cannaday | 33 | Navy attorney / federal prosecutor | 28.1 | 0.64 | 8.6 | 0.041 |
| 8 | Sharonda Cox | 34 | OB-GYN resident physician | 27.9 | 0.64 | 8.8 | 0.083 |
| 9 | Angelica "Jelly" Loblack | 29 | Sociology professor | 27.7 | 0.60 | 8.4 | 0.049 |
| 10 | Aaliyah Puglia | 24 | Chef | 27.3 | 0.60 | 8.6 | 0.063 |
| 11 | Mike Pinsky | 32 | Asst. director, baseball ops | 27.1 | 0.58 | 8.1 | 0.030 |
| 12 | Cristian Chavez | 25 | Human resources | 27.1 | 0.58 | 8.3 | 0.065 |
| 13 | Alexis Levine | 34 | Criminal defense attorney | 26.9 | 0.56 | 8.1 | 0.040 |
| 14 | Ana Sani | 34 | Voice actor | 26.8 | 0.57 | 8.3 | 0.074 |
| 15 | Jenna Doore | 30 | Wedding photographer | 26.6 | 0.55 | 8.1 | 0.059 |
| 16 | Linnea Capobianco | 25 | Entrepreneur | 26.3 | 0.53 | 7.9 | 0.042 |
| 17 | Maggie Nestor | 40 | Farmer | 26.3 | 0.51 | 7.6 | 0.039 |
| 18 | Danny "Kilby" Kilby | 30 | Game designer | 26.3 | 0.55 | 8.0 | 0.035 |
| 19 | An "Thien An" Nguyen | 24 | Medical student | 25.9 | 0.50 | 7.6 | 0.039 |
| 20 | Rob Antonson | 40 | Airline gate agent | 24.7 | 0.41 | 7.0 | 0.041 |
| 21 | Kristin Flickinger | 49 | Crisis management | 21.2 | 0.13 | 4.4 | 0.010 |

Submitted to the site as the full 21-name preference order on 2026-09-18
via `tools/submit.py draft`, and verified against a fresh read of the page.
Ranking by your own value is the right way to fill a preference list for
an exclusive snake draft: you cannot influence what others take, and the
two picks' values add.

## Sole Survivor pick

**Eric Macksoud** — P(win) 0.090

The bonus pays 1 point per consecutive episode, counted back from the
final, that you hold the eventual winner - up to 13 points if held from
week one. There is no payout for second or third. **You may change this
pick at any time for free.** Re-run `python3 -m fsb mvp` whenever the
standings or edit signals move. The Sole Survivor bonus is a separate
choice from the draft and is not part of the draft value above.

Submitted and verified live on 2026-09-17 via
`tools/submit.py sole-survivor eric`.

| Castaway | P(win) | Draft rank |
|---|---|---|
| Eric Macksoud | 0.090 | 6 |
| Sharonda Cox | 0.083 | 8 |
| Devin Way | 0.075 | 4 |
| Ana Sani | 0.074 | 14 |
| Cristian Chavez | 0.065 | 12 |

## Warning

The tribe rosters were not public before the premiere. The engine prices
all 21 castaways as one pool, which is also how the site's episode 1 vote
page groups them. From episode 2, `tools/submit.py vote` reads the real
tribes off the site's vote page.

`preseason_buzz` and `draft_model` are opinion and assumption, not
knowledge. Once episodes 1-2 are scored, calibrate `draft_model` against
the standings "Survivor" column - it is exactly the points each player's
two drafted castaways earned.
