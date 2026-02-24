# X Search 任務：macro_finance_hybrid

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
尋找全球總體經濟發展、央行政策轉向、利率決策、通膨趨勢、債券市場動態、
匯率波動及其對金融市場的影響。聚焦於機構投資者、經濟學家和金融分析師
對宏觀主題的專業討論，而非個股推薦。

推薦檢索策略：
- 宏觀主體：(macro OR "monetary policy" OR "interest rate" OR Fed OR ECB OR "central bank")
- 市場指標：("bond yield" OR "yield curve" OR inflation OR recession OR "GDP growth" OR FX OR forex OR commodity)
- 排除條件：-crypto -bitcoin -ethereum -nft -defi -airdrop

若上述 keywords 未找到合適結果，可依據「目標描述」擴大或調整搜尋方向，但務必嚴格遵守排除條件。
```

### 條件參數
- `min_faves:50`（互動門檻）
- `lang:en OR lang:zh`（語言過濾）


## 內容篩選

### 優先收錄
央行政策聲明、總體經濟數據發布、利率決策分析、債券市場動態、
匯率與大宗商品走勢、知名經濟學家觀點、全球總體經濟趨勢、
央行政策轉向信號、通膨與就業數據解讀、機構投資者宏觀觀點、
跨資產類別的連動分析

### 排除內容
加密貨幣價格預測、個股推薦、個股或個別公司分析、
純技術分析、純技術指標討論、無根據的市場謠言、
未經證實的市場傳言、投資廣告、投資組合廣告

## 輸出格式
請以結構化 JSON 格式返回，每條推文包含以下欄位：
- author: 作者顯示名稱
- username: @用戶名（不含@）
- time: 發布時間（ISO 8601 格式，含時區，例如 2026-02-23T14:30:00Z）
- content: 推文完整內容（保留原始文字，包含連結）
- url: 推文永久連結（格式：https://x.com/username/status/post_id）
- engagement: {likes: 數量, retweets: 數量, replies: 數量}
- media_urls: 推文中的圖片或影片連結陣列（無媒體則為空陣列 []）
- relevance_note: 簡短說明為何符合此主題（1-2句，請說明與宏觀金融的關聯性）

## 注意事項
1. 請確保資訊準確，包含正確的推文連結
2. 如果找到的推文不足 10 條，請說明原因
3. 如果沒有找到符合條件的推文，請明確告知
4. 優先選擇互動數較高（按讚、轉推多）的內容
