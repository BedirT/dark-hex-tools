class strategies:
    '''
    A class that has pre-written strategies to use on SVerify.
    Each strategy is described.
    '''
    # ryan 3x4 .25 lower bound strategy
    ryan_3x4_lb = {
        'name': 'ryan_3x4_lb',
        'description': 'Ryan 3x4 lower bound strategy',
        'board_size': (3, 4),
        'player': '0',
        'strategy': {
            "............0": [(8, 1.0),],
            "........z...1": [(4, 1.0),],
            "....o...z...0": [(5, 1.0),],
            "....oz..z...1": [(1, 1.0),],
            ".o..oz..z...0": [(2, 1.0),],
            "....z...z...2": [(0, 1.0),],
            "o...z...z...1": [(1, 1.0),],
            "oo..z...z...0": [(3, 1.0),],
            "oo.yz...z...1": [(7, 1.0),],
            "oo.yz..oz...0": [(6, 1.0),],
            "oo.yz.yoz...1": [(9, 1.0),],
            "oo.yz.yozo..0": [(10, 1.0),],
            "oo.yz..yz...2": [(11, 1.0),],
            "oo.yz..yz..o1": [(10, 1.0),],
            "oo.yz..yz.oo0": [(6, 1.0),],
            "oo.yz.yyz.oo1": [(9, 1.0),],
            "oo.yz.yyzooo0": [(5, 1.0),]
        }
    }

    # 2x2 prob 1 strategy
    prob_1_2x2 = {
        'name': 'prob_1_2x2',
        'description': '2x2 prob 1 strategy',
        'board_size': (2, 2),
        'player': '0',
        'strategy': {   
            '....0': [(1, 0.5), (2, 0.5)],
            '.y..1': [(2, 0.5), (3, 0.5)],
            '.yo.0': [(3, 1)],
            '.y.o0': [(2, 1)],
            '..z.1': [(0, 0.5), (1, 0.5)],
            'o.z.0': [(1, 1)],
            '.oz.0': [(0, 1)],
        }
    }