"""Tests for pokeapi_client.

These run entirely against the fixture cache files committed under
data/cache/ (pikachu, charizard, bulbasaur), so they don't require network
access. If the cache for a sample Pokémon is missing, get_pokemon_data
falls back to a live PokéAPI request.
"""

from pokeadvisor import pokeapi_client


def test_get_pikachu_data():
    data = pokeapi_client.get_pokemon_data("pikachu")
    assert data["name"] == "pikachu"
    assert "electric" in data["types"]
    assert "hp" in data["stats"]
    assert "thunderbolt" in data["moves"]


def test_get_charizard_data():
    data = pokeapi_client.get_pokemon_data("charizard")
    assert data["name"] == "charizard"
    assert set(data["types"]) == {"fire", "flying"}


def test_cache_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(pokeapi_client, "CACHE_DIR", str(tmp_path))
    sample = {"name": "bulbasaur", "types": ["grass", "poison"], "stats": {}, "moves": []}
    pokeapi_client._write_cache("bulbasaur", sample)
    assert pokeapi_client._read_cache("bulbasaur") == sample


def test_get_pokemon_data_uses_cache_without_network(monkeypatch):
    def fail_if_called(*args, **kwargs):
        raise AssertionError("should not hit the network when cache is present")

    monkeypatch.setattr(pokeapi_client.requests, "get", fail_if_called)
    data = pokeapi_client.get_pokemon_data("pikachu")
    assert data["name"] == "pikachu"
    assert "electric" in data["types"]
