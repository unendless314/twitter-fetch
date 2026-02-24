# X Search 任務：crypto_institutional_hybrid

## 任務說明
請使用 X (Twitter) 的搜尋功能，幫我收集符合以下條件的推文。

## 搜尋策略
- **工具類型**：Hybrid Search
- **排序模式**：Latest
- **數量限制**：10 條相關推文

## 搜尋條件

### 查詢主體（Hybrid Search）
```
目標：
尋找比特幣和以太坊的機構級發展，包括 ETF 資金流向、監管政策進展、
協議升級（如質押和 Layer 2 擴展）、企業財庫採用案例，
以及加密資產作為資產類別的宏觀分析。
聚焦於已建立聲譽的加密機構研究、監管文件和基本面鏈上指標。

推薦檢索策略：
- 核心資產：(Bitcoin OR BTC OR Ethereum OR ETH OR "crypto ETF")
- 機構/技術：(institutional OR ETF OR adoption OR regulation OR halving OR "layer 2" OR upgrade OR staking OR "spot ETF" OR inflow OR outflow OR "hash rate")
- 排除條件：-airdrop -gem -"100x" -scam -memecoin -shitcoin

若上述 keywords 未找到合適結果，可依據「目標描述」擴大或調整搜尋方向，但務必嚴格遵守排除條件。
```

### 條件參數
- `min_faves:80`（互動門檻）
- `lang:en OR lang:zh`（語言過濾）


## 內容篩選

### 優先收錄
機構資金流向、ETF 申購贖回數據、監管政策進展、協議技術升級、
大型企業採用案例、鏈上基本面分析、機構研究報告、
監管政策解讀、ETF 資金流向分析、協議基本面數據、
企業採用案例、宏觀資產配置觀點

### 排除內容
散戶喊盤、垃圾幣推廣、詐騙項目、
散戶投機討論、無根據傳言、詐騙項目推廣、
過度簡化的投資建議

## 輸出格式
請以結構化 JSON 格式返回，每條推文包含以下欄位：
- author: 作者顯示名稱
- username: @用戶名（不含@）
- time: 發布時間（ISO 8601 格式，含時區，例如 2026-02-23T14:30:00Z）
- content: 推文完整內容（保留原始文字，包含連結）
- url: 推文永久連結（格式：https://x.com/username/status/post_id）
- engagement: {likes: 數量, retweets: 數量, replies: 數量}
- media_urls: 推文中的圖片或影片連結陣列（無媒體則為空陣列 []）
- relevance_note: 簡短說明為何符合此主題（1-2句，請說明與機構級加密資產的關聯性）

## 注意事項
1. 請確保資訊準確，包含正確的推文連結
2. 如果找到的推文不足 10 條，請說明原因
3. 如果沒有找到符合條件的推文，請明確告知
4. 優先選擇互動數較高（按讚、轉推多）的內容
