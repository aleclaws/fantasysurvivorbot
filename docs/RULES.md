# Scoring rules

## How this page was made

A local Claude Code session ran `tools/recon.py` against a signed-in Chrome
profile on 2026-09-17. That machine can open `fantasysurvivorgame.com`. The
session read `rules.html` and `faq.html` directly. The text below is
quoted from those pages, saved at `data/site/rules.txt` and
`data/site/faq.txt`. `data/scoring.json` holds the same numbers in a form
the code reads.

The session could not sign in to the league itself (see the note at the
bottom). Nothing that needs a login is in this file.

## High confidence — quoted from the site

### Outwit (the weekly vote)

- You get **10 points per tribe**, each week.
- You divide those 10 points between the castaways of that tribe.
- You can put a maximum of **10 points on one castaway**.
- You score the points you put on the castaway who is voted out.
- The votes reset after the site scores the episode.
- You must send the votes **before the episode starts on the US East coast**.
- Counts as "voted out": most votes at tribal council, eliminated by drawing
  rocks, loses a final fire-making challenge, or sent elsewhere (e.g.
  Extinction Island) by vote.
- Does **not** count: quitting, medical evacuation, or removal by production.

### Outplay (drafted castaways)

The real system pays a point value per named action, not a flat weekly rate.
Every value below is quoted from the rules page. See `data/scoring.json` ->
`outplay.actions` for the machine-readable copy.

| Action | Points | Limit |
|---|---|---|
| Win the Marooning Challenge | 1 | — |
| Win the Supply Challenge | 1 | — |
| Win a Tribe Reward Challenge | 2 | — |
| Win a Tribe Immunity Challenge | 3 | — |
| Win an Individual Reward Challenge | 1 | winner + any castaway they bring |
| Win an Individual Immunity Challenge | 2 | — |
| Win a Journey Challenge | 1 | — |
| Win the Final Four Fire-Making Challenge | 2 | — |
| Read Tree Mail | 1 | once per episode |
| Strategize at the Water Well | 1 | once per episode |
| Make Fire at Camp | 1 | once per episode |
| Find Food | 1 | once per episode |
| Go to Exile Island | 1 | — |
| Go on a Journey | 1 | once per episode |
| Join the merged tribe | 2 | once per season |
| Attend the Survivor Auction | 1 | — |
| Get Love from Home | 1 | — |
| Find a clue to an idol or advantage | 1 | — |
| Play an idol or advantage | 2 | — |
| First to gain an immunity idol | 1 | — |
| First to gain an advantage | 1 | — |
| Play Shot in the Dark | 1 | — |

### Outlast (the Sole Survivor pick)

This is **not** a placement bonus. There is no separate payout for second or
third. The real mechanic is a streak:

- Each player picks one castaway as their predicted season winner.
- You may **change this pick at any time** between episodes.
- To score, your pick going into the final episode must be the actual
  winner.
- Points paid = **1 point per consecutive episode**, counted backward from
  and including the final episode, that the correct winner was your
  standing pick. A switch away and back breaks the streak.
- Maximum: **13 points** (the site's own text: "Pick Winner of Survivor
  (0-13 points)"), which matches the 13-episode season length.

This changes strategy. Hedging is possible and free: switching to a
stronger candidate costs you nothing except a streak you were not going to
finish anyway. Re-run `python3 -m fsb mvp` whenever the standings or the
edit signals change, not only once before the premiere.

### Tie-breaker, in order

1. More vote (outwit) points.
2. More survivor (outplay) points.
3. More sole survivor + out-of-game points.
4. Still tied: stays tied.

### League mechanics

- Max league size: 50 players.
- A player may join up to 3 leagues.
- You cannot leave a league once it has drafted.

## Conflicting — needs a real scored episode to resolve

**Out-of-game points.** The rules page says a castaway keeps earning your
draft roster 1 point per episode after they are voted out, up to 13 points
total ("Castaway Out of Game (0-13 points)"). The FAQ page says the
opposite: "The survivor will stop earning you points" once voted out.

`data/scoring.json` currently uses the rules-page number, because that page
is titled the official rules and is the more specific source. Treat it as
unconfirmed until a scored episode shows which page is right. If you can
see your own score breakdown after episode 1, check whether an eliminated
roster pick still added points that week.

## Open questions — need the account or draft page (behind login)

The local session read the public rules and FAQ pages, but could not sign in
to the league (see below), so it could not open the draft or account pages.
These remain open:

1. **Roster size.** Not stated on the rules or FAQ page. `data/scoring.json`
   -> `outplay.roster_size` is `null`. Read it off the draft page once
   signed in.
2. **Can the roster be edited during the season, or is the draft final?**
   The FAQ says a league cannot be *left* once drafting begins — a
   different question from whether the roster itself can be changed.
   Unconfirmed.
3. Resolved — see Outlast above. The bonus does not pay for second or
   third; it is a streak, not a placement payout.
4. Resolved — the deadline is "before the episode airs on the US East
   coast," i.e. 20:00 ET Wednesday.
5. **Double boot / split tribal.** Not addressed on the rules page directly.
   The vote rule is written per-castaway, not per-episode, so a double boot
   most likely lets you score on both names if you put points on both —
   but this is a reading of the rule, not a confirmation.
6. **Tribe swap budget.** The rule reads "10 points per tribe, each week."
   A swap into three tribes should scale the budget to 30 points that week
   by the same reading. Not separately confirmed.
7. Resolved — quitting, medical evacuation, and production removal all do
   **not** count as "voted out" for vote points.

## Why standings and the draft are still not confirmed

The signed-in Chrome profile recon ran against (`malcolm.laws@gmail.com`,
Google-signed-in) turned out **not** to be signed in to
`fantasysurvivorgame.com` itself — the league site uses its own
email/password login, separate from Google. The group page returned a
login form, not standings.

Creating a new account on the site is blocked by this environment's own
safety controls (it flagged it as a real-world external transaction) even
with direct authorization in the chat. That needs a setting change on your
end, not more retries from here. See `docs/UNLOCK.md` for what changes once
a session has a real, signed-in session.

## Season facts

- Survivor 51, "The Open Era", on CBS.
- Premiere: Wednesday 23 September 2026, 20:00-22:00 ET.
- Then: Wednesdays, 20:00-21:30 ET, from 30 September 2026.
- Cast: 21 castaways. The largest start in the show's history.
- Tribes: two at the start. Reported as Savu (purple) and Toka (yellow).
- Projected finale: 16 December 2026 — 13 weekly episodes premiere to
  finale, matching the site's 13-point Outlast cap.

The tribe rosters were not public before the premiere. `data/state.json`
holds no tribe assignments. Add them after episode 1.

Jeff Probst calls the season "the open era". Any past twist can return, at
any time, in any order. Expect the schedule to change.
