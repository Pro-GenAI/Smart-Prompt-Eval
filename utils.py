from typing import Optional
from dotenv import load_dotenv
from IPython.display import display, Markdown
import openai
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

# from openai.types.chat.chat_completion_user_message_param import ChatCompletionUserMessageParam

import os


backtick = "`"
backticks = "```"
data_format = "csv"


def log(text="", filename="output.txt"):
    print(text)
    with open(filename, "a") as f:
        print(text, file=f)


def print_progress(chr="."):
    print(chr, end="", flush=True)


def print_error(chr=" E "):
    print_progress(chr)


def display_md(md: str | None):
    if md:
        display(Markdown(md))


def remove_spaces_after_commas(text):
    # remove spaces after commas, but not before commas
    return ",".join([part.strip() for part in text.split(",")])


def extract_data(response):
    if backticks not in response:
        # Replace single backtick with triple backticks
        if backtick in response:
            response = response.replace(backtick, backticks)
        else:
            raise Exception("No backticks found in the response")

    last = response.rfind(backticks)
    last_2 = response.rfind(backticks, 0, last) + len(backticks)
    response = response[last_2:last].strip()

    response = response.strip().strip(backtick).strip()
    if response.startswith(data_format):
        response = response[len(data_format) :] if data_format else response

    response = remove_spaces_after_commas(response)
    # strip every line
    response = "\n".join([line.strip() for line in response.split("\n")])
    return response


def get_accuracy(question, correct_answer, params: Optional[dict] = None):
    total_attempts = 10
    correct_attempts = 0
    with open('response.log', 'a') as f:
        print("Q:", question, file=f)
    for i in range(total_attempts):
        try:
            response = get_response(question, **(params or {}))
            with open('response.log', 'a') as f:
                print("A:", response, file=f)
            response = extract_data(response)
            # break
        except Exception as e:
            print_error(" SE ")
            continue
        print_progress(response) # type: ignore
        if response == correct_answer:
            print_progress()
            correct_attempts += 1
        else:
            print_error()
    accuracy = (100 * correct_attempts) / total_attempts
    accuracy = f"{accuracy:.2f}%"
    print()
    return accuracy


def attempt_question(correct_answer, question, key=None, params: Optional[dict] = None):
    print(f"Attempting for: {key}")
    accuracy = get_accuracy(question, correct_answer, params)
    if key is None:
        key = str(params)
    log(f"{key}: {accuracy}")


# ________________________ OpenAI client ________________________

load_dotenv(override=True)

client = openai.OpenAI()
model = os.getenv("OPENAI_MODEL", "")
if not model:
    raise ValueError("OPENAI_MODEL environment variable not set")


def message(content: str, role: str) -> ChatCompletionMessageParam:
    return {"role": role, "content": content}  # type: ignore


def user_message(content: str) -> ChatCompletionMessageParam:
    return message(content, "user")


def system_message(content: str) -> ChatCompletionMessageParam:
    return message(content, "system")


def bot_message(content: str) -> ChatCompletionMessageParam:
    return message(content, "assistant")


def get_response(
    messages: str | list[ChatCompletionMessageParam], **kwargs
) -> str | None:
    if isinstance(messages, str):
        messages = [user_message(messages)]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        **kwargs,  # More arguments like seed, temperature, etc.
    )
    return response.choices[0].message.content


log("\n-----------")
log("Model: " + model)
