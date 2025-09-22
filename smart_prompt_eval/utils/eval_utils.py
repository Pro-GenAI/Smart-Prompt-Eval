#!/usr/bin/env python3
"""
Evaluation Utilities
Shared functions for evaluation scripts to reduce code duplication.
"""

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from smart_prompt_eval.utils.common_utils import model

# Project root (one level up from this file: /<project_root>/utils)
project_root = Path(__file__).parent.parent


def load_gsm8k_questions(
    num_questions: Optional[int] = None, start_idx: int = 0
) -> List[Dict[str, Any]]:
    """
    Load GSM8K questions from the test file.

    Args:
        num_questions: Number of questions to load
        start_idx: Starting index in the file

    Returns:
        List of question dictionaries with id, question, and answer
    """
    questions = []
    # Use path relative to this file's directory
    gsm8k_path = project_root / "datasets" / "gsm8k_test.jsonl"
    with open(gsm8k_path, "r") as f:
        for i, line in enumerate(f):
            if i < start_idx:
                continue
            if num_questions and i >= start_idx + num_questions:
                break

            data = json.loads(line.strip())
            # Extract final answer from the answer field
            answer_text = data["answer"]
            if "####" in answer_text:
                final_answer = answer_text.split("####")[-1].strip()
            else:
                final_answer = answer_text.strip()

            questions.append(
                {
                    "id": f"gsm8k_{i+1}",
                    "question": data["question"],
                    "answer": final_answer,
                }
            )
    return questions


def extract_final_answer(answer_text: str) -> str:
    """
    Extract the final answer from GSM8K answer format.

    Args:
        answer_text: Raw answer text that may contain "#### final_answer"

    Returns:
        Extracted final answer
    """
    if "####" in answer_text:
        return answer_text.split("####")[-1].strip()
    else:
        return answer_text.strip()


def save_evaluation_results(
    results: Dict[str, Any],
    filename: str,
    responses: Optional[List[Dict[str, Any]]] = None,
) -> tuple[Path, Optional[Path]]:
    """
    Save evaluation results to a JSON file in a model-based folder structure.

    Args:
        results: Results dictionary to save
        filename: Name of the output file (without .json extension)
        responses: Optional list of individual responses to save separately

    Returns:
        Path to the saved results file
    """
    # Create model-based directory structure
    model_name = model.replace("/", "_").replace(
        "-", "_"
    )  # Sanitize model name for folder
    results_dir = project_root / "results" / model_name
    results_dir.mkdir(parents=True, exist_ok=True)

    # Save main results
    results_file = results_dir / f"{filename}_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    # Save individual responses if provided
    responses_file = None
    if responses:
        responses_file = results_dir / f"{filename}_responses.json"
        with open(responses_file, "w") as f:
            json.dump(responses, f, indent=2)

    return results_file, responses_file


def log_evaluation_start(title: str) -> None:
    """Log the start of an evaluation."""
    print("=" * 60)
    print(f"{title}")
    print("=" * 60)


def log_evaluation_end(title: str, result_file: Path, responses_file: Optional[Path]) -> None:
    """Log the end of an evaluation."""
    print(f"\n{'='*60}")
    print(f"{title} COMPLETE")
    if responses_file:
        print(f"Responses saved to: {responses_file}")
    print()
    print(f"Results saved to: {result_file}")
    print(f"{'='*60}")


def log_test_case_info(i: int, case_id: str, question: str, correct_answer: str) -> None:
    """Log standardized test case information."""
    print(f"Q{i+1} ", end="", flush=True)
    if i % 10 == 0:
        print()  # New line every 10 cases
    # log(f"\n{'-'*40}")
    # log(f"Testing case {i+1}: {case_id}")
    # log(f"Question: {question}")
    # log(f"Correct answer: {correct_answer}")
    # log(f"{'-'*40}")


default_instruction: str = (
    "Provide the final answer as a number at the end like #### 4"
)


def create_base_prompt(question: str, instruction: str = default_instruction) -> str:
    """
    Create a base prompt with question and instruction.

    Args:
        question: The question to ask
        instruction: Instruction for how to answer

    Returns:
        Formatted prompt
    """
    return f"{question}\n\n{instruction}"


def initialize_evaluation_results(
    experiment_name: str, description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Initialize a standard evaluation results dictionary.

    Args:
        experiment_name: Name of the experiment
        description: Description of what the experiment tests

    Returns:
        Initialized results dictionary
    """
    return {"experiment": experiment_name, "description": description, "test_cases": []}


def run_evaluation_main(
    eval_function: Callable[..., Any],
    eval_name: str,
    *args: Any,
    **kwargs: Any
) -> tuple[Path, Optional[Path]]:
    """
    Centralized main function for running evaluations.

    Args:
        eval_function: The evaluation function to run
        eval_name: Name of the evaluation (used for logging and filenames)
        eval_description: Description of what the evaluation tests
        *args: Arguments to pass to the evaluation function
        **kwargs: Keyword arguments to pass to the evaluation function

    Returns:
        Path to the saved results file
    """
    log_evaluation_start(f"{eval_name.upper()} EVALUATION")

    # Run the evaluation
    eval_result = eval_function(*args, **kwargs)

    # Handle both single return (results) and tuple return (results, responses)
    if isinstance(eval_result, tuple):
        results, responses = eval_result
    else:
        results = eval_result
        responses = None

    # Compute summary statistics
    total_problems = len(results["test_cases"])

    # Support two kinds of test case representations:
    # - Direct evaluations where each case has an `is_correct` boolean
    # - Variant evaluations where each case has a `variant_results` dict mapping
    #   variant_name -> boolean
    total_attempts: int = 0
    correct_answers: int = 0

    for case in results.get("test_cases", []):
        # Case with single boolean result
        if "is_correct" in case:
            total_attempts += 1
            if case.get("is_correct"):
                correct_answers += 1
        # Case with multiple variant results
        elif "variant_results" in case and isinstance(case["variant_results"], dict):
            variant_vals = list(case["variant_results"].values())
            total_attempts += len(variant_vals)
            # Count each True/Truthy variant as a correct attempt
            correct_answers += sum(1 for v in variant_vals if bool(v))
        else:
            # Unknown format: count as one attempt (not correct)
            total_attempts += 1

    accuracy = float(correct_answers) / total_attempts if total_attempts > 0 else 0.0

    results["total_problems"] = total_problems
    results["total_attempts"] = total_attempts
    results["correct_answers"] = correct_answers
    results["accuracy"] = accuracy

    # If any test case used variant_results, compute per-variant summaries
    per_variant_summary: Dict[str, Dict[str, Any]] = {}
    for case in results.get("test_cases", []):
        vr = case.get("variant_results")
        if isinstance(vr, dict):
            for variant_name, val in vr.items():
                if variant_name not in per_variant_summary:
                    per_variant_summary[variant_name] = {"attempts": 0, "correct": 0}
                per_variant_summary[variant_name]["attempts"] += 1
                if bool(val):
                    per_variant_summary[variant_name]["correct"] += 1

    if per_variant_summary:
        # Attach to results for downstream use and saving
        # Compute accuracy for each variant
        for vname, stats in per_variant_summary.items():
            attempts = stats.get("attempts", 0)
            correct = stats.get("correct", 0)
            stats["accuracy"] = correct / attempts if attempts > 0 else 0

        results["per_variant_summary"] = per_variant_summary

    # Log results summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    if "total_problems" in results:
        print(f"Total Problems: {results['total_problems']}")
    if "total_attempts" in results:
        print(f"Total Attempts: {results['total_attempts']}")
    if "correct_answers" in results:
        print(f"Correct Answers: {results['correct_answers']}")
    if "accuracy" in results:
        # Log accuracy as a percentage-like decimal with two decimals
        try:
            print(f"{results['accuracy']:.2f}")
        except Exception:
            # Fallback to raw value if formatting fails
            print(str(results["accuracy"]))

    # Print per-variant breakdown if present
    pvs = results.get("per_variant_summary")
    if pvs:
        print("\nPer-variant breakdown:")
        for variant_name, stats in pvs.items():
            attempts = stats.get("attempts", 0)
            correct = stats.get("correct", 0)
            accuracy_v = correct / attempts if attempts > 0 else 0
            try:
                print(
                    f"  {variant_name}: attempts={attempts}, correct={correct},"
                    f" accuracy={accuracy_v:.2f}"
                )
            except Exception:
                print(
                    f"  {variant_name}: attempts={attempts}, correct={correct},"
                    f" accuracy={accuracy_v}"
                )

    # Save results (responses will be handled by individual evaluation functions)
    filename_base = eval_name.lower().replace(" ", "_")
    result_file, responses_file = save_evaluation_results(results, filename_base, responses)

    log_evaluation_end(f"{eval_name.upper()} EVALUATION", result_file, responses_file)

    return result_file, responses_file
