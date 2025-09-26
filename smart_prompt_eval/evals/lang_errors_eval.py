#!/usr/bin/env python3
"""
Language Errors Evaluation
Tests model robustness to spelling and grammatical errors.
"""

import random
import re
from typing import Any, Dict, List

from smart_prompt_eval.utils.common_utils import attempt
from smart_prompt_eval.utils.eval_utils import (
    create_base_prompt,
    initialize_evaluation_results,
    load_gsm8k_questions,
    log_test_case_info,
    run_evaluation_main,
)


def is_numeric_token(token: str) -> bool:
    """Return True if token contains digits or common currency/percent signs."""
    # Treat tokens with digits or currency/percent symbols as numeric-like and skip them.
    return bool(re.search(r'[\d\$€£¥%]', token))

def should_manipulate(word: str, min_length: int = 3) -> bool:
    """Decide whether to manipulate a word based on its characteristics."""
    # Skip very short words and numeric/currency tokens
    if len(word) < min_length or is_numeric_token(word):
        return False
    should_repeat = random.random() < 0.2
    if not should_repeat:
        return False
    return True


def apply_character_repeated(text: str) -> str:
    """Apply character repetition errors to random characters in words."""
    # Set random seed for reproducibility of manipulating random characters
    random.seed(42 + len(text))

    words = text.split()
    new_sentence = []

    for word in words:
        if not should_manipulate(word):
            new_sentence.append(word)
            continue

        # Select random characters to repeat (1-3 characters)
        num_chars_to_repeat = random.randint(1, min(3, len(word) - 1))
        positions = random.sample(range(len(word)), num_chars_to_repeat)

        modified_word = list(word)
        for pos in sorted(positions):
            char = modified_word[pos]
            # Repeat the character 1-2 times
            repeats = random.randint(1, 2)
            modified_word[pos] = char * (repeats + 1)

        new_sentence.append("".join(modified_word))

    return " ".join(new_sentence)


def apply_character_missing(text: str) -> str:
    """Remove random character from words longer than 5 characters."""
    random.seed(42 + len(text))

    words = text.split()
    new_sentence = []

    for word in words:
        if should_manipulate(word, min_length=6):
            new_sentence.append(word)
            continue

        # Remove a random character
        pos_to_remove = random.randint(0, len(word) - 1)
        modified_word = word[:pos_to_remove] + word[pos_to_remove + 1 :]
        new_sentence.append(modified_word)

    return " ".join(new_sentence)


words_swapped_per_sentence = 3

def apply_character_swapping(text: str) -> str:
    """Swap characters in random words (3 words per sentence by default)."""
    random.seed(42 + len(text))

    # Select random words to modify (up to the limit)
    words = text.split()
    num_words_to_modify = min(words_swapped_per_sentence, len(words))
    word_indices = random.sample(range(len(words)), num_words_to_modify)

    modified_words = words.copy()

    for idx in word_indices:
        word = modified_words[idx]
        if not should_manipulate(word):
            continue

        # Find positions where consecutive characters are different
        possible_positions = [i for i in range(len(word) - 1) if word[i] != word[i + 1]]
        if not possible_positions:
            continue
        # Select random position to swap consecutive characters
        pos = random.choice(possible_positions)
        word_list = list(word)
        word_list[pos], word_list[pos + 1] = word_list[pos + 1], word_list[pos]
        modified_words[idx] = "".join(word_list)

    return " ".join(modified_words)


# def apply_word_swapping(text: str) -> str:
#     """Swap 2 random words in the sentence."""
#     random.seed(42 + len(text))

#     words = text.split()
#     if len(words) < 2:
#         return text
#     # Swap only consecutive words: pick an index i and swap words[i] and words[i+1]
#     if len(words) == 2:
#         i = 0
#     else:
#         i = random.randint(0, len(words) - 2)
#     words[i], words[i + 1] = words[i + 1], words[i]
#     return " ".join(words)


def create_error_variants(question: str) -> Dict[str, str]:
    """Create different language error variants of a question."""
    return {
        "original": create_base_prompt(question),
        "character_repeated": create_base_prompt(apply_character_repeated(question)),
        "character_missing": create_base_prompt(apply_character_missing(question)),
        "character_swapping": create_base_prompt(apply_character_swapping(question)),
        # "word_swapping": create_base_prompt(apply_word_swapping(question)),
    }


def evaluate_language_errors() -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Evaluate model performance with language errors on GSM8K questions."""

    # Load GSM8K test questions
    test_questions = load_gsm8k_questions()

    results = initialize_evaluation_results(
        "lang_errors",
        "Testing model robustness to spelling and grammatical errors on GSM8K problems",
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

        variants = create_error_variants(question)

        for variant_name, query in variants.items():
            is_correct, response_text = attempt(query, correct_answer)
            case_results["variant_results"][variant_name] = is_correct

            # Collect response data for this variant
            responses.append(
                {
                    "question_id": case_id,
                    "question": question,
                    "correct_answer": correct_answer,
                    "variant": variant_name,
                    "accuracy": is_correct,
                    "prompt": query,
                    "response": response_text,
                }
            )

        results["test_cases"].append(case_results)

    return results, responses


if __name__ == "__main__":
    run_evaluation_main(
        evaluate_language_errors,
        "Language Errors",
    )
