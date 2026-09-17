# Strategy

## The mistake to avoid

The weekly vote looks like a simple problem. You have 10 points. You put them
on the castaway who is most likely to go home. Expected points are:

    EV(x) = sum of p_i * x_i,  where the sum of x_i is 10

This is a linear function on a simplex. A linear function on a simplex is
always largest at a corner. So this rule always gives the same answer: put all
10 points on the most likely boot. Do this every week, all season.

That rule is correct, and it is almost worthless.

The league does not pay you for points. It pays you for first place. If ten
players all put 10 points on the same obvious boot, then nobody moves. The
weeks that the favourite goes home, everybody scores 10. The weeks the
favourite stays, nobody scores. Consensus play collects points and gains no
ground.

## What the engine maximises

The engine maximises the probability that you finish first. It estimates that
probability with a simulation:

1. Draw who goes home, this week and each week after it.
2. Draw what the other players do.
3. Add up every score.
4. Count how often your score is the highest.

This objective is not linear. It gives different advice in different
positions, which is the point.

## The three regimes

The table below is real output. The position is six castaways left. The
favourite is Carter, at p = 0.21.

| Your position | The engine's picks | Why |
|---|---|---|
| 28 points ahead | 3 Carter, 3 Maggie, 3 Alexis, 1 Aaliyah | Cover the field. Score when they score. |
| Level | 10 Carter | Nothing to protect. Take the points. |
| 25 points behind | 6 Maggie, 4 Carter | The favourite cannot close the gap. Buy variance. |

Read the third row again. When you are behind, the favourite is the worst
place for your points, because every rival already holds that position. You
need the weeks the field is wrong.

## The model of the other players

The simulation gives each opponent their own fixed misread of the cast. The
misread stays with them all season.

This detail decides the quality of the advice. An earlier version made the
other players a sharpened copy of your own beliefs. That version gave you no
way to beat them by being correct, only by being different. So it gambled
every week. It recommended a longshot in episode 1 and gave up 1.0 expected
points to do it.

Opponents who are noisy, not only herd-like, keep the edge honest. You beat
them by holding better probabilities. You gamble only when arithmetic says
that accuracy alone is not enough.

Three settings in `data/league.json` control the model:

- `field_sharpness` — how much the field piles onto the obvious boot
- `field_all_in_fraction` — how many of them spend all 10 points on one name
- `field_noise` — how wrong their reads are

Raise `field_sharpness` when you can see their picks and they all agree.
Lower `field_noise` when the league is strong. Both changes make the engine
more willing to leave the favourite.

## Where the real edge is

The vote budget is 10 points per tribe per week. Over a 13-episode season that
is a few hundred points. The draft and the Sole Survivor bonus are large and
you set them once.

So order your effort like this:

1. **Get the rules right.** A wrong constant beats any amount of modelling.
2. **Get the Sole Survivor pick right.** It pays 1 point per consecutive
   episode, counted back from the final, that you held the eventual winner —
   worth up to 13 points, not a one-off placement bonus. You may change the
   pick at any time for free, so re-check it whenever the standings or edit
   signals move, not only once before the premiere. See `docs/RULES.md`.
3. **Draft for survival time**, not for challenge strength.
4. **Update the edit signals each week.** They are stronger than any prior.
5. **Then** worry about the weekly allocation.

## Draft value against winner value

These are different questions, and the engine answers them separately.

Draft value is an annuity. A castaway pays you for each week they stay in the
game, and pays more after the merge. Physical players last longer before the
merge, so they lead the draft board.

Winner value is not the same. Physical players become targets after the merge.
The engine changes the sign of the physicality weight at the merge, because
Survivor does. The result is that the top of the draft board and the top of
the win-probability list are different castaways. Draft the first group. Pick
your MVP from the second.

## What the model does not know

Be honest about this list:

- The pre-season priors use age and occupation only. They are weak.
- No tribe rosters were public before the premiere.
- The "open era" format can break the schedule the simulation assumes.
- The draft scoring constants are a guess. See `docs/RULES.md`.

The edit signals fix most of this after episode 1. Until then, treat the
numbers as a starting point and not as knowledge.
