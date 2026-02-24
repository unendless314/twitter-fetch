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

*本報告基於 2026-02-24 實際 API 測試數據與 Grok 評比結果生成。*
