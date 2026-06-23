"""Damage calculation engine: type effectiveness, STAB, and the core damage formula.

The core formula implemented here is the standard Pokémon damage formula
(simplified — no critical hits, random damage roll, weather, or item/ability
modifiers, since those aren't knowable from the menu the player sees):

    Damage = ((2 * Level / 5 + 2) * Power * Attack / Defense / 50 + 2) * Modifiers

where Modifiers = STAB * TypeEffectiveness. STAB (Same-Type Attack Bonus) is
1.5x when the move's type matches one of the attacker's types. Type
effectiveness is the product of the move's multiplier against each of the
defender's types (e.g. a Water move into a Fire/Rock Pokémon is 2.0 * 2.0 =
4.0x, "super effective").

Attack/Defense are chosen by the move's damage class: physical moves use
attack/defense, special moves use special-attack/special-defense.
"""

import json
import os

TYPE_CHART_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "type_chart.json")

_type_chart_cache = None


def _load_type_chart():
    global _type_chart_cache
    if _type_chart_cache is None:
        with open(TYPE_CHART_PATH, "r") as f:
            _type_chart_cache = json.load(f)
    return _type_chart_cache


def type_effectiveness(move_type, defender_types):
    """Return the combined type-effectiveness multiplier for a move against
    a (possibly dual-typed) defender.

    Looks up each defending type in the attacking type's row of the chart;
    a missing entry means the default 1x (neutral) multiplier. The result
    for dual types is the product of both lookups (e.g. 2x * 2x = 4x).
    """
    chart = _load_type_chart()
    row = chart.get(move_type, {})
    multiplier = 1.0
    for defender_type in defender_types:
        multiplier *= row.get(defender_type, 1.0)
    return multiplier


def stab_multiplier(move_type, attacker_types):
    """Return 1.5 if the move's type matches one of the attacker's types, else 1.0."""
    return 1.5 if move_type in attacker_types else 1.0


def effectiveness_tier(multiplier):
    """Classify a type-effectiveness multiplier into a human-readable tier."""
    if multiplier == 0:
        return "no effect"
    if multiplier < 1:
        return "not very effective"
    if multiplier > 1:
        return "super effective"
    return "neutral"


def calculate_damage(attacker, move, defender, level=50):
    """Estimate the damage a move deals, using the core Pokémon damage formula.

    attacker/defender are dicts shaped like pokeapi_client.get_pokemon_data's
    output ({"types": [...], "stats": {...}, ...}). move is shaped like
    pokeapi_client.get_move_data's output ({"type": ..., "power": ...,
    "damage_class": ...}).

    Returns a dict: {"damage": float, "type_multiplier": float,
    "effectiveness": str, "stab": float}. Status moves (power is None) deal
    0 damage by definition.
    """
    power = move["power"]
    if power is None:
        return {"damage": 0.0, "type_multiplier": 1.0, "effectiveness": "status", "stab": 1.0}

    if move["damage_class"] == "physical":
        attack_stat = attacker["stats"]["attack"]
        defense_stat = defender["stats"]["defense"]
    else:
        attack_stat = attacker["stats"]["special-attack"]
        defense_stat = defender["stats"]["special-defense"]

    type_mult = type_effectiveness(move["type"], defender["types"])
    stab = stab_multiplier(move["type"], attacker["types"])
    modifiers = stab * type_mult

    damage = ((2 * level / 5 + 2) * power * attack_stat / defense_stat / 50 + 2) * modifiers

    return {
        "damage": damage,
        "type_multiplier": type_mult,
        "effectiveness": effectiveness_tier(type_mult),
        "stab": stab,
    }


def rank_moves(attacker, moves, defender, level=50):
    """Rank the attacker's moves against the defender by estimated damage.

    moves is a list of move dicts (pokeapi_client.get_move_data output).
    Returns a list of {"move": name, "damage": float, "effectiveness": str,
    "stab": float} sorted by damage descending.
    """
    results = []
    for move in moves:
        result = calculate_damage(attacker, move, defender, level=level)
        results.append({
            "move": move["name"],
            "damage": result["damage"],
            "effectiveness": result["effectiveness"],
            "stab": result["stab"],
        })
    results.sort(key=lambda r: r["damage"], reverse=True)
    return results
