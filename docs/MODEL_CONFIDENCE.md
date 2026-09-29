# What the model rests on

Every input group was audited on 2026-09-29. This page says where each one
comes from, how much it is trusted, and which live decision it controls.
Detail for the two measured ones is in [AGE_PRIOR.md](AGE_PRIOR.md).

| Input | Weight | Basis | Confidence | Controls |
|---|---|---|---|---|
| `edit` | 1.40 | Aired content, per castaway, sourced in EPISODES.md | **High** | The vote |
| `phys` | −1.20 | Bio guess from age and occupation | **Low**, self-declared | Sole pick |
| `age` | 1.10 | Asserted, never measured until today. **Measured: wrong** | **Low** | Sole pick |
| `social` | −0.90 | Bio guess from age and occupation | **Low**, self-declared | Sole pick |
| `threat` | −0.25 | Bio guess from age and occupation | **Low**, self-declared | Little |
| `preseason_buzz` | 0.20 | Two cited pundit sources, averaged, capped ±0.30 | Low, already halved | Little |
| field params | n/a | Calibrated from episode 1's real vote scores | **High** | Accuracy vs variance |
| scoring constants | n/a | All 25 verified name and value against the live page | **High** | Everything |
| `idol_play_success` | 0.55 | Assumed | **Low** | Sole pick |
| event-frequency params | n/a | Assumed | **Low** | Nothing live — see below |

## The two things worth knowing

**The vote rests on the strong inputs.** Jelly on Toka and Eric on Savu
hold across every perturbation tried: the age weight from 1.1 to 0, the
three bio weights from full to zero, and both together. Both picks get
*stronger* as the weak priors shrink — Eric goes from 0.252 to 0.309. The
vote is driven by `edit`, which is sourced, and by the verified scoring
constants. This is the reassuring half, and it is the half the automation
submits.

**The Sole Survivor pick rests on the weak ones.** Rob leads only at full
weights. Every low-confidence input, moved on its own toward a
better-evidenced value, either flips the pick or erases the lead:

| Change one thing | Sole pick |
|---|---|
| nothing (baseline) | rob 0.166 |
| age weight 1.1 → 0.55 | rob 0.166, kristin 0.159 — a tie |
| age weight 1.1 → 0.3 | **kristin 0.193** |
| bio weights × 0.5 | **patt 0.166** |
| `idol_play_success` 0.55 → 0.35 | rob 0.143, patt 0.142 — a tie |

Rob's one hard fact is that he holds a verified idol. How much that is
worth is set by `idol_play_success`, which is marked confidence: low. So
even the fact reaches the model through a guess.

## Event-frequency parameters affect nothing live

`camp_points_per_episode`, `advantage_points_per_episode`,
`tribe_reward_fraction`, `reward_companions`, `auction_prob`,
`fire_making_prob` and the rest are consumed only by `draft_board`, which
turns per-action point values into expected season points. The draft has
already happened and the roster cannot be changed, so these move no live
decision. They are worth calibrating for a future season, not this week.

Only five of the `draft_model` entries reach a live decision, all through
`simulate_placements`: `merge_at_players`, `idol_play_success`,
`idol_expires_at_players`, `finalists`, `love_from_home_window`. Of those,
only `idol_play_success` moves the answer materially.

## The episode 1 measurement, for Thursday

`priors.json` asks for these to be calibrated "from the standings
'Survivor' column once episodes 1-2 are scored". Episode 1's column is now
read and recorded in [RULES.md](RULES.md). After removing tribe immunity,
the 16 drafted castaways earned 16 non-immunity points between them, which
is **1.0 per castaway per episode**. The model implies roughly 0.45 from
`camp_points_per_episode` 6 and `advantage_points_per_episode` 3 spread
over the field.

Do not act on that yet. Episode 1 is inflated by premiere-only scoring —
the marooning challenge, the supply challenge, first fire, first idol — so
1.0 is an upper bound. Episode 2 doubles the sample and the file itself
says to wait for it.
