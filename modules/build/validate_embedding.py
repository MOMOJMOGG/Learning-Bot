from chromadb import PersistentClient
import os

# 設定路徑與 collection 名稱
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "sat_courses"
QUERY_TEXT = "深度學習基礎入門"

# 驗證開始
if not os.path.exists(CHROMA_DIR):
    raise FileNotFoundError(f"❌ 找不到 Chroma 資料夾: {CHROMA_DIR}")

client = PersistentClient(path=CHROMA_DIR)

collections = client.list_collections()
if COLLECTION_NAME not in [c.name for c in collections]:
    raise ValueError(f"❌ 找不到 collection: {COLLECTION_NAME}")
    
# 嘗試取得你建立的 collection
collection = client.get_collection(name=COLLECTION_NAME)

# 查看總筆數
all_data = collection.get()
num_docs = len(all_data["ids"])
print(f"📦 Collection '{COLLECTION_NAME}' 包含 {num_docs} 筆資料")

# 顯示前幾筆內容（最多顯示 3 筆）
print("\n📋 前 3 筆資料簡介：")
for doc, meta in zip(all_data["documents"][:3], all_data["metadatas"][:3]):
    print(f"- 課程標題: {meta['title']}")
    print(f"  講師: {meta['teacher']} | 分類: {meta['category']}")
    print(f"  課程連結: {meta['link']}")
    print(f"  評分: {meta['rating']} | 價格: {meta['price']}")
    print()
    
# 執行一筆語意查詢測試
print(f"🔍 查詢語句: {QUERY_TEXT}")

# 查看能不能做語意搜尋
results = collection.query(
    query_texts=[QUERY_TEXT],  # 輸入任意查詢語句
    n_results=3
)

print("\n🔎 查詢結果 (Top 3)：")
for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
    print(f"- {meta['title']} | 講師: {meta['teacher']} | 分類: {meta['category']}")
    print(f"  相似度: {dist:.4f}")