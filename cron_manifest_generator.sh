#!/bin/bash
# Manifest Generator Cron Script
# 定時聚合 Agent 輸出，生成 Markdown Manifest（人類可讀總覽）

PROJECT_DIR="/home/openclaw/Projects/twitter-fetch"
cd "$PROJECT_DIR"

# 啟用虛擬環境
source .venv/bin/activate

# 確保日誌目錄存在
mkdir -p logs

# 記錄開始時間
echo "==========================================" >> logs/cron_manifest.log
echo "🚀 Manifest 生成任務開始時間: $(date '+%Y-%m-%d %H:%M:%S')" >> logs/cron_manifest.log
echo "==========================================" >> logs/cron_manifest.log

# 定義要生成 manifest 的 Agents
AGENTS=(
    "traffic_catalyst"
    "deep_research_scout"
)

DATE_STR=$(date '+%Y%m%d')
TOTAL_TASKS=${#AGENTS[@]}
SUCCESS_COUNT=0

# 依序為每個 Agent 生成 manifest
for AGENT in "${AGENTS[@]}"; do
    echo "" >> logs/cron_manifest.log
    echo "[${SUCCESS_COUNT}+1/${TOTAL_TASKS}] 生成 ${AGENT} 的 manifest..." >> logs/cron_manifest.log
    echo "執行時間: $(date '+%H:%M:%S')" >> logs/cron_manifest.log
    
    if python3 manifest_generator.py --agent "${AGENT}" --date today --output file >> logs/cron_manifest.log 2>&1; then
        echo "✅ ${AGENT} manifest 生成完成" >> logs/cron_manifest.log
        ((SUCCESS_COUNT++))
    else
        echo "❌ ${AGENT} manifest 生成失敗" >> logs/cron_manifest.log
    fi
done

# 記錄結束時間
echo "" >> logs/cron_manifest.log
echo "==========================================" >> logs/cron_manifest.log
echo "✅ Manifest 生成任務結束時間: $(date '+%Y-%m-%d %H:%M:%S')" >> logs/cron_manifest.log
echo "成功: ${SUCCESS_COUNT}/${TOTAL_TASKS}" >> logs/cron_manifest.log
echo "==========================================" >> logs/cron_manifest.log
echo "" >> logs/cron_manifest.log
