# twitter-fetch

透過 xAI Grok 的 X Search 功能，自動收集 Twitter/X 上的推文，並透過 Agent 分析找出具備傳播潛力的內容。

## 安裝

```bash
# 建立虛擬環境並安裝依賴
python3 -m venv .venv
pip install -r requirements.txt
```

## 設定

```bash
cp .env.example .env
# 編輯 .env，填入你的 XAI_API_KEY
```

## 使用前：啟用虛擬環境

**每次開啟新的終端機，都需要先執行這行：**

```bash
source .venv/bin/activate
```

啟用後，終端機提示符會變成 `(.venv) $`，之後就可以直接用 `python3` 執行所有指令。

---

## 功能概覽

本專案分為兩個階段：

1. **Fetch（資料收集）**：使用 Grok API 抓取 Twitter 資料
2. **Analyze（Agent 分析）**：使用免費 LLM CLI（Gemini/Qwen）分析推文並找出流量催化劑

---

## 第一階段：Fetch 資料收集

### 新增主題

```bash
# 1. 建立或編輯配置檔
vim configs/new_topic.yaml

# 2. 生成對應 prompt
python3 prompt_factory.py --config new_topic

# 3. 預覽 prompt（不寫檔）
python3 prompt_factory.py --config new_topic --dry-run
```

### 執行收集

```bash
# 執行所有 prompts
python3 fetch.py

# 只執行特定主題
python3 fetch.py --prompt ai_breakthrough

# 多個主題
python3 fetch.py --prompt ai_breakthrough,ai_emerging

# 預覽（不呼叫 API）
python3 fetch.py --dry-run
```

### Config 欄位參考

```yaml
search:
  tool: "keyword"       # keyword（關鍵字搜尋）或 semantic（語意搜尋）
  mode: "Latest"        # Latest（最新）或 Top（熱門）
  limit: 15             # 返回推文數量
  lookback_days: 7      # 搜尋最近幾天（自動注入 since: 日期）
  query: |              # 查詢主體
    ...
  conditions:
    min_faves: 100
    filter: "-replies"  # 排除類型（加 -）：-replies | -images | -videos
                        # 只限類型（不加 -）：images | videos | news | links
    lang: "en OR lang:zh"
    from_accounts:      # 選填，限定帳號來源
      - OpenAI
```

### 輸出格式

每次執行產生 `data/raw/{topic_id}/{YYYYMMDD_HHMMSS}.md`，包含：

```markdown
---
topic: "ai_breakthrough"
executed_at: "2026-02-23T22:31:24+08:00"
status: "success"
---

（Grok 原始回應內容）
```

---

## 第二階段：Agent 分析

使用免費 LLM CLI（Gemini 或 Qwen）分析已收集的推文，識別具備高傳播潛力的內容。

### 設定 Agent 配置

編輯 `configs/agent.yaml`：

```yaml
default_provider: "qwen"  # 或 "gemini"
default_models:
  qwen: "qwen-coder"      # Qwen 模型名稱
  gemini: "gemini-2.5-pro" # Gemini 模型名稱
```

**注意**：必須先設定此配置才能執行分析。

### 執行分析

```bash
# 分析單一主題
python3 analyze.py --agent traffic_catalyst --topics ai_news_keyword

# 分析多個主題（跨主題聚合）
python3 analyze.py --agent traffic_catalyst --topics ai_news_hybrid,ai_news_keyword,ai_news_semantic

# 預覽組裝後的 prompt（不呼叫 LLM）
python3 analyze.py --agent traffic_catalyst --topics ai_news_keyword --dry-run
```

### 現有 Agent

| Agent | 用途 | Prompt 檔案 |
|-------|------|-------------|
| `traffic_catalyst` | 識別短期高傳播潛力內容 | `prompts/agent/traffic_catalyst_agent.md` |
| `deep_research_scout` | 挖掘深度研究機會 | `prompts/agent/deep_research_scout_agent.md` |

### 輸出結果

分析結果儲存於 `data/refined/{agent_id}/{timestamp}_{topics}.md`：

```markdown
---
agent: traffic_catalyst
analyzed_at: "2026-02-26T00:24:11+08:00"
provider: gemini
model: gemini-2.5-pro
sources: ai_news_hybrid, ai_news_keyword, ai_news_semantic
---

Rank: [1]
Topic: ai_news_semantic
Title: AI 自主解决 6 项未解数学研究难题
URL: https://x.com/minchoi/status/...
Emotional Hook: 震撼与认知颠覆
...
```

---

## 第三階段：Manifest 彙整（選用）

將多個 Agent 分析結果彙整成單一 Markdown 檔案，方便人工一次性閱讀。

### 執行彙整

```bash
# 為指定 Agent 生成當日總覽
python3 manifest_generator.py --agent traffic_catalyst --date today
python3 manifest_generator.py --agent deep_research_scout --date today

# 預覽輸出（不儲存）
python3 manifest_generator.py --agent traffic_catalyst --date today --output stdout

# 指定日期
python3 manifest_generator.py --agent deep_research_scout --date 20260226
```

### 輸出位置

`data/manifest/{agent_id}_{YYYYMMDD}.md`

---

## 定時自動執行

使用 cron 設定每日自動執行：

```bash
# 編輯 crontab
crontab -e

# 加入以下行（台北時間）
# 05:00 - 抓取資料（15 topics）
0 5 * * * /home/openclaw/Projects/twitter-fetch/cron_fetch.sh

# 06:00 - 分析資料（2 agents x 5 topic groups = 10 API calls）
0 6 * * * /home/openclaw/Projects/twitter-fetch/cron_analyze.sh

# 07:00 - 生成總覽（2 agents）
0 7 * * * /home/openclaw/Projects/twitter-fetch/cron_manifest_generator.sh
```

---

## 專案結構

```
twitter-fetch/
├── .venv/                      # Python 虛擬環境
├── configs/                    # 配置檔（YAML）
│   ├── fetch/                  # Fetch 主題配置
│   └── agent.yaml              # Agent 分析配置（必要）
├── prompts/
│   ├── fetch/                  # 生成的搜尋 prompt
│   └── agent/                  # Agent 分析 prompt
├── data/
│   ├── raw/                    # Fetch 收集的原始資料
│   ├── refined/                # Agent 分析結果
│   └── manifest/               # 每日彙整總覽（給人閱讀）
├── logs/                       # 執行日誌
├── cron_fetch.sh               # 定時抓取腳本
├── cron_analyze.sh             # 定時分析腳本（多 Agent）
├── cron_manifest_generator.sh  # 定時生成總覽腳本
├── prompt_factory.py           # config → prompt 生成工具
├── manifest_generator.py       # 分析結果彙整工具
├── fetch.py                    # Fetch 執行腳本
├── analyze.py                  # Agent 分析腳本
└── requirements.txt
```
