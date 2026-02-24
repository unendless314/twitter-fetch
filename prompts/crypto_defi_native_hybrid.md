# X Search 任務：crypto_defi_native_hybrid

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
尋找去中心化金融（DeFi）生態系統的最新發展，包括流動性挖礦策略、
流動性池動態、資金費率套利、智能合約安全性、代幣經濟模型分析、協議治理更新，
以及 TVL、FDV 等鏈上指標變化。
聚焦於專業 DeFi 社群討論，而非純粹的投機交易。

推薦檢索策略：
- DeFi 術語：(DeFi OR "yield farming" OR "liquidity pool" OR vault OR arbitrage OR "funding rate" OR FDV OR TVL OR "buyback" OR DCA OR staking OR whale OR tokenomics OR "smart contract")
- 協議/機制：(protocol OR airdrop OR governance OR "AMM" OR DEX OR APY OR impermanent OR MEV OR memecoin)
- 排除條件：-scam -rug -gem -"100x" -shitcoin -"guaranteed"

若上述 keywords 未找到合適結果，可依據「目標描述」擴大或調整搜尋方向，但務必嚴格遵守排除條件。
```

### 條件參數
- `min_faves:80`（互動門檻）
- `lang:en OR lang:zh`（語言過濾）


## 內容篩選

### 優先收錄
DeFi 協議更新、流動性挖礦策略、資金費率分析、鏈上數據洞察、
智能合約審計結果、代幣經濟模型討論、套利機會分析、巨鯨動向追蹤、
協議經濟模型分析、流動性策略優化、風險調整後收益討論、
治理提案評估、智能合約安全、鏈上數據深度洞察、機構級 DeFi 採用案例

### 排除內容
未經審計的新項目推廣、過度承諾收益、無根據的暴富策略、
Rug Pull 預警以外的恐慌散布、純粹的代幣銷售廣告、
無風險提示的投資建議、純粹的代幣促銷、缺乏數據支撐的觀點

## 輸出格式
請以結構化 JSON 格式返回，每條推文包含以下欄位：
- author: 作者顯示名稱
- username: @用戶名（不含@）
- time: 發布時間（ISO 8601 格式，含時區，例如 2026-02-23T14:30:00Z）
- content: 推文完整內容（保留原始文字，包含連結）
- url: 推文永久連結（格式：https://x.com/username/status/post_id）
- engagement: {likes: 數量, retweets: 數量, replies: 數量}
- media_urls: 推文中的圖片或影片連結陣列（無媒體則為空陣列 []）
- relevance_note: 簡短說明為何符合此主題（1-2句，請說明與 DeFi 原生策略或協議的關聯性）

## 注意事項
1. 請確保資訊準確，包含正確的推文連結
2. 如果找到的推文不足 10 條，請說明原因
3. 如果沒有找到符合條件的推文，請明確告知
4. 優先選擇互動數較高（按讚、轉推多）的內容
