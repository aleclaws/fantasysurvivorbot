"""Boot-probability model.

Two stages, because Survivor scoring has two stages:

  Pre-merge   P(boot) = P(this tribe loses immunity) * P(this player | tribe loses)
  Post-merge  P(boot) = P(player does not win immunity) * P(this player | vulnerable)

Within a stage, each player gets a hazard score that is a weighted sum of
features.  Hazards become probabilities through a softmax over the relevant
pool.  The softmax is the whole point: it keeps every probability strictly
positive, which matters because the league pays you for longshots.
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def _load(name: str) -> dict:
    with open(os.path.join(DATA, name), "r", encoding="utf-8") as fh:
        return json.load(fh)


@dataclass
class Castaway:
    id: str
    name: str
    age: int
    occupation: str
    tribe: Optional[str] = None
    phys: float = 0.5
    social: float = 0.5
    threat: float = 0.5
    # Edit risk in [-1, 1]. Set weekly from recaps: +1 = doomed-looking edit
    # (sudden backstory, on the wrong side of the numbers, name said out loud
    # at camp), -1 = protected (idol in pocket, clear winner edit).
    edit: float = 0.0
    # Cited pre-season pundit predictions, same sign convention as edit but
    # deliberately smaller (see priors.json). Real edit evidence dominates
    # this once the season starts, by weight and by typical magnitude.
    preseason_buzz: float = 0.0
    idol: bool = False
    out: bool = False
    placement: Optional[int] = None


def age_risk(age: int) -> float:
    """Age-driven boot risk, normalised to roughly [0, 1].

    New-era Survivor culls the oldest member of a losing tribe early and often;
    the effect is mild until the late 30s and then climbs fast.  Very young
    players carry a smaller, separate risk (read as naive, used as a number).
    """
    old = max(0.0, (age - 37) / 13.0)
    young = max(0.0, (25 - age) / 8.0) * 0.35
    return min(1.0, old + young)


class Season:
    """The cast, its features, and the hazard weights that act on them."""

    def __init__(self, season_file: str = "season51.json",
                 priors_file: str = "priors.json",
                 state_file: str = "state.json") -> None:
        meta = _load(season_file)
        priors = _load(priors_file)
        state = _load(state_file)
        self.meta = meta
        self.state = state
        self.weights = priors["weights"]
        feats = priors["features"]
        self.cast: Dict[str, Castaway] = {}
        for row in meta["cast"]:
            f = feats.get(row["id"], {})
            self.cast[row["id"]] = Castaway(
                id=row["id"], name=row["name"], age=row["age"],
                occupation=row["occupation"], tribe=row.get("tribe"),
                phys=f.get("phys", 0.5), social=f.get("social", 0.5),
                threat=f.get("threat", 0.5),
                preseason_buzz=f.get("preseason_buzz", 0.0),
            )
        self.apply_state(state)

    def apply_state(self, state: dict) -> None:
        """Overlay the live game state onto the static cast."""
        self.episode = int(state.get("episode", 1))
        self._merged = bool(state.get("merged", False))
        for cid, tribe in (state.get("tribes") or {}).items():
            if cid in self.cast:
                self.cast[cid].tribe = tribe
        for rank, cid in enumerate(state.get("eliminated") or [], start=1):
            if cid in self.cast:
                self.cast[cid].out = True
                self.cast[cid].placement = len(self.cast) - rank + 1
        for cid, val in (state.get("edit") or {}).items():
            if cid in self.cast:
                self.cast[cid].edit = max(-1.0, min(1.0, float(val)))
        for cid in (state.get("idols") or []):
            if cid in self.cast:
                self.cast[cid].idol = True

    # ---- roster views -------------------------------------------------

    def alive(self) -> List[Castaway]:
        return [c for c in self.cast.values() if not c.out]

    def tribes(self) -> Dict[str, List[Castaway]]:
        out: Dict[str, List[Castaway]] = {}
        for c in self.alive():
            out.setdefault(c.tribe or "UNASSIGNED", []).append(c)
        return out

    def merged(self) -> bool:
        """True once one tribe remains.

        Read from state, never inferred.  Inferring it from the roster would
        silently report a merge during the pre-season, when no tribe has been
        assigned yet and every player sits in one UNASSIGNED bucket.
        """
        return self._merged

    # ---- hazards ------------------------------------------------------

    def hazard(self, c: Castaway, postmerge: bool) -> float:
        w = self.weights["postmerge" if postmerge else "premerge"]
        h = (w["age"] * age_risk(c.age)
             + w["phys"] * c.phys
             + w["social"] * c.social
             + w["threat"] * c.threat
             + w["edit"] * c.edit
             + w.get("preseason_buzz", 0.0) * c.preseason_buzz)
        if c.idol:
            # An idol in hand does not make you safe, but it moves the target.
            h -= 0.9
        return h

    def conditional_boot(self, pool: Iterable[Castaway],
                         postmerge: bool) -> Dict[str, float]:
        """P(player is the boot | this pool goes to tribal), via softmax."""
        pool = list(pool)
        if not pool:
            return {}
        hs = {c.id: self.hazard(c, postmerge) for c in pool}
        top = max(hs.values())
        exp = {k: math.exp(v - top) for k, v in hs.items()}
        total = sum(exp.values())
        return {k: v / total for k, v in exp.items()}

    def tribe_loss_probability(self) -> Dict[str, float]:
        """P(tribe goes to tribal council this episode).

        Bigger tribes win immunity more often; the effect is real but small
        next to raw challenge variance, so it is deliberately damped.
        """
        tribes = self.tribes()
        if len(tribes) <= 1:
            return {name: 1.0 for name in tribes}
        strength = {}
        for name, members in tribes.items():
            avg_phys = sum(c.phys for c in members) / len(members)
            strength[name] = avg_phys + 0.04 * len(members)
        # Softmax on negative strength -> weak tribes lose more often.
        top = max(-s for s in strength.values())
        exp = {k: math.exp((-v) - top) for k, v in strength.items()}
        total = sum(exp.values())
        return {k: v / total for k, v in exp.items()}

    def step_probabilities(self, alive_ids: Iterable[str],
                           postmerge: bool) -> Dict[str, float]:
        """P(boot this episode) over an arbitrary set of survivors.

        Used by the forward simulation, which needs to re-price the cast at
        every step: the same physicality that keeps a player safe before the
        merge is what gets them targeted after it.
        """
        pool = [self.cast[i] for i in alive_ids if i in self.cast]
        if not pool:
            return {}
        if postmerge:
            return self.conditional_boot(pool, postmerge=True)
        groups: Dict[str, List[Castaway]] = {}
        for c in pool:
            groups.setdefault(c.tribe or "UNASSIGNED", []).append(c)
        if len(groups) <= 1:
            return self.conditional_boot(pool, postmerge=False)
        strength = {n: sum(c.phys for c in m) / len(m) + 0.04 * len(m)
                    for n, m in groups.items()}
        top = max(-s for s in strength.values())
        exp = {k: math.exp((-v) - top) for k, v in strength.items()}
        tot = sum(exp.values())
        loss = {k: v / tot for k, v in exp.items()}
        out: Dict[str, float] = {}
        for name, members in groups.items():
            for cid, pr in self.conditional_boot(members, False).items():
                out[cid] = pr * loss[name]
        return out

    def boot_probabilities(self) -> Dict[str, float]:
        """Unconditional P(player is booted this episode), over the whole cast."""
        post = self.merged()
        if post:
            pool = self.alive()
            return self.conditional_boot(pool, postmerge=True)
        loss = self.tribe_loss_probability()
        out: Dict[str, float] = {}
        for name, members in self.tribes().items():
            cond = self.conditional_boot(members, postmerge=False)
            for cid, p in cond.items():
                out[cid] = p * loss.get(name, 0.0)
        return out
