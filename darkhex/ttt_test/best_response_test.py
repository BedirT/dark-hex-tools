import pyspiel
from darkhex.ttt_test.best_response_log import BestResponse
from darkhex.utils.util import load_file, get_open_spiel_state


def irbr_test(game, folder_path, data):
    initial_state = get_open_spiel_state(game, data["initial_board"])

    # create best response object
    br = BestResponse(initial_state=initial_state,
                      eval_player=data["player"],
                      eval_strategy=data["strategy"],
                      br_strategy_save_path=folder_path + "br_strategy.pkl")

    # calculate best response value
    br_val = br.best_response()
    print(f"Best Response Value: {1 - br_val}")

if __name__ == "__main__":
    folder_path = "darkhex/data/strategy_data/4x3_0_def/"
    data = load_file(folder_path + "game_info.pkl")
    game_ttt = pyspiel.load_game(f'phantom_ttt_ir')
    game_dh = pyspiel.load_game(
        f'dark_hex_ir(num_cols={data["num_cols"]},num_rows={data["num_rows"]},use_early_terminal=True)'
    )
    
    p = 1
    # br_ttt_test(f"darkhex/data/ttt/test_{p}/")
    # br_dh_test("darkhex/data/strategy_data/4x3_mccfr/p0_2_0.1_0.05_50/")
    irbr_test(game_dh, folder_path, data)
