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

"""Example use of the C++ MCCFR algorithms on Kuhn Poker.

This examples calls the underlying C++ implementations via the Python bindings.
Note that there are some pure Python implementations of some of these algorithms
in python/algorithms as well.
"""
import pickle
import pyspiel
from tqdm import tqdm
import numpy as np
import os
import time


def main(_):
  num_rows = 4
  num_cols = 3
  pone = FLAGS.pone
  if FLAGS.game == "dark_hex_ir":
    ir_text = "ir"
    pone_text = "pone" if pone else "npone"
    parameters = {"num_rows": num_rows,
                  "num_cols": num_cols,
                  "use_early_terminal": pone}
  else:
    ir_text = "pr"
    pone_text = "npone"
    parameters = {"num_rows": num_rows,
                  "num_cols": num_cols}
  game = pyspiel.load_game(FLAGS.game, parameters)
  
  folder_path = f"tmp/Arena/arena_mccfr_{num_rows}x{num_cols}_{pone_text}_{ir_text}_{FLAGS.iterations}"
  # create folder if it doesn't exist
  if not os.path.exists(folder_path):
    os.makedirs(folder_path)

  solver = pyspiel.OutcomeSamplingMCCFRSolver(game)
  evals = []
  cur_time = time.time()
  for i in tqdm(range(FLAGS.iterations)):
    solver.run_iteration()
    if i % FLAGS.eval_freq == 0 or i == FLAGS.iterations - 1:
      policy = solver.average_policy()

      _eval = run_random_games(game, policy, FLAGS.num_eval_games)
      print(f"Ep {i}; Rand eval: {_eval}")

  print("Persisting the model...")
  with open(f"{folder_path}/solver.pkl", "wb") as file:
    pickle.dump(solver, file, pickle.HIGHEST_PROTOCOL)

  evals.append(_eval)
  with open(f"{folder_path}/eval.pkl", "wb") as file:
    pickle.dump(evals, file, pickle.HIGHEST_PROTOCOL)


def run_random_games(game, policy, num_games):
  """Runs random games and returns average score."""
  scores_as_p = [0., 0.]
  games_per_p = num_games // 2
  
  for _ in range(games_per_p):
    scores_as_p[0] += run_random_game(game, policy, 0) / games_per_p
    scores_as_p[1] += run_random_game(game, policy, 1) / games_per_p
  return scores_as_p


def run_random_game(game, policy, player):
  """Runs a single random game and returns score as player."""
  state = game.new_initial_state()
  while not state.is_terminal():
    legal_actions = state.legal_actions()
    if state.current_player() == player:
      action_probs = policy.action_probabilities(state)
      action_probs = [action_probs[a] for a in legal_actions]
    else:
      action_probs = [1. / len(legal_actions)] * len(legal_actions)
    action = np.random.choice(legal_actions, p=action_probs)
    state.apply_action(action)
  return state.returns()[player]


if __name__ == "__main__":
  app.run(main)
