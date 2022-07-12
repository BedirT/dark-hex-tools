from darkhex.ttt_test.policy_simplify import PolicySimplifyTTT
from darkhex.utils.util import save_file
import pyspiel
import pickle
from darkhex.ttt_test.convert_strategy import convert

def simplify_policy(player,
                    initial_board,
                    file_path):
    ps = PolicySimplifyTTT(pyspiel.load_game("phantom_ttt_ir"),
                           initial_board,
                            player,
                            file_path,
                            epsilon=1 / 10,
                            eta=0.03,
                            frac_limit=10,
                            max_number_of_actions=2)
    # print(ps.info_states)
    conv_is = {}
    for key, value in ps.info_states.items():
        conv_is[key] = [(k, v) for k, v in value.items()]
    new_strategy = convert(conv_is, 3, 3, player)
    data = {
        "player": player,
        "initial_board": initial_board,
        "strategy": new_strategy,
    }
    # print(ps.info_states)
    print(f"Total states: {len(ps.info_states)}")
    save_file(
        data,
        f"darkhex/data/ttt/test_{player}/game_info.pkl"
    )


if __name__ == "__main__":
    file_path = "../open_spiel/tmp/phantom_ttt_ir/solver.pkl"
    simplify_policy(player=0,
                    initial_board=".........",
                    file_path=file_path)
