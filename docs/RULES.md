# Scoring rules

## How this page was made

A local Claude Code session read `rules.html` and `faq.html` directly on
2026-09-17, and later signed in to the league with a real account and read
`draft.html`, `sole-survivor.html`, and `vote.html` too. The text below is
quoted from those pages, saved at `data/site/`. `data/scoring.json` holds
the same numbers in a form the code reads. See `docs/UNLOCK.md` for how the
sign-in happened.

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

## Out-of-game points — resolved

The rules page says a castaway keeps earning 1 point per episode after
they leave, including the episode they leave, up to 13. The FAQ says a
drafted survivor "will stop earning you points". The standings page
settles it: it has an **Out** column titled "Extra points gained for
Survivors voted out", and its markup comments "Extra points earned by both
survivors being out of game". The FAQ answer is stale.

This changes draft strategy. An early boot still banks about 13 points, so
an episode in the game is worth only its gameplay points minus the 1 point
the castaway would earn anyway once out. That margin is large before the
merge (tribe challenge points go to every tribe member) and small after
it. Draft value is mostly "reaches the merge", and the gap between the top
ten draft picks is about 2 points. The weekly vote, where one correct
all-in is worth 10, is where this league is decided.

## Open questions — status after signing in

1. **Roster size.** Resolved: **2**. `howto-draft.html`: "Each player will
   draft 2 Survivors." Exclusive snake draft over two rounds, draft order
   random, run automatically at the draft time (Sep 23, 8:00 PM EDT) from
   each player's preference order. **Correction:** an earlier version of
   this file said 3. That was inferred from the three empty drop-slots on
   `draft.html`, which `js/draft-helper.js` shows are only UI placeholders.
2. **Can the roster be edited during the season, or is the draft final?**
   Still open. The preference *order* can be changed "at any time until the
   draft begins" (`howto-draft.html`, and confirmed - `tools/submit.py`
   overwrote it and read it back). Nothing on the site says the 2 drafted
   castaways can be swapped afterwards.
3. Resolved — see Outlast above. The bonus does not pay for second or
   third; it is a streak, not a placement payout.
4. Resolved — the deadline is "before the episode airs on the US East
   coast," i.e. 20:00 ET Wednesday.
5. **Double boot / split tribal.** Not addressed on the rules page directly.
   The vote rule is written per-castaway, not per-episode, so a double boot
   most likely lets you score on both names if you put points on both —
   but this is a reading of the rule, not a confirmation.
6. **Tribe swap budget.** The rule reads "10 points per tribe, each week."
   Confirmed structurally: pre-tribe-reveal, `vote.html` treats the whole
   21-castaway cast as one pool with a single 10-point budget (tribe index
   1). A swap into three tribes should scale the budget to 30 points that
   week the same way, by direct reading of the field-naming pattern
   (`votenum<episode>-<tribe>-<survivor>`) - `tools/submit.py`'s
   `parse_vote_fields` reads this live each week instead of assuming a
   fixed tribe count, so this will keep working through a swap without a
   code change. Not separately confirmed by seeing an actual swap yet.
7. Resolved — quitting, medical evacuation, and production removal all do
   **not** count as "voted out" for vote points.

## Standings and the draft are confirmed

A local session signed in with a real account (`malcolm.laws+ai@gmail.com`)
on 2026-09-17, joined the league "identos" (group code 411E-3E80-5B0C, 3
opponents, all tied at 0 before episode 1), and read the real draft,
sole-survivor, and vote pages. See `docs/UNLOCK.md` for exactly how.

**The 3-opponent count is provisional, not final.** The user confirmed on
2026-09-18 that not everyone who will join this league has signed up yet.
The site gives no way to see pending invites - `invite.html` only shows
the shareable group code, nothing about who has it or when they'll use it.
`python3 tools/submit.py standings` re-reads the real membership each time
it runs and rebuilds `data/league.json` from however many rows actually
exist, so new joiners get picked up automatically. Re-run it before every
weekly decision, not just once.

The draft preference order, Sole Survivor pick, and episode 1's vote were all
submitted through `tools/submit.py` and verified against a fresh read of
the site.

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
