#!/usr/bin/env python3
"""Submit picks to fantasysurvivorgame.com and verify they were saved.

Every URL, form field, and helper JS function this module calls was read
from the live, authenticated site on 2026-09-17 (data/site/*.html, plus
js/draft-helper.js and js/vote-helper.js, fetched directly - see
docs/RULES.md). Nothing here is a guessed selector.

Each submit_* function re-reads the page after submitting and raises
SubmitError if the change did not stick, instead of trusting the POST.

Credentials come only from the FSG_EMAIL / FSG_PASSWORD environment
variables. Never put them in code, in data/, or in a commit.

Usage:

    pip install playwright && playwright install chromium
    export FSG_EMAIL=... FSG_PASSWORD=...

    python3 tools/submit.py sole-survivor eric
    python3 tools/submit.py draft            # full board order, best to worst
    python3 tools/submit.py vote             # this week's fsb picks
    python3 tools/submit.py verify           # re-read and print current state
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
BASE = "https://www.fantasysurvivorgame.com"

sys.path.insert(0, str(ROOT))


class SubmitError(RuntimeError):
    """A submission could not be verified against a re-read of the page."""


# --------------------------------------------------------------- data glue

def load_site_ids() -> Dict[str, int]:
    """engine castaway id -> fantasysurvivorgame.com's numeric survivor id."""
    with open(DATA / "season51.json", encoding="utf-8") as fh:
        meta = json.load(fh)
    return {row["id"]: row["site_survivor_id"] for row in meta["cast"]
            if "site_survivor_id" in row}


def site_ids_to_engine_ids() -> Dict[int, str]:
    return {v: k for k, v in load_site_ids().items()}


# --------------------------------------------------------- pure parsing/build
#
# These take raw HTML/strings and touch no network, so they are unit tested
# directly against the fixtures in data/site/.

def build_draft_action_url(ordered_site_ids: List[int]) -> str:
    """The exact action URL draft.html's own JS builds as cards are picked.

    See js/draft-helper.js: rebuildActionURL() appends "&<survivorId>" for
    every pick, in order, onto "draft.html?satisfied=yes".
    """
    return "draft.html?satisfied=yes" + "".join(f"&{i}" for i in ordered_site_ids)


VOTE_FIELD_RE = re.compile(r"votenum(\d+)-(\d+)-(\d+)")


def parse_vote_fields(html: str) -> Dict[int, Tuple[str, str]]:
    """survivor_id -> (episode, tribe_index) for every vote input on the page.

    Reads the page's own field-naming convention instead of assuming a fixed
    tribe index, so this keeps working across a tribe swap or merge, when
    the site changes how many tribe buckets exist.
    """
    return {int(sid): (ep, tribe) for ep, tribe, sid in VOTE_FIELD_RE.findall(html)}


def parse_draft_picklist(html: str) -> List[int]:
    """The site_survivor_ids currently saved in the picklist, in order.

    Each saved pick renders server-side as <div id="picked<id>" ...>; the
    permanent empty slots render as id="placeholder<n>" instead.
    """
    return [int(m) for m in re.findall(r'id="picked(\d+)"', html)]


def count_draft_placeholders(html: str) -> int:
    """How many open roster slots the draft page shows right now."""
    return len(re.findall(r'id="placeholder\d+"', html))


def parse_sole_survivor_confirmation(body_text: str) -> bool:
    return "chosen as Sole Survivor" in body_text


ROW_RE = re.compile(r'<tr( id="leaderboard-self")?[^>]*>(.*?)</tr>', re.S)
TRIBENAME_RE = re.compile(r'<span class="player-tribename">([^<]*)</span>')
REALNAME_RE = re.compile(r'<span class="player-realname">([^<]*)</span>')
POINTS_RE = re.compile(r'<td class="points">\s*([^<]*?)\s*</td>')


def parse_standings(html: str) -> List[Dict[str, object]]:
    """One row per league member: is_self, tribe_name, real_name, total.

    Total is always the last "points" cell in the row, which stays true
    regardless of how many stat columns the site shows (it has changed once
    already, gaining a Draft column once a draft actually happened).
    """
    tbody = re.search(r"<tbody>(.*?)</tbody>", html, re.S)
    if not tbody:
        return []
    out: List[Dict[str, object]] = []
    for is_self, row_html in ROW_RE.findall(tbody.group(1)):
        tribe = TRIBENAME_RE.search(row_html)
        real = REALNAME_RE.search(row_html)
        points = [p for p in POINTS_RE.findall(row_html) if p.strip()]
        total_text = points[-1] if points else "0"
        try:
            total = int(total_text)
        except ValueError:
            total = 0  # e.g. "-" for a stat that isn't scoreable yet
        out.append({
            "is_self": bool(is_self),
            "tribe_name": tribe.group(1) if tribe else "",
            "real_name": real.group(1) if real else "",
            "total": total,
        })
    return out


# ------------------------------------------------------------- Playwright IO
#
# Each of these takes an already-created, already-logged-in Playwright page.

def login(page, email: str, password: str) -> None:
    page.goto(f"{BASE}/login.html", wait_until="domcontentloaded", timeout=30000)
    page.fill("#email", email)
    page.fill("#password", password)
    page.keyboard.press("Enter")
    page.wait_for_load_state("domcontentloaded", timeout=15000)
    page.wait_for_timeout(800)
    if "login.html" in page.url:
        raise SubmitError("login failed - check FSG_EMAIL / FSG_PASSWORD")


def submit_sole_survivor(page, site_id: int) -> None:
    page.goto(f"{BASE}/sole-survivor.html?solesurvivor={site_id}",
              wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(1000)
    if not parse_sole_survivor_confirmation(page.inner_text("body")):
        raise SubmitError("sole survivor pick was not confirmed by the site")


def submit_draft_preferences(page, ordered_site_ids: List[int]) -> None:
    page.goto(f"{BASE}/draft.html", wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(500)
    action_url = build_draft_action_url(ordered_site_ids)
    page.evaluate(
        "(url) => { const f = document.getElementById('draftform'); "
        "f.action = url; f.submit(); }", action_url)
    page.wait_for_load_state("domcontentloaded", timeout=20000)
    page.wait_for_timeout(1000)
    verify_draft_preferences(page, ordered_site_ids)


def verify_draft_preferences(page, ordered_site_ids: List[int]) -> None:
    page.goto(f"{BASE}/draft.html", wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(800)
    saved = parse_draft_picklist(page.content())
    if saved != list(ordered_site_ids):
        raise SubmitError(
            f"draft preference order did not stick: sent {ordered_site_ids}, "
            f"site now shows {saved}")


def submit_vote(page, episode: int, allocation_by_site_id: Dict[int, int]) -> None:
    """Set every castaway's vote value and force an immediate save.

    Discovers each castaway's real (episode, tribe) field suffix from the
    live page instead of assuming tribe index 1, so this keeps working after
    a tribe swap changes how many vote pools there are.
    """
    page.goto(f"{BASE}/vote.html", wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(800)
    fields = parse_vote_fields(page.content())

    for site_id, points in allocation_by_site_id.items():
        if site_id not in fields:
            raise SubmitError(f"no vote field found for survivor {site_id} "
                               f"(episode {episode}) - voting may be closed")
        ep, tribe = fields[site_id]
        page.evaluate(
            "([sel, val]) => { const el = document.getElementById(sel); "
            "el.value = val; el.dispatchEvent(new Event('input', {bubbles: true})); }",
            [f"votenum{ep}-{tribe}-{site_id}", str(points)])
    page.wait_for_timeout(300)
    page.evaluate("window.submitVotes()")
    page.wait_for_timeout(1500)
    verify_vote(page, episode, allocation_by_site_id)


def verify_vote(page, episode: int, allocation_by_site_id: Dict[int, int]) -> None:
    page.goto(f"{BASE}/vote.html", wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(800)
    for site_id, points in allocation_by_site_id.items():
        got = page.eval_on_selector(
            f'input[name^="votenum{episode}-"][name$="-{site_id}"]',
            "el => el.value")
        if int(got or 0) != points:
            raise SubmitError(
                f"vote for survivor {site_id} did not stick: sent {points}, "
                f"site now shows {got!r}")


def sync_league_standings(page) -> dict:
    """Read the real standings and write my_score/opponent_scores.

    Preserves every other field in league.json (field_sharpness and
    friends) - this only touches the numbers the site itself reports.
    """
    page.goto(f"{BASE}/standings.html", wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(800)
    rows = parse_standings(page.content())
    self_row = next((r for r in rows if r["is_self"]), None)
    if self_row is None:
        raise SubmitError("could not find my own row in the standings table")

    league_path = DATA / "league.json"
    with open(league_path, encoding="utf-8") as fh:
        league = json.load(fh)
    league["my_score"] = self_row["total"]
    league["opponent_scores"] = [r["total"] for r in rows if not r["is_self"]]
    league["num_opponents"] = len(league["opponent_scores"])
    with open(league_path, "w", encoding="utf-8") as fh:
        json.dump(league, fh, indent=2)
        fh.write("\n")
    return league


def join_group(page, group_code: str) -> None:
    page.goto(f"{BASE}/group-start.html", wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(500)
    page.fill("#groupcode", group_code)
    page.keyboard.press("Enter")
    page.wait_for_load_state("domcontentloaded", timeout=15000)
    page.wait_for_timeout(800)
    body = page.inner_text("body")
    if "joined" not in body.lower() and "already" not in body.lower():
        raise SubmitError(f"group join was not confirmed: {body[:200]!r}")


# -------------------------------------------------------------------- CLI

def _make_page():
    from playwright.sync_api import sync_playwright
    email = os.environ.get("FSG_EMAIL")
    password = os.environ.get("FSG_PASSWORD")
    if not email or not password:
        raise SystemExit("set FSG_EMAIL and FSG_PASSWORD (never store them "
                          "in this repository)")
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context()
    page = ctx.new_page()
    login(page, email, password)
    return pw, browser, page


def cmd_sole_survivor(args) -> None:
    from fsb.model import Season
    site_ids = load_site_ids()
    cid = args.who if args.who in site_ids else None
    if cid is None:
        raise SystemExit(f"{args.who!r} is not a known castaway id")
    pw, browser, page = _make_page()
    try:
        submit_sole_survivor(page, site_ids[cid])
        print(f"confirmed: {cid} set as Sole Survivor pick")
    finally:
        browser.close()
        pw.stop()


def cmd_draft(args) -> None:
    from fsb.draft import draft_board
    from fsb.model import Season
    site_ids = load_site_ids()
    rows = draft_board(Season())
    order = [site_ids[cid] for cid, _pts, _p in rows if cid in site_ids]
    pw, browser, page = _make_page()
    try:
        submit_draft_preferences(page, order)
        print(f"confirmed: draft preference order saved for {len(order)} castaways")
    finally:
        browser.close()
        pw.stop()


def cmd_standings(args) -> None:
    pw, browser, page = _make_page()
    try:
        league = sync_league_standings(page)
        print(f"my_score={league['my_score']}  "
              f"opponent_scores={league['opponent_scores']}")
    finally:
        browser.close()
        pw.stop()


def cmd_vote(args) -> None:
    from fsb.allocate import optimise
    from fsb.model import Season
    with open(DATA / "league.json", encoding="utf-8") as fh:
        league = json.load(fh)
    site_ids = load_site_ids()
    season = Season()
    alloc, _diag = optimise(season, league, sims=args.sims or 4000)
    by_site_id: Dict[int, int] = {}
    for _tribe, a in alloc.items():
        for cid, pts in a.items():
            if pts and cid in site_ids:
                by_site_id[site_ids[cid]] = pts
    pw, browser, page = _make_page()
    try:
        submit_vote(page, season.episode, by_site_id)
        print(f"confirmed: episode {season.episode} vote saved "
              f"({len(by_site_id)} castaways)")
    finally:
        browser.close()
        pw.stop()


def cmd_verify(args) -> None:
    pw, browser, page = _make_page()
    try:
        page.goto(f"{BASE}/draft.html", wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(500)
        picks = parse_draft_picklist(page.content())
        engine_ids = site_ids_to_engine_ids()
        print("draft preference order:",
              [engine_ids.get(i, i) for i in picks])
        page.goto(f"{BASE}/vote.html", wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(500)
        fields = parse_vote_fields(page.content())
        html = page.content()
        for site_id in fields:
            val = page.eval_on_selector(
                f'#votenum{fields[site_id][0]}-{fields[site_id][1]}-{site_id}',
                "el => el.value")
            if val:
                print(f"  vote: {engine_ids.get(site_id, site_id)} = {val}")
    finally:
        browser.close()
        pw.stop()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("sole-survivor", help="set the Sole Survivor pick")
    p.add_argument("who", help="castaway id, e.g. eric")
    p.set_defaults(func=cmd_sole_survivor)

    p = sub.add_parser("draft", help="submit the full draft preference order")
    p.set_defaults(func=cmd_draft)

    p = sub.add_parser("standings", help="read the real standings into league.json")
    p.set_defaults(func=cmd_standings)

    p = sub.add_parser("vote", help="submit this week's vote allocation")
    p.add_argument("--sims", type=int, default=0)
    p.set_defaults(func=cmd_vote)

    p = sub.add_parser("verify", help="re-read and print what the site has saved")
    p.set_defaults(func=cmd_verify)

    args = ap.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
