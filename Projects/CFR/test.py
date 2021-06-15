from Projects.base.game.darkHex import DarkHex

game = DarkHex()
print(game.turn_info())
game.step('B', 0)
print(game.turn_info())
game.step('W', 1)
print(game.turn_info())
game.rewind()
print('here')
game.rewind()
pass