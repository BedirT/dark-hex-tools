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
from Projects.base.game.hex import pieces
from Projects.base.util.colors import colors
from copy import deepcopy

def printBoard(board_state, num_cols, num_rows, move_sequence):
    '''
    Method for printing the board in a nice format.
    '''
    num_cells = num_cols * num_rows
    print(colors.C_PLAYER1 + '  ' + '{0: <3}'.format(pieces.kBlack) * num_cols + colors.ENDC)
    print(colors.BOLD + colors.C_PLAYER1 + ' ' + '-' * (num_cols * 3 +1) + colors.ENDC)
    for cell in range(num_cells):
        if cell % num_cols == 0: # first col
            print(colors.BOLD + colors.C_PLAYER2 + pieces.kWhite +'\\ ' + colors.ENDC, end= '')
        if board_state[cell] in pieces.black_pieces:
            clr = colors.C_PLAYER1
        elif board_state[cell] in pieces.white_pieces:
            clr = colors.C_PLAYER2
        else:
            clr = colors.NEUTRAL
        print(clr + '{0: <3}'.format(board_state[cell]) + colors.ENDC, end='') 
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

def get_moves(board_state, num_cols, num_rows, move_sequence):
    '''
    Get moves for the current board state from the user.
    Seperate the moves by spaces.

    - board_state: The current board state.
    '''
    # Print the board state to the user.
    printBoard(board_state, num_cols, num_rows, move_sequence)
    ins = list(map(int, input('Enter moves for board state (space between each move): ').strip().split(' ')))
    return ins
    
def is_collusion_possible(board_state, player, opponent, player_order):
    '''
    Check if a collusion is possible.

    - board_state: The current board state.
    '''
    # Get the number of pieces on the board.
    count = Counter(board_state)
    print(count)
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
        return opponent_pieces <= player_pieces + 1

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
    
def game_over(board_state):
    '''
    Check if the game is over.

    - board_state: The current board state.
    '''
    return board_state.count(pieces.kBlackWin) +\
        board_state.count(pieces.kWhiteWin) == 1

def generate_info_states(board_state, info_states, player, opponent, player_order, num_cols, num_rows, move_sequence):
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
    if game_over(board_state):
        return
    # Get the moves for the current board state. (Try until valid options are provided)
    valid_moves = False
    moves = []
    while not valid_moves:
        valid_moves = True
        moves = get_moves(board_state, num_cols, num_rows, move_sequence)
        # Check if the moves are valid. Save the new board states for each move.
        moves_and_boards = {}
        for move in moves:
            new_board = updated_board(board_state, move, opponent, num_cols, num_rows)
            new_board_2 = updated_board(board_state, move, player, num_cols, num_rows)
            if not new_board:
                print("Illegal move: " + str(move))
                valid_moves = False
                break
            moves_and_boards[str(move)+opponent] = new_board
            moves_and_boards[str(move)+player] = new_board_2
    # Update info_states with the moves.
    info_states[board_state] = moves
    # If a collusion is possible
    collusion_possible = is_collusion_possible(board_state, player, opponent, player_order)
    # For each move, recursively call the generate_info_states function.
    for move in moves:
        printBoard(board_state, num_cols, num_rows, move_sequence)
        if collusion_possible:
            new_board = moves_and_boards[str(move)+opponent]
            if new_board not in info_states: 
                new_seq = move_sequence + [[move, opponent]]
                generate_info_states(new_board, info_states, player, opponent, player_order, num_cols, num_rows, new_seq)
        # Generate the information state for a non-collusion.
        new_board = moves_and_boards[str(move)+player]
        if new_board not in info_states:
            new_seq = move_sequence + [[move, player]]
            generate_info_states(new_board, info_states, player, opponent, player_order, num_cols, num_rows, new_seq)
        
if __name__ == "__main__":
    '''
    Main function.
    '''
    # GAME SETUP
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    num_cols, num_rows = 3, 3                                                      # +
    player = pieces.kBlack                                                         # +
    opponent = pieces.kWhite                                                       # +
    player_order = 0 # 0 for first player, 1 for second player                     # +                
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    board_state = pieces.kEmpty * num_cols * num_rows # empty board
    info_states = defaultdict(lambda: list())
    generate_info_states(board_state, info_states, player, opponent, player_order, num_cols, num_rows, [])
    # save info_states to file
    with open('info_states.txt', 'w') as f:
        for key, value in info_states.items():
            f.write('"' + str(key) + '": ' + str(value) + ',\n')
    # print info_states
    print(info_states)
