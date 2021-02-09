from game.darkHex import DarkHex
from agent.RandomAgent import RandomAgent


game = DarkHex()

actor1 = RandomAgent('B')
actor2 = RandomAgent('W')

i = 0

while game.check_game_status() == '=':
    if i % 2 == 0:
        result = 'f'
        while result == 'f':
            action = actor1.step(game.BOARD)
            board, done, result, reward = game.step('B', action)
        game.printBoard_for_player('B')
    else:
        result = 'f'
        while result == 'f':
            action = actor2.step(game.BOARD)
            board, done, result, reward = game.step('W', action)
        game.printBoard_for_player('W')
    print()
    # game.printBoard()
    i+=1

print('\nWinner:', game.check_game_status())
