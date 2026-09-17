#!/bin/bash
# Weekly automation: pull the cloud routine's state, submit this week's
# picks to fantasysurvivorgame.com, verify, and push.
#
# Scheduled by ~/Library/LaunchAgents/com.fantasysurvivorbot.weekly.plist,
# Wednesdays at 18:30 ET - after the cloud routine's 14:05 ET push (which
# researches the last episode and computes picks, but cannot submit them),
# and before the 20:00 ET pick deadline.
#
# Requires .env in the repo root (FSG_EMAIL, FSG_PASSWORD - gitignored,
# never committed). See docs/PLAYBOOK.md.

set -euo pipefail

REPO="/Users/alec/fantasysurvivorbot"
LOG="$REPO/tools/weekly_submit.log"

cd "$REPO"
exec >> "$LOG" 2>&1

echo "=== $(date) ==="

git pull --ff-only origin claude/sleepy-heisenberg-7mhgml

source .venv/bin/activate
set -a
source .env
set +a

TESTS_OK=1
python3 -m unittest discover -s tests || TESTS_OK=0

python3 tools/submit.py standings
python3 tools/submit.py vote
python3 tools/submit.py verify

if [ "$TESTS_OK" = "1" ]; then
	if ! git diff --quiet; then
		git add data/state.json data/league.json
		git commit -m "chore: weekly picks submitted ($(date +%Y-%m-%d))

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
		git pull --ff-only origin claude/sleepy-heisenberg-7mhgml
		git push origin claude/sleepy-heisenberg-7mhgml
	fi
else
	echo "TESTS FAILED - picks were still submitted (deadline-bound), but nothing was pushed. Investigate before next Wednesday."
fi

echo "=== done ==="
