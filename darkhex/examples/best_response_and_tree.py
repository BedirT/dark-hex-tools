import pyspiel
from darkhex.algorithms.best_response import BestResponse
from darkhex.algorithms.tree_generator import TreeGenerator
from darkhex.algorithms.tree_run import TreeRun
from darkhex.utils.util import load_file


def main():
    file_name = "simplified_4x3_mccfr_p0_new"
    file_path = f"darkhex/data/strategy_data/{file_name}/"
    data = load_file(file_path + "game_info.pkl")
    game = pyspiel.load_game(
        f'dark_hex_ir(num_cols={data["num_cols"]},num_rows={data["num_rows"]})'
    )

    # create best response object
    br = BestResponse(
        game,
        data["player"],
        data["initial_board"],
        data["num_cols"],
        data["strategy"],
        file_path + "opp_strategy.pkl",
    )

    # calculate best response value
    br_value = br.best_response()
    print(f"Best response value: {br_value}")

    # create tree generator object
    TreeGenerator(game, file_name)

    # create tree run object
    tree_run = TreeRun(file_name)
    tree_run.tree_run()


if __name__ == "__main__":
    main()
