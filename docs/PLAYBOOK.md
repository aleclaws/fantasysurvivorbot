# Weekly playbook

Survivor 51 airs on Wednesdays at 20:00 ET. The league closes the votes when
the episode starts. Do this sequence each Wednesday.

## Before the premiere, once

1. Open the league. Use the join link in `data/league.json`.
2. Open the rules page. Correct `data/scoring.json`. See `docs/RULES.md`.
3. Count the other players. Write the number in `data/league.json`.
4. Run `python3 -m fsb board`. Draft from the top of the list.
5. Write your roster into `my_draft` in `data/state.json`.
6. Run `python3 -m fsb mvp`. Set `my_mvp` in `data/state.json`.
   The Sole Survivor pick pays for a streak of consecutive episodes correct,
   counted back from the final, and you may change it at any time for free.
   Re-run this step after every update, not only once before the premiere —
   see `docs/RULES.md`.

## After each episode

Do these steps on Thursday. Do not wait until Wednesday.

1. Record the boot:

   ```
   python3 -m fsb record <name>
   ```

   This marks the castaway as out. It also moves to the next episode.

2. Add the tribe assignments, after episode 1 and after each swap:

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

4. Record idols. Add the id to `idols` in `data/state.json`.

5. Update the standings. Copy your score and the other scores from the site
   into `data/league.json`. **Do this step.** The engine changes its advice
   from the standings. Without them it assumes everybody is level.

## On Wednesday, before 20:00 ET

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

3. Type the allocation into the site. One tribe at a time.

4. Confirm that the site accepted the votes before 20:00 ET.

## If you are short of time

Run `python3 -m fsb picks` and copy the output. The stale data costs you
accuracy. A missed deadline costs you the whole week.

## Rule changes to watch

Survivor 51 starts 21 castaways in two tribes. The split is uneven. Watch for
these events, and read `docs/RULES.md` question 5 and question 6:

- A double boot. You may score from two castaways in one week.
- A split tribal council.
- A tribe swap into three tribes. Your budget then becomes 30 points.

Set `merged` to `true` in `data/state.json` on merge night. The engine does
not detect the merge. It changes every hazard weight when you set the flag.
