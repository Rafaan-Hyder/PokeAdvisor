"""Evaluation script for PokéAdvisor's two predictive components.

1. Moveset predictor: replays a handful of battle logs (data/replays/) move
   by move and checks whether each move the opponent actually used was in
   our top-4 predicted moveset at the time. Reports a hit rate.
2. Counter engine: runs the recommendation engine against constructed
   battle scenarios with a known objectively-correct action, and reports
   the agreement rate.

Run with: python evaluate.py
"""

import json
import os

from pokeadvisor import counter_engine, moveset_predictor

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
USAGE_STATS_PATH = os.path.join(DATA_DIR, "usage_stats", "gen9ou-sample.txt")
REPLAYS_PATH = os.path.join(DATA_DIR, "replays", "sample_replays.json")


def evaluate_moveset_predictor():
    """Replay each logged battle and check if each revealed move was predicted.

    For every move an opponent reveals, we ask: was this move in the top-4
    prediction *before* it was revealed? After checking, we apply
    update_with_observed_move so later checks in the same replay reflect
    what we'd have known at that point in a real battle.

    Returns a dict with per-replay and overall hit rates.
    """
    usage_stats = moveset_predictor.parse_usage_file(USAGE_STATS_PATH)
    with open(REPLAYS_PATH, "r") as f:
        replays = json.load(f)

    per_replay = []
    total_hits = 0
    total_checks = 0

    for replay in replays:
        prediction = moveset_predictor.predict_moveset(replay["pokemon"], usage_stats)
        hits = 0
        for move in replay["revealed_moves"]:
            predicted_moves = {entry["move"] for entry in prediction}
            if move in predicted_moves:
                hits += 1
            prediction = moveset_predictor.update_with_observed_move(prediction, move)

        total = len(replay["revealed_moves"])
        per_replay.append({
            "replay_id": replay["replay_id"],
            "pokemon": replay["pokemon"],
            "hits": hits,
            "total": total,
            "hit_rate": hits / total if total else 0.0,
        })
        total_hits += hits
        total_checks += total

    return {
        "per_replay": per_replay,
        "overall_hit_rate": total_hits / total_checks if total_checks else 0.0,
    }


def _counter_engine_scenarios():
    """Constructed battle scenarios with a known objectively-correct action.

    Mirrors tests/test_counter_engine.py; kept self-contained here so this
    script can run standalone.
    """
    return [
        {
            "name": "super-effective beats neutral",
            "player": {"types": ["fire", "flying"], "stats": {"attack": 84, "defense": 78, "special-attack": 109, "special-defense": 85}},
            "opponent": {"types": ["grass", "poison"], "stats": {"attack": 49, "defense": 49, "special-attack": 65, "special-defense": 65}},
            "player_moves": [
                {"name": "flamethrower", "type": "fire", "power": 90, "damage_class": "special"},
                {"name": "tackle", "type": "normal", "power": 40, "damage_class": "physical"},
            ],
            "predicted_moveset": [{"move": "vine-whip", "weight": 1.0}],
            "bench": None,
            "expected_action": "flamethrower",
        },
        {
            "name": "switch out of a bad matchup",
            "player": {"types": ["grass"], "stats": {"attack": 60, "defense": 50, "special-attack": 60, "special-defense": 50}},
            "opponent": {"types": ["fire"], "stats": {"attack": 80, "defense": 70, "special-attack": 100, "special-defense": 70}},
            "player_moves": [
                {"name": "vine-whip", "type": "grass", "power": 45, "damage_class": "physical"},
            ],
            "predicted_moveset": [{"move": "flamethrower", "weight": 1.0}],
            "bench": [{"name": "incoming", "pokemon": {"types": ["water"], "stats": {"attack": 60, "defense": 80, "special-attack": 60, "special-defense": 90}}}],
            "expected_action": "switch",
        },
        {
            "name": "weak neutral move beats a no-effect move",
            "player": {"types": ["electric"], "stats": {"attack": 55, "defense": 40, "special-attack": 50, "special-defense": 50}},
            "opponent": {"types": ["ground"], "stats": {"attack": 90, "defense": 70, "special-attack": 50, "special-defense": 60}},
            "player_moves": [
                {"name": "thunderbolt", "type": "electric", "power": 90, "damage_class": "special"},
                {"name": "quick-attack", "type": "normal", "power": 40, "damage_class": "physical"},
            ],
            "predicted_moveset": [{"move": "earthquake", "weight": 0.7}, {"move": "tackle", "weight": 0.3}],
            "bench": None,
            "expected_action": "quick-attack",
        },
    ]


def evaluate_counter_engine():
    """Run the recommendation engine against constructed scenarios and
    report agreement with the known-correct action.
    """
    results = []
    agreements = 0

    for scenario in _counter_engine_scenarios():
        result = counter_engine.recommend_action(
            scenario["player"],
            scenario["player_moves"],
            scenario["opponent"],
            scenario["predicted_moveset"],
            bench=scenario["bench"],
        )
        recommendation = result["recommendation"]
        chosen = recommendation.get("move") or recommendation["action"]
        agreed = chosen == scenario["expected_action"]
        agreements += int(agreed)
        results.append({
            "scenario": scenario["name"],
            "expected": scenario["expected_action"],
            "recommended": chosen,
            "agreed": agreed,
        })

    return {
        "per_scenario": results,
        "agreement_rate": agreements / len(results) if results else 0.0,
    }


def main():
    print("=== Moveset Predictor Evaluation ===")
    moveset_results = evaluate_moveset_predictor()
    for entry in moveset_results["per_replay"]:
        print(f"  {entry['replay_id']} ({entry['pokemon']}): {entry['hits']}/{entry['total']} hits "
              f"({entry['hit_rate'] * 100:.1f}%)")
    print(f"  Overall hit rate: {moveset_results['overall_hit_rate'] * 100:.1f}%")

    print()
    print("=== Counter Engine Evaluation ===")
    counter_results = evaluate_counter_engine()
    for entry in counter_results["per_scenario"]:
        status = "AGREE" if entry["agreed"] else "DISAGREE"
        print(f"  [{status}] {entry['scenario']}: expected={entry['expected']!r}, "
              f"recommended={entry['recommended']!r}")
    print(f"  Agreement rate: {counter_results['agreement_rate'] * 100:.1f}%")


if __name__ == "__main__":
    main()
