"""Runner for evaluation modules.

Usage:
    python run_eval.py evals.direct_gsm8k_eval
    python run_eval.py direct_gsm8k_eval  # assumes module under evals

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

if len(sys.argv) < 2:
    print("Usage: python run_eval.py <module-name>")
    print("Example: python run_eval.py evals.direct_gsm8k_eval")
    sys.exit(2)

module = sys.argv[1]
# If user passed just the file base name, prefix with 'evals.'
if "." not in module and not module.startswith("evals."):
    module = f"evals.{module}"

try:
    import evals
except Exception:
    pass

runpy.run_module(module, run_name="__main__", alter_sys=True)
