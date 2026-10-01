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

## The same problem, in the bio priors — measured the same day

`phys`, `social` and `threat` carry weights of −1.2, −0.9 and −0.25. The
second and third largest weights in the model are two of those three. The
file is honest about what they are:

> phys/social/threat are SUBJECTIVE pre-season priors from bio data only
> (age + occupation). Weak.

So the problem is not that they are hidden. It is that inputs described in
their own file as weak, built from nothing but age and occupation, carry
near-top weights — and they are still at full strength in episode 2, after
real edit evidence exists for nine castaways.

Scaling all three toward zero:

| bio weights | Toka | Savu | Sole |
|---|---|---|---|
| ×1.0 | jelly .174 | eric .252 | rob .166 |
| ×0.75 | jelly .175 | eric .260 | rob .154 |
| ×0.5 | jelly .175 | eric .268 | **patt .166** |
| ×0.0 | jelly .176 | eric .283 | **patt .178** |

## Both priors together — the honest summary

| age | bio | Toka | Savu | Sole |
|---|---|---|---|---|
| 1.1 | ×1.0 | jelly .174 | eric .252 | rob .166 |
| 0.75 | ×0.75 | jelly .176 | eric .272 | rob .155 |
| 0.55 | ×0.75 | jelly .177 | eric .278 | **kristin .157** |
| 0.45 | ×0.5 | jelly .178 | eric .288 | **kristin .154** |
| 0.3 | ×0.5 | jelly .179 | eric .291 | **kristin .172** |
| 0.0 | ×0.0 | jelly .180 | eric .309 | **kristin .179** |

**The vote is rock solid.** Jelly and Eric hold at every combination, and
both get STRONGER as the weak priors shrink — Eric from 0.252 to 0.309.
The vote rests on aired evidence, not on the guesses. That is the single
most reassuring result of the day, because the vote is what the automation
submits.

**The Sole Survivor pick is not solid.** It is Rob only at full weights.
Discount the weak priors even moderately and it becomes Kristin, and some
bio-only settings give Patt. Three answers across a plausible range is not
a pick, it is a coin toss.

The direction is consistent and worth naming: **every discount moves toward
Kristin**, because both weak priors happen to punish her. She is the oldest
castaway, and she carries the lowest `phys` in the cast at 0.30. Set
against that, the evidence that is NOT a guess all points the other way —
the best edit signal in the cast at −0.5, chosen by her tribe to negotiate,
first to make fire, ranked first of twenty by DraftKings, and the new-era
record above saying the oldest player outperforms.

## Decision, revised the same evening

**Still hold Rob through the Wednesday lock**, for a better reason than
before. Not because Rob is robust — he is not — but because episode 2 airs
tomorrow and will produce fresh edit evidence for the whole cast, including
Savu, which has produced little so far. Real evidence outranks any guess I
could make tonight about what these weights should be. Deciding Rob against
Kristin after episode 2 uses strictly more information.

The price of waiting is 1 point of streak. The pick can be changed for
free, and the bonus counts consecutive episodes back from the final.

**Thursday, in order:** recalibrate the age curve against
`data/newera_boots.json`; decide whether the bio weights should decay as
`edit_updated_episode` advances, since the priors file already says edit
data overwrites them; fold in episode 2's evidence; then re-run `fsb mvp`
and change the Sole pick if it still says Kristin.

## Fitted at last — 2026-10-01

Measured on 2026-09-29, fitted on 2026-10-01. Early boot means first 4 out
of 18, so the base rate is 0.222. Observed rate relative to that base, over
seasons 41-49:

| band | n | early | rate | multiplier |
|---|---|---|---|---|
| under 25 | 22 | 3 | 0.136 | **0.61** |
| 25-29 | 49 | 10 | 0.204 | 0.92 |
| 30-34 | 40 | 5 | 0.125 | 0.56 |
| 35-39 | 21 | 6 | 0.286 | 1.29 |
| 40-44 | 10 | 6 | 0.600 | **2.70** |
| 45+ | 20 | 6 | 0.300 | 1.35 |
| 50+ | 8 | 2 | 0.250 | 1.12 (z=+0.19) |

The trustworthy aggregate, since several bins are thin: **38 and over runs
1.83x the base rate, z=+2.50**, and that elevation is concentrated below 50.

**This corrects what was written here on 2026-09-29.** That said the
magnitude and the shape were both wrong. The fit says the **magnitude was
close** - 1.1 against a fitted 1.0 - and the **shape was the real error**.

`age_risk` is now a bump, not a ramp: zero below 36, rising to 1.0 at 41,
decaying to zero by 52. Kristin at 49 goes from 0.923 to 0.27.

Two beliefs the old function encoded are gone, because the record
contradicts both:

- **Risk keeps climbing with age.** It does not. 50+ sits at 1.12x, which is
  nothing, and the oldest castaway of a season finishes at percentile 0.673
  where chance is 0.500.
- **The very young carry a naivety risk.** They do not. Under-25s go early
  at 0.61x base. An unsupported term is worse than no term, so it is gone.

`postmerge` age stays at 0.35 and is **not** fitted. The data here covers
early premerge boots only. Do not claim it reaches further than that.

### Two tests were replaced, not worked around

`test_rises_with_age_past_the_late_thirties` asserted
`age_risk(42) < age_risk(49)`, and `test_very_young_carries_some_risk_too`
asserted `age_risk(22) > age_risk(31)`. Both encoded the guesses the
function was built on, which is why neither could ever have caught those
guesses being wrong. A test that asserts an assumption cannot test it.

### One allocation test was under-powered, and that is NOT the same thing

`test_recoverable_deficit_late_buys_variance` failed after the refit. The
tempting move was to relax it, since it guards an effect worth under a
thousandth of win probability. Measuring instead:

```
sims=25000   spent=10  P(win)=0.00396  evmax=0.00396   joins consensus
sims=60000   spent=2   P(win)=0.00473  evmax=0.00373   VARIANCE PLAY
sims=120000  spent=2   P(win)=0.00466  evmax=0.00376   VARIANCE PLAY
```

The engine's actual choice never changed. It backs the same castaway either
way, 8 of its 10 points on the name the field is not sitting on. What
changed is that the refit narrowed the gap between the top two from 0.023 to
0.019, which shrank the paired gain against its own error bar, so the
significance guard refused the play - correctly, on the evidence it had.

So the model was right, the guard was right, and the test needed more draws.
Raised to 60000 with the measurements recorded beside it. Weakening the
assertion would have deleted a real guard to paper over a sampling problem.
