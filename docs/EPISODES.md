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

**Picks:** 10 on Jelly Loblack (Toka), 10 on Eric Macksoud (Savu).
(This line first said Kristin. The Savu section below moved the pick to
Eric on aired evidence. The line is corrected here so that the two agree.)

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


### The Shot in the Dark is not modelled — measured 2026-09-29

`data/scoring.json` prices `play_shot_in_the_dark` at 1 point, but the
engine does not know that the item can save its holder. A Shot in the Dark
makes the votes void 1 time in 6. When that occurs, the tribe votes again
and a different castaway goes out. Points on the first target then score
nothing.

The gap is not equal across Toka. Jenna Doore played her Shot in episode 1
and it failed, so she has none. Devin Way and Jelly Loblack still hold
theirs, and both know that they are the only two in the minority.

**How large is the error?** Discount each castaway by the chance that the
castaway plays a Shot and draws safety:

```
P(voted out) = P(target) x [1 - P(plays) / 6]
```

Episode 1 gives the only in-season data for `P(plays)`: both targets
(Aaliyah and Jenna) played a Shot. That is 2 of 2, so `P(plays)` is high
for a castaway who knows that the tribe wants to vote the castaway out.

**Does it change this week?** No. This table gives the Toka winner and its
lead over the second castaway, across the full range of both unknowns:

| Jenna edit | P(plays)=0.0 | 0.5 | 0.7 | 0.9 |
|---|---|---|---|---|
| **+0.5** (now) | jelly +0.018 | jelly +0.004 | jenna +0.002 | jenna +0.008 |
| +0.3 | jelly +0.023 | jelly +0.021 | jelly +0.020 | jelly +0.019 |
| +0.0 | jelly +0.024 | jelly +0.022 | jelly +0.021 | jelly +0.020 |
| −0.4 | jelly +0.025 | jelly +0.023 | jelly +0.022 | jelly +0.021 |

Jelly wins in every cell but two, and in those two the lead is 0.002 to
0.008. That is smaller than the simulation noise. The reason the lead is
stable is that the discount is symmetric: once Jenna falls below Devin, the
second castaway is Devin, who holds a Shot exactly as Jelly does.

Savu does not move at all. Eric stays at 0.246 and Kristin at 0.150,
because no Savu castaway has used a Shot.

**Decision.** Keep the picks. Do not change the engine before the 20:00 ET
lock. Add the mechanic on Thursday with tests, as a `shots_spent` list in
`data/state.json` and a discount in `Season.vote_probabilities()`. The
measurement above is the reason to wait, not a reason to skip it: the gap
is real, and it will decide a pick as soon as two candidates are close and
only one of them holds a Shot.

### Episode 2, predicted before it airs

Record these now, and score them on Thursday. The model and the press
disagree, and only the result can say which to trust later in the season.

| # | Prediction | Source |
|---|---|---|
| 1 | Toka loses immunity and votes. | Press, from the first-look photos |
| 2 | Jelly is the Toka boot. | Model, 0.174 against Devin 0.152 |
| 3 | Devin is the Toka boot. | Press, from the episode title |
| 4 | Brady stays. He is not evacuated. | Footage has him in the challenge |
| 5 | Devin or Jelly plays a Shot in the Dark. | Press, and 2 of 2 in episode 1 |

Predictions 2 and 3 are opposed. The title, "Weaponized Honesty", points
to Devin, who called his own game "radical honesty". The press reads the
title as the move that removes him. The model still puts Jelly first,
because she and Devin carry the same edit signal and Jelly loses the other
hazard terms. The lead is 0.022, which is small.

**Two signals to settle on Thursday, whatever the result.**

- **Jenna at +0.5.** Episode 1 left this value alone on purpose, and it has
  not been tested. She was the first target, and the tribe then spared her.
  She has no Shot left. Against that, she turned the vote herself. If she
  survives episode 2 and drives the vote, +0.5 is stale and must fall.
- **Lewis at +0.5.** This is the weakest value in the file. Lewis was on
  Exile Island during the episode 1 vote, so no tribal evidence supports
  it. The one source that discusses him says that he is not in danger, and
  he is the strongest body on a tribe that keeps losing. Note a conflict of
  interest before this value moves: Lewis is one of my two drafted
  castaways, so a lower value flatters my own projection. Move it on aired
  evidence only.

CBS facts, kept apart from the reading of them: the episode is 90 minutes;
two tribes face off, so there is one Tribal Council and not a double boot;
one castaway "attempts a never-before-seen move to save an ally". The ally
is the castaway in danger, not the castaway who makes the move.

Source: [Surviving Tribal first look](https://survivingtribal.com/survivor-51-episode-2-first-look-photos-and-predictions)

### The Sole Survivor pick rested on an unsourced claim — 2026-09-29

The Sole bonus pays 1 point for each consecutive episode the correct winner
was the standing pick, counted back from the final, to a maximum of 13. The
standings show `-` in the Sole column for all eight players, so nobody has
banked any of it. It is the largest pot still open, and the site allows the
pick to be changed for free.

**Change it early or not at all.** A change resets the streak. At episode 2
that costs 1 or 2 points. At episode 8 it costs 8. So this is the cheapest
week of the season in which to be wrong, which is the reason to test the
pick now rather than later.

**What the test found.** `idols: ["rob"]` entered in the episode 1 ingest
with no source recorded anywhere in this repository. The only other mention
of Rob and an idol in these notes is Rob accusing ERIC of idol-hunting,
which is not evidence that Rob holds one.

That one unsourced line was carrying the whole pick:

| Scenario | rob | patt | kristin | pick |
|---|---|---|---|---|
| idol, age prior as-is | **0.166** | 0.138 | 0.107 | rob |
| idol, age prior halved | **0.166** | 0.130 | 0.159 | rob |
| idol, age prior off | 0.159 | 0.120 | **0.232** | kristin |
| no idol, age prior as-is | 0.102 | **0.148** | 0.108 | patt |
| no idol, age prior halved | 0.109 | 0.137 | **0.169** | kristin |
| no idol, age prior off | 0.108 | 0.122 | **0.242** | kristin |

Take the idol away and Rob falls from 0.166 to 0.102, and the pick becomes
Patt or Kristin. The idol is not a detail. It is the reason.

**The claim is true.** Inside Survivor's episode 1 stats page: "Rob found a
hidden immunity idol. This is the first idol without an attached twist
(beware/boomerang) found in a premiere episode since *David vs. Goliath*."
Premiere recap coverage agrees. The same coverage says Lewis was offered an
idol on Exile Island and failed to retrieve it, so Lewis holds nothing.

The source is now written into `_idols_note` in `data/state.json`, next to
the value, with a warning not to remove the entry without re-running
`fsb mvp`.

**The pick stands: Rob.** It survives halving the age prior. Only setting
that weight to zero flips it, and zero is not a correction, it is the other
extreme. The age prior remains the largest untested weight in the model,
and this is the second decision it has now been shown to control.

**Two items for Thursday.**

- ~~Idol expiry may be off by one.~~ **Confirmed and fixed the same day.**
  reality blurred's rules explainer is explicit: "The last time you can use
  the hidden immunity idol is when there are five survivors remaining in the
  game." The idol IS playable at the final five. The simulation required
  `len(live) > 5`, which barred exactly that play, so
  `idol_expires_at_players` is now 4 and the note sits beside the value.
  Rob's P(win) rises 0.171 to 0.177. The vote is untouched, and not by luck:
  the parameter is read only inside `simulate_placements`, which
  `vote_probabilities` never calls. Jelly stayed at 0.084 and Eric at 0.130,
  identical to the digit.

  Worth recording how nearly this went the other way. A first search summary
  said idols "can no longer be played once the game reaches the final five",
  the opposite of the cited quote, and the Survivor Wiki returns HTTP 402 so
  it could not settle it. Two summaries disagreeing is a reason to find a
  quote, not to pick the summary that suits the model.
- `Season.apply_state` only ever SETS `out`, `idol`, `edit` and `medevac`.
  It never clears them. Re-applying a state that drops an idol therefore
  leaves the castaway holding it. No production path hits this, because
  each run builds one Season from the file, but it silently corrupted the
  first version of this test and it will catch someone else.

### A stale note, corrected before the cloud routine reads it — 2026-09-29

`_medevac_note` in `data/state.json` still described Brady at 0.5 after the
value itself was lowered to 0.15 on 2026-09-28. The note, not the value, is
the risk: the cloud routine runs at 14:05 ET on Wednesday and edits this
file, and a note that argues for 0.5 invites it to restore 0.5. The note
now states 0.15 and gives the reason - set medical risk from footage, never
from a synopsis.

Sources: [Inside Survivor episode 1 stats](https://insidesurvivor.com/survivor-51-episode-1-stats-61724),
[reality blurred premiere recap](https://www.realityblurred.com/realitytv/2026/09/survivor-51-episode-1-recap/)

> The age prior is no longer unvalidated. It was measured on 2026-09-29
> against every new-era season - see [AGE_PRIOR.md](AGE_PRIOR.md). The
> direction holds and the magnitude does not, and the oldest player in a
> new-era season finishes BETTER than chance rather than worse. The weight
> is unchanged until Thursday, because the vote does not depend on it and
> the Sole Survivor pick flips in the middle of the plausible range.

### The 2026-09-30 weekly job failed partway. The picks were unaffected.

**What happened.** The job fired at 18:39:29, nine minutes behind its 18:30
schedule, which is a launchd wake delay and matches the 18:34 start on
Sep 23. The machine was about four times slower than normal: 71 tests took
133 seconds against a usual 35. `rules-check` passed, 25 actions against 25.
Then `standings` failed with:

```
SubmitError: login failed - check FSG_EMAIL / FSG_PASSWORD
```

**That message is wrong, and the wrongness is the lesson.** The same `.env`
logged in by hand minutes later and read the site correctly. Nothing was
wrong with the credentials. `login()` raises that error whenever it cannot
find what it expects after signing in, so a slow page under load is reported
as a bad password. The next person to read that line will go looking in the
wrong place.

**Why the job was killed rather than left to finish.** `standings` set
STATUS=1 and the script carried on to `vote`, as designed. `vote` then ran
for over 18 minutes, almost certainly stuck in the same slow login, with the
20:00 lock approaching.

A failed login is harmless: it raises inside `_make_page()`, before any form
is touched. The danger is the case where login SUCCEEDS and the write stalls,
because `submit_vote` works in two passes, zeroing every field and then
setting the two it wants. An interrupted write leaves the allocation at zero,
which scores nothing for the week. Once the job had demonstrated it could not
log in reliably and was hanging, letting it keep racing the deadline had
negative expected value. Killed at 19:33.

**Outcome.** Verified by hand at 19:33, 27 minutes before the lock:
`jelly = 10`, `eric = 10`. At 20:03 `verify` prints the draft order but no
vote lines, so login worked and the vote fields are simply gone - the lock is
in effect. The submitted allocation is the intended one.

**Why this cost nothing.** The picks were submitted and verified days
earlier, so the weekly job was only ever a refresh. The one real loss is that
`standings` never synced, so `data/league.json` still holds last week's
scores. That does not affect a vote already submitted, and tomorrow's ingest
re-reads the standings anyway.

**Three fixes for Thursday, in priority order.**

1. **Make `login()` tell the truth.** Separate "could not find the element in
   time" from "the site rejected the credentials". Retry with backoff before
   raising either. A misleading error is worse than no error, because it sends
   the reader to the wrong cause.
2. **Make an interrupted vote safe.** The two-pass zero-then-set has a window
   where the allocation is zero. Either write the wanted values first and zero
   the rest afterwards, or re-read and repair immediately after writing.
3. **Do not let the job race the lock.** If it is past roughly 19:45, it
   should skip straight to the vote and verify, and never start a long
   `standings` sync it has no time to finish.

### The three fixes, 2026-09-30 evening. One of them was wrong.

Done after the 20:00 lock, which is the safest moment to touch the
submission path: a full week before the next deadline.

**1. `login()` now tells the truth. Done, test first.** Signing in has three
outcomes, not two: `ok`, `bad_credentials`, `unconfirmed`.
`classify_login_outcome()` decides which, and only `unconfirmed` is retried -
three attempts with 0s, 4s and 12s backoff. A real rejection is never
retried, because repeated attempts with a bad password are how accounts get
locked. The wait is now on the navigation itself rather than a fixed 800ms,
so a slow machine gets the time it needs. The unconfirmed message says
plainly that this is usually a slow site and not a wrong password. Six new
tests, including the exact 2026-09-30 case: correct password, slow page, no
rejection text.

**2. Removing the zero-then-set window: WITHDRAWN. The plan was wrong.**

Last night this was written down as a fix to make. Reading `submit_vote`
properly shows there is nothing to fix, and that making the change would
break something that works.

Both passes are client-side DOM manipulation. `window.submitVotes()` appears
exactly once in the file, at the very end. Nothing reaches the server before
it. So an interrupted write closes the browser holding a zeroed FORM while
the server still holds the previous allocation. **Zeros cannot persist.**

Worse, writing the wanted values before zeroing the rest would reintroduce a
bug that was found by hand: the site's `capInputAtMaximum` clamps each field
against the running total at the moment its own input event fires, so a
target increase landing before an unrelated decrease gets silently clamped.
Zeroing first guarantees every field starts the second pass at 0, so the
running total is always a subset sum of the final allocation. The ordering is
deliberate and it stays.

**This also corrects the reasoning given for killing the job tonight.**
Stopping it was still right - it was failing logins and burning the clock to
no purpose. But the urgency was argued from a risk that does not exist. The
picks were never in danger from an interrupted write.

**3. The job no longer races the lock. Done.** Past `LOCK_GUARD_HHMM` (1930)
the script skips `rules-check` and `standings`, logs why, sets STATUS=1 and
goes straight to the vote. Tonight it spent close to an hour on a standings
sync it could not finish and had still not reached the vote with 27 minutes
left. Checked on both sides of the boundary: 1830 and 1929 run normally,
1930, 1945 and 2015 skip. The `10#` prefix is load-bearing - a morning time
like `0930` is invalid octal and errors without it.

## Episode 2 — "Weaponized Honesty" (30 September 2026) — RESULT

**Result.** Savu lost immunity. Ana Sani was voted out after a 4-4 tie: four
votes Ana, four votes Eric, and the last two parchments both read Ana, so
she left 6-4. Eric Macksoud was offered his Shot in the Dark and **declined
it**. Rob Antonson, holding an idol, **declined** to play it on Eric. Brady
Booker was not evacuated: medical told him he would "be good to go for
today's immunity challenge", he competed in both challenges, and the total
cost was a small piece of thumb.

**My week: zero vote points.** 10 on Jelly (Toka) scored nothing because
Toka never voted. 10 on Eric (Savu) scored nothing because Eric survived.
Say it plainly: the picks were wrong and the week was lost.

### The five predictions, scored

Recorded on 2026-09-29 before the episode aired.

| # | Prediction | Source | Result |
|---|---|---|---|
| 1 | Toka loses immunity and votes | Press | **WRONG** — Savu lost |
| 2 | Jelly is the Toka boot | Model | **Untested** — no Toka tribal |
| 3 | Devin is the Toka boot | Press | **Untested** — no Toka tribal |
| 4 | Brady stays, not evacuated | Footage read | **RIGHT** |
| 5 | Devin or Jelly plays a Shot in the Dark | Press + ep 1 base rate | **WRONG** |

**The model beat the press on the one thing both called.**
`tribe_loss_probability` had Savu at 0.516 against Toka 0.484 — a marginal
lean, but the right one. The press was confident Toka would lose again, on
Brady's hands and Lewis's hands and the whale carry. Savu lost. That lean is
nearly a coin flip and should not be oversold, but it is the model's first
correct call against a confident contrary press read.

**It did not help, and that is structural.** The budget is 10 points per
tribe and cannot be moved between them, so being right about which tribe
votes earns nothing on its own. Knowing Savu would vote would only have
mattered if it changed the Savu pick, and it did not.

### Where the Savu pick actually went wrong

Eric was the right read of the *target* and still the wrong pick. He took
four of ten votes. The model had him at 0.252 of Savu's boot weight, far
clear of Kristin at 0.154. That part was close to right.

Ana was 5th at 0.089. She carried **no edit signal at all** — she sat at
the baseline the bio priors give her, because no episode-1 content had named
her. A 4-4 tie means Savu was split down the middle and the model saw only
one side of the split.

**The honest diagnosis: this was lost on information I did not have**, not
on a model defect. Savu's internal alliance structure — Rob telling Eric
that "Ana was a fake vote" — is not in any pre-episode source. The press
missed it too, and more badly.

### What the Shot in the Dark result says

**Good news for Tuesday's decision.** The mechanic was measured and
deliberately not implemented before the lock. It would not have changed the
Savu pick either: discounting Eric by the full `P(plays)/6` gives
0.252 × (1 − 0.8/6) = 0.218, still far clear of Kristin's 0.154. The gap was
too wide for the correction to matter. Not implementing it cost nothing.

**But the parameter needs revising down.** Episode 1 gave 2 of 2 targets
playing a Shot, which put `P(plays | targeted)` near 0.8. Eric declined
while sitting on four votes, so the record is now **2 of 3**, about 0.67,
and the one castaway who declined did so in exactly the spot where the
theory said he would play. Use 0.6 or lower when this is implemented, and
treat "a target will play it" as a tendency rather than a rule.

### One strategic question this raises

The optimiser went all-in on one name per tribe because the field is
"beatable on accuracy alone" — 6 of 8 players scored no vote points in
episode 1. That reasoning assumed my accuracy was decent. It is now 0 for 1
on the real boot.

Do not over-correct on one week. But when the site rescores and the episode 2
Vote column is readable, check two things: how many opponents found Ana, and
whether a spread would have beaten an all-in. If the field is also missing,
accuracy still wins. If several found Ana, the field is better than the
episode 1 calibration said and `field_sharpness` is too low.

**Also still to do:** refresh the edit signals from the analytical recaps
once they publish, and set `edit_updated_episode` to 3. Deliberately not done
tonight on same-night recaps - `edit` carries weight 1.40, the heaviest in
the model, and it is the wrong input to rush.
