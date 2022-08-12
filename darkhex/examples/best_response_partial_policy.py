# Copyright 2019 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for open_spiel.python.algorithms.best_response_imperfect_recall."""

import numpy as np
import dill
import time
import resource
from absl import flags
from absl import app

from open_spiel.python import policy
from open_spiel.python.algorithms import best_response
import pyspiel

FLAGS = flags.FLAGS
flags.DEFINE_string("path", None, "Path to the strategy")

def report(data, type: str) -> None:
    """ Prints the report in a pretty format given the data
    and the type. Valid types are = ['memory', 'time']

    Time: Output of time.time()
    Memory: Output of process.memory_info().rss
    """
    bold = "\033[1m"
    red = "\033[1;31m"
    yellow = "\033[1;33m"
    green = "\033[1;32m"
    end = "\033[0m"
    with open("tmp/report.txt", "a") as f:
        if type == 'memory':
            report = f"{bold}{green}Memory usage:\t{end}"
            gbs = data // (1024**2)
            mbs = (data - gbs * 1024**2) // 1024
            kbs = (data - gbs * 1024**2 - mbs * 1024)
            if gbs > 0:
                report += f"{gbs} {red}GB{end} "
            if mbs > 0:
                report += f"{mbs} {red}MB{end} "
            if kbs > 0:
                report += f"{kbs} {red}KB{end} "
            report += f"\n"
            print(report)
            f.write(report)
        elif type == 'time':
            report = f"{bold}{green}Time taken:\t{end}"
            m, s = divmod(data, 60)
            h, m = divmod(m, 60)
            h, m, s = int(h), int(m), int(s)
            if h > 0:
                report += f"{h}:{m:02d}:{s:02d} {yellow}hours{end}\n"
            elif m > 0:
                report += f"{m}:{s:02d} {yellow}minutes{end}\n"
            else:
                report += f"{s:02d} {yellow}seconds{end}\n"
            print(report)
            f.write(report)
        else:
            report = f"{red}{bold}Invalid type given to report(). Valid types are = ['memory', 'time']{end}\n"
            print(report)
            f.write(report)


def test_best_response_for_partial_ir_policy():
    game = pyspiel.load_game("phantom_ttt_ir")
    test_player = 0
    tabular_policy = {
        # infostate: [(action, prob)]
        "P0 ...\n...\n...": [(4, 1.0)],
        "P0 ...\n.x.\n...": [(0, 1.0)],
        "P0 o..\n.x.\n...": [(1, 1.0)],
        "P0 ox.\n.x.\n...": [(7, 1.0)],
        "P0 ox.\n.x.\n.o.": [(6, 1.0)],
        "P0 ox.\n.x.\nxo.": [(2, 1.0)],
        "P0 oxo\n.x.\nxo.": [(3, 1.0)],
        "P0 oxo\nxx.\nxo.": [(5, 1.0)],
        "P0 oxo\nxxo\nxo.": [(8, 1.0)],
        "P0 x..\n.x.\n...": [(8, 1.0)],
        "P0 x..\n.x.\n..o": [(6, 1.0)],
        "P0 x..\n.x.\no.o": [(7, 1.0)],
        "P0 x..\n.x.\noxo": [(1, 1.0)],
        "P0 xo.\n.x.\noxo": [(3, 1.0)],
        "P0 xo.\nxx.\noxo": [(5, 1.0)],
        "P0 xo.\nxxo\noxo": [(2, 1.0)],
        "P0 x..\n.x.\nx.o": [(2, 1.0)],
        "P0 x.o\n.x.\nx.o": [(3, 1.0)],
        "P0 x.o\nox.\nx.o": [(5, 1.0)],
        "P0 x.o\noxx\nx.o": [(1, 1.0)],
        "P0 xoo\noxx\nx.o": [(7, 1.0)],
    }
    pyspiel_policy = policy.PartialTabularPolicy(game, tabular_policy,
                                                 test_player)
    br = best_response.BestResponsePolicyIR(game,
                                            policy=pyspiel_policy,
                                            player_id=1 - test_player)
    state_test = game.new_initial_state()
    state_test.apply_action(0)
    br_pi = br.value(state_test)
    print(br_pi)


def test_br_strategy_full_size():
    start = time.time()
    file_path = "tmp/phantom_ttt_p1_simplified.pkl"
    data = dill.load(open(file_path, "rb"))
    game = pyspiel.load_game("phantom_ttt_ir")
    player_id = data["player"]
    pyspiel_policy = policy.PartialTabularPolicy(game,
                                                 policy=data["strategy"],
                                                 player=player_id)
    br = best_response.BestResponsePolicyIR(game,
                                            policy=pyspiel_policy,
                                            player_id=1 - player_id)
    state_test = game.new_initial_state()
    # state_test.apply_action(0)
    br_pi = br.value(state_test)
    print(br_pi)
    report(time.time() - start, 'time')
    report(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, 'memory')


def test_br_strategy_large_game(argv):
    start = time.time()
    # folder = "p1_2_0.1_0.0_0"
    folder = FLAGS.path
    # folder = "p1_2_0.1_0.05_20"
    # file_path = f"../darkhex/darkhex/data/strategy_data/4x3_mccfr/{folder}/game_info.pkl"
    folder = "4x3_1_def_fixed"
    file_path = f"../darkhex/darkhex/data/strategy_data/{folder}/"
    import os
    if not os.path.exists(f"tmp/real_br/{folder}"):
        os.makedirs(f"tmp/real_br/{folder}")
    data = dill.load(open(file_path + 'game_info.pkl', "rb"))
    game = pyspiel.load_game(
        "dark_hex_ir(num_rows=4,num_cols=3,use_early_terminal=True)")
    player_id = data["player"]
    pyspiel_policy = policy.PartialTabularPolicy(game,
                                                 policy=data["strategy"],
                                                 player=player_id)
    br = best_response.BestResponsePolicyIR(game,
                                            policy=pyspiel_policy,
                                            player_id=1 - player_id)
    state_test = game.new_initial_state()
    # state_test.apply_action(0)
    br_val, br_strategy = br.get_best_response()
    print(f"Lower bound value: {br_val}")
    report(time.time() - start, 'time')
    report(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, 'memory')
    # save the data to a file
    with open(f"{file_path}/br_data.pkl", "wb") as f:
        data = {
            "br_value": br_val,
            "br_strategy": br_strategy,
        }
        dill.dump(data, f)


if __name__ == "__main__":
    # test_best_response_for_partial_ir_policy()
    # test_br_strategy_full_size()
    app.run(test_br_strategy_large_game)
