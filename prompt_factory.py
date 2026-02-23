#!/usr/bin/env python3
"""
prompt_factory.py
讀取 configs/{id}.yaml，生成對應的 prompts/{id}.md。
"""

import argparse
import sys
from pathlib import Path

import yaml


CONFIGS_DIR = Path("configs")
PROMPTS_DIR = Path("prompts")

TOOL_NAMES = {
    "keyword": "Keyword Search",
    "semantic": "Semantic Search",
}


def load_config(config_arg: str) -> dict:
    """解析 --config 參數，支援 ID 或路徑。"""
    path = Path(config_arg)
    if not path.suffix:
        path = CONFIGS_DIR / f"{config_arg}.yaml"

    if not path.exists():
        print(f"[prompt_factory] ❌ 找不到配置檔：{path}", file=sys.stderr)
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    required_keys = ["id", "search", "filter", "output"]
    for key in required_keys:
        if key not in config:
            print(f"[prompt_factory] ❌ 配置缺少必要欄位：{key}", file=sys.stderr)
            sys.exit(1)

    return config


def build_prompt(config: dict) -> str:
    """將 config 組合成 Markdown prompt。"""
    topic_id = config["id"]
    search = config["search"]
    filt = config["filter"]
    output = config["output"]

    tool_name = TOOL_NAMES.get(search.get("tool", "keyword"), "Keyword Search")
    mode = search.get("mode", "Latest")
    limit = search.get("limit", 15)
    query = search.get("query", "").strip()

    # 先讀 conditions，再從其中取出各過濾參數（含 from_accounts）
    conditions = search.get("conditions") or {}
    from_accounts = conditions.get("from_accounts") or []
    from_accounts = [a.lstrip("@") for a in from_accounts if a]  # 去除多餘的 @

    include_text = filt.get("include", "").strip()
    exclude_text = filt.get("exclude", "").strip()
    output_format = output.get("format", "").strip()

    # 組合帳號來源區塊（有設定才顯示）
    accounts_section = ""
    if from_accounts:
        accounts_list = " OR ".join(f"from:{a}" for a in from_accounts)
        accounts_section = f"\n## 來源帳號限制\n請**優先**從以下帳號搜尋：`{accounts_list}`\n如果這些帳號近期無符合條件的推文，可擴大至一般搜尋。\n"

    prompt = f"""# X Search 任務：{topic_id}

## 任務說明
請使用 X (Twitter) 的搜尋功能，幫我收集符合以下條件的推文。

## 搜尋策略
- **工具類型**：{tool_name}
- **排序模式**：{mode}
- **數量限制**：{limit} 條相關推文

## 搜尋條件

### 查詢主體（{tool_name}）
```
{query}
```

### 條件參數
"""

    # 組合條件參數區塊（conditions 底下的所有過濾參數）
    min_faves = conditions.get("min_faves")
    filter_val = conditions.get("filter", "").strip()
    lang = conditions.get("lang", "").strip()

    cond_lines = []
    if min_faves:
        cond_lines.append(f"- `min_faves:{min_faves}`（互動門檻）")
    if filter_val:
        # 若以 - 開頭表示排除，否則為包含
        if filter_val.startswith("-"):
            filter_type = filter_val.lstrip("-")
            cond_lines.append(
                f"- `-filter:{filter_type}`（排除類型，可選：replies / images / videos / news / links）"
            )
        else:
            cond_lines.append(
                f"- `filter:{filter_val}`（只限類型，可選：images / videos / news / links）"
            )
    if lang:
        cond_lines.append(f"- `lang:{lang}`（語言過濾）")

    if cond_lines:
        prompt += "\n".join(cond_lines) + "\n"
    else:
        prompt += "（無額外過濾條件）\n"

    prompt += f"""
{accounts_section}
## 內容篩選

### 優先收錄
{include_text}

### 排除內容
{exclude_text}

## 輸出格式
{output_format}

## 注意事項
1. 請確保資訊準確，包含正確的推文連結
2. 如果找到的推文不足 {limit} 條，請說明原因
3. 如果沒有找到符合條件的推文，請明確告知
4. 優先選擇互動數較高（按讚、轉推多）的內容
"""
    return prompt


def main():
    parser = argparse.ArgumentParser(
        description="從 config YAML 生成 prompt Markdown"
    )
    parser.add_argument(
        "--config",
        required=True,
        help="主題 ID（如 ai_breakthrough）或 YAML 檔案路徑",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="輸出路徑（預設：prompts/{id}.md）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="預覽模式：只印出結果，不寫入檔案",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    topic_id = config["id"]
    prompt_content = build_prompt(config)

    if args.dry_run:
        print(f"[prompt_factory] 預覽模式（不寫入）\n")
        print("=" * 60)
        print(prompt_content)
        print("=" * 60)
        return

    output_path = Path(args.output) if args.output else PROMPTS_DIR / f"{topic_id}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(prompt_content)

    print(f"[prompt_factory] ✅ 已生成：{output_path}")


if __name__ == "__main__":
    main()
