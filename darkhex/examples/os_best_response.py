from open_spiel.python import policy
from open_spiel.python.algorithms import best_response
from open_spiel.python.algorithms import exploitability
import pyspiel
import pickle
import time
import argparse


def get_exploitability(game, strategy, folder_path):
    # Convert strategy to pyspiel policy
    tabular_policy = pyspiel.PartialTabularPolicy(strategy)
    root_state = game.new_initial_state()

    # Get best response policy
    start = time.time()
    # results = exploitability.best_response(game, tabular_policy, player_id=1)
    results = pyspiel.TabularBestResponseMDP(game, tabular_policy)
    br_info = results.compute_best_response(1)
    print("Best Response:", br_info.br_values)
    # print("BR Policies:", br_info.br_policies)
    policy_dict = {}
    print(br_info.br_policies[1].policy_table())
    for info_state, policy in br_info.br_policies[1].policy_table().items():
        policy_dict[info_state] = policy
    print("On_policy values:", br_info.on_policy_values)
    print("NashConv:", br_info.nash_conv)
    print("Exploitability:", br_info.exploitability)

    # Save results
    results = {
        "br_values": br_info.br_values,
        "br_policies": policy_dict,
        "on_policy_values": br_info.on_policy_values,
        "nash_conv": br_info.nash_conv,
        "exploitability": br_info.exploitability,
    }
    with open(folder_path + "br_info.pkl", "wb") as f:
        pickle.dump(results, f)

    print(f"Time: {time.time() - start}")


def test_methods(policy_folder_path):
    with open(policy_folder_path + "game_info.pkl", "rb") as f:
        game_info = pickle.load(f)
    # print(game_info)
    game = pyspiel.load_game(
        "dark_hex_ir", {
            "num_rows": game_info['num_rows'],
            "num_cols": game_info['num_cols'],
            "use_early_terminal": True,
        })
    strategy = game_info['strategy']

    # get_best_response(game, strategy)
    # get_best_response_mdp(game, strategy)
    get_exploitability(game, strategy, policy_folder_path)


if __name__ == "__main__":
    # Take folder path as argument from command line
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "folder_path",
        type=str,
        help="Path to folder containing game_info.pkl and strategy.pkl")
    args = parser.parse_args()
    print(args.folder_path)
    test_methods(args.folder_path)
