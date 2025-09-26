#!/usr/bin/env python3
"""
Multi-lang Prompting Evaluation
Tests model performance across different languages.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from smart_prompt_eval.utils.common_utils import attempt
from smart_prompt_eval.utils.eval_utils import (
    create_base_prompt,
    initialize_evaluation_results,
    load_gsm8k_questions,
    run_evaluation_main,
)


lang_codes = {
    "English": "en",
    "German": "de",
    "Spanish": "es",
    "French": "fr",
    "Italian": "it",
}

def load_all_translated_questions() -> Dict[str, Dict[str, str]]:
    """
    Load all translated questions for all languages into a lookup dictionary.

    Returns:
        Dictionary mapping language_code -> {original_id -> translated_question}
    """
    translated_lookup = {}  # lang_code -> {original_id -> translated_question}

    for lang_name, lang_code in lang_codes.items():
        if lang_name == "English":
            continue  # Skip English as it's the original
        translated_questions = load_gsm8k_questions(lang_code=lang_code)
        lang_lookup = {}  # original_id -> translated_question

        for translated_q in translated_questions:
            original_id = translated_q.get("original_id")
            lang_lookup[original_id] = translated_q["question"]

        translated_lookup[lang_code] = lang_lookup
        print(f"Loaded {len(lang_lookup)} translated questions for {lang_name}")

    return translated_lookup


def evaluate_multi_lang_prompting() -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Evaluate model performance across different languages on GSM8K questions."""

    test_questions = load_gsm8k_questions()  # Loads English questions

    # Load all translated questions once for efficient lookup
    translated_lookup = load_all_translated_questions()

    results = initialize_evaluation_results(
        "multi_lang_prompting",
        "Testing model performance across different languages on GSM8K problems",
    )

    responses = []  # Collect all individual responses

    for language, lang_code in lang_codes.items():
        # log(f"\n{'='*60}")
        print("\n")
        print(f"Processing {language} ({lang_code})")
        # log(f"{'='*60}")

        # Get the lookup for this language
        lang_lookup = translated_lookup.get(lang_code, {})

        for i, test_case in enumerate(test_questions):
            if i % 5 == 0:
                print(i, end=" ", flush=True)
            question = test_case["question"]
            correct_answer = test_case["answer"]
            case_id = test_case["id"]

            # Find translated question
            if language == "English":
                translated_question = question
            else:
                translated_question = lang_lookup.get(case_id)
                if translated_question is None:
                    print(f"Translated question not found for {language} ({case_id})")
                    continue

            query = create_base_prompt(translated_question)
            is_correct, response_text = attempt(query, correct_answer)

            # Find or create the test case result
            for cr in results["test_cases"]:
                if cr["id"] == case_id:
                    case_result = cr
                    break
            else:
                case_result = {
                    "id": case_id,
                    "question": question,
                    "correct_answer": correct_answer,
                    "variant_results": {},
                }
                results["test_cases"].append(case_result)

            # Add language result
            case_result["variant_results"][language] = is_correct

            # Collect response data
            responses.append(
                {
                    "question_id": case_id,
                    "question": question,
                    "correct_answer": correct_answer,
                    "language": language,
                    "accuracy": is_correct,
                    "prompt": query,
                    "response": response_text,
                }
            )

    return results, responses


if __name__ == "__main__":
    run_evaluation_main(
        evaluate_multi_lang_prompting,
        "Multi-lang Prompting",
    )
