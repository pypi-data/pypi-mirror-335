# -*- coding: utf-8 -*-
from distutils.core import setup

long_description = ""

setup(
    name="pta_reload",
    packages=[
        "pta_reload",
        "pta_reload.momentum",
        "pta_reload.overlap",
        "pta_reload.statistics",
        "pta_reload.trend",
        "pta_reload.utils",
        "pta_reload.volatility",
        "pta_reload.volume"
    ],
    version=".".join(("1", "0", "2")),
    description=long_description,
    long_description=long_description,
    author="Thinh Vu",
    author_email="mrthinh@live.com",
    maintainer="Thinh Vu",
    maintainer_email="mrthinh@live.com",

    install_requires=[
        "numpy<=1.26.4",
        "pandas",
    ],

    extras_require={
        "dev": [
            "matplotlib", "mplfinance", "scipy",
            "sklearn", "statsmodels", "stochastic",
            "tqdm"
        ],
    },
)
