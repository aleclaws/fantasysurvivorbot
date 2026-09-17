"""Draft board and sole-survivor pick.

The weekly vote is a prediction market; the draft is an annuity.  A drafted
castaway pays out for every week they stay in the game, and pays out more
after the merge, so draft value is mostly survival time and only secondarily
challenge ability.

Survival curves come from the same hazard model the allocator uses, run
forward as a full-season simulation.  That keeps one source of truth: correct
an edit score and both the weekly picks and the draft board move together.
"""

from __future__ import annotations

import json
import os
import random
from typing import Dict, List, Tuple

from .model import DATA, Season


def load_scoring() -> dict:
    with open(os.path.join(DATA, "scoring.json"), "r", encoding="utf-8") as fh:
        return json.load(fh)


def simulate_placements(season: Season, n: int = 4000, seed: int = 51,
                        merge_at: int = 12) -> Dict[str, dict]:
    """Run the season forward `n` times and record how everyone finishes.

    Returns, per castaway: P(win), P(top 3), and mean episodes survived.
    """
    alive0 = [c.id for c in season.alive()]
    rng = random.Random(seed)

    stats = {cid: {"win": 0, "second": 0, "third": 0, "weeks": 0.0,
                   "post_merge_weeks": 0.0} for cid in alive0}

    for _ in range(n):
        live = list(alive0)
        while len(live) > 1:
            post = season.merged() or len(live) <= merge_at
            # Re-price every step: pre-merge and post-merge hazards invert.
            weights = season.step_probabilities(live, postmerge=post)
            total = sum(weights.values()) or 1.0
            r = rng.random() * total
            acc = 0.0
            boot = live[-1]
            for k, v in weights.items():
                acc += v
                if r <= acc:
                    boot = k
                    break
            for cid in live:
                stats[cid]["weeks"] += 1
                if post:
                    stats[cid]["post_merge_weeks"] += 1
            if len(live) == 3:
                stats[boot]["third"] += 1
            elif len(live) == 2:
                stats[boot]["second"] += 1
            live.remove(boot)
        if live:
            stats[live[0]]["win"] += 1

    out = {}
    for cid, s in stats.items():
        out[cid] = {
            "p_win": s["win"] / n,
            "p_second": s["second"] / n,
            "p_third": s["third"] / n,
            "mean_weeks": s["weeks"] / n,
            "mean_post_merge_weeks": s["post_merge_weeks"] / n,
        }
    return out


def draft_board(season: Season, n: int = 4000,
                seed: int = 51) -> List[Tuple[str, float, dict]]:
    """Expected season points per castaway, highest first.

    The real scoring page (data/site/rules.txt) pays per named action, not a
    flat per-week rate, so this is a deliberate aggregation of that table into
    four buckets the hazard model can actually price:

      challenge  - tribe/individual reward and immunity wins, scaled by phys,
                   since challenge outcome is the one category the model
                   already treats as a physicality contest.
      camp_life  - the four recurring one-per-episode actions (tree mail,
                   water well, make fire, find food). Real airtime decides who
                   gets these; lacking that signal pre-season, they are split
                   across the live pool and tilted toward `social`.
      advantages - idol/advantage finds and plays. Rare and roughly flat per
                   person, so a small trickle rather than a per-person model.
      season_bonuses - merge, auction, love from home: each capped near once
                   per season, so paid in proportion to season survived.

    Plus the real Outlast rule: 1 point per consecutive episode a player has
    the eventual winner picked, up to sole_survivor.max_points if held from
    week one. Drafting for E[pts] and picking the MVP for P(win) are still two
    different questions - see mvp_pick.
    """
    sc = load_scoring()
    op, ss = sc["outplay"], sc["sole_survivor"]
    a = op["actions"]
    season_len = season.meta.get("episode_count", 13)
    out_rate = op["out_of_game"]["per_episode"]
    out_cap = op["out_of_game"]["cap_episodes"]
    camp_life_pool = (a["read_tree_mail"] + a["water_well_strategize"]
                       + a["make_fire_at_camp"] + a["find_food"])
    advantage_pool = (a["find_idol_or_advantage_clue"]
                       + a["first_to_gain_immunity_idol"]
                       + a["first_to_gain_advantage"]
                       + a["play_idol_or_advantage"]
                       + a["play_shot_in_the_dark"])
    season_bonus_pool = (a["reach_merge"] + a["attend_survivor_auction"]
                          + a["love_from_home"])

    places = simulate_placements(season, n=n, seed=seed)
    alive_now = max(1, len(season.alive()))

    rows = []
    for cid, p in places.items():
        c = season.cast[cid]
        pre_weeks = max(0.0, p["mean_weeks"] - p["mean_post_merge_weeks"])
        post_weeks = p["mean_post_merge_weeks"]
        total_weeks = pre_weeks + post_weeks

        pts = 0.0
        pts += pre_weeks * c.phys * (a["tribe_immunity_win"]
                                      + a["tribe_reward_win"]) * 0.5
        pts += post_weeks * c.phys * 0.30 * (a["individual_immunity_win"]
                                              + a["individual_reward_win"])
        pts += total_weeks * camp_life_pool * (0.5 + 0.5 * c.social) / alive_now
        pts += total_weeks * advantage_pool * 0.15 / alive_now
        pts += season_bonus_pool * (total_weeks / season_len)
        weeks_out = max(0.0, min(out_cap, season_len - total_weeks))
        pts += weeks_out * out_rate
        pts += p["p_win"] * ss["max_points"]
        rows.append((cid, pts, p))
    rows.sort(key=lambda r: -r[1])
    return rows


def mvp_pick(season: Season, roster: List[str], n: int = 4000,
             seed: int = 51) -> Tuple[str, dict]:
    """Sole-survivor pick: the castaway most likely to actually win.

    The real rule pays 1 point per consecutive episode, counting back from
    the final, that you had the eventual winner picked - see
    scoring.json:sole_survivor. You may change this pick at any time, and
    switching to a stronger P(win) candidate loses nothing except a streak
    you were not going to finish anyway, so this always maximises P(win) and
    should be re-run whenever the standings or edit signals change, not only
    once before the premiere.
    """
    places = simulate_placements(season, n=n, seed=seed)
    pool = [c for c in (roster or list(places)) if c in places]
    if not pool:
        raise ValueError("no eligible castaways for the MVP pick")
    best = max(pool, key=lambda c: places[c]["p_win"])
    return best, places[best]
