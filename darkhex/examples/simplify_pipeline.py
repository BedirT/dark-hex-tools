'''
Simplify the given mccfr policy + convert the strategy to a dictionary
+ run best response on the policy
'''
from darkhex.examples.policy_simplify import simplify_policy
from darkhex.algorithms.convert_strategy import convert
from darkhex.utils.util import load_file, save_file
from darkhex.algorithms.best_response_log import BestResponse
from darkhex.algorithms.tree_generator import TreeGenerator
from darkhex.algorithms.tree_run import TreeRun
import pickle
import pyspiel
import time


def sim_pipeline(file_path,
                 num_rows=4,
                 num_cols=3,
                 player=0,
                 initial_board="............",
                 epsilon=0.2,
                 max_number_of_actions=2,
                 eta=0.00,
                 frac_limit=0,
                 policy_type='mccfr',
                 include_isomorphic=True):
    print(f"Simplifying {file_path}")
    simplify_policy(num_rows, num_cols, player, initial_board, file_path,
                    epsilon, max_number_of_actions, eta, frac_limit,
                    policy_type, include_isomorphic)

    # convert the strategy to a dictionary
    print(f"Converting {file_path}")
    fname = f'p{player}_{max_number_of_actions}_{epsilon}_{eta}_{frac_limit}'
    folder_path = f"darkhex/data/strategy_data/4x3_mccfr/{fname}/"
    file_path = folder_path + 'game_info.pkl'
    with open(file_path, "rb") as f:
        game_info = pickle.load(f)
    new_strategy = convert(game_info['strategy'], game_info['num_cols'],
                           game_info['num_rows'], game_info['player'])
    # save new strategy
    game_info['strategy'] = new_strategy
    print(file_path, type(file_path))
    with open(file_path, "wb") as f:
        pickle.dump(game_info, f)
    print("Done simplifying and converting")

    # run best response on the policy
    print(f"Running best response on {file_path}")
    data = load_file(file_path)
    game = pyspiel.load_game(
        f'dark_hex_ir(num_cols={data["num_cols"]},num_rows={data["num_rows"]},'
        + 'use_early_terminal=True)')
    # create best response object
    br = BestResponse(
        game,
        data["player"],
        data["initial_board"],
        data["num_cols"],
        data["strategy"],
        folder_path + "br_strategy.pkl",
    )

    start = time.time()
    # calculate best response value
    br_value = br.best_response()
    print(f"Best response value: {br_value}")
    print(f"Time taken: {time.time() - start}")

    # create tree generator object
    TreeGenerator(game, folder_path)

    # create tree run object
    tree_run = TreeRun(folder_path)
    tree_run.tree_run()


if __name__ == "__main__":
    file_path = "../open_spiel/tmp/Arena/arena_mccfr_4x3_pone_ir/solver.pkl"
    sim_pipeline(file_path)
