# loads pickle data on given path
import pickle
import argparse
from Projects.base.util import cPlot

parser = argparse.ArgumentParser()
parser.add_argument("--in_file", "-if", type=str,
                    help="File path to load the results from")
args = parser.parse_args()

with open(args.in_file, 'rb') as f:
    dct = pickle.load(f)

cPlot.heat_map(dct['results'], dct['num_cols'], dct['num_rows'])