import pyspiel


def test_mccfr_os():
    parameters = {"num_rows": 4, "num_cols": 3, "use_early_terminal": True}
    game = pyspiel.load_game("dark_hex_ir", parameters)

    solver = pyspiel.OutcomeSamplingMCCFRSolver(game)

    for i in range(int(1e3)):
        solver.run_iteration()
