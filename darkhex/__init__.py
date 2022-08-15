import typing
import darkhex.utils.util as util
import logging


class CustomFormatter(logging.Formatter):

    # colors
    grey = "\x1b[38;5;242m"
    yellow = "\x1b[38;5;11m"
    red = "\x1b[38;5;9m"
    green = "\x1b[38;5;10m"
    blue = "\x1b[38;5;12m"
    bold = "\x1b[1m"
    reset = "\x1b[0m"

    format_temp = "[%(asctime)s] %(name)s/%(levelname)s: %(message)s (%(filename)s:%(lineno)d)"

    formats = {
        logging.DEBUG: bold + green + format_temp + reset,
        logging.INFO: grey + format_temp + reset,
        logging.WARNING: bold + yellow + format_temp + reset,
        logging.ERROR: red + format_temp + reset,
        logging.CRITICAL: bold + red + format_temp + reset
    }

    def format(self, record):
        log_fmt = self.formats.get(record.levelno, self.format_temp)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


# Logger configuration
logger = logging.getLogger("darkhex")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(CustomFormatter())

logger.addHandler(console_handler)
###


class CHECK:
    """ Validity checks for the library. """

    @staticmethod
    def EQUAL(a: typing.Any, b: typing.Any):
        """
        Check if two objects are equal.
        
        Args:
            a (typing.Any): The first object.
            b (typing.Any): The second object.
        """
        if a != b:
            raise ValueError(f"{a} != {b}")

    @staticmethod
    def EQUAL_OR_N(a: typing.Any, b: typing.Any) -> None:
        """
        Check if two objects are equal or None.
        
        Args:
            a (typing.Any): The first object.
            b (typing.Any): The second object.
        """
        if a != b and a is not None and b is not None:
            raise ValueError(f"{a} != {b} with None")

    @staticmethod
    def TABULAR_POLICY(policy: dict) -> None:
        """
        Check if the policy is valid. 
            - Type should be dict[str, dict[int, float]]
            - The keys of the dictionary should be valid info_states
            - The values of the dictionary should be valid action probabilities
        
        ! We do not check for legal actions for states given.  
        
        Args:
            policy (dict): The policy to check.
        """
        if not isinstance(policy, dict):
            raise ValueError(f"{policy} is not a dictionary")
        for info_state, action_probabilities in policy.items():
            self.INFO_STATE(info_state)
            self.ACTION_PROBABILITIES(action_probabilities)

    @staticmethod
    def INFO_STATE(info_state: str) -> None:
        """
        Check if the info_state is valid. 
            - Type should be str
            - The info_state should begin with 'Px' where x is the player (0/1), and 
            continue with a space and then the board representation.
            - The board should be a valid board:
                - Only contains values from the set: {'.', 'x', 'o', 'X', 'O', 'y', 'z', 'p', 'q'}
                - Number of white stones are less than or equal to the number of
                  black stones
        TODO: Complete the board checks.

        Args:
            board (str): The board to check.
        """
        if not isinstance(info_state, str):
            raise ValueError(f"{info_state} is not a string")
        if not info_state.startswith("P"):
            raise ValueError(f"{info_state} does not start with 'P'")

    @staticmethod
    def BOARD_SIZE(board_size: typing.Tuple[int], state: str) -> None:
        """
        Check if the board size matches the state.

        TODO: Complete the board checks.

        Args:
            board_size (typing.Tuple[int]): The board size.
            state (str): The state.
        """
        if not isinstance(board_size, tuple):
            raise ValueError(f"{board_size} is not a tuple")
        if len(board_size) != 2:
            raise ValueError(f"{board_size} is not a tuple of length 2")
        if not isinstance(board_size[0], int):
            raise ValueError(f"{board_size[0]} is not an int")
        if not isinstance(board_size[1], int):
            raise ValueError(f"{board_size[1]} is not an int")
        if board_size[0] <= 0:
            raise ValueError(f"{board_size[0]} is not a positive int")
        if board_size[1] <= 0:
            raise ValueError(f"{board_size[1]} is not a positive int")
        # if util.board_from_info_state(state) != board_size[0] * board_size[1]:
        #     raise ValueError(f"{state} is not the correct length")

    @staticmethod
    def PLAYER(player: int) -> None:
        """
        Check if the player is valid.
            - Type should be int
            - The player should be 0 or 1
        
        Args:
            player (int): The player to check.
        """
        if not isinstance(player, int):
            raise ValueError(f"{player} is not an int")
        if player not in [0, 1]:
            raise ValueError(f"{player} is not 0 or 1")

    @staticmethod
    def ACTION_PROBABILITIES(
            action_probabilities: typing.Dict[int, float]) -> None:
        """
        Check if the action probabilities are valid.
            - Type should be dict[int, float]
            - The keys of the dictionary should be valid actions
            - The values of the dictionary should be valid probabilities
        
        Args:
            action_probabilities (dict): The action probabilities to check.
        """
        if not isinstance(action_probabilities, dict):
            raise ValueError(f"{action_probabilities} is not a dictionary")
        for action, probability in action_probabilities.items():
            self.PROBABILITY(probability)
            self.ACTION(action)

    @staticmethod
    def PROBABILITY(probability: float) -> None:
        """
        Check if the probability is valid.
            - Type should be float
            - The probability should be between 0 and 1
        
        Args:
            probability (float): The probability to check.
        """
        if not isinstance(probability, float):
            raise ValueError(f"{probability} is not a float")
        if probability < 0 or probability > 1:
            raise ValueError(f"{probability} is not between 0 and 1")

    @staticmethod
    def ACTION(action: int) -> None:
        """
        Check if the action is valid.
            - Type should be a positive int
        
        Args:
            action (int): The action to check.
        """
        if not isinstance(action, int):
            raise ValueError(f"{action} is not an int")
        if action < 0:
            raise ValueError(f"{action} is not a positive int")
