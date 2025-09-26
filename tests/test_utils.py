"""Unit tests for utility modules in smart_prompt_eval."""

import json
from pathlib import Path
from typing import Any, Dict

from smart_prompt_eval import translate_gsm8k
from smart_prompt_eval.utils import common_utils, eval_utils


def test_remove_spaces_after_commas():
    assert common_utils.remove_spaces_after_commas("a, b,  c, d") == "a,b,c,d"
    assert common_utils.remove_spaces_after_commas("no_commas") == "no_commas"
    assert common_utils.remove_spaces_after_commas("") == ""


def test_extract_answer_various_formats():
    assert common_utils.extract_answer("") == ""
    assert common_utils.extract_answer(None) == ""
    assert common_utils.extract_answer("#### 42\nSome explanation") == "42"
    assert common_utils.extract_answer("$1,234.00 #### 1,234.00") == "1234"
    assert common_utils.extract_answer("€99.00 #### 99") == "99"
    assert common_utils.extract_answer("1000 feet #### 1000 feet") == "1000"
    # trailing percent and decimals
    assert common_utils.extract_answer("#### 50%") == "50"


def test_response_cacher_key_and_persistence(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # Ensure fresh module import context for response_cacher
    import importlib

    import smart_prompt_eval.utils.response_cacher as rc

    importlib.reload(rc)

    # Basic key generation
    key1 = rc.get_cache_key("hello world", model="mymodel", temperature=0.5)
    key2 = rc.get_cache_key(
        [{"role": "user", "content": "hello world"}], model="mymodel", temperature=0.5
    )
    assert isinstance(key1, str) and len(key1) > 0
    assert key1 == key2

    # Test saving and retrieving
    assert rc.get_cached_response(key1) is None
    rc.save_cached_response(key1, "my response")
    assert rc.get_cached_response(key1) == "my response"

    # File should be created
    assert (tmp_path / "response_cache.json").exists()
    # Reload and verify persistence
    importlib.reload(rc)
    assert rc.CACHE.get(key1) == "my response"


def test_eval_utils_extract_and_prompt_and_init():
    # extract_final_answer
    assert eval_utils.extract_final_answer("Some reasoning #### 5") == "5"
    assert eval_utils.extract_final_answer("No delim here") == "No delim here"

    # create_base_prompt
    q = "What is 2+2?"
    prompt = eval_utils.create_base_prompt(q)
    assert q in prompt
    assert "####" in prompt

    # initialize_evaluation_results
    res = eval_utils.initialize_evaluation_results("exp1", "desc")
    assert res["experiment"] == "exp1"
    assert res["description"] == "desc"
    assert res["test_cases"] == []


def test_run_evaluation_main_single_and_variant(tmp_path: Path, monkeypatch):
    # Prevent writing results to the real results dir by monkeypatching project_root
    monkeypatch.setattr(eval_utils, "project_root", tmp_path)

    # Case 1: single boolean results
    def eval_fn_single() -> Dict[str, Any]:
        return {
            "test_cases": [
                {"id": "c1", "is_correct": True},
                {"id": "c2", "is_correct": False},
            ]
        }

    result_file, responses_file = eval_utils.run_evaluation_main(
        eval_fn_single, "TestEvalSingle"
    )
    assert result_file.exists()
    with open(result_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["total_problems"] == 2
    assert data["total_attempts"] == 2
    assert data["correct_answers"] == 1
    assert abs(data["accuracy"] - 0.5) < 1e-6

    # Case 2: variant results
    def eval_fn_variant():
        return {
            "test_cases": [
                {"id": "c1", "variant_results": {"a": True, "b": False}},
                {"id": "c2", "variant_results": {"a": True, "b": True}},
            ]
        }

    result_file2, _ = eval_utils.run_evaluation_main(eval_fn_variant, "TestEvalVariant")
    assert result_file2.exists()
    with open(result_file2, "r", encoding="utf-8") as f:
        data2 = json.load(f)
    # total attempts = 2 + 2 = 4
    assert data2["total_attempts"] == 4
    # correct answers = 1 + 2 = 3
    assert data2["correct_answers"] == 3
    assert "per_variant_summary" in data2
    assert data2["per_variant_summary"]["a"]["attempts"] == 2
    assert data2["per_variant_summary"]["a"]["correct"] == 2


# Small smoke test to ensure package version still matches
def test_package_version():
    import smart_prompt_eval

    assert str(smart_prompt_eval.__version__) == "0.0.1"


def test_translate_load_gsm8k_questions(tmp_path: Path):
    # Create a small JSONL file with two entries and one invalid line
    data = [
        {"question": "What is 1+1?", "answer": "2"},
        {"question": "What is 3+4?", "answer": "7"},
    ]
    file = tmp_path / "gsm8k_test_small.jsonl"
    with open(file, "w", encoding="utf-8") as f:
        f.write(json.dumps(data[0]) + "\n")
        f.write("not a json\n")
        f.write(json.dumps(data[1]) + "\n")

    loaded = translate_gsm8k.load_gsm8k_questions(str(file))
    # Should load two valid entries
    assert len(loaded) == 2
    assert loaded[0]["question"] == "What is 1+1?"


def test_translate_translate_text_success_and_warnings(monkeypatch):
    # Monkeypatch get_translator to return an object with translate method
    class FakeTranslator:
        def __init__(self, responses):
            self._responses = responses
            self._idx = 0

        def translate(self, text):
            r = self._responses[self._idx]
            self._idx = min(self._idx + 1, len(self._responses) - 1)
            return r

    # Replace the module-level translators dict and get_translator
    monkeypatch.setitem(translate_gsm8k.__dict__, "translators", {})

    # Case: success on first try
    monkeypatch.setitem(
        translate_gsm8k.__dict__, "get_translator", lambda lang: FakeTranslator(["Hola"])
    )
    assert translate_gsm8k.translate_text("Hello", "es") == "Hola"

    # Case: translator returns a warning then success. We must return the
    # same translator instance across attempts so the second call yields
    # the success response.
    warn_then_ok = FakeTranslator(["MYMEMORY WARNING: something", "Bonjour"])
    monkeypatch.setitem(translate_gsm8k.__dict__, "get_translator", lambda lang: warn_then_ok)
    assert translate_gsm8k.translate_text("Hello", "fr", max_retries=2) == "Bonjour"

    # Case: translator keeps failing
    def fake_get_translator_fail(lang):
        return FakeTranslator(["MYMEMORY WARNING: x", "QUERY LENGTH LIMIT EXCEEDED"])

    monkeypatch.setitem(translate_gsm8k.__dict__, "get_translator", fake_get_translator_fail)
    assert translate_gsm8k.translate_text("Hello", "ru", max_retries=2) is None
