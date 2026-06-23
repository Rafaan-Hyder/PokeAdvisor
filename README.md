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

## Damage calculation

`pokeadvisor/damage_calc.py` implements the core Pokémon damage formula
(STAB + type effectiveness, no crit/random roll), using a bundled type
chart at `data/type_chart.json` and move data fixtures under
`data/cache/moves/`. `rank_moves()` ranks a Pokémon's moves against an
opponent by estimated damage and effectiveness tier.

## Moveset prediction

`pokeadvisor/moveset_predictor.py` parses Smogon-style usage stats text
files (see `data/usage_stats/gen9ou-sample.txt`) into per-Pokémon move
usage percentages. `predict_moveset()` turns those into a normalized
probability distribution over an opponent's likely moveset.
`update_with_observed_move()` performs the in-battle update described in
the proposal: once a move is revealed, it's removed from the unseen
candidate pool and the remaining probability mass is redistributed
proportionally among the still-unseen moves.

## Status

Stage 3 — moveset predictor implemented and tested. Counter recommendation
and GUI are not yet implemented.

Note: move/Pokémon data and usage stats are currently backed by
hand-written JSON/text fixtures (`data/cache/`, `data/usage_stats/`)
rather than live PokéAPI/Smogon downloads, since this sandbox's network
policy blocks outbound requests. The fetch code is already written and
should work unmodified once that's resolved.
