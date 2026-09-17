# Handoff prompt

Paste the block below into a Claude Code session on the local machine. That
machine can open `fantasysurvivorgame.com`. This repository was built in a
cloud session that cannot.

Keep this file. Use the same prompt again if the local session is lost.

---

I am handing you a fantasy Survivor project that a Claude Code cloud session
started. Your job is to win the league. The user does not want to do manual
steps. Do the work yourself and only ask when you truly cannot proceed.

REPOSITORY

    git clone https://github.com/aleclaws/fantasysurvivorbot
    cd fantasysurvivorbot
    git checkout claude/sleepy-heisenberg-7mhgml

Commit and push to that branch. Do not open a pull request.

Read these first, in this order. Do not rebuild what exists.

  README.md            what is built and how to run it
  docs/UNLOCK.md       what you can do that the cloud session could not
  docs/RULES.md        the scoring rules and how much to trust each one
  docs/STRATEGY.md     why the engine maximises P(win), not points
  docs/PLAYBOOK.md     the weekly procedure

WHAT ALREADY WORKS

A dependency-free Python engine, 25 passing tests:

    python3 -m unittest discover -s tests
    python3 -m fsb picks | board | mvp | status | rules
    python3 -m fsb record <who> | tribe <who> <tribe> | edit <who> <-1..1>

It models boot probability in two stages, and it maximises the probability
of finishing first rather than expected points. Physicality protects a
castaway before the merge and targets them after it.

THE LEAGUE

  Group code   411E-3E80-5B0C
  Join link    https://www.fantasysurvivorgame.com/group-join.html?groupcode=411E-3E80-5B0C
  Season       Survivor 51, CBS, Wednesdays 20:00 ET
  Premiere     23 September 2026
  Cast         21 castaways, two tribes, rosters not public before episode 1

YOUR TASKS, IN PRIORITY ORDER

1. Run the recon script. It needs a browser profile that is already signed
   in to the league site.

       pip install playwright && playwright install chromium
       python3 tools/recon.py --profile <path-to-a-signed-in-profile>

   Use `--manual` if the profile path does not work. Never store a password
   in the repository.

2. Correct `data/scoring.json` from `data/site/rules.txt`. This is the most
   valuable task. The draft and bonus constants are currently a documented
   guess. Answer the seven open questions in `docs/RULES.md`. Questions 5
   and 6 matter most, because 21 players in two tribes is an uneven split
   and a swap or a split tribal is likely.

3. Confirm the user has joined the league. Read the standings. Put the real
   opponent count and the real scores into `data/league.json`. The engine
   needs these to choose between scoring points and buying variance.

4. Do the draft, if it is still open, and set the Sole Survivor pick.

       python3 -m fsb board
       python3 -m fsb mvp

   Use the corrected constants, not the old ones. Write the roster into
   `my_draft` and the MVP into `my_mvp` in `data/state.json`. Then enter
   them on the site. Note that the draft leaders and the win-probability
   leaders are different castaways; `docs/PRESEASON.md` explains why.

5. Write `tools/submit.py`. Use the real form in `data/site/group.html` and
   `data/site/group_forms.json`. The cloud session did not write it,
   because inventing selectors for a page it could not open would fail
   silently later. Make the script verify what it sent and report a
   mismatch. Add tests.

6. Set up local weekly automation. Picks lock when the episode starts at
   20:00 ET on Wednesday. Run the job earlier that day. Follow
   `docs/PLAYBOOK.md`: research the last episode, record the boot, set the
   tribes, set the edit signals, update the standings, calculate the picks,
   submit them, verify, commit, push.

EXISTING AUTOMATION, AND A CONFLICT TO AVOID

A cloud routine already fires every Wednesday at 18:05 UTC, which is 14:05
ET. It researches the episode, calculates the picks, pushes to the same
branch, and notifies the user. It cannot submit anything.

So always `git pull` before you commit, or the two will conflict.

Once your local automation submits picks reliably, tell the user to delete
the routine named "Survivor 51 weekly picks" from their routines list on
claude.ai. Do not leave both running for long.

RULES

- Never invent an episode result, a standing, a scoring constant or a cast
  detail. If you cannot verify it, say so.
- Keep every constant in `data/`. Put none in the source.
- Run the tests before each push.
- Write in ASD-STE100 Simplified Technical English: short sentences, active
  voice, simple words, one instruction per sentence.
- Report the picks first, in a form the user can copy, then the reasoning.
