"""Sanity-check tests for evaluate.py's two evaluation routines."""

import pytest

import evaluate


def test_moveset_predictor_evaluation_reports_per_replay_and_overall():
    results = evaluate.evaluate_moveset_predictor()
    assert len(results["per_replay"]) == 3
    assert 0.0 <= results["overall_hit_rate"] <= 1.0
    bulbasaur_entry = next(r for r in results["per_replay"] if r["pokemon"] == "bulbasaur")
    assert bulbasaur_entry["hit_rate"] == 1.0


def test_counter_engine_evaluation_agrees_on_constructed_scenarios():
    results = evaluate.evaluate_counter_engine()
    assert len(results["per_scenario"]) == 3
    assert results["agreement_rate"] == 1.0
    assert all(entry["agreed"] for entry in results["per_scenario"])
