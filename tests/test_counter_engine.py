"""Tests for counter_engine, using constructed battle scenarios with a known
correct answer."""

import pytest

from pokeadvisor import counter_engine


def test_recommends_super_effective_move_over_neutral_one():
    player = {
        "name": "p", "types": ["fire", "flying"],
        "stats": {"attack": 84, "defense": 78, "special-attack": 109, "special-defense": 85},
    }
    opponent = {
        "name": "o", "types": ["grass", "poison"],
        "stats": {"attack": 49, "defense": 49, "special-attack": 65, "special-defense": 65},
    }
    flamethrower = {"name": "flamethrower", "type": "fire", "power": 90, "damage_class": "special"}
    tackle = {"name": "tackle", "type": "normal", "power": 40, "damage_class": "physical"}
    predicted_moveset = [{"move": "vine-whip", "weight": 1.0}]

    result = counter_engine.recommend_action(player, [flamethrower, tackle], opponent, predicted_moveset)

    assert result["recommendation"]["action"] == "move"
    assert result["recommendation"]["move"] == "flamethrower"


def test_recommends_switch_when_current_matchup_is_bad():
    current_player = {
        "name": "p", "types": ["grass"],
        "stats": {"attack": 60, "defense": 50, "special-attack": 60, "special-defense": 50},
    }
    incoming_player = {
        "name": "i", "types": ["water"],
        "stats": {"attack": 60, "defense": 80, "special-attack": 60, "special-defense": 90},
    }
    opponent = {
        "name": "o", "types": ["fire"],
        "stats": {"attack": 80, "defense": 70, "special-attack": 100, "special-defense": 70},
    }
    vine_whip = {"name": "vine-whip", "type": "grass", "power": 45, "damage_class": "physical"}
    predicted_moveset = [{"move": "flamethrower", "weight": 1.0}]
    bench = [{"name": "incoming", "pokemon": incoming_player}]

    result = counter_engine.recommend_action(
        current_player, [vine_whip], opponent, predicted_moveset, bench=bench
    )

    assert result["recommendation"]["action"] == "switch"
    assert result["recommendation"]["pokemon"] == "incoming"


def test_recommends_weaker_neutral_move_over_move_with_no_effect():
    # Thunderbolt is useless against a pure Ground type (no effect); a weak
    # neutral move that actually deals damage should win even though its
    # raw power is lower.
    player = {
        "name": "p", "types": ["electric"],
        "stats": {"attack": 55, "defense": 40, "special-attack": 50, "special-defense": 50},
    }
    opponent = {
        "name": "o", "types": ["ground"],
        "stats": {"attack": 90, "defense": 70, "special-attack": 50, "special-defense": 60},
    }
    thunderbolt = {"name": "thunderbolt", "type": "electric", "power": 90, "damage_class": "special"}
    quick_attack = {"name": "quick-attack", "type": "normal", "power": 40, "damage_class": "physical"}
    predicted_moveset = [{"move": "earthquake", "weight": 0.7}, {"move": "tackle", "weight": 0.3}]

    result = counter_engine.recommend_action(player, [thunderbolt, quick_attack], opponent, predicted_moveset)

    assert result["recommendation"]["move"] == "quick-attack"
    thunderbolt_candidate = next(c for c in result["candidates"] if c["move"] == "thunderbolt")
    assert thunderbolt_candidate["my_damage"] == 0.0


def test_explanation_mentions_the_recommended_action():
    player = {"name": "p", "types": ["fire"], "stats": {"attack": 80, "defense": 70, "special-attack": 80, "special-defense": 70}}
    opponent = {"name": "o", "types": ["grass"], "stats": {"attack": 60, "defense": 60, "special-attack": 60, "special-defense": 60}}
    flamethrower = {"name": "flamethrower", "type": "fire", "power": 90, "damage_class": "special"}
    predicted_moveset = [{"move": "vine-whip", "weight": 1.0}]

    result = counter_engine.recommend_action(player, [flamethrower], opponent, predicted_moveset)

    assert "flamethrower" in result["explanation"]
