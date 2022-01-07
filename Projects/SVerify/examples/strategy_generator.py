'''
Example of a strategy generator using generate_info_states
'''
import sys
sys.path.append('../../')

from Projects.SVerify.algorithms.generate_info_states import generate_information_states
from Projects.base.game.hex import pieces

def main():
    generate_information_states(
        num_cols=3,
        num_rows=4,
        player=pieces.kBlack,
        isomorphic=True,
        board_state='....x.......',
        file_path='Data/strategy_data/4x3_boundsOver7/game_info.pkl'
    )

if __name__ == '__main__':
    main()
