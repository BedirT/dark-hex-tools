# loads pickle data on given path
import pickle

file_name = 'default_file.pkl'

with open(file_name, 'rb') as f:
    a = pickle.load(f)

for i, e in enumerate(a):
    for j, h in enumerate(e):
        for x in h:
            if h[x] != '=':
                print(x, h[x], '| h=', j, ' | e=', i)