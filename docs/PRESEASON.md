# Pre-season board

Generated before the premiere. No episode has aired. Re-run
`python3 -m fsb board` after episode 1 - real edit signals should always
win over anything on this page.

`E[pts]` uses the real scoring constants read from the site on 2026-09-17
(see `docs/RULES.md`). The hazard model blends three kinds of prior, all
weak on their own:

- `phys`/`social`/`threat` - a subjective read from age and occupation only.
- `preseason_buzz` - cited, dated pre-season predictions (not a guess) from
  Idol Speculation's 2026-08-28 full-cast assessment and a Yahoo piece on
  historical winner occupations, checked 2026-09-17. Capped at +-0.30 and
  weighted below the in-season `edit` signal on purpose - see
  `data/priors.json`. **No Survivor 51 prediction-market odds exist yet**:
  Polymarket and Kalshi were checked directly and only have markets for
  already-aired seasons (48-50), not 51. Screen-time analysis is not
  possible before the season airs - there is no screen time yet.

Draft roster size: confirmed at **3** (`docs/RULES.md`). It is a
preference order over all 21, not a direct pick.

## Draft board

Draft from the top. The engine values survival time, because the league
pays for each week a castaway stays in the game, plus a smaller trickle
after elimination (`docs/RULES.md` - that trickle is one of two facts
still unconfirmed against a real scored episode).

| # | Castaway | Age | Occupation | E[pts] | P(win) | Weeks |
|---|---|---|---|---|---|---|
| 1 | Brady Booker | 27 | Professional wrestler | 29.3 | 0.018 | 11.6 |
| 2 | Ori Jean-Charles | 27 | Personal trainer | 28.9 | 0.040 | 12.3 |
| 3 | Carter Krull | 24 | Livestock farmer | 27.0 | 0.031 | 11.7 |
| 4 | Lewis Kelly | 28 | Farmer | 25.9 | 0.035 | 11.6 |
| 5 | Maggie Nestor | 40 | Farmer | 21.7 | 0.039 | 10.1 |
| 6 | Patt Cannaday | 33 | Navy attorney / federal prosecutor | 21.4 | 0.041 | 11.5 |
| 7 | Devin Way | 33 | Actor | 21.0 | 0.075 | 12.3 |
| 8 | Aaliyah Puglia | 24 | Chef | 20.4 | 0.063 | 11.6 |
| 9 | Eric Macksoud | 34 | Mental health counselor | 20.0 | 0.090 | 12.2 |
| 10 | Mike Pinsky | 32 | Asst. director, baseball ops | 19.9 | 0.030 | 10.8 |
| 11 | Sharonda Cox | 34 | OB-GYN resident physician | 19.8 | 0.083 | 12.1 |
| 12 | Cristian Chavez | 25 | Human resources | 19.3 | 0.065 | 11.3 |
| 13 | Angelica "Jelly" Loblack | 29 | Sociology professor | 18.2 | 0.049 | 11.4 |
| 14 | Jenna Doore | 30 | Wedding photographer | 18.1 | 0.059 | 10.9 |
| 15 | Alexis Levine | 34 | Criminal defense attorney | 17.9 | 0.040 | 10.9 |
| 16 | Linnea Capobianco | 25 | Entrepreneur | 17.8 | 0.042 | 10.5 |
| 17 | Danny "Kilby" Kilby | 30 | Game designer | 17.6 | 0.035 | 10.6 |
| 18 | An "Thien An" Nguyen | 24 | Medical student | 17.6 | 0.039 | 10.2 |
| 19 | Ana Sani | 34 | Voice actor | 17.3 | 0.074 | 11.3 |
| 20 | Rob Antonson | 40 | Airline gate agent | 16.5 | 0.041 | 9.4 |
| 21 | Kristin Flickinger | 49 | Crisis management | 14.2 | 0.010 | 5.5 |

Submitted to the site as a full 21-name preference order on 2026-09-17 via
`tools/submit.py draft`, and verified against a fresh read of the page.

## Sole Survivor pick

**Eric Macksoud** — P(win) 0.090

The bonus pays 1 point per consecutive episode, counted back from the
final, that you hold the eventual winner as your pick — up to 13 points if
held from week one. There is no separate payout for second or third place.
**You may change this pick at any time for free.** Re-run
`python3 -m fsb mvp` whenever the standings or edit signals move, and
switch the moment a clearly stronger candidate emerges — see
`docs/RULES.md`.

Submitted and verified live on 2026-09-17 via
`tools/submit.py sole-survivor eric`.

Top five by win probability:

| Castaway | P(win) | Draft rank |
|---|---|---|
| Eric Macksoud | 0.090 | 9 |
| Devin Way | 0.075 | 7 |
| Sharonda Cox | 0.083 | 11 |
| Ana Sani | 0.074 | 19 |
| Aaliyah Puglia | 0.063 | 8 |

Eric held the top spot both before and after adding the pre-season buzz
signal - the margin over the field widened slightly rather than flipping,
so no reason to change it. Aaliyah, Devin, and Sharonda all moved up on
buzz (Idol Speculation's winner/dark-horse picks), which narrowed the gap
without closing it.

Note the gap between the draft board and this list. The draft leaders are
physical players. They last a long time before the merge. Then they
become targets. The win-probability leaders are social players. Draft the
first group for points. Pick your MVP from the second group.

## Warning

The tribe rosters were not public before the premiere. The engine prices
all 21 castaways as one pool. The pre-merge numbers are therefore wrong.
Add the tribes after episode 1:

```
python3 -m fsb tribe <name> Savu
```

`preseason_buzz` is one blogger's opinion plus one historical-occupation
stat, not knowledge - it is deliberately capped and under-weighted so real
edit signals take over cleanly after episode 1. The out-of-game point rule
is also unconfirmed - see `docs/RULES.md`.
