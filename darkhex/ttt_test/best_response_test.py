import pyspiel
from darkhex.ttt_test.best_response_log import BestResponse
from darkhex.utils.util import load_file

def br_ttt_test(folder_path):
    data = load_file(folder_path + "game_info.pkl")
    game = pyspiel.load_game(f'phantom_ttt_ir')

    # create best response object
    br = BestResponse(
        game,
        data["player"],
        data["initial_board"],
        3,
        data["strategy"],
        folder_path + "br_strategy.pkl",
    )

    # calculate best response value
    br_val = br.best_response()
    print(f"Best Response Value: {br_val}")


if __name__ == "__main__":
    # main("darkhex/data/strategy_data/simplified_4x3_mccfr_p1/")
    br_ttt_test("darkhex/data/ttt/test_1/")
