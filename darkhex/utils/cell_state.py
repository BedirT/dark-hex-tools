class cellState:
    kEmpty = "."
    kBlack = "x"
    kWhite = "o"
    kBlackWin = "X"
    kWhiteWin = "O"
    kBlackNorth = "y"
    kBlackSouth = "z"
    kWhiteWest = "p"
    kWhiteEast = "q"

    white_pieces = [kWhite, kWhiteEast, kWhiteWest, kWhiteWin]
    black_pieces = [kBlack, kBlackNorth, kBlackSouth, kBlackWin]
