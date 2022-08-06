import pyspiel
from darkhex.utils.util import load_file, get_open_spiel_state, save_file


def test():
    folder_path = "darkhex/data/strategy_data/4x3_mccfr/p1_4_0.1_0.05_20/"
    save_name = "simcap+_large"
    player = 1
    data = load_file(f"{folder_path}/game_info.pkl")
    save_file(data["strategy"], f"../open_spiel/tmp/Arena/{save_name}/p{player}_strategy.pkl")


test()