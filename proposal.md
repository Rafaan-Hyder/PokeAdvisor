CPSC 481 — Project Proposal
PokéAdvisor: An AI Battle Assistant for Pokémon Showdown
Rafaan Hyder
1. Project Title
PokéAdvisor: An AI Battle Assistant for Pokémon Showdown
2. Problem Description
Competitive Pokémon battles require players to make fast, high-stakes decisions involving type matchups, damage calculations, move probabilities, and opponent prediction. Even experienced players can misread a situation under pressure, leading to suboptimal plays.
PokéAdvisor is a standalone Python desktop tool that acts as a real-time AI advisor during Pokémon Showdown battles. Given the player's active Pokémon and the opponent's active Pokémon, the tool calculates optimal moves based on type effectiveness and damage output, predicts the opponent's most likely moveset using publicly available Smogon usage statistics, and recommends the best counter-play response. The goal is to bridge the gap between raw game knowledge and in-battle decision-making speed.
3. Programming Language
The project will be implemented entirely in Python 3, using the following libraries:
Tkinter — built-in Python GUI library for the desktop interface
Requests — for querying the PokéAPI REST API
JSON / csv — for parsing Smogon usage statistics
4. Datasets
Two primary data sources will be used:
PokéAPI (pokeapi.co) — A free, open REST API providing Pokémon base stats, types, moves, damage classes, and type effectiveness multipliers. No authentication required.
Smogon Usage Statistics (smogon.com/stats) — Monthly downloadable plain-text files listing the most commonly used movesets, items, and abilities for each Pokémon in competitive play. These will be parsed locally to power the moveset prediction engine.
5. Existing Code and Extensions
No existing codebase will be directly reused. The project is built from scratch in Python. However, the following pre-existing resources will be leveraged:
The PokéAPI will supply all game data (stats, types, moves), eliminating the need to manually compile a Pokémon database.
Smogon's publicly available usage stat files will serve as the foundation for the moveset prediction engine.
The original contributions of this project include:
Implementation of the official Pokémon damage formula, including STAB bonuses, type effectiveness multipliers, and base power calculations.
A probabilistic moveset predictor that ranks the opponent's likely moves using Smogon frequency data.
A minimax-inspired counter-recommendation engine that evaluates the best player response given the predicted opponent moveset.
A Tkinter-based GUI displaying move recommendations, damage estimates, and opponent predictions in a clear, color-coded interface.
6. Algorithm and Approach
The system operates in three layers:
Layer 1 — Damage Analysis
For each of the player's available moves, the tool computes an estimated damage output against the opponent using the core Pokémon damage formula: Damage = ((2 × Level / 5 + 2) × Power × Attack / Defense / 50 + 2) × Modifiers. Modifiers include STAB (1.5× if the move matches the user's type) and type effectiveness multipliers (0×, 0.25×, 0.5×, 1×, 2×, or 4×) sourced from PokéAPI. Moves are ranked and color-coded: green for super effective, yellow for neutral, and red for ineffective.
Layer 2 — Moveset Prediction
Using Smogon monthly usage data, the tool retrieves the top four most commonly run moves for the opponent's Pokémon in the current competitive format (e.g., OU). Each move is assigned a usage probability weight. As the opponent reveals moves during the battle, the tool updates its probability distribution using Bayesian updating — previously seen moves are confirmed and the remaining probability mass is redistributed among unseen moves.
Layer 3 — Counter Recommendation
Given the predicted opponent moveset, the tool evaluates possible player actions (attack with move A, attack with move B, switch Pokémon) using a simplified minimax decision tree. It considers the estimated damage the opponent's highest-probability move would deal to the player's current Pokémon, the estimated damage the player's best move would deal in return, and the net advantage of each action. The recommended action is displayed with a plain-language explanation.
7. Performance Evaluation
The tool's effectiveness will be evaluated across two dimensions:
Prediction accuracy: The moveset predictor will be tested against a set of recorded Pokémon Showdown replays. For each battle, the tool's predicted top-4 moveset will be compared against the moves the opponent actually used, and a hit rate (correctly predicted moves / total moves revealed) will be calculated.
Recommendation quality: In a set of test battle scenarios, the tool's recommended move will be compared against the objectively optimal move (computed exhaustively). Agreement rate will be reported as a measure of recommendation correctness.
8. Roles and Responsibilities
This is a solo project. Rafaan Hyder is responsible for all aspects of the project, including:
Data acquisition and parsing (PokéAPI integration, Smogon stat file processing)
Implementation of the damage formula and type effectiveness engine
Design and implementation of the probabilistic moveset predictor
Development of the counter-recommendation decision engine
GUI design and implementation using Tkinter
Performance evaluation and written report
Final presentation preparation
