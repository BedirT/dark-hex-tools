import pyspiel
from darkhex.ttt_test.best_response_log import BestResponse
from darkhex.ttt_test.tree_generator import TreeGenerator
from darkhex.algorithms.tree_run import TreeRun
from darkhex.utils.util import load_file, get_open_spiel_state


def main():
    folder_path = f"darkhex/data/ttt/test_1/"
    data = load_file(folder_path + "game_info.pkl")
    game = pyspiel.load_game("phantom_ttt_ir")
    initial_state = get_open_spiel_state(game, data["initial_board"])
    # create best response object
    br = BestResponse(initial_state=initial_state,
                      eval_player=data["player"],
                      eval_strategy=data["strategy"],
                      br_strategy_save_path=folder_path + "br_strategy.pkl")

    # calculate best response value
    br_value = br.best_response()
    print(f"Best response value: {br_value}")

    # create tree generator object
    TreeGenerator(game, folder_path)

    # create tree run object
    tree_run = TreeRun(folder_path)
    tree_run.tree_run()


if __name__ == "__main__":
    main()
