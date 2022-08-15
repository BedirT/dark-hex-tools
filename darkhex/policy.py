import typing
import darkhex.utils.util as util
import pyspiel
import os
from darkhex import *  # class vars


class Policy:

    def __init__(self,
                 policy,
                 board_size: typing.Tuple[int, int],
                 initial_state: str = None):
        """
        Initialize the policy.
        Args:
            policy: The policy.
            board_size: The board size.
        """
        if isinstance(policy, str):
            # setup all the parameters using the policy data
            self._load_policy(policy)
            CHECK.EQUAL_OR_N(self.board_size, board_size)
            CHECK.EQUAL_OR_N(self.initial_state, initial_state)
        else:
            if initial_state is None:
                self.initial_state = "P0 " + "".join(
                    ["." for _ in range(board_size[0] * board_size[1])])
            CHECK.INFO_STATE(self.initial_state)
            CHECK.BOARD_SIZE(board_size, initial_state)
            self.policy = policy
            self.board_size = board_size

        self.num_rows = self.board_size[0]
        self.num_cols = self.board_size[1]
        self.num_cells = self.num_rows * self.num_cols

    def get_action_prob(self, info_state: str) -> typing.Dict[int, float]:
        """
        Get the action probability dictionary for the given state.
        Args:
            info_state: The info state.
        
        Returns:
            The action probability dictionary.
        """
        raise NotImplementedError

    def get_action(self, info_state: str) -> int:
        """
        Take an action for the given state.
        Args:
            info_state: The info state.
        
        Returns:
            The action.
        """
        a_p = self.get_action_prob(info_state)
        return max(a_p, key=a_p.get)

    def _load_policy(self, policy_name: str) -> None:
        """
        Load the Policy data from the file.
        Args:
            policy_name (str): The policy_name name/folder path.
        """
        if policy_name not in os.listdir(util.PathVars.policies):
            path = policy_name
        else:
            path = util.PathVars.policies + policy_name + "/policy.pkl"
        data = util.load_file(path)
        self.policy = data.policy
        self.initial_state = data.initial_state
        self.board_size = data.board_size
        if data.player in [0, 1]:
            self.player = data.player

    def save_policy_to_file(self, policy_name: str) -> None:
        """
        Save the policy as a pickle to the file.

        Args:
            policy_name (str): The policy name.
        """
        data = util.dotdict(
            policy=self.policy,
            initial_state=self.initial_state,
            board_size=self.board_size,
            player=self.player if hasattr(self, "player") else None)
        path = util.PathVars.policies + policy_name + "/policy.pkl"
        log.info("Saved policy to path: " + path)


class TabularPolicy(Policy):

    def __init__(
        self,
        policy,
        board_size: typing.Tuple[int] = None,
        initial_state: str = None,
    ):
        """
        Setup a tabular policy. Any two player policy that has a tabular representation can be used.

        Args:
            policy (str or dict[str, dict[int, float]]): The policy name or a dictionary of action probability dictionary.
            board_size (list): The size of the board.
            initial_state (str): The initial state of the board.
        """
        super().__init__(policy, board_size, initial_state)

    def get_action_prob(self, info_state: str) -> typing.Dict[int, float]:
        """
        Get the action probability dictionary for the given state.
        Args:
            info_state: The info state.
        
        Returns:
            The action probability dictionary.
        """
        return self.policy[info_state]


class SinglePlayerTabularPolicy(TabularPolicy):

    def __init__(
        self,
        policy,
        board_size: typing.Tuple[int] = None,
        player: int = None,
        initial_state: str = None,
    ):
        """
        Setup a single player tabular policy. Any single player policy that has a tabular representation can be used.

        Args:
            policy (str or dict[str, dict[int, float]]): The policy name or a dictionary of action probability dictionary.
            board_size (list): The size of the board.
            player (int): The player the policy belongs to.
            initial_state (str): The initial state of the board.
        """
        super().__init__(policy, board_size, initial_state)
        if not self.player:
            self.player = player
        CHECK.PLAYER(self.player)
        self.opponent = 1 - player

    def get_action_prob(self, info_state: str) -> typing.Dict[int, float]:
        """
        Get the action probability dictionary for the given state.
        Args:
            info_state: The info state.
        
        Returns:
            The action probability dictionary.
        """
        CHECK.STATE_PLAYER(info_state, self.player)
        return self.policy[info_state]


class PyspielSolverPolicy(Policy):

    def __init__(self,
                 solver=None,
                 path=None,
                 board_size: typing.Tuple[int] = None,
                 initial_state: str = None):
        """
        Setup a pyspiel policy that uses a solver. A policy file that has a type where average
        policy can be accessed using a solver can be used.

        Args:
            solver (pyspiel.OutcomeSamplingMCCFRSolver or pyspiel.ExternalSamplingMCCFRSolver): 
                A pyspiel solver object.
            path (str): The path to the policy file. Cannot be used with solver.
            board_size (list): The size of the board.
            initial_state (str): The initial state of the board.
        """
        if (solver is None and path is None) or (solver is not None and
                                                 path is not None):
            raise ValueError("Either solver or path must be provided.")
        if solver is not None:
            self.solver = solver
            super().__init__(solver.average_policy(), board_size, initial_state)
        else:
            self._load_policy(path)

    def get_action_prob(
            self, pyspiel_state: pyspiel.State) -> typing.Dict[int, float]:
        """
        Get the action probability dictionary for the given pyspiel state.

        Args:
            pyspiel_state: The pyspiel state.

        Returns:
            The action probability dictionary.
        """
        return self.policy.action_probabilities(pyspiel_state)

    def get_action(self, pyspiel_state: pyspiel.State) -> int:
        """
        Get the action for the given pyspiel state.

        Args:
            pyspiel_state: The pyspiel state.

        Returns:
            (int) The action.
        """
        action_probs = self.get_action_prob(pyspiel_state)
        return max(action_probs, key=action_probs.get)

    def _load_policy(self, policy_path: str) -> None:
        """
        Load the Policy data from the file.
        Args:
            policy_path (str): The policy path/folder path.
        """
        if policy_path not in os.listdir(util.PathVars.policies):
            path = policy_path
        else:
            path = util.PathVars.policies + policy_path + "/policy.pkl"
        data = util.load_file(path)
        self.solver = data.solver
        self.initial_state = data.initial_state
        self.board_size = data.board_size
        self.policy = self.solver.average_policy()

    def save_policy_to_file(self, policy_name: str) -> None:
        """
        Save the policy as a pickle to the file.

        Args:
            policy_name (str): The policy name.
        """
        data = util.dotdict(
            solver=self.solver,
            initial_state=self.initial_state,
            board_size=self.board_size,
        )
        path = util.PathVars.policies + policy_name + "/policy.pkl"
        util.save_file(data, path)
        logger.info("Saved policy to path: " + path)


def convert_pyspiel_policy_to_darkhex_policy():
    """
    Convert a pyspiel policy to a darkhex policy.
    """
    pass
