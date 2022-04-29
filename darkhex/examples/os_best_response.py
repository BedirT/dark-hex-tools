from open_spiel.python import policy
from open_spiel.python.algorithms import best_response
from open_spiel.python.algorithms import exploitability
import pyspiel
import pickle


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


def get_exploitability(policy_folder_path):
    with open(policy_folder_path + "game_info.pkl", "rb") as f:
        game_info = pickle.load(f)
    print(game_info)
    game = pyspiel.load_game("dark_hex_ir", {
        "num_rows": game_info['num_rows'],
        "num_cols": game_info['num_cols'],
        "use_early_terminal": True,
    })
    strategy = game_info['strategy']

    # Convert strategy to pyspiel polic
    pi = PolicyWithDefault(strategy)
    tabular_policy = policy.tabular_policy_from_callable(game, 
        lambda state: pi.policy_with_default(state),
        game_info['player'])
    tabular_policy = policy.python_policy_to_pyspiel_policy(tabular_policy)
    print('Done')

    # Get best response policy
    br_computer = pyspiel.TabularBestResponseMDP(game, tabular_policy)
    print('Set?')
    br_info = br_computer.exploitability()
    # for attr in dir(br_info):
    #     print("obj.%s = %r" % (attr, getattr(br_info, attr)))

    # save results to file
    results = {
        'br_values': br_info.br_values,
        # 'br_policy': br_info.br_policies,
        'exploitability': br_info.exploitability,
        'nash_conv': br_info.nash_conv,
        'on_policy_values': br_info.on_policy_values,
    }
    print(results)

    with open(policy_folder_path + "br_info.pkl", "wb") as f:
        pickle.dump(results, f)

def main():
    get_exploitability("darkhex/data/strategy_data/3x3_0_def/")

if __name__ == "__main__":
    main()