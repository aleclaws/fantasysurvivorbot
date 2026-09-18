"""Draft board and sole-survivor pick.

The site pays a drafted castaway per named action while they play AND 1 point
per episode after they leave (data/site/standings.html: the "Out" column,
"Extra points gained for Survivors voted out"). So survival is not an
annuity: an episode in the game is only worth its gameplay points MINUS the
1 point the castaway would earn anyway once out. Pre-merge that margin is
large (tribe challenge points go to every tribe member); post-merge it is
small. Draft value is therefore mostly "reaches the merge", not "wins".

Survival curves come from the same hazard model the allocator uses, run
forward as a full-season simulation, so correcting an edit score moves the
weekly picks and the draft board together.
"""

from __future__ import annotations

import json
import math
import os
import random
from typing import Callable, Dict, List, Tuple

from .model import DATA, Castaway, Season


def load_scoring() -> dict:
    with open(os.path.join(DATA, "scoring.json"), "r", encoding="utf-8") as fh:
        return json.load(fh)


def _schedule(season: Season, n_alive: int) -> Tuple[int, int, Callable[[int], int]]:
    """Map the i-th remaining boot to the episode it happens in.

    The simulation removes one castaway per step, but the show has a fixed
    number of episodes, so some episodes hold more than one boot. Boots are
    spread evenly over the remaining episodes; everyone past the last real
    boot is a finalist and plays through the final episode.
    """
    last_ep = int(season.meta.get("episode_count", 13))
    first_ep = min(season.episode, last_ep)
    finalists = int(season.draft_model.get("finalists", 3))
    boots = max(1, n_alive - finalists)
    span = last_ep - first_ep + 1

    def episode_of(b: int) -> int:
        if b > boots:
            return last_ep
        return first_ep - 1 + math.ceil(b * span / boots)

    return boots, first_ep, episode_of


def simulate_placements(season: Season, n: int = 8000,
                        seed: int = 51) -> Dict[str, dict]:
    """Run the season forward `n` times and record how everyone finishes.

    Per castaway: P(win), P(2nd), P(3rd), and, in EPISODES (not boot steps),
    mean episodes in the game before and after the merge, P(reach merge),
    P(finalist), P(still in near the end), and mean out-of-game episodes.
    """
    alive0 = [c.id for c in season.alive()]
    rng = random.Random(seed)
    merge_at = int(season.draft_model.get("merge_at_players", 12))
    late_window = int(season.draft_model.get("love_from_home_window", 3))
    last_ep = int(season.meta.get("episode_count", 13))
    boots, first_ep, episode_of = _schedule(season, len(alive0))
    merged = season.merged()
    pre_boots = 0 if merged else max(0, len(alive0) - merge_at)
    merge_ep = first_ep if merged or not pre_boots else episode_of(pre_boots) + 1

    keys = ("win", "second", "third", "pre", "post", "merge", "final",
            "late", "out")
    stats = {cid: dict.fromkeys(keys, 0.0) for cid in alive0}

    for _ in range(n):
        live = list(alive0)
        leave: Dict[str, int] = {}
        b = 0
        while len(live) > 1:
            post = merged or len(live) <= merge_at
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
            b += 1
            if len(live) == 3:
                stats[boot]["third"] += 1
            elif len(live) == 2:
                stats[boot]["second"] += 1
            live.remove(boot)
            leave[boot] = b
        stats[live[0]]["win"] += 1

        for cid in alive0:
            bi = leave.get(cid, boots + 1)
            finalist = bi > boots
            ep_leave = last_ep if finalist else episode_of(bi)
            pre = max(0, min(ep_leave, merge_ep - 1) - first_ep + 1)
            s = stats[cid]
            s["pre"] += pre
            s["post"] += (ep_leave - first_ep + 1) - pre
            s["merge"] += (not merged) and bi > pre_boots
            s["final"] += finalist
            s["late"] += ep_leave > last_ep - late_window
            s["out"] += 0 if finalist else last_ep - ep_leave + 1

    out = {}
    for cid, s in stats.items():
        out[cid] = {
            "p_win": s["win"] / n,
            "p_second": s["second"] / n,
            "p_third": s["third"] / n,
            "mean_weeks": (s["pre"] + s["post"]) / n,
            "mean_pre_merge_weeks": s["pre"] / n,
            "mean_post_merge_weeks": s["post"] / n,
            "p_merge": s["merge"] / n,
            "p_final": s["final"] / n,
            "p_late": s["late"] / n,
            "mean_out_weeks": s["out"] / n,
        }
    return out


def _tribe_win_odds(season: Season) -> float:
    """Chance a given tribe avoids tribal: every tribe but one wins."""
    live = len(season.tribes())
    tribes = live if live > 1 else len(season.meta.get("starting_tribes", [])) or 2
    return (tribes - 1) / tribes


def _rates(season: Season, c: Castaway, a: dict, dm: dict) -> Tuple[float, float]:
    """Expected gameplay points per in-game episode, before and after merge.

    Tribe challenge points go to every tribe member, so they depend on the
    tribe's odds, with only a small tilt for the castaway's own physicality.
    Individual challenges, camp content and advantages are split across the
    players still in the game, weighted by a pre-season proxy.
    """
    alive = season.alive()
    n_alive = len(alive)
    merge_at = int(dm.get("merge_at_players", 12))
    finalists = int(dm.get("finalists", 3))
    pre_field = max(1.0, (n_alive + merge_at) / 2)
    post_field = max(1.0, (merge_at + finalists) / 2)
    mean_phys = sum(x.phys for x in alive) / n_alive
    mean_social = sum(x.social for x in alive) / n_alive
    mean_threat = sum(x.threat for x in alive) / n_alive

    tribe_p = _tribe_win_odds(season) + dm["own_phys_tribe_tilt"] * (c.phys - mean_phys)
    tribe_p = min(1.0, max(0.0, tribe_p))
    airtime = (0.5 + 0.5 * c.social) / (0.5 + 0.5 * mean_social)
    agency = (0.5 + 0.5 * c.threat) / (0.5 + 0.5 * mean_threat)

    pre = (a["tribe_immunity_win"] * tribe_p
           + a["tribe_reward_win"] * tribe_p * dm["tribe_reward_fraction"]
           + dm["camp_points_per_episode"] * airtime / pre_field
           + dm["advantage_points_per_episode"] * agency / pre_field)

    win_share = (c.phys / mean_phys) / post_field
    post = (a["individual_immunity_win"] * win_share
            + a["individual_reward_win"] * dm["individual_reward_fraction"]
            * (win_share + dm["reward_companions"] / post_field)
            + dm["camp_points_per_episode"] * airtime / post_field
            + dm["advantage_points_per_episode"] * agency / post_field)
    return pre, post


def draft_board(season: Season, n: int = 8000,
                seed: int = 51) -> List[Tuple[str, float, dict]]:
    """Expected season points per castaway as a draft pick, highest first.

    Gameplay points while in the game, one-off bonuses weighted by the
    chance of being there for them, plus the out-of-game trickle. The Sole
    Survivor bonus is NOT included: it pays for your winner pick, which is
    a separate choice from your draft (see mvp_pick).
    """
    outplay = load_scoring()["outplay"]
    a, out_rule = outplay["actions"], outplay["out_of_game"]
    dm = season.draft_model
    finalists = int(dm.get("finalists", 3))
    opening = 0.0
    if season.episode == 1:
        opening = (a["marooning_challenge_win"]
                   + a["supply_challenge_win"]) * _tribe_win_odds(season)
    places = simulate_placements(season, n=n, seed=seed)

    rows = []
    for cid, p in places.items():
        pre_rate, post_rate = _rates(season, season.cast[cid], a, dm)
        pts = (opening
               + p["mean_pre_merge_weeks"] * pre_rate
               + p["mean_post_merge_weeks"] * post_rate
               + a["reach_merge"] * p["p_merge"]
               + a["attend_survivor_auction"] * dm["auction_prob"] * p["p_merge"]
               + a["love_from_home"] * dm["love_from_home_prob"] * p["p_late"]
               + a["fire_making_final_four_win"] * dm["fire_making_prob"]
               * p["p_final"] / finalists
               + out_rule["per_episode"]
               * min(out_rule["cap_episodes"], p["mean_out_weeks"]))
        rows.append((cid, pts, p))
    rows.sort(key=lambda r: -r[1])
    return rows


def mvp_pick(season: Season, roster: List[str], n: int = 8000,
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
