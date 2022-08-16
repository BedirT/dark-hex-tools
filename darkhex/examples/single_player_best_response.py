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


def test_br_strategy_large_game(argv):
    start = time.time()
    policy = "4x3_1_ryan_new"
    file_path = f"darkhex/data/strategy_data/{folder}/"
    game = pyspiel.load_game(
        "dark_hex_ir(num_rows=4,num_cols=3,use_early_terminal=True)")
    pyspiel_policy = policy.PartialTabularPolicy(game,
                                                 policy=data["strategy"],
                                                 player=player_id)
    br = best_response.BestResponsePolicyIR(game,
                                            policy=pyspiel_policy,
                                            player_id=1 - player_id)
    br_val, br_strategy = br.get_best_response()
    print(f"Lower bound value: {br_val}")
    report(time.time() - start, 'time')
    report(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, 'memory')
    # save best response policy



if __name__ == "__main__":
    # test_best_response_for_partial_ir_policy()
    # test_br_strategy_full_size()
    app.run(test_br_strategy_large_game)
