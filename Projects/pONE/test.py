import pickle 

file_name = 'Exp_Results/pONE/3x3/default_file.pkl'

with open(file_name, 'rb') as f:
    dct = pickle.load(f)

results = dct['results']
num_cols = dct['num_cols']
num_rows = dct['num_rows']

nc = num_cols*num_rows

for e in range(nc):
    for h in range(nc//2):
        for x in results[e][h]:
            if results[e][h][x] == 'W' and h != 0:
                print(x, h)