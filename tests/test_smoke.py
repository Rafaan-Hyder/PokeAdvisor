"""Smoke test: confirm all modules import cleanly."""

import pokeadvisor.damage_calc
import pokeadvisor.moveset_predictor
import pokeadvisor.counter_engine
import pokeadvisor.pokeapi_client
import pokeadvisor.gui


def test_modules_import():
    assert pokeadvisor.damage_calc
    assert pokeadvisor.moveset_predictor
    assert pokeadvisor.counter_engine
    assert pokeadvisor.pokeapi_client
    assert pokeadvisor.gui
