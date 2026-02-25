#!/usr/bin/env python3
"""
analyze.py
讀取 data/raw/ 資料，組裝 Agent Prompt，呼叫免費 LLM CLI 進行分析。
"""

import argparse
import re
import subprocess
import sys
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


# ============ Provider 實作 ============

def call_gemini(prompt_content: str, model: str) -> tuple[str, bool]:
    """呼叫 Gemini CLI"""
    cmd = ["gemini", "請分析", "-m", model]
    
    try:
        result = subprocess.run(
            cmd,
            input=prompt_content,
            capture_output=True,
            text=True,
            timeout=300,
        )
        return result.stdout, result.returncode == 0
    except Exception as e:
        return str(e), False


def call_qwen(prompt_content: str, model: str) -> tuple[str, bool]:
    """呼叫 Qwen CLI"""
    cmd = ["qwen", "請分析", "-m", model]
    
    try:
        result = subprocess.run(
            cmd,
            input=prompt_content,
            capture_output=True,
            text=True,
            timeout=300,
        )
        return result.stdout, result.returncode == 0
    except Exception as e:
        return str(e), False


# ============ 核心邏輯 ============

def load_config() -> dict:
    """載入配置檔，缺少必要欄位時報錯"""
    if not CONFIG_FILE.exists():
        print(f"[analyze.py] ❌ 找不到配置檔：{CONFIG_FILE}", file=sys.stderr)
        print(f"[analyze.py] 💡 請建立 {CONFIG_FILE} 並設定 default_provider 和 default_models", file=sys.stderr)
        sys.exit(1)
    
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    
    # 檢查必要欄位
    if "default_provider" not in config:
        print(f"[analyze.py] ❌ 配置檔缺少必要欄位：default_provider", file=sys.stderr)
        sys.exit(1)
    
    if "default_models" not in config or not config["default_models"]:
        print(f"[analyze.py] ❌ 配置檔缺少必要欄位：default_models", file=sys.stderr)
        sys.exit(1)
    
    provider = config["default_provider"]
    if provider not in config["default_models"]:
        print(f"[analyze.py] ❌ 配置檔錯誤：default_provider '{provider}' 在 default_models 中找不到對應模型", file=sys.stderr)
        sys.exit(1)
    
    return config


def get_latest_raw_file(topic_dir: Path) -> Path | None:
    """取得 topic 目錄下最新的檔案"""
    md_files = list(topic_dir.glob("*.md"))
    if not md_files:
        return None
    return sorted(md_files, key=lambda p: p.stem, reverse=True)[0]


def read_content(file_path: Path) -> str:
    """讀取檔案內容，如有 frontmatter 則只返回 body"""
    text = file_path.read_text(encoding="utf-8")
    
    match = re.match(r'^---\s*\n.*?\n---\s*\n(.*)$', text, re.DOTALL)
    if match:
        return match.group(1)
    return text


def assemble_sources(topics: list[str]) -> str:
    """組裝 sources 文字"""
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
        
        content = read_content(latest_file)
        
        section = f"""---
## topic: {topic}
---

{content.strip()}
"""
        sections.append(section)
    
    return "\n\n".join(sections)


def save_result(agent_id: str, topics: list[str], output: str, provider: str, model: str, timestamp: str):
    """儲存分析結果"""
    output_dir = REFINED_DIR / agent_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if len(topics) == 1:
        topics_desc = topics[0]
    elif len(topics) <= 3:
        topics_desc = "_".join(topics)
    else:
        topics_desc = f"multi_{len(topics)}topics"
    
    output_file = output_dir / f"{timestamp}_{topics_desc}.md"
    
    md_content = f"""---
agent: {agent_id}
analyzed_at: {datetime.now(tz=ZoneInfo("Asia/Taipei")).isoformat()}
provider: {provider}
model: {model}
sources: {', '.join(topics)}
---

{output}
"""
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print(f"[analyze.py] ✅ 結果已儲存：{output_file}")


def run_analysis(agent_id: str, topics: list[str], provider: str, model: str, dry_run: bool = False):
    """執行分析流程"""
    
    # 1. 載入 agent prompt template
    prompt_file = AGENT_PROMPTS_DIR / f"{agent_id}_agent.md"
    
    if not prompt_file.exists():
        print(f"[analyze.py] ❌ 找不到 Agent prompt：{prompt_file}", file=sys.stderr)
        sys.exit(1)
    
    template = prompt_file.read_text(encoding="utf-8")
    
    # 2. 組裝 sources
    print(f"[analyze.py] 組裝 sources：{', '.join(topics)}")
    sources_text = assemble_sources(topics)
    
    if not sources_text:
        print("[analyze.py] ❌ 沒有可用的 source 資料", file=sys.stderr)
        sys.exit(1)
    
    # 3. 組裝 prompt（直接拼接）
    prompt_content = template.rstrip() + "\n\n" + sources_text
    
    # 4. Dry run 模式
    if dry_run:
        print("=" * 60)
        print("[DRY RUN] 組裝後的 Prompt：")
        print("=" * 60)
        print(prompt_content)
        print("=" * 60)
        return
    
    # 5. 寫入 temp 檔案（供 debug）
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(tz=ZoneInfo("Asia/Taipei")).strftime("%Y%m%d_%H%M%S")
    temp_file = TEMP_DIR / f"{agent_id}_{timestamp}.md"
    temp_file.write_text(prompt_content, encoding="utf-8")
    print(f"[analyze.py] Debug 檔案：{temp_file}")
    
    print(f"[analyze.py] 使用 Provider：{provider}，Model：{model}")
    
    # 6. 呼叫 LLM
    if provider == "gemini":
        output, success = call_gemini(prompt_content, model)
    elif provider == "qwen":
        output, success = call_qwen(prompt_content, model)
    else:
        print(f"[analyze.py] ❌ 不支援的 Provider：{provider}", file=sys.stderr)
        sys.exit(1)
    
    if not success:
        print(f"[analyze.py] ❌ LLM 呼叫失敗：{output}", file=sys.stderr)
        sys.exit(1)
    
    # 7. 儲存（直接存原始輸出，不做任何解析）
    save_result(agent_id, topics, output, provider, model, timestamp)
    
    # 8. 分析成功後刪除 temp debug 檔案
    try:
        temp_file.unlink()
        print(f"[analyze.py] 🗑️  已清理 debug 檔案：{temp_file.name}")
    except OSError as e:
        print(f"[analyze.py] ⚠️  無法刪除 debug 檔案：{e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="執行 Agent 分析")
    parser.add_argument("--agent", "-a", required=True, help="Agent ID")
    parser.add_argument("--topics", "-t", required=True, help="Topics，逗號分隔")
    parser.add_argument("--dry-run", action="store_true", help="僅組裝 prompt")
    
    args = parser.parse_args()
    
    # 載入配置（會在缺少必要欄位時報錯退出）
    config = load_config()
    
    # 從配置檔讀取 provider 和 model
    provider = config["default_provider"]
    model = config["default_models"].get(provider)
    if not model:
        print(f"[analyze.py] ❌ 配置檔中找不到 provider '{provider}' 對應的模型", file=sys.stderr)
        sys.exit(1)
    
    topics = [t.strip() for t in args.topics.split(",")]
    
    run_analysis(args.agent, topics, provider, model, args.dry_run)


if __name__ == "__main__":
    main()
