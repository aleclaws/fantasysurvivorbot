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
occupation; `preseason_buzz`, which averages two cited pundit assessments
(Idol Speculation and Inside Survivor) plus an occupation base rate, so
one blogger cannot drive the model and disagreement shrinks the signal;
and event-frequency assumptions in `data/priors.json` -> `draft_model`,
all confidence low. **No Survivor 51 prediction-market odds exist yet**
(Polymarket and Kalshi checked), and there is no screen time to analyse
before the season airs.

**Tribe rosters are still not public** as of 2026-09-22, checked against
CBS reporting, Wikipedia and the site itself - so neither the draft nor
the episode 1 vote can use them. CBS's teaser does confirm the buffs are
pre-assigned and that "one of you will not begin the game with the
others": 21 splits into two tribes plus one castaway held out somehow.

## Draft board

Ranked by expected points as a draft pick. `P(merge)` is the chance of
reaching the merge; `Eps` is expected episodes in the game (of 13).

| # | Castaway | Age | Occupation | E[pts] | P(merge) | Eps | P(win) |
|---|---|---|---|---|---|---|---|
| 1 | Ori Jean-Charles | 27 | Personal trainer | 29.9 | 0.72 | 9.1 | 0.038 |
| 2 | Brady Booker | 27 | Professional wrestler | 29.5 | 0.70 | 8.7 | 0.017 |
| 3 | Carter Krull | 24 | Livestock farmer | 28.9 | 0.67 | 8.8 | 0.034 |
| 4 | Devin Way | 33 | Actor | 28.6 | 0.66 | 9.0 | 0.072 |
| 5 | Lewis Kelly | 28 | Farmer | 28.4 | 0.64 | 8.5 | 0.032 |
| 6 | Eric Macksoud | 34 | Mental health counselor | 28.3 | 0.64 | 8.9 | 0.089 |
| 7 | Patt Cannaday | 33 | Navy attorney / federal prosecutor | 28.1 | 0.64 | 8.5 | 0.040 |
| 8 | Angelica "Jelly" Loblack | 29 | Sociology professor | 27.9 | 0.62 | 8.6 | 0.058 |
| 9 | Sharonda Cox | 34 | OB-GYN resident physician | 27.7 | 0.62 | 8.7 | 0.079 |
| 10 | Mike Pinsky | 32 | Asst. director, baseball ops | 27.3 | 0.59 | 8.2 | 0.035 |
| 11 | Aaliyah Puglia | 24 | Chef | 27.2 | 0.60 | 8.5 | 0.060 |
| 12 | Alexis Levine | 34 | Criminal defense attorney | 27.1 | 0.58 | 8.3 | 0.049 |
| 13 | Cristian Chavez | 25 | Human resources | 27.0 | 0.57 | 8.2 | 0.058 |
| 14 | Ana Sani | 34 | Voice actor | 26.8 | 0.57 | 8.3 | 0.071 |
| 15 | Jenna Doore | 30 | Wedding photographer | 26.8 | 0.56 | 8.3 | 0.065 |
| 16 | Linnea Capobianco | 25 | Entrepreneur | 26.3 | 0.52 | 7.8 | 0.040 |
| 17 | Danny "Kilby" Kilby | 30 | Game designer | 26.2 | 0.54 | 7.9 | 0.035 |
| 18 | Maggie Nestor | 40 | Farmer | 26.2 | 0.49 | 7.5 | 0.035 |
| 19 | An "Thien An" Nguyen | 24 | Medical student | 26.0 | 0.52 | 7.8 | 0.044 |
| 20 | Rob Antonson | 40 | Airline gate agent | 24.7 | 0.40 | 7.0 | 0.040 |
| 21 | Kristin Flickinger | 49 | Crisis management | 21.2 | 0.13 | 4.4 | 0.009 |

Submitted to the site as the full 21-name preference order on 2026-09-22
via `tools/submit.py draft`, and verified against a fresh read of the page.
Ranking by your own value is the right way to fill a preference list for
an exclusive snake draft: you cannot influence what others take, and the
two picks' values add.

## Sole Survivor pick

**Eric Macksoud** — P(win) 0.089

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
| Eric Macksoud | 0.089 | 6 |
| Sharonda Cox | 0.079 | 9 |
| Devin Way | 0.072 | 4 |
| Ana Sani | 0.071 | 14 |
| Jenna Doore | 0.065 | 15 |

## Warning

The tribe rosters were not public before the premiere. The engine prices
all 21 castaways as one pool, which is also how the site's episode 1 vote
page groups them. From episode 2, `tools/submit.py vote` reads the real
tribes off the site's vote page.

`preseason_buzz` and `draft_model` are opinion and assumption, not
knowledge. Once episodes 1-2 are scored, calibrate `draft_model` against
the standings "Survivor" column - it is exactly the points each player's
two drafted castaways earned.
