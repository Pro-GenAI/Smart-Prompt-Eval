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
import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from translate import Translator

from smart_prompt_eval.utils.common_utils import env

translators = {}


def get_translator(lang: str) -> Translator:
    if lang not in translators:
        translators[lang] = Translator(
            to_lang=lang,
            provider=env("TRANSLATE_PROVIDER"),
            region=env("TRANSLATE_REGION"),
            secret_access_key=env("TRANSLATE_KEY"),
        )
    return translators[lang]


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
            translation = get_translator(target_lang).translate(text)
            if translation.startswith("MYMEMORY WARNING:"):
                raise ValueError("Translation service returned warning")
            if translation.startswith("QUERY LENGTH LIMIT EXCEEDED"):
                raise ValueError("Translation service returned length limit error")
            return str(translation)
        except Exception as e:
            print(f"Translation attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait before retry
            else:
                print(f"Translation failed after {max_retries} attempts")
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
    with open(filepath, encoding="utf-8") as f:
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
                print(f"Error parsing line {i+1}: {e}")
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


def main() -> int:
    """Main function to translate GSM8K dataset."""
    parser = argparse.ArgumentParser(
        description="Translate GSM8K dataset to multiple languages"
    )

    # Compute defaults relative to the package directory so the script can be
    # executed from the repo root and still find `smart_prompt_eval/datasets`.
    package_root = Path(__file__).resolve().parent
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
        print(f"Error: Input file {input_file} does not exist")
        return 1

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load original questions
    print(f"Loading questions from {input_file}")
    original_questions = load_gsm8k_questions(str(input_file), args.limit)
    print(f"Loaded {len(original_questions)} questions")

    if not original_questions:
        print("Error: No questions loaded from input file")
        return 1

    # Translate each question to all languages
    total_successful = 0
    total_processed = 0

    # Pre-load existing translations for all languages to check what already exists
    existing_translations: Dict[str, set[str]] = {}
    for lang_code in args.languages:
        if lang_code not in language_config:
            continue
        lang_name = language_config[lang_code]
        output_file = output_dir / f"gsm8k_test_{lang_code}.jsonl"
        existing_translations[lang_code] = set()

        if output_file.exists():
            print(
                f"Loading existing translations for {lang_name} ({lang_code}) "
                f"from {output_file}"
            )
            with open(output_file, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line.strip())
                            original_id = (
                                data.get("original_id") or data["id"].rsplit("_", 1)[0]
                            )
                            existing_translations[lang_code].add(original_id)
                        except json.JSONDecodeError:
                            continue
            print(
                f"Found {len(existing_translations[lang_code])} existing"
                f" translations for {lang_name}"
            )

    # Process each question across all languages
    for i, question_data in enumerate(original_questions):
        question_id = question_data["id"]
        original_question = question_data["question"]
        answer = question_data["answer"]

        print(f"\nProcessing question {i+1}/{len(original_questions)}: {question_id}")

        question_successful = 0

        for lang_code in args.languages:
            if lang_code not in language_config:
                continue

            lang_name = language_config[lang_code]
            output_file = output_dir / f"gsm8k_test_{lang_code}.jsonl"

            # Skip if already translated
            if question_id in existing_translations[lang_code]:
                # log(f"  {lang_name}: Already translated, skipping")
                continue

            print(f"  Translating to {lang_name}...")

            # Translate the question
            translated_question = translate_question(original_question, lang_code)

            # Open file in append mode and write the translation
            with open(output_file, "a", encoding="utf-8") as f:
                if translated_question:
                    # Create translated entry
                    translated_entry = {
                        "id": f"{question_id}_{lang_code}",
                        "original_id": question_id,
                        "question": translated_question,
                        "original_question": original_question,
                        "answer": answer,
                        "language": lang_code,
                        "language_name": lang_name,
                    }
                    f.write(json.dumps(translated_entry, ensure_ascii=False) + "\n")
                    question_successful += 1
                    print(f"  ✓ {lang_name}: Translated successfully")
                else:
                    print(f"  ✗ {lang_name}: Translation failed")
                    # Add original question as fallback
                    translated_entry = {
                        "id": f"{question_id}_{lang_code}",
                        "original_id": question_id,
                        "question": original_question,  # Fallback to original
                        "original_question": original_question,
                        "answer": answer,
                        "language": lang_code,
                        "language_name": lang_name,
                        "translation_failed": True,
                    }
                    f.write(json.dumps(translated_entry, ensure_ascii=False) + "\n")

        if question_successful > 0:
            print(f"  Completed {question_successful} translations for {question_id}")

        total_successful += question_successful
        total_processed += len([lang for lang in args.languages if lang in language_config])

    # Summary
    print("\n" + "=" * 60)
    print("TRANSLATION SUMMARY")
    print("=" * 60)
    print(f"Total questions processed: {len(original_questions)}")
    print(f"Total translation attempts: {total_processed}")
    print(f"Successful translations: {total_successful}")
    if total_processed > 0:
        success_rate = (total_successful / total_processed) * 100
        print(f"Success rate: {success_rate:.1f}%")
    print(f"Output directory: {output_dir}")

    return 0


if __name__ == "__main__":
    exit(main())
