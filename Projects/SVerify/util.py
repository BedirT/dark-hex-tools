from copy import deepcopy
import logging

import sys
import os
sys.path.append('../../')

import coloredlogs
import dill
from Projects.base.game.hex import pieces
from strategy_data import strategies


LOG_LEVEL = 'DEBUG'
log = logging.getLogger(__name__)
coloredlogs.install(level=LOG_LEVEL)  # Change this to DEBUG to see more info.


def cell_connections(cell, num_cols, num_rows):
    '''
    Returns the neighbours of the given cell.

    args:
        cell    - The location on the board to check the neighboring cells for.
                In the format [row, column]
    
    returns:
        format >> positions

        positions   - List of all the neighbouring cells to the cell.
                    Elements are in the format [row, column].
    '''
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
    '''
    Check if the game is over.

    - board_state: The current refree board state.
    '''
    return board_state.count(pieces.kBlackWin) +\
        board_state.count(pieces.kWhiteWin) == 1
        
        
def updated_board(board_state, cell, color, num_cols, num_rows):
    '''
    Update the board state with the move.

    - board_state: The current board state.
    - move: The move to be made. (int)
    - piece: The piece to be placed on the board.
    '''
    # Work on a list version of the board state.
    updated_board_state = list(deepcopy(board_state))
    # If the move is illegal return false.
    # - Illegal if the move is out of bounds.
    # - Illegal if the move is already taken.
    if cell < 0 or cell >= len(updated_board_state) or\
        updated_board_state[cell] != pieces.kEmpty:
        return False
    # Update the board state with the move.
    if color == pieces.kBlack:
        north_connected = False
        south_connected = False 
        if cell < num_cols: # First row
            north_connected = True
        elif cell >= num_cols * (num_rows - 1): # Last row
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
        if cell % num_cols == 0: # First column
            west_connected = True
        elif cell % num_cols == num_cols - 1: # Last column
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
    return ''.join(updated_board_state)


def replace_action(board, action, new_value):
    '''
    Replaces the action on the board with the new value.
    '''
    new_board = list(deepcopy(board))
    new_board[action] = new_value
    return ''.join(new_board)


def play_action(game, player, action):
    '''
    Plays the action on the game board.
    '''
    new_game = deepcopy(game)
    if new_game['board'][action] != pieces.kEmpty:
        opponent = pieces.kBlack if player == pieces.kWhite else pieces.kWhite
        new_game['boards'][player] = replace_action(new_game['boards'][player], action, 
                                                    opponent)
        return new_game, True
    else:
        res = updated_board(new_game['board'], action, 
                            player, game['num_cols'], game['num_rows'])
        if res == pieces.kBlackWin or res == pieces.kWhiteWin:
            # The game is over.
            return res, False
        new_game['board'] = res
        new_game['boards'][player] = replace_action(new_game['boards'][player], action, 
                                                    new_game['board'][action])
        s = ""
        opponent = pieces.kBlack if player == pieces.kWhite else pieces.kWhite
        for r in new_game['boards'][player]:
            if r in pieces.black_pieces:
                s += pieces.kBlack
            elif r in pieces.white_pieces:
                s += pieces.kWhite
            else:
                s += r
        new_game['boards'][player] = s
        return new_game, False


def load_file(filename):
    '''
    Loads a file and returns the content.
    '''
    return dill.load(open(filename, 'rb'))


def save_file(content, filename):
    '''
    Saves the content to a file.
    '''
    # Create the directory if it doesn't exist.
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)

    dill.dump(content, open(filename, 'wb'))


def pos_by_coord(num_cols, r, c):
    return num_cols * r + c


def conv_alphapos(pos, num_cols):
    '''
    Converts a position to a letter and number
    pos: int
    '''
    col = pos % num_cols
    row = pos // num_cols
    return '{}{}'.format(chr(ord('a') + col), row + 1)


def choose_strategy(choice=None):
    '''
    User is displayed all the options in strategies
    and will pick one to run the algorithm for.
    '''
    i = 0
    arr = []
    if choice is None:
        print('Choose a strategy to run the algorithm for:')

    for name, strategy in vars(strategies).items():
        # no private variables
        if not name.startswith('__'):
            if choice is None:
                print('{}. {}'.format(i, name))
            i += 1; arr.append((strategy, name))
    
    # make sure the choice is valid
    try:
        if choice is None:
            choice = int(input('Enter your choice: '))
        if choice < 0 or choice >= len(arr):
            raise ValueError
    except ValueError:
        print('Invalid choice')
        return choose_strategy()
    return arr[choice][0], arr[choice][1]


def get_game_state(game, opp_strategy=None):
    game_state = {
        'board': game['board']
            if 'board' in game 
            else pieces.kEmpty * (game['num_rows'] * game['num_cols']),
        'boards': {
            game['player']: 
                game['boards'][game['player']]
                if 'boards' in game
                else pieces.kEmpty * (game['num_rows'] * game['num_cols']),
            pieces.kWhite if game['player'] == pieces.kBlack else pieces.kBlack: 
                game['boards'][pieces.kWhite if game['player'] == pieces.kBlack else pieces.kBlack]
                if 'boards' in game
                else pieces.kEmpty * (game['num_rows'] * game['num_cols'])
        },
        'num_rows': game['num_rows'],
        'num_cols': game['num_cols'],
        'first_player': game['first_player'],
        'player_order': game['player_order'],
        'player': game['player'],
        'opponent': pieces.kWhite if game['player'] == pieces.kBlack else pieces.kBlack,
        'player_strategy': game['strategy'],
        'opponent_strategy': opp_strategy
    }
    return game_state


def greedify(strategy, multiple_actions_allowed=False):
    '''
    Greedifies the given strategy. -1 is the minumum value and 1 is the maximum.
    Args:
        strategy: The strategy to greedify.
        multiple_actions_allowed: Whether multiple actions are allowed.
    Returns:
        A greedified version of the strategy.
    '''
    log.info('Greedifying strategy...')
    greedy_strategy = {}
    for board_state, item in strategy.items():
        mx_value = -1
        valid_moves = [i for i, x in enumerate(board_state) if x == pieces.kEmpty]
        actions = []
        for idx, value in enumerate(item):
            if idx not in valid_moves:
                continue
            if value > mx_value:
                mx_value = value
                actions = [idx]
            elif value == mx_value and multiple_actions_allowed:
                actions.append(idx)
        greedy_strategy[board_state] = [(actions[i], 1 / len(actions)) for i in range(len(actions))]
    return greedy_strategy


def calculate_turn(game_state):
    '''
    Calculates which player's turn it is.
    '''
    log.debug(f'Calculating turn for board {game_state["board"]}')
    game_board = game_state['board']
    num_black = 0; num_white = 0
    for i in range(len(game_board)):
        if game_board[i] in pieces.black_pieces: num_black += 1
        if game_board[i] in pieces.white_pieces: num_white += 1
    if game_state['first_player'] == pieces.kBlack:
        if num_black > num_white:   return 1
        else:                       return 0
    else:
        if num_white > num_black:   return 1
        else:                       return 0
        