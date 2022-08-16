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


class cellState:
    kEmpty = "."
    kBlack = "x"
    kWhite = "o"
    kBlackWin = "X"
    kWhiteWin = "O"
    kBlackNorth = "y"
    kBlackSouth = "z"
    kWhiteWest = "p"
    kWhiteEast = "q"

    white_pieces = [kWhite, kWhiteEast, kWhiteWest, kWhiteWin]
    black_pieces = [kBlack, kBlackNorth, kBlackSouth, kBlackWin]


def get_all_states(board_size: typing.Tuple[int, int]) -> dict:
    """
    Returns a dictionary of all possible states for Imperfect Recall
    version of the game for given board size.

    Args: 
        board_size: Tuple of board size.
    """
    return util.load_file(
        f"{util.PathVars.all_states}{board_size[0]}x{board_size[1]}.pkl")