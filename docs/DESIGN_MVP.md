# Twitter Fetch - MVP 設計方案

> 目標：簡單、實用、不過度設計

---

## 設計決策紀錄

> 以下為 MVP 階段確認的關鍵設計選擇，寫程式時直接依此實作。

### Topic ID 規則
- **Prompt 檔名即 topic_id**：`prompts/ai_breakthrough.md` → topic_id = `ai_breakthrough`
- `fetch.py` 透過掃描 `prompts/fetch/` 目錄自動列出可執行的主題
- `outputs/{topic_id}/` 資料夾名稱直接對應 prompt 檔名（不含副檔名）

### 輸出策略
- **純存原始回應**：Grok 回傳什麼就寫什麼，不做任何後處理或格式轉換
- 設計原則：prompt 仍在調整期，現在規定後處理格式容易造成重工
- 輸出檔案開頭加 YAML frontmatter（topic、executed_at、status），其餘為 Grok 原始回應

### 錯誤重試策略
- **指數退避，最多 3 次重試**
- 等待時間：第 1 次失敗後等 2 秒、第 2 次 4 秒、第 3 次 8 秒
- 3 次全失敗後：在 frontmatter 記錄 `status: failed`，繼續執行下一個 prompt（不中斷整體流程）

### CLI 輸出（進度可見性）
- 執行時在終端機顯示簡單描述，讓使用者知道程式正在運作
- 建議格式：
  ```
  [fetch.py] 找到 2 個 prompts：ai_breakthrough, crypto_market
  [1/2] 執行 ai_breakthrough ...
  [1/2] ✅ 完成 → outputs/ai_breakthrough/20240115_083000.md
  [2/2] 執行 crypto_market ...
  [2/2] ❌ 失敗（retry 1/3）...
  [2/2] ✅ 完成（retry 2/3）→ outputs/crypto_market/20240115_083005.md
  [fetch.py] 全部完成。成功 2 / 失敗 0
  ```
- 使用 `print()` 即可，MVP 不需要 logging 框架

---

## 專案結構

```
twitter-fetch/
├── configs/                 # 主題配置文件（一個主題一個檔案）
│   ├── ai_breakthrough.yaml
│   └── crypto_market.yaml
│
├── prompts/                 # 生成的 prompts（手動管理）
│   ├── ai_breakthrough.md
│   └── crypto_market.md
│
├── outputs/                 # 收集結果（與 prompts 同名對應）
│   ├── ai_breakthrough/     # 同編號對應同主題
│   │   ├── 20240115_083000.md   # 含時間戳的收集結果
│   │   ├── 20240115_143000.md   # 多次執行不覆蓋
│   │   └── 20240116_090000.md
│   └── crypto_market/
│       └── ...
│
├── logs/                    # 執行日誌
│
├── prompt_factory.py        # 一次性工具：config → prompt
├── fetch.py                 # 執行入口
├── requirements.txt
└── README.md
```

---

## 工作流程

### 新增主題時（使用 prompt_factory）

```bash
# 1. 創建或編輯配置檔
vim configs/ai_breakthrough.yaml

# 2. 執行工廠，生成對應的 prompt
python prompt_factory.py --config ai_breakthrough
# 自動讀取 configs/ai_breakthrough.yaml → 生成 prompts/ai_breakthrough.md

# 3. 檢查生成的 prompts/ai_breakthrough.md，手動微調（如需）
# 4. 之後 prompt_factory.py 可以收起來，直到需要新增主題
```

### 每日收集（核心使用流程）

```bash
# 執行所有 prompts（預設行為）
python fetch.py

# 只執行特定 prompt（debug/優化時使用）
python fetch.py --prompt ai_breakthrough

# 執行多個指定 prompts
python fetch.py --prompt ai_breakthrough,crypto_market
```

檔案命名：`outputs/{topic_id}/{YYYYMMDD}_{HHMMSS}.md`

---

## 配置文件設計

### configs/ai_breakthrough.yaml

```yaml
# 主題識別碼（用於檔名、資料夾名）
id: "ai_breakthrough"

# 搜尋策略
search:
  tool: "keyword"       # keyword (精準) 或 semantic (語意)
  mode: "Latest"        # Top (熱門) 或 Latest (最新時間排序)
  limit: 15             # 預期返回推文數量
  query: |
    (artificial intelligence OR AI OR "machine learning")
    (breakthrough OR release OR announced OR launched)
    min_faves:100
    -filter:replies
    lang:en OR lang:zh

# 內容篩選說明
filter:
  include: "官方公告、技術論文、有數據或截圖佐證的消息、知名研究者分享"
  exclude: "價格炒作、加密貨幣相關、無根據謠言、純粹的產品廣告"

# 輸出格式要求
output:
  format: |
    請以結構化 JSON 格式返回，每條推文包含以下欄位：
    - author: 作者顯示名稱
    - username: @用戶名（不含@）
    - time: 發布時間（ISO 8601 格式）
    - content: 推文完整內容（保留原始文字，包含連結）
    - url: 推文永久連結
    - engagement: {likes: 數量, retweets: 數量, replies: 數量}
    - relevance_note: 簡短說明為何符合此主題（1-2句）
```

---

## prompt_factory.py 設計

### 功能

- 讀取 `configs/{id}.yaml`
- 生成對應的 `prompts/{id}.md`
- **一次性執行**，針對單一配置檔

### 使用方式

```bash
# 基本用法（使用 ID）
python prompt_factory.py --config ai_breakthrough
# 自動讀取 configs/ai_breakthrough.yaml → 生成 prompts/ai_breakthrough.md

# 指定輸入輸出路徑（若檔案不在預設位置）
python prompt_factory.py --config ./my_configs/custom.yaml --output ./my_prompts/custom.md

# 預覽模式（不實際寫入）
python prompt_factory.py --config ai_breakthrough --dry-run
```

### 生成的 prompt.md 範例

```markdown
# X Search 任務：AI 重大突破

## 任務說明
請使用 X (Twitter) 的搜尋功能，幫我收集符合以下條件的推文。

## 搜尋策略
- **工具類型**：Keyword Search
- **排序模式**：Latest
- **數量限制**：15 條相關推文

## 搜尋條件
```
(artificial intelligence OR AI OR "machine learning")
(breakthrough OR release OR announced OR launched)
min_faves:100
-filter:replies
lang:en OR lang:zh
```

## 內容篩選

### 優先收錄
官方公告、技術論文、有數據或截圖佐證的消息、知名研究者分享

### 排除內容
價格炒作、加密貨幣相關、無根據謠言、純粹的產品廣告

## 輸出格式
請以結構化 JSON 格式返回，每條推文包含以下欄位：
- author: 作者顯示名稱
- username: @用戶名（不含@）
- time: 發布時間（ISO 8601 格式）
- content: 推文完整內容（保留原始文字，包含連結）
- url: 推文永久連結
- engagement: {likes: 數量, retweets: 數量, replies: 數量}
- relevance_note: 簡短說明為何符合此主題（1-2句）

## 注意事項
1. 請確保資訊準確，包含正確的推文連結
2. 如果找到的推文不足 15 條，請說明原因
3. 如果沒有找到符合條件的推文，請明確告知
4. 優先選擇互動數較高（按讚、轉推多）的內容

```

---

## fetch.py 設計

### 功能

- 讀取指定的 `prompt.md`
- 呼叫 xAI API
- 將結果寫入 `outputs/{topic_id}/{YYYYMMDD}_{HHMMSS}.md`（含時間戳，不覆蓋舊檔案）

### 命令列介面

```bash
# 執行所有 prompts（預設行為，生產環境使用）
python fetch.py

# 只執行特定 prompt（debug/優化時使用）
python fetch.py --prompt ai_breakthrough

# 執行多個指定 prompts
python fetch.py --prompt ai_breakthrough,crypto_market

# 預覽模式（顯示會做什麼，但不實際執行）
python fetch.py --dry-run
```

### 輸出格式範例

#### outputs/ai_breakthrough/20240115_083000.md

```markdown
---
topic: "ai_breakthrough"
executed_at: "2024-01-15T08:30:00+08:00"
status: "success"
---

# Grok 檢索結果（可能是 Markdown 列表、JSON、或自然語言描述）

---

```json
[
  {
    "author": "OpenAI",
    "username": "OpenAI",
    "content": "We are launching GPT-5...",
    "url": "https://x.com/OpenAI/status/123456789"
  }
]
```

或：

1. **@OpenAI**: We are launching GPT-5... (https://x.com/OpenAI/status/123456789)
2. **@sama**: Excited about the new model... (https://x.com/sama/status/...)

---

## 典型使用場景

### 場景 1：新增主題

```bash
# 1. 創建配置
vim configs/new_topic.yaml

# 2. 生成 prompt（使用相同 ID）
python prompt_factory.py --config new_topic

# 3. 檢查並微調
vim prompts/new_topic.md

# 4. 測試執行（使用相同 ID）
python fetch.py --prompt new_topic
```

### 場景 2：日常收集

```bash
# 收集所有 prompts（預設）
python fetch.py

# 只收集特定主題（debug/測試）
python fetch.py --prompt ai_breakthrough

# 收集多個指定主題
python fetch.py --prompt ai_breakthrough,crypto_market
```

### 場景 3：高頻收集

因檔名含時間戳，可多次執行不覆蓋：

```bash
# 早上收集一次
python fetch.py

# 下午再次收集（新時間戳，獨立檔案）
python fetch.py

# outputs/ai_breakthrough/ 目錄下會有：
# - 20240115_083000.md
# - 20240115_143000.md
```

### 場景 4：Prompt 優化

```bash
# 發現效果不好，直接編輯 prompt
vim prompts/ai_breakthrough.md

# 單獨執行測試（不影響其他 prompts）
python fetch.py --prompt ai_breakthrough
```

---

