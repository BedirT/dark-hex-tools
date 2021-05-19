# pONE GUIDE

This is a short guide on how to use pONE, and related code that are included in the repository.

### Generating the data

Since github has limit on size of the files, I have not uploaded the 4x3 (should be around ~150mb). Therefor before doing anything you first need to generate the data for the board size you are planning to use. We have **runner.py** for this purpose. It takes 3 inputs:

- **Number of Rows (-nr / --num_of_rows):** Number of rows for the hex board. Do not forget that Black (first player) is connecting the north/suuth therefore if rows are more then columns first player is is going the longer distance.
- **Number of Columns (-nc / --num_of_cols):** Number of columns for the hex board.
- **Saving destination (-f / --out_file):** The destination for the data to be saved. If not specified it will be saved as **default_file.pkl**. Please be adviced that no matter what the file will be saved in **Exp_Results/pONE/*row_size*x*col_size*/*file_name*.pkl**. We are adding the '.pkl' extension so you do not need to add it exclusively to the name.

Here let's see an example run;

```python
$ python3 Projects/pONE/runner.py -nc 3 -nr 3 -f 'save/here/file_name'
```

After the run the file will be saved in the location;
```Dark-Hex/Exp_Results/pONE/3x3/save/here/file_name.pkl```

The data saved is structured as a dictionary. It has 3 keys included. 
- Number of rows ('num_rows')
- Number of columns ('num_cols')
- Results dictionary ('results')

Results are in e-h array format. i.e. To access the game states with 3 hidden stoness and 4 empty cells: ```loaded['results'][4][3]```.

### Player

Player only plays for positions the given dataset has a definite win move for, otherwise it will play randomly.

**TEST_MODE** turn it to False not to print the ref board until the end.

You can set the initial position using the ```customP1``` and ```customP2``` on top of the file. 
```python
customP1 = ['.','.','.',
              '.','.','.',
                '.','.','.',
                  '.','.','.',]
customP2 = ['.','.','.',
              '.','.','.',
                '.','.','.',
                  '.','.','.',]
```
Please be aware that if the boards are inconsistent, the program will crash.

**pONE_player.py** is the file you need to run to be able to play. Input file is required (data). Here is how it will look like for a 3x3 board saved prior;
```python3 Projects/pONE/pONE_player.py -if 'Exp_Results/pONE/3x3/default_file.pkl'```

- **Input file path (-if / --in_file):** Input path for pONE data saved.

**UPDATE (v0.3):** I have uploaded and made it easier to use the playing option. If you do not specify any input file, you will have the online options to choose from. Just follow the menu after running the file;
```$ python3 Projects/pONE/pONE_player.py```