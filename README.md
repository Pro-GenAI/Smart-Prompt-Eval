# Hack-Prompting

This repository contains a collection of prompt engineering techniques to test robustness of various non-reasoning models based on vulnerabilities revealed in the papers of the past few years. The techniques are organized into different experiments, each focusing on a specific aspect of model behavior.

## Project Structure

```
Hack-Prompting/
├── evaluate.py                 # Main evaluation runner
├── utils.py                    # Core utilities (OpenAI client, logging, etc.)
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (API keys, model config)
├── evals/                      # Evaluation scripts directory
│   ├── eval_utils.py          # Shared utilities for evaluations
│   ├── gsm8k_test.jsonl       # GSM8K test dataset
│   ├── gsm8k_eval.py          # GSM8K evaluation
│   ├── math_eval.py           # MATH dataset evaluation
│   ├── seed_consistency_eval.py    # Seed consistency testing
│   ├── linguistic_errors_eval.py   # Linguistic errors testing
│   ├── multilingual_prompting_eval.py  # Multilingual testing
│   ├── power_of_roles_eval.py       # Role-based testing
│   ├── run_evaluations.py      # Runner for all evals
│   └── README.md              # Evaluation documentation
├── experiments/               # Prompt engineering experiments
│   ├── Linguistic_Errors.py
│   ├── Multilingual_Prompting.py
│   ├── Power_of_Roles.py
│   └── Does_Seed_Matter.py
└── README.md
```

## Available Experiments

- **GSM8K Evaluation**: Testing model performance on grade school math problems
- **MATH Evaluation**: Testing model performance on MATH dataset problems
- **Language Errors**: Testing model performance with various grammatical and spelling errors
- **Multilingual Prompting**: Testing model performance across different languages
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

4. Run the evaluation:
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

## Output

- **Experiment Results**: Saved to `output.txt` in the root directory
- **Dataset Evaluation Results**: Saved as JSON files in the `evals/` directory
  - `gsm8k_results.json`
  - `math_results.json`
  - `seed_consistency_results.json`
  - `linguistic_errors_results.json`
  - `multilingual_prompting_results.json`
  - `power_of_roles_results.json`

## Configuration

Make sure your `.env` file is properly configured with:
- `OPENAI_API_KEY`: Your API key
- `OPENAI_BASE_URL`: API endpoint (e.g., Groq, OpenAI)
- `OPENAI_MODEL`: Model to evaluate

## Adding New Evaluations

To add a new evaluation:
1. Create a new `*_eval.py` file in the `evals/` directory
2. Import shared utilities from `eval_utils.py`
3. Load questions using `load_gsm8k_questions()`
4. Implement the evaluation logic
5. Save results using `save_evaluation_results()`
6. The `run_evaluations.py` will automatically pick it up
