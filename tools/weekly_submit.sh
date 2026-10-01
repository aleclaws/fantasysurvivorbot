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

set -uo pipefail

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

# Dropping `set -e` (so a git hiccup cannot abort a run that has already
# submitted) also removed the thing that stopped the script on a FAILED
# submission - it would carry on and exit 0, so a week that scored nothing
# looked like a clean run. Failures are tracked explicitly instead, and the
# vote, which is the only step with a deadline, gets one retry and decides
# the exit code.
STATUS=0

# Deadline first. The vote closes at 20:00 ET and is the only step with a
# deadline; rules-check and standings only improve the picks. On 2026-09-30
# the job started 9 minutes late onto a machine running 4x slow, spent close
# to an hour failing a standings sync, and still had not reached the vote
# with 27 minutes left. Past LOCK_GUARD_HHMM, skip straight to the vote.
# "Stale data costs accuracy. A missed deadline costs the whole week."
LOCK_GUARD_HHMM=1930
NOW_HHMM=$(date +%H%M)

if [ "$((10#$NOW_HHMM))" -ge "$((10#$LOCK_GUARD_HHMM))" ]; then
	echo "TIME GUARD: it is $NOW_HHMM, at or past $LOCK_GUARD_HHMM."
	echo "Skipping rules-check and standings to protect the 20:00 vote"
	echo "deadline. Picks come from the data already on disk."
	STATUS=1
else
	python3 tools/submit.py rules-check || {
		echo "RULES CHANGED - re-read rules.html into data/scoring.json"
		STATUS=1
	}
	python3 tools/submit.py standings || {
		echo "WARNING: standings sync failed - picks computed on stale scores"
		STATUS=1
	}
fi

if ! python3 tools/submit.py vote; then
	echo "vote submission failed, retrying once..."
	sleep 20
	if ! python3 tools/submit.py vote; then
		echo "########################################################"
		echo "# VOTE NOT SUBMITTED. This week scores ZERO unless it   #"
		echo "# is fixed before the 20:00 ET lock.                    #"
		echo "########################################################"
		STATUS=2
	fi
fi

python3 tools/submit.py verify || {
	echo "WARNING: could not verify what the site has saved"
	STATUS=1
}

if [ "$TESTS_OK" = "1" ]; then
	# Scope the check to the files actually committed. Checking the whole
	# tree meant the run's own log file made it look dirty, so the commit
	# ran with nothing staged, failed, and set -e killed the script before
	# the push - every week the picks did not change.
	if ! git diff --quiet -- data/state.json data/league.json; then
		git add data/state.json data/league.json
		git commit -m "chore: weekly picks submitted ($(date +%Y-%m-%d))

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
		git pull --ff-only origin claude/sleepy-heisenberg-7mhgml
		git push origin claude/sleepy-heisenberg-7mhgml
	else
		echo "no state change to commit"
	fi
else
	echo "TESTS FAILED - picks were still submitted (deadline-bound), but nothing was pushed. Investigate before next Wednesday."
fi

if [ "$STATUS" = "0" ]; then
	echo "=== done: picks submitted and verified ==="
else
	echo "=== done WITH PROBLEMS (status $STATUS) - read the log above ==="
fi
exit $STATUS
