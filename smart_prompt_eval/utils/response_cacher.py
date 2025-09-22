import hashlib
import json
import os
from typing import Any, Dict, List, Optional, Union

# Simple response caching
CACHE_DIR = "response_cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def get_cache_key(messages: Union[str, List[Dict[str, Any]]], **kwargs: Any) -> str:
    """Generate a unique cache key based on request content."""
    if isinstance(messages, str):
        content = messages
    else:
        # For message lists, combine all content
        content = " ".join(
            [msg.get("content", "") for msg in messages if msg.get("content")]
        )

    # Include relevant kwargs in cache key
    cache_data = {
        "content": content,
        "model": kwargs.get("model", ""),
        "temperature": kwargs.get("temperature", 1.0),
        "max_tokens": kwargs.get("max_tokens"),
    }

    # Create hash of the cache data
    cache_str = json.dumps(cache_data, sort_keys=True)
    return hashlib.md5(cache_str.encode()).hexdigest()


def get_cached_response(cache_key: str) -> Optional[str]:
    """Get cached response if it exists."""
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                response = data.get("response")
                return response if isinstance(response, str) else None
        except (json.JSONDecodeError, KeyError):
            return None
    return None


def save_cached_response(cache_key: str, response: str, **kwargs: Any) -> None:
    """Save response to cache."""
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    data = {
        "response": response,
        "timestamp": (
            os.path.getctime(cache_file) if os.path.exists(cache_file) else None
        ),
        "kwargs": kwargs,
    }
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
