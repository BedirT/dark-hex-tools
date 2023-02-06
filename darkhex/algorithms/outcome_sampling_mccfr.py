import numpy as np
import pyspiel
import typing
from darkhex.algorithms.mccfr import MCCFRBase


class OutcomeSamplingMCCFR(MCCFRBase):

    def __init__(self, game: pyspiel.Game, epsilon: float = 0.6) -> None:
        super().__init__(game)
        self._eps = epsilon  # Exploration parameter

    def run(self, num_iterations: int) -> None:
        """
        Runs the MCCFR algorithm for the given number of iterations.
        Args:
            num_iterations (int): The number of iterations to run.
        """
        for _ in range(num_iterations):
            self._iteration()

    def _iteration(self) -> None:
        """
        Performs one iteration of the MCCFR algorithm.
        """
        for update_player in range(self._num_players):
            init_state = self._game.new_initial_state()
            self._run_episode(init_state,
                              update_player,
                              player_reach=1.0,
                              opponent_reach=1.0,
                              sample_reach=1.0)

    def _run_episode(self, state: pyspiel.State, update_player: int,
                     player_reach: float, opponent_reach: float,
                     sample_reach: float) -> None:
        """
        Runs an episode of the MCCFR algorithm.
        Args:
            state (pyspiel.State): The current state.
            update_player (int): The player to update.
            player_reach (float): The reach probability of the player.
            opponent_reach (float): The reach probability of the opponent.
            sample_reach (float): The reach probability of the sample.
        """
        pass
