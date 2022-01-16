"""
Sampe file to generate a strategy tree using tree_generator.py
"""
import pyspiel
from algorithms.tree_generator import TreeGenerator
from utils.util import load_file


def main():
    file_name = "4x3_boundsOver7"
    game_info = load_file(f"data/strategy_data/{file_name}/game_info.pkl")

    # Load the game
    game = pyspiel.load_game(
        f'dark_hex_ir(num_rows={game_info["num_rows"]},num_cols={game_info["num_cols"]})'
    )

    # Create a tree generator
    TreeGenerator(game, file_name)


if __name__ == "__main__":
    main()
