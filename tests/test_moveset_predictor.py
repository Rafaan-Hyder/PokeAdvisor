"""Tests for moveset_predictor: usage-file parsing and the Bayesian-style update."""

import os

import pytest

from pokeadvisor import moveset_predictor

SAMPLE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "usage_stats", "gen9ou-sample.txt"
)


@pytest.fixture
def usage_stats():
    return moveset_predictor.parse_usage_file(SAMPLE_FILE)


def test_parse_usage_file_finds_all_pokemon(usage_stats):
    assert set(usage_stats.keys()) == {"pikachu", "charizard", "bulbasaur"}


def test_parse_usage_file_extracts_move_percentages(usage_stats):
    assert usage_stats["pikachu"]["volt-tackle"] == 65.432
    assert usage_stats["pikachu"]["thunderbolt"] == 55.123
    assert usage_stats["charizard"]["flamethrower"] == 70.512


def test_parse_usage_file_does_not_leak_abilities_into_moves(usage_stats):
    assert "static" not in usage_stats["pikachu"]
    assert "solar-power" not in usage_stats["charizard"]


def test_predict_moveset_returns_top_n_normalized(usage_stats):
    prediction = moveset_predictor.predict_moveset("pikachu", usage_stats, top_n=4)
    assert len(prediction) == 4
    assert [entry["move"] for entry in prediction] == [
        "volt-tackle", "thunderbolt", "knock-off", "iron-tail",
    ]
    assert pytest.approx(sum(entry["weight"] for entry in prediction)) == 1.0


def test_predict_moveset_unknown_pokemon_returns_empty(usage_stats):
    assert moveset_predictor.predict_moveset("missingno", usage_stats) == []


def test_update_with_observed_move_redistributes_evenly():
    # Bulbasaur's 4 moves are evenly weighted at 25% each.
    prediction = [
        {"move": "vine-whip", "weight": 0.25},
        {"move": "tackle", "weight": 0.25},
        {"move": "sleep-powder", "weight": 0.25},
        {"move": "leech-seed", "weight": 0.25},
    ]
    updated = moveset_predictor.update_with_observed_move(prediction, "Tackle")

    assert len(updated) == 3
    assert "tackle" not in [entry["move"] for entry in updated]
    for entry in updated:
        assert entry["weight"] == pytest.approx(1 / 3)
    assert pytest.approx(sum(entry["weight"] for entry in updated)) == 1.0


def test_update_with_observed_move_preserves_relative_proportions():
    prediction = [
        {"move": "volt-tackle", "weight": 0.5},
        {"move": "thunderbolt", "weight": 0.3},
        {"move": "knock-off", "weight": 0.2},
    ]
    updated = moveset_predictor.update_with_observed_move(prediction, "volt-tackle")

    # thunderbolt was 0.3/0.5 = 1.5x knock-off's weight before; that ratio
    # should be preserved after renormalizing the remaining 0.5 mass to 1.0.
    weights = {entry["move"]: entry["weight"] for entry in updated}
    assert weights["thunderbolt"] == pytest.approx(0.6)
    assert weights["knock-off"] == pytest.approx(0.4)


def test_update_with_unobserved_move_is_noop():
    prediction = [{"move": "tackle", "weight": 1.0}]
    updated = moveset_predictor.update_with_observed_move(prediction, "hyper-beam")
    assert updated == prediction
