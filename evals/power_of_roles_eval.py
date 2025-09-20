#!/usr/bin/env python3
"""
Power of Roles Evaluation
Tests the impact of different role configurations on model performance.
Based on the Power_of_Roles experiment.
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
from utils.utils import get_accuracy, log, user_message, system_message, bot_message
from typing import Dict, List
from utils.utils import ChatCompletionMessageParam

def create_role_variants(question: str) -> Dict[str, List[ChatCompletionMessageParam]]:
    """Create different role-based prompt configurations."""
    base_prompt = create_base_prompt(question)

    return {
        "user_only": [user_message(base_prompt)],
        "with_system": [
            system_message("You are a helpful math assistant. Always provide accurate calculations."),
            user_message(base_prompt)
        ],
        "with_assistant_history": [
            user_message("What is 2 + 2?"),
            bot_message("2 + 2 = 4"),
            user_message(base_prompt)
        ],
        "multiple_roles": [
            system_message("You are a math expert."),
            user_message("Please help me with this math problem."),
            bot_message("I'll be happy to help you solve this math problem."),
            user_message(base_prompt)
        ]
    }

def evaluate_power_of_roles():
    """Evaluate the impact of different role configurations on GSM8K questions."""

    # Load GSM8K test questions
    test_questions = load_gsm8k_questions(num_questions=3)

    results = initialize_evaluation_results(
        "power_of_roles",
        "Testing the impact of different role configurations on model performance with GSM8K problems"
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
            "role_results": {}
        }

        # Create role variants
        role_variants = create_role_variants(question)

        for role_name, messages in role_variants.items():
            log(f"\nTesting role configuration: {role_name}")

            # For role-based tests, we need to modify get_accuracy to handle messages
            # For now, we'll extract the user message content
            if isinstance(messages, list) and len(messages) > 0:
                # Find the last user message
                user_content = None
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        user_content = msg.get("content")
                        break

                if user_content:
                    accuracy = get_accuracy(user_content, correct_answer)
                else:
                    accuracy = "0.00%"
            else:
                accuracy = get_accuracy(str(messages), correct_answer)

            case_results["role_results"][role_name] = accuracy

            # Collect response data for this role configuration
            responses.append({
                "question_id": case_id,
                "question": question,
                "correct_answer": correct_answer,
                "role_config": role_name,
                "accuracy": accuracy,
                "messages": messages
            })

        results["test_cases"].append(case_results)

    return results, responses

if __name__ == "__main__":
    run_evaluation_main(evaluate_power_of_roles, "Power of Roles", "Testing the impact of different role configurations on model performance with GSM8K problems")