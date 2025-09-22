#!/usr/bin/env python3
"""
Seed Consistency Evaluation
Tests whether different seed values affect model output consistency.
Based on the Does_Seed_Matter experiment.
"""

import sys

# from smart_prompt_eval.utils.common_utils import attempt
# from smart_prompt_eval.utils.eval_utils import (
#     create_base_prompt,
#     initialize_evaluation_results,
#     load_gsm8k_questions,
#     log_test_case_info,
#     run_evaluation_main,
# )

print("Warning: This file has been archived as it is not commonly used. Exiting...")
sys.exit(0)

# def evaluate_seed_consistency():
#     """Evaluate seed consistency across different GSM8K problems."""

#     test_questions = load_gsm8k_questions()

#     results = initialize_evaluation_results(
#         "seed_consistency",
#         "Testing if different seed values affect model output consistency on GSM8K problems",
#     )

#     responses = []  # Collect all individual responses
#     seeds = [0, 10, 20, 64]  # None,

#     for i, test_case in enumerate(test_questions):
#         question = test_case["question"]
#         correct_answer = test_case["answer"]
#         case_id = test_case["id"]

#         log_test_case_info(i, case_id, question, correct_answer)

#         case_results = {
#             "id": case_id,
#             "question": question,
#             "correct_answer": correct_answer,
#             "variant_results": {},
#         }

#         # Format question for the model
#         prompt = create_base_prompt(question)

#         for seed in seeds:
#             print(f"\nTesting with seed: {seed}")
#             is_correct, response_text = attempt(
#                 prompt, correct_answer, {"seed": seed} if seed is not None else {}
#             )
#             case_results["variant_results"][str(seed)] = is_correct

#             # Collect individual responses for this seed
#             responses.append(
#                 {
#                     "question_id": case_id,
#                     "question": question,
#                     "correct_answer": correct_answer,
#                     "seed": seed,
#                     "accuracy": is_correct,
#                     "prompt": prompt,
#                     "response": response_text,
#                 }
#             )

#         results["test_cases"].append(case_results)

#     return results, responses


# if __name__ == "__main__":
#     run_evaluation_main(
#         evaluate_seed_consistency,
#         "Seed Consistency",
#     )
