"""
Setup for calculating all the definite wins for a board
using pONE.
"""
import typing

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyspiel
import seaborn as sns
from darkhex.algorithms.pone_optimal import PoneOptimal
from darkhex.utils.util import save_file, convert_os_str, calculate_turn


def report_results(
    num_rows: int, num_cols: int, definite_wins: typing.Dict[str, int]
) -> None:
    p0_wins = [s for s in definite_wins if s[1] == "0"]
    print(f"{len(p0_wins)} definite wins for player 0")
    # player 1 wins
    p1_wins = [s for s in definite_wins if s[1] == "1"]
    print(f"{len(p1_wins)} definite wins for player 1")


def plot(num_rows: int, num_cols: int, definite_wins: typing.Dict[str, int]) -> None:
    def_wins_by_num_moves_p0 = np.zeros(num_cols * num_rows)
    def_wins_by_num_moves_p1 = np.zeros(num_cols * num_rows)
    for state in definite_wins:
        num_empty_cells = state.count(".")
        if state[1] == "0":
            def_wins_by_num_moves_p0[num_empty_cells - 1] += 1
        else:
            def_wins_by_num_moves_p1[num_empty_cells - 1] += 1
    # Plot the results in a bar chart
    df = pd.DataFrame(
        {
            "Player 0": def_wins_by_num_moves_p0,
            "Player 1": def_wins_by_num_moves_p1,
        }
    )
    # x-axis starts from 1
    df.index += 1
    df.plot.bar(rot=0)
    plt.title(f"Definite wins by number of moves for {num_rows}x{num_cols}")
    plt.xlabel("Number of empty cells")
    plt.ylabel("Number of definite wins")
    # save the plot
    plt.savefig(f"darkhex/data/definite_wins/{num_rows}x{num_cols}.png")
    plt.show()


def find_p1_wins(num_cols: int, num_rows: int) -> None:
    pone = PoneOptimal(num_rows, num_cols, 1)
    res = pone.search()
    definite_wins = {}
    for h in res:
        for state, val in h.items():
            if val >= 0:
                definite_wins[state] = val
    pone = PoneOptimal(num_rows, num_cols, 0)
    res = pone.search()
    intersection = {}
    for h in res:
        for state, val in h.items():
            if val >= 0:
                if state in definite_wins:
                    intersection[state] = val
                else:
                    definite_wins[state] = val
    # print(definite_wins)
    print(f"Found {len(definite_wins)} definite wins")
    # print(intersection)
    print(f"Found {len(intersection)} definite wins in intersection")

    # save to file
    save_file(definite_wins, f"darkhex/data/dw_{num_rows}x{num_cols}.pkl")

    # report_results(num_rows, num_cols, definite_wins)
    # plot(num_rows, num_cols, definite_wins)


if __name__ == "__main__":
    find_p1_wins(3, 3)
