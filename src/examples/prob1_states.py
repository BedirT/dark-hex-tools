"""
Setup for calculating all the definite wins for a board
using pONE.
"""
from algorithms.pONE import PONE
from utils.util import save_file


def main():
    # create game
    num_rows = 3
    num_cols = 3
    game = pyspiel.load_game(f"dark_hex_ir(num_cols={num_cols},num_rows={num_rows})")
    pone = PONE(game, num_rows, num_cols)
    # get definite win states
    definite_wins = pone.get_definite_win_states()
    # save to file
    save_file(definite_wins, f"data/definite_wins/{num_rows}x{num_cols}.pkl")
    # report results
    print(f"{num_rows}x{num_cols}")
    print(f"{len(definite_wins[0])} definite win states for player 0")
    print(f"{len(definite_wins[1])} definite win states for player 1")
