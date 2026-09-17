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
    """Expected season points per castaway, highest first."""
    sc = load_scoring()
    d, ss = sc["draft"], sc["sole_survivor"]
    places = simulate_placements(season, n=n, seed=seed)

    rows = []
    for cid, p in places.items():
        c = season.cast[cid]
        pre_weeks = max(0.0, p["mean_weeks"] - p["mean_post_merge_weeks"])
        pts = (pre_weeks * d["survive_week_premerge"]
               + p["mean_post_merge_weeks"] * d["survive_week_postmerge"])
        # Challenge and advantage points scale with physicality; post-merge
        # immunity is close to a pure physicality lottery.
        pts += pre_weeks * c.phys * (
            d["tribe_immunity_win"] + d["tribe_reward_win"]) * 0.5
        pts += p["mean_post_merge_weeks"] * c.phys * 0.30 * (
            d["individual_immunity_win"] + d["individual_reward_win"])
        pts += d["find_idol"] * 0.35
        pts += (p["p_win"] * ss["first"] + p["p_second"] * ss["second"]
                + p["p_third"] * ss["third"])
        rows.append((cid, pts, p))
    rows.sort(key=lambda r: -r[1])
    return rows


def mvp_pick(season: Season, roster: List[str], n: int = 4000,
             seed: int = 51) -> Tuple[str, dict]:
    """Sole-survivor pick: the roster player most likely to actually win.

    The bonus only pays on an outright win, so this maximises P(win) and
    ignores expected points entirely.  Hedging a winner pick is not possible -
    you get one.
    """
    places = simulate_placements(season, n=n, seed=seed)
    pool = [c for c in (roster or list(places)) if c in places]
    if not pool:
        raise ValueError("no eligible castaways for the MVP pick")
    best = max(pool, key=lambda c: places[c]["p_win"])
    return best, places[best]
