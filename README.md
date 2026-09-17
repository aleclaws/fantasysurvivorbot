# Fantasy Survivor Bot

A decision engine for a fantasysurvivorgame.com league. Season: Survivor 51.

The season starts on 23 September 2026. The league sends picks before each
episode. This repository makes those picks.

## Important limit

The build machine cannot open `fantasysurvivorgame.com`. The network policy
blocks the domain. Read `docs/RULES.md` before you trust the numbers.

Two results follow from this limit:

1. This tool cannot send your picks. You must type them into the website.
2. The draft scoring constants are an assumption, not a fact. Confirm them.

The vote scoring rules are reliable. The search index shows the text of the
site's own rules page. See `docs/RULES.md` for each rule and its confidence.

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

- `docs/RULES.md` — the scoring rules, and how much to trust each one
- `docs/STRATEGY.md` — why the engine does not maximise points
- `docs/PLAYBOOK.md` — what to do each Wednesday

## Tests

```
python3 -m unittest discover -s tests -v
```
