import importlib.resources
from pathlib import Path

from finesse import Model

import virgui

GLOBAL_MODEL = Model()
LAYOUTS = Path(str(importlib.resources.files(virgui))) / "layouts"
ASSETS = Path(str(importlib.resources.files(virgui))) / "assets"
