from game.Hex import Hex
from agent.RandomAgent import RandomAgent


game = Hex()

actor1 = RandomAgent('B')
actor2 = RandomAgent('W')

i = 0

while game.check_game_status() == '=':
    if i % 2 == 0:
        action = actor1.step(game.BOARD)
        game.step('B', action)
    else:
        action = actor2.step(game.BOARD)
        game.step('W', action)
    game.printBoard()
    print()
    i+=1

print('\nWinner:', game.check_game_status())
