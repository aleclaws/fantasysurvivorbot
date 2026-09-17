"""Tests for the decision engine.

These lock down the two things that actually decide the league: that the
probability model stays coherent as the season changes shape, and that the
allocator changes its behaviour with the standings instead of always parroting
the favourite.
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fsb.allocate import (candidate_allocations, optimise, win_probability,
                          Scenarios)
from fsb.draft import draft_board, mvp_pick, simulate_placements
from fsb.model import Season, age_risk


def league(**over):
    base = {"league_name": "t", "num_opponents": 9, "my_score": 0,
            "opponent_scores": [], "field_sharpness": 2.5,
            "field_all_in_fraction": 0.7, "field_noise": 0.6}
    base.update(over)
    return base


class TestAgeRisk(unittest.TestCase):
    def test_rises_with_age_past_the_late_thirties(self):
        self.assertLess(age_risk(37), age_risk(42))
        self.assertLess(age_risk(42), age_risk(49))

    def test_bounded(self):
        for a in range(18, 75):
            self.assertGreaterEqual(age_risk(a), 0.0)
            self.assertLessEqual(age_risk(a), 1.0)

    def test_very_young_carries_some_risk_too(self):
        self.assertGreater(age_risk(22), age_risk(31))


class TestModel(unittest.TestCase):
    def setUp(self):
        self.s = Season()

    def test_boot_probabilities_form_a_distribution(self):
        p = self.s.boot_probabilities()
        self.assertAlmostEqual(sum(p.values()), 1.0, places=9)
        self.assertTrue(all(v > 0 for v in p.values()))

    def test_merge_is_read_from_state_not_inferred(self):
        # Pre-season every tribe field is null, so the whole cast sits in one
        # bucket.  Inferring the merge from that would price episode one as a
        # post-merge tribal and invert every hazard.
        self.assertFalse(self.s.state.get("tribes"))
        self.assertFalse(self.s.merged())

    def test_eliminated_players_leave_the_pool(self):
        s = Season()
        s.apply_state({"episode": 2, "merged": False,
                       "eliminated": ["kristin"], "tribes": {}, "edit": {},
                       "idols": []})
        self.assertNotIn("kristin", s.boot_probabilities())
        self.assertEqual(len(s.alive()), 20)

    def test_doom_edit_raises_risk_and_idol_lowers_it(self):
        base = Season().boot_probabilities()["mike"]
        doomed = Season()
        doomed.apply_state({"edit": {"mike": 1.0}})
        self.assertGreater(doomed.boot_probabilities()["mike"], base)
        safe = Season()
        safe.apply_state({"idols": ["mike"]})
        self.assertLess(safe.boot_probabilities()["mike"], base)

    def test_preseason_buzz_nudges_risk_but_stays_weaker_than_edit(self):
        # linnea is the cited pre-season "predicted first boot" pick
        # (preseason_buzz=+0.30); aaliyah is the cited primary winner pick
        # (preseason_buzz=-0.30). A real edit signal should be able to
        # override that cheaply, since it carries more weight and range.
        s = Season()
        self.assertGreater(s.cast["linnea"].preseason_buzz, 0)
        self.assertLess(s.cast["aaliyah"].preseason_buzz, 0)
        buzzed_up = s.hazard(s.cast["linnea"], postmerge=False)
        s.apply_state({"edit": {"linnea": -1.0}})
        overridden = s.hazard(s.cast["linnea"], postmerge=False)
        self.assertLess(overridden, buzzed_up)

    def test_two_tribes_split_the_probability_mass(self):
        s = Season()
        ids = list(s.cast)
        tribes = {c: ("Savu" if i % 2 else "Toka") for i, c in enumerate(ids)}
        s.apply_state({"tribes": tribes})
        self.assertEqual(len(s.tribes()), 2)
        p = s.boot_probabilities()
        self.assertAlmostEqual(sum(p.values()), 1.0, places=9)

    def test_physicality_flips_sign_at_the_merge(self):
        # Pre-merge an athlete is protected; post-merge they are the target.
        s = Season()
        live = [c.id for c in s.alive()]
        pre = s.step_probabilities(live, postmerge=False)
        post = s.step_probabilities(live, postmerge=True)
        athlete, weak = "brady", "kristin"
        self.assertLess(pre[athlete], pre[weak])
        self.assertGreater(post[athlete] / pre[athlete],
                           post[weak] / pre[weak])


class TestAllocation(unittest.TestCase):
    def setUp(self):
        self.s = Season()
        self.probs = self.s.boot_probabilities()

    def test_candidates_always_spend_the_whole_budget(self):
        ids = list(self.probs)
        for a in candidate_allocations(ids, self.probs, budget=10):
            self.assertEqual(sum(a.values()), 10)
            self.assertTrue(all(0 <= v <= 10 for v in a.values()))

    def test_optimiser_respects_the_budget_per_tribe(self):
        alloc, _ = optimise(self.s, league(), sims=300)
        for tribe, a in alloc.items():
            self.assertEqual(sum(a.values()), 10, tribe)
            self.assertTrue(all(v <= 10 for v in a.values()))

    def test_budget_is_per_tribe_not_per_episode(self):
        s = Season()
        ids = list(s.cast)
        s.apply_state({"tribes": {c: ("Savu" if i % 2 else "Toka")
                                  for i, c in enumerate(ids)}})
        alloc, _ = optimise(s, league(), sims=300)
        self.assertEqual(set(alloc), {"Savu", "Toka"})
        for a in alloc.values():
            self.assertEqual(sum(a.values()), 10)

    def test_optimiser_never_does_worse_than_chasing_points(self):
        _, d = optimise(self.s, league(), sims=1200)
        self.assertGreaterEqual(d["win_probability"] + 1e-9,
                                d["win_probability_if_ev_max"])

    def test_recoverable_deficit_late_buys_variance(self):
        """Behind but still live, copying the field cannot close the gap.

        Roughly 50 points are left on the table, so a 25-point deficit is
        recoverable only by scoring where the field is not.  The engine has to
        stop maximising points and start buying variance.
        """
        s = Season()
        gone = [c.id for c in s.alive()][:15]
        s.apply_state({"episode": 16, "merged": True, "eliminated": gone,
                       "tribes": {}, "edit": {}, "idols": []})
        lg = league(my_score=95,
                    opponent_scores=[120, 118, 112, 108, 105, 100, 98, 90, 85])
        alloc, d = optimise(s, lg, sims=4000)
        self.assertGreater(d["win_probability"], 0.0,
                           "deficit must be live for this test to mean anything")
        self.assertGreaterEqual(d["win_probability"],
                                d["win_probability_if_ev_max"])
        self.assertLess(d["expected_points"], d["expected_points_if_ev_max"],
                        "buying variance should cost expected points")

    def test_dead_position_still_banks_points(self):
        """When the win is gone, every allocation ties at zero.

        The engine must not freeze on its starting guess and score nothing; it
        falls back to collecting points, which is also the safe behaviour if
        the standings I fed it turn out to be wrong.
        """
        s = Season()
        gone = [c.id for c in s.alive()][:15]
        s.apply_state({"episode": 16, "merged": True, "eliminated": gone,
                       "tribes": {}, "edit": {}, "idols": []})
        lg = league(my_score=0,
                    opponent_scores=[400, 390, 380, 370, 360, 350, 340, 330, 320])
        _, d = optimise(s, lg, sims=800)
        self.assertEqual(d["win_probability"], 0.0)
        self.assertGreaterEqual(d["expected_points"],
                                d["expected_points_if_ev_max"] - 1e-9)

    def test_comfortable_lead_does_not_gamble(self):
        s = Season()
        gone = [c.id for c in s.alive()][:15]
        s.apply_state({"episode": 16, "merged": True, "eliminated": gone,
                       "tribes": {}, "edit": {}, "idols": []})
        lg = league(my_score=200,
                    opponent_scores=[80, 70, 65, 60, 55, 50, 45, 40, 30])
        _, d = optimise(s, lg, sims=1200)
        self.assertGreater(d["win_probability"], 0.9)

    def test_win_probability_is_monotone_in_my_score(self):
        sc = Scenarios(self.s, league(), n=600, seed=7)
        a = {max(self.probs, key=lambda k: self.probs[k]): 10}
        self.assertLessEqual(win_probability(a, sc, 0.0),
                             win_probability(a, sc, 500.0))


class TestDraft(unittest.TestCase):
    def setUp(self):
        self.s = Season()

    def test_placements_are_probabilities(self):
        pl = simulate_placements(self.s, n=400)
        self.assertAlmostEqual(sum(v["p_win"] for v in pl.values()), 1.0,
                               places=6)
        for v in pl.values():
            self.assertGreaterEqual(v["mean_weeks"], 0)

    def test_board_covers_everyone_still_in(self):
        rows = draft_board(self.s, n=400)
        self.assertEqual(len(rows), len(self.s.alive()))
        pts = [r[1] for r in rows]
        self.assertEqual(pts, sorted(pts, reverse=True))

    def test_oldest_player_is_not_the_top_draft_pick(self):
        rows = draft_board(self.s, n=800)
        self.assertNotEqual(rows[0][0], "kristin")

    def test_board_scores_stay_positive_and_bounded(self):
        # An early elimination still banks out-of-game trickle points under
        # the real rule (data/scoring.json outplay.out_of_game), so nobody's
        # expected points should collapse to zero or explode from a formula
        # error.
        rows = draft_board(self.s, n=800)
        for cid, pts, _ in rows:
            self.assertGreater(pts, 0, cid)
            self.assertLess(pts, 60, cid)

    def test_mvp_comes_from_my_roster(self):
        roster = ["rob", "kristin", "an"]
        pick, _ = mvp_pick(self.s, roster, n=400)
        self.assertIn(pick, roster)

    def test_mvp_rejects_an_empty_impossible_roster(self):
        with self.assertRaises(ValueError):
            mvp_pick(self.s, ["nobody-by-this-name"], n=100)


class TestDataFiles(unittest.TestCase):
    def test_cast_is_complete_and_unique(self):
        with open(os.path.join("data", "season51.json")) as fh:
            meta = json.load(fh)
        ids = [c["id"] for c in meta["cast"]]
        self.assertEqual(len(ids), meta["cast_size"])
        self.assertEqual(len(set(ids)), len(ids))

    def test_every_castaway_has_priors(self):
        with open(os.path.join("data", "season51.json")) as fh:
            ids = {c["id"] for c in json.load(fh)["cast"]}
        with open(os.path.join("data", "priors.json")) as fh:
            feats = set(json.load(fh)["features"])
        self.assertEqual(ids, feats)

    def test_scoring_constants_declare_their_confidence(self):
        with open(os.path.join("data", "scoring.json")) as fh:
            sc = json.load(fh)
        for block, body in sc.items():
            if not block.startswith("_"):
                self.assertIn(body.get("confidence"), {"high", "low"}, block)

    def test_scoring_matches_the_real_site_structure(self):
        # Locks in the correction made from data/site/rules.txt: the real
        # game pays per named action and a streak-based Outlast bonus, not
        # the flat premerge/postmerge rate and placement bonus the engine
        # started with before recon.py could read the site.
        with open(os.path.join("data", "scoring.json")) as fh:
            sc = json.load(fh)
        self.assertNotIn("draft", sc)
        self.assertIn("outplay", sc)
        self.assertEqual(sc["outplay"]["actions"]["tribe_immunity_win"], 3)
        self.assertEqual(sc["sole_survivor"]["max_points"], 13)
        self.assertNotIn("first", sc["sole_survivor"])
        self.assertTrue(sc["sole_survivor"]["pick_changeable_anytime"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
