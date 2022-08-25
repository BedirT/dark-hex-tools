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
        self.moves_and_boards = {}
        self.move_stack = []

        self.random_roll = False  # if true, take actions until the terminal state.
        self.target_stack_board = None

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
            str: The new information state.
            bool: True if the game is over.
        """
        # Check if the given input is valid.
        actions, probs = self.is_valid_moves(self.board, given_input)
        if not actions:
            return self.board, False

        # log the action type
        log.info(f"Parsed actions: {actions} / {given_input}")
        self.info_states[self.board] = self._action_probs(actions, probs)

        if self.include_isomorphic:
            iso_state, iso_moves_probs = isomorphic_single(
                self.board, actions, probs)
            if iso_state not in self.info_states:
                self.info_states[iso_state] = iso_moves_probs
            else:
                ls = []
                d = {}
                for action, prob in iso_moves_probs:
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
        addition = 0
        for action in actions:
            new_board = self.moves_and_boards[f"{action}{self.p}"]
            if util.is_board_terminal(new_board, self.p):
                log.info(f"Terminal state reached with action {action}.")
            elif new_board not in self.info_states:
                self.move_stack.append(new_board)
                addition += 1
            if collusion_possible:
                new_board = self.moves_and_boards[f"{action}{self.o}"]
                if util.is_board_terminal(new_board, self.p):
                    log.info(f"Terminal state reached with action {action}.")
                elif new_board not in self.info_states:
                    self.move_stack.append(new_board)
                    addition += 1
        if len(self.move_stack) == 0:
            self.history_buffer.add_history_buffer(self, given_input)
            log.info(f"Game has ended. No more actions to take.")
            self.current_info_state = util.get_info_state_from_board(
                self.board, self.p)
            return self.board, True
        self.board = self.move_stack.pop()
        self.history_buffer.add_history_buffer(self, given_input)
        if self.random_roll:
            self.random_roll = False
            self.target_stack_board = deepcopy(self.move_stack[-addition])
        if self.target_stack_board:
            if self.target_stack_board == self.board:
                self.target_stack_board = None
            else:
                self.iterate_board("random_roll")
        log.info("Move performed succeded.")
        self.current_info_state = util.get_info_state_from_board(
            self.board, self.p)
        return self.board, False

    def is_valid_moves(
            self, board: str, given_input: str
    ) -> typing.Tuple[typing.List[int], typing.List[float]]:
        """Returns the valid actions and their probabilities.

        Args:
            board (str): The current board state.
            given_input (str): The action probabilities. i.e. "a4 0.5 b4 0.5" or "= a4 b4"

        Returns:
            typing.List[int]: The actions given in the input.
            typing.List[float]: The corresponding probabilities.
        """
        actions, probs = self._get_moves(board, given_input)
        if not actions:
            log.error(f"Invalid input: {given_input}")
            return [], []
        # Check if the actions are valid. Save the new board states for each action.
        self.moves_and_boards = {}
        for action in actions:
            new_board = util.board_after_action(board, action, self.o,
                                                self.num_rows, self.num_cols)
            new_board_2 = util.board_after_action(board, action, self.p,
                                                  self.num_rows, self.num_cols)
            if not new_board:
                log.error(f"Invalid action: {action}")
                return [], []
            self.moves_and_boards[f"{action}{self.o}"] = new_board
            self.moves_and_boards[f"{action}{self.p}"] = new_board_2
        # check if sum of probs is 1
        if abs(sum(probs) - 1) > 0.0000001:  # python float comparison
            log.error(f"Values don't add up to one: {probs}->{sum(probs)}")
            return [], []
        log.info(f"Input processed successfully.")
        return actions, probs

    def _get_moves(
            self, board: str, given_input: str
    ) -> typing.Tuple[typing.List[int], typing.List[float]]:
        """Returns the valid actions and their probabilities.

        Args:
            board (str): The current board state.
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
            if self.target_stack_board is None:
                self.random_roll = True
            action = board.find('.')
            return [action], [1]
        if len(action_probs) == 1:
            a = util.convert_alphanumeric_to_position(action_probs[0],
                                                      self.num_cols)
            if isinstance(a, int):
                actions = [a]
                probs = [1]
            else:
                log.error(f"Invalid action: {action_probs[0]}")
                return [], []
        elif action_probs[0] == "=":
            actions = [
                util.convert_alphanumeric_to_position(x, self.num_cols)
                for x in action_probs[1:]
            ]
            if False in actions:
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
        self.move_stack = history.move_stack[-1]
        self.moves_and_boards = history.moves_and_boards[-1]
        self.info_states = history.info_states[-1]
        self.initial_state = history.initial_state[-1]
