## Sample Game for test_DarkHex.py

Run ```python3 test_darkHex.py``` is all that is necessary.

Here I will be giving a short example for test_darkHex.py game. We
are using fixed-policy agent as the opponent for the player.

Input is given as x /space y pair. 

If the entry is an invalid move the player will have to try to move again.

```bash
x y: 1 1
This cell is taken.
Valid moves are: [[0, 0], [0, 1], [0, 2], [0, 3], [1, 0], [1, 2], [1, 3], [2, 0], [2, 1], [2, 2], [2, 3]]
x y: 2 2
. . . . 
 . W . . 
  . . B . 

x y: 2 3
. . . . 
 . W . . 
  . . B B 

x y: 1 1
Invalid Move.
Valid moves are: [[0, 0], [0, 1], [0, 2], [0, 3], [1, 0], [1, 3], [2, 1]]
x y: 1 0
. . . . 
 B W . . 
  . . B B 

Winner: W
```

After each ```x y:``` the entry is given by the player.
