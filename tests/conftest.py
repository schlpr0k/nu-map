"""Pytest configuration ensuring the project package is importable.

Pytest runs from the repository root, but the project is not installed
as a package during CI runs.  Add the repository root to ``sys.path`` so
``import numap`` and related statements succeed.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUBS = ROOT / 'tests' / 'stubs'

for path in (STUBS, ROOT):
    str_path = str(path)
    if str_path not in sys.path:
        sys.path.insert(0, str_path)
