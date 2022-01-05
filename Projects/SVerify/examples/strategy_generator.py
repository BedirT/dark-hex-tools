'''
Example of a strategy generator using generate_info_states
'''
import sys
sys.path.append('../../')

from Projects.SVerify.algorithms.generate_info_states import generate_information_states
from Projects.base.game.hex import pieces

def main():
    generate_information_states(
        num_cols=2,
        num_rows=2,
        player=pieces.kBlack,
        isomorphic=True,
        # board_state='....x.......',
        file_path='Data/pre_process/2x2_test'
    )

if __name__ == '__main__':
    main()
