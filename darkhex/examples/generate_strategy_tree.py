"""
Sampe file to generate a strategy tree using tree_generator.py
"""
import pyspiel
from darkhex.algorithms.tree_generator import TreeGenerator
from darkhex.utils.util import load_file


def main():
    file_name = "simplified_4x3_mccfr_p1_test"
    game_info = load_file(
        f"darkhex/data/strategy_data/{file_name}/game_info.pkl")

    # Load the game
    game = pyspiel.load_game(
        f'dark_hex_ir(num_rows={game_info["num_rows"]},num_cols={game_info["num_cols"]},use_early_terminal=True)'
    )

    # Create a tree generator
    TreeGenerator(game, file_name)


if __name__ == "__main__":
    main()
