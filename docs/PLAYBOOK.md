# Weekly playbook

Survivor 51 airs on Wednesdays at 20:00 ET. The league closes the votes when
the episode starts. Two automated jobs now do most of this sequence - see
the README's Weekly automation section. This page describes what they do,
and how to do any of it by hand if you need to.

## Before the premiere, once — done on 2026-09-17

1. Joined the league (see `docs/UNLOCK.md`).
2. Corrected `data/scoring.json` from the real rules page.
3. Read the real opponent count into `data/league.json`: 3.
4. Ran `python3 -m fsb board` and submitted the full preference order with
   `python3 tools/submit.py draft`.
5. Ran `python3 -m fsb mvp` and submitted the pick with
   `python3 tools/submit.py sole-survivor eric`.
   The Sole Survivor pick pays for a streak of consecutive episodes correct,
   counted back from the final, and you may change it at any time for free.
   Re-run this whenever the standings or edit signals move — see
   `docs/RULES.md`. `my_draft` in `data/state.json` stays empty until the
   site's auto-draft actually assigns the 2 roster slots on Sep 23.

## After each episode

Do these steps on Thursday. Do not wait until Wednesday.

1. Record the boot:

   ```
   python3 -m fsb record <name>
   ```

   This marks the castaway as out. It also moves to the next episode.

2. Tribe assignments no longer need doing by hand. `tools/submit.py vote`
   reads the pools, the tribe names and the votable cast straight off the
   live vote page before it allocates, so a swap or a merge is picked up
   automatically. The manual command still works if you want state.json
   correct for `fsb status`:

   ```
   python3 -m fsb tribe <name> Savu
   ```

3. Set the edit signals. This step gives the largest improvement. Use `-1` to
   `+1`:

   ```
   python3 -m fsb edit <name> 0.8
   ```

   Use these values:

   | Signal | Value |
   |---|---|
   | The episode gives a castaway a sudden backstory | +0.6 |
   | Other castaways say the name at camp | +0.8 |
   | The castaway is on the wrong side of the numbers | +0.7 |
   | The castaway has no content at all | +0.3 |
   | The castaway has a clear winner edit | −0.6 |
   | The castaway holds an idol | use `idols` instead |
   | The castaway is injured and medical is involved | use `medevac_risk` |

   `medevac_risk` in `data/state.json` is a separate 0..1 chance that a
   castaway leaves by medical or a quit rather than by vote. It is not an
   edit signal: the rules pay NOBODY vote points for a departure like that,
   so points parked on that castaway score nothing. Set it from footage,
   not from a synopsis - "an injury threatens to send a player home" is how
   every promo is written, and Brady was carried at 0.5 on that basis while
   the actual first-look footage had him bandaged and competing.

4. Record idols. Add the id to `idols` in `data/state.json`.

5. Update the standings, and check whether the site changed the rules:

   ```
   python3 tools/submit.py rules-check
   python3 tools/submit.py standings
   ```

   `rules-check` counts the scored actions on the live rules page against
   `data/scoring.json`. The site ADDS rules mid-season - the open era keeps
   reviving twists and each one gets priced - and three went unnoticed for a
   week. The league activity feed logs each one.

   This reads your score and the other scores directly off the site into
   `data/league.json`. **Do this step.** The engine changes its advice from
   the standings. Without them it assumes everybody is level.

The cloud routine (14:05 ET Wednesday) does steps 1-4 automatically each
week by searching the web for the episode result - see the README.

## On Wednesday, before 20:00 ET

The local job (`tools/weekly_submit.sh`, 18:30 ET) does this automatically:
reads the real standings, computes the picks, submits them, verifies, and
pushes. To do it by hand instead:

1. Run the picks:

   ```
   python3 -m fsb picks
   ```

2. Read the two probabilities in the output. They tell you what the engine is
   doing:

   - The two numbers are equal: the engine plays for points. You are level or
     ahead early.
   - `P(win league)` is higher than the EV line: the engine is buying
     variance. You are behind, or the season is nearly over.

3. Submit and verify:

   ```
   python3 tools/submit.py vote
   ```

4. Re-check the Sole Survivor pick, but do not churn it:

   ```
   python3 -m fsb mvp
   python3 tools/submit.py sole-survivor <id>   # only if clearly better
   ```

   The bonus pays 1 point per CONSECUTIVE episode the correct winner was
   your standing pick, counting back from the final. Switching resets that
   run, so it is worth doing for a real gap in P(win) and not for a
   rounding difference.

## If you are short of time

Run `python3 tools/submit.py vote` directly - it recomputes from the
current `data/state.json` and `data/league.json` and submits in one step.
Stale data costs accuracy. A missed deadline costs the whole week.

## Rule changes to watch

Survivor 51 starts 21 castaways in two tribes. The split is uneven. Watch for
these events, and read `docs/RULES.md` question 5 and question 6:

- A double boot. You may score from two castaways in one week.
- A split tribal council.
- A tribe swap into three tribes. Your budget then becomes 30 points.

Set `merged` to `true` in `data/state.json` on merge night. The engine does
not detect the merge. It changes every hazard weight when you set the flag.

## The league is not full yet

A site-wide banner says the draft runs again each Wednesday at 20:00 ET for
late signups, so `num_opponents` will grow. It re-runs AT the lock, not
before it, so each Wednesday 18:30 job submits against the opponent count
as it stands that evening. A jump the following week is expected. See
`docs/RULES.md`.
