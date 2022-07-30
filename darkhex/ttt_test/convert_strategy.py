"""Converts strategies with old info_state representation
ie. 'yyq.yqyqx...' to new representation ie. for player_id=0
'P0 xxo.xoxox...'
"""
from darkhex.ttt_test.policy_simplify import get_os_str
from darkhex.utils.util import convert_os_str
import pickle


def convert(strategy, num_cols, num_rows, pid):
    new_strategy = {}
    for info_state, action_probs in strategy.items():
        new_info_state = get_os_str(info_state, num_cols, player=pid)
        new_strategy[new_info_state] = action_probs
    return new_strategy


def convert_dh(strategy, num_cols, num_rows, pid):
    # same as convert but converts the stones to x-o
    new_strategy = {}
    for info_state, action_probs in strategy.items():
        new_info_state = convert_os_str(info_state, num_cols, player=pid)
        new_strategy[new_info_state] = action_probs
    return new_strategy


if __name__ == "__main__":
    file_path = "darkhex/data/ttt/test_1/game_info.pkl"
    with open(file_path, "rb") as f:
        game_info = pickle.load(f)
    new_strategy = convert(game_info['strategy'], 3, 3, game_info['player'])
    # save new strategy
    game_info['strategy'] = new_strategy
    print(file_path, type(file_path))
    with open(file_path, "wb") as f:
        pickle.dump(game_info, f)
    print("Done")
