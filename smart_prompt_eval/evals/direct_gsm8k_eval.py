#!/usr/bin/env python3
"""
GSM8K Evaluation Script
Tests model performance on grade school math problems.
"""

from smart_prompt_eval.utils.eval_utils import (
    load_gsm8k_questions,
    create_base_prompt,
    initialize_evaluation_results,
    run_evaluation_main,
    log_test_case_info
)
from smart_prompt_eval.utils.common_utils import attempt, log


def evaluate_gsm8k():
    """Evaluate model performance on GSM8K problems."""

    # Load GSM8K test questions
    test_questions = load_gsm8k_questions()

    results = initialize_evaluation_results(
        "gsm8k",
        "Testing model performance on grade school math problems"
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
            "is_correct": False
        }

        # Create the prompt
        query = create_base_prompt(question)

        # Test the model
        log(f"\nTesting GSM8K problem")
        is_correct = attempt(query, correct_answer)
        case_results["is_correct"] = is_correct

        # Collect response data
        responses.append({
            "question_id": case_id,
            "question": question,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "prompt": query
        })

        results["test_cases"].append(case_results)

    return results, responses


if __name__ == "__main__":
    run_evaluation_main(
        evaluate_gsm8k,
        "GSM8K",
        "Testing model performance on grade school math problems"
    )
