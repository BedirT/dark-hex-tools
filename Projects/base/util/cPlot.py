import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle

def heat_map(in_file):
    with open(in_file, 'rb') as f:
        dct = pickle.load(f)

    results = dct['results']
    num_cols = dct['num_cols']
    num_rows = dct['num_rows']
    num_cells = num_rows * num_cols
    all_total = 0; new_data_b = []; new_data_tot = []
    e_size = num_cells + 1
    h_size = num_cells//2 + 1

    y_size=range(e_size)
    x_size=range(h_size)
    round_tot_b_h = [0] * h_size
    for e in y_size:
        round_tot_b = 0
        for h in x_size:
            new_data_b.append(len([x for x in results[e][h] if results[e][h][x] != '=']))
            new_data_tot.append(len(results[e][h]))
            round_tot_b += new_data_b[-1]
            round_tot_b_h[h] += new_data_tot[-1]
        new_data_b.append(round_tot_b)
        all_total += round_tot_b
    round_tot_b_h.append(all_total)
    new_data_b.extend(round_tot_b_h)

    df = pd.DataFrame(np.array(new_data_b).reshape(e_size+1, h_size+1),
                    index=[*y_size, 'TOT'], columns=[*x_size, 'TOT'])

    mask = np.zeros((e_size+1, h_size+1))
    mask[:,-1] = True
    mask[-1,:] = True

    sns.heatmap(df, mask=mask, cmap='Blues')
    sns.heatmap(df, alpha=0, cbar=False, annot=True, cmap='Blues', 
                    fmt='g', annot_kws={"size": 12, "color":"g"})

    plt.savefig('Visual/test.png')
    plt.show()