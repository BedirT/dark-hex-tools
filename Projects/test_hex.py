from Projects.base.game.hex import Hex
from Projects.base.agent.RandomAgent import RandomAgent

game = Hex(verbose=True)

actors = {game.C_PLAYER1: RandomAgent(game.C_PLAYER1), game.C_PLAYER2: RandomAgent(game.C_PLAYER2)}

i = 0; res = '='

while res == '=':
    player = game.C_PLAYER1 if i % 2 == 0 else game.C_PLAYER2
    action = actors[player].step(game.BOARD)
    _, _, res, _ = game.step(player, action)
    game.printBoard(); print(); i+=1

print('\nWinner:', res)
