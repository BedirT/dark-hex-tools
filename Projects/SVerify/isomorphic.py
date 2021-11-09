'''
Converts a given darkhex board strategy in the form
of a dictionry (information_state: [actions]) with its
isomorphic equivalent.
'''
from Projects.base.game.hex import pieces

def convert_piece(given_piece):
    # converts the north pieces to south and vice versa
    # west pieces to east and vice versa
    if given_piece == pieces.kBlackNorth:
        return pieces.kBlackSouth
    elif given_piece == pieces.kBlackSouth:
        return pieces.kBlackNorth
    elif given_piece == pieces.kWhiteWest:
        return pieces.kWhiteEast
    elif given_piece == pieces.kWhiteEast:
        return pieces.kWhiteWest
    else:
        return given_piece

def isomorphic(board_strategy):
    # find isomorphic placements
    iso_strategy = {}
    for dh_board, actions in board_strategy.items():
        new_board, new_moves = isomorphic_single(dh_board, actions)
        iso_strategy[''.join(new_board)] = new_moves
    return iso_strategy

def isomorphic_single(dh_board, actions, probs):
    # find isomorphic placements
    new_board = [pieces.kEmpty] * len(dh_board)
    for i in range(len(dh_board)):
        iso_index = len(dh_board)-1-i
        new_board[iso_index] = convert_piece(dh_board[i])
    new_moves = []
    for action, prob in zip(actions, probs):
        new_moves.append((len(dh_board)-1-action, prob))
    return ''.join(new_board), new_moves
        