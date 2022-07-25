""" 
Imperfect Recall Best Response

IRBR is a BR variant that uses imperfect recall. Perfect recall
games will still work, but the aim of IRBR is to be able to
calculate the best response value for imperfect recall games.

We still use the action history to calculate the reach probabilities,
after that however we bucket the histories based on the information
states. We then focus only on the buckets individually and calculate
the q_values for each bucket and the actions for each bucket. We then
use the q_values to calculate the best response strategy, hence the
best response value.

Couple tricks to make this work:
  - We use the action history to calculate individual reach probabilities.
  - We bucket the histories based on the information states, and accumulate
    the reach probabilities for each bucket.
  - While bucketing, we also calculate the q_values for each bucket. 
  - The value of an information state is the maximum of the q_values times
    the reach probability for that information state.
    - The q_value is the expectation of the values of the action for each
      history.
    - The reach probability of an information state is the sum of the reach
      probabilities of the histories that contain the information state.
  - The best response action is the action with the highest q_value with
    probability one.
  - All the probabilities are calculated using the logarithm. This is
    because the probabilities are very small and we want to avoid
    underflow. We also multiply the probabilities by the reach probability
    many times, so using the logarithm is a good way to get a more
    precise result.
"""
import time
import resource
import typing
import numpy as np
import pyspiel
from collections import defaultdict
from darkhex.utils.util import load_file, save_file, report


class Node:
    """Best response strategy state node. """

    def __init__(self,
                 info_state: str,
                 history: str,
                 reach_prob: float):
        """ Initialize a node. """
        self.info_state = info_state
        self.history = history
        self.reach_prob = reach_prob

    def __repr__(self):
        return f"{self.history}"


class BRTree:
    """
    Best Response tree functionality. Driver for the Nodes.
    """

    def __init__(self, br_player: int):
        self.root = None
        self.nodes = {}  # type: typing.Dict[str, Node]
        self.br_player = br_player

    def add_node(self,
                 state: pyspiel.State,
                 history: list,
                 reach_prob: np.float64):
        """ Add a node to the tree. 
        
        Args:
            state (pyspiel.State): State of the game.
            history (list): Action history of the game, used to create the node key.
            reach_prob (np.float64): Reach probability on log-scale.
        """
        info_state = state.information_state_string(self.br_player)
        history_str = "".join(str(x) for x in history)
        if history_str not in self.nodes:
            self.nodes[history_str] = Node(info_state, history_str, reach_prob)
            if len(self.nodes) == 1:
                self.root = self.nodes[history_str]
        return self.nodes[history_str]

    def get_node(self, node_key: str) -> Node:
        """ Get a node from the tree. """
        return self.nodes.get(node_key, None)


class BestResponse:

    def __init__(
        self,
        initial_state: pyspiel.State,
        eval_player: int,
        eval_strategy: typing.Dict[str, typing.List[typing.Tuple[int, float]]],
        br_strategy_save_path: str,
    ):
        """
        Initialize the best response class.

        Args:
            initial_state (pyspiel.State): Initial state of the game.
            eval_player (int): Player to evaluate the best response for.
            eval_strategy (typing.Dict[str, typing.List[typing.Tuple[int, float]]]):
                Dictionary of information state to action and probability. The
                strategy of the eval_player that we are evaluating.
            br_strategy_save_path (str): Path to save the best response strategy.
        """
        self._initial_state = initial_state
        self._eval_player = eval_player
        self._br_player = 1 - eval_player
        self._eval_strategy = eval_strategy
        self._br_strategy_save_path = br_strategy_save_path

        self._br_tree = BRTree(self._br_player)
        self._br_tree.root = self._br_tree.add_node(self._initial_state, [],
                                                    np.log(1.0))
        self._value_memory = {}  # type: typing.Dict[str, float]
        self._buckets = defaultdict(lambda: defaultdict(lambda: np.log(1.0)))
        self._br_strategy = {}  # type: typing.Dict[str, typing.List[typing.Tuple[int, float]]]

    def best_response(self):
        """
        Calculate the best response value for the given player strategy.

        (Driver)

        - Create the tree keeping the histories and their reach probabilities.
        - Combine the nodes in buckets and calculate q_values for each bucket.
        - Calculate the best response value.
        """
        start = time.time()  # Start timer for reporting

        self._generate_history_tree(self._initial_state, [])
        print(f"Completed generating history tree in {time.time() - start} seconds.")
        self._info_set_rp = self._bucket_histories() # information set reach probabilities
        # self._info_set_rp = self._buckets
        root_value = self._value(self._initial_state)
        # self._br_strategy = load_file(self._br_strategy_save_path) # test

        self.strategies = {
            self._eval_player: self._eval_strategy,
            self._br_player: self._br_strategy,
        }
        br_value = self._calculate_br_value(self._initial_state)

        # reporting
        print(f"Number of histories: {len(self._br_tree.nodes)}")
        report(time.time() - start, 'time')
        report(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, 'memory')

        # write the opponent strategy to a file
        save_file(self._br_strategy, self._br_strategy_save_path)

        return br_value

    def _generate_history_tree(
        self,
        cur_state: pyspiel.State,
        history: list,
        reach_prob: np.float64 = np.log(1.0)) -> float:
        """
        Generate the value tree for the best response player playing against
        the given player strategy.

        Args:
            cur_state: The current state of the game.
            parent_node: The parent node of the current state.
            history: The action history of the current state.
            reach_prob: The reach probability of the current state.
        """
        cur_player = cur_state.current_player()
        info_state = cur_state.information_state_string()

        if cur_player == self._br_player:
            # best response players turn
            history_str = "".join(str(x) for x in history)
            self._buckets[info_state][history_str] += reach_prob
            for action in cur_state.legal_actions():
                next_state = cur_state.child(action)
                # new_history = history + [action]
                if not next_state.is_terminal():
                    self._generate_history_tree(next_state, history,
                                                reach_prob)
            return
        # strategy players turn
        for action, prob in self._eval_strategy[info_state]:
            next_state = cur_state.child(action)
            new_history = history + [action]
            if not next_state.is_terminal():
                self._generate_history_tree(next_state, new_history,
                                            reach_prob + np.log(prob))

    def _bucket_histories(self):
        """
        Bucket the histories of the tree into information sets.
        Then calculate the reach probability of each bucket, and return the
        reach probability dictionary.
        """
        accumulated_reach_prob = {}
        for info_state, histories in self._buckets.items():
            reach_prob = np.log(1.0)
            for _, rp in histories.items():
                reach_prob = np.logaddexp(reach_prob, rp)
            accumulated_reach_prob[info_state] = reach_prob
        return accumulated_reach_prob

    def _value(self, state: pyspiel.State) -> float:
        """
        Calculate the value of the given state. A value of a state
        is the average of the q_values of the actions if the player
        is the best response player, otherwise its the expectation
        of the actions.
            
        Args:
            state: The state to calculate the value for.
        """
        if state.is_terminal():
            return state.returns()[self._br_player]
        full_info_state = state.information_state_string(0) + \
            state.information_state_string(1)
        if full_info_state in self._value_memory:
            return self._value_memory[full_info_state]
        cur_player = state.current_player()
        info_state = state.information_state_string()
        if cur_player == self._br_player:
            mx_value = -np.inf
            reach_prob = np.exp(self._info_set_rp[state.information_state_string()])
            for action in state.legal_actions():
                next_state = state.child(action)
                value = self._value(next_state) * reach_prob
                if value > mx_value:
                    mx_value = value
                    self._br_strategy[info_state] = [(action, 1.0)]
            self._value_memory[full_info_state] = mx_value
            return mx_value
        exp_value = 0
        for action, prob in self._eval_strategy[info_state]:
            next_state = state.child(action)
            exp_value += prob * self._value(next_state)
        self._value_memory[full_info_state] = exp_value
        return exp_value

    def _calculate_br_value(
        self, cur_state: pyspiel.State,
        reach_prob: np.float64 = np.log(1.0)) -> float:
        """
        Calculate the best response value for the given player strategy and
        calculated opponent strategy.
        """
        br_value = 0.
        cur_player = cur_state.current_player()
        info_state = cur_state.information_state_string()
        for action, prob in self.strategies[cur_player][info_state]:
            new_state = cur_state.child(action)
            if new_state.is_terminal():
                value = new_state.returns()[self._br_player]
                if value in [-1, 0]: # if the game is lost or drawn
                    value = 0
                br_value += np.exp(
                    reach_prob + np.log(prob)) * value
            else:
                br_value += self._calculate_br_value(new_state,
                                                     reach_prob + np.log(prob))
        return br_value
