from game.hex import Hex
from agent.RandomAgent import RandomAgent

C_PLAYER1 = 'B'
C_PLAYER2 = 'W'

game = Hex(verbose=True)

actors = {C_PLAYER1: RandomAgent(C_PLAYER1), C_PLAYER2: RandomAgent(C_PLAYER2)}

i = 0; res = '='

while res == '=':
    player = C_PLAYER1 if i % 2 == 0 else C_PLAYER2
    action = actors[player].step(game.BOARD)
    _, _, res, _ = game.step(player, action)
    game.printBoard(); print(); i+=1

print('\nWinner:', res)
