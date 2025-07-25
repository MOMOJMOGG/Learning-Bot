from dotenv import load_dotenv
from chromadb import PersistentClient
import json
import os
import openai
import sys
import time

# 讀取 .env 檔案
load_dotenv()

# 初始化 OpenAI API
openai.api_key = os.environ.get("OPAI_API_KEY")

# 查詢 OpenAI embedding
def get_openai_embedding(text: str) -> list:
    response = openai.embeddings.create(
        model="text-embedding-3-small",  # 或改成 text-embedding-ada-002
        input=text
    )
    return response.data[0].embedding

if __name__ == "__main__":
    course_file = "data/sat_courses.json"
    chroma_dir = "./chroma_db"
    collection_name = "sat_courses_openai"

    force_rebuild = "--force-rebuild" in sys.argv

    if not os.path.exists(course_file):
        raise FileNotFoundError(f"找不到課程資料檔案: {course_file}")

    with open(course_file, "r", encoding="utf-8") as f:
        courses = json.load(f)

    start = time.time()

    documents = []
    metadatas = []
    ids = []

    for i, course in enumerate(courses):
        content = (
            f"可成名稱: {course['title']}\n"
            f"講師: {course['teacher']['name']}\n"
            f"分類: {course['category']['name']}\n"
            f"簡介: {course['intro']}"
        )
        documents.append(content)
        metadatas.append({
            'id': i,
            'title': course['title'],
            'teacher': course['teacher']['name'],
            'link': course['link'],
            'price': course['price']['price'],
            'rating': course['rating']['rate'],
            'category': course['category']['name'],
            'platform': course['platform']
        })

    ids = [str(i) for i in range(len(documents))]

    # === 產生 OpenAI Embedding ===
    print(f"🔄 正在使用 OpenAI 建立 {len(documents)} 筆向量...")
    embeddings = [get_openai_embedding(doc) for doc in documents]

    # === 初始化 Chroma 向量資料庫 ===
    chroma_client = PersistentClient(path=chroma_dir)

    if force_rebuild:
        if collection_name in [c.name for c in chroma_client.list_collections()]:
            chroma_client.delete_collection(name=collection_name)
            print(f"⚠️ 已刪除舊的 collection: {collection_name}")

    if collection_name in [c.name for c in chroma_client.list_collections()]:
        collection = chroma_client.get_collection(name=collection_name)
        print(f"✅ 已載入現有 collection: {collection_name}")
    else:
        collection = chroma_client.create_collection(name=collection_name)
        print(f"✅ 建立新 collection: {collection_name}")

    # === 避免重複新增 ===
    existing_ids = set(collection.get()["ids"])
    new_docs = []
    new_ids = []
    new_metas = []
    new_embeds = []

    for doc, meta, embed, doc_id in zip(documents, metadatas, embeddings, ids):
        if doc_id not in existing_ids:
            new_docs.append(doc)
            new_ids.append(doc_id)
            new_metas.append(meta)
            new_embeds.append(embed)

    if new_docs:
        collection.add(
            documents=new_docs,
            embeddings=new_embeds,
            metadatas=new_metas,
            ids=new_ids
        )
        print(f"✅ 新增 {len(new_docs)} 筆資料")
    else:
        print("所有資料已存在，未新增")

    end = time.time()
    print(f"✅ 完成建庫，耗時: {end - start:.2f} 秒")