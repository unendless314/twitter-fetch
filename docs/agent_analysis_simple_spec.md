# Agent Analysis Pipeline - 簡化設計規格

> 原則：**增量開發，不干擾現有代碼**

---

## 1. 僅新增一個檔案

```
twitter-fetch/
├── fetch.py                  # 現有：不動
├── prompt_factory.py         # 現有：不動
├── analyze.py                # 【新增】唯一的新檔案
├── configs/
│   └── fetch/                # 現有：不動
│   └── agent.yaml            # 【新增】Agent 配置（簡單版）
├── prompts/
│   └── fetch/                # 現有：不動
│   └── agent/                # 現有：您已建立
└── data/
    └── raw/                  # 現有：輸入來源
    └── refined/              # 現有：輸出目錄
```

**只新增 2 個檔案：**
1. `analyze.py` - 主要執行腳本
2. `configs/agent.yaml` - 簡單配置

---

## 2. analyze.py 設計

參考現有 `fetch.py` 的風格，保持簡單直接：

```python
#!/usr/bin/env python3
"""
analyze.py
讀取 data/raw/ 資料，組裝 Agent Prompt，呼叫免費 LLM CLI 進行分析。
"""

import argparse
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

# ============ 配置 ============
RAW_DIR = Path("data/raw")
REFINED_DIR = Path("data/refined")
AGENT_PROMPTS_DIR = Path("prompts/agent")
CONFIG_FILE = Path("configs/agent.yaml")
TEMP_DIR = Path("temp/analyze")

DEFAULT_PROVIDER = "gemini"  # 或 qwen
DEFAULT_MODEL = "gemini-2.5-pro"  # gemini-2.5-pro / qwen-coder


# ============ Provider 實作 ============

def call_gemini(prompt_file: Path, model: str) -> tuple[str, bool]:
    """呼叫 Gemini CLI"""
    meta_prompt = f"請讀取 {prompt_file.name} 並按照其中指示分析，輸出 YAML 格式結果"
    cmd = [
        "gemini",
        "-p", meta_prompt,
        "-o", "json",
        "-m", model,
        "--approval-mode", "plan",
    ]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=TEMP_DIR.parent,  # 沙盒限制：只能讀取執行目錄下檔案
            capture_output=True,
            text=True,
            timeout=300,
        )
        return result.stdout, result.returncode == 0
    except Exception as e:
        return str(e), False


def call_qwen(prompt_file: Path, model: str) -> tuple[str, bool]:
    """呼叫 Qwen CLI"""
    meta_prompt = f"請讀取 {prompt_file.name} 並按照其中指示分析，輸出 YAML 格式結果"
    cmd = [
        "qwen",
        meta_prompt,  # positional，非 -p
        "-o", "json",
        "-m", model,
        "--approval-mode", "plan",
    ]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=TEMP_DIR.parent,
            capture_output=True,
            text=True,
            timeout=300,
        )
        return result.stdout, result.returncode == 0
    except Exception as e:
        return str(e), False


# ============ 核心邏輯 ============

def load_config() -> dict:
    """載入配置檔"""
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_latest_raw_file(topic_dir: Path) -> Path | None:
    """取得 topic 目錄下最新的檔案（依檔名 timestamp）"""
    md_files = list(topic_dir.glob("*.md"))
    if not md_files:
        return None
    # 依檔名排序（timestamp 格式：YYYYMMDD_HHMMSS.md）
    return sorted(md_files, key=lambda p: p.stem, reverse=True)[0]


def parse_frontmatter(file_path: Path) -> tuple[dict, str]:
    """解析 Markdown frontmatter，回傳 (frontmatter_dict, content)"""
    text = file_path.read_text(encoding="utf-8")
    
    # 簡單的 frontmatter 解析
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', text, re.DOTALL)
    if match:
        try:
            frontmatter = yaml.safe_load(match.group(1))
            content = match.group(2)
            return frontmatter or {}, content
        except yaml.YAMLError:
            pass
    return {}, text


def assemble_sources(topics: list[str]) -> str:
    """
    組裝 sources 文字，用於替換 {{SOURCES}}
    
    輸出格式：
    ---
    ## Source: {topic}
    ## File: {file_path}
    ## Executed At: {timestamp}
    ---
    
    {content}
    """
    sections = []
    
    for topic in topics:
        topic_dir = RAW_DIR / topic
        if not topic_dir.exists():
            print(f"[analyze.py] ⚠️  Topic 目錄不存在：{topic}", file=sys.stderr)
            continue
        
        latest_file = get_latest_raw_file(topic_dir)
        if not latest_file:
            print(f"[analyze.py] ⚠️  Topic 無資料檔案：{topic}", file=sys.stderr)
            continue
        
        frontmatter, content = parse_frontmatter(latest_file)
        
        section = f"""---
## Source: {topic}
## File: {latest_file}
## Executed At: {frontmatter.get('executed_at', 'unknown')}
## Status: {frontmatter.get('status', 'unknown')}
---

{content.strip()}
"""
        sections.append(section)
    
    return "\n\n".join(sections)


def run_analysis(agent_id: str, topics: list[str], provider: str, model: str, dry_run: bool = False):
    """執行分析流程"""
    
    # 1. 載入 agent prompt template
    prompt_file = AGENT_PROMPTS_DIR / f"{agent_id}.md"
    if not prompt_file.exists():
        # 嘗試自動補上 _agent 後綴
        prompt_file = AGENT_PROMPTS_DIR / f"{agent_id}_agent.md"
    
    if not prompt_file.exists():
        print(f"[analyze.py] ❌ 找不到 Agent prompt：{agent_id}", file=sys.stderr)
        sys.exit(1)
    
    template = prompt_file.read_text(encoding="utf-8")
    
    # 2. 組裝 sources
    print(f"[analyze.py] 組裝 sources：{', '.join(topics)}")
    sources_text = assemble_sources(topics)
    
    if not sources_text:
        print("[analyze.py] ❌ 沒有可用的 source 資料", file=sys.stderr)
        sys.exit(1)
    
    # 3. 替換 {{SOURCES}}
    prompt_content = template.replace("{{SOURCES}}", sources_text)
    
    # 4. Dry run 模式：輸出 prompt 並結束
    if dry_run:
        print("=" * 60)
        print("[DRY RUN] 組裝後的 Prompt：")
        print("=" * 60)
        print(prompt_content)
        print("=" * 60)
        return
    
    # 5. 寫入 temp 檔案
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(tz=ZoneInfo("Asia/Taipei")).strftime("%Y%m%d_%H%M%S")
    temp_file = TEMP_DIR / f"{agent_id}_{timestamp}.md"
    temp_file.write_text(prompt_content, encoding="utf-8")
    
    print(f"[analyze.py] 使用 Provider：{provider}，Model：{model}")
    
    try:
        # 6. 呼叫 LLM
        if provider == "gemini":
            output, success = call_gemini(temp_file, model)
        elif provider == "qwen":
            output, success = call_qwen(temp_file, model)
        else:
            print(f"[analyze.py] ❌ 不支援的 Provider：{provider}", file=sys.stderr)
            sys.exit(1)
        
        if not success:
            print(f"[analyze.py] ❌ LLM 呼叫失敗：{output}", file=sys.stderr)
            sys.exit(1)
        
        # 7. 解析輸出（從 JSON 或 YAML 區塊提取）
        result = parse_llm_output(output)
        
        # 8. 儲存結果
        save_result(agent_id, topics, result, provider, model, timestamp)
        
    finally:
        # 清理 temp 檔案
        temp_file.unlink(missing_ok=True)


def parse_llm_output(output: str) -> dict:
    """解析 LLM 輸出為結構化資料"""
    # 嘗試直接解析 JSON（因為 CLI 使用 -o json）
    try:
        return yaml.safe_load(output)
    except yaml.YAMLError:
        pass
    
    # 嘗試從 code block 提取
    match = re.search(r'```(?:yaml|json)\s*(.*?)\s*```', output, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            pass
    
    # 無法解析，回傳原始內容
    return {"raw_output": output}


def save_result(agent_id: str, topics: list[str], result: dict, provider: str, model: str, timestamp: str):
    """儲存分析結果到 data/refined/"""
    
    output_dir = REFINED_DIR / agent_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 組合檔名
    if len(topics) == 1:
        topics_desc = topics[0]
    elif len(topics) <= 3:
        topics_desc = "_".join(topics)
    else:
        topics_desc = f"multi_{len(topics)}topics"
    
    output_file = output_dir / f"{timestamp}_{topics_desc}.yaml"
    
    # 建構完整輸出
    output_data = {
        "agent": agent_id,
        "analyzed_at": datetime.now(tz=ZoneInfo("Asia/Taipei")).isoformat(),
        "provider": provider,
        "model": model,
        "sources": topics,
        "results": result,
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(output_data, f, allow_unicode=True, sort_keys=False)
    
    print(f"[analyze.py] ✅ 結果已儲存：{output_file}")


# ============ CLI ============

def main():
    parser = argparse.ArgumentParser(description="執行 Agent 分析")
    parser.add_argument("--agent", "-a", required=True, help="Agent ID（如 deep_research_scout）")
    parser.add_argument("--topics", "-t", required=True, help="Topics，逗號分隔")
    parser.add_argument("--provider", "-p", default=DEFAULT_PROVIDER, choices=["gemini", "qwen"], 
                        help="LLM Provider")
    parser.add_argument("--model", "-m", default=None, help="模型名稱")
    parser.add_argument("--dry-run", action="store_true", help="僅組裝 prompt，不執行 LLM")
    
    args = parser.parse_args()
    
    topics = [t.strip() for t in args.topics.split(",")]
    model = args.model or DEFAULT_MODEL
    
    run_analysis(args.agent, topics, args.provider, model, args.dry_run)


if __name__ == "__main__":
    main()
```

---

## 3. configs/agent.yaml（簡單版）

```yaml
# Agent Analysis 設定
# 可選，不提供則使用 analyze.py 內的預設值

# 預設 Provider
default_provider: "gemini"  # 或 "qwen"

# Provider 預設模型
default_models:
  gemini: "gemini-2.5-pro"
  qwen: "qwen-coder"
```

---

## 4. 使用範例

```bash
# 基本用法（Gemini CLI）
python analyze.py --agent deep_research_scout --topics ai_news_keyword

# 多個 topics（跨領域聚合）
python analyze.py --agent deep_research_scout --topics ai_news_keyword,crypto_defi_native_keyword

# 切換到 Qwen CLI
python analyze.py --agent traffic_catalyst --topics ai_news_keyword --provider qwen

# 指定模型
python analyze.py --agent deep_research_scout --topics ai_news_keyword --provider gemini --model gemini-2.0-flash

# 僅組裝 prompt（除錯用）
python analyze.py --agent deep_research_scout --topics ai_news_keyword --dry-run
```

---

## 5. 與現有代碼的關係

| 現有模組 | 關係 | 說明 |
|---------|------|------|
| `fetch.py` | 無關聯 | Fetch pipeline 獨立運作 |
| `prompt_factory.py` | 無關聯 | 產生 fetch prompts |
| `prompts/fetch/` | 輸入來源之一 | analyze.py 可讀取這些 topics |
| `data/raw/` | 輸入來源 | analyze.py 讀取此處的資料 |
| `configs/fetch/` | 無關聯 | Fetch 專用配置 |

**完全獨立的新功能，不影響既有流程。**

---

