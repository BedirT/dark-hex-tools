'''
Use create_policy.py to generate suitable policy objects if
needed. Add the result at the end of the class 'strategies'.
'''
from Projects.base.game.hex import pieces

class strategies:
    '''
    A class that has pre-written strategies to use on SVerify.
    Each strategy is described.
    '''

    # ryan 3x4 .25 lower bound strategy (second player)
    ryan_3x4_lower_bound = {
        'name': 'ryan_3x4_lower_bound',
        'description': 'ryan 3x4 lower bound strategy',
        'num_rows': 3,
        'num_cols': 4,
        'player': pieces.kBlack,
        'player_order': 1,
        'strategy': {
            "............": [3, 8],
            "........o...": [3],
            "...o........": [8],
            "...x....o...": [7],
            "...o....x...": [4],
            "...x...oo...": [6],
            "...oo...x...": [5],
            "...x..xoo...": [10],
            "...oox..x...": [1],
            "...x..xoo.o.": [9],
            ".o.oox..x...": [2],
            "...x...xo...": [11],
            "...ox...x...": [0],
            "...x...xo..o": [10],
            "o..ox...x...": [1],
            "...x...xo.oo": [9],
            "oo.ox...x...": [2],
            "...x...xoxoo": [6],
            "ooxox...x...": [5],
            "...x..oxoxoo": [5],
            "ooxoxo..x...": [6],
            "...x.xoxoxoo": [2],
            "ooxoxox.x...": [9],
            "..ox.xoxoxoo": [1],
            "ooxoxox.xo..": [10],
            "........x...": [4],
            "...x........": [7],
            "....o...x...": [5],
            "...x...o....": [6],
            "....oo..x...": [3],
            "...x..oo....": [8],
            "...xoo..x...": [6, 7],
            "...x..oox...": [5, 4],
            "...xooo.x...": [7],
            "...x.ooox...": [4],
            "...xoooxx...": [11],
            "...xxooox...": [0],
            "...xoooxx..o": [10],
            "o..xxooox...": [1],
            "...xoox.x...": [10],
            "...x.xoox...": [1],
            "...xoox.x.o.": [9],
            ".o.x.xoox...": [2],
            "...xoox.xoo.": [11],
            ".oox.xoox...": [0],
            "...xoox.xoox": [7],
            "xoox.xoox...": [4],
            "...xoo.ox...": [6],
            "...xo.oox...": [5],
            "...xooxox...": [10],
            "...xoxoox...": [1],
            "...xooxox.o.": [9],
            ".o.xoxoox...": [2],
            "...xoo.xx...": [11],
            "...xx.oox...": [0],
            "...xoo.xx..o": [10],
            "o..xx.oox...": [1],
            "...xoo.xx.oo": [6],
            "oo.xx.oox...": [5],
            "...xooxxx.oo": [9],
            "oo.xxxoox...": [2],
            "....ox..x...": [1],
            "...x..xo....": [10],
            ".o..ox..x...": [2],
            "...x..xo..o.": [9],
            ".oo.ox..x...": [3],
            "...x..xo.oo.": [8],
            ".ooxox..x...": [6],
            "...x..xoxoo.": [5],
            ".ooxoxo.x...": [7],
            "...x.oxoxoo.": [4],
            ".ooxoxoxx...": [11],
            "...xxoxoxoo.": [0],
            ".ooxoxoxx..o": [10],
            "o..xxoxoxoo.": [1],
            "....x...x...": [0],
            "...x...x....": [11],
            "o...x...x...": [1],
            "...x...x...o": [10],
            "oo..x...x...": [2, 3],
            "...x...x..oo": [9, 8],
            "ooo.x...x...": [3],
            "...x...x.ooo": [8],
            "oooxx...x...": [7],
            "...x...xxooo": [4],
            "oooxx..ox...": [6],
            "...xo..xxooo": [5],
            "oooxx.xox...": [10],
            "...xox.xxooo": [1],
            "oooxx.xox.o.": [9],
            ".o.xox.xxooo": [2],
            "oooxx..xx...": [11],
            "...xx..xxooo": [0],
            "oooxx..xx..o": [10],
            "o..xx..xxooo": [1],
            "oooxx..xx.oo": [6],
            "oo.xx..xxooo": [5],
            "oooxx.xxx.oo": [9],
            "oo.xxx.xxooo": [2],
            "oooxx.xxxooo": [5],
            "oooxxx.xxooo": [6],
            "oox.x...x...": [5],
            "...x...x.xoo": [6],
            "oox.xo..x...": [7],
            "...x..ox.xoo": [4],
            "oox.xo.ox...": [6],
            "...xo.ox.xoo": [5],
            "oox.xoxox...": [10],
            "...xoxox.xoo": [1],
            "oox.xoxox.o.": [9],
            ".o.xoxox.xoo": [2],
            "oox.xo.xx...": [6],
            "...xx.ox.xoo": [5],
            "oox.xooxx...": [3],
            "...xxoox.xoo": [8],
            "ooxxxooxx...": [11],
            "...xxooxxxoo": [0],
            "ooxxxooxx..o": [10],
            "o..xxooxxxoo": [1],
            "oox.xoxxx...": [11],
            "...xxxox.xoo": [0],
            "oox.xoxxx..o": [10],
            "o..xxxox.xoo": [1],
            "oox.xoxxx.oo": [9],
            "oo.xxxox.xoo": [2],
            "oo.xx...x...": [6, 7],
            "...x...xx.oo": [5, 4],
            "oo.xx.o.x...": [7],
            "...x.o.xx.oo": [4],
            "oo.xx.oxx...": [11],
            "...xxo.xx.oo": [0],
            "oo.xx.oxx..o": [10],
            "o..xxo.xx.oo": [1],
            "oo.xx.oxx.oo": [2],
            "oo.xxo.xx.oo": [9],
            "ooxxx.oxx.oo": [5],
            "oo.xxo.xxxoo": [6],
            "oo.xx.x.x...": [10],
            "...x.x.xx.oo": [1],
            "oo.xx.x.x.o.": [9],
            ".o.x.x.xx.oo": [2],
            "oo.xx.x.xoo.": [5],
            ".oox.x.xx.oo": [6],
            "oo.xxox.xoo.": [11],
            ".oox.xoxx.oo": [0],
            "oo.xxox.xoox": [7],
            "xoox.xoxx.oo": [4],
            "oo.xx..ox...": [5, 6],
            "...xo..xx.oo": [6, 5],
            "oo.xxo.ox...": [6],
            "...xo.oxx.oo": [5],
            "oo.xxoxox...": [10],
            "...xoxoxx.oo": [1],
            "oo.xxoxox.o.": [9],
            ".o.xoxoxx.oo": [2],
            "oo.xxx.ox...": [2],
            "...xo.xxx.oo": [9],
            "oooxxx.ox...": [6],
            "...xo.xxxooo": [5],
            "oo.xx.xox...": [10],
            "...xox.xx.oo": [1],
            "oo.xx.xox.o.": [9],
            ".o.xox.xx.oo": [2],
            "oo.xx.xoxoo.": [5],
            ".ooxox.xx.oo": [6],
            "oo.xx..xx...": [11],
            "...xx..xx.oo": [0],
            "oo.xx..xx..o": [10],
            "o..xx..xx.oo": [1],
            "oo.xx..xx.oo": [6, 5],
            "oo.xxx.xx.oo": [2],
            "oo.xx.xxx.oo": [9],
            "oooxxx.xx.oo": [6],
            "oo.xx.xxxooo": [5],
        }
    }

    test_2x2 = {
        'name': 'test_2x2',
        'description': 'test 2x2',
        'num_rows': 2,
        'num_cols': 2,
        'player': pieces.kBlack,
        'player_order': 0,
        'strategy': {
            "....": [1],
            "..x.": [0, 3],
            ".x..": [3, 0],
            "o.x.": [1],
            ".x.o": [2],
            "..xo": [0],
            "oy..": [3],
            "..xx": [0],
            "yy..": [3],
            "o.xx": [1],
            "yy.o": [2],
        }
    }

    test_2x3_33p = {
        'name': 'test_2x3',
        'description': 'test 2x3',
        'num_rows': 2,
        'num_cols': 3,
        'player': pieces.kBlack,
        'player_order': 0,
        'strategy': {
            "......": [2],
            "...x..": [0, 4, 5],
            "..x...": [5, 1, 0],
            "o..x..": [1],
            "..x..o": [4],
            "...xo.": [2],
            ".ox...": [3],
            "..xxo.": [5],
            ".oxx..": [0],
            "..xxoo": [0],
            "ooxx..": [5],
            "...xx.": [5],
            ".xx...": [0],
            "...xxo": [0],
            "oxx...": [5],
            "o..xxo": [1],
            "oxx..o": [4],
            "...xxx": [0],
            "xxx...": [5],
            "o..xxx": [1],
            "xxx..o": [4],
            "oo.xxx": [2],
            "xxx.oo": [3],
            "...x.o": [4],
            "o.x...": [1],
            "...x.x": [4],
            "x.x...": [1],
            "...xox": [0],
            "xox...": [5],
            "o..xox": [1],
            "xox..o": [4],
        }
    }

    test_4x3_1 = {
        'name': 'test_4x3_1',
        'description': 'test 4x3: starting from the board state "pp.yzp..z.o.".',
        'num_rows': 3,
        'num_cols': 4,
        'player': pieces.kBlack,
        'player_order': 0,
        'strategy': {
            "oo.xxo..x.o.": [6, 7],
            ".o.x..oxx.oo": [5, 4],
            "oo.xxox.x.o.": [9],
            ".o.x.xoxx.oo": [2],
            "oo.xxox.xoo.": [11],
            ".oox.xoxx.oo": [0],
            "oo.xxox.xoox": [7],
            "xoox.xoxx.oo": [4],
            "oo.xxo.xx.o.": [11],
            ".o.xx.oxx.oo": [0],
            "oo.xxo.xx.oo": [9],
            "oo.xx.oxx.oo": [2],
            "oo.xxo.xxxoo": [6],
            "ooxxx.oxx.oo": [5],
        }
    }

