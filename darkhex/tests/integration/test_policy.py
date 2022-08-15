import pytest
import pyspiel

import darkhex.utils.util as util
import darkhex.policy as policy


def test_mccfr_solver_from_str():
    file_path = "darkhex/tests/integration/fixtures/test_mccfr_solver.pkl"
    data = util.load_file(file_path)
    darkhex_policy = policy.PyspielSolverPolicy(solver=data, board_size=(4, 3))

    game = pyspiel.load_game(
        "dark_hex_ir(num_cols=3,num_rows=4,use_early_terminal=True)")
    state = game.new_initial_state()
    assert darkhex_policy.get_action(state) == 7
    assert len(darkhex_policy.get_action_prob(state)) == 12


def test_mccfr_policy_from_data():
    file_path = "darkhex/tests/integration/fixtures/test_mccfr_policy.pkl"
    darkhex_policy = policy.PyspielSolverPolicy(path=file_path)

    game = pyspiel.load_game(
        "dark_hex_ir(num_cols=3,num_rows=4,use_early_terminal=True)")
    state = game.new_initial_state()
    assert darkhex_policy.get_action(state) == 7
    assert len(darkhex_policy.get_action_prob(state)) == 12
