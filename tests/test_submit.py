"""Tests for tools/submit.py.

These cover the pure parsing/build functions only - the ones that touch no
network - against data/site/*.html, which were saved from the real,
authenticated site on 2026-09-17. They do not exercise login or the actual
POST/AJAX calls, since those need live credentials this test suite does not
have. See docs/RULES.md for how submit.py was verified against the live
site by hand.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "tools"))

import submit  # noqa: E402

SITE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "data", "site")


def _read(name: str) -> str:
    with open(os.path.join(SITE, name), encoding="utf-8") as fh:
        return fh.read()


class TestSiteIdMapping(unittest.TestCase):
    def test_every_castaway_has_a_site_id(self):
        ids = submit.load_site_ids()
        self.assertEqual(len(ids), 21)
        self.assertEqual(ids["eric"], 546)
        self.assertEqual(ids["brady"], 541)

    def test_mapping_is_a_bijection(self):
        ids = submit.load_site_ids()
        reverse = submit.site_ids_to_engine_ids()
        self.assertEqual(len(ids), len(reverse))
        for cid, sid in ids.items():
            self.assertEqual(reverse[sid], cid)


class TestBuildDraftActionURL(unittest.TestCase):
    def test_matches_the_sites_own_rebuildActionURL_format(self):
        # js/draft-helper.js appends "&<id>" per pick onto the base action.
        url = submit.build_draft_action_url([541, 553, 542])
        self.assertEqual(url, "draft.html?satisfied=yes&541&553&542")

    def test_empty_order_leaves_the_base_action(self):
        self.assertEqual(submit.build_draft_action_url([]),
                         "draft.html?satisfied=yes")


class TestParseVoteFields(unittest.TestCase):
    def test_finds_all_21_castaways_pre_tribe_reveal(self):
        fields = submit.parse_vote_fields(_read("vote.html"))
        self.assertEqual(len(fields), 21)
        # Pre-tribe-reveal, the whole cast is one pool: episode 1, tribe 1.
        self.assertEqual(fields[536], ("1", "1"))
        self.assertEqual(fields[546], ("1", "1"))

    def test_survives_no_vote_fields_present(self):
        self.assertEqual(submit.parse_vote_fields("<html></html>"), {})


class TestParseDraftPicklist(unittest.TestCase):
    def test_empty_picklist_before_any_submission(self):
        # This fixture was saved before any preference was submitted.
        picks = submit.parse_draft_picklist(_read("draft.html"))
        self.assertEqual(picks, [])

    def test_three_open_placeholders_before_any_submission(self):
        self.assertEqual(submit.count_draft_placeholders(_read("draft.html")), 3)

    def test_reads_saved_order_from_picked_divs(self):
        # Minimal reproduction of the server-rendered markup for a saved
        # preference list, confirmed against the live site (id="picked<id>",
        # in saved order; verified 2026-09-17).
        html = (
            '<div id="picked541" class="pickbox">01 Brady</div>'
            '<div id="picked553" class="pickbox">02 Ori</div>'
            '<div id="placeholder1" class="pickbox draftplaceholder">Survivor</div>'
        )
        self.assertEqual(submit.parse_draft_picklist(html), [541, 553])


class TestParseStandings(unittest.TestCase):
    def test_finds_all_four_league_members(self):
        rows = submit.parse_standings(_read("standings.html"))
        self.assertEqual(len(rows), 4)

    def test_finds_exactly_one_self_row(self):
        rows = submit.parse_standings(_read("standings.html"))
        selves = [r for r in rows if r["is_self"]]
        self.assertEqual(len(selves), 1)
        self.assertEqual(selves[0]["real_name"], "AI bot")

    def test_everyone_is_tied_at_zero_pre_season(self):
        rows = submit.parse_standings(_read("standings.html"))
        self.assertTrue(all(r["total"] == 0 for r in rows))

    def test_opponent_names_match_the_league_page(self):
        rows = submit.parse_standings(_read("standings.html"))
        names = {r["tribe_name"] for r in rows if not r["is_self"]}
        self.assertEqual(names,
                         {"Touch Copper", "Claude Spoiler Bot 2000", "Claude's Fleshbag"})


class _FakePage:
    """Just enough of the Playwright Page interface to drive submit_vote /
    verify_vote against an in-memory field store, seeded from the real
    vote.html fixture's 21 fields (episode 1, tribe 1).

    Reproduces js/vote-helper.js's capInputAtMaximum: every field write is
    clamped against the LIVE running total across all fields in the same
    (episode, tribe) pool at that exact moment, budget 10 - not against the
    caller's intended final total. This is what actually caught the live
    bug: setting fields to their targets in discovery order let an increase
    land before an unrelated decrease, transiently exceeding budget and
    getting silently clamped.
    """

    BUDGET = 10

    def __init__(self, initial_values):
        self._values = dict(initial_values)  # site_id -> str value
        self._html = _read("vote.html")

    def goto(self, *a, **k):
        pass

    def wait_for_timeout(self, *a, **k):
        pass

    def content(self):
        return self._html

    def evaluate(self, script, arg=None):
        if isinstance(arg, list):
            sel, val = arg
            site_id = int(sel.rsplit("-", 1)[1])
            others = sum(int(v or 0) for k, v in self._values.items()
                        if k != site_id)
            clamped = min(int(val), self.BUDGET - others)
            self._values[site_id] = str(max(0, clamped))
        # window.submitVotes() call: nothing to simulate, values already set.

    def eval_on_selector(self, selector, script):
        tail = selector.rsplit("-", 1)[1]
        site_id = int(tail.rstrip('"]'))
        return self._values.get(site_id, "")


class TestSubmitVoteReplacesRatherThanMerges(unittest.TestCase):
    def test_dropped_castaways_get_zeroed_not_left_stale(self):
        # Reproduces the exact bug found live: a prior submission had
        # points on rob/maggie/an (555/551/538); resubmitting a fresh
        # all-in on kristin (548) must zero the other three, not just add
        # 10 on top of their leftover values.
        page = _FakePage({555: "1", 551: "1", 538: "1", 548: "0"})
        submit.submit_vote(page, 1, {548: 10})
        self.assertEqual(page._values[548], "10")
        self.assertEqual(page._values[555], "0")
        self.assertEqual(page._values[551], "0")
        self.assertEqual(page._values[538], "0")

    def test_verify_fails_if_a_dropped_castaway_is_left_nonzero(self):
        page = _FakePage({555: "1", 548: "10"})  # 555 never got cleared
        with self.assertRaises(submit.SubmitError):
            submit.verify_vote(page, 1, {548: 10})


class TestSoleSurvivorConfirmation(unittest.TestCase):
    def test_recognises_the_sites_own_confirmation_text(self):
        self.assertTrue(submit.parse_sole_survivor_confirmation(
            "Eric chosen as Sole Survivor.\nSHOP\n..."))

    def test_rejects_unrelated_text(self):
        self.assertFalse(submit.parse_sole_survivor_confirmation(
            "LOGIN\nEmail address\nPassword"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
