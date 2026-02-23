# X Search 任務：ai_emerging

## 任務說明
請使用 X (Twitter) 的搜尋功能，幫我收集符合以下條件的推文。

## 搜尋策略
- **工具類型**：Semantic Search
- **排序模式**：Latest
- **數量限制**：10 條相關推文

## 搜尋條件

### 查詢主體（Semantic Search）
```
AI and machine learning community breakthroughs, surprising new model releases,
paradigm shifts, or emerging research trends that the tech community is
excited about — including things that may not yet have a well-known name.
```

### 條件參數
- `min_faves:100`（互動門檻）
- `-filter:replies`（排除類型，可選：replies / images / videos / news / links）
- `lang:en OR lang:zh`（語言過濾）


## 來源帳號限制
請**優先**從以下帳號搜尋：`from:OpenAI OR from:AnthropicAI OR from:GoogleDeepMind`
如果這些帳號近期無符合條件的推文，可擴大至一般搜尋。

## 內容篩選

### 優先收錄
社群熱烈討論的新技術、令人意外的研究結果、尚無定論但引發廣泛關注的新發展

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
