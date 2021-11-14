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
from Projects.base.game.hex import pieces, customBoard_print
from strategy_data import strategies
from copy import deepcopy
from time import time

opp_info = {}

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

def game_over(board_state):
    '''
    Check if the game is over.

    - board_state: The current board state.
    '''
    return board_state.count(pieces.kBlackWin) +\
        board_state.count(pieces.kWhiteWin) == 1

def possible_win_moves(game_state, to_play):
    '''
    Calculates the possible moves that opponent can make and end up in a win.
    If the probability of the win (for opponent) is greater than 0 then we include
    that move in the list of possible moves.

    This is necessary to find the intersection of the moves for every branching on the
    strategy tree.

    - game_state: The current game state.
    - to_play: The player whose turn it is. Needed to check if it is the opponent's turn.
    '''
    # It should be the turn of the to_play
    assert calculate_turn(game_state) == to_play
    
    boards = game_state['boards']

    if boards[pieces.kBlack] + boards[pieces.kWhite] in opp_info:
        return opp_info[boards[pieces.kBlack] + boards[pieces.kWhite]]

    allowed_moves = []; mn_prob = 1; player = game_state['opponent']
    opponent_board = boards[player]
    opponent_board_valid_moves = [i for i, k in enumerate(opponent_board) if k == pieces.kEmpty]
    
    for action in opponent_board_valid_moves:
        new_game, collusion = play_action(game_state, player, action)
        if new_game in [pieces.kBlackWin, pieces.kWhiteWin]:
            if mn_prob > 0: 
                allowed_moves = [action]
            else: 
                allowed_moves.append(action)
            mn_prob = 0
        else:
            pos_moves = possible_win_moves(new_game, to_play) if collusion else []
            res = start_the_game(new_game, pos_moves, to_play if collusion else (to_play + 1) % 2)
            if mn_prob > res: 
                mn_prob = res
                allowed_moves = [action]
            elif mn_prob == res: 
                allowed_moves.append(action)

    assert len(allowed_moves) > 0
    if mn_prob == 1:
        allowed_moves = []

    opp_info[boards[pieces.kBlack] + 
             boards[pieces.kWhite]] = allowed_moves

    return allowed_moves

def calculate_turn(game_state):
    '''
    Calculates the turn of the player.
    '''
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

def start_the_game(game, op_moves, to_play):
    '''
    Plays the game until all the S moves are exhausted
    recursively calls itself. If the game is tied, the strategy is incomplete.
    Recursively calculates the probability of winning for player p.
    '''
    player_board = game['boards'][game['player']]
    possible_op_moves = []
    p_res = 0 # probability of p winning for the current branch
    if to_play == game['player_order']:
        # assert op_moves == [] # COME BACK TO THIS
        if player_board not in game['strategy']:
            # strategy is incomplete
            print('{}\n{}'.format(player_board, game['board']))
            print('Strategy incomplete')
            exit()
        for action, prob in game['strategy'][player_board]:
            new_game, collusion = play_action(game, game['player'], action)
            if new_game in [pieces.kBlackWin, pieces.kWhiteWin]:
                continue
            elif not collusion:
                possible_op_moves += possible_win_moves(new_game, (to_play + 1) % 2)
        possible_op_moves = list(set(possible_op_moves))

        for action, prob in game['strategy'][player_board]:
            new_game, collusion = play_action(game, game['player'], action)
            if new_game in [pieces.kBlackWin, pieces.kWhiteWin]:
                p_res += prob
            else:
                value = start_the_game(new_game, possible_op_moves, (to_play if collusion else (to_play + 1) % 2))
                p_res += prob * value
        return p_res
    else:
        pos_results = []
        if len(op_moves) == 0:
            # If the opponent has no moves, then the probability of the opponent winning is 1.
            return 1
        assert len(op_moves) > 0
        for action in op_moves:
            new_game, collusion = play_action(game, game['opponent'], action)
            if new_game in [pieces.kBlackWin, pieces.kWhiteWin]:
                
                pos_results.append(0)
            else:
                pos_moves = possible_win_moves(new_game, to_play) if collusion else [x for x in op_moves if x != action]
                res = start_the_game(new_game, pos_moves, to_play if collusion else (to_play + 1) % 2)
                pos_results.append(res)
        mean_val = sum(pos_results) / len(pos_results)
        return mean_val

def choose_strategy():
    '''
    User is displayed all the options in strategies
    and will pick one to run the algorithm for.
    '''
    print('Choose a strategy to run the algorithm for:')
    i = 0
    arr = []
    for name, strategy in vars(strategies).items():
        # no private variables
        if not name.startswith('__'):
            print('{}. {}'.format(i, name))
            i += 1; arr.append(strategy)
    choice = int(input('Enter your choice: '))
    return arr[choice]

def main(): 
    start = time()
    # list all the strategies from strategies, display 
    # and let the user choose one
    strategy_dict = choose_strategy()
    game_state = {
        'num_rows': strategy_dict['num_rows'],
        'num_cols': strategy_dict['num_cols'],
        'player_order': strategy_dict['player_order'], # 0 or 1 depending on if player goes first
        'player': strategy_dict['player'], # player to evaluate - kBlack or kWhite
        'first_player': strategy_dict['first_player'], # kBlack or kWhite
        'opponent': pieces.kWhite if strategy_dict['player'] == pieces.kBlack else pieces.kBlack,
        'strategy': strategy_dict['strategy'],
        'board': strategy_dict['board']
            if 'board' in strategy_dict 
            else pieces.kEmpty * (strategy_dict['num_rows'] * strategy_dict['num_cols']),
        'boards': {
            strategy_dict['player']: 
                strategy_dict['boards'][strategy_dict['player']]
                if 'boards' in strategy_dict
                else pieces.kEmpty * (strategy_dict['num_rows'] * strategy_dict['num_cols']),
            pieces.kWhite if strategy_dict['player'] == pieces.kBlack else pieces.kBlack: 
                strategy_dict['boards'][pieces.kWhite if strategy_dict['player'] == pieces.kBlack else pieces.kBlack]
                if 'boards' in strategy_dict
                else pieces.kEmpty * (strategy_dict['num_rows'] * strategy_dict['num_cols'])
        },
    }
    # customBoard_print(game_state['board'], game_state['num_cols'], game_state['num_rows'])
    turn = calculate_turn(game_state)
    opponent_moves = possible_win_moves(game_state, 0) if turn != game_state['player_order'] else []
    win_p = start_the_game(game_state, opponent_moves, turn)
    # report win probability for player p using strategy S
    print('Win probability for player {} (order {}): {}'\
        .format(game_state['player'], game_state['player_order'], win_p))
    print('Time taken: {}'.format(time() - start))

if __name__ == '__main__':
    main()