"""Tests for common_utils.get_response with mocked OpenAI client and cacher."""

from types import SimpleNamespace

import smart_prompt_eval.utils.common_utils as common_utils

# Ensure OPENAI_MODEL is set after importing common_utils,
#  as common_utils loads the .env file.
common_utils.model = "test-model"


class FakeChoice:
    def __init__(self, content):
        self.message = SimpleNamespace(content=content)


class FakeResponse:
    def __init__(self, content):
        self.choices = [FakeChoice(content)]


class FakeRateLimitError(Exception):
    pass


def test_get_response_uses_cache(monkeypatch):
    # Simulate cache hit by monkeypatching the functions used inside common_utils
    monkeypatch.setattr(common_utils, "get_cached_response", lambda key: "cached text")
    monkeypatch.setattr(common_utils, "save_cached_response", lambda k, v: None)

    # Ensure client is not called by replacing create with a function that raises
    monkeypatch.setattr(
        common_utils.client.chat.completions,
        "create",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("should not be called")),
    )

    res = common_utils.get_response("Hello world")
    assert res == "cached text"


def test_get_response_calls_api_and_saves(monkeypatch, tmp_path):
    # Simulate cache miss initially by patching the functions in common_utils
    monkeypatch.setattr(common_utils, "get_cached_response", lambda key: None)

    saved = {}

    def fake_save(key, value):
        saved["key"] = key
        saved["value"] = value

    monkeypatch.setattr(common_utils, "save_cached_response", fake_save)

    # Mock client to return a fake response
    def fake_create(messages=None, **kwargs):
        return FakeResponse("hello from api")

    monkeypatch.setattr(common_utils.client.chat.completions, "create", fake_create)

    res = common_utils.get_response("Hello world")
    assert res == "hello from api"
    assert saved["value"] == "hello from api"


def test_get_response_rate_limit_retries(monkeypatch):
    # Simulate cache miss by patching common_utils's references
    monkeypatch.setattr(common_utils, "get_cached_response", lambda key: None)
    monkeypatch.setattr(common_utils, "save_cached_response", lambda k, v: None)

    # Prepare a fake that raises a RateLimit error twice, then returns a valid response
    calls = {"n": 0}

    # Monkeypatch the RateLimitError symbol used in common_utils to a simple
    # Exception subclass so raising it is straightforward in tests.
    class SimpleRateLimitError(Exception):
        pass

    monkeypatch.setattr(common_utils.openai, "RateLimitError", SimpleRateLimitError)

    def fake_create(messages=None, **kwargs):
        calls["n"] += 1
        if calls["n"] <= 2:
            raise SimpleRateLimitError("rate limit")
        return FakeResponse("ok after retry")

    # Prevent long sleeps during retry handling
    monkeypatch.setattr(common_utils.time, "sleep", lambda s: None)
    monkeypatch.setattr(common_utils.client.chat.completions, "create", fake_create)

    res = common_utils.get_response("Hello world")
    assert res == "ok after retry"
    assert calls["n"] == 3


def test_get_response_fails_after_retries(monkeypatch):
    # Simulate cache miss by patching common_utils's references
    monkeypatch.setattr(common_utils, "get_cached_response", lambda key: None)
    monkeypatch.setattr(common_utils, "save_cached_response", lambda k, v: None)

    # Prepare a fake that always raises a generic exception
    def fake_create(messages=None, **kwargs):
        raise Exception("API down")

    # Ensure no slow sleeps (not strictly needed for generic errors but safe)
    monkeypatch.setattr(common_utils.time, "sleep", lambda s: None)
    monkeypatch.setattr(common_utils.client.chat.completions, "create", fake_create)

    res = common_utils.get_response("Hello world")
    assert res is None
