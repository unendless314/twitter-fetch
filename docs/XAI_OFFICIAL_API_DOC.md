# xAI X Search 官方 API 文檔

> 來源：https://docs.x.ai/developers/tools/x-search  
> 抓取時間：2024年  
> 用途：了解官方 API 暴露的參數與使用方式

---

## 概述

X Search 工具讓 Grok 能夠在 X（Twitter）上執行：
- 關鍵字搜尋（keyword search）
- 語意搜尋（semantic search）
- 用戶搜尋（user search）
- 串文抓取（thread fetch）

此工具讓模型可以存取即時社交媒體內容、分析貼文，並從 X 的海量資料中獲取洞察。

---

## SDK 支援

| SDK/API | Tool 名稱 |
|---------|----------|
| xAI SDK | `x_search` |
| OpenAI Responses API | `x_search` |
| Vercel AI SDK | `xai.tools.xSearch()` |

此工具也支援所有 Responses API 相容的 SDK。

---

## 基本使用範例

```python
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import x_search

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",  # reasoning model
    tools=[x_search()],
    include=["verbose_streaming"],
)

chat.append(user("What are people saying about xAI on X?"))

is_thinking = True
for response, chunk in chat.stream():
    for tool_call in chunk.tool_calls:
        print(f"\nCalling tool: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
    if response.usage.reasoning_tokens and is_thinking:
        print(f"\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
    if chunk.content and is_thinking:
        print("\n\nFinal Response:")
        is_thinking = False
    if chunk.content and not is_thinking:
        print(chunk.content, end="", flush=True)

print("\n\nCitations:")
print(response.citations)
```

---

## X Search 參數

| 參數 | 說明 |
|------|------|
| `allowed_x_handles` | 只考慮來自特定 X 帳號的貼文（最多 10 個） |
| `excluded_x_handles` | 排除特定 X 帳號的貼文（最多 10 個） |
| `from_date` | 搜尋範圍起始日期（ISO8601 格式） |
| `to_date` | 搜尋範圍結束日期（ISO8601 格式） |
| `enable_image_understanding` | 啟用貼文中圖片的分析 |
| `enable_video_understanding` | 啟用貼文中影片的分析 |

---

## 參數詳細說明

### 只考慮特定帳號的貼文

使用 `allowed_x_handles` 來限制只搜尋特定 X 帳號的貼文。最多可包含 10 個帳號。

**限制：** `allowed_x_handles` 不能與 `excluded_x_handles` 同時設定。

```python
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import x_search

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        x_search(allowed_x_handles=["elonmusk"]),
    ],
)

chat.append(user("What is the current status of xAI?"))
# stream or sample the response...
```

### 排除特定帳號的貼文

使用 `excluded_x_handles` 來排除特定帳號的貼文。最多可排除 10 個帳號。

```python
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        x_search(excluded_x_handles=["elonmusk"]),
    ],
)
```

### 日期範圍

可透過 `from_date` 和 `to_date` 限制搜尋資料的日期範圍。範圍包含起始和結束日期。

兩個欄位需使用 ISO8601 格式，例如 `"YYYY-MM-DD"`。若使用 xAI Python SDK，`from_date` 和 `to_date` 可以傳入 `datetime.datetime` 物件。

```python
import os
from datetime import datetime

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import x_search

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        x_search(
            from_date=datetime(2025, 10, 1),
            to_date=datetime(2025, 10, 10),
        ),
    ],
)

chat.append(user("What is the current status of xAI?"))
# stream or sample the response...
```

### 啟用圖片理解

將 `enable_image_understanding` 設為 true，讓 agent 能夠分析搜尋過程中遇到的 X 貼文中的圖片。

```python
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        x_search(enable_image_understanding=True),
    ],
)
```

### 啟用影片理解

將 `enable_video_understanding` 設為 true，讓 agent 能夠分析 X 貼文中的影片。此功能僅適用於 X Search（不適用於 Web Search）。

```python
chat = client.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        x_search(enable_video_understanding=True),
    ],
)
```

---

## 引用（Citations）

關於如何取得和使用搜尋結果的引用資訊，請參閱 Citations 頁面。

---

## 與 Grok 內部能力的對比分析

### 官方 API 暴露的參數（極度有限）

| 參數 | 類型 | 限制 |
|------|------|------|
| `allowed_x_handles` | 帳號白名單 | 最多 10 個 |
| `excluded_x_handles` | 帳號黑名單 | 最多 10 個 |
| `from_date` / `to_date` | 日期範圍 | ISO8601 格式 |
| `enable_image_understanding` | 圖片分析 | 開關 |
| `enable_video_understanding` | 影片分析 | 開關 |

### 官方 API **沒有**暴露的參數（但 Grok 內部支援）

| 功能 | 說明 |
|------|------|
| `query` 進階運算子 | `min_faves:`, `min_retweets:`, `filter:images`, `lang:`, `from:`, `to:` 等 |
| `mode` | `Top` / `Latest` 排序切換 |
| `limit` | 回傳貼文數量控制 |
| `min_score_threshold` | 語意搜尋相關度門檻 |
| `Semantic Search` | 明確的語意搜尋模式選擇 |

---

## 關鍵洞察：Prompt-Driven 控制

### 核心發現

官方 API 參數極度精簡，但 **Grok 作為 Agent 可以透過 Prompt 理解並執行更複雜的搜尋策略**。

這意味著：

```python
# 官方 API 層面 - 只能設定這些
x_search(
    allowed_x_handles=["elonmusk"],
    from_date=datetime(2025, 1, 1),
    to_date=datetime(2025, 1, 31),
)

# 但 Prompt 層面 - 可以指導 Grok 這樣做：
user_prompt = """
請使用 X Keyword Search 搜尋 @elonmusk 在 2025年1月的貼文，
設定條件：
- mode: Latest（按時間排序）
- limit: 20
- query: from:elonmusk -filter:replies min_faves:1000
- 只關注與 AI 相關的內容

請以結構化格式返回結果。
"""
```

### 運作機制推測

1. **API 層**：只是告訴 Grok「你可以使用 X Search 工具」
2. **Prompt 層**：使用者用自然語言描述想要的搜尋策略
3. **Agent 層**：Grok 理解意圖後，調用內部完整的 X Search 能力（包含未暴露的參數）
4. **執行層**：實際使用 Keyword Search 或 Semantic Search，並套用指定的參數

### 這種設計的優缺點

| 優點 | 缺點 |
|------|------|
| 彈性極高，可用自然語言描述複雜需求 | 結果的可重現性較低（取決於 Grok 的理解） |
| 無需學習複雜的 API 參數 | 無法精確控制底層參數 |
| 可利用 Grok 的推理能力優化搜尋 | 可能需要反覆調整 Prompt 才能達到理想效果 |
| 可混合多種搜尋策略（Keyword + Semantic） | 成本較難預估（ reasoning tokens ） |

---

## 對本專案的設計啟示

### Prompt 設計將是核心競爭力

由於官方 API 參數極度有限，**Prompt 的設計品質直接決定資料收集的品質**。

建議的 Prompt 結構：

```markdown
## 任務類型
[Keyword Search / Semantic Search / 混合]

## 搜尋目標
[主題描述]

## 技術參數
- mode: [Top / Latest]
- limit: [數量]
- query: [進階搜尋語法]
- 時間範圍: [日期]

## 內容篩選
[品質標準、排除條件、優先順序]

## 輸出格式
[結構化要求]
```

### 需要測試的關鍵問題

1. Grok 是否總是遵從 Prompt 中指定的搜尋策略？
2. 同樣的 Prompt 多次執行，結果一致性如何？
3. 如何驗證 Grok 確實使用了指定的參數（如 min_faves）？
4. reasoning tokens 的使用量與 prompt 複雜度的關係？

---

*文件建立時間：專案研究階段*
*用途：理解官方 API 限制與 Prompt-Driven 控制的可行性*
