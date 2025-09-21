"""evals package re-exporting evaluation modules for `hack_prompt_eval`.

This module also ensures the project root directory is on ``sys.path`` so that
top-level imports like ``utils`` resolve correctly when evaluation modules are
executed or imported directly. Centralizing the path modification here avoids
duplicating the same snippet across multiple evaluation scripts.
"""

import os
import sys
from pathlib import Path

# Put the project root (workspace root) on sys.path so top-level imports work.
# We assume this package lives at <project_root>/evals, so parent of this file
# is the project root.
_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _THIS_FILE.parent
if str(_PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(_PROJECT_ROOT))

__all__ = []
