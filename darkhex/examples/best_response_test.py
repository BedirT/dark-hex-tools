import json
from os import stat
import time

import pyspiel
from darkhex.algorithms.best_response import BestResponse
from darkhex.utils.util import load_file, get_open_spiel_state, save_file, convert_os_strategy


def main(folder_path):
    data = load_file(folder_path + "game_info.pkl")
    game = pyspiel.load_game(
        f'dark_hex_ir(num_cols={data["num_cols"]},num_rows={data["num_rows"]},use_early_terminal=True)'
    )

    # create best response object
    br = BestResponse(
        game,
        data["player"],
        data["initial_board"],
        data["num_cols"],
        data["strategy"],
        folder_path + "br_strategy.pkl",
    )

    # calculate best response value
    br_val = br.best_response()
    print(f"Best Response Value: {br_val}")


if __name__ == "__main__":
    main("darkhex/data/strategy_data/simplified_4x3_mccfr_p1_test_2/")
