# Change given current board to open_spiel board
#
# Author: Bedir Tapkan, 2021
#
# Description:
#		This program changes the given board to open_spiel hex board.
#
# Parameters:
#       board: board to be changed
#
# Return Value:
#       new_board: converted board
#
from Projects.base.util.colors import pieces

def convert_to_open_spiel(board, num_rows, num_cols):
    for move, cell in enumerate(board):
        if cell == pieces.C_PLAYER1:
            north_connected = False
            south_connected = False 
            if move < num_cols: # First row
                north_connected = True
            elif move >= num_cols * (num_rows - 1): # Last row
                south_connected = True
            for neighbour in connections(move, num_cols, num_rows):
                if board[neighbour] == pieces.kBlackNorth:
                    north_connected = True
                elif board[neighbour] == pieces.kBlackSouth:
                    south_connected = True
            if north_connected and south_connected:
                board[move] = pieces.kBlackWin
            elif north_connected:
                board[move] = pieces.kBlackNorth
            elif south_connected:
                board[move] = pieces.kBlackSouth
            else:
                board[move] = pieces.kBlack
        elif cell == pieces.C_PLAYER2:
            east_connected = False
            west_connected = False
            if move % num_cols == 0: # First column
                west_connected = True
            elif move % num_cols == num_cols - 1: # Last column
                east_connected = True
            for neighbour in connections(move, num_cols, num_rows):
                if board[neighbour] == pieces.kWhiteWest:
                    west_connected = True
                elif board[neighbour] == pieces.kWhiteEast:
                    east_connected = True
            if east_connected and west_connected:
                board[move] = pieces.kWhiteWin
            elif east_connected:
                board[move] = pieces.kWhiteEast
            elif west_connected:
                board[move] = pieces.kWhiteWest
            else:
                board[move] = pieces.kWhite
    return board

def connections(cell, num_cols, num_rows):
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

def pos_by_coord(num_cols, r, c):
    return num_cols * r + c

new_b = convert_to_open_spiel(['.', 'B', 'W', 'B'], 2, 2)
print(new_b)