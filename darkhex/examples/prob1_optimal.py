"""
Setup for calculating all the definite wins for a board
using pONE.
"""
import typing

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
import pyspiel
import seaborn as sns
from darkhex.algorithms.pone_optimal import PoneOptimal
from darkhex.utils.util import (save_file, convert_os_str, calculate_turn,
                                load_file, convert_to_infostate, game_over)


def report_results(num_rows: int, num_cols: int,
                   definite_wins: typing.Dict[str, int]) -> None:
    p0_wins = [x for x in definite_wins.values() if x == 0]
    print(f"{len(p0_wins)} definite wins for player 0")
    # player 1 wins
    p1_wins = [x for x in definite_wins.values() if x == 1]
    print(f"{len(p1_wins)} definite wins for player 1")


def plot(num_rows: int, num_cols: int,
         tot_results: typing.List[typing.Dict[str, int]]) -> None:
    lim = math.ceil((num_cols * num_rows + 1) / 2) + 1
    def_wins_by_num_moves_p0 = np.zeros(lim)
    def_wins_by_num_moves_p1 = np.zeros(lim)
    for h, states in enumerate(tot_results):
        for state, val in states.items():
            if val == 0:
                def_wins_by_num_moves_p0[h] += 1
            elif val == 1:
                def_wins_by_num_moves_p1[h] += 1
    # Plot the results in a bar chart
    df = pd.DataFrame(
        {
            "h": range(lim),
            "Player 0": def_wins_by_num_moves_p0,
            "Player 1": def_wins_by_num_moves_p1,
        },)

    sns.set(style="darkgrid")
    # sns.color_palette("crest", as_cmap=True)
    sns.set_palette("Set2")
    ax = df.plot(x="h", y=["Player 0", "Player 1"], kind="bar", rot=0)
    ax.set_xlabel("Number of hidden cells")
    ax.set_ylabel("Number of definite wins")
    ax.set_title(f"Definite wins by number of moves for {num_rows}x{num_cols}")
    plt.savefig(
        f"darkhex/data/definite_wins/{num_rows}x{num_cols}/definite_wins.png")
    plt.show()


def find_p1_wins(num_rows: int, num_cols: int) -> None:
    definite_wins = {}
    pone = PoneOptimal(num_rows, num_cols)
    tot_results = [{} for _ in range(num_cols * num_rows + 1)]
    results_w_p = [
        [{} for _ in range(num_cols * num_rows + 1)] for _ in range(2)
    ]  # 2 players
    res_0 = pone.search(0)
    for h, states in enumerate(res_0):
        for state, val in states.items():
            if val >= 0:
                definite_wins[state] = val
                tot_results[h][state] = val
                results_w_p[0][h][state] = val
    res_1 = pone.search(1)
    intersection = {}
    for h, states in enumerate(res_1):
        for state, val in states.items():
            if val >= 0:
                if state in definite_wins:
                    intersection[state] = val
                else:
                    definite_wins[state] = val
                    tot_results[h][state] = val
                    results_w_p[1][h][state] = val
    print(f"Found {len(definite_wins)} definite wins")
    print(f"Found {len(intersection)} definite wins in intersection")

    # save to file
    save_file(
        definite_wins,
        f"darkhex/data/definite_wins/{num_rows}x{num_cols}/definite_wins.pkl")
    save_file(
        intersection,
        f"darkhex/data/definite_wins/{num_rows}x{num_cols}/intersection.pkl")
    save_file(
        results_w_p,
        f"darkhex/data/definite_wins/{num_rows}x{num_cols}/results_w_p.pkl")

    new_data = []
    for player in range(2):
        for h, p_data in enumerate(results_w_p[player]):
            for board, res in p_data.items():
                info_state = convert_to_infostate(board, player)
                if not game_over(info_state):
                    # print(f"{info_state} {res}")
                    new_data.append((info_state, res))
    # dont add the header to the csv
    df = pd.DataFrame(new_data, columns=["info_state", "res"])
    df.to_csv(
        f"darkhex/data/definite_wins/{num_rows}x{num_cols}/results_w_p.csv",
        index=False,
        header=False)

    # plot the results
    report_results(num_rows, num_cols, definite_wins)
    plot(num_rows, num_cols, tot_results)


if __name__ == "__main__":
    find_p1_wins(3, 2)
