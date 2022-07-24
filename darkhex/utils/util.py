import os
from copy import deepcopy

import dill
import numpy as np
import pyspiel
from darkhex.utils.cell_state import cellState


def cell_connections(cell, num_cols, num_rows):
    """
    Returns the neighbours of the given cell.

    args:
        cell    - The location on the board to check the neighboring cells for.

    returns:
        positions   - List of all the neighbouring cells to the cell.
                    Elements are in the format [row, column].
    """
    row = cell // num_cols
    col = cell % num_cols

    positions = []
    if col + 1 < num_cols:
        positions.append(pos_by_coord(num_cols, row, col + 1))
    if col - 1 >= 0:
        positions.append(pos_by_coord(num_cols, row, col - 1))
    if row + 1 < num_rows:
        positions.append(pos_by_coord(num_cols, row + 1, col))
        if col - 1 >= 0:
            positions.append(pos_by_coord(num_cols, row + 1, col - 1))
    if row - 1 >= 0:
        positions.append(pos_by_coord(num_cols, row - 1, col))
        if col + 1 < num_cols:
            positions.append(pos_by_coord(num_cols, row - 1, col + 1))
    return positions


def game_over(board_state):
    """
    Check if the game is over.

    - board_state: The current refree board state.
    """
    return (board_state.count(cellState.kBlackWin) +
            board_state.count(cellState.kWhiteWin) == 1)


def updated_board(board_state, cell, color, num_rows, num_cols):
    """
    Update the board state with the move.

    - board_state: The current board state.
    - move: The move to be made. (int)
    - piece: The piece to be placed on the board.
    """
    # Work on a list version of the board state.
    updated_board_state = list(deepcopy(board_state))
    # If the move is illegal return false.
    # - Illegal if the move is out of bounds.
    # - Illegal if the move is already taken.
    if (cell < 0 or cell >= len(updated_board_state) or
            updated_board_state[cell] != cellState.kEmpty):
        return False
    # Update the board state with the move.
    if color == cellState.kBlack:
        north_connected = False
        south_connected = False
        if cell < num_cols:  # First row
            north_connected = True
        elif cell >= num_cols * (num_rows - 1):  # Last row
            south_connected = True
        for neighbour in cell_connections(cell, num_cols, num_rows):
            if updated_board_state[neighbour] == cellState.kBlackNorth:
                north_connected = True
            elif updated_board_state[neighbour] == cellState.kBlackSouth:
                south_connected = True
        if north_connected and south_connected:
            updated_board_state[cell] = cellState.kBlackWin
        elif north_connected:
            updated_board_state[cell] = cellState.kBlackNorth
        elif south_connected:
            updated_board_state[cell] = cellState.kBlackSouth
        else:
            updated_board_state[cell] = cellState.kBlack
    elif color == cellState.kWhite:
        east_connected = False
        west_connected = False
        if cell % num_cols == 0:  # First column
            west_connected = True
        elif cell % num_cols == num_cols - 1:  # Last column
            east_connected = True
        for neighbour in cell_connections(cell, num_cols, num_rows):
            if updated_board_state[neighbour] == cellState.kWhiteWest:
                west_connected = True
            elif updated_board_state[neighbour] == cellState.kWhiteEast:
                east_connected = True
        if east_connected and west_connected:
            updated_board_state[cell] = cellState.kWhiteWin
        elif east_connected:
            updated_board_state[cell] = cellState.kWhiteEast
        elif west_connected:
            updated_board_state[cell] = cellState.kWhiteWest
        else:
            updated_board_state[cell] = cellState.kWhite

    if updated_board_state[cell] in [cellState.kBlackWin, cellState.kWhiteWin]:
        return updated_board_state[cell]
    elif updated_board_state[cell] not in [cellState.kBlack, cellState.kWhite]:
        # The cell is connected to an edge but not a win position.
        # We need to use flood-fill to find the connected edges.
        flood_stack = [cell]
        latest_cell = 0
        while len(flood_stack) != 0:
            latest_cell = flood_stack.pop()
            for neighbour in cell_connections(latest_cell, num_cols, num_rows):
                if updated_board_state[neighbour] == color:
                    updated_board_state[neighbour] = updated_board_state[cell]
                    flood_stack.append(neighbour)
        # Flood-fill is complete.
    # Convert list back to string
    return "".join(updated_board_state)


def replace_action(board, action, new_value):
    """
    Replaces the action on the board with the new value.
    """
    new_board = list(deepcopy(board))
    new_board[action] = new_value
    return "".join(new_board)


def play_action(game, player, action):
    """
    Plays the action on the game board.
    """
    new_game = deepcopy(game)
    if new_game["board"][action] != cellState.kEmpty:
        opponent = cellState.kBlack if player == cellState.kWhite else cellState.kWhite
        new_game["boards"][player] = replace_action(new_game["boards"][player],
                                                    action, opponent)
        return new_game, True
    else:
        res = updated_board(new_game["board"], action, player, game["num_cols"],
                            game["num_rows"])
        if res == cellState.kBlackWin or res == cellState.kWhiteWin:
            # The game is over.
            return res, False
        new_game["board"] = res
        new_game["boards"][player] = replace_action(new_game["boards"][player],
                                                    action,
                                                    new_game["board"][action])
        s = ""
        opponent = cellState.kBlack if player == cellState.kWhite else cellState.kWhite
        for r in new_game["boards"][player]:
            if r in cellState.black_pieces:
                s += cellState.kBlack
            elif r in cellState.white_pieces:
                s += cellState.kWhite
            else:
                s += r
        new_game["boards"][player] = s
        return new_game, False


def load_file(filename):
    """
    Loads a file and returns the content.
    """
    try:
        return dill.load(open(filename, "rb"))
    except IOError:
        raise IOError(f"File not found: {filename}")


def save_file(content, file_path):
    """
    Saves the content to a file.
    """
    # Create the directory if it doesn't exist.
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    dill.dump(content, open(file_path, "wb"))


def pos_by_coord(num_cols, r, c):
    return num_cols * r + c


def conv_alphapos(pos, num_cols):
    """
    Converts a position to a letter and number
    pos: int
    """
    col = pos % num_cols
    row = pos // num_cols
    return "{}{}".format(chr(ord("a") + col), row + 1)


def greedify(strategy, multiple_actions_allowed=False):
    """
    Greedifies the given strategy. -1 is the minumum value and 1 is the maximum.
    Args:
        strategy: The strategy to greedify.
        multiple_actions_allowed: Whether multiple actions are allowed.
    Returns:
        A greedified version of the strategy.
    """
    greedy_strategy = {}
    for board_state, action_val in strategy.items():
        mx_value = -1
        actions = []
        for action, value in action_val.items():
            if value > mx_value:
                mx_value = value
                actions = [action]
            elif value == mx_value and multiple_actions_allowed:
                actions.append(action)
        greedy_strategy[board_state] = [
            (actions[i], 1 / len(actions)) for i in range(len(actions))
        ]
    return greedy_strategy


def calculate_turn(state: str):
    """
    Calculates which player's turn it is given board state.
    """
    num_black = 0
    num_white = 0
    for cell in state:
        if cell in cellState.black_pieces:
            num_black += 1
        elif cell in cellState.white_pieces:
            num_white += 1
    return 1 if num_black > num_white else 0


def num_action(action, num_cols):
    """
    Converts the action in the form of alpha-numeric row column sequence to
    numeric actions. i.e. a2 -> 3 for 3x3 board.
    """
    # If not alpha-numeric, return the action as is.
    action = action.lower().strip()
    try:
        if not action[0].isalpha():
            return action
        row = int(action[1:]) - 1
        # for column a -> 0, b -> 1 ...
        col = ord(action[0]) - ord("a")
        return pos_by_coord(num_cols, row, col)
    except ValueError:
        log.error("Invalid action: {}".format(action))
        return False


def random_selection(board_state):
    pos_moves = [i for i, x in enumerate(board_state) if x == cellState.kEmpty]
    return [np.random.choice(pos_moves)], [1.0]


def convert_to_xo(str_board):
    """
    Convert the board state to only x and o.
    """
    for p in cellState.black_pieces:
        str_board = str_board.replace(p, cellState.kBlack)
    for p in cellState.white_pieces:
        str_board = str_board.replace(p, cellState.kWhite)
    return str_board


def get_open_spiel_state(game: pyspiel.Game,
                         initial_state: str) -> pyspiel.State:
    """
    Setup the game state, -start is same as given initial state
    """
    game_state = game.new_initial_state()
    black_stones_loc = []
    white_stones_loc = []
    for i in range(len(initial_state)):
        if initial_state[i] in cellState.black_pieces:
            black_stones_loc.append(i)
        if initial_state[i] in cellState.white_pieces:
            white_stones_loc.append(i)
    black_loc = 0
    white_loc = 0
    for _ in range(len(black_stones_loc) + len(white_stones_loc)):
        cur_player = game_state.current_player()
        if cur_player == 0:
            game_state.apply_action(black_stones_loc[black_loc])
            game_state.apply_action(black_stones_loc[black_loc])
            black_loc += 1
        else:
            game_state.apply_action(white_stones_loc[white_loc])
            game_state.apply_action(white_stones_loc[white_loc])
            white_loc += 1
    return game_state


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
        if cell in cellState.black_pieces:
            new_board += cellState.kBlack
        elif cell in cellState.white_pieces:
            new_board += cellState.kWhite
        else:
            new_board += cellState.kEmpty
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
    player = cellState.kBlack \
        if state[init_pos] in cellState.black_pieces \
        else cellState.kWhite
    flood_stack = [init_pos]
    while len(flood_stack) > 0:
        latest_cell = flood_stack.pop()
        for n in cell_connections(latest_cell, num_cols, num_rows):
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
        gbs = data // (1024 ** 2)
        mbs = (data - gbs * 1024 ** 2) // 1024
        kbs = (data - gbs * 1024 ** 2 - mbs * 1024)
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
        print(f"{red}{bold}Invalid type given to report(). Valid types are = ['memory', 'time']{end}")
