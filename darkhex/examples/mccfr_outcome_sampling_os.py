"""
Example use of MCCFR algorithm from OpenSpiel.

This example uses the Outcome Sampling version of MCCFR. For more details, see
the OpenSpiel documentation.
"""
import pyspiel
from tqdm import tqdm

import darkhex.policy as policy


def run_mccfr_os(num_iterations: int, policy_name: str):
    game_str = "dark_hex_ir"
    parameters = {"num_rows": 4, "num_cols": 3, "use_early_terminal": True}
    game = pyspiel.load_game(game_str, parameters)

    solver = pyspiel.OutcomeSamplingMCCFRSolver(game)

    for i in tqdm(range(num_iterations)):
        solver.run_iteration()

    darkhex_policy = policy.PyspielSolverPolicy(solver=solver,
                                                board_size=(4, 3))
    darkhex_policy.save_policy_to_file(policy_name)


if __name__ == "__main__":
    policy_name = "mccfr_os_1e3"
    run_mccfr_os(int(1e3), policy_name)
