#!/usr/bin/env python3
"""
Multiple Roles Evaluation
Tests the impact of different role configurations on model performance.
"""

from typing import Dict, List

from smart_prompt_eval.utils.common_utils import (
    attempt,
    bot_message,
    log,
    system_message,
    user_message,
)
from smart_prompt_eval.utils.eval_utils import (
    create_base_prompt,
    initialize_evaluation_results,
    load_gsm8k_questions,
    log_test_case_info,
    run_evaluation_main,
)


def create_role_variants(question: str) -> Dict[str, List[Dict[str, str]]]:
    """Create different role-based prompt configurations."""
    prompt = create_base_prompt(question)

    return {
        # "user_only": [user_message(prompt)],
        "with_system": [
            system_message(
                "You are a helpful math assistant. Always provide accurate calculations."
            ),
            user_message(prompt),
        ],
        "with_assistant_sample_response": [
            user_message("What is 2 kgs + 2 kgs?"),
            bot_message(
                "When we add 2 with 2, we calculate the sum is 2 kgs + 2 kgs = 4 kgs  \n#### 4"
            ),
            user_message(prompt),
        ],
        "with_bot_promise": [
            system_message("You are a math expert."),
            user_message("Please help me with this math problem."),
            bot_message("I'll be happy to help you solve this math problem."),
            user_message(prompt),
        ],
    }


def evaluate_power_of_roles():
    """Evaluate the impact of different role configurations on GSM8K questions."""

    test_questions = load_gsm8k_questions()

    results = initialize_evaluation_results(
        "power_of_roles",
        "Testing the impact of different role configurations on model performance with GSM8K problems",
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
            "variant_results": {},
        }

        # Create role variants
        role_variants = create_role_variants(question)

        for role_name, messages in role_variants.items():
            # log(f"\nTesting role configuration: {role_name}")

            # For role-based tests, we need to modify attempt to handle messages
            # For now, we'll extract the user message content
            if isinstance(messages, list) and len(messages) > 0:
                # Find the last user message
                user_content = None
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        user_content = msg.get("content")
                        break

                if user_content:
                    is_correct, response_text = attempt(user_content, correct_answer)
                else:
                    is_correct, response_text = (
                        False,
                        "",
                    )  # Default to False if no user content found
            else:
                is_correct, response_text = attempt(str(messages), correct_answer)

            case_results["variant_results"][role_name] = is_correct

            # Collect response data for this role configuration
            responses.append(
                {
                    "question_id": case_id,
                    "question": question,
                    "correct_answer": correct_answer,
                    "role_config": role_name,
                    "accuracy": is_correct,
                    "messages": messages,
                    "response": response_text,
                }
            )

        results["test_cases"].append(case_results)

    return results, responses


if __name__ == "__main__":
    run_evaluation_main(
        evaluate_power_of_roles,
        "Multiple Roles",
        "Testing the impact of different role configurations on model performance with GSM8K problems",
    )
