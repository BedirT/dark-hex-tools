# loads pickle data on given path
import pickle

file_name = 'default_file.pkl'

with open(file_name, 'rb') as f:
    a = pickle.load(f)

for i in a[0]:
    ns = len(i)
    n = i.count('.')
    if n == ns-1 and  a[0][i] != '=':
        print(i, a[0][i])