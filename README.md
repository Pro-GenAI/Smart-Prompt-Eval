<img src="assets/Project_logo.jpg" alt="Project logo" height="200px" align="left"/>

# _Smart-Prompt-Eval_: Evaluating LLM Robustness using Manipulated Prompts

<!-- Tags -->
[![AI](https://img.shields.io/badge/AI-C21B00?style=for-the-badge&logo=openaigym&logoColor=white)]()
[![LLMs](https://img.shields.io/badge/LLMs-1A535C?style=for-the-badge&logo=openai&logoColor=white)]()
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=ffdd54)]()
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-darkgreen?style=for-the-badge&logo=github&logoColor=white)](./LICENSE.md)

## Introduction
Smart-Prompt-Eval is a framework for stress-testing LLMs under different prompt manipulations, making it easy to benchmark robustness across tasks.
Are Large Language Models (LLMs) robust yet? LLMs are powerful, but their robustness is still an open question.
Smart-Prompt-Eval evaluates LLM robustness using multiple **prompt manipulation techniques** inspired by vulnerabilities identified in prior research. Each experiment highlights a different aspect of robustness.

## Sample Manipulations

#### Language Error Demo:
<img src="assets/Lang_Error_Demo.jpg" alt="Language Error Demo" height="300px"/>

#### Harmful Prompt Demo:
<img src="assets/Harm_Prompt_Demo.jpg" alt="Harmful Prompt Demo" height="250px"/>

## Available Experiments

- **Language Errors**: Testing model performance by manipulating queries to add various grammatical and spelling errors
- **Multilingual Prompting**: Testing model performance by translating queries into different languages
- **Multiple Roles**: Testing with multiple roles (user, assistant, and system)
- **Evaluating Harmful Prompts**: Testing model responses to potentially harmful prompts, using original and manipulated versions of the harmful prompts
<!-- - **Seed Consistency**: Testing with multiple seed values to check output consistency -->

## Setup

1. Clone the repository and open the directory:
   ```bash
   git clone https://github.com/Pro-GenAI/Smart-Prompt-Eval.git
   cd Smart-Prompt-Eval
   ```

2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

3. (Optional) Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Set up .env file:
    - Create a `.env` file in the root directory using .env.example as a template:
     ```bash
     cp .env.example .env
     ```
    - Edit the `.env` file to access an OpenAI-compatible API of your model.
        - Example: OpenAI API, Azure OpenAI, vLLM, Ollama, etc.

## Usage

### Running All Evaluations
```bash
python smart_prompt_eval/run_eval.py
```

### Running Individual Evaluations
```bash
python smart_prompt_eval/evals/harmful_eval.py
python smart_prompt_eval/run_eval.py harmful_eval linguistic_errors_eval
```

## Development

### Code Quality
This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

Run all quality checks:
```bash
black smart_prompt_eval tests
isort smart_prompt_eval tests
flake8
mypy
```
<!-- 
To test whether it builds without errors:
```bash
python -m build
```
-->

### Testing
Run the test suite:
```bash
pytest -q
```

### Citation
If you find this repository useful in your research, please consider citing:
```bibtex
@misc{vadlapati2025smartprompteval,
  author       = {Vadlapati, Praneeth},
  title        = {Smart-Prompt-Eval: Evaluating LLM Robustness with Manipulated Prompts},
  year         = {2025},
  howpublished = {\url{https://github.com/Pro-GenAI/Smart-Prompt-Eval}},
  note         = {GitHub repository},
}
```

## Created based on my past papers and code

- [Linguistic Errors](https://github.com/Pro-GenAI/PromptSpell) - Experiments on grammatical and spelling errors in prompts.
- [Multilingual Prompting](https://github.com/Pro-GenAI/PromptLang) - Experiments on prompting LLMs in multiple languages.
- [The Power of Roles](https://github.com/Pro-GenAI/Power-of-Roles) - Experiments on the impact of different roles in prompting.
<!-- - [Does Seed Matter](https://github.com/Pro-GenAI/PromptSeed) - Experiments on randomness and seed impact on LLM outputs. -->

## Datasets supported: (More can be added in future)

- **GSM8K (Grade School Math 8K)**: This repository includes a copy of the GSM8K test file for convenience (see `smart_prompt_eval/datasets/gsm8k_test.jsonl` and localized variants). [GSM8K](https://github.com/openai/grade-school-math) is a collection of grade-school math word problems used to evaluate numerical reasoning. The original dataset and citation are available at the project's repository. Please cite the original dataset authors and consult the original repository for license and citation details.

## :email: Contact
For personal queries, please find the author's contact details here: https://prane-eth.github.io/

Image credits:
- User icon: https://www.flaticon.com/free-icon/user_9131478
- Robot icon: https://www.flaticon.com/free-icon/robot_18355220
