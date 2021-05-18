import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def heat_map(results, num_cols, num_rows):
    all_total = 0; new_data_b = []; new_data_tot = []
    y_size=range(num_rows)
    x_size=range(num_cols)
    round_tot_b_h = [0] * num_cols
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

    df = pd.DataFrame(np.array(new_data_b).reshape(num_rows+1, num_cols+1),
                    index=[*y_size, 'TOT'], columns=[*x_size, 'TOT'])

    mask = np.zeros((num_rows+1, num_cols+1))
    mask[:,-1] = True
    mask[-1,:] = True

    sns.heatmap(df, mask=mask, cmap='Blues')
    sns.heatmap(df, alpha=0, cbar=False, annot=True, cmap='Blues', 
                    fmt='g', annot_kws={"size": 12, "color":"g"})

    plt.show()