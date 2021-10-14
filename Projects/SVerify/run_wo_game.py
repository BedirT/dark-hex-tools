'''
Strategy Verifier
-----------------
This program evaluates the performance of a strategy S for player p
against every possible strategy S' for player p', on the game DarkHex.

Strategy S is given as a {information set: [(action, probability), ...]}
Strategy S' is every legal move possible at the given game position.

The program works in a linear logic. p makes its move as long as S has
a move to make, if ANY branch stops in a tied position, the strategy is
incomplete. Otherwise the program returns the probability of the winning
for the player p.

Parameters:
    -p: player to evaluate
    -S: strategy to evaluate
'''
from Projects.base.game.hex import pieces
from strategy_data import strategies
from copy import deepcopy

incomplete = False
last_move = None

def pos_by_coord(num_cols, r, c):
    return num_cols * r + c

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
        if ''.join(updated_board_state) == '...yxooyzzoo':
            print(''.join(updated_board_state))
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
    global last_move
    new_game = deepcopy(game)
    if player == game['player']:
        last_move = action
    if new_game['board'][action] != pieces.kEmpty:
        opponent = pieces.kBlack if player == pieces.kWhite else pieces.kWhite
        new_game['boards'][player] = replace_action(new_game['boards'][player], action, 
                                                    opponent)
        return new_game, True
    else:
        res = updated_board(new_game['board'], action, 
                            player, game['num_cols'], game['num_rows'])
        if res == pieces.kBlackWin or res == pieces.kWhiteWin:
            return res, False
        new_game['board'] = res
        new_game['boards'][player] = replace_action(new_game['boards'][player], action, 
                                                    new_game['board'][action])
        s = ""
        for r, k in zip(res, new_game['boards'][player]):
            if k == game['player'] and r != game['player']:
                s += r
            else:
                s += k
        new_game['boards'][player] = s
        return new_game, False

def game_over(board_state):
    '''
    Check if the game is over.

    - board_state: The current board state.
    '''
    return board_state.count(pieces.kBlackWin) +\
        board_state.count(pieces.kWhiteWin) == 1

def start_the_game(game, player_turn):
    '''
    Plays the game until all the S moves are exhausted
    recursively calls itself. If the game is tied, the strategy is incomplete.
    Recursively calculates the probability of winning for player p.
    '''
    global incomplete
    if incomplete: 
        return False
    player_board = game['boards'][game['player']]
    p_res = 0 # probability of p winning for the current branch
    if player_turn == game['player_order']:
        if player_board not in game['strategy']:
            # strategy is incomplete
            print('{}\n{}'.format(player_board, game['board']))
            incomplete = True
            return False
        prob = 1 / len(game['strategy'][player_board])
        for action in game['strategy'][player_board]:
            new_game, collusion = play_action(game, game['player'], action)
            if new_game == pieces.kBlackWin or new_game == pieces.kWhiteWin:
                p_res += prob
            else:
                p_res += prob * start_the_game(new_game, (player_turn if collusion else (player_turn + 1) % 2))
        return p_res
    else:
        pos_results = []
        valid_moves = [i for i, x in enumerate(game['board']) if x == pieces.kEmpty]
        for action in valid_moves:
            new_game, _ = play_action(game, game['opponent'], action)
            if new_game == pieces.kBlackWin or new_game == pieces.kWhiteWin:
                return 0
            else:
                pos_results.append(start_the_game(new_game, (player_turn + 1) % 2))
        # print(pos_results)
        return min(pos_results)

def main(): 
    strategy_dict = strategies.test_2x3_33p
    game = {
        'num_rows': strategy_dict['num_rows'],
        'num_cols': strategy_dict['num_cols'],
        'player_order': strategy_dict['player_order'], # 0 or 1 depending on if player goes first
        'player': strategy_dict['player'], # player to evaluate - kBlack or kWhite
        'opponent': pieces.kWhite if strategy_dict['player'] == pieces.kBlack else pieces.kBlack,
        'strategy': strategy_dict['strategy'],
        'board': pieces.kEmpty * (strategy_dict['num_rows'] * strategy_dict['num_cols']),
        'boards': {
            strategy_dict['player']: pieces.kEmpty * (strategy_dict['num_rows'] * strategy_dict['num_cols']),
            pieces.kWhite if strategy_dict['player'] == pieces.kBlack else pieces.kBlack: 
                                    pieces.kEmpty * (strategy_dict['num_rows'] * strategy_dict['num_cols'])
        },
    }
    win_p = start_the_game(game, 0)
    if incomplete:
        print('Strategy incomplete')
    else:
        # report win probability for player p using strategy S
        print('Win probability for player {} (order {}): {}'\
            .format(game['player'], game['player_order'], win_p))

if __name__ == '__main__':
    main()