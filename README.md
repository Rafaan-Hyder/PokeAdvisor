# PokéAdvisor

An AI battle assistant for Pokémon Showdown. Given the player's active Pokémon
(with moves) and the opponent's active Pokémon, it calculates damage output,
predicts the opponent's likely moveset using Smogon usage stats, and
recommends the best counter-play action.

See `proposal.md` for the full project proposal and `BUILD_PLAN.md` for the
staged build plan.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Test

```bash
pytest
```

## PokéAPI cache

`pokeadvisor/pokeapi_client.py` fetches a Pokémon's types, base stats, and
move list from [PokéAPI](https://pokeapi.co) and caches the result under
`data/cache/<name>.json`. A handful of sample fixtures (pikachu, charizard,
gengar, bulbasaur) are committed so the client, its tests, and the demo
script work offline. Run the demo with:

```bash
python scripts/fetch_sample_pokemon.py
```

## Status

Stage 1 — PokéAPI client implemented and cached. Damage calc, moveset
prediction, counter recommendation, and GUI are not yet implemented.
