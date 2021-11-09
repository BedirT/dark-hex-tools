<!--An explanation for couple files-->
<!--Explaning generate_info_states.py-->
# generate_info_states.py
Infostate creator. Generates all information state given player will see through the game, gets the actions and corresponding probabilities for each action, and maps these with the infostate.

Works in following order:
- For each move specified, recursively call the generate_info_states
function, one for a collusion if possible, and one for a non-collusion.
- For the collusion; place an opponent stone, and for the non-collusion
place a player stone on the board for information state.
- Calls continue until there is no other possible state for the player.

Arguments:
- num_cols: Number of columns in the board.
- num_rows: Number of rows in the board.
- player_order: If player is the first or the second player. (0 or 1)
- player_color: Color of the player. (b for black, w for white) Black player connects top to bottom, white player connects left to right.
- board_state: The starting board state. Given in a string form. (must use board connection notation, please refer to [Hex.py/Pieces](Projects/game/Hex.py)). The provided board will be starting position of the game, for both players. If no board is provided then the board will be empty. i.e. '.y.......' is a 3x3 board with a black stone with a north connection.
- convert_xo: Save using 'x' and 'o' instead of using connection information.
- isomorphic: Include isomorphic states to the strategy.
- write_to_dict: Add the information state to the strategy_data.py file.
- dict_name: Name of the dictionary to be used. Needed if write_to_dict is True.

[Sample input](in.txt)

<!--Explaning run_wo_game.py-->

<!--Explaning strategy_data.py-->