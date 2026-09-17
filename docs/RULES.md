# Scoring rules

## How this page was made

The machine that built this repository cannot open
`fantasysurvivorgame.com`. The network egress policy rejects the domain. It
also rejects `en.wikipedia.org` and the television news sites. Web search
still works. The rules below come from the search index of the site's own
rules page, plus general reporting.

Do not treat the low-confidence rules as facts. Open the site and confirm
them. Then correct `data/scoring.json`. The code reads that file at run time.
Every recommendation changes when you change a number in it.

## High confidence

The search index returns this text from the site's rules page.

You score points in three ways:

- **Outwit** — predict the castaway who is voted out each week.
- **Outplay** — draft castaways who score points through their gameplay.
- **Outlast** — predict the Sole Survivor.

The weekly vote works as follows:

- You get **10 points for each tribe**, each week.
- You divide those 10 points between the castaways of that tribe.
- You can put a maximum of **10 points on one castaway**.
- You score the points that you put on the castaway who is voted out.
- The votes reset after the site scores the episode.
- You must send the votes **before the episode starts on the US East coast**.

The highest total score at the end of the season wins.

## Low confidence

The site describes a draft and a Sole Survivor bonus. The exact values are not
in the search index. The values in `data/scoring.json` follow the usual format
of this type of game. Treat them as placeholders.

- Roster size: 4 castaways
- Survive one week before the merge: 1 point
- Survive one week after the merge: 3 points
- Tribe immunity win: 3 points; tribe reward win: 2 points
- Individual immunity win: 3 points; individual reward win: 1 point
- Find an idol: 2 points; play an idol correctly: 1 point
- Sole Survivor bonus: 30 points for first, 20 for second, 10 for third

## Open questions

Answer these on the site, then correct `data/scoring.json`.

1. How many castaways does the draft roster hold?
2. Can you change the roster during the season, or is the draft final?
3. Does the Sole Survivor bonus pay for second and third place?
4. What is the exact deadline? The rules say "before the episode airs".
5. What happens in a double boot? Do you score for both castaways?
6. What happens at a tribe swap? How does the 10-point budget divide then?
7. Does a quit or a medical evacuation count as "voted out"?

Question 5 and question 6 matter most. Survivor 51 starts 21 players in two
tribes. That is an uneven split. A swap or a split tribal is likely.

## Season facts

- Survivor 51, "The Open Era", on CBS
- Premiere: Wednesday 23 September 2026, 20:00–22:00 ET
- Then: Wednesdays, 20:00–21:30 ET, from 30 September 2026
- Cast: 21 castaways. This is the largest start in the show's history.
- Tribes: two at the start. Reported as Savu (purple) and Toka (yellow).
- Expected finale: 16 December 2026

The tribe rosters were not public before the premiere. `data/state.json`
holds no tribe assignments. Add them after episode 1.

Jeff Probst calls the season "the open era". Any past twist can return, at any
time, in any order. Expect the schedule to change.
