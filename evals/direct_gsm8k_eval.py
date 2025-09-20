#!/usr/bin/env python3
"""
GSM8K Evaluation Script
Tests model performance on grade school math problems.
"""

from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

from utils.eval_utils import (
    load_gsm8k_questions,
    save_evaluation_results,
    log_evaluation_start,
    log_evaluation_end,
    run_evaluation_main
)
from utils.utils import get_response, log


def evaluate_gsm8k(problems: List[Dict[str, Any]], num_trials: int = 5) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Evaluate model on GSM8K problems."""
    results = {
        "total_problems": len(problems),
        "correct_answers": 0,
        "total_attempts": 0,
        "accuracy": 0.0,
        "problem_results": []
    }

    responses = []  # Collect all individual responses

    for problem in problems:
        question = problem["question"]
        correct_answer = problem["answer"]

        log(f"\nEvaluating: {question}")
        log(f"Correct answer: {correct_answer}")

        correct_count = 0
        for trial in range(num_trials):
            try:
                prompt = f"{question}\n\nSolve this step by step and provide the final answer as a number in backticks like `42`."
                response = get_response(prompt)

                if response is None:
                    log(f"Trial {trial + 1}: No response")
                    responses.append({
                        "question_id": problem["id"],
                        "question": question,
                        "correct_answer": correct_answer,
                        "trial": trial + 1,
                        "response": None,
                        "extracted_answer": None,
                        "is_correct": False,
                        "error": "No response"
                    })
                    continue

                # Extract answer from response (simple extraction)
                if "`" in response:
                    extracted = response.split("`")[1].split("`")[0].strip()
                else:
                    extracted = response.strip()

                log(f"Trial {trial + 1}: {extracted}")

                is_correct = extracted == correct_answer
                if is_correct:
                    correct_count += 1

                responses.append({
                    "question_id": problem["id"],
                    "question": question,
                    "correct_answer": correct_answer,
                    "trial": trial + 1,
                    "response": response,
                    "extracted_answer": extracted,
                    "is_correct": is_correct,
                    "prompt": prompt
                })

            except Exception as e:
                log(f"Trial {trial + 1} failed: {e}")
                responses.append({
                    "question_id": problem["id"],
                    "question": question,
                    "correct_answer": correct_answer,
                    "trial": trial + 1,
                    "response": None,
                    "extracted_answer": None,
                    "is_correct": False,
                    "error": str(e)
                })

        accuracy = correct_count / num_trials
        results["correct_answers"] += correct_count
        results["total_attempts"] += num_trials

        problem_result = {
            "question": question,
            "correct_answer": correct_answer,
            "correct_count": correct_count,
            "accuracy": accuracy
        }
        results["problem_results"].append(problem_result)

        log(f"Problem accuracy: {accuracy:.2f}")

    results["accuracy"] = results["correct_answers"] / results["total_attempts"] if results["total_attempts"] > 0 else 0
    return results, responses

def main():
    """Main evaluation function."""
    def run_gsm8k_eval():
        problems = load_gsm8k_questions(10)
        return evaluate_gsm8k(problems)

    return run_evaluation_main(run_gsm8k_eval, "GSM8K", "Evaluate model performance on grade school math problems")

if __name__ == "__main__":
    main()