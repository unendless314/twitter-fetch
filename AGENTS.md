# AGENTS.md - Twitter Fetch Project Guide

> This file provides essential information for AI coding agents working on this project.
> For human contributors, see README.md.

---

## Project Overview

**Twitter Fetch** is a two-phase data pipeline for collecting and analyzing Twitter/X content:

1. **Fetch Phase**: Uses xAI Grok API with X Search capability to collect tweets based on configured topics
2. **Analyze Phase**: Uses free LLM CLI tools (Gemini/Qwen) to analyze collected content and identify high-engagement opportunities

The project is designed with a "simple, practical, no over-engineering" philosophy. All configurations are YAML-based, outputs are Markdown with YAML frontmatter, and the codebase is minimal (~500 lines total).

### Language

Project documentation, code comments, and variable names use **Traditional Chinese (zh-TW)** as the primary language.

---

## Technology Stack

- **Runtime**: Python 3.12+
- **Dependencies** (see `requirements.txt`):
  - `xai-sdk` - xAI Grok API client
  - `pyyaml` - YAML parsing
  - `python-dotenv` - Environment variable management
- **External CLI Tools** (must be installed separately):
  - `gemini` - Google Gemini CLI
  - `qwen` - Alibaba Qwen CLI
- **Virtual Environment**: `.venv/` (required for execution)

### Environment Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and set XAI_API_KEY
```

---

## Project Structure

```
twitter-fetch/
├── fetch.py                  # Fetch phase entry point
├── analyze.py                # Analysis phase entry point
├── prompt_factory.py         # Config → Prompt generator
├── entrypoint.sh             # Cron job entrypoint
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (gitignored)
│
├── configs/
│   ├── fetch/                # Fetch topic configurations
│   │   ├── ai_news_keyword.yaml
│   │   ├── ai_news_semantic.yaml
│   │   ├── crypto_*.yaml
│   │   └── ...
│   └── agent.yaml            # Agent analysis configuration
│
├── prompts/
│   ├── fetch/                # Generated search prompts (from configs)
│   │   ├── ai_news_keyword.md
│   │   └── ...
│   └── agent/                # Agent analysis prompt templates
│       ├── traffic_catalyst_agent.md
│       └── deep_research_scout_agent.md
│
├── data/
│   ├── raw/                  # Fetch output: raw tweet data
│   │   ├── ai_news_keyword/
│   │   │   ├── 20260225_070042.md
│   │   │   └── ...
│   │   └── ...
│   └── refined/              # Analyze output: analysis results
│       └── traffic_catalyst/
│           └── 20260226_002022_ai_news_keyword.md
│
├── logs/                     # Execution logs
├── temp/                     # Temporary files (debug prompts)
└── docs/                     # Design documentation
```

---

## Key Concepts & Conventions

### Topic ID Convention

- **Topic ID** = filename without extension
- `configs/fetch/ai_news_keyword.yaml` → topic_id = `ai_news_keyword`
- Prompt files, output directories all use the same topic_id

### Timestamp Format

- All timestamps use format: `YYYYMMDD_HHMMSS`
- Timezone: `Asia/Taipei` (UTC+8)
- Example: `20260225_070042` = Feb 25, 2026, 07:00:42

### Output File Format

All output files are Markdown with YAML frontmatter:

```markdown
---
topic: "ai_news_keyword"
executed_at: "2026-02-25T07:00:42+08:00"
status: "success"
---

[Content body...]
```

### Search Strategies

Three search strategies are supported in configs:

1. **keyword** - X Advanced Search operators (recommended, most reliable)
2. **semantic** - Natural language description
3. **hybrid** - Combination of both

See `docs/SEARCH_STRATEGY_ANALYSIS.md` for detailed comparison.

---

## Core Modules

### 1. fetch.py - Fetch Pipeline

Executes Grok API calls to collect tweets.

**Key Configuration** (in file):
- `MODEL = "grok-4-1-fast-reasoning"` - Grok model
- `MAX_RETRIES = 3` - API retry limit
- `RETRY_DELAYS = [2, 4, 8]` - Exponential backoff

**CLI Usage**:
```bash
# Run all prompts
python3 fetch.py

# Run specific topic(s)
python3 fetch.py --prompt ai_news_keyword
python3 fetch.py --prompt ai_news_keyword,crypto_defi_native_keyword

# Dry run (preview only)
python3 fetch.py --dry-run
```

**Dynamic Date Injection**:
The script reads `lookback_days` from config and injects `since:{date}` at runtime.

### 2. analyze.py - Analysis Pipeline

Analyzes collected data using LLM CLI tools.

**CLI Usage**:
```bash
# Basic usage
python3 analyze.py --agent traffic_catalyst --topics ai_news_keyword

# Multiple topics (cross-topic aggregation)
python3 analyze.py --agent traffic_catalyst --topics ai_news_keyword,ai_news_semantic

# Dry run (preview assembled prompt)
python3 analyze.py --agent traffic_catalyst --topics ai_news_keyword --dry-run
```

**Provider Support**:
- `gemini` - Google Gemini CLI
- `qwen` - Alibaba Qwen CLI

### 3. prompt_factory.py - Config to Prompt Generator

Converts YAML configs to Markdown prompts.

**CLI Usage**:
```bash
# Generate from config ID
python3 prompt_factory.py --config ai_news_keyword

# Dry run (preview only)
python3 prompt_factory.py --config ai_news_keyword --dry-run

# Custom output path
python3 prompt_factory.py --config ai_news_keyword --output custom/path.md
```

---

## Configuration Schema

### Fetch Config (`configs/fetch/{topic_id}.yaml`)

```yaml
id: "ai_news_keyword"           # Topic identifier

search:
  tool: "keyword"               # keyword | semantic | hybrid
  mode: "Latest"                # Latest | Top
  limit: 10                     # Number of tweets to fetch
  lookback_days: 5              # Search window (injected as since: date)
  
  query: |                      # Search query
    (artificial intelligence OR AI)
    (breakthrough OR release)
  
  conditions:                   # Filtering conditions
    min_faves: 100              # Minimum likes
    filter: "-replies"          # Exclude: -replies | -images | -videos
                                # Include: images | videos | news | links
    lang: "en OR lang:zh"       # Language filter
    from_accounts:              # Optional: limit to specific accounts
      - OpenAI
      - AnthropicAI

filter:
  include: "官方公告、技術論文..."  # Content to prioritize
  exclude: "價格炒作、加密貨幣..."    # Content to exclude

output:
  format: |                     # Expected output format (shown to Grok)
    請以結構化 JSON 格式返回...
```

### Agent Config (`configs/agent.yaml`)

```yaml
default_provider: "qwen"        # Default LLM provider

default_models:
  gemini: "gemini-2.5-pro"      # Gemini model name
  qwen: "qwen-coder"            # Qwen model name
```

---

## Development Workflow

### Adding a New Topic

1. Create config: `configs/fetch/my_topic.yaml`
2. Generate prompt: `python3 prompt_factory.py --config my_topic`
3. Review/edit: `vim prompts/fetch/my_topic.md` (if needed)
4. Test run: `python3 fetch.py --prompt my_topic`

### Adding a New Agent

1. Create prompt template: `prompts/agent/my_agent.md`
2. Test: `python3 analyze.py --agent my_agent --topics ai_news_keyword --dry-run`
3. Execute: `python3 analyze.py --agent my_agent --topics ai_news_keyword`

### Cron/Scheduled Execution

Use `entrypoint.sh` for scheduled execution:

```bash
# Add to crontab for daily execution at 7:00 AM
0 7 * * * /home/openclaw/Projects/twitter-fetch/entrypoint.sh
```

---

## Testing & Debugging

### Dry Run Mode

All scripts support `--dry-run` to preview without execution:

```bash
python3 prompt_factory.py --config ai_news_keyword --dry-run
python3 fetch.py --prompt ai_news_keyword --dry-run
python3 analyze.py --agent traffic_catalyst --topics ai_news_keyword --dry-run
```

### Debug Files

- `temp/analyze/` - Assembled prompts for analysis (with timestamps)
- `logs/cron.log` - Cron execution logs

### Validation

- `fetch.py` validates XAI_API_KEY on startup
- `analyze.py` validates agent.yaml config on startup
- `prompt_factory.py` validates required config fields

---

## Security Considerations

1. **API Keys**: Store in `.env` file only (gitignored)
   - XAI_API_KEY for Grok API
   - No keys stored in code or configs

2. **Output Data**: 
   - Raw tweet data may contain PII
   - Data stored in `data/` directory (not gitignored by default)
   - Consider adding `data/` to `.gitignore` for privacy

3. **External CLI Tools**:
   - Gemini/Qwen CLI must be installed separately
   - These tools may send data to external APIs
   - Review their privacy policies for sensitive content

---

## Common Issues

### Missing Virtual Environment

**Error**: `ModuleNotFoundError: No module named 'xai_sdk'`
**Fix**: Run `source .venv/bin/activate` before executing scripts

### Missing API Key

**Error**: `[fetch.py] ❌ 未找到 XAI_API_KEY...`
**Fix**: Ensure `.env` file exists with valid XAI_API_KEY

### Missing Config

**Error**: `[analyze.py] ❌ 找不到配置檔：configs/agent.yaml`
**Fix**: Create `configs/agent.yaml` with required fields

---

## File Organization Rules

When modifying code, maintain these organizational principles:

1. **One topic = one config + one prompt** - Keep IDs consistent
2. **Timestamps in filenames** - Never overwrite existing data
3. **YAML frontmatter** - All outputs must have metadata headers
4. **Chinese comments** - Code comments should be in Traditional Chinese
5. **Simple error handling** - Use `print()` + `sys.exit(1)` for fatal errors

---

## Reference Documentation

- `README.md` - User-facing documentation (in Chinese)
- `docs/DESIGN_MVP.md` - Original MVP design decisions
- `docs/SEARCH_STRATEGY_ANALYSIS.md` - Search strategy comparison
- `docs/agent_analysis_simple_spec.md` - Analysis pipeline design spec
