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
from darkhex.utils.util import load_file, save_file, report


class Node:
    """Best response strategy state node. """

    def __init__(self,
                 info_state: str,
                 history: str,
                 reach_prob: float,
                 value: float = 0.,
                 wait_node: bool = False,
                 is_terminal: bool = False):
        """ Initialize a node. """
        self.info_state = info_state
        self.history = history
        self.reach_prob = reach_prob
        self.value = value
        self.wait_node = wait_node
        self.is_terminal = is_terminal
        self.children = {}

        self.node_key = history

    def __repr__(self):
        return f"{self.node_key}"


class BRTree:
    """
    Best Response tree functionality. Driver for the Nodes.
    """

    def __init__(self, br_player: int):
        self.root = None
        self.nodes = {}  # type: typing.Dict[str, Node]
        self.terminal_nodes = {}  # type: typing.Dict[str, Node]
        self.br_player = br_player

    def add_node(self,
                 state: pyspiel.State,
                 history: list,
                 reach_prob: np.float64,
                 parent: Node = None,
                 action: int = None,
                 value: float = 0.):
        """ Add a node to the tree. 
        
        Args:
            state (pyspiel.State): State of the game.
            history (list): Action history of the game, used to create the node key.
            reach_prob (np.float64): Reach probability on log-scale.
            parent (Node, optional): Parent node. Defaults to None.
            action (int, optional): Action taken to get to this state. Defaults to None.
            value (float, optional): Value of the state. Defaults to 0.
        """
        wait_node = len(state.legal_actions(self.br_player)) == 0
        info_state = state.information_state_string(self.br_player)
        history_str = "".join(str(x) for x in history)
        key = history_str

        if key not in self.nodes:
            self.nodes[key] = Node(info_state, history_str, reach_prob, value,
                                   wait_node)

        # Connect the node to the parent
        if parent is not None:
            parent_node = self.get_node(parent.node_key)
            if action in parent_node.children:
                raise ValueError(
                    f"Node {parent_node} already has child {action}")
            parent_node.children[action] = self.nodes[key]
        return self.nodes[key]

    def add_terminal_node(self,
                          state: pyspiel.State,
                          history: list,
                          reach_prob: np.float64 = np.log(1.),
                          parent: Node = None,
                          action: int = None,
                          value: float = 0.):
        """ Add a terminal node to the tree. 
        
        Args:
            state (pyspiel.State): State of the game.
            history (list): Action history of the game, used to create the node key.
            reach_prob (np.float64, optional): Reach probability on log-scale. Defaults to np.log(1.).
            parent (Node, optional): Parent node. Defaults to None.
            action (int, optional): Action taken to get to this state. Defaults to None.
            value (float, optional): Value of the state. Defaults to 0.
        """
        parent_node = self.get_node(parent.node_key)
        info_state = state.information_state_string(self.br_player)
        history_str = "".join(str(x) for x in history)
        key = history_str

        if key not in self.terminal_nodes:
            self.terminal_nodes[key] = Node(info_state,
                                            history_str,
                                            reach_prob,
                                            value,
                                            is_terminal=True)
        if action in parent_node.children:
            raise ValueError(f"Node {parent_node} already has child {action}")
        parent_node.children[action] = self.terminal_nodes[key]

    def get_node(self, node_key: tuple) -> Node:
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

    def best_response(self):
        """
        Calculate the best response value for the given player strategy.

        (Driver)

        - Create the tree keeping the histories and their reach probabilities.
        - Combine the nodes in buckets and calculate q_values for each bucket.
        - Calculate the best response value.
        """
        start = time.time()  # Start timer for reporting

        self._generate_history_tree(self._initial_state, self._br_tree.root, [])
        self._calculate_values(self._br_tree.root, {})

        # Generate best response strategy
        br_strategy = self._best_response_strategy(self._br_tree)
        # br_strategy = load_file(self._br_strategy_save_path)

        self.strategies = {
            self._eval_player: self._eval_strategy,
            self._br_player: br_strategy,
        }

        br_value = 1 - (self._calculate_br_value(self._initial_state) + 1) / 2

        # reporting
        print(f"BR Tree size: {len(self._br_tree.nodes)}")
        print(f"Number of terminal nodes: {len(self._br_tree.terminal_nodes)}")
        report(time.time() - start, 'time')
        report(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, 'memory')

        # write the opponent strategy to a file
        save_file(br_strategy, self._br_strategy_save_path)

        return br_value

    def _generate_history_tree(
        self,
        cur_state: pyspiel.State,
        parent_node: Node,
        history: list,
        reach_prob: np.float64 = np.log(1.0)) -> float:
        """
        Generate the value tree for the best response player playing against
        the given player strategy.

        Value is always in perspective of the best response player. Only the
        terminal states are assigned a value for now, later on we backpropagate
        to update the value of the parent states.

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
            for action in cur_state.legal_actions():
                next_state = cur_state.child(action)
                new_history = history + [action]
                if next_state.is_terminal():
                    value = next_state.returns()[self._br_player]
                    self._br_tree.add_terminal_node(state=next_state,
                                                    history=new_history,
                                                    reach_prob=reach_prob,
                                                    parent=parent_node,
                                                    action=action,
                                                    value=value)
                else:
                    new_node = self._br_tree.add_node(state=next_state,
                                                      history=new_history,
                                                      reach_prob=reach_prob,
                                                      parent=parent_node,
                                                      action=action)
                    self._generate_history_tree(next_state, new_node, new_history,
                                                reach_prob)
            return

        # strategy players turn
        for action, prob in self._eval_strategy[info_state]:
            next_state = cur_state.child(action)
            new_history = history + [action]
            if next_state.is_terminal():
                value = next_state.returns()[self._br_player]
                self._br_tree.add_terminal_node(state=next_state,
                                                history=new_history,
                                                reach_prob=reach_prob +
                                                np.log(prob),
                                                parent=parent_node,
                                                action=action,
                                                value=value)
            else:
                new_node = self._br_tree.add_node(state=next_state,
                                                  history=new_history,
                                                  reach_prob=reach_prob +
                                                  np.log(prob),
                                                  parent=parent_node,
                                                  action=action)
                self._generate_history_tree(next_state, new_node, new_history,
                                            reach_prob + np.log(prob))

    # todo: Use decorator for memoization
    def _calculate_values(self, cur_node: Node, memoize: dict):
        """
        Backpropogate the values from the terminal nodes to the parent nodes.

        Args:
            cur_node: The current node to backpropogate from.
        """
        if cur_node.is_terminal:
            cur_node.value *= np.exp(cur_node.reach_prob)
            return cur_node.value
        if cur_node.node_key in memoize:
            return memoize[cur_node.node_key]
        tot_value = 0.
        mx_value = -np.inf
        for action, child in cur_node.children.items():
            child_value = self._calculate_values(child, memoize)
            mx_value = max(mx_value, child_value)
            tot_value += child_value
        if cur_node.wait_node:
            cur_node.value = tot_value
            return tot_value
        cur_node.value = mx_value
        memoize[cur_node.node_key] = cur_node.value
        return cur_node.value

    def _get_br_strategy(self, cur_state: pyspiel.State, br_buckets: dict,
                         br_strategy: dict):
        """ Depth first search to find the best response strategy using the
        bucketed histories. """
        if cur_state.is_terminal():
            return
        cur_player = cur_state.current_player()
        info_state = cur_state.information_state_string()
        if info_state in br_strategy:
            self._get_br_strategy(
                cur_state.child(br_strategy[info_state][0][0]), br_buckets,
                br_strategy)
            return
        if cur_player == self._br_player:
            # best response player turn
            best_val = -np.inf
            best_action = None
            for val, action in br_buckets[info_state]:
                if val > best_val:
                    best_val = val
                    best_action = action
            br_strategy[info_state] = [(best_action, 1.)]
            self._get_br_strategy(cur_state.child(best_action), br_buckets,
                                  br_strategy)
            return
        # strategy player turn
        for action, prob in self._eval_strategy[info_state]:
            self._get_br_strategy(cur_state.child(action), br_buckets,
                                  br_strategy)

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
                value = new_state.returns()[self._br_player] * np.exp(
                    reach_prob + np.log(prob))
                br_value += value
            else:
                br_value += self._calculate_br_value(new_state,
                                                     reach_prob + np.log(prob))
        return br_value
