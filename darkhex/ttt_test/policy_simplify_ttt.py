from darkhex.ttt_test.policy_simplify import PolicySimplifyTTT
from darkhex.algorithms.policy_simplify import PolicySimplify
from darkhex.utils.util import save_file
import pyspiel
import pickle
from darkhex.ttt_test.convert_strategy import convert, convert_dh


def simplify_policy_pttt(initial_board, file_path):
    ps = PolicySimplifyTTT(
        initial_board,
        1,  # player
        file_path,
        epsilon=0.1,  # probability threshold
        eta=0.00,  # smoothing distance
        frac_limit=10,  # max fraction to check the distance
        max_number_of_actions=4)  # max number of actions allowed
    # print(ps.info_states)
    conv_is = {}
    for key, value in ps.info_states.items():
        conv_is[key] = [(k, v) for k, v in value.items()]
    new_strategy = convert(conv_is, 3, 3, ps.p)
    data = {
        "player": ps.p,
        "initial_board": initial_board,
        "strategy": new_strategy,
    }
    # print(ps.info_states)
    print(f"Total states: {len(ps.info_states)}")
    save_file(data, f"darkhex/data/ttt/test_{ps.p}/game_info.pkl")


def simplify_policy_darkhex(initial_board, file_path):
    num_cols, num_rows = 3, 4
    ps = PolicySimplify(
        initial_board=initial_board,
        num_rows=num_rows,
        num_cols=num_cols,
        player=1,
        policy_type="mccfr",
        file_path=file_path,
        epsilon=0.1,  # probability threshold
        eta=0.00,  # smoothing distance
        frac_limit=0,  # max fraction to check the distance
        max_number_of_actions=2)  # max number of actions allowed
    # print(ps.info_states)
    fname = f'p{ps.p}_{ps.max_number_of_actions}_{ps.epsilon}_{ps.eta}_{ps.frac_limit}'
    conv_is = {}
    for key, value in ps.info_states.items():
        conv_is[key] = [(k, v) for k, v in value.items()]
    conv_is = convert_dh(conv_is, num_cols, num_rows, ps.p)
    data = {
        "player": ps.p,
        "initial_board": initial_board,
        "strategy": conv_is,
    }
    # print(ps.info_states)
    print(f"Total states: {len(ps.info_states)}")
    save_file(data, f"darkhex/data/strategy_data/4x3_mccfr/{fname}/game_info.pkl")


if __name__ == "__main__":
    # file_path = "../open_spiel/tmp/phantom_ttt_ir/solver.pkl"
    # simplify_policy_pttt(initial_board=".........", file_path=file_path)
    file_path = "../open_spiel/tmp/Arena/arena_mccfr_4x3_pone_ir_100000000/solver.pkl"
    simplify_policy_darkhex(initial_board="............", file_path=file_path)
