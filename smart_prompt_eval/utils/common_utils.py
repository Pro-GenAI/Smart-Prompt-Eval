import os
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import openai
from dotenv import load_dotenv

from smart_prompt_eval.utils.response_cacher import (
    get_cache_key,
    get_cached_response,
    save_cached_response,
)


def print_progress(chr: str = ".") -> None:
    print(chr, end="", flush=True)


def print_error(chr: str = " E ") -> None:
    print_progress(chr)


def remove_spaces_after_commas(text: str) -> str:
    # remove spaces after commas, but not before commas
    return ",".join([part.strip() for part in text.split(",")])


def extract_answer(answer: Any) -> str:
    if not answer:
        return ""
    # Create a copy to avoid modifying the original
    answer = str(answer)
    # In GSM8K, answer exists after the last #### in the last part.
    answer = answer.split("####")[-1].split("\n")[0].strip()

    # Clean the answer to get only numbers.
    answer = answer.lstrip("$").lstrip("€").strip()  # Remove currency symbols
    answer = (
        answer.rstrip("%").rstrip(".00").strip()
    )  # Remove percentage and trailing zeros
    answer = answer.replace(",", "")  # Remove commas. Example: $1,000.00 -> 1000
    # Select first word by excluding units such as 'years', 'feet', etc.
    # Example: '1000 feet' -> '1000'
    answer = answer.split(" ")[0]
    return str(answer.strip())


def attempt(
    question: str, correct_answer: str, params: Optional[Dict[str, Any]] = None
) -> Tuple[bool, str]:
    try:
        response = get_response(question, **(params or {}))
        if response is None:
            print_error(" NR ")
            return False, ""
        extracted_answer = extract_answer(response)
        is_correct = extracted_answer == correct_answer
        return is_correct, response
    except Exception:
        print_error(" SE ")
        return False, ""


# ________________________ OpenAI client ________________________

load_dotenv(override=True)


def env(varname: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(varname) or default


if env("AZURE_OPENAI_ENDPOINT"):
    client: Union[openai.OpenAI, openai.AzureOpenAI] = openai.AzureOpenAI()
else:
    client = openai.OpenAI()

model: str = env("OPENAI_MODEL", "")  # type: ignore
if not model:
    raise Exception("OPENAI_MODEL environment variable not set")


def message(content: str, role: str) -> Dict[str, str]:
    return {"role": role, "content": content}


def user_message(content: str) -> Dict[str, str]:
    return message(content, "user")


def system_message(content: str) -> Dict[str, str]:
    return message(content, "system")


def bot_message(content: str) -> Dict[str, str]:
    return message(content, "assistant")


def get_response(
    messages: Union[str, List[Dict[str, str]]], attempt: Optional[int] = None, **kwargs: Any
) -> Optional[str]:
    """Get response from OpenAI API with automatic caching."""

    # Generate cache key
    kwargs["model"] = model  # Ensure model is part of the cache key
    cache_key = get_cache_key(messages, **kwargs)
    if attempt:  # attempt 0 doesn't need to be mentioned
        cache_key += f"_attempt{attempt}"
    if not os.getenv("IGNORE_CACHE"):
        cached_response = get_cached_response(cache_key)
        if cached_response is not None:
            return cached_response

    # Make API call if not cached
    if isinstance(messages, str):
        messages = [user_message(messages)]

    response_text = None
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                messages=messages,  # type: ignore
                **kwargs,  # More arguments like seed, temperature, etc.
            )
            response_text = response.choices[0].message.content
            if not response_text:
                raise Exception("Empty response")
            break
        except openai.RateLimitError:
            print_error(" RL ")
            time.sleep(30)  # Wait before retrying
            if attempt < 2:
                continue
            response_text = None
        except Exception as e:
            print_error(" Err ")
            print("get_response: Error:", e)
            response_text = None
    if not response_text:
        return None
    save_cached_response(cache_key, response_text, **kwargs)
    return response_text
