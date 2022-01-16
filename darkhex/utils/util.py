import os
from copy import deepcopy

import dill
import numpy as np
import pyspiel


def cell_connections(cell, num_cols, num_rows):
    """
    Returns the neighbours of the given cell.

    args:
        cell    - The location on the board to check the neighboring cells for.
                In the format [row, column]

    returns:
        format >> positions

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
    return (
        board_state.count(pieces.kBlackWin) + board_state.count(pieces.kWhiteWin) == 1
    )


def updated_board(board_state, cell, color, num_cols, num_rows):
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
    if (
        cell < 0
        or cell >= len(updated_board_state)
        or updated_board_state[cell] != pieces.kEmpty
    ):
        return False
    # Update the board state with the move.
    if color == pieces.kBlack:
        north_connected = False
        south_connected = False
        if cell < num_cols:  # First row
            north_connected = True
        elif cell >= num_cols * (num_rows - 1):  # Last row
            south_connected = True
        for neighbour in cell_connections(cell, num_cols, num_rows):
            if updated_board_state[neighbour] == pieces.kBlackNorth:
                north_connected = True
            elif updated_board_state[neighbour] == pieces.kBlackSouth:
                south_connected = True
        if north_connected and south_connected:
            updated_board_state[cell] = pieces.kBlackWin
        elif north_connected:
            updated_board_state[cell] = pieces.kBlackNorth
        elif south_connected:
            updated_board_state[cell] = pieces.kBlackSouth
        else:
            updated_board_state[cell] = pieces.kBlack
    elif color == pieces.kWhite:
        east_connected = False
        west_connected = False
        if cell % num_cols == 0:  # First column
            west_connected = True
        elif cell % num_cols == num_cols - 1:  # Last column
            east_connected = True
        for neighbour in cell_connections(cell, num_cols, num_rows):
            if updated_board_state[neighbour] == pieces.kWhiteWest:
                west_connected = True
            elif updated_board_state[neighbour] == pieces.kWhiteEast:
                east_connected = True
        if east_connected and west_connected:
            updated_board_state[cell] = pieces.kWhiteWin
        elif east_connected:
            updated_board_state[cell] = pieces.kWhiteEast
        elif west_connected:
            updated_board_state[cell] = pieces.kWhiteWest
        else:
            updated_board_state[cell] = pieces.kWhite

    if updated_board_state[cell] in [pieces.kBlackWin, pieces.kWhiteWin]:
        return updated_board_state[cell]
    elif updated_board_state[cell] not in [pieces.kBlack, pieces.kWhite]:
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
    if new_game["board"][action] != pieces.kEmpty:
        opponent = pieces.kBlack if player == pieces.kWhite else pieces.kWhite
        new_game["boards"][player] = replace_action(
            new_game["boards"][player], action, opponent
        )
        return new_game, True
    else:
        res = updated_board(
            new_game["board"], action, player, game["num_cols"], game["num_rows"]
        )
        if res == pieces.kBlackWin or res == pieces.kWhiteWin:
            # The game is over.
            return res, False
        new_game["board"] = res
        new_game["boards"][player] = replace_action(
            new_game["boards"][player], action, new_game["board"][action]
        )
        s = ""
        opponent = pieces.kBlack if player == pieces.kWhite else pieces.kWhite
        for r in new_game["boards"][player]:
            if r in pieces.black_pieces:
                s += pieces.kBlack
            elif r in pieces.white_pieces:
                s += pieces.kWhite
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


def choose_strategy(choice=None):
    """
    User is displayed all the options in strategies
    and will pick one to run the algorithm for.
    """
    i = 0
    arr = []
    if choice is None:
        print("Choose a strategy to run the algorithm for:")

    # Read strategies from Data/strategy_data folder
    data_folder_names = os.listdir(os.path.join(os.getcwd(), "Data", "strategy_data"))
    # give the data folders as options to user
    for data_folder_name in data_folder_names:
        if choice is None:
            print("{}. {}".format(i, data_folder_name))
        # get the
        arr.append(data_folder_name)
        i += 1

    # make sure the choice is valid
    try:
        if choice is None:
            choice = int(input("> "))
        if choice < 0 or choice >= len(arr):
            raise ValueError
    except ValueError:
        print("Invalid choice. Please try again.")
        return choose_strategy(choice)

    # return the chosen strategy
    strat = load_file(
        os.path.join(os.getcwd(), "Data", "strategy_data", arr[choice], "game_info.pkl")
    )
    return strat, arr[choice]


def get_game_state(game, opp_strategy=None):
    game_state = {
        "board": game["board"]
        if "board" in game
        else pieces.kEmpty * (game["num_rows"] * game["num_cols"]),
        "boards": {
            game["player"]: game["boards"][game["player"]]
            if "boards" in game
            else pieces.kEmpty * (game["num_rows"] * game["num_cols"]),
            pieces.kWhite
            if game["player"] == pieces.kBlack
            else pieces.kBlack: game["boards"][
                pieces.kWhite if game["player"] == pieces.kBlack else pieces.kBlack
            ]
            if "boards" in game
            else pieces.kEmpty * (game["num_rows"] * game["num_cols"]),
        },
        "num_rows": game["num_rows"],
        "num_cols": game["num_cols"],
        "player": game["player"],
        "opponent": pieces.kWhite if game["player"] == pieces.kBlack else pieces.kBlack,
        "player_strategy": game["strategy"],
        "opponent_strategy": opp_strategy,
    }
    return game_state


def greedify(strategy, multiple_actions_allowed=False):
    """
    Greedifies the given strategy. -1 is the minumum value and 1 is the maximum.
    Args:
        strategy: The strategy to greedify.
        multiple_actions_allowed: Whether multiple actions are allowed.
    Returns:
        A greedified version of the strategy.
    """
    log.info("Greedifying strategy...")
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


def calculate_turn(game_state):
    """
    Calculates which player's turn it is.
    """
    log.debug(f'Calculating turn for board {game_state["board"]}')
    game_board = game_state["board"]
    num_black = 0
    num_white = 0
    for i in range(len(game_board)):
        if game_board[i] in pieces.black_pieces:
            num_black += 1
        if game_board[i] in pieces.white_pieces:
            num_white += 1
    return 1 if num_black > num_white else 0


def numeric_action(action, num_cols):
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
    except ValueError:
        log.error("Invalid action: {}".format(action))
        return False
    return pos_by_coord(num_cols, row, col)


def random_selection(board_state):
    pos_moves = [i for i, x in enumerate(board_state) if x == pieces.kEmpty]
    return [np.random.choice(pos_moves)], [1.0]


def convert_to_xo(str_board):
    """
    Convert the board state to only x and o.
    """
    for p in pieces.black_pieces:
        str_board = str_board.replace(p, pieces.kBlack)
    for p in pieces.white_pieces:
        str_board = str_board.replace(p, pieces.kWhite)
    return str_board


def get_open_spiel_state(game: pyspiel.Game, initial_state: str) -> pyspiel.State:
    """
    Setup the game state, -start is same as given initial state
    """
    game_state = game.new_initial_state()
    black_stones_loc = []
    white_stones_loc = []
    for i in range(len(initial_state)):
        if initial_state[i] in pieces.black_pieces:
            black_stones_loc.append(i)
        if initial_state[i] in pieces.white_pieces:
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


def convert_os_str(str_board: str, num_cols: int, player: int):
    """
    Convert the board state to pyspiel format.
    ie. P{player} firstrow\nsecondrow
    """
    new_board = "P" + str(player) + " "
    for i, cell in enumerate(str_board):
        if i % num_cols == 0 and i != 0:
            new_board += "\n"
        if cell in pieces.black_pieces:
            new_board += pieces.kBlack
        elif cell in pieces.white_pieces:
            new_board += pieces.kWhite
        else:
            new_board += pieces.kEmpty
    return new_board


def convert_os_strategy(strategy: dict, num_cols: int, player: int) -> dict:
    """
    Convert the strategy from open_spiel to the format of the game.
    """
    new_strat = {}
    for board_state, actions in strategy.items():
        new_strat[convert_os_str(board_state, num_cols, player)] = actions
    return new_strat
