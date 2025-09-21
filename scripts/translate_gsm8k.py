#!/usr/bin/env python3
"""
GSM8K Translation Script
Translates the GSM8K dataset into multiple languages and saves as JSONL files.

USAGE:
    python translate-gsm8k.py --languages de es fr --limit 100
    python translate-gsm8k.py --languages zh ja ko --limit 50
    python translate-gsm8k.py --languages all --limit 0  # Translate all questions

OUTPUT FORMAT:
Each translated file (e.g., gsm8k_test_de.jsonl) contains JSONL format with:
- id: unique ID for translated question (e.g., "gsm8k_1_de")
- original_id: reference to original question (e.g., "gsm8k_1")
- question: translated question text
- original_question: original English question
- answer: original answer (unchanged)
- language: language code (e.g., "de")
- language_name: full language name (e.g., "German")

SUPPORTED LANGUAGES:
- de: German
- es: Spanish
- fr: French
- zh: Chinese
- ja: Japanese
- ko: Korean
- it: Italian
- pt: Portuguese
- ru: Russian
- ar: Arabic
- hi: Hindi

REQUIRES:
- GSM8K dataset: evals/gsm8k_test.jsonl
"""
import json
import sys
from pathlib import Path

# Ensure project root is on sys.path so top-level imports like `utils` resolve
# when running this script directly (e.g. `python scripts/translate_gsm8k.py`).
# Project root is the parent of this script's directory.
_THIS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = str(_THIS_DIR.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from typing import Dict, List, Optional
import time
import argparse

from utils.common_utils import log


def translate_text(text: str, target_lang: str, max_retries: int = 3) -> Optional[str]:
    """
    Translate text to target language using translation service.

    Args:
        text: Text to translate
        target_lang: Target language code (e.g., 'es', 'fr', 'de')
        max_retries: Maximum number of retry attempts

    Returns:
        Translated text or None if translation fails
    """
    for attempt in range(max_retries):
        try:
            # Lazy import to avoid requiring the `translate` package unless translation is actually run
            from translate import Translator

            translator = Translator(to_lang=target_lang)
            translation = translator.translate(text)
            return translation
        except Exception as e:
            log(f"Translation attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait before retry
            else:
                log(f"Translation failed after {max_retries} attempts")
                return None

    return None


def load_gsm8k_questions(filepath: str, limit: Optional[int] = None) -> List[Dict]:
    """
    Load GSM8K questions from JSONL file.

    Args:
        filepath: Path to the JSONL file
        limit: Maximum number of questions to load (None for all)

    Returns:
        List of question dictionaries
    """
    questions = []
    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if limit and i >= limit:
                break
            try:
                data = json.loads(line.strip())
                questions.append(
                    {
                        "id": f"gsm8k_{i+1}",
                        "question": data["question"],
                        "answer": data["answer"],
                    }
                )
            except json.JSONDecodeError as e:
                log(f"Error parsing line {i+1}: {e}")
                continue

    return questions


def translate_question(question: str, target_lang: str) -> Optional[str]:
    """
    Translate a single question to target language.

    Args:
        question: Question text to translate
        target_lang: Target language code

    Returns:
        Translated question or None if failed
    """
    return translate_text(question, target_lang)


def create_translated_dataset(
    original_questions: List[Dict], target_lang: str, lang_name: str, output_file: str
) -> int:
    """
    Create a translated dataset for a specific language.

    Args:
        original_questions: List of original question dictionaries
        target_lang: Target language code
        lang_name: Human-readable language name
        output_file: Output file path

    Returns:
        Number of successfully translated questions
    """
    translated_questions = []
    successful_translations = 0

    log(f"Starting translation to {lang_name} ({target_lang})")
    log(f"Processing {len(original_questions)} questions...")

    for i, question_data in enumerate(original_questions):
        if (i + 1) % 50 == 0:
            log(f"Processed {i + 1}/{len(original_questions)} questions...")

        question_id = question_data["id"]
        original_question = question_data["question"]
        answer = question_data["answer"]

        # Translate the question
        translated_question = translate_question(original_question, target_lang)

        if translated_question:
            # Create translated entry
            translated_entry = {
                "id": f"{question_id}_{target_lang}",
                "original_id": question_id,
                "question": translated_question,
                "original_question": original_question,
                "answer": answer,
                "language": target_lang,
                "language_name": lang_name,
            }
            translated_questions.append(translated_entry)
            successful_translations += 1
        else:
            log(f"Failed to translate question {question_id}")
            # Add original question as fallback
            translated_entry = {
                "id": f"{question_id}_{target_lang}",
                "original_id": question_id,
                "question": original_question,  # Fallback to original
                "original_question": original_question,
                "answer": answer,
                "language": target_lang,
                "language_name": lang_name,
                "translation_failed": True,
            }
            translated_questions.append(translated_entry)

    # Save to JSONL file
    log(f"Saving {len(translated_questions)} questions to {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        for entry in translated_questions:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    log(
        f"✓ Successfully created {output_file} with {successful_translations}/{len(original_questions)} translated questions"
    )
    return successful_translations


def main():
    """Main function to translate GSM8K dataset."""
    parser = argparse.ArgumentParser(
        description="Translate GSM8K dataset to multiple languages"
    )
    parser.add_argument(
        "--input",
        "-i",
        default="./evals/gsm8k_test.jsonl",
        help="Input GSM8K JSONL file path",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="./evals",
        help="Output directory for translated files",
    )
    parser.add_argument(
        "--languages",
        "-l",
        nargs="+",
        default=["es", "fr", "de", "it", "pt"],
        help="Target languages (default: es fr de it pt)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of questions to translate (default: all)",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")

    args = parser.parse_args()

    # Language configurations
    language_config = {
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
    }

    # Validate input file
    input_file = Path(args.input)
    if not input_file.exists():
        log(f"Error: Input file {input_file} does not exist")
        return 1

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load original questions
    log(f"Loading questions from {input_file}")
    original_questions = load_gsm8k_questions(str(input_file), args.limit)
    log(f"Loaded {len(original_questions)} questions")

    if not original_questions:
        log("Error: No questions loaded from input file")
        return 1

    # Translate to each language
    total_successful = 0
    total_processed = 0

    for lang_code in args.languages:
        if lang_code not in language_config:
            log(f"Warning: Unknown language code '{lang_code}', skipping")
            continue

        lang_name = language_config[lang_code]
        output_file = output_dir / f"gsm8k_test_{lang_code}.jsonl"

        # Check if file exists
        if output_file.exists() and not args.force:
            log(
                f"Skipping {lang_name} ({lang_code}) - file already exists: {output_file}"
            )
            log("Use --force to overwrite existing files")
            continue

        try:
            successful = create_translated_dataset(
                original_questions, lang_code, lang_name, str(output_file)
            )
            total_successful += successful
            total_processed += len(original_questions)

        except Exception as e:
            log(f"Error translating to {lang_name}: {e}")
            continue

    # Summary
    log("\n" + "=" * 60)
    log("TRANSLATION SUMMARY")
    log("=" * 60)
    log(f"Total questions processed: {total_processed}")
    log(f"Successful translations: {total_successful}")
    log(".1f")
    log(f"Output directory: {output_dir}")

    return 0


if __name__ == "__main__":
    exit(main())
