# Fantasy Survivor Bot

A decision engine for a fantasysurvivorgame.com league. Season: Survivor 51.

The season starts on 23 September 2026. The league sends picks before each
episode. This repository makes those picks.

## Status

A local session ran `tools/recon.py` on 2026-09-17 and read the site's real
rules and FAQ pages. `data/scoring.json` now holds the real scoring
constants, not a guess. Read `docs/RULES.md` for every rule and its
confidence.

What is still blocked:

- **No signed-in session.** The Chrome profile recon ran against was not
  signed in to `fantasysurvivorgame.com` (a separate login from Google).
  So the standings, the draft page, and the pick form are still unread.
- **This tool still cannot send your picks.** `tools/submit.py` needs the
  real pick form to be written safely; it does not exist yet, because
  inventing selectors for a form nobody has opened would fail silently
  later.
- Creating a new account from a session is blocked by this environment's
  own safety controls, independent of anything typed in chat.

**To remove this limit, read `docs/UNLOCK.md`.**

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

A scheduled routine runs each Wednesday at 14:00 ET. It does this:

1. Searches the web for the result of the last episode.
2. Updates `data/state.json`.
3. Calculates the picks.
4. Pushes the new state to this branch.
5. Sends you the picks by push notification and email.

The first run is 23 September 2026, the day of the premiere.

You must still type the picks into the website. The routine cannot reach it.

To stop the routine, delete it from your routines list on claude.ai.

## Tests

```
python3 -m unittest discover -s tests -v
```
