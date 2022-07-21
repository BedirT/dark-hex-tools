import pyspiel
from darkhex.ttt_test.best_response_log import BestResponse
from darkhex.ttt_test.tree_generator import TreeGenerator
# from darkhex.algorithms.tree_run import TreeRun
from darkhex.utils.util import load_file
import time


def main():
    folder_name = 'test_1'
    file_path = f"darkhex/data/ttt/{folder_name}/"
    data = load_file(file_path + "game_info.pkl")
    game = pyspiel.load_game('phantom_ttt_ir')
    # create best response object
    br = BestResponse(
        game,
        data["player"],
        data["initial_board"],
        3,
        data["strategy"],
        file_path + "br_strategy.pkl",
    )

    start = time.time()
    # calculate best response value
    br_value = br.best_response()
    print(f"Best response value: {br_value}")
    print(f"Time taken: {time.time() - start}")

    # create tree generator object
    TreeGenerator(game, f'ttt/{folder_name}')

    # create tree run object
    # tree_run = TreeRun(file_name)
    # tree_run.tree_run()


if __name__ == "__main__":
    main()
