#!/usr/bin/env python3
"""
run.py
掃描 prompts/ 目錄，呼叫 xAI Grok API，將結果存入 outputs/{topic_id}/{timestamp}.md。
"""

import argparse
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml
from dotenv import load_dotenv

load_dotenv()

PROMPTS_DIR = Path("prompts")
OUTPUTS_DIR = Path("outputs")
CONFIGS_DIR = Path("configs")
MODEL = "grok-4-1-fast-reasoning"
MAX_RETRIES = 3
RETRY_DELAYS = [2, 4, 8]  # 指數退避等待秒數
DEFAULT_LOOKBACK_DAYS = 7  # 若 config 未設定，預設抓最近 7 天


def get_api_key() -> str:
    key = os.getenv("XAI_API_KEY")
    if not key:
        print("[run.py] ❌ 未找到 XAI_API_KEY，請設定環境變數或建立 .env 檔案", file=sys.stderr)
        sys.exit(1)
    return key


def load_lookback_days(topic_id: str) -> int:
    """從對應 config 讀取 lookback_days，找不到則用預設值。"""
    config_path = CONFIGS_DIR / f"{topic_id}.yaml"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config.get("search", {}).get("lookback_days", DEFAULT_LOOKBACK_DAYS)
    return DEFAULT_LOOKBACK_DAYS


def inject_date_range(prompt_content: str, lookback_days: int) -> str:
    """在 prompt 末尾注入動態時間範圍（since: 日期），避免模板過期。"""
    since_date = (datetime.now(tz=ZoneInfo("Asia/Taipei")) - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    date_note = (
        f"\n## 時間範圍（動態）\n"
        f"請將搜尋範圍限制在 `since:{since_date}` 之後（最近 {lookback_days} 天）。\n"
    )
    return prompt_content.rstrip() + "\n" + date_note


def discover_prompts(selected: list[str] | None) -> list[Path]:
    """掃描 prompts/ 目錄，回傳可執行的 prompt 路徑列表。"""
    if not PROMPTS_DIR.exists():
        print(f"[run.py] ❌ 找不到 prompts/ 目錄，請先執行 prompt_factory.py", file=sys.stderr)
        sys.exit(1)

    all_prompts = sorted(PROMPTS_DIR.glob("*.md"))
    if not all_prompts:
        print("[run.py] ❌ prompts/ 目錄中沒有 .md 檔案", file=sys.stderr)
        sys.exit(1)

    if selected:
        # 篩選指定的 topics
        selected_set = set(selected)
        result = [p for p in all_prompts if p.stem in selected_set]
        missing = selected_set - {p.stem for p in result}
        if missing:
            print(f"[run.py] ⚠️  找不到以下 prompt：{', '.join(sorted(missing))}", file=sys.stderr)
        return result

    return all_prompts


def call_api(prompt_content: str, api_key: str) -> str:
    """呼叫 xAI API，回傳 Grok 的回應文字。"""
    from xai_sdk import Client
    from xai_sdk.chat import user
    from xai_sdk.tools import x_search

    client = Client(api_key=api_key, timeout=3600)
    chat = client.chat.create(
        model=MODEL,
        tools=[x_search()],
    )
    chat.append(user(prompt_content))
    response = chat.sample()
    return response.content


def call_api_with_retry(prompt_content: str, api_key: str, topic_id: str) -> tuple[str, str]:
    """
    帶指數退避重試的 API 呼叫。
    回傳 (content, status)，status 為 "success" 或 "failed"。
    """
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            content = call_api(prompt_content, api_key)
            if attempt > 0:
                print(f"  ✅ 成功（retry {attempt}/{MAX_RETRIES - 1}）")
            return content, "success"
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                wait = RETRY_DELAYS[attempt]
                print(f"  ❌ 失敗（retry {attempt + 1}/{MAX_RETRIES - 1}），{wait} 秒後重試... ({e})")
                time.sleep(wait)
            else:
                print(f"  ❌ 全部 {MAX_RETRIES} 次嘗試失敗：{e}")

    return str(last_error), "failed"


def write_output(topic_id: str, content: str, status: str, executed_at: datetime) -> Path:
    """將結果寫入時間戳命名的 Markdown 檔案。"""
    timestamp = executed_at.strftime("%Y%m%d_%H%M%S")
    output_dir = OUTPUTS_DIR / topic_id
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{timestamp}.md"
    executed_at_str = executed_at.isoformat()

    frontmatter = f"""---
topic: "{topic_id}"
executed_at: "{executed_at_str}"
status: "{status}"
---

"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(frontmatter)
        f.write(content)

    return output_path


def main():
    parser = argparse.ArgumentParser(description="執行 Grok X Search 資料收集")
    parser.add_argument(
        "--prompt",
        default=None,
        help="指定 topic ID（逗號分隔多個，如 ai_breakthrough,crypto_market）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="預覽模式：顯示將執行的操作，但不實際呼叫 API",
    )
    args = parser.parse_args()

    selected = [s.strip() for s in args.prompt.split(",")] if args.prompt else None
    prompt_paths = discover_prompts(selected)
    topic_ids = [p.stem for p in prompt_paths]

    print(f"[run.py] 找到 {len(prompt_paths)} 個 prompts：{', '.join(topic_ids)}")

    if args.dry_run:
        print("[run.py] [dry-run] 不實際呼叫 API，以下為預計執行內容：")
        for i, path in enumerate(prompt_paths, 1):
            print(f"  [{i}/{len(prompt_paths)}] {path.stem} → outputs/{path.stem}/<timestamp>.md")
        return

    api_key = get_api_key()

    success_count = 0
    fail_count = 0

    for i, prompt_path in enumerate(prompt_paths, 1):
        topic_id = prompt_path.stem
        print(f"[{i}/{len(prompt_paths)}] 執行 {topic_id} ...")

        prompt_content = prompt_path.read_text(encoding="utf-8")
        lookback_days = load_lookback_days(topic_id)
        prompt_content = inject_date_range(prompt_content, lookback_days)
        executed_at = datetime.now(tz=ZoneInfo("Asia/Taipei"))

        content, status = call_api_with_retry(prompt_content, api_key, topic_id)
        output_path = write_output(topic_id, content, status, executed_at)

        if status == "success":
            print(f"[{i}/{len(prompt_paths)}] ✅ 完成 → {output_path}")
            success_count += 1
        else:
            print(f"[{i}/{len(prompt_paths)}] ❌ 失敗（已記錄）→ {output_path}")
            fail_count += 1

    print(f"[run.py] 全部完成。成功 {success_count} / 失敗 {fail_count}")


if __name__ == "__main__":
    main()
