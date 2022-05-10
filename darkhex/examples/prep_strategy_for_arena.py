import pyspiel
from darkhex.utils.util import load_file, get_open_spiel_state, save_file


def test():
    data = load_file(
        "darkhex/data/strategy_data/simplified_4x3_mccfr_p1/game_info.pkl")
    game = pyspiel.load_game(
        f'dark_hex_ir(num_cols={data["num_cols"]},num_rows={data["num_rows"]})')
    save_file(data["strategy"], "data/arena_strats/simplified_4x3_mccfr_p1.pkl")
