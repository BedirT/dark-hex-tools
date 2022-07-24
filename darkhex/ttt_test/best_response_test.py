import pyspiel
from darkhex.ttt_test.best_response_log import BestResponse
from darkhex.utils.util import load_file, get_open_spiel_state


def br_ttt_test_value(folder_path):
    data = load_file(folder_path + "game_info.pkl")
    initial_state = get_open_spiel_state(pyspiel.load_game(f'phantom_ttt_ir'),
                                         data["initial_board"])

    # create best response object
    br = BestResponseValue(initial_state=initial_state,
                           eval_player=data["player"],
                           eval_strategy=data["strategy"],
                           br_strategy_save_path=folder_path + "br_strategy.pkl")

    # calculate best response value
    br_val = br.best_response()
    print(f"Best Response Value: {br_val}")


if __name__ == "__main__":
    p = 0
    br_ttt_test_value(f"darkhex/data/ttt/test_{p}/")
