""" Testing the benefits of using pone """

import pyspiel
import time
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from darkhex.algorithms.gel_all_information_states import get_all_information_states


def num_states_encountered():
    """ Returns the number of possible states to encounter in a game. """
    num_rows = 4
    num_cols = 3
    # No pone
    start = time.time()
    game = pyspiel.load_game(
        f"dark_hex_ir(num_rows={num_rows},num_cols={num_cols})")
    info_states = get_all_information_states(game,
                                             num_rows,
                                             num_cols,
                                             include_terminal_states=True,
                                             get_data=False)
    game1_len = len(info_states)
    time1 = time.time() - start
    print(f'Number of states (No pone): {game1_len}')
    print(f'Time: {time1}')
    # Pone
    start = time.time()
    game = pyspiel.load_game(
        f"dark_hex_ir(num_rows={num_rows},num_cols={num_cols},use_early_terminal=True)"
    )
    info_states = get_all_information_states(game,
                                             num_rows,
                                             num_cols,
                                             include_terminal_states=True,
                                             get_data=False)
    game2_len = len(info_states)
    time2 = time.time() - start
    print(f'Number of states (Pone): {game2_len}')
    print(f'Time: {time2}')

    # plot number of states encountered
    plt.figure(figsize=(3, 5))
    sns.color_palette("tab10")
    sns.set_style("darkgrid")

    x = ['p-one', 'no p-one']
    y = [game2_len / 100000, game1_len / 100000]
    plt.bar(x,
            y,
            width=.9,
            color=sns.color_palette("tab10")[:2],
            align='center')
    plt.ylabel('Number of states encountered (x100000)')
    plt.title(f'Number of states\nfor p-one vs no p-one')
    plt.tight_layout()
    plt.savefig('darkhex/experiments/results/pone_vs_npone_num_states.pdf')

    # plot time
    plt.figure(figsize=(3, 5))

    x = ['p-one', 'no p-one']
    y = [time2, time1]
    plt.bar(x,
            y,
            width=.9,
            color=sns.color_palette("tab10")[:2],
            align='center')
    plt.ylabel('Time (s)')
    plt.title(f'Time\nfor p-one vs no p-one')
    plt.tight_layout()
    plt.savefig('darkhex/experiments/results/pone_vs_npone_time.pdf')


if __name__ == "__main__":
    num_states_encountered()
