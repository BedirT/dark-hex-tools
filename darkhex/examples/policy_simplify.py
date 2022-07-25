from darkhex.algorithms.policy_simplify import PolicySimplify
from darkhex.utils.util import save_file
import pyspiel
import pickle


def simplify_policy(num_rows,
                    num_cols,
                    player,
                    initial_board,
                    file_path,
                    epsilon=0.2,
                    max_number_of_actions=2,
                    eta=0.0,
                    frac_limit=0,
                    policy_type='mccfr',
                    include_isomorphic=True):
    ps = PolicySimplify(initial_board,
                        num_rows,
                        num_cols,
                        player,
                        policy_type,
                        file_path,
                        epsilon=1 / 15,
                        eta=0.03,
                        frac_limit=15,
                        max_number_of_actions=2)
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
    fname = f'p{player}_{max_number_of_actions}_{epsilon}_{eta}_{frac_limit}'
    save_file(data,
              f"darkhex/data/strategy_data/4x3_mccfr/{fname}/game_info.pkl")


if __name__ == "__main__":
    file_path = "../open_spiel/tmp/Arena/arena_mccfr_4x3_pone_ir/solver.pkl"
    simplify_policy(num_rows=4,
                    num_cols=3,
                    player=0,
                    initial_board="............",
                    file_path=file_path)
