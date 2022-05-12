from __future__ import annotations

import typing
import pyspiel
import numpy as np
import math

import darkhex.utils as utils


class Node:

    def __init__(
        self,
        info_state: str,
        player: int,
        parent: Node = None,
        k: float = 1.4,
    ):
        self.k = k  # exploration parameter
        self.info_state = info_state
        self.player = player
        self.parent = parent
        self.num_visits = 0
        self.num_available = 0
        self.total_reward = 0
        self.children = {}

    def select_child(self, det_actions: typing.Dict[str, typing.List[int]],
                     obs_player: int) -> typing.Tuple[int, Node]:
        """Select child from children using UCB according to
        the given determinization. If the node belongs to the observing player,
        then the child with the highest value is selected. Otherwise, the action
        is selected randomly since the tree only shares a single branch for this
        player's moves."""
        if self.player != obs_player:
            # select random child
            rand_action = np.random.choice(list(self.children.keys()))
            return rand_action, self.children[0]
        actions = [
            action for action in self.children.keys()
            if action in det_actions[self.info_state]
        ]
        best_action = max(actions,
                          key=lambda action: self.children[action].value())
        return best_action, self.children[best_action]

    def value(self) -> float:
        """Returns the value of the node (UCB)"""
        arg1 = self.total_reward / self.num_visits
        arg2 = self.k * math.sqrt(
            math.log(self.num_available) / self.num_visits)
        return arg1 + arg2

    def expanded(self, det_actions: typing.Dict[str, typing.List[int]]) -> bool:
        """If the node is fully expanded for the given determinization."""
        return all(action in self.children.keys()
                   for action in det_actions[self.info_state])

    def expand(self, cur_state: pyspiel.State,
               det_actions: typing.Dict[str, typing.List[int]],
               obs_player: int) -> typing.Tuple[int, Node]:
        """Expand the node, with the given determinization."""
        actions_w_det = [
            action for action in det_actions[self.info_state]
            if action not in self.children.keys()
        ]
        if obs_player != self.player:
            if not self.children:
                rand_action, child = self._new_random_child(
                    actions_w_det, cur_state)
                self.children[
                    0] = child  # only one child; no need to store action
                return rand_action, child
            rand_action = np.random.choice(actions_w_det)
            return rand_action, self.children[0]

        rand_action, child = self._new_random_child(actions_w_det, cur_state)
        self.children[rand_action] = child
        assert all(
            [key in cur_state.legal_actions() for key in self.children.keys()])
        return rand_action, self.children[rand_action]

    def _new_random_child(self, actions_w_det: typing.List[int],
                          cur_state: pyspiel.State) -> typing.Tuple[int, Node]:
        """Create a new child node with a random action."""
        rand_action = np.random.choice(actions_w_det)
        child_state = cur_state.child(rand_action)
        if child_state.is_terminal():
            # this is a winner move
            return rand_action, \
                   Node(info_state='terminal',
                        player=self.player, # winner
                        parent=self,
                        k=self.k) # terminal node
        child = Node(child_state.information_state_string(),
                     child_state.current_player(), self, self.k)
        return rand_action, child

    def update(
        self,
        reward: int,
        det_actions: typing.Dict[str, typing.List[int]],
    ) -> None:
        """Update the node values"""
        self.num_visits += 1
        self.total_reward += reward
        if self.parent is not None:
            actions_det = det_actions[self.parent.info_state]
            for action, child in self.parent.children.items():
                if action in actions_det:
                    child.num_available += 1


class ISMCTS:
    """
    Implementation of Information Set Monte Carlo Tree Search with Partialy 
    Observable Moves, from the paper: 'Information Set Monte Carlo Tree Search'
    by Peter I. Cowling, Edward J. Powley, Daniel Whitehouse. Using pyspiel
    library for the game specific logic.
    """

    def __init__(
        self,
        game: pyspiel.Game,
        obs_player: int,
        args: utils.dotdict,
    ):
        self.game = game
        self.obs_player = obs_player
        self.args = args

    def run(self, state):
        root = Node(state.information_state_string(), state.current_player(),
                    None, self.args.k)

        for _ in range(self.args.num_simulations):
            self.det_actions = self.determinization()
            node = root
            next_state = state.clone()

            # Select
            while not next_state.is_terminal() and node.expanded(
                    self.det_actions):
                # if node is not terminal and fully expanded for determinization
                action, node = node.select_child(self.det_actions,
                                                 self.obs_player)
                next_state = next_state.child(action)

            # Expand
            if not next_state.is_terminal():
                action, node = node.expand(next_state, self.det_actions,
                                           self.obs_player)
                next_state = next_state.child(action)

            # Simulate
            while not next_state.is_terminal():
                info_state = next_state.information_state_string()
                action = np.random.choice(self.det_actions[info_state])
                next_state = next_state.child(action)

            # Backpropagate
            returns = next_state.returns()
            while node is not None:
                reward = returns[node.player]
                node.update(reward, self.det_actions)
                node = node.parent

        # Select the best action
        action, _ = root.select_child(self.det_actions, self.obs_player)
        return action

    def determinization(self):
        """
        Returns a dictionary of all the determinizations of the game.
        """
        state = self.game.new_initial_state()
        determinization = self._determine(state, {})
        return determinization

    def _determine(self, state, det_actions):
        info_state = state.information_state_string()
        legal_actions = state.legal_actions()
        if self.args.branching_factor < 0 or \
            len(legal_actions) <= self.args.branching_factor:
            det_actions[info_state] = legal_actions
        else:
            det_actions[info_state] = np.random.choice(
                legal_actions, self.args.branching_factor, replace=False)
        for action in det_actions[info_state]:
            child_state = state.child(action)
            if child_state.is_terminal():
                continue
            self._determine(child_state, det_actions)
        return det_actions
