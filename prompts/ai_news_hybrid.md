# X Search 任務：ai_news_hybrid

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
尋找 AI 與機器學習領域的重大突破、令人驚喜的新模型發布、範式轉移、
基準測試結果，或正在興起的研究趨勢——包括那些可能還沒有廣為人知名稱的新事物。
聚焦於技術社群真正感到興奮且正在熱烈討論的內容。

推薦檢索策略：
- 核心關鍵字：(artificial intelligence OR AI OR "machine learning")
- 事件類型：(breakthrough OR release OR announced OR launched OR benchmark)
- 排除條件：-crypto -blockchain -token -coin -nft

若上述 keywords 未找到合適結果，可依據「目標描述」擴大或調整搜尋方向，但務必嚴格遵守排除條件。
```

### 條件參數
- `min_faves:100`（互動門檻）
- `lang:en OR lang:zh`（語言過濾）


## 內容篩選

### 優先收錄
官方公告（OpenAI、Anthropic、Google DeepMind 等）、
技術論文發布（arXiv、Hugging Face）、
有數據或截圖佐證的消息、
知名研究者或工程師分享、
社群熱烈討論的新技術、
令人意外的研究結果、
尚無定論但引發廣泛關注的新發展

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
