from chromadb import PersistentClient
from dotenv import load_dotenv
import openai
import os

# 讀取 .env 檔案
load_dotenv()

# === 設定查詢語句與參數 ===
QUERY_TEXT = "我想提升健康與體態"
CHROMA_DIR = "./chroma_db"
COLLECTION_CHROMBA = "sat_courses"
COLLECTION_OPENAI  = "sat_courses_openai"

# 初始化 OpenAI API
openai.api_key = os.environ.get("OPAI_API_KEY")

# 輔助函式：取得 OpenAI 向量
def get_openai_embedding(text: str) -> list:
    response = openai.embeddings.create(
        model="text-embedding-3-small",  # 或 "text-embedding-ada-002"
        input=text
    )
    return response.data[0].embedding

# === 初始化 ChromaDB 客戶端 ===
client = PersistentClient(path=CHROMA_DIR)

# === A. 讀取原本 sentence-transformers 建立的 collection ===
if COLLECTION_CHROMBA not in [c.name for c in client.list_collections()]:
    raise ValueError(f"❌ 找不到 collection: {COLLECTION_CHROMBA}")
collection_chromba = client.get_collection(name=COLLECTION_CHROMBA)

print(f"\n🔍 查詢語句：{QUERY_TEXT}")
print("\n📌 A. 使用原本模型查詢（collection: sat_courses）：")
results_a = collection_chromba.query(
    query_texts=[QUERY_TEXT],
    n_results=3
)

for doc, meta, dist in zip(results_a["documents"][0],
                            results_a["metadatas"][0],
                            results_a["distances"][0]):
    print(f"- {meta['title']} | 講師: {meta['teacher']} | 分類: {meta['category']}")
    print(f"  課程連結: {meta['link']}")
    print(f"  相似度: {dist:.4f}")
    
# === B. 查詢 OpenAI embedding 的 collection ===
if COLLECTION_OPENAI not in [c.name for c in client.list_collections()]:
    raise ValueError(f"❌ 找不到 collection: {COLLECTION_OPENAI}")
collection_openai = client.get_collection(name=COLLECTION_OPENAI)

print("\n📌 B. 使用 OpenAI embedding 查詢（collection: sat_courses_openai）：")
embedding_b = get_openai_embedding(QUERY_TEXT)
results_b = collection_openai.query(
    query_embeddings=[embedding_b],
    n_results=3
)
for doc, meta, dist in zip(results_b["documents"][0],
                            results_b["metadatas"][0],
                            results_b["distances"][0]):
    print(f"- {meta['title']} | 講師: {meta['teacher']} | 分類: {meta['category']}")
    print(f"  課程連結: {meta['link']}")
    print(f"  相似度: {dist:.4f}")