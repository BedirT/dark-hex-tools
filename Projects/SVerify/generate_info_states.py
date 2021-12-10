'''
Infostate creator.

- Get the game size (n by m size)
- Get which player we are generating the information
states for.
- For each move specified, recursively call the generate_info_states
function, one for a collusion if possible, and one for a non-collusion.
- For the collusion place an opponent stone, and for the non-collusion
place a player stone on the board for information state.
- Calls continue until the game terminates.
- Collect the information states and corresponding moves that are specified
from there in a dictionary.
- Return the dictionary.

The game is Dark Hex on nxm board.
'''

from collections import Counter, defaultdict
from copy import deepcopy
import logging as log
import numpy as np
import argparse
import sys
sys.path.append('../../')
# import sleep
from time import sleep

from Projects.base.game.hex import pieces
from Projects.base.util.colors import colors
from Projects.SVerify.isomorphic import isomorphic_single

def convert_to_xo(str_board):
    '''
    Convert the board state to only x and o.
    '''
    for p in pieces.black_pieces:
        str_board = str_board.replace(p, pieces.kBlack)
    for p in pieces.white_pieces:
        str_board = str_board.replace(p, pieces.kWhite)
    return str_board

def printBoard(board_state, num_cols, num_rows, move_sequence):
    '''
    Method for printing the board in a nice format.
    '''
    num_cells = num_cols * num_rows
    the_cell = 0 # The cell we are currently printing.
    print(colors.C_PLAYER1, end='  ')
    for i in range(num_cols):
        print('{0: <3}'.format(chr(ord('a') + i)), end='')
    print(colors.ENDC)
    print(colors.BOLD + colors.C_PLAYER1 + ' ' + '-' * (num_cols * 3 +1) + colors.ENDC)
    for cell in range(num_cells):
        if cell % num_cols == 0: # first col
            print(colors.BOLD + colors.C_PLAYER2 + str(cell // num_cols + 1) +'\\ ' + colors.ENDC, end='')
        if board_state[cell] in pieces.black_pieces:
            clr = colors.C_PLAYER1
        elif board_state[cell] in pieces.white_pieces:
            clr = colors.C_PLAYER2
        else:
            clr = colors.NEUTRAL
        if board_state[cell] == pieces.kEmpty:
            print(clr + '{0: <3}'.format(the_cell) + colors.ENDC, end='') 
        else:
            print(clr + '{0: <3}'.format(board_state[cell]) + colors.ENDC, end='')
        the_cell += 1 
        if cell % num_cols == num_cols-1: # last col
            print(colors.BOLD + colors.C_PLAYER2 + '\\' + pieces.kWhite + '\n' + (' ' * (cell//num_cols)) + colors.ENDC, end = ' ')
    print(colors.BOLD + colors.C_PLAYER1 + '  ' + '-' * (num_cols * 3 +1) + colors.ENDC)        
    print(colors.BOLD + colors.C_PLAYER1 + ' ' * (num_rows+4) + '{0: <3}'.format(pieces.kBlack) * num_cols + colors.ENDC)
    print(colors.BOLD + colors.QUESTIONS + 'Game seq: ' + colors.ENDC, end='')
    for mv in move_sequence:
        if mv[1] == pieces.kBlack:
            # move is player kBlack
            print(colors.C_PLAYER1 + '{}'.format(mv[0]) + colors.ENDC, end=' ')
        else:
            # move is player kWhite
            print(colors.C_PLAYER2 + '{}'.format(mv[0]) + colors.ENDC, end=' ')
    print(colors.BOLD + colors.QUESTIONS + '\n' + colors.ENDC)

def save_input(input_list):
    '''
    Save the input to a file. If the file already exists,
    append the input to the file.

    - input_list: The input to save.
    '''
    with open('input_new.txt', 'a') as f:
        for i in input_list:
            f.write(str(i) + ' ')
        f.write('\n')
 
def random_selection(board_state):
    pos_moves = [i for i, x in enumerate(board_state) if x == pieces.kEmpty]
    return [np.random.choice(pos_moves)], [1.0] 

def numeric_action(action, num_cols):
    '''
    Converts the action in the form of alpha-numeric row column sequence to
    numeric actions. i.e. a2 -> 3 for 3x3 board.
    '''
    # If not alpha-numeric, return the action as is.
    action = action.lower().strip()
    try:
        if not action[0].isalpha():
            return action
        row = int(action[1:]) - 1
        # for column a -> 0, b -> 1 ...
        col = ord(action[0]) - ord('a')
    except ValueError:
        log.error('Invalid action: {}'.format(action))
        return False
    return pos_by_coord(num_cols, row, col)
  
def get_moves(board_state, num_cols, num_rows, move_sequence, fill_randomly):
    '''
    Get moves for the current board state from the user.
    Seperate the moves by spaces.

    - board_state: The current board state.
    '''
    if fill_randomly:
        moves, probs = random_selection(board_state)
        return moves, probs, fill_randomly
    
    # TODO: FIX THE PROBABILITIES
    # Print the board state to the user.
    printBoard(board_state, num_cols, num_rows, move_sequence)
    sleep(0.1)
    # Get the moves and (if wanted) probabilities of those moves from the user.
    moves_and_probs = input(colors.BOLD + colors.QUESTIONS + 
                    'Enter moves and probabilities (separated by spaces)\n' +
                    'For the single entries (one action) no need for the probabilites\n' + 
                    'Start the entry with = for equiprobable entries (no prob entries)\n' +
                    '"r" for random selection for the rest of the branch\n' + 
                    '"exit" for exitting program\n:' + colors.ENDC)
    moves_and_probs = moves_and_probs.strip().split(' ')

    if moves_and_probs[0] == 'exit':
        exit()

    if moves_and_probs[0] == 'r':
        # randomly select one possible move
        moves, probs = random_selection(board_state)
        fill_randomly = True
    elif len(moves_and_probs) == 1:
        # If there is only one move, then the probability is 1.
        a = numeric_action(moves_and_probs[0], num_cols)
        if a:
            moves = [a]
            probs = [1]
        else:
            log.error('Invalid move: {}'.format(moves_and_probs[0]))
            return get_moves(board_state, num_cols, num_rows, move_sequence, fill_randomly)
    elif moves_and_probs[0] == '=':
        # Equaprobability
        # No probabilities given.
        moves = [numeric_action(x, num_cols) for x in moves_and_probs[1:]]
        if False in moves:
            return get_moves(board_state, num_cols, num_rows, move_sequence, fill_randomly)
        probs = [1/len(moves)] * len(moves)
    else:
        moves = []
        probs = []
        for i in range(0, len(moves_and_probs), 2):
            a = numeric_action(moves_and_probs[i], num_cols)
            if a:
                moves.append(a)
                probs.append(float(moves_and_probs[i+1]))
            else:
                log.warning('Invalid move: {}'.format(moves_and_probs[i]))
                return get_moves(board_state, num_cols, num_rows, move_sequence, fill_randomly)
        
    moves = list(map(int, moves))
    probs = list(map(float, probs))
    save_input(moves_and_probs)
    
    return moves, probs, fill_randomly
    
def is_collusion_possible(board_state, player, opponent, player_order):
    '''
    Check if a collusion is possible.

    - board_state: The current board state.
    '''
    # Get the number of pieces on the board.
    count = Counter(board_state)
    if opponent == pieces.kBlack:
        opponent_pieces = sum([s for x, s in count.items() if x in pieces.black_pieces])
        player_pieces = sum([s for x, s in count.items() if x in pieces.white_pieces])
    else:
        opponent_pieces = sum([s for x, s in count.items() if x in pieces.white_pieces])
        player_pieces = sum([s for x, s in count.items() if x in pieces.black_pieces])
    # second player has to have less than or equal amount of
    # pieces on the board at all times.
    if player_order == 0:
        return opponent_pieces < player_pieces
    else:
        return opponent_pieces <= player_pieces

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
    
def game_over(board_state, player, player_order):
    '''
    Check if the game is over.

    - board_state: The current board state.
    '''
    if  board_state.count(pieces.kBlackWin) +\
        board_state.count(pieces.kWhiteWin) == 1:
        return True
    ct = Counter(board_state)
    empty_cells = ct[pieces.kEmpty]
    if player == pieces.kBlack:
        opponent_pieces = sum([s for x, s in ct.items() if x in pieces.white_pieces])
        player_pieces = sum([s for x, s in ct.items() if x in pieces.black_pieces])
    else:
        opponent_pieces = sum([s for x, s in ct.items() if x in pieces.black_pieces])
        player_pieces = sum([s for x, s in ct.items() if x in pieces.white_pieces])
    if (player_order == 0 and opponent_pieces + empty_cells == player_pieces) or\
        (player_order == 1 and opponent_pieces + empty_cells == player_pieces+1):
        return True
    return False

def moves_and_probs(moves, probs):
    if probs is None:
        # equal probability for all moves
        probs = [1/len(moves)] * len(moves)
    else:
        assert len(moves) == len(probs)
    # return moves and probs in a list of tuples
    # so 0th element will be (move[0], prob[0])
    return list(zip(moves, probs))

def generate_info_states(board_state, info_states, player, opponent, player_order, num_cols, num_rows, isomorphic, move_sequence, fill_randomly):
    '''
    Recursively call the generate_info_states function, one for a
    collusion if possible, and one for a non-collusion. Moves are specified
    by the user for each board state.

    - board_state: The current board state.
    - info_states: The dictionary of information states and corresponding
    moves.
    - player: The player we are generating the information states for.
    '''
    # Check if the game is over.
    if game_over(board_state, player, player_order):
        return
    # Get the moves for the current board state. (Try until valid options are provided)
    valid_moves = False
    moves = []
    probs = []
    while not valid_moves:
        valid_moves = True
        moves, probs, fill_randomly = get_moves(board_state, num_cols, num_rows, move_sequence, fill_randomly)
        # Check if the moves are valid. Save the new board states for each move.
        moves_and_boards = {}
        for move in moves:
            new_board = updated_board(board_state, move, opponent, num_cols, num_rows)
            new_board_2 = updated_board(board_state, move, player, num_cols, num_rows)
            if not new_board:
                log.warning(f"Illegal move: {move}")
                valid_moves = False
                while True:
                    xxx = input()
                    if xxx == 'continue':
                        break
                break
            moves_and_boards[str(move)+opponent] = new_board
            moves_and_boards[str(move)+player] = new_board_2
    # Update info_states with the moves.
    info_states[board_state] = moves_and_probs(moves, probs)
    if isomorphic:
        # Also update the isomorphic states.
        iso_state, iso_moves_probs = isomorphic_single(board_state, moves, probs)
        if iso_state not in info_states:
            info_states[iso_state] = iso_moves_probs
        else:
            ls = []
            d = {}
            for move, prob in iso_moves_probs:
                if move not in d:
                    ls.append((move, prob/2))
                    d[move] = len(ls)-1
                else:
                    ls[d[move]] = (move, ls[d[move]][1] + prob/2)
            for move, prob in info_states[iso_state]:
                if move not in d:
                    ls.append((move, prob/2))
                    d[move] = len(ls)-1
                else:
                    ls[d[move]] = (move, ls[d[move]][1] + prob/2)
            info_states[iso_state] = ls
    # If a collusion is possible
    collusion_possible = is_collusion_possible(board_state, player, opponent, player_order)
    # For each move, recursively call the generate_info_states function.
    for move in moves:
        printBoard(board_state, num_cols, num_rows, move_sequence)
        if collusion_possible:
            new_board = moves_and_boards[str(move)+opponent]
            if new_board not in info_states: 
                new_seq = move_sequence + [[move, opponent]]
                generate_info_states(new_board, info_states, player, opponent, player_order, num_cols, num_rows, isomorphic, new_seq, fill_randomly)
        # Generate the information state for a non-collusion.
        new_board = moves_and_boards[str(move)+player]
        if new_board not in info_states:
            new_seq = move_sequence + [[move, player]]
            generate_info_states(new_board, info_states, player, opponent, player_order, num_cols, num_rows, isomorphic, new_seq, fill_randomly)
        
def main():
    '''
    Main function.
    '''
    # GAME SETUP
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    argparser = argparse.ArgumentParser(description='Generate information states.')
    argparser.add_argument('--num_cols', type=int, default=3, help='Number of columns.')
    argparser.add_argument('--num_rows', type=int, default=3, help='Number of rows.')
    argparser.add_argument('--player_order', type=int, default=0, help='Player order (0/1)')
    argparser.add_argument('--player_color', type=str, default='b', help='Player color (b/w)')
    argparser.add_argument('--board_state', type=str, default='', help='Custom board state.')
    argparser.add_argument('--convert_xo', action='store_true', default=True, help='Convert the board to x and o\'s.')
    argparser.add_argument('--isomorphic', action='store_true', default=True, help='Generate isomorphic states.')
    argparser.add_argument('--write_to_dict', action='store_true', default=True, help='Write to the end of the strategy_data.py')
    argparser.add_argument('--dict_name', type=str, help='Name of the variable to write to.', required='--write_to_dict' in sys.argv)
    args = argparser.parse_args()
    
    if args.player_color == 'b':
        player = pieces.kBlack 
        opponent = pieces.kWhite
    else:
        player = pieces.kWhite  
        opponent = pieces.kBlack
    
    if args.board_state == '':
        board_state = pieces.kEmpty * args.num_cols * args.num_rows # empty board
    else:
        board_state = args.board_state
        if len(board_state) != args.num_cols * args.num_rows:
            log.error("Board state is not the correct size!")
            return
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    info_states = defaultdict(lambda: list())
    generate_info_states(board_state, info_states, player, opponent, args.player_order, args.num_cols, args.num_rows, args.isomorphic, [], False)
    # save info_states to file
    with open('info_states.txt', 'w') as f:
        for key, value in info_states.items():
            if args.convert_xo:
                key = convert_to_xo(key)
            f.write('"' + key + '": ' + str(value) + ',\n')
    # write info_states to the end on the strategy_data.py file
    if args.write_to_dict:
        with open('strategy_data.py', 'a') as f:
            f.write('\n\t' + args.dict_name + ' = {\n')
            f.write('\t\t"num_rows": {},\n'.format(args.num_rows))
            f.write('\t\t"num_cols": {},\n'.format(args.num_cols))
            the_p = 'pieces.kBlack' if player == pieces.kBlack else 'pieces.kWhite'
            f.write('\t\t"player": {},\n'.format(the_p))
            f.write('\t\t"player_order": {},\n'.format(args.player_order))
            first_p = player if args.player_order == 0 else opponent
            first_p = 'pieces.kBlack' if first_p == pieces.kBlack else 'pieces.kWhite'
            f.write('\t\t"first_player": {},\n'.format(first_p))
            f.write('\t\t"isomorphic": {},\n'.format(args.isomorphic))
            if board_state != '':
                f.write('\t\t"board": "{}",\n'.format(board_state))
                f.write('\t\t"boards": {\n')
                f.write('\t\t\tpieces.kBlack: "{}",\n'.format(convert_to_xo(board_state)))
                f.write('\t\t\tpieces.kWhite: "{}"\n'.format(convert_to_xo(board_state)))
                f.write('\t\t},\n')
            f.write('\t\t"strategy": {\n')
            for key, value in info_states.items():
                if args.convert_xo:
                    key = convert_to_xo(key)
                f.write('\t\t\t"' + key + '": ' + str(value) + ',\n')
            f.write('\t\t}\n\t}')
    save_input([''])
    
    # print success message
    # state the number of states generated
    # state the path where the info_states.txt file is saved
    log.info('Successfully generated information states.')
    log.info(f'Number of states: {len(info_states)}')
    log.info('Path: info_states.txt')    
    
if __name__ == "__main__":
    main()