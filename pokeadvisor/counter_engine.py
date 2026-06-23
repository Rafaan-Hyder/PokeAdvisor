"""Counter-recommendation engine combining damage calc and moveset prediction.

For each action the player could take this turn — attacking with one of
their moves, or switching to a bench Pokémon — the engine estimates:

  - "my_damage": the damage the player's move deals this turn (0 if switching,
    since switching forfeits the player's attack)
  - "expected_damage_taken": the probability-weighted average damage the
    opponent deals back, using the predicted moveset from moveset_predictor
  - "worst_case_damage_taken": the damage from the single most-damaging move
    in the predicted moveset (a pessimistic read on the opponent's response)

These are combined into a "net_advantage" score — my_damage minus an
average of the expected- and worst-case damage taken — and the action with
the highest net_advantage is recommended. Averaging expected and worst case
is a simplified minimax: it rewards actions that do well on average without
being blindsided by the opponent's single best response.
"""

from pokeadvisor import damage_calc
from pokeadvisor.pokeapi_client import get_move_data


def _opponent_damage_profile(opponent, predicted_moveset, target):
    """Damage the opponent could deal to `target` with each predicted move.

    Returns a list of {"move": str, "weight": float, "damage": float}.
    """
    profile = []
    for entry in predicted_moveset:
        move_data = get_move_data(entry["move"])
        damage = damage_calc.calculate_damage(opponent, move_data, target)["damage"]
        profile.append({"move": entry["move"], "weight": entry["weight"], "damage": damage})
    return profile


def _expected_damage(profile):
    return sum(p["weight"] * p["damage"] for p in profile)


def _worst_case_damage(profile):
    return max((p["damage"] for p in profile), default=0.0)


def evaluate_move_action(player, move, opponent, predicted_moveset):
    """Evaluate attacking with a single move this turn."""
    my_damage = damage_calc.calculate_damage(player, move, opponent)["damage"]
    profile = _opponent_damage_profile(opponent, predicted_moveset, player)
    expected = _expected_damage(profile)
    worst = _worst_case_damage(profile)
    return {
        "action": "move",
        "move": move["name"],
        "my_damage": my_damage,
        "expected_damage_taken": expected,
        "worst_case_damage_taken": worst,
        "net_advantage": my_damage - (0.5 * expected + 0.5 * worst),
    }


def evaluate_switch_action(incoming_pokemon, incoming_name, opponent, predicted_moveset):
    """Evaluate switching out to a bench Pokémon this turn.

    The player deals no damage on a switch turn, so the score is purely
    about how much damage the incoming Pokémon avoids relative to staying in.
    """
    profile = _opponent_damage_profile(opponent, predicted_moveset, incoming_pokemon)
    expected = _expected_damage(profile)
    worst = _worst_case_damage(profile)
    return {
        "action": "switch",
        "pokemon": incoming_name,
        "my_damage": 0.0,
        "expected_damage_taken": expected,
        "worst_case_damage_taken": worst,
        "net_advantage": -(0.5 * expected + 0.5 * worst),
    }


def _explain(candidate):
    if candidate["action"] == "move":
        return (
            f"Use {candidate['move']}: estimated {candidate['my_damage']:.1f} damage dealt, "
            f"versus an estimated {candidate['expected_damage_taken']:.1f} damage taken in return."
        )
    return (
        f"Switch to {candidate['pokemon']}: the current matchup is unfavorable, and switching "
        f"limits the incoming damage to an estimated {candidate['expected_damage_taken']:.1f}."
    )


def recommend_action(player, player_moves, opponent, predicted_moveset, bench=None):
    """Recommend the player's best action this turn.

    player/opponent: dicts shaped like pokeapi_client.get_pokemon_data output.
    player_moves: list of move dicts (pokeapi_client.get_move_data output).
    predicted_moveset: list of {"move": str, "weight": float}, e.g. from
    moveset_predictor.predict_moveset.
    bench: optional list of {"name": str, "pokemon": pokemon_data} for
    Pokémon the player could switch into.

    Returns {"recommendation": dict, "candidates": [dict, ...], "explanation": str}.
    """
    candidates = [
        evaluate_move_action(player, move, opponent, predicted_moveset)
        for move in player_moves
    ]

    for entry in bench or []:
        candidates.append(
            evaluate_switch_action(entry["pokemon"], entry["name"], opponent, predicted_moveset)
        )

    best = max(candidates, key=lambda c: c["net_advantage"])

    return {
        "recommendation": best,
        "candidates": candidates,
        "explanation": _explain(best),
    }
