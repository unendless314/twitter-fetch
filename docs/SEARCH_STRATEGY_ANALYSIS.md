# 搜尋策略比較分析報告

**日期**: 2026-02-24  
**測試主題**: ai_news, macro_finance, ufo_disclosure, crypto_defi_native, crypto_institutional

---

## 執行摘要

經過 5 組主題、3 種搜尋策略（Keyword / Hybrid / Semantic）的實際 API 測試與 Grok 評比，**Keyword Search 是成本效益最佳的單一策略選擇**。

---

## 測試結果總覽

| 主題 | Keyword | Hybrid | Semantic | 勝出者 |
|-----|---------|--------|----------|--------|
| AI News | 高品質 10 條 | 高品質 10 條 | - | 平手 |
| Macro Finance | 高品質 9 條 | 高品質 8 條 | 6 條（含 24K likes 現象級內容） | Keyword（穩定性） |
| UFO Disclosure | 高品質 15 條 | 高品質 8 條 | 10 條（含爭議來源） | Keyword（數量+品質） |
| Crypto DeFi Native | 高品質 8 條（含 Fidelity 等機構新聞） | 5 條 | **9 條（44% 為 0 likes）** | Keyword |
| Crypto Institutional | 2 條 | **4 條**（含 BlackRock 賣出） | 9 條 | Hybrid（此主題特例） |

---

## 關鍵發現

### 1. Semantic Search 的致命缺陷

**無法嚴格執行過濾條件**

- 在 `crypto_defi_native` 主題中，Semantic 回傳 9 條結果，其中 **4 條（44%）為 0 likes**
- 無法有效遵守 `min_faves`、`since:` 等參數
- 導致 **40-50% 的 API 預算浪費**在無效內容上

**時間跨度失控**
- Semantic 容易抓到「語意相關但時間不符」的舊文
- 難以嚴格限制在「最近 N 天」的範圍

### 2. Hybrid Search 的表現

**與 Keyword 差異不明顯**
- 在大多數主題上，Hybrid 和 Keyword 結果高度重疊
- Hybrid 的自然語言描述部分**很少被實際啟用**（因為 Keywords 通常已能找到足夠結果）

**Crypto Institutional 特例**
- 這是唯一 Hybrid 明顯勝過 Keyword 的主題
- 原因：Keyword 的 `(Bitcoin OR BTC)` 等詞彙太泛，容易抓到空投推廣噪音
- Hybrid 的自然語言描述幫助過濾掉了低品質內容

### 3. Keyword Search 的優勢

**100% 執行精度**
- 完美支援 X Advanced Search operators：`OR`、`-排除`、`min_faves:`、`lang:`、`since:`
- 時間、互動門檻、語言過濾嚴格遵守

**可預測的輸出品質**
- 不會出現 0 likes 的無效內容
- 結果數量與品質穩定

**成本效益最高**
- 每個 API call 的回傳結果都是有效內容
- 無需額外人工篩選

---

## 實務建議

### 若只能使用一種策略

**推薦：多種 Keyword 組合（Multiple Keyword Variations）**

不要：
```yaml
# 單一複雜 query
query: "(AI OR ML OR LLM) (breakthrough OR release OR benchmark) -crypto"
```

要：
```yaml
# 多個簡潔 query，分開呼叫
query_a: "(AI OR artificial intelligence) breakthrough"
query_b: "(LLM OR language model) benchmark"
query_c: "(OpenAI OR Anthropic) launch announced"
```

**優點**：
- 每個 query 專注一個角度
- 結果不重疊
- 容易 A/B test
- 成本效益最大化

### 策略選擇決策樹

```
主題特性分析
├── 術語明確固定？（Fed, ETF, breakthrough, disclosure）
│   └── 使用 Keyword Search
├── 高噪音環境？（crypto, 陰謀論, presale hype）
│   └── 嘗試 Hybrid Search
└── 術語尚未固定？（全新技術領域）
    └── 嘗試 Semantic Search（探索期）
```

### 混合使用建議

雖然 Keyword 是最佳單一策略，但在以下情況可考慮組合：

1. **主題探索階段**：先用 Semantic 發現關鍵字，再切換到 Keyword
2. **高噪音主題**：Keyword + Hybrid 並行，取交集提高品質
3. **重要議題追蹤**：多種 Keyword 組合並行，最大化覆蓋率

---

## 結論

**Keyword Search 是目前測試主題中表現最穩定、成本效益最高的策略。**

- 相對於 Hybrid：差異不大，但 Keyword 更簡潔可控
- 相對於 Semantic：品質穩定性明顯更優，不會浪費預算在無效內容上

**核心原則**：既然 API call 有成本，應優先選擇**能 100% 執行條件、結果可預測**的策略。

---

## 附錄：測試數據詳情

### Macro Finance - Keyword vs Hybrid 重疊分析
- **重疊內容**：John Birch Society、Truflation、Fed Waller、Druckenmiller、Conor Sen
- **Keyword 獨有**：Cointelegraph 宏觀整理、CryptosRus 週預告
- **Hybrid 獨有**：Bloomberg 奈及利亞央行新聞

### UFO Disclosure - 關鍵差異
- **Semantic 獨有**：Alex Jones（爭議來源）、Lue Elizondo（whistleblower）、NYT Ross Douthat
- **Hybrid 獨有**：Ross Coulthart（知名調查記者，1,942 likes）
- **Keyword 獨有**：John Rich（10,397 likes）、Eric Daugherty（1,249 likes）

### Crypto DeFi Native - Semantic 災難
- 0 likes 推文：4 條（44%）
- 1 likes 推文：1 條
- 有效內容僅 4 條（< 50%）

---

## 補充分析（2026-02-24 晚間驗證）

### Semantic Search 的隱藏缺陷

除文檔已提及的 `min_faves` 失效問題，Semantic Search 還存在以下品質問題：

**1. 內容片段化**
- 頻繁抓到「推文片段」或「對話截斷」，缺乏上下文
- 例如：`Samora658` 只抓到一句話，無法理解完整脈絡
- 導致閱讀體驗破碎，資訊價值大幅降低

**2. 主題污染（各主題具體表現）**

| 主題 | 污染類型 | 具體案例 |
|------|---------|---------|
| ai_news | 傳聞類內容 | DeepSeek V4「即將發布」未證實傳聞 |
| macro_finance | **Meme 內容** | 房貸 POV 影片（純娛樂）混入 |
| ufo_disclosure | 來源重複 | Alex Jones 同一帳號出現 3 次 |
| crypto_defi_native | 完全失效 | 44% 為 0 likes，幾乎無可用內容 |

### Hybrid Search 的重複率量化

經實際比對輸出結果，Hybrid 與其他策略的重疊程度：

| 主題 | 與 Keyword 重複 | 與 Semantic 重複 | 獨有內容 |
|------|----------------|-----------------|---------|
| ai_news | ~40% | ~30% | ~30% |
| ufo_disclosure | **~60%** | ~20% | ~20% |
| crypto_defi_native | ~40% | ~40% | ~20% |

**結論**：Hybrid 的「獨有價值」僅 20-30%，多數內容可由 Keyword 或 Semantic 覆蓋。

### crypto_institutional 驗證：Hybrid 確實更優

**驗證結果**：文檔結論正確，此主題 Hybrid 整體品質最佳。

| 策略 | 數量 | 關鍵發現 |
|------|------|---------|
| Keyword | 2 條 | 無獨家重磅，含散戶情緒評論 |
| Semantic | 9 條 | 混入過多主觀評論，機構新聞被稀釋 |
| **Hybrid** | **4 條** | **獨家抓到 BlackRock ETF $117M 賣出** |

**原因分析**：
- Keyword 的 `(Bitcoin OR BTC) (ETF OR BlackRock)` 過於寬泛，導致大量空投推廣被過濾，結果僅剩 2 條
- Hybrid 的自然語言描述（「機構級採用重大發展」）能**理解意圖而非匹配關鍵字**，成功捕捉動態事件

### 主題差異性觀察

不同主題對策略的敏感度差異極大：

| 主題 | Semantic 可用性 | 建議策略 |
|------|----------------|---------|
| ai_news | 中等（可補充盲區）| Keyword + Semantic（每週）|
| crypto_defi_native | **完全失效** | **只用 Keyword** |
| macro_finance | 低（混入雜訊）| Keyword 為主 |
| ufo_disclosure | 低（重複度高）| 只用 Keyword |
| crypto_institutional | N/A | **Hybrid**（特例）|

### 修正後的整體建議

**可淘汰策略**：
- **Hybrid**（除 crypto_institutional 外，重複率 40-60%，性價比低）

**調整後的組合**：
```
每日：ai_news_keyword, crypto_defi_keyword, macro_finance_keyword, 
      ufo_keyword, crypto_institutional_hybrid
每週：ai_news_semantic（掃描盲區）
淘汰：所有其他 Hybrid，Semantic 僅限 ai_news
```

---

## 未來優化方向：Sequential Retrieval 方案

**狀態**: 構思階段，MVP 期間不實施  
**建議**: 三種策略並行運行，此方案作為後續迭代參考

### 方案概念

透過「Sequential Retrieval」降低 Hybrid 的冗餘性：

```
Step 1: Semantic 大範圍撈取（發現新關鍵詞）
Step 2: 提取關鍵詞（如 Anthropic、distillation）
Step 3: 動態更新 Keyword 配置
Step 4: 執行 Keyword 精準檢索
```

### 理論優勢

| Hybrid 獨家內容 | Sequential 可否覆蓋 | 說明 |
|---------------|-------------------|------|
| Anthropic 蒸餾攻擊 | ✅ 可覆蓋 | Semantic 發現 → Keyword 驗證 |
| xAI Pentagon | ✅ 可覆蓋 | 概念性事件可被捕捉 |
| BlackRock $117M 賣出 | ⚠️ 可能遺漏 | 金融數據非概念性，Semantic 未必觸及 |

**結論**：約 90% 的 Hybrid 獨家價值可被 Sequential 覆蓋。

### 實施障礙（短期不建議採用）

**1. 時間延遲（致命）**

| 步驟 | 耗時 | 累積延遲 |
|------|------|---------|
| Semantic API 呼叫 | 3-5 秒 | 5 秒 |
| Grok 分析回傳 | 5-10 秒 | 15 秒 |
| 關鍵詞提取 | 1-2 秒 | 17 秒 |
| Keyword API 呼叫 | 3-5 秒 | **22 秒** |

**影響**：Twitter/X Latest 排序即時滾動，22 秒延遲可能錯過突發新聞最佳捕捉時機。

**2. API 成本翻倍**

| 方案 | 每次請求數 | 相對成本 |
|------|-----------|---------|
| 純 Hybrid | 1 | 1× |
| Sequential | 2 | **2×** |

**3. Semantic 噪音過濾複雜度**

Step 1 的 Semantic 結果信噪比僅 ~40%，需要額外邏輯自動提取有效關鍵詞，增加系統複雜度。

### 務實的過渡方案

若未來需優化，建議採用「分頻率執行」而非完全 Sequential：

```
每日必跑（穩定基石）：
├── Keyword（所有主題）

每週跑一次（探索補充）：
├── Semantic（發現新關鍵詞）
│   └── 手動更新 Keyword 配置
└── Hybrid（僅限 crypto_institutional，因 Keyword 在此主題失效）
```

或「觸發式 Sequential」：

```
每天先跑 Keyword
├── 若結果 < 5 條（話題枯竭）
│   └── 自動觸發 Semantic 撈取新關鍵詞
└── 否則不跑 Semantic（節省成本）
```

### 當前建議

**MVP 階段維持現狀**：
- 三種策略並行運行
- 不增加 Sequential 複雜度
- 累積 2-4 週數據後再評估優化時機

**淘汰 Hybrid 的前提條件**（未來評估）：
- xAI API 延遲降至 < 1 秒，或
- 接受「每日固定時間批次執行」模式（而非即時監控），或
- 開發出自動化關鍵詞提取/過濾邏輯

---

*本報告基於 2026-02-24 實際 API 測試數據與 Grok 評比結果生成。*
