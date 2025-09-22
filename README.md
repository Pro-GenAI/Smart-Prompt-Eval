# Smart-Prompt-Eval
<!-- Robust-Prompt-Eval -->

This repository contains a collection of prompt engineering techniques to test robustness of various non-reasoning models based on vulnerabilities revealed in the papers of the past few years. The techniques are organized into different experiments, each focusing on a specific aspect of model behavior.

## Available Experiments

- **Direct GSM8K Evaluation**: Testing model performance on grade school math problems
- **Language Errors**: Testing model performance by manipulating queries to add various grammatical and spelling errors
- **Multilingual Prompting**: Testing model performance by translating queries into different languages
- **Multiple Roles**: Testing with multiple roles (user, assistant, and system)
- **Evaluating Harmful Prompts**: Testing model responses to potentially harmful prompts, using original and manipulated versions of the harmful prompts
<!-- - **Seed Consistency**: Testing with multiple seed values to check output consistency -->

## Setup

1. Clone the repository and open the directory:
   ```bash
   git clone https://github.com/Pro-GenAI/Smart-Prompting-Eval.git
   cd Smart-Prompting-Eval
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up .env file:
    - Create a `.env` file in the root directory using .env.example as a template:
     ```bash
     cp .env.example .env
     ```
    - Edit the `.env` file to access an OpenAI-compatible API of your model.
        - Example: OpenAI API, vLLM, Ollama, etc.

4. Install the package:
   ```bash
   pip install -e .
   ```

## Usage

### Running All Evaluations
```bash
python smart_prompt_eval/run_eval.py
```

### Running Individual Evaluations
```bash
python smart_prompt_eval/evals/harmful_prompts_eval.py
python smart_prompt_eval/run_eval.py harmful_prompts_eval
```

### Base papers with code

- Does Seed Matter - https://github.com/Pro-GenAI/PromptSeed
- Linguistic Errors - https://github.com/Pro-GenAI/PromptSpell
- Multilingual Prompting - https://github.com/Pro-GenAI/PromptLang
- The Power of Roles - https://github.com/Pro-GenAI/Power-of-Roles
