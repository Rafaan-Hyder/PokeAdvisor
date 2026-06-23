"""Manual demo script: fetch and print data for a few sample Pokémon.

Run with: python scripts/fetch_sample_pokemon.py
"""

from pokeadvisor.pokeapi_client import get_pokemon_data

SAMPLE_POKEMON = ["pikachu", "charizard", "gengar"]


def main():
    for name in SAMPLE_POKEMON:
        data = get_pokemon_data(name)
        print(f"--- {data['name']} ---")
        print(f"Types: {data['types']}")
        print(f"Stats: {data['stats']}")
        print(f"Moves ({len(data['moves'])} total): {data['moves'][:10]}...")
        print()


if __name__ == "__main__":
    main()
