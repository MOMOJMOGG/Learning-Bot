# 🤖 Learning-Bot - LINE 課程推薦機器人 (RAG 技術驅動) | LINE Course Recommendation Bot with RAG

## 📌 專案介紹 | Project Overview
Learning-Bot 是一個結合 RAG (Retrieval-Augmented Generation) 技術的課程推薦系統，使用者透過 LINE Bot 輸入當前的困擾或問題，系統會檢索課程資料庫並給出個人化的課程推薦，並以 LINE Flex Message 呈現。

Learning-Bot is a course recommendation system powered by RAG (Retrieval-Augmented Generation). Users can input their current challenges via LINE Bot, and the system will retrieve relevant courses from its knowledge base and reply with personalized recommendations through LINE Flex Message cards.

| 本專案強調 RAG 技術主軸 (Embedding + 向量檢索 + GPT)，適合延伸應用於 FAQ、自動化知識問答系統與推薦系統

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## ✨ 專案亮點 | Highlights
- ✅ RAG 技術核心：OpenAI Embedding + 向量資料庫 (ChromaDB)
- ✅ 支援課程資料庫檢索，提供語意相關度排序
- ✅ 整合 OpenAI GPT 模型生成推薦理由
- ✅ LINE Bot 前端介面，使用 Flex Message 卡片回覆
- ✅ 支援多輪對話架構可擴充 (Session Context Ready)

- ✔️ RAG Pipeline Core: OpenAI Embedding + Vector DB (ChromaDB)
- ✔️ Semantic search with course database
- ✔️ OpenAI GPT model generates contextual recommendation explanations
- ✔️ LINE Bot integration with Flex Message carousel
- ✔️ Ready for multi-turn conversation extension

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🧩 系統架構 | System Architecture
```
[使用者訊息 LINE Bot]
            ↓
      LINE Webhook (Flask)
            ↓
      RAG Pipeline
   ┌──────────────┐
   │ 1. Embedding │ → OpenAI Embedding API
   │ 2. Retrieval │ → ChromaDB 向量檢索課程資料
   │ 3. Generate  │ → GPT 模型產生推薦理由
   └──────────────┘
            ↓
[LINE Flex Message 回覆課程名單]
```
```
[User Input via LINE Bot]
            ↓
    LINE Webhook (Flask)
            ↓
      RAG Pipeline
   ┌──────────────┐
   │ 1. Embedding │ → OpenAI Embedding API
   │ 2. Retrieval │ → ChromaDB vector search
   │ 3. Generate  │ → GPT model for recommendations
   └──────────────┘
            ↓
[LINE Flex Message with course cards]
```

## 🔁 使用流程 | Workflow
1. 使用者在 LINE Bot 輸入困擾或問題
2. 解析輸入文字，進入 RAG Pipeline
3. 使用 OpenAI Embedding 將問題轉換成向量
4. 向量檢索課程資料庫，找到最相關的課程
5. 使用 GPT 模型生成推薦理由
6. 透過 LINE Flex Message 回覆課程卡片名單

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 📦 套件使用 | Key Packages
- `Flask`： LINE Webhook Server
- `line-bot-sdk` v3： LINE Messaging API 整合
- `chromadb`： 向量資料庫 (Vector DB)
- `openai`： Embedding 與 GPT 模型 API

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 💻 安裝說明 | Installation
```
# Python 版本建議 3.9+
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🛠️ 前置說明 | Prerequisites
1. 你需要一個 LINE Messaging API Channel 並設定 Webhook | [申請參考][Line Developer]
2. 建立 OpenAI API Key (用於 Embedding 與 GPT 推薦)
3. 課程資料來源需整理成 JSON 格式後，執行建庫腳本產生向量資料庫 (ChromaDB)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🔧 設定說明 | Configuration
請在專案根目錄建立 `.env` 參考 `.env.example`：
```
OPAI_API_KEY=your_openai_key
CHANNEL_ACCESS_TOKEN=your_line_developer_channel_token
CHANNEL_SECRET=your_line_developer_channel_secret
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🚀 啟動說明 | Getting Started
1. 啟動 Flask Webhook
```
flask run
```

2. 部署後將 Webhook URL 填入 LINE Developer Console 測試即可

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 📁 專案結構 | Project Structure
```
learning-bot/
├── app.py                 # LINE Webhook 主程式
├── data/                  # 課程原始 JSON 資料
├── chroma_db/             # ChromaDB 向量資料庫儲存目錄
├── requirements.txt       # 環境套件
└── .env.example           # 環境變數範例
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 📸 專案展示 | Showcase
| 下圖為 RAG 推薦課程結果 Flex Message 卡片示例

| Example of RAG-powered course recommendation in LINE Flex Message

![Image][demo-image1]
![Image][demo-image2]

[Line Developer]: https://www.youtube.com/watch?v=Mw3cODdkaFM
[demo-image1]: https://github.com/MOMOJMOGG/learning-bot/blob/main/demo/demo1.png
[demo-image2]: https://github.com/MOMOJMOGG/learning-bot/blob/main/demo/demo2.png
