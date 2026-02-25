# X Search 任務：ufo_disclosure_hybrid

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
尋找政府 UFO/UAP 披露進展，包括國會聽證會、五角大廈報告、軍事人員證詞、
解密文件以及對不明空中現象的官方調查。
聚焦於可信來源，如政府官員、軍事人員、調查記者和學術研究人員，
討論披露工作進展及 UAP 相關證據。

推薦檢索策略：
- 立法與政府機構：(UAPDA OR AARO OR "Schumer amendment" OR FOIA OR SCIF OR "intelligence committee")
- 深度調查與吹哨人：("David Grusch" OR "first-hand" OR "classified" OR NDA OR "crash retrieval" OR NHI)

若上述 keywords 未找到合適結果，可依據「目標描述」擴大或調整搜尋方向。
```

### 條件參數
- `min_faves:50`（互動門檻）
- `lang:en OR lang:zh`（語言過濾）


## 內容篩選

### 優先收錄
政府聽證會內容、官方報告發布、軍事人員證詞、解密文件、
UAP 目擊事件調查、相關立法進展、官方披露進展、
政府調查報告、解密文件分析、學術研究、主流媒體深度報導

### 排除內容
純娛樂內容、科幻小說討論、電影遊戲宣傳、
無根據猜測、科幻創作

## 輸出格式
請以結構化 JSON 格式返回，每條推文包含以下欄位：
- author: 作者顯示名稱
- username: @用戶名（不含@）
- time: 發布時間（ISO 8601 格式，含時區，例如 2026-02-23T14:30:00Z）
- content: 推文完整內容（保留原始文字，包含連結）
- url: 推文永久連結（格式：https://x.com/username/status/post_id）
- engagement: {likes: 數量, retweets: 數量, replies: 數量}
- media_urls: 推文中的圖片或影片連結陣列（無媒體則為空陣列 []）
- relevance_note: 簡短說明為何符合此主題（1-2句，請說明與 UFO/Disclosure 主題的關聯性）

## 注意事項
1. 請確保資訊準確，包含正確的推文連結
2. 如果找到的推文不足 10 條，請說明原因
3. 如果沒有找到符合條件的推文，請明確告知
4. 優先選擇互動數較高（按讚、轉推多）的內容
