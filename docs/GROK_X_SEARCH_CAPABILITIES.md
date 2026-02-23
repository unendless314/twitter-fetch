# Grok X 搜尋工具能力說明

> 來源：Grok 對話紀錄整理  
> 日期：2024年  
> 用途：了解 Grok 內部 X 搜尋工具與官方 API 的差異

---

## 核心發現

Grok 內部的 X 檢索工具比官方公開的 xAI API **可調整範圍明顯更大、更靈活**，在實戰控制力上更強大。

---

## 一、Grok 內部可用的兩個搜尋工具

### 1. X Keyword Search（關鍵字進階搜尋）

最精確、控制力最強的搜尋方式，支援 Twitter 完整的進階搜尋語法。

#### 參數說明

| 參數名稱 | 說明 | 常見用法舉例 | 是否必填 |
|---------|------|-------------|---------|
| `query` | 搜尋條件字串（支援所有進階運算子） | `(台灣 OR Taiwan) 地震 min_faves:500` | ✅ 必填 |
| `limit` | 想要回傳的貼文數量 | `5`、`10`、`20` | 選填（預設 3） |
| `mode` | 排序方式：`Top`（熱門/演算法推薦）或 `Latest`（最新時間排序） | `Latest` | 選填（頻設 `Top`） |

#### Query 常用調整技巧

| 技巧 | 語法範例 | 說明 |
|------|---------|------|
| 關鍵字組合 | `地震 台南`、`地震 OR 餘震` | AND / OR 邏輯 |
| 精確片語 | `"花式滑冰 金牌"` | 完全匹配的詞組 |
| 排除 | `-中國 -中國人` | 排除特定關鍵字 |
| 來自某人 | `from:ChunChiaoLin` | 特定帳號發文 |
| 提到某人 | `@ChunChiaoLin` | 提及特定帳號 |
| 最小互動數 | `min_faves:1000`、`min_retweets:200` | 按讚/轉推門檻 |
| 時間範圍 | `since:2026-02-01 until:2026-02-23` | 日期區間 |
| 媒體類型 | `filter:images`、`filter:videos`、`filter:news` | 內容類型過濾 |
| 語言 | `lang:zh`、`lang:en` | 語言限制 |
| 回覆/引用/串文 | `filter:replies`、`-filter:replies`、`conversation_id:123456789` | 互動類型過濾 |

---

### 2. X Semantic Search（語意搜尋）

用 AI 理解「你想找什麼意思」，適合找主題相關但關鍵字不完全一樣的貼文。

#### 參數說明

| 參數名稱 | 說明 | 常見用法舉例 | 是否必填 |
|---------|------|-------------|---------|
| `query` | 你想找的主題描述（自然語言） | `「台南最近的地震感受與討論」` | ✅ 必填 |
| `limit` | 回傳貼文數量 | `5`、`10`、`15` | 選填（預設 3） |
| `from_date` | 從哪一天開始（格式：YYYY-MM-DD） | `2026-02-01` | 選填 |
| `to_date` | 到哪一天結束（格式：YYYY-MM-DD） | `2026-02-23` | 選填 |
| `exclude_usernames` | 排除特定帳號（陣列） | `["BBCNews", "CNN"]` | 選填 |
| `usernames` | 只看特定帳號（陣列） | `["ChunChiaoLin", "pthaiwan"]` | 選填 |
| `min_score_threshold` | 相關度門檻（0~1，越高越嚴格，預設 0.18） | `0.25` | 選填 |

---

## 二、使用建議

| 場景 | 推薦工具 | 原因 |
|------|---------|------|
| 精準找某個關鍵字、某人、某時間、某互動門檻 | **Keyword Search** | 控制力最強 |
| 找「大概這個意思」的討論、氛圍、相關話題 | **Semantic Search** | AI 理解意圖 |
| 綜合策略 | **兩者搭配** | 先用 Semantic 找大方向，再用 Keyword 縮小範圍 |

---

## 三、與官方 API 的比較

### 官方 xAI API 文檔中的 X Search（公開版本）

根據 [官方文件](https://docs.x.ai/developers/tools/x-search#x-search-parameters)，公開 API 只暴露非常有限的參數：

- `allowed_x_handles`（只看特定帳號，最多 10 個）
- `excluded_x_handles`（排除特定帳號，最多 10 個）
- `from_date` / `to_date`（日期範圍）
- `enable_image_understanding` / `enable_video_understanding`（圖片/影片理解開關）

**限制：** 完全沒有 query 字串、沒有 mode（Top/Latest）、沒有 min_score_threshold、沒有 min_faves/min_retweets 等進階過濾。

官方版本更像是給外部開發者用的「簡化安全版」，功能被大幅收斂。

### 詳細比較表

| 項目 | 官方 xAI API（公開） | Grok 內部工具 | 誰更強？ |
|------|-------------------|-------------|---------|
| 關鍵字進階運算子 | ❌ 不支援 | ✅ 完整支援（幾乎所有 Twitter 語法） | Grok 遠勝 |
| 熱門/最新排序 | ❌ 無 | ✅ 有（Top / Latest） | Grok 有 |
| 互動數門檻（讚/轉推） | ❌ 無 | ✅ 有（min_faves:、min_retweets:） | Grok 有 |
| 語意搜尋 + 相關度調節 | ❌ 無（只有基本日期/帳號） | ✅ 有 + min_score_threshold | Grok 遠勝 |
| 帳號過濾上限 | 最多 10 個 | 較鬆（實務上可更多） | Grok 較鬆 |
| 媒體/語言/回覆過濾 | ❌ 無 | ✅ 有（filter:、lang: 等） | Grok 有 |

---

## 四、結論

Grok 的檢索工具在**可調整範圍**和**精細度**上，比官方公開 API 強非常多。

- **官方版**：給第三方開發者的「安全玩具版」
- **Grok 內部版**：接近原始 Twitter 資料管道的完整版本，能做到更精準、更即時、更多樣的過濾與排序

---

## 五、對本專案的影響

### 重要發現

1. **Prompt 策略需要調整**：
   - 由於 Grok 內部工具比官方 API 強大，Prompt 中可以直接要求使用特定參數
   - 例如：「使用 Keyword Search，設定 limit=10，mode=Latest，query 包含 min_faves:100」

2. **兩種搜尋方式的選擇**：
   - 精準主題追蹤 → Keyword Search
   - 探索性/氛圍收集 → Semantic Search

3. **無法直接呼叫**：
   - 重要：這些內部工具參數**無法透過官方 API 直接指定**
   - 必須透過自然語言 Prompt 告訴 Grok 使用特定設定
   - 這增加了收集結果的不可控性（取決於 Grok 是否正確理解並執行）

---

*文件建立時間：專案初期研究階段*
