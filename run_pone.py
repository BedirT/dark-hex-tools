'''
Sample runner for PONE.
'''

import pickle
from PONE.pone import PONE
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--num_of_rows", "-nr", default=3, type=int,
                    help="Number of rows on the board.")
parser.add_argument("--num_of_cols", "-nc", default=3, type=int,
                    help="Number of columns on the board.")
parser.add_argument("--out_file", "-f", default="default_file", type=str,
                    help="File path to save the resulting list on. Please do not add any extension to file.\
                    here is an example usage:\n\t'filepath/filename'")  
args = parser.parse_args()


p = PONE([args.num_of_rows, args.num_of_cols])
chcc = [(x, p.state_results[h][x]) 
        for h in range(p.num_cells) for x in p.state_results[h]
        if p.state_results[h][x] != '=' ]

with open(args.out_file + '.pkl', 'wb') as f:
    pickle.dump(chcc, f)