#!/usr/bin/env python3
"""
Evaluation Utilities
Shared functions for evaluation scripts to reduce code duplication.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.utils import log, model


def load_gsm8k_questions(
    num_questions: int = 5, start_idx: int = 0
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
    gsm8k_path = Path(__file__).parent / "gsm8k_test.jsonl"
    with open(gsm8k_path, "r") as f:
        for i, line in enumerate(f):
            if i < start_idx:
                continue
            if i >= start_idx + num_questions:
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
) -> Path:
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
    if responses:
        responses_file = results_dir / f"{filename}_responses.json"
        with open(responses_file, "w") as f:
            json.dump(responses, f, indent=2)

    return results_file


def log_evaluation_start(title: str):
    """Log the start of an evaluation."""
    log("=" * 60)
    log(f"{title}")
    log("=" * 60)


def log_evaluation_end(title: str, output_file: Path):
    """Log the end of an evaluation."""
    log(f"\n{'='*60}")
    log(f"{title} COMPLETE")
    log(f"Results saved to: {output_file}")
    log(f"{'='*60}")


def log_test_case_info(i: int, case_id: str, question: str, correct_answer: str):
    """Log standardized test case information."""
    log(f"\n{'-'*40}")
    log(f"Testing case {i+1}: {case_id}")
    log(f"Question: {question}")
    log(f"Correct answer: {correct_answer}")
    log(f"{'-'*40}")


instruction: str = "Provide final answer as a number in a new line like #### 4"


def create_base_prompt(question: str) -> str:
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
    experiment_name: str, description: str
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
    eval_function, eval_name: str, eval_description: str, *args, **kwargs
):
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

    # Log results summary
    log("\n" + "=" * 60)
    log("RESULTS SUMMARY")
    log("=" * 60)

    if "total_problems" in results:
        log(f"Total Problems: {results['total_problems']}")
    if "total_attempts" in results:
        log(f"Total Attempts: {results['total_attempts']}")
    if "correct_answers" in results:
        log(f"Correct Answers: {results['correct_answers']}")
    if "accuracy" in results:
        log(".2f")

    # Save results (responses will be handled by individual evaluation functions)
    filename_base = eval_name.lower().replace(" ", "_")
    output_file = save_evaluation_results(results, filename_base, responses)

    log_evaluation_end(f"{eval_name.upper()} EVALUATION", output_file)

    return output_file
