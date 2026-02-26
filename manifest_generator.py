#!/usr/bin/env python3
"""
manifest_generator.py
讀取指定 Agent 的輸出檔案，聚合成單一 Markdown Manifest。
最簡單作法：直接將各檔案的 frontmatter + body 原封不動 dump 出來。
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

# ============ 配置 ============
REFINED_DIR = Path("data/refined")
MANIFEST_DIR = Path("data/manifest")


def parse_file(file_path: Path) -> tuple[dict | None, str]:
    """
    解析 Markdown 檔案，回傳 (frontmatter_dict, body_content)
    如果沒有 frontmatter，frontmatter_dict 為 None
    """
    text = file_path.read_text(encoding="utf-8")
    
    # 嘗試解析 frontmatter
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', text, re.DOTALL)
    if match:
        try:
            frontmatter = yaml.safe_load(match.group(1)) or {}
            body = match.group(2).strip()
            return frontmatter, body
        except yaml.YAMLError:
            pass
    
    # 沒有 frontmatter，整個內容當作 body
    return None, text.strip()


def filter_files_by_date(files: list[Path], date_str: str) -> list[Path]:
    """根據日期過濾檔案（從檔名解析 YYYYMMDD）"""
    filtered = []
    for f in files:
        match = re.match(r'(\d{8})_\d{6}', f.stem)
        if match and match.group(1) == date_str:
            filtered.append(f)
    return filtered


def generate_manifest(agent_id: str, date_str: str) -> str:
    """生成 Markdown Manifest"""
    
    agent_dir = REFINED_DIR / agent_id
    
    # 檢查目錄是否存在
    if not agent_dir.exists():
        print(f"[manifest_generator.py] ❌ 找不到 Agent 目錄：{agent_dir}", file=sys.stderr)
        sys.exit(1)
    
    # 取得所有 .md 檔案並排序
    all_files = sorted(agent_dir.glob("*.md"), key=lambda p: p.stem)
    
    if not all_files:
        print(f"[manifest_generator.py] ⚠️ 目錄中沒有 .md 檔案：{agent_dir}", file=sys.stderr)
        sys.exit(1)
    
    # 日期過濾
    if date_str == "today":
        date_str = datetime.now(tz=ZoneInfo("Asia/Taipei")).strftime("%Y%m%d")
    
    files = filter_files_by_date(all_files, date_str)
    
    if not files:
        print(f"[manifest_generator.py] ⚠️ 找不到 {date_str} 的檔案", file=sys.stderr)
        sys.exit(1)
    
    print(f"[manifest_generator.py] 找到 {len(files)} 個檔案，日期：{date_str}")
    
    # 生成 Manifest
    timestamp = datetime.now(tz=ZoneInfo("Asia/Taipei")).isoformat()
    display_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    
    # 收集所有 frontmatter 資訊用於標頭
    sources = []
    for f in files:
        frontmatter, _ = parse_file(f)
        if frontmatter:
            if 'sources' in frontmatter:
                sources.append(frontmatter['sources'])
            elif 'topic' in frontmatter:
                sources.append(frontmatter['topic'])
    
    lines = [
        "---",
        f"manifest_type: {agent_id}",
        f"date: {display_date}",
        f"generated_at: {timestamp}",
        f"source_files: {len(files)}",
        "---",
        "",
        f"# {agent_id.replace('_', ' ').title()} Manifest - {display_date}",
        "",
        f"> 自動生成於 {timestamp}",
        f"> 原始檔案數：{len(files)}",
        "",
        "---",
        "",
    ]
    
    # 直接 dump 每個檔案的內容
    for i, f in enumerate(files, 1):
        frontmatter, body = parse_file(f)
        
        # 標題從檔名取得（去掉日期前綴）
        file_title = re.sub(r'^\d{8}_\d{6}_', '', f.stem)
        file_title = file_title.replace('_', ' ')
        
        lines.append(f"## Source {i}: {file_title}")
        lines.append("")
        
        # 如果有 frontmatter，顯示關鍵資訊
        if frontmatter:
            if 'sources' in frontmatter:
                lines.append(f"**Sources**: {frontmatter['sources']}")
            if 'analyzed_at' in frontmatter:
                lines.append(f"**Analyzed At**: {frontmatter['analyzed_at']}")
            if 'provider' in frontmatter:
                lines.append(f"**Provider**: {frontmatter.get('provider', 'N/A')} / {frontmatter.get('model', 'N/A')}")
            lines.append("")
        
        # 直接 dump body 內容（LLM 原始輸出）
        lines.append(body)
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def save_manifest(manifest: str, agent_id: str, date_str: str) -> Path:
    """儲存 Manifest 檔案"""
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    
    output_file = MANIFEST_DIR / f"{agent_id}_{date_str}.md"
    output_file.write_text(manifest, encoding="utf-8")
    
    return output_file


def main():
    parser = argparse.ArgumentParser(description="生成 Agent 輸出的 Markdown Manifest")
    parser.add_argument("--agent", "-a", required=True, help="Agent ID (e.g., deep_research_scout)")
    parser.add_argument("--date", "-d", default="today", 
                        help="日期 (YYYYMMDD 或 'today')，預設 today")
    parser.add_argument("--output", "-o", choices=["file", "stdout"], default="file",
                        help="輸出模式：file (儲存到 data/manifest/) 或 stdout (輸出到終端)")
    
    args = parser.parse_args()
    
    # 生成 Manifest
    manifest = generate_manifest(args.agent, args.date)
    
    # 輸出
    if args.output == "stdout":
        print(manifest)
    else:
        date_str = args.date if args.date != "today" else datetime.now(tz=ZoneInfo("Asia/Taipei")).strftime("%Y%m%d")
        output_path = save_manifest(manifest, args.agent, date_str)
        print(f"[manifest_generator.py] ✅ Manifest 已儲存：{output_path}")


if __name__ == "__main__":
    main()
