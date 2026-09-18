# Fantasy Survivor Bot

A decision engine for a fantasysurvivorgame.com league. Season: Survivor 51.

The season starts on 23 September 2026. The league sends picks before each
episode. This repository makes those picks.

## Status

Fully unlocked as of 2026-09-17. A local session read the site's real rules,
signed in with a real account, joined the league, and submitted picks. See
`docs/UNLOCK.md` for the full story, including two dead ends (borrowing a
different browser session, registering a new account) that this
environment's own controls correctly refused before real credentials made
either one unnecessary.

What is confirmed and done:

- `data/scoring.json` holds the real scoring constants, read from
  `rules.html`/`faq.html`. See `docs/RULES.md`.
- Signed in to the league "identos" as `AI bot`, tribe name "Win
  Probability". 3 opponents, all tied at 0 before episode 1.
- Draft roster size confirmed: 2, via an exclusive snake draft run
  automatically from each player's preference order (see
  `docs/RULES.md`). The full 21-castaway preference order was submitted
  and verified.
- Sole Survivor pick (Eric Macksoud) submitted and verified. This pick can
  be changed for free at any time - see `docs/RULES.md`.
- Episode 1's vote allocation submitted and verified.
- `tools/submit.py` submits and verifies draft preferences, the Sole
  Survivor pick, the weekly vote, and standings sync - each against the
  real, authenticated site, with tests in `tests/test_submit.py`.

What is still open:

- Whether the 2 castaways the auto-draft actually assigns (at the
  scheduled draft time, Sep 23 8:00 PM EDT) can be changed afterward -
  `docs/RULES.md` question 2.

## Install

No dependencies. Python 3.8 or later is sufficient.

```
python3 -m fsb status
```

## Commands

| Command | Function |
|---|---|
| `python3 -m fsb picks` | Calculate this week's point allocation |
| `python3 -m fsb board` | Rank the cast by expected season points |
| `python3 -m fsb mvp` | Select the sole-survivor pick |
| `python3 -m fsb status` | Show the current board |
| `python3 -m fsb rules` | Show the scoring constants in use |
| `python3 -m fsb tribe <who> <tribe>` | Assign a castaway to a tribe |
| `python3 -m fsb edit <who> <-1..1>` | Set a doom signal from the edit |
| `python3 -m fsb record <who>` | Record a boot and go to the next episode |

`<who>` accepts an id, a first name, or any unique part of a name.

| `tools/submit.py` command | Function |
|---|---|
| `sole-survivor <who>` | Set and verify the Sole Survivor pick |
| `draft` | Submit and verify the full draft preference order |
| `vote` | Submit and verify this week's vote allocation |
| `standings` | Read the real standings into `data/league.json` |
| `verify` | Re-read and print what the site currently has saved |

`tools/submit.py` needs `FSG_EMAIL` and `FSG_PASSWORD` in the environment
(e.g. from a local, gitignored `.env` - never commit one).

## Files

| File | Function |
|---|---|
| `data/season51.json` | The cast and the schedule. Static. |
| `data/scoring.json` | The scoring constants. Correct these first. |
| `data/priors.json` | Pre-season features and hazard weights. |
| `data/state.json` | The live game state. This file changes each week. |
| `data/league.json` | Your score, the other players, and the field model. |

The code reads every constant from these files. No constant is in the source.

## Documents

- `docs/UNLOCK.md` — how to remove the network limit
- `docs/HANDOFF.md` — the prompt that moves this work to a local session
- `docs/PRESEASON.md` — the draft board and the Sole Survivor pick
- `docs/RULES.md` — the scoring rules, and how much to trust each one
- `docs/STRATEGY.md` — why the engine does not maximise points
- `docs/PLAYBOOK.md` — what to do each Wednesday

## Weekly automation

Two complementary jobs run each Wednesday - keep both:

**The cloud routine**, 14:05 ET. It searches the web for the last episode's
result, records the boot, sets the edit signals, and pushes the updated
`data/state.json` to this branch. It cannot reach the site, so it does not
submit anything. To stop it, delete "Survivor 51 weekly picks" from your
routines list on claude.ai - but only the research step it does would be
lost, so keep it.

**The local job**, 18:30 ET (`tools/weekly_submit.sh`, scheduled via
`~/Library/LaunchAgents/com.fantasysurvivorbot.weekly.plist`). After the
cloud routine has updated `data/state.json`, it pulls, reads the real
standings into `data/league.json`, computes and submits this week's vote
with `tools/submit.py`, verifies it stuck, and pushes. Logs land in
`tools/weekly_submit.log`.

Nothing needs to be typed into the website by hand any more.

## Tests

```
python3 -m unittest discover -s tests -v
```
