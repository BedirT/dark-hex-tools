import os
import typing
from copy import deepcopy
from collections import Counter
import dill
import numpy as np

from darkhex import cellState
import darkhex.check as CHECK
from darkhex import logger as log


class dotdict(dict):
    """New data structure that allows for dot notation to access dictionary values."""
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


class PathVars:
    """ The path data for common tasks. These variables are here to
    keep the saved file organized, please use them. """

    policies = "darkhex/data/policies/"
    all_states = "darkhex/data/all_states/"
    pone_states = "darkhex/data/pone_states/"
    game_trees = "darkhex/data/game_trees/"


def position_from_coordinates(num_cols: int, row_idx: int, col_idx: int) -> int:
    """
    Converts a row and column (2d index) to a 1d index, position.

    Args:
        num_cols (int): The number of columns in the board.
        row_idx (int): The row index.
        col_idx (int): The column index.
    Returns:
        int: The 1d index.
    """
    if col_idx < 0 or col_idx >= num_cols:
        raise ValueError("Invalid column index")
    if row_idx < 0:
        raise ValueError("Invalid row index")
    return num_cols * row_idx + col_idx


def neighbour_indexes(cell: int, num_cols: int,
                      num_rows: int) -> typing.List[typing.List[int]]:
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
            positions.append(
                position_from_coordinates(num_cols, row + 1, col - 1))
    if row - 1 >= 0:
        positions.append(position_from_coordinates(num_cols, row - 1, col))
        if col + 1 < num_cols:
            positions.append(
                position_from_coordinates(num_cols, row - 1, col + 1))
    return positions


def board_after_action(board: str, action: int, player: int) -> str:
    """
    Update the board state with the new action.
    
    Args:
        board (str): The current board state to update the action on. [layered, xo]
        action (int): The action to play.
        player (int): The player to play the action. Based on the player the stone
        to be placed will change.
        num_rows (int): The number of rows in the board.
        num_cols (int): The number of columns in the board.
    Returns:
        str: The new board state.
    """
    stone = cellState.kBlack if player == 0 else cellState.kWhite
    num_cols = board.find("\n")
    board_flat = layered_board_to_flat(board)
    if board_flat[action] != cellState.kEmpty:
        return False
    board_flat = board_flat[:action] + stone + board_flat[action + 1:]
    board_layered = flat_board_to_layered(board_flat, num_cols)
    log.debug(board_layered)
    return convert_xo_to_board(board_layered)


def load_file(file_path: str) -> typing.Any:
    """
    Loads a file and returns the content.

    Args:
        file_path (str): The path to load from.
    Returns:
        Any: The content of the file.
    """
    try:
        return dill.load(open(file_path, "rb"))
    except IOError:
        raise IOError(f"File not found: {file_path}")


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
    i.e. 0 -> a1, 1 -> b1

    Args:
        position (int): The position to convert.
        num_cols (int): The number of columns in the board.
    Returns:
        str: The alphanumeric representation of the position.
    """
    col = position % num_cols
    row = position // num_cols
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
    action = alpha_numeric.lower().strip()
    try:
        if not action[0].isalpha():
            return int(action)
        row = int(action[1:]) - 1
        # for column a -> 0, b -> 1 ...
        col = ord(action[0]) - ord("a")
        return position_from_coordinates(num_cols, row, col)
    except ValueError:
        log.error("Invalid action: {}".format(action))
        raise ValueError("Invalid action: {}".format(action))


def convert_board_to_xo(board: str) -> str:
    """
    Board state, when play is going on, is represented by multiple characters
    based on the connection the pieces have. i.e. if a black stone is only connected
    to north edge the stone will be represented as y instead of x. This function 
    converts the board state to only x's and o's.

    Args:
        board (str): The board state to convert. [:, connection]
    Returns:
        str: The converted board state. [:, xo]
    """
    for p in cellState.black_pieces:
        board = board.replace(p, cellState.kBlack)
    for p in cellState.white_pieces:
        board = board.replace(p, cellState.kWhite)
    return board


def convert_xo_to_board(board_in_xo: str) -> str:
    """
    Converts the board cells to location values as in cellState, from xo notation.
    i.e. North connected x will be converted to y.
    
    Uses flood fill to be able to determine the connections.

    Args:
        board_in_xo (str): The board state to convert. [layered, xo]
    Returns:
        str: The converted board state [layered, connection]
    """
    num_cols = board_in_xo.find("\n")
    num_rows = board_in_xo.count("\n") + 1

    def flood_fill(state: list, init_pos: int, num_rows: int,
                   num_cols: int) -> list:
        if state[init_pos] in cellState.black_pieces:
            player = cellState.kBlack
            opposite_type = cellState.kBlackSouth if state[
                init_pos] == cellState.kBlackNorth else cellState.kBlackNorth
        elif state[init_pos] in cellState.white_pieces:
            player = cellState.kWhite
            opposite_type = cellState.kWhiteEast if state[
                init_pos] == cellState.kWhiteWest else cellState.kWhiteWest
        flood_stack = [init_pos]
        while len(flood_stack) > 0:
            latest_cell = flood_stack.pop()
            for n in neighbour_indexes(latest_cell, num_cols, num_rows):
                if state[n] == player:
                    state[n] = state[latest_cell]
                    flood_stack.append(n)
                elif state[n] == opposite_type:
                    state[
                        n] = cellState.kBlackWin if player == cellState.kBlack else cellState.kWhiteWin
        return state

    # first row
    board_as_list = list(layered_board_to_flat(board_in_xo))
    log.debug(board_as_list)
    for i in range(num_cols):
        if board_as_list[i] in cellState.black_pieces:
            board_as_list[i] = cellState.kBlackNorth
            board_as_list = flood_fill(board_as_list, i, num_rows, num_cols)
    # last row
    for i in range(num_rows * num_cols - num_cols, num_rows * num_cols):
        if board_as_list[i] in cellState.black_pieces:
            board_as_list[i] = cellState.kBlackSouth
            board_as_list = flood_fill(board_as_list, i, num_rows, num_cols)
    # first column
    for i in range(0, num_rows * num_cols, num_cols):
        if board_as_list[i] in cellState.white_pieces:
            board_as_list[i] = cellState.kWhiteWest
            board_as_list = flood_fill(board_as_list, i, num_rows, num_cols)
    # last column
    for i in range(num_rows * num_cols - 1, -1, -num_cols):
        if board_as_list[i] in cellState.white_pieces:
            board_as_list[i] = cellState.kWhiteEast
            board_as_list = flood_fill(board_as_list, i, num_rows, num_cols)
    return flat_board_to_layered("".join(board_as_list), num_cols)


def is_collusion_possible(board: str, player: int) -> bool:
    """
    Checks if a collusion is possible given the board state and player.
    
    Args:
        board (str): The board state to check. [:, :]
        player (int): The player to check for collusion.
    Returns:
        bool: True if collusion is possible, False otherwise.
    """
    CHECK.PLAYER(player)
    count = Counter(board)
    if player == 1:
        player_pieces = sum(
            [s for x, s in count.items() if x in cellState.white_pieces])
        opponent_pieces = sum(
            [s for x, s in count.items() if x in cellState.black_pieces])
        return opponent_pieces <= player_pieces
    player_pieces = sum(
        [s for x, s in count.items() if x in cellState.black_pieces])
    opponent_pieces = sum(
        [s for x, s in count.items() if x in cellState.white_pieces])
    return opponent_pieces < player_pieces


def is_board_terminal(board: str, player: int) -> bool:
    """
    Checks if the board is in a terminal state by looking at the number of
    pieces or if there is a connection. Works with player boards. Functions
    both with xo and connection boards.

    Args:
        board (str): The board state to check / Can also be single item string
        in the case of updated_board returns [:, connection]
        player (int): The player to check for collusion.
    Returns:
        bool: True if the board state is a terminal state, False otherwise.
    """
    if (board.count(cellState.kBlackWin) + board.count(cellState.kWhiteWin) >
            0):
        return True

    # Checking the number of pieces on the board for end game.
    ct = Counter(board)
    empty_cells = ct[cellState.kEmpty]
    if player == 0:
        opponent_pieces = sum(
            [s for x, s in ct.items() if x in cellState.white_pieces])
        player_pieces = sum(
            [s for x, s in ct.items() if x in cellState.black_pieces])
        if opponent_pieces + empty_cells == player_pieces:
            return True
    else:
        opponent_pieces = sum(
            [s for x, s in ct.items() if x in cellState.black_pieces])
        player_pieces = sum(
            [s for x, s in ct.items() if x in cellState.white_pieces])
        if opponent_pieces + empty_cells == player_pieces + 1:
            return True
    return False


def get_board_from_info_state(info_state: str,
                              perfect_recall: bool = False) -> str:
    """
    Gets the board state from the info state. The info state can be either in the
    perfect recall format or the imperfect recall format. Returned board is always
    in xo format.
    
    Args:
        info_state (str): The info state to get the board state from.
        perfect_recall (bool): If true, the perfect recall is used.
    Returns:
        str: The board state. [layered, xo]
    """
    split_items = info_state.split("\n")
    if perfect_recall:
        if split_items[-1] == "":
            split_items.pop()
            return "\n".join(split_items[1:])
        return "\n".join(split_items[1:-1])
    return "\n".join(split_items[1:])


def get_imperfect_recall_state(player: int, board: str) -> str:
    """
    Gets the imperfect recall state from the board state.
    
    Args:
        player (int): The player to get the imperfect recall state from.
        board (str): The board state to get the imperfect recall state from. [layered, connection]
    Returns:
        str: The imperfect recall state.
    """
    CHECK.PLAYER(player)
    board_state = convert_board_to_xo(board)
    return "P{}\n{}".format(player, board)


def get_perfect_recall_state(player: int, board: str,
                             action_sequence: typing.List[int]) -> str:
    """
    Gets the perfect recall state from the board state and action sequence.
    
    Args:
        player (int): The player to get the perfect recall state from.
        board (str): The board state to get the perfect recall state from. [layered, connection]
        action_sequence (typing.List[int]): The action sequence to get the perfect recall state from.
    Returns:
        str: The perfect recall state.
    """
    CHECK.PLAYER(player)
    str_action_seq = "".join(
        [f"{player},{action} " for action in action_sequence])
    board = convert_board_to_xo(board)
    return "P{}\n{}\n{}".format(player, board, str_action_seq)


def get_info_state_from_board(board: str,
                              player: int,
                              action_history: typing.List[int] = None,
                              perfect_recall: bool = False) -> str:
    """
    Gets the info state from the board state. Information states are in the form
    of "P{player} board". We use the board and the player information to create
    the info state.

    Args:
        board (str): The board state to get the info state from. [layered, connection]
        player (int): The player to get the info state from.
        action_history (typing.List[int]): The action history to get the info state from. (only for perfect recall)
        perfect_recall (bool): If true, the perfect recall is used.
    Returns:
        str: The info state.
    """
    if perfect_recall:
        if action_history is None:
            raise ValueError(
                "action_history must be provided for perfect recall")
        return get_perfect_recall_state(player, board, action_history)
    return get_imperfect_recall_state(player, board)


def layered_board_to_flat(board: str) -> str:
    """
    Converts a layered board to a flat board. Layered board has a newline character
    between each row, and flat board has no newline characters.
    
    Args:
        board (str): The board state to get the flat board from. [layered, :]
    Returns:
        str: The flat board. [flat, :]
    """
    return board.replace("\n", "")


def flat_board_to_layered(board: str, num_cols: int) -> str:
    """
    Converts a flat board to a layered board. Flat board has no newline characters,
    and layered board has a newline character between each row.
    
    Args:
        board (str): The board state to get the layered board from. [flat, :]
        num_cols (int): The number of columns in the board.
    Returns:
        str: The layered board. [layered, :]
    """
    assert len(board) % num_cols == 0, "Board is not a multiple of num_cols"
    return "\n".join(
        board[i:i + num_cols] for i in range(0, len(board), num_cols))


def policy_dict_to_policy_tuple(
    policy_dict: typing.Dict[str, typing.Dict[int, float]]
) -> typing.Dict[str, typing.List[typing.Tuple[int, float]]]:
    """
    Converts a policy dictionary to a policy tuple.
    
    Args:
        policy_dict (typing.Dict[str, typing.Dict[int, float]]): The policy dictionary to convert.
    Returns:
    """
    return {k: list(v.items()) for k, v in policy_dict.items()}


def policy_tuple_to_policy_dict(
    policy_tuple: typing.Dict[str, typing.List[typing.Tuple[int, float]]]
) -> typing.Dict[str, typing.Dict[int, float]]:
    """
    Converts a policy tuple to a policy dictionary.
    
    Args:
        policy_tuple (typing.Dict[str, typing.Tuple[int, float]]): The policy tuple to convert.
    Returns:
    """
    return {k: dict(v) for k, v in policy_tuple.items()}


def get_all_states(board_size: typing.Tuple[int, int]) -> dict:
    """
    Returns a dictionary of all possible states for Imperfect Recall
    version of the game for given board size.

    Args: 
        board_size: Tuple of board size.
    Returns:
        dict: Dictionary of all possible states.
    """
    return util.load_file(
        f"{util.PathVars.all_states}{board_size[0]}x{board_size[1]}.pkl")


def is_valid_action(board: str, action: int) -> bool:
    """
    Checks if the action is valid for the board.
    
    Args:
        board (str): The board to check the action on. [:, :]
        action (int): The action to check.
    Returns:
        bool: True if the action is valid, False otherwise.
    """
    if board.find('\n') != -1:
        board = layered_board_to_flat(board)
    return action >= 0 and action < len(
        board) and board[action] == cellState.kEmpty


def get_random_action(board: str) -> int:
    """
    Returns a random action for the board.
    
    Args:
        board (str): The board to get the random action from. [:, :]
    Returns:
        int: The random action. Returns -1 if no action is valid.
    """
    if board.find('\n') != -1:
        board = layered_board_to_flat(board)
    legal_actions = [
        i for i in range(len(board)) if board[i] == cellState.kEmpty
    ]
    if len(legal_actions) == 0:
        return -1
    return np.random.choice(legal_actions)


def info_state_after_action(info_state: str,
                            action: int,
                            player_stone: int,
                            is_perfect_recall: bool = False) -> str:
    """
    Update the info_state with the new action.
    
    Args:
        info_state (str): The current info_state. 
        action (int): The action to play.
        player (int): The player to play the action. Based on the player the stone
        to be placed will change.
        is_perfect_recall (bool): If true, the action will be played on the 
        perfect recall info_state.
    Returns:
        str: The new board state.
    """
    board = get_board_from_info_state(info_state, is_perfect_recall)
    state_player = get_player_from_info_state(info_state)
    board = board_after_action(board, action, player_stone)
    action_history = get_action_history(info_state)
    return get_info_state_from_board(board,
                                     state_player,
                                     action_history + [action],
                                     is_perfect_recall)


def get_random_action_for_info_state(info_state: str) -> int:
    """
    Returns a random action for the info_state.
    
    Args:
        info_state (str): The info_state to get the random action from.
    Returns:
        int: The random action. Returns -1 if no action is valid.
    """
    board = get_board_from_info_state(info_state)
    return get_random_action(board)


def is_valid_action_from_info_state(info_state: str, action: int) -> bool:
    """
    Checks if the action is valid for the info_state.
    
    Args:
        info_state (str): The info_state to check the action on.
        action (int): The action to check.
    Returns:
        bool: True if the action is valid, False otherwise.
    """
    board = get_board_from_info_state(info_state)
    return is_valid_action(board, action)


def is_collusion_possible_info_state(info_state: str) -> bool:
    """
    Checks if collusion is possible for the info_state.
    
    Args:
        info_state (str): The info_state to check collusion on.
    Returns:
        bool: True if collusion is possible, False otherwise.
    """
    board = get_board_from_info_state(info_state)
    player = get_player_from_info_state(info_state)
    return is_collusion_possible(board, player)


def get_action_history(info_state: str) -> typing.List[int]:
    """
    Returns the action history for the info_state. Only works for
    perfect recall info_states.
    
    Args:
        info_state (str): The info_state to get the action history from.
    Returns:
        typing.List[int]: The action history.
    """
    # 0,1 0,2 0,3 -> [1, 2, 3]
    player_action_pairs = info_state.split('\n')[-1]
    if not player_action_pairs:
        return []
    action_pairs = player_action_pairs.split(' ')[:-1]
    log.debug(action_pairs)
    return [int(action_pair.split(',')[1]) for action_pair in action_pairs]


def get_player_from_info_state(info_state: str) -> int:
    """
    Returns the player from the info_state.
    
    Args:
        info_state (str): The info_state to get the player from.
    Returns:
        int: The player.
    """
    return int(info_state[1])


def is_info_state_terminal(info_state: str, perfect_recall = False) -> bool:
    """
    Checks if the info_state is terminal.
    
    Args:
        info_state (str): The info_state to check.
    Returns:
        bool: True if the info_state is terminal, False otherwise.
    """
    board = get_board_from_info_state(info_state, perfect_recall)
    player = get_player_from_info_state(info_state)
    board = convert_xo_to_board(board)
    return is_board_terminal(board, player)