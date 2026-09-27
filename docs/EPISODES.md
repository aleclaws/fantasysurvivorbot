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
