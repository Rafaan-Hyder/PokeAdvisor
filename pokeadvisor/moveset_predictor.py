"""Probabilistic moveset predictor based on Smogon usage statistics.

Smogon (smogon.com/stats) publishes monthly plain-text usage files for each
competitive format. For every Pokémon, the file lists each move it was seen
running along with the percentage of battles in which that move appeared.
This module parses those files and uses the move percentages as a prior
probability distribution over the opponent's (unknown) moveset.

As the opponent reveals moves during a battle, `update_with_observed_move`
performs a simple Bayesian-style update: the revealed move is removed from
the "unseen" candidate pool (it's now confirmed, not a useful prediction
target any more) and the remaining probability mass is redistributed
proportionally among the still-unseen candidates so their weights sum back
to 1.
"""

import re

_HEADER_RE = re.compile(r"^\s*\|\s*([A-Za-z0-9\-' .]+?)\s*\|\s*$")
_MOVE_LINE_RE = re.compile(r"^\s*\|\s*(.+?)\s{2,}(\d+\.\d+)%\s*\|\s*$")
_SEPARATOR_RE = re.compile(r"^\s*\+-+\+\s*$")
_MOVES_SECTION_RE = re.compile(r"^\s*\|\s*Moves\s*\|?\s*$")
_OTHER_SECTION_RE = re.compile(r"^\s*\|\s*(Abilities|Items|Spreads|Tera Types|Teammates|Checks and Counters)\s*\|?\s*$")


def parse_usage_file(filepath):
    """Parse a Smogon-style usage stats text file.

    Returns a dict: {pokemon_name (lowercase): {move_name (lowercase): pct}}.
    Only the "Moves" section of each Pokémon's block is parsed; Abilities,
    Items, and Spreads sections are ignored.
    """
    with open(filepath, "r") as f:
        lines = f.readlines()

    usage = {}
    current_pokemon = None
    in_moves_section = False

    for line in lines:
        if _SEPARATOR_RE.match(line):
            continue

        if _MOVES_SECTION_RE.match(line):
            in_moves_section = True
            continue
        if _OTHER_SECTION_RE.match(line):
            in_moves_section = False
            continue

        move_match = _MOVE_LINE_RE.match(line)
        if in_moves_section and move_match:
            move_name = move_match.group(1).strip().lower().replace(" ", "-")
            percentage = float(move_match.group(2))
            usage[current_pokemon][move_name] = percentage
            continue

        header_match = _HEADER_RE.match(line)
        if header_match:
            candidate = header_match.group(1).strip()
            if candidate:
                current_pokemon = candidate.lower().replace(" ", "-")
                usage.setdefault(current_pokemon, {})
                in_moves_section = False

    return usage


def predict_moveset(pokemon_name, usage_stats, top_n=4):
    """Predict an opponent's likely moveset for a Pokémon.

    usage_stats is the dict produced by parse_usage_file. Returns a list of
    {"move": str, "weight": float} for the top_n most-used moves, with
    weights renormalized to sum to 1.0 (a probability distribution over
    "which move is in an unknown slot").
    """
    moves = usage_stats.get(pokemon_name.lower(), {})
    top_moves = sorted(moves.items(), key=lambda kv: kv[1], reverse=True)[:top_n]

    total = sum(pct for _, pct in top_moves)
    if total == 0:
        return []

    return [{"move": move, "weight": pct / total} for move, pct in top_moves]


def update_with_observed_move(predicted_moveset, observed_move):
    """Update a predicted moveset after the opponent reveals a move in battle.

    The observed move is confirmed (removed from the prediction pool, since
    predicting it is no longer useful) and the remaining moves' weights are
    renormalized to sum back to 1.0, preserving their relative proportions.
    If the observed move isn't in the current prediction, it's returned
    unchanged (we have no data to redistribute from).
    """
    observed_move = observed_move.lower().replace(" ", "-")

    remaining = [entry for entry in predicted_moveset if entry["move"] != observed_move]
    if len(remaining) == len(predicted_moveset):
        return predicted_moveset

    remaining_total = sum(entry["weight"] for entry in remaining)
    if remaining_total == 0:
        return remaining

    return [{"move": entry["move"], "weight": entry["weight"] / remaining_total} for entry in remaining]
