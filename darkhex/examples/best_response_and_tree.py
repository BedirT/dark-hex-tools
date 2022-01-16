import logging

import coloredlogs
import pyspiel
from algorithms.best_response import BestResponse
from algorithms.tree_generator import TreeGenerator
from algorithms.tree_run import TreeRun
from utils.util import load_file


def main():
    file_name = "4x3_boundsOver7"
    # file_name = '4x3_subgame'
    file_path = f"data/strategy_data/{file_name}/"
    data = load_file(file_path + "game_info.pkl")
    game = pyspiel.load_game(
        f'dark_hex_ir(num_cols={data["num_cols"]},num_rows={data["num_rows"]})'
    )

    strategy = data["strategy"]
    initial_state = data["initial_board"]

    # create best response object
    player = 0 if data["player"] == "x" else 1
    br = BestResponse(
        game,
        player,
        initial_state,
        data["num_cols"],
        strategy,
        file_path + "opp_strategy.pkl",
    )

    # calculate best response value
    br_value = br.best_response()
    log.info(f"Best response value: {br_value}")

    # create tree generator object
    TreeGenerator(game, file_name)

    # create tree run object
    tree_run = TreeRun(file_name)
    tree_run.tree_run()


if __name__ == "__main__":
    main()
