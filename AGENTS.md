# Twitter Fetch - AI Coding Agent Guide

## Project Overview

This is a Python-based automation tool that collects tweets from Twitter/X using xAI Grok's X Search capabilities. It allows users to define search topics via YAML configurations, generate optimized prompts, and execute automated data collection through the xAI API.

The project is designed with simplicity in mind - it follows a config → prompt → output workflow where each topic is independently configurable and results are stored with timestamps to preserve history.

## Technology Stack

- **Language**: Python 3.12+
- **Core Dependencies**:
  - `xai-sdk` - Official xAI SDK for Grok API access
  - `pyyaml` - YAML configuration parsing
  - `python-dotenv` - Environment variable management
- **Model**: `grok-4-1-fast-reasoning` (as defined in run.py)
- **API**: xAI Grok API with X Search tool

## Project Structure

```
twitter-fetch/
├── configs/                 # Topic configuration files (YAML)
│   ├── ai_breakthrough.yaml # Example: AI breakthrough tracking
│   └── ai_emerging.yaml     # Example: Emerging AI trends
├── prompts/                 # Generated prompt files (Markdown)
│   ├── ai_breakthrough.md
│   └── ai_emerging.md
├── outputs/                 # Collection results organized by topic
│   ├── ai_breakthrough/     # Timestamped result files
│   └── ai_emerging/
├── logs/                    # Execution logs (currently unused)
├── docs/                    # Documentation and research notes
│   ├── DESIGN_MVP.md        # MVP design decisions
│   ├── GROK_X_SEARCH_CAPABILITIES.md  # Grok search capabilities
│   └── XAI_OFFICIAL_API_DOC.md        # API documentation notes
├── prompt_factory.py        # Config → Prompt generator tool
├── run.py                   # Main execution script
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variable template
└── .gitignore              # Git ignore rules
```

## Configuration System

### Config File Format (configs/{topic_id}.yaml)

Each topic is defined by a YAML configuration with the following structure:

```yaml
# Required: Topic identifier (used for filenames and folders)
id: "topic_name"

# Required: Search strategy configuration
search:
  tool: "keyword"           # "keyword" (precise) or "semantic" (AI understanding)
  mode: "Latest"            # "Top" (popular) or "Latest" (chronological)
  limit: 15                 # Number of tweets to retrieve
  lookback_days: 7          # Search window (injected as since: date)
  
  query: |                  # Search query
    (artificial intelligence OR AI)
    (breakthrough OR release)
  
  conditions:               # Optional filtering conditions
    min_faves: 100          # Minimum likes threshold
    filter: "-replies"      # Exclude types (-replies, -images, -videos)
                            # Or include only: images, videos, news, links
    lang: "en OR lang:zh"   # Language filter
    from_accounts:          # Optional: limit to specific accounts
      - OpenAI
      - AnthropicAI

# Required: Content filtering instructions
filter:
  include: "What to prioritize"
  exclude: "What to avoid"

# Required: Output format specification
output:
  format: "Detailed output format instructions for Grok"
```

## Build and Run Commands

### Environment Setup

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment (required for every new terminal)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your XAI_API_KEY
```

### Generate Prompts from Configs

```bash
# Generate prompt from config (configs/{name}.yaml → prompts/{name}.md)
python3 prompt_factory.py --config topic_name

# Preview without writing to file
python3 prompt_factory.py --config topic_name --dry-run

# Custom output path
python3 prompt_factory.py --config ./custom.yaml --output ./custom.md
```

### Execute Data Collection

```bash
# Run all prompts
python3 run.py

# Run specific topic(s)
python3 run.py --prompt ai_breakthrough
python3 run.py --prompt ai_breakthrough,ai_emerging

# Dry run (preview without API calls)
python3 run.py --dry-run
```

## Output Format

Results are saved to `outputs/{topic_id}/{YYYYMMDD_HHMMSS}.md` with YAML frontmatter:

```markdown
---
topic: "ai_breakthrough"
executed_at: "2026-02-23T22:31:24+08:00"
status: "success"  # or "failed"
---

(Grok's raw response content)
```

## Code Organization

### Main Modules

1. **prompt_factory.py**: Configuration-to-prompt converter
   - Validates required config fields: `id`, `search`, `filter`, `output`
   - Generates structured Markdown prompts for Grok
   - Supports keyword and semantic search modes

2. **run.py**: Main execution engine
   - Discovers prompts from `prompts/` directory
   - Calls xAI API with retry logic (exponential backoff)
   - Injects dynamic date ranges based on `lookback_days`
   - Writes timestamped output files

### Key Constants (in run.py)

```python
MODEL = "grok-4-1-fast-reasoning"
MAX_RETRIES = 3
RETRY_DELAYS = [2, 4, 8]  # Exponential backoff in seconds
DEFAULT_LOOKBACK_DAYS = 7
TIMEZONE = "Asia/Taipei"
```

## Testing Strategy

This project follows a **minimal testing approach** by design (MVP philosophy):

- No formal unit tests
- Validation through dry-run modes:
  - `prompt_factory.py --dry-run`: Preview generated prompts
  - `run.py --dry-run`: Preview execution plan
- Manual testing via single topic execution: `python3 run.py --prompt topic_name`

## Error Handling and Retry Logic

The API caller implements exponential backoff:
- Maximum 3 retry attempts
- Delays: 2s → 4s → 8s between retries
- Failed requests are logged with `status: failed` in output frontmatter
- Execution continues to next prompt on failure (does not stop entire batch)

## Development Conventions

### Code Style

- Use type hints where practical (`-> str`, `-> list[Path]`, etc.)
- Prefer pathlib `Path` over string manipulation for file paths
- Use f-strings for string formatting
- Print statements for CLI feedback (no logging framework in MVP)
- Comments in Traditional Chinese (project convention)

### File Naming

- Configs: `configs/{topic_id}.yaml`
- Prompts: `prompts/{topic_id}.md`
- Outputs: `outputs/{topic_id}/{YYYYMMDD_HHMMSS}.md`
- Topic IDs should use snake_case (lowercase with underscores)

### Time Handling

- All timestamps use Asia/Taipei timezone
- Output filenames use local time format: `YYYYMMDD_HHMMSS`
- ISO 8601 format with timezone in frontmatter

## Security Considerations

### API Key Management

- API key stored in `.env` file (gitignored)
- `.env.example` provides template without actual values
- Key loaded via `python-dotenv` at runtime
- No hardcoded credentials in source code

### Sensitive Files (Gitignored)

```
.env                    # API credentials
.venv/                  # Virtual environment
__pycache__/            # Python bytecode
outputs/                # Generated content
logs/*.log              # Log files
```

## Extending the Project

### Adding a New Topic

1. Create config: `configs/new_topic.yaml`
2. Generate prompt: `python3 prompt_factory.py --config new_topic`
3. Review/edit: `prompts/new_topic.md`
4. Test: `python3 run.py --prompt new_topic`
5. Run in production: `python3 run.py`

### Modifying Search Behavior

- Edit configs in `configs/` directory
- Re-run `prompt_factory.py` to regenerate prompts
- Or directly edit prompts in `prompts/` directory for quick iteration

## Documentation References

- `docs/DESIGN_MVP.md` - Original MVP design decisions and rationale
- `docs/GROK_X_SEARCH_CAPABILITIES.md` - Research on Grok's search capabilities
- `docs/XAI_OFFICIAL_API_DOC.md` - Notes on official xAI API documentation

## Important Notes for AI Agents

1. **Always activate virtual environment** before running commands: `source .venv/bin/activate`
2. **Config changes require prompt regeneration** unless editing `.md` files directly
3. **API calls cost tokens** - use `--dry-run` to test without charges
4. **Output files are never overwritten** - each run creates new timestamped files
5. **The project is in Traditional Chinese** - maintain this for comments and documentation
6. **No formal test suite** - verify functionality through dry-runs and selective execution
