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
from typing import Dict, List, Optional, Sequence, Tuple

from .model import Season

Alloc = Dict[str, int]


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

class Scenarios:
    """Pre-drawn futures: who goes home when, and what the field scored.

    Each opponent gets their own persistent misread of the cast, drawn once per
    scenario and carried all season.  That noise is where my edge lives: if the
    field's beliefs were just a sharpened copy of mine, I could never out-score
    them by being right, only by being different, and the optimiser would
    gamble every week to manufacture a difference.  Modelling opponents as
    noisy instead of merely herd-like keeps the edge honest.
    """

    def __init__(self, season: Season, league: dict, n: int = 8000,
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

        opp_scores = list(league.get("opponent_scores") or [])
        if not opp_scores:
            opp_scores = [float(league.get("my_score", 0))] * int(
                league.get("num_opponents", 9))
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
            self.boot_now.append(boot)
            for j in range(self.n_opp):
                opps[j] += self._field_points(rng, weights, misread[j], boot,
                                              pools, sharp, all_in)

            # Remaining episodes.  Future-me plays the same differentiating
            # policy this optimiser recommends, not naive EV-max.  Modelling
            # future-me as a herd follower would leave this week as the only
            # place to gain ground, and the optimiser would answer by dumping
            # the whole budget on a longshot in episode one.
            weights.pop(boot, None)
            mine_future = 0.0
            while len(weights) > 2:
                nxt = _draw(rng, weights)
                if _best_response(weights, sharp, all_in) == nxt:
                    mine_future += 10.0
                live = {"ALL": list(weights)}
                for j in range(self.n_opp):
                    opps[j] += self._field_points(rng, weights, misread[j],
                                                  nxt, live, sharp, all_in)
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


def optimise(season: Season, league: dict, sims: int = 8000, seed: int = 51,
             rounds: int = 2) -> Tuple[Dict[str, Alloc], dict]:
    """Best allocation per tribe, by coordinate ascent on P(win)."""
    probs = season.boot_probabilities()
    sc = Scenarios(season, league, n=sims, seed=seed)
    my_score = float(league.get("my_score", 0))
    pools = Scenarios._pools(season)

    # Start every tribe at the EV-max corner, then improve one tribe at a time.
    current: Dict[str, Alloc] = {}
    cands: Dict[str, List[Alloc]] = {}
    for name, members in pools.items():
        cands[name] = candidate_allocations(members, probs)
        fav = max(members, key=lambda i: probs.get(i, 0.0))
        current[name] = {fav: 10}

    def merged_alloc(over: Optional[Tuple[str, Alloc]] = None) -> Alloc:
        out: Alloc = {}
        for name, a in current.items():
            use = over[1] if over and over[0] == name else a
            for k, v in use.items():
                out[k] = out.get(k, 0) + v
        return out

    # Lexicographic: maximise P(win), break ties on expected points.
    #
    # The tie-break earns its keep in two places.  In a dead-lost position
    # every allocation scores P(win)=0 and the engine would otherwise freeze
    # on whatever it started with, banking nothing; and because P(win) is a
    # Monte Carlo estimate, candidates inside the noise floor are not really
    # distinguishable, so preferring points among them avoids fitting noise.
    tie_eps = 1.0 / max(sims, 1)

    def score(alloc: Alloc) -> Tuple[float, float]:
        return win_probability(alloc, sc, my_score), expected_points(alloc, probs)

    best_p, best_ev = score(merged_alloc())
    for _ in range(rounds):
        improved = False
        for name in pools:
            for cand in cands[name]:
                p, ev = score(merged_alloc((name, cand)))
                better = (p > best_p + tie_eps
                          or (abs(p - best_p) <= tie_eps and ev > best_ev + 1e-9))
                if better:
                    best_p, best_ev, improved = max(p, best_p), ev, True
                    current[name] = cand
        if not improved:
            break

    final = merged_alloc()
    ev_alloc = {}
    for name, members in pools.items():
        fav = max(members, key=lambda i: probs.get(i, 0.0))
        ev_alloc[fav] = ev_alloc.get(fav, 0) + 10
    diag = {
        "win_probability": best_p,
        "win_probability_if_ev_max": win_probability(ev_alloc, sc, my_score),
        "expected_points": expected_points(final, probs),
        "expected_points_if_ev_max": expected_points(ev_alloc, probs),
        "boot_probabilities": probs,
        "scenarios": sims,
        "opponents": sc.n_opp,
    }
    return current, diag
