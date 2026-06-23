"""Unit tests for damage_calc, using known type matchups as sanity checks."""

from pokeadvisor import damage_calc
from pokeadvisor.pokeapi_client import get_pokemon_data, get_move_data


def test_water_move_vs_fire_flying_is_super_effective():
    # Water (against Fire/Flying charizard): Fire is 2x, Flying is 1x -> 2x overall.
    multiplier = damage_calc.type_effectiveness("water", ["fire", "flying"])
    assert multiplier == 2.0
    assert damage_calc.effectiveness_tier(multiplier) == "super effective"


def test_electric_move_vs_ground_is_no_effect():
    multiplier = damage_calc.type_effectiveness("electric", ["ground"])
    assert multiplier == 0.0
    assert damage_calc.effectiveness_tier(multiplier) == "no effect"


def test_normal_move_vs_ghost_is_no_effect():
    multiplier = damage_calc.type_effectiveness("normal", ["ghost", "poison"])
    assert multiplier == 0.0


def test_fire_move_vs_grass_steel_is_4x_super_effective():
    # Fire is 2x against Grass and 2x against Steel -> 4x combined.
    multiplier = damage_calc.type_effectiveness("fire", ["grass", "steel"])
    assert multiplier == 4.0
    assert damage_calc.effectiveness_tier(multiplier) == "super effective"


def test_stab_applies_when_move_type_matches_attacker():
    assert damage_calc.stab_multiplier("electric", ["electric"]) == 1.5
    assert damage_calc.stab_multiplier("electric", ["fire", "flying"]) == 1.0


def test_calculate_damage_status_move_deals_zero():
    attacker = {"types": ["electric"], "stats": {"attack": 55, "special-attack": 50}}
    defender = {"types": ["water"], "stats": {"defense": 40, "special-defense": 50}}
    status_move = {"type": "normal", "power": None, "damage_class": "status"}
    result = damage_calc.calculate_damage(attacker, status_move, defender)
    assert result["damage"] == 0.0
    assert result["effectiveness"] == "status"


def test_calculate_damage_super_effective_beats_resisted():
    pikachu = get_pokemon_data("pikachu")
    charizard = get_pokemon_data("charizard")
    bulbasaur = get_pokemon_data("bulbasaur")

    thunderbolt = get_move_data("thunderbolt")

    vs_charizard = damage_calc.calculate_damage(pikachu, thunderbolt, charizard)
    vs_bulbasaur = damage_calc.calculate_damage(pikachu, thunderbolt, bulbasaur)

    # Electric is super effective into Fire/Flying charizard, but resisted
    # (0.5x) into Grass/Poison bulbasaur, so the former should deal more damage.
    assert vs_charizard["effectiveness"] == "super effective"
    assert vs_bulbasaur["effectiveness"] == "not very effective"
    assert vs_charizard["damage"] > vs_bulbasaur["damage"]


def test_rank_moves_orders_by_damage_descending():
    pikachu = get_pokemon_data("pikachu")
    charizard = get_pokemon_data("charizard")
    moves = [get_move_data("thunderbolt"), get_move_data("quick-attack")]

    ranked = damage_calc.rank_moves(pikachu, moves, charizard)

    assert len(ranked) == 2
    assert ranked[0]["damage"] >= ranked[1]["damage"]
    assert ranked[0]["move"] == "thunderbolt"
