'''
Sample file for using tree_run.py
'''
import sys
sys.path.append('../../')
from Projects.SVerify.algorithms.tree_run import TreeRun

def main():
    file_name = '4x3_boundsOver7'
    tree_run = TreeRun(file_name)
    tree_run.tree_run()

if __name__ == '__main__':
    main()