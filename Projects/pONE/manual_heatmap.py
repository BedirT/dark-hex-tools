# loads pickle data on given path
import argparse
from Projects.base.util import cPlot

parser = argparse.ArgumentParser()
parser.add_argument("--in_file", "-if", type=str,
                    help="File path to load the results from")
args = parser.parse_args()

cPlot.heat_map(args.in_file)