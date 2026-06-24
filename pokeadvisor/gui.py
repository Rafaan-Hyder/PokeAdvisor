"""Tkinter GUI for PokéAdvisor.

A single-window form: pick the player's active Pokémon and up to 4 of its
known moves, pick the opponent's active Pokémon, and click Analyze. The
output panel shows the player's moves ranked by estimated damage
(color-coded by type effectiveness), the opponent's predicted moveset with
probabilities, and the recommended action with a plain-language reason.

As the opponent reveals moves over the course of a battle, picking one
from "Opponent revealed a move" and clicking Reveal feeds it into
moveset_predictor.update_with_observed_move, narrowing the live
prediction; the next Analyze (and the recommendation it produces) uses
the updated, narrowed-down moveset. Switching opponents resets the
prediction back to the usage-stats prior and clears the revealed-moves
log, since that's a new battle.

Move choices are limited to the intersection of a Pokémon's learnset and
the moves we have cached power/type/category data for (`data/cache/moves/`)
-- see the README note on offline fixtures for why that set is currently
small.

The opponent's predicted moveset is driven by USAGE_STATS_PATH, which
points at a real downloaded Smogon gen9ou moveset file
(`data/usage_stats/gen9ou-1500.txt`), not the hand-built
`gen9ou-sample.txt` fixture -- that fixture only covers Pikachu,
Charizard, and Bulbasaur and is kept around as a documented offline
fallback (see README).
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox

from pokeadvisor import counter_engine, damage_calc, moveset_predictor
from pokeadvisor.pokeapi_client import CACHE_DIR, MOVES_CACHE_DIR, get_move_data, get_pokemon_data

# Real Smogon gen9ou moveset data (downloaded from smogon.com/stats), not
# the hand-built gen9ou-sample.txt fixture. See module docstring.
USAGE_STATS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "usage_stats", "gen9ou-1500.txt")

EFFECTIVENESS_COLORS = {
    "super effective": "#1a7f37",
    "neutral": "#1f2328",
    "not very effective": "#9a6700",
    "no effect": "#cf222e",
    "status": "#57606a",
}

MAX_PLAYER_MOVES = 4


def get_available_pokemon():
    """Names of Pokémon we have cached data for (data/cache/*.json)."""
    names = []
    for filename in os.listdir(CACHE_DIR):
        if filename.endswith(".json") and os.path.isfile(os.path.join(CACHE_DIR, filename)):
            names.append(filename[:-len(".json")])
    return sorted(names)


def get_available_moves_for(pokemon_data):
    """A Pokémon's learnable moves, restricted to ones with cached move data."""
    cached_moves = {f[:-len(".json")] for f in os.listdir(MOVES_CACHE_DIR) if f.endswith(".json")}
    return sorted(set(pokemon_data["moves"]) & cached_moves)


class PokeAdvisorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PokéAdvisor")

        self.pokemon_names = get_available_pokemon()
        self.usage_stats = moveset_predictor.parse_usage_file(USAGE_STATS_PATH)
        self.move_vars = []
        self.predicted_moveset = []
        self.revealed_moves = []

        self._build_input_panel()
        self._build_output_panel()

        if self.pokemon_names:
            self.player_combo.current(0)
            self.opponent_combo.current(0)
            self._on_player_pokemon_change()
            self._on_opponent_pokemon_change()

    def _build_input_panel(self):
        input_frame = ttk.Frame(self.root, padding=10)
        input_frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(input_frame, text="Your Pokémon").grid(row=0, column=0, sticky="w")
        self.player_combo = ttk.Combobox(input_frame, values=self.pokemon_names, state="readonly", width=20)
        self.player_combo.grid(row=1, column=0, sticky="w")
        self.player_combo.bind("<<ComboboxSelected>>", lambda e: self._on_player_pokemon_change())

        ttk.Label(input_frame, text="Your moves").grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.moves_frame = ttk.Frame(input_frame)
        self.moves_frame.grid(row=3, column=0, sticky="w")

        ttk.Label(input_frame, text="Opponent's Pokémon").grid(row=0, column=1, sticky="w", padx=(20, 0))
        self.opponent_combo = ttk.Combobox(input_frame, values=self.pokemon_names, state="readonly", width=20)
        self.opponent_combo.grid(row=1, column=1, sticky="w", padx=(20, 0))
        self.opponent_combo.bind("<<ComboboxSelected>>", lambda e: self._on_opponent_pokemon_change())

        ttk.Label(input_frame, text="Opponent revealed a move").grid(row=2, column=1, sticky="w", padx=(20, 0), pady=(8, 0))
        self.reveal_frame = ttk.Frame(input_frame)
        self.reveal_frame.grid(row=3, column=1, sticky="w", padx=(20, 0))
        self.reveal_combo = ttk.Combobox(self.reveal_frame, state="readonly", width=14)
        self.reveal_combo.grid(row=0, column=0)
        self.reveal_button = ttk.Button(self.reveal_frame, text="Reveal", command=self._on_reveal_move)
        self.reveal_button.grid(row=0, column=1, padx=(4, 0))

        self.analyze_button = ttk.Button(input_frame, text="Analyze", command=self._on_analyze)
        self.analyze_button.grid(row=4, column=0, columnspan=2, pady=(12, 0), sticky="w")

    def _build_output_panel(self):
        output_frame = ttk.Frame(self.root, padding=10)
        output_frame.grid(row=1, column=0, sticky="nsew")

        ttk.Label(output_frame, text="Your moves, ranked", font=("", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.ranked_moves_box = tk.Text(output_frame, width=55, height=6, state="disabled")
        self.ranked_moves_box.grid(row=1, column=0, sticky="w")

        ttk.Label(output_frame, text="Predicted opponent moveset", font=("", 10, "bold")).grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.predicted_box = tk.Text(output_frame, width=55, height=5, state="disabled")
        self.predicted_box.grid(row=3, column=0, sticky="w")

        ttk.Label(output_frame, text="Recommendation", font=("", 10, "bold")).grid(row=4, column=0, sticky="w", pady=(10, 0))
        self.recommendation_label = ttk.Label(output_frame, text="", wraplength=420, justify="left")
        self.recommendation_label.grid(row=5, column=0, sticky="w")

    def _on_player_pokemon_change(self):
        for widget in self.moves_frame.winfo_children():
            widget.destroy()
        self.move_vars = []

        player_name = self.player_combo.get()
        if not player_name:
            return

        player_data = get_pokemon_data(player_name)
        available_moves = get_available_moves_for(player_data)

        for move_name in available_moves:
            var = tk.BooleanVar(value=False)
            checkbox = ttk.Checkbutton(self.moves_frame, text=move_name, variable=var)
            checkbox.pack(anchor="w")
            self.move_vars.append((move_name, var))

    def _on_opponent_pokemon_change(self):
        """Reset the live moveset prediction when the opponent changes.

        Switching opponents starts a fresh battle, so any moves revealed
        about the *previous* opponent no longer apply: the prediction is
        re-derived from the usage-stats prior and the revealed-moves log
        is cleared.
        """
        opponent_name = self.opponent_combo.get()
        self.predicted_moveset = moveset_predictor.predict_moveset(opponent_name, self.usage_stats)
        self.revealed_moves = []

        opponent_data = get_pokemon_data(opponent_name)
        self.reveal_combo["values"] = get_available_moves_for(opponent_data)
        self.reveal_combo.set("")

        self._render_predicted_moveset(self.predicted_moveset)

    def _on_reveal_move(self):
        """Feed an opponent's revealed move back into the live prediction.

        Confirms the move (it's no longer a useful prediction target) and
        redistributes the remaining weights via update_with_observed_move,
        so the next Analyze uses the updated, narrowed-down moveset.
        """
        move_name = self.reveal_combo.get()
        if not move_name:
            return

        self.predicted_moveset = moveset_predictor.update_with_observed_move(self.predicted_moveset, move_name)
        self.revealed_moves.append(move_name)
        self._render_predicted_moveset(self.predicted_moveset)

    def _selected_moves(self):
        return [name for name, var in self.move_vars if var.get()]

    def _on_analyze(self):
        player_name = self.player_combo.get()
        opponent_name = self.opponent_combo.get()
        selected_move_names = self._selected_moves()

        if not player_name or not opponent_name:
            messagebox.showwarning("Missing input", "Pick both your Pokémon and the opponent's Pokémon.")
            return
        if not selected_move_names:
            messagebox.showwarning("Missing input", "Pick at least one of your moves.")
            return
        if len(selected_move_names) > MAX_PLAYER_MOVES:
            messagebox.showwarning("Too many moves", f"Pick at most {MAX_PLAYER_MOVES} moves.")
            return

        player_data = get_pokemon_data(player_name)
        opponent_data = get_pokemon_data(opponent_name)
        player_moves = [get_move_data(name) for name in selected_move_names]

        ranked = damage_calc.rank_moves(player_data, player_moves, opponent_data)
        result = counter_engine.recommend_action(player_data, player_moves, opponent_data, self.predicted_moveset)

        self._render_ranked_moves(ranked)
        self._render_predicted_moveset(self.predicted_moveset)
        self.recommendation_label.config(text=result["explanation"])

    def _render_ranked_moves(self, ranked):
        self.ranked_moves_box.config(state="normal")
        self.ranked_moves_box.delete("1.0", "end")
        for entry in ranked:
            tag = entry["effectiveness"]
            line = f"{entry['move']:<16} {entry['damage']:6.1f} dmg   ({entry['effectiveness']})\n"
            self.ranked_moves_box.insert("end", line, tag)
            self.ranked_moves_box.tag_config(tag, foreground=EFFECTIVENESS_COLORS.get(tag, "#1f2328"))
        self.ranked_moves_box.config(state="disabled")

    def _render_predicted_moveset(self, predicted_moveset):
        self.predicted_box.config(state="normal")
        self.predicted_box.delete("1.0", "end")
        if self.revealed_moves:
            self.predicted_box.insert("end", f"Revealed so far: {', '.join(self.revealed_moves)}\n\n")
        if not predicted_moveset:
            self.predicted_box.insert("end", "No usage data for this opponent.\n")
        for entry in predicted_moveset:
            self.predicted_box.insert("end", f"{entry['move']:<16} {entry['weight'] * 100:5.1f}%\n")
        self.predicted_box.config(state="disabled")


def run():
    root = tk.Tk()
    PokeAdvisorApp(root)
    root.mainloop()
