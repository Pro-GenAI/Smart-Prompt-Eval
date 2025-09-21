"""Runner for evaluation modules.

Usage:
    python run_eval.py evals.direct_gsm8k_eval
    python run_eval.py direct_gsm8k_eval  # assumes module under evals

This script imports the `evals` package first so the package-level sys.path
bootstrap runs, then executes the specified module as `__main__`.
"""
import sys
import runpy
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python run_eval.py <module-name>")
    print("Example: python run_eval.py evals.direct_gsm8k_eval")
    sys.exit(2)

module = sys.argv[1]
# If user passed just the file base name, prefix with 'evals.'
if "." not in module and not module.startswith("evals."):
    module = f"evals.{module}"

# Ensure evals package is imported first so its __init__ runs (bootstrap sys.path)
try:
    import evals  # noqa: F401
except Exception:
    # continue — evals.__init__ will be imported when running the module
    pass

# Execute the target module as a script (so if it has `if __name__ == '__main__'` it runs)
runpy.run_module(module, run_name="__main__", alter_sys=True)
