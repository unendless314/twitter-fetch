#!/bin/bash
# Twitter Analyze Cron Script
# 定時執行多個 Agent 分析任務
# 使用 Gemini 免費 API

PROJECT_DIR="/home/openclaw/Projects/twitter-fetch"
cd "$PROJECT_DIR"

# 啟用虛擬環境
source .venv/bin/activate

# 確保日誌目錄存在
mkdir -p logs

# 記錄開始時間
echo "==========================================" >> logs/cron_analyze.log
echo "🚀 分析任務開始時間: $(date '+%Y-%m-%d %H:%M:%S')" >> logs/cron_analyze.log
echo "==========================================" >> logs/cron_analyze.log

# ============ 定義分析任務 ============

# 定義主題組合（每組 3 個 topics，共 5 次 API 呼叫）
TOPIC_GROUPS=(
    "ai_news_hybrid,ai_news_keyword,ai_news_semantic"
    "crypto_defi_native_hybrid,crypto_defi_native_keyword,crypto_defi_native_semantic"
    "crypto_institutional_hybrid,crypto_institutional_keyword,crypto_institutional_semantic"
    "macro_finance_hybrid,macro_finance_keyword,macro_finance_semantic"
    "ufo_disclosure_hybrid,ufo_disclosure_keyword,ufo_disclosure_semantic"
)

# 定義要執行的 Agents
AGENTS=(
    "traffic_catalyst"
    "deep_research_scout"
)

# 計算總任務數
TOTAL_TOPIC_GROUPS=${#TOPIC_GROUPS[@]}
TOTAL_AGENTS=${#AGENTS[@]}
TOTAL_TASKS=$((TOTAL_TOPIC_GROUPS * TOTAL_AGENTS))

SUCCESS_COUNT=0
TASK_NUM=0

# ============ 執行分析 ============

for AGENT in "${AGENTS[@]}"; do
    echo "" >> logs/cron_analyze.log
    echo "==========================================" >> logs/cron_analyze.log
    echo "📊 Agent: ${AGENT}" >> logs/cron_analyze.log
    echo "==========================================" >> logs/cron_analyze.log
    
    for TOPICS in "${TOPIC_GROUPS[@]}"; do
        ((TASK_NUM++))
        
        echo "" >> logs/cron_analyze.log
        echo "[${TASK_NUM}/${TOTAL_TASKS}] Agent: ${AGENT} | Topics: ${TOPICS}" >> logs/cron_analyze.log
        echo "執行時間: $(date '+%H:%M:%S')" >> logs/cron_analyze.log
        
        # 執行分析
        if python3 analyze.py --agent "${AGENT}" --topics "${TOPICS}" >> logs/cron_analyze.log 2>&1; then
            echo "✅ 完成" >> logs/cron_analyze.log
            ((SUCCESS_COUNT++))
        else
            echo "❌ 失敗" >> logs/cron_analyze.log
        fi
        
        # 任務間等待 10 秒避免 rate limit
        echo "等待 10 秒..." >> logs/cron_analyze.log
        sleep 10
    done
done

# ============ 記錄結束 ============

echo "" >> logs/cron_analyze.log
echo "==========================================" >> logs/cron_analyze.log
echo "✅ 分析任務結束時間: $(date '+%Y-%m-%d %H:%M:%S')" >> logs/cron_analyze.log
echo "成功: ${SUCCESS_COUNT}/${TOTAL_TASKS}" >> logs/cron_analyze.log
echo "==========================================" >> logs/cron_analyze.log
echo "" >> logs/cron_analyze.log
