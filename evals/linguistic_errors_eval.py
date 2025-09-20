#!/usr/bin/env python3
"""
Linguistic Errors Evaluation
Tests model robustness to spelling and grammatical errors.
Based on the Linguistic_Errors experiment.
"""

from utils.eval_utils import (
    load_gsm8k_questions,
    save_evaluation_results,
    log_evaluation_start,
    log_evaluation_end,
    create_base_prompt,
    initialize_evaluation_results,
    run_evaluation_main,
    log_test_case_info
)
from utils.utils import get_accuracy, log
from typing import Dict

def create_error_variants(question: str) -> Dict[str, str]:
    """Create different linguistic error variants of a question."""
    return {
        "original": create_base_prompt(question),
        "spelling_errors": f"{question.replace('sold', 'sol').replace('clips', 'clps').replace('friends', 'frnds')}\n\nSolve this prblem and provid the final answr as a numbr in backticks lik `42`.",
        "grammar_errors": f"{question}\n\nSolving this problem and providing the final answer as a number in backticks like `42`.",
        "combined_errors": f"{question.replace('sold', 'sol').replace('clips', 'clps')}\n\nSolving this prblem and provid the final answr as a numbr in bacticks lik `42`."
    }

def evaluate_linguistic_errors():
    """Evaluate model performance with linguistic errors on GSM8K questions."""

    # Load GSM8K test questions
    test_questions = load_gsm8k_questions(num_questions=5)

    results = initialize_evaluation_results(
        "linguistic_errors",
        "Testing model robustness to spelling and grammatical errors on GSM8K problems"
    )

    responses = []  # Collect all individual responses

    for i, test_case in enumerate(test_questions):
        question = test_case["question"]
        correct_answer = test_case["answer"]
        case_id = test_case["id"]

        log_test_case_info(i, case_id, question, correct_answer)

        case_results = {
            "id": case_id,
            "question": question,
            "correct_answer": correct_answer,
            "variant_results": {}
        }

        # Create error variants
        variants = create_error_variants(question)

        for variant_name, query in variants.items():
            log(f"\nTesting variant: {variant_name}")
            accuracy = get_accuracy(query, correct_answer)
            case_results["variant_results"][variant_name] = accuracy

            # Collect response data for this variant
            responses.append({
                "question_id": case_id,
                "question": question,
                "correct_answer": correct_answer,
                "variant": variant_name,
                "accuracy": accuracy,
                "prompt": query
            })

        results["test_cases"].append(case_results)

    return results, responses

if __name__ == "__main__":
    run_evaluation_main(evaluate_linguistic_errors, "Linguistic Errors", "Testing model robustness to spelling and grammatical errors on GSM8K problems")