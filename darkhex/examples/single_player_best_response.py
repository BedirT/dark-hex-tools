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
import resource
import time
import pyspiel

from open_spiel.python import policy as open_spiel_policy
from open_spiel.python.algorithms import best_response

import darkhex.policy as darkhexPolicy
import darkhex.utils.util as util
from darkhex import logger


def single_player_br_policy_and_value(policy_name: str):
    """Test single player full BR on a small Dark Hex problem."""
    start = time.time()
    darkhex_policy = darkhexPolicy.SinglePlayerTabularPolicy(policy=policy_name)
    if darkhex_policy.is_perfect_recall:
        game = pyspiel.load_game("dark_hex", {
            "num_rows": darkhex_policy.num_rows,
            "num_cols": darkhex_policy.num_cols
        })
    else:
        game = pyspiel.load_game(
        "dark_hex_ir", {
            "num_rows": darkhex_policy.num_rows,
            "num_cols": darkhex_policy.num_cols,
            "use_early_terminal": True
        })
    # Open Spiel PartialTabularPolicy requires a policy with tuples:
    # info_state -> [(action, probability)]
    # we have the function util.policy_dict_to_policy_tuple() to convert
    # os_tuple_policy = util.policy_dict_to_policy_tuple(darkhex_policy.policy)
    pyspiel_policy = open_spiel_policy.PartialTabularPolicy(
        game, policy=darkhex_policy.policy, player=darkhex_policy.player)
    br = best_response.BestResponsePolicyIR(game,
                                            policy=pyspiel_policy,
                                            player_id=1 - darkhex_policy.player)
    br_value, br_strategy = br.get_best_response()

    logger.info(f"Lower bound value: {br_value}")
    logger.debug(f"Time: {time.time() - start}")
    logger.debug(
        f"Peak Memory: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}")

    # save best response policy
    br_policy = darkhexPolicy.SinglePlayerTabularPolicy(
        policy=br_strategy,
        player=1 - darkhex_policy.player,
        board_size=darkhex_policy.board_size,
        initial_state=game.new_initial_state())
    br_policy.save_policy_to_file(policy_name, is_best_response=True)


if __name__ == "__main__":
    single_player_br_policy_and_value("4x3_white_hp_pr")
