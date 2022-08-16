import os
import typing
from copy import deepcopy

import dill
import numpy as np
import pyspiel
import darkhex.check as CHECK
import darkhex
from collections import Counter


class PathVars:
    """ The path data for common tasks. These variables are here to
    keep the saved file organized, please use them. """

    policies = "darkhex/data/policies/"
    all_states = "darkhex/data/all_states/"
    pone_states = "darkhex/data/pone_states/"


def position_from_coordinates(num_cols: int, row_idx:int, col_idx:int) -> int:
    """
    Converts a row and column (2d index) to a 1d index, position.

    Args:
        num_cols (int): The number of columns in the board.
        row_idx (int): The row index.
        col_idx (int): The column index.
    Returns:
        int: The 1d index.
    """
    return num_cols * row_idx + col_idx


def neighbour_indexes(cell: int, num_cols: int, num_rows: int) -> typing.List[typing.List[int]]:
    """
    Returns the neighbours of the given cell.

    Args:
        cell (int): The cell to get the neighbours of.
        num_cols (int): The number of columns in the board.
        num_rows (int): The number of rows in the board.
        
    Returns:
        list: The neighbours of the given cell. each element in the form of 
        [row_index, column_index].
    """
    row = cell // num_cols
    col = cell % num_cols
    CHECK.ROW_INDEX(row, num_rows)
    CHECK.COLUMN_INDEX(col, num_cols)

    positions = []
    if col + 1 < num_cols:
        positions.append(position_from_coordinates(num_cols, row, col + 1))
    if col - 1 >= 0:
        positions.append(position_from_coordinates(num_cols, row, col - 1))
    if row + 1 < num_rows:
        positions.append(position_from_coordinates(num_cols, row + 1, col))
        if col - 1 >= 0:
            positions.append(position_from_coordinates(num_cols, row + 1, col - 1))
    if row - 1 >= 0:
        positions.append(position_from_coordinates(num_cols, row - 1, col))
        if col + 1 < num_cols:
            positions.append(position_from_coordinates(num_cols, row - 1, col + 1))
    return positions


def board_after_action(board: str, action: int, player: int, num_rows: int, num_cols: int) -> str:
    """
    Update the board state with the new action.
    
    Args:
        board (str): The current board state to update the action on.
        action (int): The action to play.
        player (int): The player to play the action. Based on the player the stone
        to be placed will change.
        num_rows (int): The number of rows in the board.
        num_cols (int): The number of columns in the board.
    Returns:
        str: The new board state.
    """
    updated_board = list(deepcopy(board))
    CHECK.ACTION_BOARD(action, board)
    color = darkhex.cellState.kBlack if player == 0 else darkhex.cellState.kWhite
    # Update the board state with the move.
    if color == darkhex.cellState.kBlack:
        north_connected = False
        south_connected = False
        if action < num_cols:  # First row
            north_connected = True
        elif action >= num_cols * (num_rows - 1):  # Last row
            south_connected = True
        for neighbour in neighbour_indexes(action, num_cols, num_rows):
            if updated_board[neighbour] == darkhex.cellState.kBlackNorth:
                north_connected = True
            elif updated_board[neighbour] == darkhex.cellState.kBlackSouth:
                south_connected = True
        if north_connected and south_connected:
            updated_board[action] = darkhex.cellState.kBlackWin
        elif north_connected:
            updated_board[action] = darkhex.cellState.kBlackNorth
        elif south_connected:
            updated_board[action] = darkhex.cellState.kBlackSouth
        else:
            updated_board[action] = darkhex.cellState.kBlack
    elif color == darkhex.cellState.kWhite:
        east_connected = False
        west_connected = False
        if action % num_cols == 0:  # First column
            west_connected = True
        elif action % num_cols == num_cols - 1:  # Last column
            east_connected = True
        for neighbour in neighbour_indexes(action, num_cols, num_rows):
            if updated_board[neighbour] == darkhex.cellState.kWhiteWest:
                west_connected = True
            elif updated_board[neighbour] == darkhex.cellState.kWhiteEast:
                east_connected = True
        if east_connected and west_connected:
            updated_board[action] = darkhex.cellState.kWhiteWin
        elif east_connected:
            updated_board[action] = darkhex.cellState.kWhiteEast
        elif west_connected:
            updated_board[action] = darkhex.cellState.kWhiteWest
        else:
            updated_board[action] = darkhex.cellState.kWhite

    if updated_board[action] in [darkhex.cellState.kBlackWin, darkhex.cellState.kWhiteWin]:
        return updated_board[action]
    elif updated_board[action] not in [darkhex.cellState.kBlack, darkhex.cellState.kWhite]:
        # The action is connected to an edge but not a win position.
        # We need to use flood-fill to find the connected edges.
        flood_stack = [action]
        latest_cell = 0
        while len(flood_stack) != 0:
            latest_cell = flood_stack.pop()
            for neighbour in neighbour_indexes(latest_cell, num_cols, num_rows):
                if updated_board[neighbour] == color:
                    updated_board[neighbour] = updated_board[action]
                    flood_stack.append(neighbour)
        # Flood-fill is complete.
    # Convert list back to string
    return "".join(updated_board)


def load_file(filename: str) -> typing.Any:
    """
    Loads a file and returns the content.

    Args:
        filename (str): The filename to load.
    Returns:
        Any: The content of the file.
    """
    try:
        return dill.load(open(filename, "rb"))
    except IOError:
        raise IOError(f"File not found: {filename}")


def save_file(content: typing.Any, file_path: str) -> None:
    """
    Saves the content to the file_path.

    Args:
        content (Any): The content to save.
        file_path (str): The file path to save the content to.
    Returns:
        None
    """
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(file_path, "wb") as f:
        dill.dump(content, f)


def convert_position_to_alphanumeric(position: int, num_cols: int) -> str:
    """
    Converts a position of the board to an alphanumeric representation. 
    i.e. 0 -> a1, 1 -> a2

    Args:
        position (int): The position to convert.
        num_cols (int): The number of columns in the board.
    Returns:
        str: The alphanumeric representation of the position.
    """
    col = pos % num_cols
    row = pos // num_cols
    return "{}{}".format(chr(ord("a") + col), row + 1)


def convert_alphanumeric_to_position(alpha_numeric: str, num_cols: int) -> int:
    """
    Converts the action in the form of alpha-numeric row column sequence to
    numeric actions/position. i.e. a2 -> 2 for 3x3 board.
    
    Args:
        alpha_numeric (str): The alpha-numeric representation of the action.
        num_cols (int): The number of columns in the board.
    Returns:
        int: The numeric representation of the action.
    """
    # If not alpha-numeric, return the action as is.
    action = action.lower().strip()
    try:
        if not action[0].isalpha():
            return action
        row = int(action[1:])
        # for column a -> 0, b -> 1 ...
        col = ord(action[0]) - ord("a")
        return position_from_coordinates(num_cols, row, col)
    except ValueError:
        log.error("Invalid action: {}".format(action))
        return False


def convert_board_to_xo(board: str) -> str:
    """
    Board state, when play is going on, is represented by multiple characters
    based on the connection the pieces have. i.e. if a black stone is only connected
    to north edge the stone will be represented as y instead of x. This function 
    converts the board state to only x's and o's.

    Args:
        board (str): The board state to convert.
    Returns:
        str: The converted board state.
    """
    for p in darkhex.cellState.black_pieces:
        str_board = str_board.replace(p, darkhex.cellState.kBlack)
    for p in darkhex.cellState.white_pieces:
        str_board = str_board.replace(p, darkhex.cellState.kWhite)
    return str_board


def is_collusion_possible(board: str, player: int) -> bool:
    """
    Checks if a collusion is possible given the board state and player.
    
    Args:
        board (str): The board state to check.
        player (int): The player to check for collusion.
    Returns:
        bool: True if collusion is possible, False otherwise.
    """
    CHECK.PLAYER(player)
    count = Counter(board)
    if player == 1:
        player_pieces = sum(
            [s for x, s in count.items() if x in darkhex.cellState.white_pieces])
        opponent_pieces = sum(
            [s for x, s in count.items() if x in darkhex.cellState.black_pieces])
        return opponent_pieces <= player_pieces
    player_pieces = sum(
        [s for x, s in count.items() if x in darkhex.cellState.black_pieces])
    opponent_pieces = sum(
        [s for x, s in count.items() if x in darkhex.cellState.white_pieces])
    return opponent_pieces < player_pieces


def is_board_terminal(board: str, player: int) -> bool:
    """
    Checks if the board state is a terminal state.

    Todo: Have a terminal state lookup table.

    Args:
        board (str): The board state to check.
        player (int): The player to check for collusion.
    Returns:
        bool: True if the board state is a terminal state, False otherwise.
    """
    if (board.count(darkhex.cellState.kBlackWin) +
        board.count(darkhex.cellState.kWhiteWin) > 0):
        return True
    ct = Counter(board)
    empty_cells = ct[darkhex.cellState.kEmpty]
    if player == 0:
        opponent_pieces = sum(
            [s for x, s in ct.items() if x in darkhex.cellState.white_pieces])
        player_pieces = sum(
            [s for x, s in ct.items() if x in darkhex.cellState.black_pieces])
        if opponent_pieces + empty_cells == player_pieces:
            return True
    else:
        opponent_pieces = sum(
            [s for x, s in ct.items() if x in darkhex.cellState.black_pieces])
        player_pieces = sum(
            [s for x, s in ct.items() if x in darkhex.cellState.white_pieces])
        if opponent_pieces + empty_cells == player_pieces + 1:
            return True
    return False


def get_board_from_info_state(info_state: str) -> str:
    """
    Gets the board state from the info state. Information states are in the form
    of "P{player} board". We extract the board state from the info state.
    
    Args:
        info_state (str): The info state to get the board state from.
    Returns:
        str: The board state.
    """
    return info_state.split(" ")[1]


def get_info_state_from_board(board: str, player: int) -> str:
    """
    Gets the info state from the board state. Information states are in the form
    of "P{player} board". We use the board and the player information to create
    the info state.

    Args:
        board (str): The board state to get the info state from.
        player (int): The player to get the info state from.
    Returns:
        str: The info state.
    """
    return "P{} {}".format(player, board)


def convert_os_str(str_board: str, num_cols: int, player: int = -1):
    """
    Convert the board state to pyspiel format.
    ie. P{player} firstrowsecondrow
    """
    if player == -1:
        new_board = ""
    else:
        new_board = f"P{player} "
    for i, cell in enumerate(str_board):
        if cell in darkhex.cellState.black_pieces:
            new_board += darkhex.cellState.kBlack
        elif cell in darkhex.cellState.white_pieces:
            new_board += darkhex.cellState.kWhite
        else:
            new_board += darkhex.cellState.kEmpty
    return new_board


def convert_os_strategy(strategy: dict, num_cols: int, player: int) -> dict:
    """
    Convert the strategy from open_spiel to the format of the game.
    """
    new_strat = {}
    for board_state, actions in strategy.items():
        new_strat[convert_os_str(board_state, num_cols, player)] = actions
    return new_strat


class dotdict(dict):
    """dict with dot access"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    __type__ = dict

    def __init__(self, d=None, **kwargs):
        if d is None:
            d = {}
        dict.__init__(self, d, **kwargs)
        self.__dict__ = self

    # class returns a new instance of itself
    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)


def safe_normalize(y, out=None):
    """
    Returns +y+/||+y+||_1 or indmax y if ||+y+||_1 = 0.

    Assumes that +y+ >= 0.
    """
    if out is None:
        out = y.copy()
    z = np.sum(y)
    if z > 0:
        out[:] = y / z
    else:
        a = y.argmax()
        out[:] = 0
        out[a] = 1.
    return out


def flood_fill(state: list, init_pos: int, num_rows: int,
               num_cols: int) -> list:
    player = darkhex.cellState.kBlack \
        if state[init_pos] in darkhex.cellState.black_pieces \
        else darkhex.cellState.kWhite
    flood_stack = [init_pos]
    while len(flood_stack) > 0:
        latest_cell = flood_stack.pop()
        for n in neighbour_indexes(latest_cell, num_cols, num_rows):
            if state[n] == player:
                state[n] = state[latest_cell]
                flood_stack.append(n)
    return state


def convert_to_infostate(board_state: str, player: int) -> str:
    board_ls = list(board_state)
    board_ls.insert(0, "P{} ".format(player))
    return "".join(board_ls)


def report(data, type: str) -> None:
    """ Prints the report in a pretty format given the data
    and the type. Valid types are = ['memory', 'time']

    Time: Output of time.time()
    Memory: Output of process.memory_info().rss
    """
    bold = "\033[1m"
    red = "\033[1;31m"
    yellow = "\033[1;33m"
    green = "\033[1;32m"
    end = "\033[0m"
    if type == 'memory':
        print(f"{bold}{green}Memory usage:\t{end}", end='')
        gbs = data // (1024**2)
        mbs = (data - gbs * 1024**2) // 1024
        kbs = (data - gbs * 1024**2 - mbs * 1024)
        if gbs > 0:
            print(f"{gbs} {red}GB{end} ", end='')
        if mbs > 0:
            print(f"{mbs} {red}MB{end} ", end='')
        if kbs > 0:
            print(f"{kbs} {red}KB{end}", end='')
        print()
    elif type == 'time':
        print(f"{bold}{green}Time taken:\t{end}", end="")
        m, s = divmod(data, 60)
        h, m = divmod(m, 60)
        h, m, s = int(h), int(m), int(s)
        if h > 0:
            print(f"{h}:{m:02d}:{s:02d} {yellow}hours{end}")
        elif m > 0:
            print(f"{m}:{s:02d} {yellow}minutes{end}")
        else:
            print(f"{s:02d} {yellow}seconds{end}")
    else:
        print(
            f"{red}{bold}Invalid type given to report(). Valid types are = ['memory', 'time']{end}"
        )


# ! THIS SHOULD NOT BE NEEDED CORRECT EVERYTHING THAT USES THIS
def convert(strategy, num_cols, num_rows, pid):
    """Converts strategies with old info_state representation
    ie. 'yyq.yqyqx...' to new representation ie. for player_id=0
    'P0 xxo.xoxox...'
    """
    new_strategy = {}
    for info_state, actions in strategy.items():
        new_info_state = convert_os_str(info_state, num_cols, player=pid)
        assert (len(new_info_state) == num_cols * num_rows + 3)
        new_strategy[new_info_state] = actions
    return new_strategy
