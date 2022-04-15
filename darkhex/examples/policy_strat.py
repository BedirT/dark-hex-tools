from darkhex.algorithms.policy_simplify import PolicySimplify
from darkhex.utils.util import save_file
import pyspiel
import pickle


def simplify_policy(num_rows, num_cols, player, initial_board, file_path, policy_type='mccfr', include_isomorphic=True):
    ps = PolicySimplify(initial_board, num_rows, num_cols, player, policy_type, file_path, include_isomorphic)
    # print(ps.info_states)
    conv_is = {}
    for key, value in ps.info_states.items():
        conv_is[key] = [(k, v) for k, v in value.items()]
    data = {
        "num_cols": num_cols,
        "num_rows": num_rows,
        "player": player,
        "isomorphic": include_isomorphic,
        "initial_board": initial_board,
        "strategy": conv_is,
    }
    # print(ps.info_states)
    print(f"Total states: {len(ps.info_states)}")
    save_file(data, f"darkhex/data/strategy_data/simplified_{num_rows}x{num_cols}_{policy_type}_p{player}_new/game_info.pkl")


if __name__ == "__main__":
    file_path = "../open_spiel/tmp/Arena/arena_mccfr_4x3_pone_ir/solver.pkl"
    simplify_policy(4, 3, 0, "............", file_path)