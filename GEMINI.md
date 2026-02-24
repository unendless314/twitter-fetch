# GEMINI.md - Twitter Fetch Project Context

This file provides the necessary context for Gemini to understand and work with the `twitter-fetch` project.

## Project Overview

`twitter-fetch` is a Python-based automation tool that leverages the **xAI Grok API** (specifically the **X Search tool**) to collect tweets from X (Twitter). It follows a structured workflow: **Config (YAML) → Prompt (Markdown) → Output (Markdown)**.

- **Purpose**: Automate the collection of niche-specific tweets (e.g., AI news, Crypto trends) with high precision using Grok's reasoning and search capabilities.
- **Main Technologies**: Python 3.12+, `xai-sdk`, `pyyaml`, `python-dotenv`.
- **Primary Model**: `grok-4-1-fast-reasoning`.
- **Timezone**: `Asia/Taipei`.

## Project Structure

- `configs/`: YAML files defining search topics, queries, filters, and output formats.
- `prompts/`: Markdown prompts generated from configs (or manually refined).
- `outputs/`: API responses organized by `topic_id`, stored in timestamped `.md` files.
- `logs/`: Execution logs (standard output is also used for progress).
- `docs/`: Design documents and API research.
- `prompt_factory.py`: Utility to convert `configs/*.yaml` to `prompts/*.md`.
- `run.py`: Main script to execute prompts and save results.

## Building and Running

### Prerequisites
- Python 3.12+
- xAI API Key (configured in `.env`)

### Commands
- **Environment Setup**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  cp .env.example .env # Then edit .env
  ```
- **Generate Prompts**:
  ```bash
  # Generate from configs/ai_news.yaml to prompts/ai_news.md
  python3 prompt_factory.py --config ai_news
  ```
- **Run Collection**:
  ```bash
  # Run all prompts in prompts/
  python3 run.py
  
  # Run specific topic
  python3 run.py --prompt ai_news
  
  # Preview without API calls
  python3 run.py --dry-run
  ```

## Development Conventions

- **Topic IDs**: Use `snake_case` (e.g., `crypto_defi_native`).
- **File Naming**:
  - Config: `configs/{topic_id}.yaml`
  - Prompt: `prompts/{topic_id}.md`
  - Output: `outputs/{topic_id}/{YYYYMMDD_HHMMSS}.md`
- **Coding Style**:
  - Use `pathlib.Path` for file system operations.
  - Use type hints for function signatures.
  - Traditional Chinese is used for comments and documentation (maintain this consistency).
- **Error Handling**: `run.py` implements exponential backoff retries (3 attempts).
- **Dynamic Prompts**: `run.py` automatically injects a `since:YYYY-MM-DD` filter into the prompt based on the `lookback_days` specified in the config.

## Adding a New Topic
1. Create `configs/my_topic.yaml`.
2. Run `python3 prompt_factory.py --config my_topic`.
3. (Optional) Refine `prompts/my_topic.md`.
4. Run `python3 run.py --prompt my_topic`.
