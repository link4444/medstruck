# Contributing to MedStruct AI

First off, thank you for considering contributing to MedStruct AI! This project is built as an offline-first, privacy-preserving medical AI dashboard.

## Getting Started

1. **Fork the repository** and clone it locally.
2. Ensure you have **Python 3.10+** installed.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pre-commit
   ```
4. Install pre-commit hooks to automatically format code before you commit:
   ```bash
   pre-commit install
   ```

## Development Workflow

1. Create a new branch (`git checkout -b feature/your-feature-name`).
2. Make your changes in the `medstruct_ai` directory.
3. Run the test suite and linters locally before pushing:
   - `black .`
   - `ruff check .`
   - `mypy medstruct_ai/`
4. Commit your changes using **Semantic Commit Messages** (e.g., `feat: added new chart`, `fix: resolved import bug`).
5. Push your branch and open a Merge Request on GitLab.

## Code Style

- We use **Black** for code formatting.
- We use **Ruff** for linting.
- We use **MyPy** for static type checking.
- The CI pipeline will automatically run these checks, so utilizing `pre-commit` locally is highly recommended to save time.

## Local AI Testing

If you are modifying the `medstruct_ai.core.vision` or `audio` modules, you must have Ollama running locally (`ollama serve`) with the `qwen3-vl:8b` and `medstruct-qwen` models downloaded to verify your changes.
