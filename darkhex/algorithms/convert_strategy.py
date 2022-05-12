"""Converts strategies with old info_state representation
ie. 'yyq.yqyqx...' to new representation ie. for player_id=0
'P0 xxo.xoxox...'
"""
from darkhex.utils.util import convert_os_str
import pickle


def convert(strategy, num_cols, num_rows, pid):
    new_strategy = {}
    for info_state, actions in strategy.items():
        new_info_state = convert_os_str(info_state, num_cols, player=pid)
        assert (len(new_info_state) == num_cols * num_rows + 3)
        new_strategy[new_info_state] = actions
    return new_strategy


if __name__ == "__main__":
    file_path = "darkhex/data/strategy_data/simplified_4x3_mccfr_p1/game_info.pkl"
    with open(file_path, "rb") as f:
        game_info = pickle.load(f)
    new_strategy = convert(game_info['strategy'], game_info['num_cols'],
                           game_info['num_rows'], game_info['player'])
    # save new strategy
    game_info['strategy'] = new_strategy
    print(file_path, type(file_path))
    with open(file_path, "wb") as f:
        pickle.dump(game_info, f)
    print("Done")
