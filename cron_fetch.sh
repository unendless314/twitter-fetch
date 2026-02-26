#!/bin/bash
# Twitter Fetch Cron Script
# 確保腳本在專案根目錄下執行，以正確載入 .env 和 configs

PROJECT_DIR="/home/openclaw/Projects/twitter-fetch"
cd "$PROJECT_DIR"

# 確保日誌目錄存在
mkdir -p logs

# 執行程式並紀錄輸出
echo "==========================================" >> logs/cron.log
echo "🚀 任務開始時間: $(date '+%Y-%m-%d %H:%M:%S')" >> logs/cron.log
./.venv/bin/python3 fetch.py >> logs/cron.log 2>&1
echo "✅ 任務結束時間: $(date '+%Y-%m-%d %H:%M:%S')" >> logs/cron.log
echo "==========================================" >> logs/cron.log
