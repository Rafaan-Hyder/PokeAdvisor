# PokéAdvisor

An AI battle assistant for Pokémon Showdown. Given the player's active Pokémon
(with moves) and the opponent's active Pokémon, it calculates damage output,
predicts the opponent's likely moveset using Smogon usage stats, and
recommends the best counter-play action.

See `proposal.md` for the full project proposal, `BUILD_PLAN.md` for the
staged build plan this was implemented against, and `EVALUATION.md` for
performance evaluation results.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

The GUI (`pokeadvisor/gui.py`) uses Tkinter, which is part of the Python
standard library but sometimes ships as a separate OS package. If `python
main.py` fails with `ModuleNotFoundError: No module named 'tkinter'`,
install it for your platform (e.g. `sudo apt install python3-tk` on
Debian/Ubuntu) and recreate the venv.

## Run

```bash
python main.py        # launch the GUI
python evaluate.py    # run the evaluation suite, print a report
pytest                # run all unit tests
```

## Project structure

```
pokeadvisor/
  pokeapi_client.py     # Stage 1: fetch + cache Pokémon/move data from PokéAPI
  damage_calc.py         # Stage 2: type effectiveness, STAB, damage formula
  moveset_predictor.py    # Stage 3: parse Smogon usage stats, predict + update moveset
  counter_engine.py       # Stage 4: recommend the best action each turn
  gui.py                  # Stage 5: Tkinter desktop app tying it together
data/
  cache/                  # cached/fixture Pokémon + move data (see note below)
  type_chart.json         # bundled 18-type effectiveness chart
  usage_stats/            # Smogon-style usage stats file(s)
  replays/                # constructed battle logs used by evaluate.py
evaluate.py               # Stage 6: evaluation script (see EVALUATION.md)
tests/                     # pytest suite, one file per module
```

## How each piece works

**PokéAPI client** (`pokeadvisor/pokeapi_client.py`) fetches a Pokémon's
types, base stats, and move list, and a move's type/power/damage class,
from [PokéAPI](https://pokeapi.co), caching each response to
`data/cache/`. Demo: `python scripts/fetch_sample_pokemon.py`.

**Damage calculator** (`pokeadvisor/damage_calc.py`) implements the core
Pokémon damage formula (STAB + type effectiveness; no crit/random
roll/weather/abilities, since those aren't knowable from the pre-battle
menu) using a bundled type chart (`data/type_chart.json`). `rank_moves()`
ranks a Pokémon's moves against an opponent by estimated damage and
effectiveness tier.

**Moveset predictor** (`pokeadvisor/moveset_predictor.py`) parses
Smogon-style usage stats text files into per-Pokémon move usage
percentages, then `predict_moveset()` normalizes the top-N moves into a
probability distribution. `update_with_observed_move()` performs the
in-battle Bayesian-style update described in the proposal: once a move is
revealed, it's dropped from the unseen candidate pool and the remaining
probability mass is redistributed proportionally among what's left.

**Counter engine** (`pokeadvisor/counter_engine.py`) combines the above to
recommend the player's best action each turn — attack with a move, or
switch to a bench Pokémon. For each candidate it computes the player's
damage dealt (0 if switching), the opponent's probability-weighted
*expected* damage in return, and the opponent's *worst-case* damage (their
single most-damaging predicted move), blends these into a net-advantage
score (a simplified minimax), and returns the top-scoring action with a
plain-language explanation.

**GUI** (`pokeadvisor/gui.py`, launched via `python main.py`) is a Tkinter
desktop app: pick your active Pokémon and up to 4 of its moves, pick the
opponent's active Pokémon, click Analyze. Shows your moves ranked by
estimated damage (color-coded by effectiveness tier), the opponent's
predicted moveset with probabilities, and the recommended action with its
explanation.

**Evaluation** (`evaluate.py`) reports the moveset predictor's hit rate
against constructed replay logs and the counter engine's agreement rate
against constructed scenarios with a known-correct answer. Results and
discussion are in `EVALUATION.md`.

## Known limitations / assumptions

- **The GUI's moveset predictor runs on real data.** `gui.py` points
  `USAGE_STATS_PATH` at `data/usage_stats/gen9ou-1500.txt`, a real
  downloaded Smogon gen9ou moveset file (smogon.com/stats), not a
  fixture. `data/cache/` (25 Pokémon and their moves) is likewise real
  data fetched live from PokéAPI. Note Bulbasaur has no real OU usage
  entry — it isn't an OU-viable Pokémon — so its predicted moveset is
  legitimately empty, not a bug.
- **Fixtures are kept as a documented offline fallback.** The original
  hand-built fixtures (`data/usage_stats/gen9ou-sample.txt`,
  `data/replays/`) are not real API responses or monthly Smogon stats.
  They exist so the test suite and `evaluate.py`'s fixture-based
  evaluation work without network access; they're no longer what the
  GUI uses at runtime. `pokeapi_client.py` has been verified against the
  live PokéAPI and `moveset_predictor.py` has been verified against real
  monthly Smogon `moveset/` files — both work unmodified against real
  data. Note: real Smogon moveset files separate the move name and
  percentage with a single space, not the two-or-more the original
  fixture used, and include an `Other XX%` catch-all line;
  `parse_usage_file`/`_MOVE_LINE_RE` were fixed to handle both.
- **The GUI has no bench/switch input.** Per the build plan's Stage 5 spec
  (player Pokémon + moves, opponent Pokémon, Analyze), the GUI only
  surfaces move recommendations; `counter_engine`'s switch-recommendation
  path is tested directly (`tests/test_counter_engine.py`,
  `evaluate.py`) but isn't reachable from the GUI yet.
- **Move/Pokémon choices in the GUI are limited** to the intersection of a
  Pokémon's learnset and the moves we have cached power/type/category data
  for, since that data isn't fetchable live in this environment.
- **The damage formula omits crit chance, the random damage roll, weather,
  and item/ability modifiers** — none of these are knowable from the
  pre-battle menu the player sees, so including them wouldn't be
  decision-useful here.
