# Smart-Prompt-Eval

This repository contains a collection of prompt engineering techniques to test robustness of various non-reasoning models based on vulnerabilities revealed in the papers of the past few years. The techniques are organized into different experiments, each focusing on a specific aspect of model behavior.

## Available Experiments

- **Direct GSM8K Evaluation**: Testing model performance on grade school math problems
- **Language Errors**: Testing model performance by manipulating queries to add various grammatical and spelling errors
- **Multilingual Prompting**: Testing model performance by translating queries into different languages
- **Multiple Roles**: Testing with multiple roles (user, assistant, and system)
- **Seed Consistency**: Testing with multiple seed values to check output consistency

## Shared Utilities

The `evals/eval_utils.py` file contains shared functions used across all evaluation scripts to reduce code duplication:

- `load_gsm8k_questions()`: Load questions from the centralized GSM8K dataset
- `save_evaluation_results()`: Save results to JSON files
- `log_evaluation_start/end()`: Standardized logging for evaluations
- `extract_final_answer()`: Extract final answers from GSM8K format
- `create_base_prompt()`: Create standardized prompts
- `initialize_evaluation_results()`: Initialize result dictionaries

## Setup

1. Clone the repository and open the directory:
   ```bash
   git clone https://github.com/Pro-GenAI/Hack-Prompting-Eval.git
   cd Hack-Prompting-Eval
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

5. Run the evaluation:
   ```bash
   python evaluate.py
   ```

## Usage

### Running All Evaluations
```bash
python evaluate.py
```

### Running Individual Evaluations
```bash
# Run specific evaluation
python evals/gsm8k_eval.py
python evals/seed_consistency_eval.py

# Run all dataset evaluations
python evals/run_evaluations.py
```

## Quick run notes

- If you run scripts directly (for example `python smart_prompt_eval/scripts/translate_gsm8k.py`) you may see import errors because Python doesn't treat the repository root as an installed package. Two easy options:
  1. Install the project in editable mode so the `smart_prompt_eval` package is importable:

     ```bash
     python -m pip install -e .
     ```

  2. Run scripts as modules which preserves package imports:

     ```bash
     python -m smart_prompt_eval.scripts.translate_gsm8k --help
     ```

Both approaches allow `from smart_prompt_eval...` imports to work from the repository root.

## Base projects with published papers

- Does Seed Matter - https://github.com/Pro-GenAI/PromptSeed
- Linguistic Errors - https://github.com/Pro-GenAI/PromptSpell
- Multilingual Prompting - https://github.com/Pro-GenAI/PromptLang
- Power of Roles - https://github.com/Pro-GenAI/Power-of-Roles
