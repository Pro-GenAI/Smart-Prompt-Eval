#!/usr/bin/env python3
"""
Linguistic Errors Evaluation
Tests model robustness to spelling and grammatical errors.
Based on the Linguistic_Errors experiment.
"""

from typing import Dict
import random

from smart_prompt_eval.utils.eval_utils import (
    load_gsm8k_questions,
    create_base_prompt,
    initialize_evaluation_results,
    run_evaluation_main,
    log_test_case_info,
)
from smart_prompt_eval.utils.common_utils import attempt, log

# Set random seed for reproducibility
random.seed(42)


def apply_character_repeated(text: str) -> str:
    """Apply character repetition errors to random characters in words."""
    words = text.split()
    modified_words = []

    for word in words:
        if len(word) <= 3:  # Skip very short words
            modified_words.append(word)
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

        modified_words.append("".join(modified_word))

    return " ".join(modified_words)


def apply_character_missing(text: str) -> str:
    """Remove random character from words longer than 5 characters."""
    words = text.split()
    modified_words = []

    for word in words:
        if len(word) > 5:
            # Remove a random character
            pos_to_remove = random.randint(0, len(word) - 1)
            modified_word = word[:pos_to_remove] + word[pos_to_remove + 1 :]
            modified_words.append(modified_word)
        else:
            modified_words.append(word)

    return " ".join(modified_words)


def apply_character_swapping(text: str, words_per_sentence: int = 3) -> str:
    """Swap characters in random words (3 words per sentence by default)."""
    words = text.split()
    if len(words) < 2:
        return text

    # Select random words to modify (up to words_per_sentence)
    num_words_to_modify = min(words_per_sentence, len(words))
    word_indices = random.sample(range(len(words)), num_words_to_modify)

    modified_words = words.copy()

    for idx in word_indices:
        word = modified_words[idx]
        if len(word) <= 3:  # Skip very short words
            continue

        # Swap 2 random characters
        pos1, pos2 = random.sample(range(len(word)), 2)
        word_list = list(word)
        word_list[pos1], word_list[pos2] = word_list[pos2], word_list[pos1]
        modified_words[idx] = "".join(word_list)

    return " ".join(modified_words)


def apply_word_swapping(text: str) -> str:
    """Swap 2 random words in the sentence."""
    words = text.split()
    if len(words) < 2:
        return text

    # Select 2 random word positions to swap
    pos1, pos2 = random.sample(range(len(words)), 2)

    # Swap the words
    words[pos1], words[pos2] = words[pos2], words[pos1]

    return " ".join(words)


# Set random seed for reproducibility of manipulating random characters
random.seed(42)


def create_error_variants(question: str) -> Dict[str, str]:
    """Create different linguistic error variants of a question."""
    return {
        # "original": create_base_prompt(question),
        "character_repeated": create_base_prompt(apply_character_repeated(question)),
        "character_missing": create_base_prompt(apply_character_missing(question)),
        "character_swapping": create_base_prompt(apply_character_swapping(question)),
        "word_swapping": create_base_prompt(apply_word_swapping(question)),
    }


def evaluate_linguistic_errors():
    """Evaluate model performance with linguistic errors on GSM8K questions."""

    # Load GSM8K test questions
    test_questions = load_gsm8k_questions()

    results = initialize_evaluation_results(
        "linguistic_errors",
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

        # Create error variants
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
        evaluate_linguistic_errors,
        "Linguistic Errors",
        "Testing model robustness to spelling and grammatical errors on GSM8K problems",
    )
