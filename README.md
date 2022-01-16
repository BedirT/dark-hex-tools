# DarkHex

Dark Hex is the imperfect information version of the game Hex. This game has a really scarce work on it. In this repository I am including an implementation of the game along with some algorithms implemented specifically for DarkHex. Also I included the results of some of the experiments.

For details on DarkHex and any of the algorithms used as well as the experiments please check my thesis [-link-]().

- [What is Hex](<https://en.wikipedia.org/wiki/Hex_(board_game)>)
- [Dark-Hex Open Spiel Implementation](https://github.com/deepmind/open_spiel/blob/master/open_spiel/games/dark_hex.h)
- [Sample Game](Sample_game.md)

## Implementations

- [x] pONE
- [x] Vanilla CFR
- [x] FSI-CFR
- [x] Backward Induction Best Response
- [ ] AlphaZero Approximate Best Response
- [ ] CFR+
- [ ] MCCFR
- [ ] NFSP
- [ ] Deep CFR

### Experiments and Results

#### pONE

Explanation for the pONE algorithm.

- [ ] Reimplement using OpenSpiel.

- [x] 2x2
- [x] 3x3
- [x] 3x4
- [x] 4x3
- [ ] 4x4

#### CFR

Explanation for the CFR algorithm.

#### FSI-CFR

Explanation for the FSI-CFR algorithm.

#### Backward Induction Best Response

Explanation for the Backward Induction Best Response algorithm.

#### AlphaZero Approximate Best Response

Explanation for the AlphaZero Approximate Best Response algorithm.

**Please add the project pythonpath for relative refs to work.**
run `export PYTHONPATH="${PYTHONPATH}:<path_to_repo>"`
