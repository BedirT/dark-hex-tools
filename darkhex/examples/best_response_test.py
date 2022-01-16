import json
from os import stat

import pyspiel
from algorithms.best_response import BestResponse
from utils.util import load_file


def main():
    data = load_file("data/strategy_data/4x3_boundsOver7/game_info.pkl")
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
        "data/strategy_data/4x3_boundsOver7/opponent_strategy.pkl",
    )

    # calculate best response value
    br.best_response()


if __name__ == "__main__":
    main()
