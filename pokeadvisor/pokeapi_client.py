"""Client for fetching Pokémon data (types, stats, moves) from PokéAPI.

PokéAPI (pokeapi.co) is a free, public REST API with no authentication. To
avoid hammering it during repeated test runs and demos, every successful
response is cached to a local JSON file under ``data/cache/``. Subsequent
calls for the same Pokémon read from disk instead of making a network
request.
"""

import json
import os

import requests

BASE_URL = "https://pokeapi.co/api/v2"
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cache")
MOVES_CACHE_DIR = os.path.join(CACHE_DIR, "moves")


def _cache_path(pokemon_name):
    return os.path.join(CACHE_DIR, f"{pokemon_name.lower()}.json")


def _read_cache(pokemon_name):
    path = _cache_path(pokemon_name)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None


def _write_cache(pokemon_name, data):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(_cache_path(pokemon_name), "w") as f:
        json.dump(data, f, indent=2)


def _move_cache_path(move_name):
    return os.path.join(MOVES_CACHE_DIR, f"{move_name.lower()}.json")


def _read_move_cache(move_name):
    path = _move_cache_path(move_name)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None


def _write_move_cache(move_name, data):
    os.makedirs(MOVES_CACHE_DIR, exist_ok=True)
    with open(_move_cache_path(move_name), "w") as f:
        json.dump(data, f, indent=2)


def get_pokemon_data(pokemon_name, use_cache=True):
    """Fetch a Pokémon's types, base stats, and move list.

    Returns a dict: {"name": str, "types": [str, ...],
    "stats": {stat_name: base_value, ...}, "moves": [move_name, ...]}.
    Raises requests.HTTPError if the Pokémon name is not found.
    """
    pokemon_name = pokemon_name.lower()

    if use_cache:
        cached = _read_cache(pokemon_name)
        if cached is not None:
            return cached

    response = requests.get(f"{BASE_URL}/pokemon/{pokemon_name}")
    response.raise_for_status()
    raw = response.json()

    data = {
        "name": raw["name"],
        "types": [t["type"]["name"] for t in raw["types"]],
        "stats": {s["stat"]["name"]: s["base_stat"] for s in raw["stats"]},
        "moves": [m["move"]["name"] for m in raw["moves"]],
    }

    if use_cache:
        _write_cache(pokemon_name, data)

    return data


def get_move_data(move_name, use_cache=True):
    """Fetch a move's type, base power, and damage class (physical/special/status).

    Returns a dict: {"name": str, "type": str, "power": int or None,
    "damage_class": str}. Raises requests.HTTPError if the move is not found.
    """
    move_name = move_name.lower()

    if use_cache:
        cached = _read_move_cache(move_name)
        if cached is not None:
            return cached

    response = requests.get(f"{BASE_URL}/move/{move_name}")
    response.raise_for_status()
    raw = response.json()

    data = {
        "name": raw["name"],
        "type": raw["type"]["name"],
        "power": raw["power"],
        "damage_class": raw["damage_class"]["name"],
    }

    if use_cache:
        _write_move_cache(move_name, data)

    return data
