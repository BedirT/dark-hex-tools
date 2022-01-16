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

### Installation

The library is uploaded on Pypi and can be installed using pip. Before pip called make sure you have the following packages installed:

- [Python 3.6](https://www.python.org/downloads/)
- [PyGObject - bindings for GTK3](https://pypi.org/project/pygobject/)
- [Graphviz](https://www.graphviz.org/)
- [GCC](https://gcc.gnu.org/)
- [Libcairo](https://www.cairographics.org/)

They are mostly required for graph drawing and setup reasons. Please make sure you have these packages installed before installing the library.

#### For Debian / Ubuntu

```bash
sudo apt-get install libgirepository1.0-dev gcc libcairo2-dev pkg-config gir1.2-gtk-3.0 graphviz
```

#### For MacOS

```bash
brew install gobject-introspection graphviz cairo pkg-config gtk+3 gcc
```

After installing the packages you can install the library using pypi.

```bash
pip install darkhex
```

#### Setup from source using pip

Installing from source would be helpful if you wanted a custom version of the library / helping with development. Make sure you have the packages above installed.

##### Virtual Environment

We recommend using a virtual environment for the development.

E.g. for Ubuntu or Debian:
```bash
sudo apt-get install virtualenv python3-virtualenv
virtualenv venv
source venv/bin/activate
````

Rest of the installation is just installing python requirements.

E.g. for Ubuntu or Debian:

```bash
# Install the libraries listed above
sudo apt-get install libgirepository1.0-dev gcc libcairo2-dev pkg-config gir1.2-gtk-3.0 graphviz

# Install the python packages
pip install -r requirements.txt
```

**Update PYTHONPATH on your .bashrc or .zshrc file (or .venv/bin/activate)**
