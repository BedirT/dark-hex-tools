import pytest
import pyspiel
import os

import darkhex.utils.util as util
import darkhex.policy as policy


def test_save_policy_to_file_mccfr_path():
    file_path = "darkhex/tests/integration/fixtures/test_mccfr_policy.pkl"
    darkhex_policy = policy.PyspielSolverPolicy(path=file_path)
    save_path = "darkhex/tests/integration/fixtures/test_mccfr_policy_save.pkl"
    darkhex_policy.save_policy_to_file(save_path)
    assert "test_mccfr_policy_save.pkl" in os.listdir(
        "darkhex/tests/integration/fixtures")
    # delete the created file
    os.remove(save_path)


def test_save_policy_to_file_mccfr_str():
    file_path = "darkhex/tests/integration/fixtures/test_mccfr_policy.pkl"
    darkhex_policy = policy.PyspielSolverPolicy(path=file_path)
    idx = "0"
    while f"test_mccfr_policy_save_{idx}" in os.listdir(util.PathVars.policies):
        # if the file exists, iterate (to avoid overwriting)
        idx = str(int(idx) + 1)
    save_path = f"test_mccfr_policy_save_{idx}"
    darkhex_policy.save_policy_to_file(save_path)
    assert save_path in os.listdir(util.PathVars.policies)
    # delete the created directory
    os.system("rm -rf " + util.PathVars.policies + save_path)
