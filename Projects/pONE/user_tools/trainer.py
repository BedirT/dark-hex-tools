import pickle
from pathlib import Path

from Projects.pONE.pONE import pONE

def train_pONE(out_file, rows, cols):
    p = pONE([rows, cols])

    dct = {
            'results': p.state_results,
            'num_cols': cols,
            'num_rows': cols
        }
        
    find_piece = out_file.rfind('/')
    if find_piece != -1:
        folder_name = 'Exp_Results/pONE/{}x{}/{}'.format(cols, 
            cols, out_file[:find_piece])
        file_name = out_file[out_file.rfind('/')+1:]
    else:
        folder_name = 'Exp_Results/pONE/{}x{}'.format(cols, cols)
        file_name = out_file
    Path(folder_name).mkdir(parents=True, exist_ok=True)
    with open('{}/{}.pkl'.format(folder_name, file_name), 'wb') as f:
        pickle.dump(dct, f)