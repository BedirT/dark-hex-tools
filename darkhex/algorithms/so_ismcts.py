# INCOMPLETE

import typing
import pyspiel
import numpy as np

class Node:
    def __init__(self, 
                 state: pyspiel.State, 
                 parent: Node=None,
                 k: float=1.4,):
        self.k = k # exploration parameter
        self.state = state
        self.parent = parent
        self.num_visits = 0
        self.num_available = 0
        self.total_reward = 0
        self.children = {}

    def select_child(self, pi_det: typing.Dict[str, typing.Tuple[int, float]]) \
                  -> typing.Tuple[int, Node]:
        """Select child from children using UCB according to
        the given determinization"""
        actions = self.children.keys()
        # get c(v, d)
        info_state = self.state.information_state_string()
        actions = [action for action in actions if action in pi_det[info_state].keys()]
        return max(actions, key=lambda action: self.children[action].value()), \
               self.children[action]

    def value(self) -> float:
        """Returns the value of the node (UCB)"""
        arg1 = self.total_reward / self.num_visits
        arg2 = self.k * math.sqrt(math.log(self.num_available) / self.num_visits)
        return arg1 + arg2

    def expanded(self, pi_det: typing.Dict[str, typing.Tuple[int, float]]) -> bool:
        """If the node is fully expanded for the given determinization."""
        node_actions = self.children.keys()
        # get c(v, d)
        info_state = self.state.information_state_string()
        for action in pi_det[info_state]:
            if action not in node_actions:
                return False
        return True
        
    def expand(self, pi_det: typing.Dict[str, typing.Tuple[int, float]])\
            -> typing.Tuple[int, Node]:
        """Expand the node, with the given action."""
        info_state = self.state.information_state_string()
        actions_det = [act_prob[0] for act_prob in pi_det[info_state]]
        actions_det = [action for action in actions_det 
                       if action not in self.children.keys()]
        rand_action = np.random.choice(actions_det)
        self.children[rand_action] = Node(self.state.child(rand_action), self, self.k)
        return self.children[rand_action]

    def update(self, 
               reward: int, 
               pi_det: typing.Dict[str, typing.Tuple[int, float]]) -> None:
        """Update the node values"""
        self.num_visits += 1
        self.total_reward += reward
        if self.parent is not None:
            info_state = self.state.information_state_string()
            actions_det = [act_prob[0] for act_prob in pi_det[info_state]]
            for action, child in self.parent.items():
                if action in actions_det:
                    child.num_available += 1
        

class SoISMCTS:
    """
    Implementation of Single Observer Information Set Monte Carlo Tree Search
    (SO-ISMCTS) from the paper: 'Information Set Monte Carlo Tree Search'
    by Peter I. Cowling, Edward J. Powley, Daniel Whitehouse. Using pyspiel
    library for the game specific logic.
    """
    def __init__(self, game, args):
        self.game = game
        self.args = args

        self.all_states = pyspiel_get_all_states.get_all_states(
            self.game, include_terminals=False, include_chance_states=False).values()

    def run(self, state):
        next_state = state.clone() # might be unnecessary
        root = Node(next_state, None, self.args.k)

        for _ in range(self.args.num_simulations):
            node = root
            pi_det = self.determine(branching_factor=self.args.branching_factor)

            # Select 
            while not next_state.is_terminal() and node.expanded(pi_det):
                # if node is not terminal and fully expanded for determinization
                action, node = node.select_child(pi_det)
                next_state = node.state.clone()

            # Expand
            if not next_state.is_terminal():
                node = node.expand(pi_det)
                next_state = node.state.clone()

            # Simulate
            while not next_state.is_terminal():
                info_state = self.state.information_state_string()
                actions_det = [act_prob[0] for act_prob in pi_det[info_state]]
                action = np.random.choice(actions_det)
                next_state = next_state.child(action)

            # Backpropagate
            returns = next_state.returns() 
            while node is not None:
                reward = returns[node.state.current_player()]
                node.update(reward)
                node = node.parent

        # Select the best action
        action, _ = root.select_child()
        return action

    def determine(self, branching_factor: int) \
        -> typing.Dict[str, typing.Tuple[int, float]]:
        """Builds a strategy for all states with given branching
        factor"""
        pi = self.tabular_policy(
            self.all_states,
            self.game.num_players() * [utils.uniform_random_immediate_strategy],
            branching_factor) # ! The branching factor should be set to -1 for the
                              # ! player.
        return pi

    @staticmethod
    def tabular_policy(all_states, strategy_profile, branching_factor):
        tabular_policy = {}
        for state in all_states:
            legal_actions = state.legal_actions()
            if len(legal_actions) < 1:
                continue
            info_state = state.information_state_string()
            if info_state in tabular_policy:
                continue
            player_idx = state.current_player()
            tabular_policy[info_state] = list(
                zip(legal_actions, strategy_profile[player_idx](state, branching_factor=branching_factor)))
        return tabular_policy
