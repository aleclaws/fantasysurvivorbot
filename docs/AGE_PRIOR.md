# The age prior, measured at last

`weights.premerge.age` is 1.1, the third largest weight in the model, and
these notes twice recorded that no base-rate data could be found for it.
Data was found on 2026-09-29. It does not support the weight, and it does
not support the shape of the function either.

## What the code claims

`fsb/model.py`, `age_risk`:

> New-era Survivor culls the oldest member of a losing tribe early and
> often; the effect is mild until the late 30s and then climbs fast.

The function rises from 0 at age 37 and saturates at 1.0 by 52:

| age | 30 | 35 | 40 | 45 | **49** | 52 | 58 |
|---|---|---|---|---|---|---|---|
| `age_risk` | 0.00 | 0.00 | 0.23 | 0.62 | **0.92** | 1.00 | 1.00 |

Kristin Flickinger is 49. The next oldest castaway alive is 40. So this one
term puts about +1.0 of hazard on one castaway and almost nothing on anyone
else.

## What the record says

Every new-era season, 41 to 49, from the Wikipedia contestant tables, which
list each cast in elimination order. S50 is excluded throughout: it is a
returnee season of 24 with an older skew. The data is saved in
`data/newera_boots.json` so that this does not need gathering twice.

**Claim 1 — the oldest player is culled early. This is false.**

| Season | Oldest | Finished |
|---|---|---|
| 41 | Heather, 52 | 15th of 18 |
| 42 | Mike, 58 | 17th of 18 |
| 43 | Mike Gabler, 51 | **won** |
| 44 | Bruce, 46 | 1st out |
| 45 | Julie, 49 | 14th of 18 |
| 46 | Maria, 47 | 14th of 18 |
| 47 | Sue, 58 | 16th of 18 |
| 48 | Chrissy, 54 | 9th of 18 |
| 49 | Matt, 52 | 5th of 18 |

Mean finish percentile **0.673**, where pure chance is 0.500. Only 2 of 9
went in the first third. The oldest castaway in the new era does BETTER
than chance, not worse. The one season that matches the claim is S44, and
Bruce was a medical departure on day 1.

**Claim 2 — age predicts finish order.** Rank correlation between age and
finish, per season, averaged: **-0.089**, about 1.1 standard errors from
zero. Seven of nine are negative, so the sign is right, but the size is not
distinguishable from nothing.

**Claim 3 — early boots skew older. This one holds, mildly.** Age
percentile within each cast, by boot position:

| | boot 1 | boot 2 | boot 3 | boot 4 | first 4 pooled | final 4 pooled |
|---|---|---|---|---|---|---|
| mean percentile | 0.627 | 0.444 | 0.627 | 0.673 | **0.593** | 0.451 |
| z against 0.50 | +1.32 | −0.58 | +1.32 | +1.80 | **+1.93** | −1.02 |

The first four out sit at the 59th percentile of their cast's ages rather
than the 50th, at z = +1.93. That is a real effect, and it is a mild one.

## What this means

The direction is right and the magnitude is wrong. A tilt worth 0.09 of a
percentile does not justify the third largest weight in the model.

The shape is wrong at the top, which is worse than the magnitude being
wrong, because a monotonic curve that saturates at 1.0 puts its largest
value on the oldest castaway — exactly the castaway the record says
outperforms. Lowering the weight alone does not fix that. The curve should
probably rise through the 40s and then roll off, not climb to a maximum and
stay there.

## What it changes

**The weekly vote: nothing.** Toka stays Jelly and Savu stays Eric at every
weight from 1.1 down to 0.0. Lowering the weight in fact strengthens Eric,
from 0.252 to 0.284, because Kristin is his nearest rival on Savu.

**The Sole Survivor pick: it flips, in the middle of the plausible range.**

| age weight | 1.1 | 0.75 | 0.55 | 0.3 | 0.0 |
|---|---|---|---|---|---|
| pick | rob .166 | rob .163 | rob .166 | **kristin .193** | **kristin .232** |
| runner-up | patt .138 | kristin .142 | kristin .159 | rob .164 | rob .159 |

The flip is near 0.42, and the evidence narrows the right weight to roughly
0.3 to 0.6 — which straddles it. So this measurement is enough to say 1.1
is wrong and not yet enough to say what replaces it.

## Decision, 2026-09-29

**Do not change the weight before the Wednesday lock.** The vote is not
affected, so there is nothing to gain this week, and picking 0.3 or 0.55 on
a Tuesday evening would replace one unjustified number with another when
those two values give opposite answers.

**Thursday:** fit the age effect against `data/newera_boots.json` instead
of choosing a value by hand, reshape `age_risk` so that it stops rising
near the top, add tests, and only then re-run `fsb mvp`.

The cost of waiting is at most 1 point of Sole Survivor streak, because the
bonus counts consecutive episodes back from the final and the pick can be
changed for free. That is the right price to pay for calibrating the third
largest weight in the model properly rather than quickly.
