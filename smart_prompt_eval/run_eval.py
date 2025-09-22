"""Runner for evaluation modules.

Usage:
    python run_eval.py evals.direct_gsm8k_eval
    python run_eval.py direct_gsm8k_eval  # assumes module under evals
    python run_eval.py  # runs all modules

Available evaluation modules:
    - evals.direct_gsm8k_eval
    - evals.linguistic_errors_eval
    - evals.multilingual_eval
    - evals.multiple_roles_eval
    - evals.harmful_prompts_eval
"""

# import runpy
import subprocess
import sys
from pathlib import Path


def get_eval_modules():
    """Get list of evaluation modules to run."""
    evals_dir = Path(__file__).parent / "evals"
    modules = []
    for file in evals_dir.glob("*.py"):
        if file.name.startswith("__"):
            continue
        module_name = f"evals.{file.stem}"
        modules.append(module_name)
    return modules


if len(sys.argv) < 2:
    # Run all modules
    modules = get_eval_modules()
    print(f"Running all evaluation modules: {', '.join(modules)}")
    for module in modules:
        try:
            # runpy.run_module(module, run_name="__main__", alter_sys=True)
            # Run in subprocess to prevent sys.exit from stopping the batch
            full_module = f"smart_prompt_eval.{module}"
            result = subprocess.run(
                [sys.executable, "-m", full_module], cwd=Path(__file__).parent.parent
            )
            if result.returncode != 0:
                print(f"Module {module} exited with code {result.returncode}")
        except Exception as e:
            print(f"Error running {module}: {e}")
    sys.exit(0)

else:
    module = sys.argv[1]
    # If user passed just the file base name, prefix with 'evals.'
    if "." not in module and not module.startswith("evals."):
        module = f"evals.{module}"

    # runpy.run_module(module, run_name="__main__", alter_sys=True)
    # Run the module in subprocess to handle sys.exit gracefully
    full_module = f"smart_prompt_eval.{module}"
    result = subprocess.run(
        [sys.executable, "-m", full_module], cwd=Path(__file__).parent.parent
    )
    sys.exit(result.returncode)
