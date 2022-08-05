'''List Best Responses of the strategies in the folder'''
import os
from darkhex.utils.util import load_file
import pyspiel

from darkhex.algorithms.best_response_log import BestResponse


def get_br(folder_path):
    file_path = folder_path + 'game_info.pkl'
    data = load_file(file_path)
    game = pyspiel.load_game(
        f'dark_hex_ir(num_cols={data["num_cols"]},num_rows={data["num_rows"]},'
        + 'use_early_terminal=True)')
    # create best response object
    br = BestResponse(
        game,
        data["player"],
        data["initial_board"],
        data["num_cols"],
        data["strategy"],
        folder_path + "br_strategy.pkl",
    )
    return br.best_response(calculate=False)


def list_brs(folder_path, prior):
    for folder_pth in os.listdir(folder_path):
        if not folder_pth.startswith(prior):
            continue
        full_path = folder_path + folder_pth + '/'
        try:
            br = get_br(full_path)
            # path and br with 20 spaces in between
            print(f"{full_path:.<80}{br}")
            # clear the memory
            del br
        except:
            print(f"{full_path} failed")


if __name__ == "__main__":
    folder_path = "darkhex/data/strategy_data/4x3_mccfr/"
    list_brs(folder_path, 'p0')
    print('\n')
    list_brs(folder_path, 'p1')
