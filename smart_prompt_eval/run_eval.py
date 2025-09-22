"""Runner for evaluation modules.

Usage:
    python run_eval.py evals.direct_gsm8k_eval
    python run_eval.py direct_gsm8k_eval  # assumes module under evals
    python run_eval.py  # runs all modules except seed_consistency_eval

Available evaluation modules:
    - evals.direct_gsm8k_eval
    - evals.linguistic_errors_eval
    - evals.multilingual_eval
    - evals.multiple_roles_eval
    - evals.seed_consistency_eval
    - evals.harmful_prompts_eval
"""
import sys
import runpy
from pathlib import Path

def get_eval_modules():
    """Get list of evaluation modules to run (excluding seed_consistency_eval)."""
    evals_dir = Path(__file__).parent / "evals"
    modules = []
    for file in evals_dir.glob("*.py"):
        if file.name.startswith("__") or file.name == "seed_consistency_eval.py" \
                or file.name == "seed_consistency_eval.py":
            continue
        module_name = f"evals.{file.stem}"
        modules.append(module_name)
    return modules

if len(sys.argv) < 2:
    # Run all modules except seed_consistency_eval
    modules = get_eval_modules()
    print(f"Running all evaluation modules: {', '.join(modules)}")
    for module in modules:
        print(f"\n{'='*50}")
        print(f"Running {module}")
        print(f"{'='*50}")
        try:
            runpy.run_module(module, run_name="__main__", alter_sys=True)
        except Exception as e:
            print(f"Error running {module}: {e}")
    sys.exit(0)

module = sys.argv[1]
# If user passed just the file base name, prefix with 'evals.'
if "." not in module and not module.startswith("evals."):
    module = f"evals.{module}"

try:
    import evals
except Exception:
    pass

runpy.run_module(module, run_name="__main__", alter_sys=True)
