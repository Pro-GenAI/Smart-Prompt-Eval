#!/usr/bin/env python3
"""
Seed Consistency Evaluation
Tests whether different seed values affect model output consistency.
Based on the Does_Seed_Matter experiment.
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

def evaluate_seed_consistency():
    """Evaluate seed consistency across different GSM8K problems."""

    # Load GSM8K test questions
    test_questions = load_gsm8k_questions(num_questions=5)

    results = initialize_evaluation_results(
        "seed_consistency",
        "Testing if different seed values affect model output consistency on GSM8K problems"
    )

    responses = []  # Collect all individual responses
    seeds = [None, 0, 10, 20, 64]

    for i, test_case in enumerate(test_questions):
        question = test_case["question"]
        correct_answer = test_case["answer"]
        case_id = test_case["id"]

        log_test_case_info(i, case_id, question, correct_answer)

        case_results = {
            "id": case_id,
            "question": question,
            "correct_answer": correct_answer,
            "seed_results": {}
        }

        # Format question for the model
        query = f"{question}\n\nSolve this problem and provide the final answer as a number in backticks like `42`."

        for seed in seeds:
            log(f"\nTesting with seed: {seed}")
            accuracy = get_accuracy(query, correct_answer, {"seed": seed} if seed is not None else {})
            case_results["seed_results"][str(seed)] = accuracy

            # Collect individual responses for this seed (this is a simplified version)
            # In a real implementation, we'd need to modify get_accuracy to return responses
            responses.append({
                "question_id": case_id,
                "question": question,
                "correct_answer": correct_answer,
                "seed": seed,
                "accuracy": accuracy,
                "prompt": query
            })

        results["test_cases"].append(case_results)

    return results, responses

if __name__ == "__main__":
    run_evaluation_main(evaluate_seed_consistency, "Seed Consistency", "Testing if different seed values affect model output consistency on GSM8K problems")
