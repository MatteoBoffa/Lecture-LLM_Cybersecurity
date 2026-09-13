#!/usr/bin/env python3
"""Alias for display.py, because that is the other name people try first."""

import runpy
import sys
from pathlib import Path

sys.argv[0] = str(Path(__file__).resolve().parent / "display.py")
runpy.run_path(sys.argv[0], run_name="__main__")
