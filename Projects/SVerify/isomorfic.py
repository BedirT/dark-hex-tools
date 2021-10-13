'''
Converts a given darkhex board strategy in the form
of a dictionry (information_state: [actions]) with its
isomorphic equivalent.
'''
from Projects.base.game.hex import pieces

def isomorphic(board_strategy):
    # find isomorphic placements
    iso_strategy = {}
    for dh_board, actions in board_strategy.items():
        new_board = [pieces.kEmpty] * len(dh_board)
        for i in dh_board:
            iso_index = len(dh_board)-1-i
            new_board[iso_index] = dh_board[i]
        new_moves = []
        for action in actions:
            new_moves.append(len(dh_board)-1-action)
        iso_strategy[''.join(new_board)] = new_moves
    return iso_strategy  