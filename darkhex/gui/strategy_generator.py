"""Strategy generator app with Tkinter GUI."""
import typing
from collections import Counter
from copy import deepcopy

from darkhex import cellState
import darkhex.utils.util as util
from darkhex import logger as log
from darkhex.utils.isomorphic import isomorphic_single
from darkhex.policy import SinglePlayerTabularPolicy
from darkhex.gui.history_buffer import gameBuffer


def error_log(message):
    """Logs an error message."""
    log.error(message)
    raise ValueError(message)


class StrategyGenerator:

    def __init__(
        self,
        initial_state: str,
        num_rows: int,
        num_cols: int,
        player: int,
        include_isomorphic: bool = True,
        is_perfect_recall: bool = False,
    ):
        self.num_cols = num_cols
        self.num_rows = num_rows
        self.p = player
        self.o = 1 - self.p
        self.include_isomorphic = include_isomorphic

        self.initial_state = initial_state
        self.current_info_state = initial_state
        self.info_states = {}
        self.action_stack = []
        self.perfect_recall = is_perfect_recall
        self.action_stack_action_history = {}

        self.random_act = False  # if true, take actions until the terminal state.
        self.target_stack_state = None

        # set history buffer
        self.history_buffer = gameBuffer(self.initial_state, num_rows, num_cols,
                                         player, include_isomorphic, self)

    def iterate_board(self, given_input: str) -> bool:
        """Iterate the board with the given action_probability. Actions might be in the form of 
        alpha-numeric or integer representation of the cell. This function updates 
        the information state and the current strategy based on the action.

        Probabilities must be valid.

        Args:
            given_input (str): The action probabilities. i.e. "a4 0.5 b4 0.5" or "= a4 b4"
        
        Returns:
            bool: True if the game is over.
        """
        # Check if the given input is valid.
        actions, probs, addition = self.is_valid_actions(given_input)

        # update the strategy
        self.info_states[self.current_info_state] = self._action_probs(
            actions, probs)

        if self.include_isomorphic:
            raise NotImplementedError("isomorphic not implemented")
            iso_state, iso_actions_probs = isomorphic_single(
                self.current_info_state, actions, probs
            )  # ! WRONG: Just using the board, should convert to info state
            if iso_state not in self.info_states:
                self.info_states[iso_state] = iso_actions_probs
            else:
                ls = []
                d = {}
                for action, prob in iso_actions_probs:
                    if action not in d:
                        ls.append((action, prob / 2))
                        d[action] = len(ls) - 1
                    else:
                        ls[d[action]] = (action, ls[d[action]][1] + prob / 2)
                for action, prob in self.info_states[iso_state]:
                    if action not in d:
                        ls.append((action, prob / 2))
                        d[action] = len(ls) - 1
                    else:
                        ls[d[action]] = (action, ls[d[action]][1] + prob / 2)
                self.info_states[iso_state] = ls

        if len(self.action_stack) == 0:
            self.history_buffer.add_history_buffer(self)
            log.info(f"Game has ended. No more actions to take.")
            return True
        log.debug(self.action_stack)
        self.current_info_state = self.action_stack.pop()
        self.history_buffer.add_history_buffer(self)
        if self.random_act:
            self.random_act = False
            try:
                self.target_stack_state = deepcopy(self.action_stack[-addition])
            except IndexError:
                self.target_stack_state = None
        if self.target_stack_state:
            if self.target_stack_state == self.current_info_state:
                self.target_stack_state = None
            else:
                self.iterate_board("r")
        log.info("Move performed succeded.")
        log.debug(f"Current info state: {self.current_info_state}")
        return False

    def is_valid_actions(
            self, given_input: str
    ) -> typing.Tuple[typing.List[int], typing.List[float]]:
        """Returns the valid actions and their probabilities.

        Args:
            given_input (str): The action probabilities. i.e. "a4 0.5 b4 0.5" or "= a4 b4"

        Returns:
            typing.List[int]: The actions given in the input.
            typing.List[float]: The corresponding probabilities.
        """
        actions, probs = [], []
        if len(given_input) < 1:
            error_log("No input given.")
        action_probs = given_input.strip().split(" ")
        if action_probs[0] == "r":  # random action
            if self.target_stack_state is None:
                self.random_act = True
            action = util.get_random_action_for_info_state(
                self.current_info_state)
            if action == -1:
                error_log(f"No valid action found. {self.current_info_state}")
            actions, probs = [action], [1.0]
        elif len(action_probs) == 1:
            a = util.convert_alphanumeric_to_position(action_probs[0],
                                                      self.num_cols)
            if isinstance(a, int):
                if util.is_valid_action_from_info_state(self.current_info_state,
                                                        a):
                    actions, probs = [a], [1]
        elif action_probs[0] == "=":  # equiprobable actions
            actions = [
                util.convert_alphanumeric_to_position(x, self.num_cols)
                for x in action_probs[1:]
            ]
            probs = [1 / len(actions)] * len(actions)
        else:
            for i in range(0, len(action_probs), 2):
                a = util.convert_alphanumeric_to_position(
                    action_probs[i], self.num_cols)
                if a:
                    actions.append(a)
                    probs.append(float(action_probs[i + 1]))
                else:
                    error_log(f"Invalid action: {action_probs[i]}")
        if not actions or not probs:
            error_log(f"No valid actions found. {given_input}")
        actions = list(map(int, actions))
        probs = list(map(float, probs))
        addition = 0
        p_list = [self.p, self.o] if util.is_collusion_possible_info_state(
            self.current_info_state) else [self.p]
        for action in actions:
            for player in p_list:
                new_state = util.info_state_after_action(
                    self.current_info_state, action, player, self.perfect_recall)
                if util.is_info_state_terminal(new_state, self.perfect_recall):
                    log.info(f"Terminal state reached with action {action}.")
                elif new_state not in self.info_states:
                    self.action_stack.append(new_state)
                    addition += 1
        # check if sum of probs is 1
        if abs(sum(probs) - 1) > 0.0000001:  # python float comparison
            error_log(f"Values don't add up to one: {probs}->{sum(probs)}")
        log.info(f"Input processed successfully. {actions} {probs}")
        return actions, probs, addition

    def _action_probs(self,
                      actions: typing.List[int],
                      probs: typing.List[float] = None
                     ) -> typing.List[typing.Tuple[int, float]]:
        """Returns the action probs for the current board. If no probs are given, the probs are uniform.

        Args:
            actions (typing.List[int]): The actions to be performed.
            probs (typing.List[float]): The corresponding probabilities.

        Returns:
            typing.List[typing.Tuple[int, float]]: The action probs.
        """
        if probs is None:
            probs = [1 / len(actions)] * len(actions)
        else:
            assert len(actions) == len(probs)
        return list(zip(actions, probs))

    def save_darkhex_policy(self, path) -> SinglePlayerTabularPolicy:
        """Converts the stored policy to a darkhex policy.
        
        Args:
            path (str): The path to save the policy to.
        Returns:
            darkhex.TabularSinglePlayerPolicy: The darkhex policy.
        """
        policy = SinglePlayerTabularPolicy(self.info_states,
                                           (self.num_rows, self.num_cols),
                                           self.initial_state, self.p,
                                           self.perfect_recall)
        policy.save_policy_to_file(path)
        return policy

    def load_game(self, history: gameBuffer):
        """Load a game from a history buffer."""
        self.num_cols = history.game_info["num_cols"]
        self.num_rows = history.game_info["num_rows"]
        self.p = history.game_info["player"]
        self.o = 1 - self.p
        self.history_buffer = history
        self.history_buffer.stratgen_class = self
        self.info_states = history.info_states[-1]
        self.target_stack_state = history.target_stack_state[-1]
        self.current_info_state = history.current_info_state[-1]
