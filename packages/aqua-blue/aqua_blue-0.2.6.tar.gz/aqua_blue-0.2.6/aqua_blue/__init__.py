"""
.. include:: ../README.md

# Examples

## Basic Lotka-Volterra example

```py
.. include:: ../examples/lotka-volterra.py
```

## Using datetime objects

```py
.. include:: ../examples/sine-cosine.py
```

## Load and output a JSON string
```py
.. include:: ../examples/json_example.py
```
"""

__version__ = "0.2.6"
__authors__ = [
    "Jacob Jeffries",
    "Hrishikesh Belagali",
    "Avik Thumati",
    "Ameen Mahmood",
    "Samuel Josephs",
]

__author_emails__ = [
    "jacob.jeffries@ccmc.global",
    "hrishikesh.belagali@ccmc.global",
    "avik.thumati@ccmc.global",
    "ameen.mahmood@ccmc.global",
    "samuel.josephs@ccmc.global"
]
__url__ = "https://github.com/Chicago-Club-Management-Company/aqua-blue"

from . import utilities as utilities
from . import reservoirs as reservoirs
from . import readouts as readouts
from . import models as models
from . import time_series as time_series
