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

## Status

Stage 0 — project scaffolding only. No functionality implemented yet.
