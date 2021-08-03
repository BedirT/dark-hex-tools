from Projects.base.game.hex import Hex, pieces
from Projects.base.agent.RandomAgent import RandomAgent

actors = {pieces.kBlack: RandomAgent(pieces.kBlack), pieces.kWhite: RandomAgent(pieces.kWhite)}

num_iterations = 1000

winners = {pieces.kBlack: 0, pieces.kWhite: 0}
for it in range(num_iterations):
    i = 0; res = '='
    game = Hex(verbose=True)
    while res == '=':
        player = pieces.kBlack if i % 2 == 0 else pieces.kWhite
        action = actors[player].step(game.BOARD)
        # action = int(input(str(player) + ':'))
        _, res, _ = game.step(player, action)
        # print(res)
        # game.printBoard(); print(); 
        i+=1
        # print(game.BOARD)
    # count the winners
    winners[res] += 1
    
# Report the recorded winners
print(winners)
