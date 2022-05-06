import json
from os import stat
import time

import pyspiel
from darkhex.algorithms.best_response import BestResponse
from darkhex.utils.util import load_file, get_open_spiel_state, save_file, convert_os_strategy


def main(folder_path):
    data = load_file(folder_path + "game_info.pkl")
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
        folder_path + "opponent_strategy.pkl",
    )

    # calculate best response value
    br_val = br.best_response()
    print(f"Best Response Value: {br_val}")

def test():
    data = load_file("darkhex/data/strategy_data/simplified_4x3_mccfr_p1/game_info.pkl")
    game = pyspiel.load_game(
        f'dark_hex_ir(num_cols={data["num_cols"]},num_rows={data["num_rows"]})'
    )
    strategy = data["strategy"]
    initial_state = data["initial_board"]
    game_state = get_open_spiel_state(game, initial_state)
    # strategy = convert_os_strategy(strategy, data["num_cols"], 1)
    save_file(strategy, "data/arena_strats/simplified_4x3_mccfr_p1.pkl")


if __name__ == "__main__":
    # main("darkhex/data/strategy_data/simplified_4x3_mccfr_p1/")
    test()
