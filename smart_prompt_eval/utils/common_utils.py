import os
import time
from typing import Optional

from dotenv import load_dotenv
import openai
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

from smart_prompt_eval.utils.response_cacher import get_cache_key, get_cached_response, save_cached_response



def log(text="", filename="output.txt", *args, **kwargs):
    print(text, *args, **kwargs)
    # with open(filename, "a") as f:
    #     print(text, *args, **kwargs, file=f)


def print_progress(chr="."):
    print(chr, end="", flush=True)


def print_error(chr=" E "):
    print_progress(chr)


def remove_spaces_after_commas(text):
    # remove spaces after commas, but not before commas
    return ",".join([part.strip() for part in text.split(",")])


# backtick = "`"
# backticks = "```"
# data_format = "csv"

# def extract_data(response):
#     if backticks not in response:
#         # Replace single backtick with triple backticks
#         if backtick in response:
#             response = response.replace(backtick, backticks)
#         else:
#             raise Exception("No backticks found in the response")

#     last = response.rfind(backticks)
#     last_2 = response.rfind(backticks, 0, last) + len(backticks)
#     response = response[last_2:last].strip()

#     response = response.strip().strip(backtick).strip()
#     if response.startswith(data_format):
#         response = response[len(data_format) :] if data_format else response

#     response = remove_spaces_after_commas(response)
#     # strip every line
#     response = "\n".join([line.strip() for line in response.split("\n")])
#     return response


def extract_answer(answer):
    if not answer:
        return ""
    # Create a copy to avoid modifying the original
    answer = str(answer)
    # In GSM8K, answer exists after the last #### in the last part.
    # The same function is used for both old-RAT and iRAT.
    answer = answer.split("####")[-1].split("\n")[0].strip()

    # Clean the answer to get only numbers.
    answer = answer.lstrip("$").lstrip("€").strip()  # Remove currency symbols
    answer = (
        answer.rstrip("%").rstrip(".00").strip()
    )  # Remove percentage and trailing zeros
    answer = answer.replace(",", "")  # Remove commas. Example: $1,000.00 -> 1000
    # Select first word by excluding units such as 'years', 'feet', etc. Example: '1000 feet' -> '1000'
    answer = answer.split(" ")[0]
    return answer.strip()


def attempt(question, correct_answer, params: Optional[dict] = None) -> tuple[bool, str]:
    # with open("response.log", "a") as f:
    #     print("Q:", question, file=f)
    try:
        response = get_response(question, **(params or {}))
        # with open("response.log", "a") as f:
        #     print("A:", response, file=f)
        if response is None:
            print_error(" NR ")
            return False, ""
        extracted_answer = extract_answer(response)
        # print_progress(response)  # type: ignore
        is_correct = extracted_answer == correct_answer
        # if is_correct:
        #     print_progress()
        # else:
        #     print_error()
        return is_correct, response
    except Exception as e:
        print_error(" SE ")
        return False, ""


# def get_accuracy(question, correct_answer, params: Optional[dict] = None) -> bool:
#     total_attempts = 1  # 10
#     # correct_attempts = 0
#     with open("response.log", "a") as f:
#         print("Q:", question, file=f)
#     for i in range(total_attempts):
#         try:
#             response = get_response(question, **(params or {}))
#             with open("response.log", "a") as f:
#                 print("A:", response, file=f)
#             response = extract_answer(response)
#             # response = extract_data(response)
#             # break
#         except Exception as e:
#             print_error(" SE ")
#             continue
#         print_progress(response)  # type: ignore
#         if response == correct_answer:
#             print_progress()
#             # correct_attempts += 1
#             return True
#         else:
#             print_error()
#     return False
#     # accuracy = (100 * correct_attempts) / total_attempts
#     # accuracy = f"{accuracy:.2f}%"
#     # print()
#     # return accuracy


# def attempt_question(correct_answer, question, key=None, params: Optional[dict] = None):
#     print(f"Attempting for: {key}")
#     accuracy = get_accuracy(question, correct_answer, params)
#     if key is None:
#         key = str(params)
#     log(f"{key}: {accuracy}")


# ________________________ OpenAI client ________________________

load_dotenv(override=True)

def env(varname: str, default: Optional[str] = None) -> str | None:
    return os.getenv(varname) or default


if env("AZURE_OPENAI_ENDPOINT"):
    client = openai.AzureOpenAI()
else:
    client = openai.OpenAI()

model: str = env("OPENAI_MODEL", "") # type: ignore
if not model:
    raise Exception("OPENAI_MODEL environment variable not set")


def message(content: str, role: str) -> ChatCompletionMessageParam:
    return {"role": role, "content": content}  # type: ignore


def user_message(content: str) -> ChatCompletionMessageParam:
    return message(content, "user")


def system_message(content: str) -> ChatCompletionMessageParam:
    return message(content, "system")


def bot_message(content: str) -> ChatCompletionMessageParam:
    return message(content, "assistant")


def get_response(
    messages: str | list[ChatCompletionMessageParam],
    attempt: Optional[int] = None,
    **kwargs
) -> str | None:
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
                messages=messages,
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
