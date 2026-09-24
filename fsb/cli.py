"""Command line entry point.  Run `python3 -m fsb <command>`."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Optional

from .allocate import optimise
from .draft import DATA, draft_board, load_scoring, mvp_pick, simulate_placements
from .model import Season


def _league() -> dict:
    with open(os.path.join(DATA, "league.json"), "r", encoding="utf-8") as fh:
        return json.load(fh)


def _state() -> dict:
    with open(os.path.join(DATA, "state.json"), "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_state(state: dict) -> None:
    with open(os.path.join(DATA, "state.json"), "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)
        fh.write("\n")


def _resolve(season: Season, who: str) -> str:
    """Accept an id, a first name, or any unambiguous substring."""
    who_l = who.lower()
    if who_l in season.cast:
        return who_l
    hits = [c.id for c in season.cast.values()
            if who_l in c.name.lower() or who_l in c.id]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        raise SystemExit(f"no castaway matches {who!r}")
    raise SystemExit(f"{who!r} is ambiguous: {', '.join(hits)}")


def cmd_picks(args) -> None:
    season, league = Season(), _league()
    if args.sims:
        league = dict(league)
    alloc, diag = optimise(season, league, **({"sims": args.sims} if args.sims else {}))
    probs = diag["boot_probabilities"]

    print(f"EPISODE {season.episode} - point allocation")
    print(f"league: {league.get('league_name')}   "
          f"me: {league.get('my_score')} pts vs {diag['opponents']} opponents")
    print()
    for tribe, a in alloc.items():
        live = [c for c in season.alive() if (c.tribe or "UNASSIGNED") == tribe]
        print(f"  {tribe}  ({len(live)} left, 10 points to spend)")
        for cid, pts in sorted(a.items(), key=lambda kv: -kv[1]):
            if pts:
                print(f"     {pts:2d} -> {season.cast[cid].name:30s} "
                      f"p(boot)={probs.get(cid, 0):.3f}")
        print()

    print(f"  P(win league)      {diag['win_probability']:.4f}")
    print(f"  ...if I chased EV  {diag['win_probability_if_ev_max']:.4f}")
    print(f"  expected points    {diag['expected_points']:.2f} "
          f"(EV-max would be {diag['expected_points_if_ev_max']:.2f})")
    if diag["win_probability"] <= diag["win_probability_if_ev_max"] + 1e-9:
        print("  -> field is beatable on accuracy alone; no need to gamble.")
    else:
        print("  -> deviating from the obvious boot buys more than it costs.")
    if not season.state.get("tribes"):
        print("\n  WARNING: no tribe assignments in data/state.json, so the")
        print("  whole cast is priced as one pool. Fill them in after the")
        print("  premiere or the pre-merge numbers will be wrong.")


def cmd_board(args) -> None:
    season = Season()
    rows = draft_board(season, **({"n": args.sims} if args.sims else {}))
    print(f"{'castaway':32s} {'age':>3s} {'E[pts]':>7s} {'P(win)':>7s} "
          f"{'P(top3)':>8s} {'weeks':>6s}")
    for cid, pts, p in rows:
        c = season.cast[cid]
        top3 = p["p_win"] + p["p_second"] + p["p_third"]
        print(f"{c.name:32s} {c.age:3d} {pts:7.1f} {p['p_win']:7.3f} "
              f"{top3:8.3f} {p['mean_weeks']:6.1f}")
    print("\nDraft for E[pts]; pick the MVP for P(win). They are not the same")
    print("player, and that gap is most of the edge in this format.")


def cmd_mvp(args) -> None:
    # The Sole Survivor pick is independent of the draft - the site lets you
    # name ANY castaway, and ours is not on our roster. Only --roster narrows it.
    season = Season()
    roster = args.roster or []
    pick, stats = mvp_pick(season, roster, **({"n": args.sims} if args.sims else {}))
    scope = "my roster" if roster else "the whole cast"
    print(f"MVP / sole-survivor pick from {scope}: {season.cast[pick].name}")
    print(f"  P(win)   {stats['p_win']:.3f}")
    print(f"  P(top 3) {stats['p_win']+stats['p_second']+stats['p_third']:.3f}")


def cmd_record(args) -> None:
    season, state = Season(), _state()
    cid = _resolve(season, args.who)
    if cid in state["eliminated"]:
        raise SystemExit(f"{season.cast[cid].name} is already recorded as out")
    state["eliminated"].append(cid)
    state["edit"].pop(cid, None)
    state["idols"] = [i for i in state.get("idols", []) if i != cid]
    state["episode"] = int(state.get("episode", 1)) + 1
    _save_state(state)
    print(f"recorded: {season.cast[cid].name} voted out "
          f"(now {len(state['eliminated'])} gone, next up episode "
          f"{state['episode']})")


def cmd_edit(args) -> None:
    season, state = Season(), _state()
    cid = _resolve(season, args.who)
    val = max(-1.0, min(1.0, args.value))
    state.setdefault("edit", {})[cid] = val
    _save_state(state)
    word = "doomed" if val > 0.3 else ("protected" if val < -0.3 else "neutral")
    print(f"{season.cast[cid].name}: edit={val:+.2f} ({word})")


def cmd_tribe(args) -> None:
    season, state = Season(), _state()
    cid = _resolve(season, args.who)
    state.setdefault("tribes", {})[cid] = args.tribe
    _save_state(state)
    print(f"{season.cast[cid].name} -> {args.tribe}")


def cmd_status(args) -> None:
    season, state = Season(), _state()
    print(f"episode {season.episode}   merged={season.merged()}   "
          f"{len(season.alive())} still in")
    for name, members in sorted(season.tribes().items()):
        print(f"\n  {name}")
        probs = season.boot_probabilities()
        for c in sorted(members, key=lambda c: -probs.get(c.id, 0)):
            flags = []
            if c.idol:
                flags.append("idol")
            if c.edit:
                flags.append(f"edit{c.edit:+.1f}")
            tag = ("  [" + ", ".join(flags) + "]") if flags else ""
            print(f"     {probs.get(c.id, 0):.3f}  {c.name:30s} {c.age}{tag}")
    if state["eliminated"]:
        gone = ", ".join(season.cast[c].name for c in state["eliminated"])
        print(f"\n  out: {gone}")


def cmd_rules(args) -> None:
    sc = load_scoring()
    for block, body in sc.items():
        if block.startswith("_"):
            continue
        print(f"[{block}]  confidence={body.get('confidence', '?')}")
        for k, v in body.items():
            if not k.startswith("_") and k != "confidence":
                print(f"    {k}: {v}")
        print()


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(prog="fsb", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn, help_):
        p = sub.add_parser(name, help=help_)
        p.set_defaults(func=fn)
        return p

    p = add("picks", cmd_picks, "this week's point allocation")
    p.add_argument("--sims", type=int, default=0)
    p = add("board", cmd_board, "draft board by expected season points")
    p.add_argument("--sims", type=int, default=0)
    p = add("mvp", cmd_mvp, "sole-survivor pick")
    p.add_argument("--roster", nargs="*", default=None)
    p.add_argument("--sims", type=int, default=0)
    p = add("record", cmd_record, "record a boot and advance the episode")
    p.add_argument("who")
    p = add("edit", cmd_edit, "set a castaway's edit signal (-1..1)")
    p.add_argument("who")
    p.add_argument("value", type=float)
    p = add("tribe", cmd_tribe, "assign a castaway to a tribe")
    p.add_argument("who")
    p.add_argument("tribe")
    add("status", cmd_status, "current board state")
    add("rules", cmd_rules, "scoring constants in use")

    args = ap.parse_args(argv)
    args.func(args)
    return 0
