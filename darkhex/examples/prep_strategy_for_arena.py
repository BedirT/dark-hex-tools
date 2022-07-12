import pyspiel
from darkhex.utils.util import load_file, get_open_spiel_state, save_file


def test():
    p = 0
    data = load_file(f"darkhex/data/ttt/test_{p}/game_info.pkl")
    save_file(data["strategy"], f"data/arena_strats/test_{p}.pkl")


test()