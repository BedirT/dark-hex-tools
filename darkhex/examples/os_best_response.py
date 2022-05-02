from open_spiel.python import policy
from open_spiel.python.algorithms import best_response
from open_spiel.python.algorithms import exploitability
import pyspiel
import pickle
import time


class StrategyPolicy(policy.Policy):

  def __init__(self, game, strategy):
    self.strategy = strategy
    all_players = list(range(game.num_players()))
    super().__init__(game, all_players)

  def action_probabilities(self, state, player_id=None):
    legal_actions = (
        state.legal_actions()
        if player_id is None else state.legal_actions(player_id))
    if not legal_actions:
      return {0: 1.0}
    probability = 1 / len(legal_actions)
    if state.information_state_string() in self.strategy:
        return {action: prob for action, prob in self.strategy[state.information_state_string()]}
    else:
        return {action: probability for action in legal_actions}


class PolicyWithDefault:
    def __init__(self, strategy):
        self.strategy = strategy

    def policy_with_default(self, state):
        if state.information_state_string() in self.strategy:
            return self.strategy[state.information_state_string()]
        else:
            legal_actions = state.legal_actions()
            return [(action, 1.0 / len(legal_actions)) for action in legal_actions]


def get_best_response(game, strategy):
    tabular_policy = pyspiel.PartialTabularPolicy(strategy)
    root_state = game.new_initial_state()

    # Get best response policy
    start = time.time()
    br_computer = best_response.BestResponsePolicy(game, 1, tabular_policy)
    print(f"Best Response: {br_computer.value(root_state)}")
    print(f"Time: {time.time() - start}")


def get_best_response_mdp(game, strategy):
    tabular_policy = pyspiel.PartialTabularPolicy(strategy)
    root_state = game.new_initial_state()

    # Get best response policy
    start = time.time()
    br_computer = pyspiel.TabularBestResponseMDP(game, 1, tabular_policy)
    print(f"Best Response: {br_computer.value(root_state)}")
    print(f"Time: {time.time() - start}")


def get_exploitability(game, strategy):
    # Convert strategy to pyspiel policy
    tabular_policy = pyspiel.PartialTabularPolicy(strategy)
    root_state = game.new_initial_state()

    # Get best response policy
    start = time.time()
    results = exploitability.best_response(game, tabular_policy, player_id=1)
    print(results)
    # for attr in dir(br_info):
    #     print("obj.%s = %r" % (attr, getattr(br_info, attr)))

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
    get_exploitability(game, strategy)

def main():
    test_methods("darkhex/data/strategy_data/4x3_0_def/")

if __name__ == "__main__":
    main()