# How to unlock the blocked features

## What is blocked

This repository was built in a Claude Code web session. That session sends
all traffic through an egress proxy. The proxy rejects
`fantasysurvivorgame.com`. It also rejects Wikipedia and the TV news sites.
Only web search works.

The account has one environment, named "Default". Its policy is "trusted
network access", which is a fixed allowlist. There is no second environment
to move to.

Three features stay locked because of this:

| Locked feature | Effect |
|---|---|
| Read `rules.html` | The draft scoring constants stay a guess |
| Read the standings | The engine assumes everybody is level |
| Send the picks | You must type them each week |

The first one is the most expensive. A wrong scoring constant beats any
amount of modelling.

## Path A — run Claude Code on your own machine

This is the better path. A local session uses your own network. No proxy
sits in front of it.

```
pip install playwright && playwright install chromium
python3 tools/recon.py --profile ~/.config/google-chrome/Default
```

Use the profile of a browser that is already signed in to the league. The
script then re-uses that session. You type no password, and this repository
stores no password.

If you prefer, use `--manual` instead. The script opens a browser, you sign
in, and you press Enter.

`tools/recon.py` saves these files to `data/site/`:

- `rules.txt` and `faq.txt` — the real scoring rules
- `group.txt` and `group.html` — the standings and the pick form
- `group_forms.json` — every input on the pick page

Then start a Claude Code session in this repository and say:

> read data/site/ and correct data/scoring.json, then write tools/submit.py

That session can write the submitter, because it can see the real form. This
one cannot. Inventing selectors for a page nobody has opened would produce
code that looks correct and fails silently.

## Path B — a new environment on the web

Create a second environment at claude.ai with a custom allowlist. Add
`fantasysurvivorgame.com` to it. Then move the weekly routine to it.

Path B unlocks the same three features. It needs your credentials in
environment variables, because a cloud browser has no session of yours to
re-use. Path A avoids that.

## The one thing that cannot be automated away

Submitting picks needs your league account. I cannot sign in to an account
without either a password or a signed-in browser session. There is no way
around that.

Path A makes it as small as possible: one command, on your machine, once.
After that the browser profile keeps the session and nothing else is needed.

## What changes after recon runs

1. `data/scoring.json` becomes fact instead of assumption. The draft board
   and the MVP pick then use real numbers.
2. `data/league.json` gets the real opponent count and the real scores. The
   engine needs these to decide between points and variance. Read
   `docs/STRATEGY.md`.
3. `tools/submit.py` becomes possible, and the weekly routine can close the
   loop without you.
