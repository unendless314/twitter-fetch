# X Search 任務：ai_news_keyword

## 任務說明
請使用 X (Twitter) 的搜尋功能，幫我收集符合以下條件的推文。

## 搜尋策略
- **工具類型**：Keyword Search
- **排序模式**：Latest
- **數量限制**：10 條相關推文

## 搜尋條件

### 查詢主體（Keyword Search）
```
(artificial intelligence OR AI OR "machine learning")
(breakthrough OR release OR announced OR launched OR benchmark)
-crypto -blockchain -token -coin -nft
```

### 條件參數
- `min_faves:100`（互動門檻）
- `lang:en OR lang:zh`（語言過濾）


## 內容篩選

### 優先收錄
官方公告、技術論文、有數據或截圖佐證的消息、知名研究者分享

### 排除內容
價格炒作、加密貨幣相關、無根據謠言、純粹的產品廣告

## 輸出格式
請以結構化 JSON 格式返回，每條推文包含以下欄位：
- author: 作者顯示名稱
- username: @用戶名（不含@）
- time: 發布時間（ISO 8601 格式，含時區，例如 2026-02-23T14:30:00Z）
- content: 推文完整內容（保留原始文字，包含連結）
- url: 推文永久連結（格式：https://x.com/username/status/post_id）
- engagement: {likes: 數量, retweets: 數量, replies: 數量}
- media_urls: 推文中的圖片或影片連結陣列（無媒體則為空陣列 []）
- relevance_note: 簡短說明為何符合此主題（1-2句）

## 注意事項
1. 請確保資訊準確，包含正確的推文連結
2. 如果找到的推文不足 10 條，請說明原因
3. 如果沒有找到符合條件的推文，請明確告知
4. 優先選擇互動數較高（按讚、轉推多）的內容
