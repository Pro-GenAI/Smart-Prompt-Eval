#!/usr/bin/env python3
"""
Multilingual Prompting Evaluation
Tests model performance across different languages.
Based on the Multilingual_Prompting experiment.
"""

from typing import Dict, Optional, List
import json
from pathlib import Path

from smart_prompt_eval.utils.eval_utils import (
    load_gsm8k_questions,
    create_base_prompt,
    initialize_evaluation_results,
    run_evaluation_main,
    log_test_case_info,
)
from smart_prompt_eval.utils.common_utils import attempt, log


def load_translated_questions(
    language_code: str, num_questions: Optional[int] = None
) -> List[Dict]:
    """
    Load translated questions from JSONL file for a specific language.

    Args:
        language_code: Language code (e.g., 'de', 'es', 'fr')
        num_questions: Number of questions to load (None for all)

    Returns:
        List of translated question dictionaries
    """
    file_path = (
        Path(__file__).parent.parent / "datasets" / f"gsm8k_test_{language_code}.jsonl"
    )

    if not file_path.exists():
        log(f"Translated file not found: {file_path}")
        return []

    translated_questions = []
    try:
        with open(file_path, encoding="utf-8") as f:
            for line_num, line in enumerate(f):
                if line.strip():
                    try:
                        question_data = json.loads(line.strip())
                        translated_questions.append(question_data)
                        if num_questions and len(translated_questions) >= num_questions:
                            break
                    except json.JSONDecodeError as e:
                        log(f"Error parsing line {line_num + 1} in {file_path}: {e}")
                        continue
    except Exception as e:
        log(f"Error reading translated file {file_path}: {e}")
        return []

    log(f"Loaded {len(translated_questions)} translated questions for {language_code}")
    return translated_questions


def load_all_translated_questions() -> Dict[str, Dict[str, str]]:
    """
    Load all translated questions for all languages into a lookup dictionary.

    Returns:
        Dictionary mapping language_code -> {original_id -> translated_question}
    """
    languages = {
        "de": "German",
        "es": "Spanish",
        "fr": "French",
        "it": "Italian",
        "pt": "Portuguese",
    }

    translated_lookup = {}

    for lang_code, lang_name in languages.items():
        translated_questions = load_translated_questions(lang_code)
        lang_lookup = {}

        for q in translated_questions:
            original_id = q.get("original_id")
            if original_id:
                lang_lookup[original_id] = q["question"]

        translated_lookup[lang_code] = lang_lookup
        log(f"Loaded {len(lang_lookup)} translated questions for {lang_name}")

    return translated_lookup


def evaluate_multilingual_prompting():
    """Evaluate model performance across different languages on GSM8K questions."""

    test_questions = load_gsm8k_questions()

    # Load all translated questions once for efficient lookup
    translated_lookup = load_all_translated_questions()

    results = initialize_evaluation_results(
        "multilingual_prompting",
        "Testing model performance across different languages on GSM8K problems",
    )

    responses = []  # Collect all individual responses

    # Process by language instead of by question
    languages = ["German", "Spanish", "French", "Italian", "Portuguese"]
    lang_codes = {
        "German": "de",
        "Spanish": "es",
        "French": "fr",
        "Italian": "it",
        "Portuguese": "pt",
    }

    for language in languages:
        lang_code = lang_codes[language]

        log(f"\n{'='*60}")
        log(f"Processing {language} ({lang_code})")
        log(f"{'='*60}")

        # Get the lookup for this language
        lang_lookup = translated_lookup.get(lang_code, {})

        for i, test_case in enumerate(test_questions):
            question = test_case["question"]
            correct_answer = test_case["answer"]
            case_id = test_case["id"]

            # Find translated question
            translated_question = lang_lookup.get(case_id)
            if translated_question is None:
                log(f"Translated question not found for {language} ({case_id})")
                continue

            query = create_base_prompt(translated_question)
            is_correct, response_text = attempt(query, correct_answer)

            # Find or create the test case result
            case_result = None
            for cr in results["test_cases"]:
                if cr["id"] == case_id:
                    case_result = cr
                    break

            if case_result is None:
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
        evaluate_multilingual_prompting,
        "Multilingual Prompting",
        "Testing model performance across different languages on GSM8K problems",
    )
