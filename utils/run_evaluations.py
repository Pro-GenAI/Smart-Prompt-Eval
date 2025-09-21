#!/usr/bin/env python3
"""
General Evaluation Runner
Runs all evaluation scripts in the evals directory.
"""

import sys
import subprocess
from pathlib import Path


def run_evaluation(eval_script: str):
    """Run a single evaluation script."""
    try:
        print(f"\n{'='*60}")
        print(f"Running evaluation: {eval_script}")
        print(f"{'='*60}")

        # Run the script
        result = subprocess.run(
            [sys.executable, eval_script],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )

        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

        return result.returncode == 0

    except Exception as e:
        print(f"Error running {eval_script}: {e}")
        return False


def main():
    """Main function to run all evaluations."""
    evals_dir = Path(__file__).parent

    # Find all evaluation scripts (files ending with _eval.py)
    eval_scripts = list(evals_dir.glob("*_eval.py"))

    if not eval_scripts:
        print("No evaluation scripts found in evals directory.")
        return

    print("Found evaluation scripts:")
    for script in eval_scripts:
        print(f"  - {script.name}")

    successful_runs = 0
    total_runs = len(eval_scripts)

    for script in eval_scripts:
        if run_evaluation(str(script)):
            successful_runs += 1

    print(f"\n{'='*60}")
    print("EVALUATION SUITE COMPLETE")
    print(f"{'='*60}")
    print(f"Successfully ran {successful_runs}/{total_runs} evaluations.")
    print("Check individual result files for detailed outputs.")


if __name__ == "__main__":
    main()
