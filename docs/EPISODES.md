# Episode log

One entry per episode. Record what happened, what it changed in the model,
and the source. The weekly routine reads this to avoid re-researching.

## Episode 1 — "Permanent Uncertainty" (23 September 2026)

**Result.** Toka lost immunity and went to a live Tribal Council. Aaliyah
Puglia was voted out 6–2. Savu won and never voted.

**What happened.** The tribe first planned to vote Jenna Doore out. Patt
Cannaday told Jenna the plan. Jenna told Brady Booker that Aaliyah was
targeting him. Toka split. Devin Way and Jelly Loblack (the "Helicopter
Alliance") cast the only two votes, for Jenna. The other six voted Aaliyah.
Aaliyah and Jenna both played a Shot in the Dark, and both failed.

**What this changed.**

| Castaway | Before | After | Reason |
|---|---|---|---|
| Jelly Loblack | edit +0.3 | **+0.7** | Confirmed as half of the exposed two-person minority. She voted Jenna with Devin and lost 6–2. She was under-weighted. |

That single correction moved the Toka pick off Jenna and onto Jelly.

**Two things to keep straight.**

1. Kristin Flickinger's prior was never tested. Savu won immunity, so Savu
   held no vote. The model's heaviest pre-merge bet, that the oldest player
   goes early, has not yet been right or wrong.
2. Jenna was the first target but the majority spared her, and she is allied
   with Patt. Her +0.5 edit is left alone. Her Shot in the Dark is now spent.

Sources: [TVLine recap](https://www.tvline.com/2267004/survivor-51-premiere-recap-coin-flip-return-aaliyah-voted-out/),
[TVInsider recap](https://www.tvinsider.com/1292889/survivor-51-episode-1-recap-who-was-voted-out/),
[Paramount+ recap](https://www.paramountplus.com/sneak-peak/survivor-season-51-episode-1-recap/)


### Corrections made 2026-09-28 (local session)

- **Brady Booker's edit was +0.7 (doomed), now -0.2.** The episode 1 ingest
  put him in the exposed minority with Devin. The research above corrects
  that - the two Jenna votes were Devin and Jelly, and Brady voted with the
  six - but his edit was never brought in line with it. His medical risk is
  separate and is carried by `medevac_risk`, not by his vote risk.
- **`my_mvp_on_site` said Eric; the site holds Rob.** Checked directly
  against profile.html from a session that can reach the site. The earlier
  reading came from the league activity feed, which lists every prediction
  ever made, so a superseded entry there looks like the current pick.
  `tools/submit.py standings` now reads the live pick off the profile every
  run, so this cannot drift again.
- With Brady corrected, `fsb mvp` puts Rob (0.153) back ahead of Patt
  (0.144), so the live pick stands and the streak is not reset. Patt is also
  held by an opponent; Rob is not.


### Savu read corrected 2026-09-28 (local session)

Savu never voted in episode 1, so the model had no evidence there and fell
back on the age prior: Kristin, 49, at 0.29 of the tribe's boot weight. The
aired content actually says the opposite.

| Castaway | Evidence | Edit |
|---|---|---|
| Kristin Flickinger | Chosen BY the tribe to negotiate for supplies, sparked the first fire, reconnected with Sharonda. Integrated and trusted, not an outsider. Her 6 points are exactly negotiate + fire + immunity + opening challenge. | **-0.3** |
| Eric Macksoud | "Starting to rub his tribemates the wrong way." Rob threw him under the bus, implying he was idol-hunting while he was using the fishing gear. Alexis called him "sweet ... but annoying". A named antagonist and multiple tribemates commenting. | **+0.8** |

That moves the Savu pick from Kristin (0.201) to Eric (0.216) - a near-tie,
but one now settled by aired evidence on both sides rather than by an
untested demographic prior. Sources: [Inside Survivor episode 1
recap](https://insidesurvivor.com/survivor-51-episode-1-recap-the-open-era-61715),
[DraftKings episode 2
predictions](https://dknetwork.draftkings.com/2026/09/25/survivor-51-predictions-who-will-be-voted-out-next/).

**The age prior itself is still unvalidated.** I tried to set its weight from
the real base rate - how often the oldest player goes early in the new era -
and could not find systematic data, only that Survivor 41's first boot was
51. One data point does not justify retuning the largest weight in the model,
so it is unchanged and still the biggest untested assumption in it.

## Episode 2 — "Weaponized Honesty" (30 September 2026) — before it airs

**Preview.** Brady Booker cuts his finger with a machete and loses a lot of
blood. Medical is called in. The immunity challenge is at sea, and one tribe
struggles to stay afloat. At Tribal Council one player attempts a
never-before-seen move to save an ally.

**Why this matters to scoring.** The rules are explicit: no Vote Points are
awarded for a castaway who quits, is medically evacuated, or is removed by
production. So points parked on Brady score nothing if he leaves on a
stretcher. Brady also sits in Toka's six-vote majority, so his vote risk is
low. If Brady leaves this week, medical is the likelier route.

This is now modelled. `medevac_risk` in `data/state.json` holds the chance
that a departure pays nobody, and `Season.vote_probabilities()` discounts a
pick by it. Brady is set to 0.5 for this episode only. **Clear that field
after the episode airs.**

There is an edge in it. Brady's injury is in the public preview, so the field
is likely to back him. If he is evacuated, every one of those points scores
zero, and being on the real vote-out is worth more than usual this week.

Source: [cartermatt preview](https://cartermatt.com/729031/survivor-51-episode-2-preview-is-brady-getting-medically-evacuated/)

**Picks:** 10 on Jelly Loblack (Toka), 10 on Kristin Flickinger (Savu).

### Brady's medical risk, corrected 2026-09-28

`medevac_risk` had Brady at 0.5 off the episode 2 synopsis ("a chilling
injury at camp threatens to send one player home"). Two outlets describing
the same first-look footage have him cutting his hand, getting it bandaged
and then **competing in the immunity challenge** - visible in the water
during the challenge clips. Someone who plays on was not pulled, so the
synopsis line is promo framing. Lowered to 0.15, leaving residual risk
because medical can still intervene later.

This matters wider than Brady: a medical evacuation pays NOBODY vote
points, so overstating its chance made the whole week look less valuable
than it is. The picks did not change - Jelly on Toka, Eric on Savu, both
already live - and the win probability held at 0.098.

Sources: [Surviving Tribal first look](https://survivingtribal.com/survivor-51-episode-2-first-look-photos-and-predictions),
plus corroborating challenge-footage description in episode 2 preview coverage.

### Savu read corroborated 2026-09-29

DraftKings' post-episode-1 power rankings, read a day after the Savu call
was made, independently rank the same two castaways at opposite poles:

- **Kristin #1 of 20.** Negotiated with the other tribe for supplies,
  "already looks like someone that won't crack under pressure", forming
  early alliances with Ori and Sharonda.
- **Eric #20 of 20.** A "friendly vampire" who "struggles socially", and
  "Rob has already turned on his fellow Rhode Islander".

That is three independent in-season sources agreeing (Inside Survivor's
recap, DK's episode 2 predictions, DK's power rankings), so the signals
were strengthened to match: Eric +0.8 -> +0.9, Kristin -0.3 -> -0.5. The
Savu gap widens from 0.216/0.201 to 0.252/0.154.

The pick does not change - Eric on Savu, Jelly on Toka, both already live.
This is confidence, not a new decision, and it is worth being clear about
the difference. Unlike the pre-season buzz that put Aaliyah at -0.30 and
then watched her go first, every one of these is a description of aired
content: who negotiated, who turned on whom.

