"""
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
"""
import os
from collections import Counter, defaultdict
from copy import deepcopy

import numpy as np
from util.colors import colors
from utils.isomorphic import isomorphic_single
from utils.util import numeric_action, random_selection, save_file, updated_board

input_list = []
COUNTER = 0


def printBoard(board_state, num_cols, num_rows):
    """
    Method for printing the board in a nice format.
    """
    num_cells = num_cols * num_rows
    the_cell = 0  # The cell we are currently printing.
    print(colors.C_PLAYER1, end="  ")
    for i in range(num_cols):
        print("{0: <3}".format(chr(ord("a") + i)), end="")
    print(colors.ENDC)
    print(colors.BOLD + colors.C_PLAYER1 + " " + "-" * (num_cols * 3 + 1) + colors.ENDC)
    for cell in range(num_cells):
        if cell % num_cols == 0:  # first col
            print(
                colors.BOLD
                + colors.C_PLAYER2
                + str(cell // num_cols + 1)
                + "\\ "
                + colors.ENDC,
                end="",
            )
        if board_state[cell] in pieces.black_pieces:
            clr = colors.C_PLAYER1
        elif board_state[cell] in pieces.white_pieces:
            clr = colors.C_PLAYER2
        else:
            clr = colors.NEUTRAL
        if board_state[cell] == pieces.kEmpty:
            print(clr + "{0: <3}".format(the_cell) + colors.ENDC, end="")
        else:
            print(clr + "{0: <3}".format(board_state[cell]) + colors.ENDC, end="")
        the_cell += 1
        if cell % num_cols == num_cols - 1:  # last col
            print(
                colors.BOLD
                + colors.C_PLAYER2
                + "\\"
                + pieces.kWhite
                + "\n"
                + (" " * (cell // num_cols))
                + colors.ENDC,
                end=" ",
            )
    print(
        colors.BOLD + colors.C_PLAYER1 + "  " + "-" * (num_cols * 3 + 1) + colors.ENDC
    )
    print(
        colors.BOLD
        + colors.C_PLAYER1
        + " " * (num_rows + 4)
        + "{0: <3}".format(pieces.kBlack) * num_cols
        + colors.ENDC
    )
    print(colors.BOLD + colors.QUESTIONS + "\n" + colors.ENDC)


def save_input(input_list):
    """
    Save the input to a file. If the file already exists,
    append the input to the file.

    - input_list: The input to save.
    """
    with open("extra/input_new.txt", "a") as f:
        f.write(" ".join(input_list) + "\n")


def get_moves(board_state, num_cols, num_rows, fill_randomly):
    """
    Get moves for the current board state from the user.
    Seperate the moves by spaces.

    - board_state: The current board state.
    """
    if fill_randomly:
        moves, probs = random_selection(board_state)
        return moves, probs, fill_randomly

    # TODO: FIX THE PROBABILITIES
    # Print the board state to the user.
    printBoard(board_state, num_cols, num_rows)
    # sleep(0.1)
    # Get the moves and (if wanted) probabilities of those moves from the user.
    moves_and_probs = input(
        colors.BOLD
        + colors.QUESTIONS
        + "Enter moves and probabilities (separated by spaces)\n"
        + "For the single entries (one action) no need for the probabilites\n"
        + "Start the entry with = for equiprobable entries (no prob entries)\n"
        + '"r" for random selection for the rest of the branch\n'
        + '"exit" for exitting program\n:'
        + colors.ENDC
    )
    moves_and_probs = moves_and_probs.strip().split(" ")

    if moves_and_probs[0] == "exit":
        exit()

    if moves_and_probs[0] == "r":
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
            log.error("Invalid move: {}".format(moves_and_probs))
            return get_moves(board_state, num_cols, num_rows, fill_randomly)
    elif moves_and_probs[0] == "=":
        # Equaprobability
        # No probabilities given.
        moves = [numeric_action(x, num_cols) for x in moves_and_probs[1:]]
        if False in moves:
            return get_moves(board_state, num_cols, num_rows, fill_randomly)
        probs = [1 / len(moves)] * len(moves)
    else:
        moves = []
        probs = []
        for i in range(0, len(moves_and_probs), 2):
            a = numeric_action(moves_and_probs[i], num_cols)
            if a:
                moves.append(a)
                probs.append(float(moves_and_probs[i + 1]))
            else:
                log.warning("Invalid move: {}".format(moves_and_probs))
                return get_moves(board_state, num_cols, num_rows, fill_randomly)

    moves = list(map(int, moves))
    probs = list(map(float, probs))
    save_input(moves_and_probs)

    return moves, probs, fill_randomly


def is_collusion_possible(board_state, player):
    """
    Check if a collusion is possible.

    - board_state: The current board state.
    """
    # Get the number of pieces on the board.
    count = Counter(board_state)
    if player == pieces.kWhite:
        player_pieces = sum([s for x, s in count.items() if x in pieces.white_pieces])
        opponent_pieces = sum([s for x, s in count.items() if x in pieces.black_pieces])
        return opponent_pieces <= player_pieces
    player_pieces = sum([s for x, s in count.items() if x in pieces.black_pieces])
    opponent_pieces = sum([s for x, s in count.items() if x in pieces.white_pieces])
    print(player_pieces, opponent_pieces)
    return opponent_pieces < player_pieces


def game_over(board_state, player):
    """
    Check if the game is over.

    - board_state: The current board state.
    """
    if board_state.count(pieces.kBlackWin) + board_state.count(pieces.kWhiteWin) == 1:
        return True
    ct = Counter(board_state)
    empty_cells = ct[pieces.kEmpty]
    if player == pieces.kBlack:
        opponent_pieces = sum([s for x, s in ct.items() if x in pieces.white_pieces])
        player_pieces = sum([s for x, s in ct.items() if x in pieces.black_pieces])
        if opponent_pieces + empty_cells == player_pieces:
            return True
    else:
        opponent_pieces = sum([s for x, s in ct.items() if x in pieces.black_pieces])
        player_pieces = sum([s for x, s in ct.items() if x in pieces.white_pieces])
        if opponent_pieces + empty_cells == player_pieces + 1:
            return True
    return False


def moves_and_probs(moves, probs):
    if probs is None:
        # equal probability for all moves
        probs = [1 / len(moves)] * len(moves)
    else:
        assert len(moves) == len(probs)
    # return moves and probs in a list of tuples
    # so 0th element will be (move[0], prob[0])
    return list(zip(moves, probs))


def traverse_the_game(
    board_state,
    info_states,
    player,
    opponent,
    num_cols,
    num_rows,
    isomorphic,
    fill_randomly,
):
    """
    Recursively call the generate_info_states function, one for a
    collusion if possible, and one for a non-collusion. Moves are specified
    by the user for each board state.

    - board_state: The current board state.
    - info_states: The dictionary of information states and corresponding
    moves.
    - player: The player we are generating the information states for.
    """
    # Check if the game is over.
    if game_over(board_state, player):
        return
    # Get the moves for the current board state. (Try until valid options are provided)
    valid_moves = False
    moves = []
    probs = []
    while not valid_moves:
        valid_moves = True
        moves, probs, fill_randomly = get_moves(
            board_state, num_cols, num_rows, fill_randomly
        )
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
                    if xxx == "continue":
                        break
                break
            moves_and_boards[str(move) + opponent] = new_board
            moves_and_boards[str(move) + player] = new_board_2
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
                    ls.append((move, prob / 2))
                    d[move] = len(ls) - 1
                else:
                    ls[d[move]] = (move, ls[d[move]][1] + prob / 2)
            for move, prob in info_states[iso_state]:
                if move not in d:
                    ls.append((move, prob / 2))
                    d[move] = len(ls) - 1
                else:
                    ls[d[move]] = (move, ls[d[move]][1] + prob / 2)
            info_states[iso_state] = ls
    # If a collusion is possible
    collusion_possible = is_collusion_possible(board_state, player)
    # For each move, recursively call the traverse_the_game function.
    for move in moves:
        printBoard(board_state, num_cols, num_rows)
        if collusion_possible:
            new_board = moves_and_boards[str(move) + opponent]
            if new_board not in info_states:
                traverse_the_game(
                    new_board,
                    info_states,
                    player,
                    opponent,
                    num_cols,
                    num_rows,
                    isomorphic,
                    fill_randomly,
                )
        # Generate the information state for a non-collusion.
        new_board = moves_and_boards[str(move) + player]
        if new_board not in info_states:
            traverse_the_game(
                new_board,
                info_states,
                player,
                opponent,
                num_cols,
                num_rows,
                isomorphic,
                fill_randomly,
            )


def generate_information_states(
    num_cols, num_rows, player, isomorphic, board_state=None, file_path=None
):
    """
    Traverse the board state and generate the information states, with
    action probabilities.
    """
    # GAME SETUP
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # TODO: USE OPEN_SPIEL RELATED VARIABLES
    opponent = pieces.kBlack if player == pieces.kWhite else pieces.kWhite

    if board_state == None:
        board_state = pieces.kEmpty * num_cols * num_rows  # empty board

    if len(board_state) != num_cols * num_rows:
        raise Exception("Board state is not the correct size.")
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    info_states = defaultdict(lambda: list())
    traverse_the_game(
        board_state,
        info_states,
        player,
        opponent,
        num_cols,
        num_rows,
        isomorphic,
        False,
    )
    log.info("Successfully generated information states.")
    log.info(f"Number of states: {len(info_states)}")

    # save the data into the file path using dill
    data = {
        "num_cols": num_cols,
        "num_rows": num_rows,
        "player": player,
        "isomorphic": isomorphic,
        "strategy": dict(info_states),
        "initial_board": board_state,
    }
    if file_path == None:
        file_path = f"Data/pre_process/{num_cols}x{num_rows}_{player}_{isomorphic}"
        # if the file already exists, add a number to the end of the file name
        i = 1
        while os.path.exists(file_path):
            file_path = (
                f"Data/pre_process/{num_cols}x{num_rows}_{player}_{isomorphic}_{i}"
            )
            i += 1
    save_file(data, file_path)
    log.info(f"Saved information states to {file_path}")
