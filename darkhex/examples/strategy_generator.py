"""
Example of a strategy generator using generate_info_states
"""
from algorithms.generate_info_states import generate_information_states


def main():
    generate_information_states(
        num_cols=3,
        num_rows=4,
        player=pieces.kBlack,
        isomorphic=True,
        board_state=".yq.y...xp..",
        file_path="data/strategy_data/4x3_subgame/game_info.pkl",
    )


if __name__ == "__main__":
    main()
