from game.hex import Hex
from agent.RandomAgent import RandomAgent

game = Hex(verbose=True)

actors = {'B': RandomAgent('B'), 'W': RandomAgent('W')}

i = 0; res = '='

while res == '=':
    player = 'B' if i % 2 == 0 else 'W'
    action = actors[player].step(game.BOARD)
    _, _, res, _ = game.step(player, action)
    game.printBoard(); print(); i+=1

print('\nWinner:', res)
