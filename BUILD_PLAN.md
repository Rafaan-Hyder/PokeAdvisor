# PokéAdvisor — Staged Build Plan for Claude Code

## Project Summary
A Python/Tkinter desktop tool that helps a Pokémon Showdown player pick the best move
in battle. Given the player's active Pokémon (with moves) and the opponent's active
Pokémon, it:
1. Calculates damage output for each of the player's moves (type effectiveness + STAB)
2. Predicts the opponent's likely moveset using Smogon usage stats
3. Recommends the best counter-play action

Full spec is in `PROPOSAL.md` in this repo.

## Ground rules for the agent
- Work in stages. After finishing each stage, STOP, summarize what was built, list any
  open questions/assumptions made, and wait for explicit approval before starting the
  next stage.
- Do not skip ahead even if the next stage seems obvious.
- Keep dependencies minimal: Python 3, `requests`, `tkinter` (stdlib), `pytest` for tests.
- Write small, testable functions. Favor clarity over cleverness — this is a course
  project that will be read and graded.
- Add docstrings/comments explaining the *algorithm*, not just the code, since the
  written report will reference this logic.

---

## Stage 0 — Project Scaffolding
- Create folder structure: `pokeadvisor/`, `tests/`, `data/`, `README.md`
- Set up a virtual environment + `requirements.txt`
- Stub out empty modules: `damage_calc.py`, `moveset_predictor.py`,
  `counter_engine.py`, `pokeapi_client.py`, `gui.py`, `main.py`
- Output: a runnable skeleton that does nothing yet but imports cleanly.
- **STOP for approval.**

## Stage 1 — PokéAPI Client
- Implement `pokeapi_client.py`: fetch a Pokémon's types, base stats, and move list
  from `pokeapi.co` (REST, no auth).
- Cache responses locally (JSON file in `data/cache/`) to avoid hammering the API
  during testing/demos.
- Write a small script/test that fetches and prints data for 2-3 sample Pokémon.
- **STOP for approval.**

## Stage 2 — Damage Calculation Engine
- Implement `damage_calc.py`:
  - Type effectiveness lookup (use PokéAPI type data, or a bundled type chart JSON
    if API calls are too slow for repeated lookups)
  - STAB multiplier logic
  - Core damage formula (level, power, attack/defense stats, modifiers)
  - Function that ranks a list of the player's moves against a given opponent
    Pokémon, returning damage estimates + effectiveness tier (super/neutral/not very/no effect)
- Unit tests with known matchups (e.g., a Water move vs a Fire/Rock Pokémon should be
  super effective) to sanity check the formula.
- **STOP for approval.**

## Stage 3 — Moveset Predictor
- Source Smogon usage stat files (download a recent month's OU stats, store under
  `data/usage_stats/`)
- Implement `moveset_predictor.py`:
  - Parse usage files into a lookup: Pokémon -> ranked moves with probabilities
  - Function `predict_moveset(pokemon_name)` returning top-4 likely moves + weights
  - Function `update_with_observed_move(pokemon_name, move)` that does the Bayesian
    update described in the proposal (confirm the move, redistribute remaining mass)
- Tests: verify parsing on a sample stats file, verify the update logic redistributes
  correctly.
- **STOP for approval.**

## Stage 4 — Counter Recommendation Engine
- Implement `counter_engine.py`:
  - Combine Stage 2 (damage calc) and Stage 3 (prediction) to recommend the player's
    best action: which move to use, or whether to switch
  - Simple minimax-style comparison: for each player action, estimate worst-case and
    expected-case opponent response, pick the action maximizing the player's net
    advantage
  - Return a recommendation + a one-sentence plain-language explanation
- Tests with 2-3 constructed battle scenarios where the "correct" answer is known.
- **STOP for approval.**

## Stage 5 — GUI
- Implement `gui.py` using Tkinter:
  - Input fields/dropdowns: player's Pokémon + moves, opponent's Pokémon
  - "Analyze" button
  - Output panel: ranked move list (color-coded by effectiveness), predicted opponent
    moveset with probabilities, recommended action with explanation
- Wire it to `main.py` as the entry point.
- **STOP for approval.**

## Stage 6 — Evaluation
- Build a small evaluation script (`evaluate.py`) that:
  - Runs the moveset predictor against a handful of real Showdown replay logs (manually
    collected or pasted in) and reports the prediction hit rate
  - Runs the counter engine against constructed scenarios and reports the agreement rate
    with the objectively optimal move
- Output a short `EVALUATION.md` summarizing results — this maps directly to the
  "Performance Evaluation" section of the report.
- **STOP for approval.**

## Stage 7 — Polish + Report Support
- Clean up README with setup/run instructions
- Make sure code is commented well enough to lift directly into the written report
- Final review pass together before the 6/24 presentation and 6/26 report deadline
