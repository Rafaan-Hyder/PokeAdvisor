# PokéAdvisor — Performance Evaluation

Run with: `python evaluate.py`. Underlying logic lives in `evaluate.py` and
is exercised by `tests/test_evaluate.py`.

## 1. Moveset Predictor

**Method.** For each replayed battle, we step through the opponent's
revealed moves in order. Before each move is revealed, we check whether it
was in our current top-4 prediction; after checking, we apply
`update_with_observed_move` so the next check reflects what we'd actually
know at that point in a real battle (this mirrors how the predictor would
be used live, rather than re-predicting from scratch every turn).

**Data.** `data/replays/sample_replays.json` — three constructed replay
logs (Pikachu, Charizard, Bulbasaur), built against the same usage-stats
fixture used in Stage 3 (`data/usage_stats/gen9ou-sample.txt`).

**Results:**

| Replay | Pokémon | Hits | Hit rate |
|---|---|---|---|
| sample-battle-1 | Pikachu | 2/3 | 66.7% |
| sample-battle-2 | Charizard | 2/3 | 66.7% |
| sample-battle-3 | Bulbasaur | 4/4 | 100.0% |
| **Overall** | | **8/10** | **80.0%** |

**Discussion.** The two misses (Quick Attack for Pikachu, Solar Beam for
Charizard) are deliberate: both moves rank 5th by usage in their
respective fixture data, just outside the top-4 cutoff, to confirm the
metric isn't trivially 100%. Bulbasaur hits 100% because its fixture data
only lists 4 moves total, so the "top 4" is the entire moveset by
construction. This shows the predictor behaves correctly — high but not
perfect hit rate when the true moveset extends past the top-4 cutoff — but
**the 80% figure itself is not meaningful as a real-world accuracy claim**;
it's a property of three hand-built fixtures, not actual Showdown replay
data or real Smogon usage stats. See the caveat below.

## 2. Counter Recommendation Engine

**Method.** Run `counter_engine.recommend_action` against constructed
battle scenarios where the objectively correct action is known by
construction (same scenarios as `tests/test_counter_engine.py`), and
measure the rate at which the engine's top recommendation matches.

**Results:**

| Scenario | Expected | Recommended | Agree? |
|---|---|---|---|
| Super-effective move beats a neutral one | flamethrower | flamethrower | ✅ |
| Switch out of a 2x-weak matchup into a resistant tank | switch | switch | ✅ |
| Weak neutral move beats a move with no effect | quick-attack | quick-attack | ✅ |

**Agreement rate: 100% (3/3).**

**Discussion.** These scenarios were deliberately constructed (extreme
stat/type contrasts) to have an unambiguous correct answer, so 100%
agreement here demonstrates the engine's core logic — type effectiveness,
STAB, and the expected/worst-case blend — behaves correctly on clear-cut
cases. It does not measure performance on closer, more realistic
50/50-ish decisions, which would require either more scenarios with
human-expert-labeled "correct" answers or, eventually, real battle replay
outcomes to compare against.

## Caveat: dummy data throughout

This sandbox's network policy blocks both `pokeapi.co` and
`smogon.com`/Showdown's replay archive, so every input to this evaluation
is a small, hand-built fixture (`data/cache/`, `data/usage_stats/`,
`data/replays/`) rather than real API data, real monthly usage stats, or
real battle logs — see the README's "Status" notes for the same caveat at
each prior stage. The evaluation methodology (replay-and-check for the
predictor, scenario-agreement for the counter engine) is built to run
unmodified once real data is available; only the fixture files would need
to be replaced with real downloads/replays for the numbers above to become
meaningful performance claims rather than sanity checks.
