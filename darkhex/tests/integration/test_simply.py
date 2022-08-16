import os
import pyspiel
import pickle
import darkhex.policy as darkhexPolicy
from darkhex.algorithms.simply import SimPly


def test_simply_plus_imperfect_recall():
    file_path = "darkhex/tests/integration/fixtures/test_mccfr_policy.pkl"
    darkhex_policy = darkhexPolicy.PyspielSolverPolicy(path=file_path)

    simply = SimPly(darkhex_policy,
                    player=0,
                    epsilon=0.1,
                    eta=0.005,
                    frac_limit=20,
                    action_cap=2)
    simply.save_policy("darkhex/tests/integration/fixtures/test_SimPly+.pkl")
    assert os.path.exists("darkhex/tests/integration/fixtures/test_SimPly+.pkl")
    os.remove("darkhex/tests/integration/fixtures/test_SimPly+.pkl")


def test_simply_plus_perfect_recall():
    file_path = "darkhex/tests/integration/fixtures/test_mccfr_policy_perfect_recall.pkl"
    darkhex_policy = darkhexPolicy.PyspielSolverPolicy(path=file_path)

    simply = SimPly(darkhex_policy,
                    player=0,
                    epsilon=0.1,
                    eta=0.005,
                    frac_limit=20,
                    action_cap=2)
    simply.save_policy("darkhex/tests/integration/fixtures/test_SimPly+_pr.pkl")
    assert os.path.exists(
        "darkhex/tests/integration/fixtures/test_SimPly+_pr.pkl")
    os.remove("darkhex/tests/integration/fixtures/test_SimPly+_pr.pkl")
