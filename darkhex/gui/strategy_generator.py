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
        self.board = util.get_board_from_info_state(initial_state,
                                                    is_perfect_recall)
        self.current_info_state = initial_state
        self.info_states = {}
        self.actions_and_states = {}
        self.action_stack = []
        self.perfect_recall = is_perfect_recall
        self.action_stack_action_history = {}

        self.random_roll = False  # if true, take actions until the terminal state.
        self.target_stack_state = None

        # set history buffer
        self.history_buffer = gameBuffer(self.initial_state, num_rows, num_cols,
                                         player, include_isomorphic, self)

    def iterate_board(self, given_input: str) -> typing.Tuple[str, bool]:
        """Iterate the board with the given action_probability. Actions might be in the form of 
        alpha-numeric or integer representation of the cell. This function updates 
        the information state and the current strategy based on the action.

        Probabilities must be valid.

        Args:
            given_input (str): The action probabilities. i.e. "a4 0.5 b4 0.5" or "= a4 b4"
        
        Returns:
            str: The new board. [layered, xo]
            bool: True if the game is over.
        """
        # Check if the given input is valid.
        actions, probs = self.is_valid_actions(self.board, given_input)
        if not actions:
            return self.board, False

        # log the action type
        log.info(f"Parsed actions: {actions} / {given_input}")
        # update the strategy
        self.info_states[self.current_info_state] = self._action_probs(
            actions, probs)

        if self.include_isomorphic:
            raise NotImplementedError("isomorphic not implemented")
            iso_state, iso_actions_probs = isomorphic_single(
                self.board, actions, probs
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
        
        collusion_possible = util.is_collusion_possible(self.board, self.p)
        log.debug(f"Collusion possible: {collusion_possible}")
        addition = 0
        for action in actions:
            # try inner function to avoid repeated code
            new_state = self.actions_and_states[f"{action}{self.p}"]
            log.debug(new_state)
            new_board = util.get_board_from_info_state(new_state,
                                                       self.perfect_recall)
            if len(new_board) > 1:
                new_board = util.convert_xo_to_board(new_board)
            if util.is_board_terminal(new_board, self.p):
                log.info(f"Terminal state reached with action {action}.")
            elif new_state not in self.info_states:
                self.action_stack.append(new_state)
                addition += 1
            if collusion_possible:
                new_state = self.actions_and_states[f"{action}{self.o}"]
                new_board = util.get_board_from_info_state(
                    new_state, self.perfect_recall)
                log.debug(new_board)
                if len(new_board) > 1:
                    new_board = util.convert_xo_to_board(new_board)
                if util.is_board_terminal(new_board, self.p):
                    log.info(f"Terminal state reached with action {action}.")
                elif new_state not in self.info_states:
                    self.action_stack.append(new_state)
                    addition += 1
        if len(self.action_stack) == 0:
            self.history_buffer.add_history_buffer(self, given_input)
            log.info(f"Game has ended. No more actions to take.")
            return self.board, True
        self.current_info_state = self.action_stack.pop()
        self.board = util.get_board_from_info_state(self.current_info_state,
                                                    self.perfect_recall)
        self.history_buffer.add_history_buffer(self, given_input)
        if self.random_roll:
            self.random_roll = False
            self.target_stack_state = deepcopy(self.action_stack[-addition])
        if self.target_stack_state:
            if self.target_stack_state == self.current_info_state:
                self.target_stack_state = None
            else:
                self.iterate_board("random_roll")
        log.info("Move performed succeded.")
        return self.board, False

    def is_valid_actions(
            self, board:str, given_input: str
    ) -> typing.Tuple[typing.List[int], typing.List[float]]:
        """Returns the valid actions and their probabilities.

        Args:
            board (str): The current board. [layered, xo]
            given_input (str): The action probabilities. i.e. "a4 0.5 b4 0.5" or "= a4 b4"

        Returns:
            typing.List[int]: The actions given in the input.
            typing.List[float]: The corresponding probabilities.
        """
        board = deepcopy(board)
        actions, probs = self._get_actions(board, given_input)
        if not actions:
            return [], []
        # Check if the actions are valid. Save the new board states for each action.
        self.actions_and_states = {}
        for action in actions:
            print(board)
            new_board_0 = util.board_after_action(board, action, self.o)
            new_board_1 = util.board_after_action(board, action, self.p)
            if not new_board_0:
                log.error(f"Invalid action: {action}")
                return [], []
            action_history = self.action_stack_action_history.get(
                self.current_info_state, []) + [action]
            new_state_0 = util.get_info_state_from_board(
                new_board_0, self.p, action_history, self.perfect_recall)
            new_state_1 = util.get_info_state_from_board(
                new_board_1, self.o, action_history, self.perfect_recall)
            self.actions_and_states[f"{action}{self.o}"] = new_state_0
            self.actions_and_states[f"{action}{self.p}"] = new_state_1
            self.action_stack_action_history[new_state_0] = deepcopy(
                action_history)
            self.action_stack_action_history[new_state_1] = deepcopy(
                action_history)
            log.debug(f"States added to stack: {new_state_0}, {new_state_1}")
        # check if sum of probs is 1
        if abs(sum(probs) - 1) > 0.0000001:  # python float comparison
            log.error(f"Values don't add up to one: {probs}->{sum(probs)}")
            return [], []
        log.info(f"Input processed successfully.")
        return actions, probs

    def _get_actions(
            self, board:str, given_input: str
    ) -> typing.Tuple[typing.List[int], typing.List[float]]:
        """Returns the valid actions and their probabilities.

        Args:
            board (str): The current board state. [layered, xo]
            given_input (str): The action probabilities. i.e. "a4 0.5 b4 0.5" or "= a4 b4"

        Returns:
            typing.List[int]: The actions given in the input.
            typing.List[float]: The corresponding probabilities.
        """
        if len(given_input) < 1:
            log.error(f"Empty input: {given_input}")
            return [], []
        action_probs = given_input.strip().split(" ")
        if action_probs[0] == "random_roll":
            if self.target_stack_state is None:
                self.random_roll = True
            action = util.get_random_action(board)
            if action == -1:
                log.error(f"No empty spaces on board: {board}")
                return [], []
            return [action], [1]
        if len(action_probs) == 1:
            a = util.convert_alphanumeric_to_position(action_probs[0],
                                                      self.num_cols)
            if isinstance(a, int):
                if util.is_valid_action(board, a):
                    return [a], [1]
                log.error(f"Invalid action: {action_probs[0]}")
                return [], []
            else:
                log.error(f"Invalid action: {action_probs[0]}")
                return [], []
        elif action_probs[0] == "=":
            actions = [
                util.convert_alphanumeric_to_position(x, self.num_cols)
                for x in action_probs[1:]
            ]
            if False in actions:
                log.error(f"Invalid action: {action_probs[1:]}")
                return [], []
            probs = [1 / len(actions)] * len(actions)
        else:
            actions = []
            probs = []
            for i in range(0, len(action_probs), 2):
                a = util.convert_alphanumeric_to_position(
                    action_probs[i], self.num_cols)
                if a:
                    actions.append(a)
                    probs.append(float(action_probs[i + 1]))
                else:
                    log.error(f"Invalid action: {action_probs[i]}")
                    return [], []
        actions = list(map(int, actions))
        probs = list(map(float, probs))
        return actions, probs

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

    def get_darkhex_policy(self) -> SinglePlayerTabularPolicy:
        """Converts the stored policy to a darkhex policy.
        
        Returns:
            darkhex.TabularSinglePlayerPolicy: The darkhex policy.
        """
        policy = SinglePlayerTabularPolicy(self.info_states,
                                           (self.num_rows, self.num_cols),
                                           self.initial_state, self.p)
        return policy

    def load_game(self, history: gameBuffer):
        """Load a game from a history buffer."""
        self.num_cols = history.game_info["num_cols"]
        self.num_rows = history.game_info["num_rows"]
        self.p = history.game_info["player"]
        self.o = 1 - self.p
        self.history_buffer = history
        self.history_buffer.stratgen_class = self
        self.board = history.board[-1]
        self.action_stack = history.action_stack[-1]
        self.actions_and_states = history.actions_and_states[-1]
        self.info_states = history.info_states[-1]
        self.initial_state = history.initial_state[-1]
        self.action_stack_action_history = history.action_stack_action_history[
            -1]
