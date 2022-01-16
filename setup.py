import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

packages = [
    'numpy',
    ''
]

setuptools.setup(
    name = 'darkhex',
    version = '0.0.1',
    author = 'Bedir Tapkan',
    author_email = 'tapkan@ualberta.ca',
    description = 'Set of tools to analyze and research the game Dark Hex.',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/BedirT/darkHex',
    project_urls = {
        'Bug Reports': 'https://github.com/BedirT/darkHex/issues',
    },
    classifiers = [
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    python_requires = '>=3.6',
    packages = setuptools.find_packages(),
    install_requires = [
        'numpy',
        'open-spiel',
        'pydot',
        'xdot',
        'pycairo',
        'PyGObject',
        'dill',
    ],
    extras_require = {
        'dev': [
            'pytest',
            'typing',
        ],
    },

)

    