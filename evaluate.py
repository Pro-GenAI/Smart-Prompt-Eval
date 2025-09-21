#!/usr/bin/env python3
"""
Main evaluation script for Hack-Prompting project.
Runs all experiments and collects results.
"""

import os
import sys
import importlib.util
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from hack_prompt_eval.utils.common_utils import log

def run_experiment(experiment_name: str):
    """Run a single experiment by importing and executing its module."""
    experiment_path = project_root / "experiments" / f"{experiment_name}.py"

    if not experiment_path.exists():
        log(f"Experiment {experiment_name} not found at {experiment_path}")
        return False

    try:
        # Import the experiment module
        spec = importlib.util.spec_from_file_location(experiment_name, experiment_path)
        if spec is None or spec.loader is None:
            log(f"Could not load experiment {experiment_name}")
            return False

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        log(f"\n{'='*50}")
        log(f"Running experiment: {experiment_name}")
        log(f"{'='*50}\n")

        # The experiment will run its code when imported
        return True

    except Exception as e:
        log(f"Error running experiment {experiment_name}: {e}")
        return False

def run_evaluations():
    """Run all evaluation scripts in evals directory."""
    evals_runner = project_root / "evals" / "run_evaluations.py"
    if evals_runner.exists():
        try:
            log(f"\n{'='*50}")
            log("Running Dataset Evaluations")
            log(f"{'='*50}\n")

            result = os.system(f"python {evals_runner}")
            if result == 0:
                log("Dataset evaluations completed successfully.")
            else:
                log("Some dataset evaluations failed.")
        except Exception as e:
            log(f"Error running dataset evaluations: {e}")
    else:
        log("No evals runner found.")

def main():
    """Main function to run all experiments."""
    log("Starting Hack-Prompting Evaluation Suite")
    log(f"Model: {os.getenv('OPENAI_MODEL', 'Not set')}")
    log(f"Base URL: {os.getenv('OPENAI_BASE_URL', 'Not set')}")
    log("-" * 50)

    experiments = [
        "Linguistic_Errors",
        "Multilingual_Prompting",
        "Power_of_Roles",
        "Does_Seed_Matter"
    ]

    successful_runs = 0
    total_runs = len(experiments)

    for experiment in experiments:
        if run_experiment(experiment):
            successful_runs += 1
        log()  # Add blank line between experiments

    log("-" * 50)
    log(f"Prompt experiments complete. {successful_runs}/{total_runs} experiments ran successfully.")

    # Run dataset evaluations
    run_evaluations()

    log("-" * 50)
    log("All evaluations complete. Check output.txt and evals/ directory for results.")

if __name__ == "__main__":
    main()
