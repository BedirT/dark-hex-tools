from open_spiel.python import policy
from open_spiel.python.algorithms import best_response
from open_spiel.python.algorithms import exploitability
import pyspiel
import pickle
import time


def get_exploitability(game, strategy, folder_path):
    # Convert strategy to pyspiel policy
    tabular_policy = pyspiel.PartialTabularPolicy(strategy)
    root_state = game.new_initial_state()

    # Get best response policy
    start = time.time()
    results = exploitability.best_response(game, tabular_policy, player_id=1)
    
    # Save results
    with open(folder_path + "exploitability.pkl", "wb") as f:
        pickle.dump(results, f)

    print(f"Time: {time.time() - start}")


def test_methods(policy_folder_path):
    with open(policy_folder_path + "game_info.pkl", "rb") as f:
        game_info = pickle.load(f)
    print(game_info)
    game = pyspiel.load_game("dark_hex_ir", {
        "num_rows": game_info['num_rows'],
        "num_cols": game_info['num_cols'],
        "use_early_terminal": True,
    })
    strategy = game_info['strategy']

    # get_best_response(game, strategy)
    # get_best_response_mdp(game, strategy)
    get_exploitability(game, strategy, policy_folder_path)

def main():
    test_methods("darkhex/data/strategy_data/4x3_0_def/")

if __name__ == "__main__":
    main()