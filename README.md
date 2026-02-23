# twitter-fetch

透過 xAI Grok 的 X Search 功能，自動收集 Twitter/X 上的推文。

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

## 使用方式

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
python3 run.py

# 只執行特定主題
python3 run.py --prompt ai_breakthrough

# 多個主題
python3 run.py --prompt ai_breakthrough,ai_emerging

# 預覽（不呼叫 API）
python3 run.py --dry-run
```

## 專案結構

```
twitter-fetch/
├── .venv/            # Python 虛擬環境（依賴套件）
├── configs/          # 主題配置（YAML）
├── prompts/          # 生成的搜尋 prompt（Markdown）
├── outputs/          # 收集結果（依主題分資料夾，含時間戳）
├── logs/             # 執行日誌
├── prompt_factory.py # config → prompt 生成工具
├── run.py            # 主執行腳本
└── requirements.txt
```

## Config 欄位參考

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

## 輸出格式

每次執行產生 `outputs/{topic_id}/{YYYYMMDD_HHMMSS}.md`，包含：

```markdown
---
topic: "ai_breakthrough"
executed_at: "2026-02-23T22:31:24+08:00"
status: "success"
---

（Grok 原始回應內容）
```
