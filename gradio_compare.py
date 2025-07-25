from chromadb import PersistentClient
from dotenv import load_dotenv
import gradio as gr
import openai
import os
import pandas as pd
import sqlite3
import tempfile

# 讀取 .env 檔案
load_dotenv()

# === 設定查詢語句與參數 ===
QUERY_TEXT = "我想提升健康與體態"
CHROMA_DIR = "./chroma_db"
COLLECTION_CHROMBA = "sat_courses"
COLLECTION_OPENAI  = "sat_courses_openai"
DB_FILE = "search_cache.db"

# 初始化 OpenAI API
openai.api_key = os.environ.get("OPAI_API_KEY")
client = PersistentClient(path=CHROMA_DIR)

# === DB 初始化 ===
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS cache (
            query TEXT PRIMARY KEY,
            table_a TEXT,
            table_b TEXT
        )
    ''')
    conn.commit()
    conn.close()
    
# === 查詢快取 ===
def load_from_cache(query):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT table_a, table_b FROM cache WHERE query=?", (query,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0], row[1]
    return None

def save_to_cache(query, html_a, html_b):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("REPLACE INTO cache (query, table_a, table_b) VALUES (?, ?, ?)",
              (query, html_a, html_b))
    conn.commit()
    conn.close()

def get_query_history():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT query FROM cache ORDER BY rowid DESC LIMIT 20")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

# === 模型查詢 ===
def get_openai_embedding(text: str) -> list:
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def query_collection_html_and_csv(collection, query_text=None, query_embedding=None, use_embedding=False):
    if use_embedding:
        result = collection.query(query_embeddings=[query_embedding], n_results=3)
    else:
        result = collection.query(query_texts=[query_text], n_results=3)

    courses = result["metadatas"][0]
    distances = result["distances"][0]

    table = {
        "欄位": ["標題", "講師", "分類", "平台", "價格", "評分", "課程連結", "相似度"]
    }

    for i, (meta, dist) in enumerate(zip(courses, distances), 1):
        link_html = f'<a href="{meta["link"]}" target="_blank">{meta["link"]}</a>'
        table[f"課程{i}"] = [
            meta["title"],
            meta["teacher"],
            meta["category"],
            meta["platform"],
            meta["price"],
            meta["rating"],
            link_html,
            f"{dist:.4f}"
        ]

    df = pd.DataFrame(table)
    df_csv = df.copy()
    
    # 找出所有課程欄位（除了第一欄「欄位」）
    course_columns = [col for col in df_csv.columns if col != "欄位"]

    # 替換「課程連結」列為純網址
    for i, col in enumerate(course_columns):
        df_csv.loc[df_csv["欄位"] == "課程連結", col] = courses[i]["link"]

    # 儲存成暫存 CSV 檔案
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode='w', newline='', encoding='utf-8')
    df_csv.to_csv(tmp.name, index=False)
    return df.to_html(escape=False, index=False), tmp.name

# === 主查詢流程 ===
def search_courses(query_text):
    cached = load_from_cache(query_text)
    if cached:
        return cached[0], cached[1], None, None, gr.update(choices=get_query_history())

    collection_transformer = client.get_collection(name=COLLECTION_CHROMBA)
    collection_openai = client.get_collection(name=COLLECTION_OPENAI)

    result_a = query_collection_html_and_csv(collection_transformer, query_text=query_text, use_embedding=False)
    embedding_b = get_openai_embedding(query_text)
    result_b = query_collection_html_and_csv(collection_openai, query_embedding=embedding_b, use_embedding=True)

    html_a, csv_a = result_a
    html_b, csv_b = result_b
    
    save_to_cache(query_text, html_a, html_b)
    return html_a, html_b, csv_a, csv_b, gr.update(choices=get_query_history())

# === 點選歷史查詢項目 ===
def reuse_history_item(selected_query):
    return search_courses(selected_query)

# === 初始化資料庫 ===
init_db()

# === Gradio 介面 ===
with gr.Blocks(title="課程語意查詢比較工具 (含快取與 CSV 下載)") as demo:
    gr.Markdown("## 🎓 課程語意查詢工具：比較兩種模型推薦結果")
    with gr.Row():
        query_input = gr.Textbox(label="輸入查詢句子", placeholder="例如：我想學AI自動化")
        search_button = gr.Button("查詢")

    with gr.Row():
        table1 = gr.HTML(label="📘 SentenceTransformer 模型查詢結果")
        table2 = gr.HTML(label="🤖 OpenAI 模型查詢結果")

    with gr.Row():
        csv1 = gr.File(label="📥 下載 SentenceTransformer 模型結果", interactive=False)
        csv2 = gr.File(label="📥 下載 OpenAI 模型結果", interactive=False)
        
    with gr.Row():
        gr.Markdown("### 🔁 歷史查詢")
        history_list = gr.Dropdown(choices=get_query_history(), label="過去查詢句子")
        
    search_button.click(
        fn=search_courses,
        inputs=[query_input],
        outputs=[table1, table2, csv1, csv2, history_list]
    )

    history_list.change(
        fn=reuse_history_item,
        inputs=[history_list],
        outputs=[table1, table2, csv1, csv2, history_list]
    )

# 啟動服務
if __name__ == "__main__":
    demo.launch()