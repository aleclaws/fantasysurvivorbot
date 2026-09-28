"""Weekly point allocation.

The league gives you 10 points per tribe to spread over that tribe's players.
You score whatever you had on the player who gets voted out.

The naive objective is expected points, and expected points is linear:

    EV(x) = sum_i p_i * x_i   subject to   sum_i x_i = 10

A linear objective on a simplex is always maximised at a corner, so pure EV
says "put all 10 on the most likely boot, every single week, forever".

That advice is close to worthless in a league, because the league does not pay
you for points.  It pays you for finishing first.  If all ten of you dump 10
points on the obvious boot, then the weeks the obvious boot goes home move
nobody, and the weeks it does not move nobody either.  Consensus play scores
points and gains no ground.

So the objective here is P(finish first), estimated by simulation against a
model of what the other players will do.  That objective is not linear, and it
produces the behaviour you actually want:

  * ahead late   -> copy the field, lock the lead in, refuse variance
  * behind late  -> take the position the field does not hold, buy variance
  * early season -> near enough to EV-max, because there is time to recover

Scenarios are drawn once and reused across every candidate allocation (common
random numbers), so candidates are ranked on identical futures.
"""

from __future__ import annotations

import math
import random
import statistics
from typing import Dict, List, Optional, Sequence, Tuple

from .draft import load_scoring
from .model import Season

Alloc = Dict[str, int]

# Stands in for "somebody left, but nobody scored".  A quit, a medical
# evacuation or a production removal ends a castaway's game and awards no vote
# points to anyone, so the week must be simulated as a real departure that
# pays out nothing.  No allocation can contain this key, so both my score and
# the field's fall through to zero for that episode.
VOID = "__no_vote_points__"


# ---------------------------------------------------------------- candidates

def candidate_allocations(ids: Sequence[str], probs: Dict[str, float],
                          budget: int = 10, depth: int = 4,
                          all_in_top: int = 8) -> List[Alloc]:
    """Plausible ways to split `budget` points over a tribe.

    Every all-in on a serious candidate, plus every integer split across the
    `depth` most likely boots.  Hopeless longshots are not enumerated: they
    lose on EV and, because nobody in the field is on them either, they buy
    less differentiation than a second-favourite does.
    """
    ranked = sorted(ids, key=lambda i: -probs.get(i, 0.0))
    out: List[Alloc] = []
    seen = set()

    def add(a: Alloc) -> None:
        key = tuple(sorted((k, v) for k, v in a.items() if v))
        if key not in seen:
            seen.add(key)
            out.append(a)

    for cid in ranked[:all_in_top]:
        add({cid: budget})

    top = ranked[:depth]

    def splits(rem: int, idx: int, acc: Alloc) -> None:
        if idx == len(top) - 1:
            add({**acc, top[idx]: rem})
            return
        for give in range(rem + 1):
            splits(rem - give, idx + 1, {**acc, top[idx]: give})

    if top:
        splits(budget, 0, {})
    return out


# -------------------------------------------------------------- field model

def _field_probs(probs: Dict[str, float], sharpness: float) -> Dict[str, float]:
    """What the other players believe, as a sharpened version of my read."""
    powered = {k: (v ** sharpness) for k, v in probs.items()}
    total = sum(powered.values())
    if total <= 0:
        n = len(probs) or 1
        return {k: 1.0 / n for k in probs}
    return {k: v / total for k, v in powered.items()}


def _field_share(truth: Dict[str, float], sharp: float,
                 all_in: float) -> Dict[str, float]:
    """Roughly what fraction of the field ends up on each player."""
    belief = _field_probs(truth, sharp)
    if not belief:
        return {}
    fav = max(belief, key=lambda i: belief[i])
    share = {i: (1.0 - all_in) * v for i, v in belief.items()}
    share[fav] = share.get(fav, 0.0) + all_in
    return share


def _best_response(truth: Dict[str, float], sharp: float,
                   all_in: float) -> str:
    """The player worth backing once you price in who else is on them.

    Points are only worth having if the field does not have them too, so this
    maximises p_i * (1 - field share on i) rather than p_i alone.
    """
    share = _field_share(truth, sharp, all_in)
    total = sum(truth.values()) or 1.0
    return max(truth, key=lambda i: (truth[i] / total)
               * (1.0 - share.get(i, 0.0)))


def _draw(rng: random.Random, weights: Dict[str, float]) -> str:
    total = sum(weights.values())
    r = rng.random() * total
    acc = 0.0
    for k, v in weights.items():
        acc += v
        if r <= acc:
            return k
    return next(reversed(list(weights)))


# ---------------------------------------------------------------- scenarios

def effective_opponent_scores(league: dict) -> List[float]:
    """Opponent scores to simulate against, padded to any known future
    minimum league size.

    league.json's opponent_scores reflects who has actually joined right
    now - tools/submit.py standings rebuilds it from the real site every
    time it runs, so it is always honest about the current signup count,
    nothing more. expected_min_opponents is a separate, user-reported
    estimate of the eventual league size that sync does not touch, so it
    survives being overwritten while real signups are still trickling in.
    Padding with my_score assumes an unseen opponent starts exactly level,
    the same fallback already used when opponent_scores is empty outright.
    """
    scores = list(league.get("opponent_scores") or [])
    if not scores:
        scores = [float(league.get("my_score", 0))] * int(
            league.get("num_opponents", 9))
    minimum = int(league.get("expected_min_opponents", 0))
    if len(scores) < minimum:
        scores = scores + [float(league.get("my_score", 0))] * (
            minimum - len(scores))
    return scores


class Scenarios:
    """Pre-drawn futures: who goes home when, and what the field scored.

    Each opponent gets their own persistent misread of the cast, drawn once per
    scenario and carried all season.  That noise is where my edge lives: if the
    field's beliefs were just a sharpened copy of mine, I could never out-score
    them by being right, only by being different, and the optimiser would
    gamble every week to manufacture a difference.  Modelling opponents as
    noisy instead of merely herd-like keeps the edge honest.
    """

    def __init__(self, season: Season, league: dict, n: int = 16000,
                 seed: int = 51) -> None:
        self.season = season
        self.league = league
        self.n = n
        rng = random.Random(seed)

        base = season.boot_probabilities()
        alive = [c.id for c in season.alive()]
        pools = self._pools(season)
        sharp = float(league.get("field_sharpness", 2.5))
        all_in = float(league.get("field_all_in_fraction", 0.7))
        noise = float(league.get("field_noise", 0.6))
        medevac = {c.id: c.medevac for c in season.alive()}

        opp_scores = effective_opponent_scores(league)
        self.n_opp = len(opp_scores)

        self.boot_now: List[str] = []
        self.opp_totals: List[List[float]] = []
        self.my_future: List[float] = []

        for _ in range(n):
            # Each opponent's season-long misread of the cast.
            misread = [{i: math.exp(rng.gauss(0.0, noise)) for i in alive}
                       for _ in range(self.n_opp)]
            weights = {i: max(base.get(i, 1e-9), 1e-9) for i in alive}
            opps = list(opp_scores)

            boot = _draw(rng, weights)
            scoring = boot if rng.random() >= medevac.get(boot, 0.0) else VOID
            self.boot_now.append(scoring)
            for j in range(self.n_opp):
                opps[j] += self._field_points(rng, weights, misread[j],
                                              scoring, pools, sharp, all_in)

            # Remaining episodes.  Future-me plays the same differentiating
            # policy this optimiser recommends, not naive EV-max.  Modelling
            # future-me as a herd follower would leave this week as the only
            # place to gain ground, and the optimiser would answer by dumping
            # the whole budget on a longshot in episode one.
            weights.pop(boot, None)
            mine_future = 0.0
            while len(weights) > 2:
                nxt = _draw(rng, weights)
                nxt_scoring = (nxt if rng.random() >= medevac.get(nxt, 0.0)
                               else VOID)
                if _best_response(weights, sharp, all_in) == nxt_scoring:
                    mine_future += 10.0
                live = {"ALL": list(weights)}
                for j in range(self.n_opp):
                    opps[j] += self._field_points(rng, weights, misread[j],
                                                  nxt_scoring, live, sharp,
                                                  all_in)
                weights.pop(nxt, None)

            self.opp_totals.append(opps)
            self.my_future.append(mine_future)

    @staticmethod
    def _pools(season: Season) -> Dict[str, List[str]]:
        return {name: [c.id for c in members]
                for name, members in season.tribes().items()}

    @staticmethod
    def _field_points(rng: random.Random, truth: Dict[str, float],
                      misread: Dict[str, float], boot: str,
                      pools: Dict[str, List[str]], sharp: float,
                      all_in: float) -> float:
        """Points one opponent scores, given who actually went home."""
        earned = 0.0
        for members in pools.values():
            sub = {i: truth.get(i, 0.0) * misread.get(i, 1.0)
                   for i in members if i in truth}
            if not sub or sum(sub.values()) <= 0:
                continue
            belief = _field_probs(sub, sharp)
            if rng.random() < all_in:
                pick = max(belief, key=lambda i: belief[i])
            else:
                pick = _draw(rng, belief)
            if pick == boot:
                earned += 10.0
        return earned


# ---------------------------------------------------------------- objective

def _threshold_z(n_positions: int) -> float:
    """How many standard errors a challenger must clear to be believed.

    Corrected for how many genuinely different bets were on offer, which is
    the number of castaways in the pool - not the number of allocation vectors
    built from them. Those vectors overlap heavily: 8@Maggie/2@Jenna and
    7@Maggie/3@Jenna are the same bet at slightly different weights, and their
    win-probability estimates move together. Correcting for all few hundred of
    them as if they were independent tests sets the bar so high that a real
    edge worth a quarter of the win probability gets thrown away.
    """
    alpha = 0.05 / max(1, n_positions)
    return statistics.NormalDist().inv_cdf(1.0 - alpha)


def win_credits(alloc: Alloc, sc: Scenarios,
                my_score: float) -> List[float]:
    """Per-scenario win credit: 1 for a win, a share of 1 for a tie, else 0.

    Kept per scenario rather than averaged so that two candidates can be
    compared as a paired sample.  Because every candidate is scored against
    the same drawn futures, most scenarios give both of them the identical
    result, and the paired difference is far better resolved than either
    estimate on its own.
    """
    out: List[float] = []
    for k in range(sc.n):
        mine = my_score + alloc.get(sc.boot_now[k], 0) + sc.my_future[k]
        opps = sc.opp_totals[k]
        best = max(opps)
        if mine > best:
            out.append(1.0)
        elif mine == best:
            out.append(1.0 / (1 + sum(1 for o in opps if o == best)))
        else:
            out.append(0.0)
    return out


def paired_gain(cand: Alloc, incumbent_credits: List[float], sc: Scenarios,
                my_score: float) -> Tuple[float, float]:
    """Mean win-probability gain over the incumbent, and its standard error."""
    n = sc.n
    total = 0.0
    total_sq = 0.0
    for k in range(n):
        mine = my_score + cand.get(sc.boot_now[k], 0) + sc.my_future[k]
        opps = sc.opp_totals[k]
        best = max(opps)
        if mine > best:
            credit = 1.0
        elif mine == best:
            credit = 1.0 / (1 + sum(1 for o in opps if o == best))
        else:
            credit = 0.0
        d = credit - incumbent_credits[k]
        total += d
        total_sq += d * d
    mean = total / n
    var = max(0.0, (total_sq / n) - mean * mean)
    return mean, math.sqrt(var / n)


def win_probability(alloc: Alloc, sc: Scenarios, my_score: float) -> float:
    """P(I finish the season in first place) if I play `alloc` this week."""
    wins = 0.0
    for k in range(sc.n):
        mine = my_score + alloc.get(sc.boot_now[k], 0) + sc.my_future[k]
        opps = sc.opp_totals[k]
        best = max(opps)
        if mine > best:
            wins += 1.0
        elif mine == best:
            wins += 1.0 / (1 + sum(1 for o in opps if o == best))
    return wins / sc.n


def expected_points(alloc: Alloc, probs: Dict[str, float]) -> float:
    return sum(probs.get(k, 0.0) * v for k, v in alloc.items())


def optimise(season: Season, league: dict, sims: int = 16000, seed: int = 51,
             rounds: int = 2,
             budgets: Optional[Dict[str, int]] = None) -> Tuple[Dict[str, Alloc], dict]:
    """Best allocation per tribe, by coordinate ascent on P(win).

    The default scenario count is set by the hardest decision of the season,
    not the easiest. Pre-merge, with ten players on a tribe and one clear
    favourite, the pick is stable on a few thousand draws. Late in the season
    six survivors sit within a few points of each other, and at 8000 draws the
    pick still moved with the random seed. 16000 holds steady there, and a
    decision taken once a week can afford the extra seconds.
    """
    # Rank and price candidates on the chance of being VOTED OUT, not the
    # chance of leaving. A castaway who is likely to go out on a stretcher
    # keeps their departure risk but is worth nothing as a pick.
    probs = season.vote_probabilities()
    # How many points each pool actually carries. tools/submit.py reads this
    # off the live vote page, because the budget is the site's to set: this is
    # the open era, it has already added scoring rules mid-season, and a week
    # that handed out a different budget would otherwise be quietly underspent.
    default_budget = int(load_scoring()["vote"]["budget_per_tribe"])
    budgets = budgets or {}
    sc = Scenarios(season, league, n=sims, seed=seed)
    my_score = float(league.get("my_score", 0))
    pools = Scenarios._pools(season)

    # Start every tribe at the EV-max corner, then improve one tribe at a time.
    current: Dict[str, Alloc] = {}
    cands: Dict[str, List[Alloc]] = {}
    for name, members in pools.items():
        budget = int(budgets.get(name, default_budget))
        cands[name] = candidate_allocations(members, probs, budget=budget)
        fav = max(members, key=lambda i: probs.get(i, 0.0))
        current[name] = {fav: budget}

    def merged_alloc(over: Optional[Tuple[str, Alloc]] = None) -> Alloc:
        out: Alloc = {}
        for name, a in current.items():
            use = over[1] if over and over[0] == name else a
            for k, v in use.items():
                out[k] = out.get(k, 0) + v
        return out

    # Accept a challenger only when it beats the incumbent by more than the
    # noise, with the threshold widened for how many challengers were tried.
    #
    # Two bugs were fixed here. The threshold used to be 1/sims, about 25 times
    # smaller than the real standard error, so on a tribe whose candidates sit
    # within a couple of points of each other the pick moved with the random
    # seed and skipped the genuine favourite. And acceptance used to be greedy
    # over every candidate in turn: at a 5% error rate, a few hundred
    # candidates yield a dozen false positives by chance, each one shifting the
    # incumbent, so a chain of them could land on an allocation worse than the
    # EV-max start. Now each pass scores every candidate against one fixed
    # incumbent, takes only the single best, and applies a Bonferroni-corrected
    # threshold for having gone looking.
    def ev(alloc: Alloc) -> float:
        return expected_points(alloc, probs)

    best_credits = win_credits(merged_alloc(), sc, my_score)
    for _ in range(rounds):
        improved = False
        for name in pools:
            incumbent = list(best_credits)
            base_ev = ev(merged_alloc())
            z = _threshold_z(len(pools[name]))
            scored = []
            for cand in cands[name]:
                merged = merged_alloc((name, cand))
                gain, se = paired_gain(merged, incumbent, sc, my_score)
                scored.append((gain, se, ev(merged), cand))
            scored = [s for s in scored if s[0] > 0.0]
            if not scored:
                continue
            # Taking the single largest measured gain is itself a selection
            # effect: among candidates whose true gains are equal, which one
            # measures highest is noise, so the pick moved with the seed even
            # though the acceptance test below is sound. Everything within an
            # error bar of the leader is treated as tied, and the tie is broken
            # on expected points, which do not depend on the draw.
            top = max(scored, key=lambda s: s[0])
            tied = [s for s in scored if s[0] >= top[0] - z * s[1]]
            best_gain, best_se, best_cand_ev, best_cand = max(
                tied, key=lambda s: (s[2], sorted(s[3].items())))
            take = best_gain > z * best_se
            if not take and best_cand_ev > base_ev + 1e-9:
                # Nothing beat the incumbent on win probability, so fall back
                # to collecting points. This is what keeps a dead position from
                # freezing on its starting guess and banking nothing.
                take = True
            if take:
                current[name] = best_cand
                best_credits = win_credits(merged_alloc(), sc, my_score)
                improved = True
        if not improved:
            break

    best_p = sum(best_credits) / sc.n
    final = merged_alloc()
    ev_alloc = {}
    for name, members in pools.items():
        fav = max(members, key=lambda i: probs.get(i, 0.0))
        ev_alloc[fav] = ev_alloc.get(fav, 0) + int(budgets.get(name, default_budget))
    diag = {
        "win_probability": best_p,
        "win_probability_if_ev_max": win_probability(ev_alloc, sc, my_score),
        "expected_points": expected_points(final, probs),
        "expected_points_if_ev_max": expected_points(ev_alloc, probs),
        "vote_probabilities": probs,
        "boot_probabilities": season.boot_probabilities(),
        "scenarios": sims,
        "opponents": sc.n_opp,
    }
    return current, diag
