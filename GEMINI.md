# Twitter Fetch & Analyze

This project is an automated pipeline for collecting Twitter/X data using xAI's Grok (X Search) and analyzing it for high-impact content using Gemini or Qwen agents.

## Project Overview

- **Purpose**: Automate the discovery of trending or high-potential content on Twitter/X across various domains (AI, Crypto, Macro, etc.).
- **Philosophy**: Simple, practical, no over-engineering. YAML-based configuration and Markdown-based outputs.
- **Primary Language**: Documentation and code comments use **Traditional Chinese (zh-TW)**.
- **Architecture**: 
  - **Phase 1 (Fetch)**: Uses YAML configurations to generate prompts for xAI Grok, executes search, and stores raw data.
  - **Phase 2 (Analyze)**: Aggregates raw data and uses LLM agents (via Gemini/Qwen CLI) to identify "traffic catalysts".

## Project Structure

- `run.py`: Executes the fetching phase using `xai-sdk`. Model: `grok-4-1-fast-reasoning`.
- `analyze.py`: Executes the analysis phase using `gemini` or `qwen` CLIs.
- `prompt_factory.py`: Generates Markdown prompts from YAML configurations.
- `configs/`:
  - `fetch/`: YAML files defining search queries. Filename is the **Topic ID**.
  - `agent.yaml`: Analysis configuration (provider/model selection).
- `data/`:
  - `raw/{topic_id}/`: Raw responses from Grok.
  - `refined/{agent_id}/`: Final analysis results.
- `prompts/`:
  - `fetch/`: Generated search prompts.
  - `agent/`: Prompt templates for agents.

## Key Conventions

- **Topic ID**: Filename without extension (e.g., `ai_news_keyword`). Used consistently across configs, prompts, and data dirs.
- **Timestamp Format**: `YYYYMMDD_HHMMSS` (Timezone: `Asia/Taipei`).
- **Output Format**: Markdown with YAML frontmatter.

## Setup and Installation

### 1. Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration
```bash
cp .env.example .env
# Edit .env and add XAI_API_KEY
```

### 3. External Tools
Ensure `gemini` and `qwen` CLI tools are installed and available in your PATH for the analysis phase.

## Usage

### Phase 1: Fetching Data
1. **Add/Edit Topic**: `configs/fetch/{topic_id}.yaml`
2. **Generate Prompt**: `python3 prompt_factory.py --config <topic_id>`
3. **Execute Fetch**: `python3 run.py --prompt <topic_id>`

### Phase 2: Analyzing Data
```bash
python3 analyze.py --agent traffic_catalyst --topics <topic_id1>,<topic_id2>
```

## Development Workflow

- **Dry Run**: All main scripts support `--dry-run` to preview actions without making API calls or writing results.
- **Adding Agents**: Create a new template in `prompts/agent/{agent_id}_agent.md`.
- **Scheduled Tasks**: Use `entrypoint.sh` for cron jobs.

## Testing & Validation
- Use `--dry-run` for all scripts to validate prompt assembly and configuration.
- Check `temp/analyze/` for debug prompts generated during the analysis phase.
