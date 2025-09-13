
from dotenv import load_dotenv
from IPython.display import display, Markdown
import openai
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
# from openai.types.chat.chat_completion_user_message_param import ChatCompletionUserMessageParam

import os

load_dotenv(override=True)
backtick = "`"
backticks = "```"


def log(text, filename="output.txt"):
    print(text)
    with open(filename, "a") as f:
        print(text, file=f)

def print_progress(chr="."):
    print(chr, end="", flush=True)

def print_error(chr="E "):
	print_progress(chr)

def display_md(md: str | None):
	if md:
		display(Markdown(md))

client = openai.OpenAI()
model = os.getenv("OPENAI_MODEL", "")
if not model:
    raise ValueError("OPENAI_MODEL environment variable not set")

def message(content: str, role: str) -> ChatCompletionMessageParam:
    return {"role": role, "content": content} # type: ignore

def user_message(content: str) -> ChatCompletionMessageParam:
	return message(content, "user")

def system_message(content: str) -> ChatCompletionMessageParam:
	return message(content, "system")

def bot_message(content: str) -> ChatCompletionMessageParam:
	return message(content, "assistant")


def get_response(messages: str | list[ChatCompletionMessageParam], **kwargs) -> str | None:
	if isinstance(messages, str):
		messages = [user_message(messages)]
	response = client.chat.completions.create(
		model=model,
		messages=messages,
		**kwargs  # More arguments like seed, temperature, etc.
	)
	return response.choices[0].message.content

