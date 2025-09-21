#!/usr/bin/env python3
"""
Multilingual Prompting Evaluation
Tests model performance across different languages.
Based on the Multilingual_Prompting experiment.
"""

from typing import Dict, Optional, List
import json
from pathlib import Path

from hack_prompt_eval.utils.eval_utils import (
    load_gsm8k_questions,
    create_base_prompt,
    initialize_evaluation_results,
    run_evaluation_main,
    log_test_case_info,
)
from hack_prompt_eval.utils.common_utils import attempt, log


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
    file_path = Path(__file__).parent / f"gsm8k_test_{language_code}.jsonl"

    if not file_path.exists():
        log(f"Translated file not found: {file_path}")
        return []

    translated_questions = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
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


def create_instruction_prompt(target_lang: str) -> str:
    """Create language-specific instruction prompts."""
    instructions = {
        "es": "Resuelve este problema y proporciona la respuesta final como un número entre comillas invertidas como `42`.",
        "fr": "Résous ce problème et fournis la réponse finale sous forme de nombre entre guillemets inversés comme `42`.",
        "de": "Löse dieses Problem und gib die endgültige Antwort als Zahl in Backticks wie `42` an.",
        "en": "Solve this problem and provide the final answer as a number in backticks like `42`.",
    }
    instruction = instructions.get(target_lang)
    if not instruction:
        raise ValueError(f"Unsupported language code: {target_lang}")
    return instruction


def create_language_variants_from_translated(
    original_question_id: str,
) -> Dict[str, str]:
    """Create language variants using pre-translated questions from JSONL files."""
    variants = {}

    # Language configurations
    languages = {"Spanish": "es", "French": "fr", "German": "de"} # "English": "en", 

    for lang_name, lang_code in languages.items():
        try:
            if lang_code == "en":
                # For English, load from original GSM8K file
                translated_question = get_original_question_by_id(original_question_id)
                if translated_question is None:
                    log(f"Could not find original question {original_question_id}")
                    continue
            else:
                # Load translated question from JSONL file
                translated_questions = load_translated_questions(
                    lang_code, num_questions=1
                )
                translated_question = None

                # Find the question with matching original_id
                for q in translated_questions:
                    if q.get("original_id") == original_question_id:
                        translated_question = q["question"]
                        break

                if translated_question is None:
                    log(
                        f"Translated question not found for {lang_name} ({original_question_id})"
                    )
                    continue

            # Create the full prompt with translated question and language-specific instructions
            instruction = create_instruction_prompt(lang_code)
            full_prompt = create_base_prompt(translated_question, instruction)

            variants[lang_name] = full_prompt
            log(f"✓ Loaded {lang_name} variant from translated file")

        except Exception as e:
            log(f"Error loading {lang_name} variant: {e}")
            # Fallback to original question with English instructions
            # if lang_code == "en":
            #     variants[lang_name] = create_base_prompt(
            #         get_original_question_by_id(original_question_id) or ""
            #     )

    return variants


# def get_original_question_by_id(question_id: str) -> Optional[str]:
#     """Get original English question by ID from GSM8K test file."""
#     try:
#         # Load from the original GSM8K file (load a large number to ensure we get the one we want)
#         original_questions = load_gsm8k_questions(
#             num_questions=1000
#         )  # Load many questions
#         for q in original_questions:
#             if q["id"] == question_id:
#                 return q["question"]
#     except Exception as e:
#         log(f"Error loading original question {question_id}: {e}")

#     return None


def evaluate_multilingual_prompting():
    """Evaluate model performance across different languages on GSM8K questions."""

    # Load GSM8K test questions
    test_questions = load_gsm8k_questions()

    results = initialize_evaluation_results(
        "multilingual_prompting",
        "Testing model performance across different languages on GSM8K problems",
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
            "language_results": {},
        }

        # Create language variants using pre-translated files
        variants = create_language_variants_from_translated(case_id)

        for language, query in variants.items():
            log(f"\nTesting language: {language}")
            is_correct = attempt(query, correct_answer)
            case_results["language_results"][language] = is_correct

            # Collect response data for this language
            responses.append(
                {
                    "question_id": case_id,
                    "question": question,
                    "correct_answer": correct_answer,
                    "language": language,
                    "accuracy": is_correct,
                    "prompt": query,
                }
            )

        results["test_cases"].append(case_results)

    return results, responses


if __name__ == "__main__":
    run_evaluation_main(
        evaluate_multilingual_prompting,
        "Multilingual Prompting",
        "Testing model performance across different languages on GSM8K problems",
    )
