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
- GSM8K dataset: datasets/gsm8k_test.jsonl
"""
import json
from pathlib import Path

from typing import Dict, List, Optional
import time
import argparse

# Safe import: if the package isn't installed, add repo root to sys.path so
# local imports like `from smart_prompt_eval.utils.common_utils import log`
# still work when running the script directly.
try:
    from smart_prompt_eval.utils.common_utils import log
except ModuleNotFoundError:
    import sys

    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    # Retry import
    from smart_prompt_eval.utils.common_utils import log


def translate_text(text: str, target_lang: str, max_retries: int = 5) -> Optional[str]:
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
    original_questions: List[Dict], target_lang: str, lang_name: str, output_file: str, existing_ids: set
) -> int:
    """
    Create a translated dataset for a specific language.

    Args:
        original_questions: List of original question dictionaries
        target_lang: Target language code
        lang_name: Human-readable language name
        output_file: Output file path
        existing_ids: Set of original IDs that have already been translated

    Returns:
        Number of successfully translated questions
    """
    translated_questions = []
    successful_translations = 0

    log(f"Starting translation to {lang_name} ({target_lang})")
    log(f"Processing {len(original_questions)} questions...")

    # Open file for writing (append if resuming, write if new)
    # mode = "a" if existing_ids else "w"
    with open(output_file, "a", encoding="utf-8") as f:
        for i, question_data in enumerate(original_questions):
            if (i + 1) % 5 == 0:
                log(f"Processed {i + 1}/{len(original_questions)} questions...")

            question_id = question_data["id"]
            original_question = question_data["question"]
            answer = question_data["answer"]

            # Skip if already translated
            if question_id in existing_ids:
                continue

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
                f.write(json.dumps(translated_entry, ensure_ascii=False) + "\n")
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
                f.write(json.dumps(translated_entry, ensure_ascii=False) + "\n")

    if successful_translations > 0:
        log(f"Saved {successful_translations} new questions to {output_file}")
    else:
        log(f"No new questions to save for {lang_name}")

    log(
        f"✓ Successfully processed {output_file} with {successful_translations} new translated questions"
    )
    return successful_translations


def main():
    """Main function to translate GSM8K dataset."""
    parser = argparse.ArgumentParser(
        description="Translate GSM8K dataset to multiple languages"
    )

    # Compute defaults relative to the package directory so the script can be
    # executed from the repo root and still find `smart_prompt_eval/datasets`.
    package_root = Path(__file__).resolve().parents[1]
    default_datasets_dir = package_root / "datasets"
    default_input = default_datasets_dir / "gsm8k_test.jsonl"

    parser.add_argument(
        "--input",
        "-i",
        default=str(default_input),
        help=f"Input GSM8K JSONL file path (default: {default_input})",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default=str(default_datasets_dir),
        help=f"Output directory for translated files (default: {default_datasets_dir})",
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

        # Load existing translated IDs to resume from where left off
        existing_ids = set()
        if output_file.exists():
            log(f"Loading existing translations for {lang_name} ({lang_code}) from {output_file}")
            with open(output_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line.strip())
                            original_id = data["id"].rsplit("_", 1)[0]  # Extract original ID, e.g., "gsm8k_1" from "gsm8k_1_es"
                            existing_ids.add(original_id)
                        except json.JSONDecodeError:
                            continue
            log(f"Found {len(existing_ids)} existing translations for {lang_name}")

        try:
            successful = create_translated_dataset(
                original_questions, lang_code, lang_name, str(output_file), existing_ids
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
