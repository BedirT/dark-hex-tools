"""
Using open_spiel dark_hex implementation
to calculate best response value for a given player strategy.
"""
import typing
from collections import defaultdict
import pydot
from decimal import Decimal

import pyspiel
from darkhex.utils.util import (convert_os_strategy, get_open_spiel_state,
                                greedify, save_file, load_file)


class Node:
    """Best response strategy state node. """

    def __init__(self,
                 info_state: str,
                 reach_prob: float,
                 wait_node: bool,
                 value: float = 0.,
                 is_terminal: bool = False):
        self.info_state = info_state
        self.reach_prob = reach_prob
        self.value = value
        self.wait_node = wait_node
        self.node_key = (info_state, wait_node)
        self.is_terminal = is_terminal

        # X <- [Node, Node], 0: action node, 1: wait node
        # Wait node can be none, but action node will never be none.
        # - Wait node must have if_wait = True
        # - Action node must have if_wait = False
        self.children = defaultdict(lambda: [None, None])

        self.best_action = None

    def __repr__(self):
        return f"{self.info_state}:{self.reach_prob}:{self.value}:{self.wait_node}"


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
                 reach_prob: float,
                 parent: Node = None,
                 action: int = None,
                 value: float = 0.):
        """ Add a node to the tree. """
        info_state = state.information_state_string(self.br_player)
        wait_node = len(state.legal_actions(self.br_player)) == 0
        key = (info_state, wait_node)

        if key not in self.nodes:
            self.nodes[key] = Node(info_state, reach_prob, wait_node, value)
        # Connect the node to the parent
        if parent is not None:
            parent_node = self.get_node(parent.node_key)
            if parent_node is not self.nodes[key]:
                if parent_node.wait_node:
                    parent_node.children[-1] = [self.nodes[key], None]
                else:
                    parent_node.children[action][int(
                        self.nodes[key].wait_node)] = self.nodes[key]
        return self.nodes[key]

    def add_terminal_node(self,
                          state: pyspiel.State,
                          parent: Node = None,
                          action: int = None,
                          reach_prob: float = Decimal('1.0'),
                          value: float = 0.):
        """ Add a terminal node to the tree. """
        wait_node = len(state.legal_actions(self.br_player)) == 0
        parent_node = self.get_node(parent.node_key)

        if parent_node.children[action][int(wait_node)] is not None:
            parent_node.children[action][int(
                wait_node)].reach_prob += reach_prob
        else:
            parent_node.children[action][int(wait_node)] = Node(
                state.information_state_string(self.br_player) + f':T:{action}',
                reach_prob,
                wait_node,
                value,
                is_terminal=True)

    def get_node(self, node_key: tuple) -> Node:
        """
        Get a node from the tree.
        """
        return self.nodes.get(node_key, None)


class BestResponse:

    def __init__(
        self,
        game: pyspiel.Game,
        strategy_player: int,
        initial_state: str,
        num_cols: int,
        strategy: typing.Dict[str, typing.List[typing.Tuple[int, float]]],
        file_path: str,
    ):
        self.game = game
        self.s_player = strategy_player
        self.br_player = 1 - strategy_player
        self.initial_state = initial_state
        self.strategy = strategy
        self.num_cols = num_cols
        self.file_path = file_path

        self.full_game_state_cache = {}

    @staticmethod
    def _br_value(val: float) -> float:
        # return (val + 1) / 2
        return Decimal(str(val))

    def _generate_value_tree(self,
                             cur_state: pyspiel.State,
                             br_tree: BRTree,
                             parent_node: Node,
                             reach_prob: float = 1.0) -> float:
        """
        Generate the value tree for the best response player playing against
        the given player strategy.

        value is always in perspective of the best response player. Only the
        terminal states are assigned a value for now, later on we backpropagate
        to update the value of the parent states.
        """
        cur_player = cur_state.current_player()
        info_state = cur_state.information_state_string()

        full_state = cur_state.information_state_string(0) + \
                     cur_state.information_state_string(1)
        if full_state in self.full_game_state_cache:
            return
        self.full_game_state_cache[full_state] = True

        if cur_player == self.br_player:
            # best response players turn
            for action in cur_state.legal_actions():
                next_state = cur_state.child(action)
                if next_state.is_terminal():
                    value = self._br_value(next_state.returns()[self.br_player])
                    br_tree.add_terminal_node(next_state, parent_node, action,
                                              reach_prob, value)
                else:
                    new_node = br_tree.add_node(next_state, reach_prob,
                                                parent_node, action)
                    self._generate_value_tree(next_state, br_tree, new_node,
                                              reach_prob)
            return
        # strategy players turn
        for action, prob in self.strategy[info_state]:
            next_state = cur_state.child(action)
            if next_state.is_terminal():
                value = self._br_value(next_state.returns()[self.br_player])
                decimal_prob = Decimal(str(prob)) * Decimal(str(reach_prob))
                br_tree.add_terminal_node(next_state, parent_node, action,
                                          decimal_prob, value)
            else:
                decimal_prob = Decimal(str(prob)) * Decimal(str(reach_prob))
                new_node = br_tree.add_node(next_state, decimal_prob,
                                            parent_node, action)
                self._generate_value_tree(next_state, br_tree, new_node,
                                          decimal_prob)

    def _backpropogate_values(self, br_tree: BRTree, cur_node: Node = None):
        """
        Backpropogate the values from the terminal nodes to the parent nodes.
        """
        if cur_node is None:
            cur_node = br_tree.root
        if cur_node.is_terminal:
            # Terminal node
            cur_node.value *= cur_node.reach_prob
            return cur_node.value
        tot_value = Decimal('0.0')
        mx_value = Decimal('-inf')
        for action, children in cur_node.children.items():
            children_value = Decimal('0.0')
            for child in children:
                if child is not None:
                    children_value += self._backpropogate_values(br_tree, child)
            tot_value += children_value
            mx_value = max(mx_value, children_value)
        if cur_node.wait_node:
            cur_node.value = tot_value
            return tot_value
        cur_node.value = mx_value
        return mx_value

    def best_response_strategy(self, br_strategy_info):
        """
        Calculate the best response strategy for the given player strategy and
        calculated best response values.

        br_strategy is greedy. So always: br_strategy[info_state] = [(action,1)]
        """
        br_strategy: typing.Dict[str, typing.List[typing.Tuple[int,
                                                               float]]] = {}
        for (info_state, wait_node), cur_node in br_strategy_info.items():
            if wait_node:
                continue
            # find the best action for the given info state
            best_action = None
            best_value = Decimal('-inf')
            for action, children in cur_node.children.items():
                children_value = Decimal('0.0')
                for child in children:
                    if child is None:
                        continue
                    children_value += child.value
                if children_value > best_value:
                    best_value = children_value
                    best_action = action
            br_strategy[info_state] = [(best_action, 1.0)]
            cur_node.best_action = best_action
        return br_strategy

    def _calculate_br_value(self, cur_state: pyspiel.State) -> float:
        """
        Calculate the best response value for the given player strategy and
        calculated opponent strategy.
        """
        br_value = Decimal('0.0')
        cur_player = cur_state.current_player()
        info_state = cur_state.information_state_string()
        for action, prob in self.strategies[cur_player][info_state]:
            new_state = cur_state.child(action)
            if new_state.is_terminal():
                value = (Decimal(str(new_state.returns()[self.br_player])) \
                    + Decimal('1.0')) / Decimal('2.0')
            else:
                value = self._calculate_br_value(new_state)
            br_value +=  Decimal(str(value)) * Decimal(str(prob))
        return br_value

    @staticmethod
    def graph_test(br_tree: BRTree, file_path: str):
        """ 
        Draw the tree graph. 
        """
        graph = pydot.Dot(graph_type='digraph')
        for node in br_tree.nodes.values():
            node_id = node.info_state + '\n' + str(node.value) + '\n' + str(
                node.reach_prob) + '\n' + str(node.wait_node)
            if node.wait_node:
                graph.add_node(
                    pydot.Node(node_id, style='filled', fillcolor='#ff0000'))
            else:
                graph.add_node(pydot.Node(node_id))
        for node in br_tree.nodes.values():
            node_id = node.info_state + '\n' + str(node.value) + '\n' + str(
                node.reach_prob) + '\n' + str(node.wait_node)
            for action, children in node.children.items():
                for child in children:
                    if child is None:
                        continue
                    ch_info = child.info_state + '\n' + str(
                        child.value) + '\n' + str(
                            child.reach_prob) + '\n' + str(child.wait_node)
                    graph.add_edge(
                        pydot.Edge(node_id, ch_info, label=str(action)))
        graph.write_png(file_path)

    def best_response(self):
        """
        Calculate the best response value for the given player strategy.
        """
        game_state = get_open_spiel_state(self.game, self.initial_state)

        # Generate the BR tree
        br_tree = BRTree(self.br_player)
        br_tree.root = br_tree.add_node(game_state, Decimal('1.0'))
        self._generate_value_tree(game_state, br_tree, br_tree.root)

        # Backpropogate the values
        self._backpropogate_values(br_tree)

        # graph test
        # self.graph_test(br_tree, 'tmp/br_tree.png')

        # Generate best response strategy
        br_strategy = self.best_response_strategy(br_tree.nodes)

        # self.br_strategy = load_file(self.file_path)

        # calculate the best response value
        self.strategies = {
            self.s_player: self.strategy,
            self.br_player: br_strategy,
        }
        br_value = 1 - self._calculate_br_value(
            game_state)  # how good the given strategy is

        # write the opponent strategy to a file
        save_file(br_strategy, self.file_path)

        return br_value
