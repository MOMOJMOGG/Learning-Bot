
from chromadb import PersistentClient
import json
import os
from sentence_transformers import SentenceTransformer
import time

if __name__ == "__main__":
    course_file = "data/sat_courses.json"
    chroma_dir  = "./chroma_db"
    collection_name = "sat_courses" 
    
    # === Step 1: 載入課程 JSON 檔 ===
    if not os.path.exists(course_file):
        raise FileNotFoundError(f"找不到課程資料檔案: {course_file}")
    
    with open(course_file, "r", encoding="utf-8") as f:
        courses = json.load(f)
    
    start = time.time()
    # === Step 2: 提取文字內容與 metadata ===
    documents = []
    metadatas = []
    ids = []
    for i, course in enumerate(courses):
        #* 文字內容會拿來當作語意向量 embedding
        content = (
            f"可成名稱: {course['title']}\n"
            f"講師: {course['teacher']['name']}\n"
            f"分類: {course['category']['name']}\n"
            f"簡介: {course['intro']}"
        )
        documents.append(content)
        
        #* metadata 可用於搜尋與顯示結果
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
    
    # === Step 3. 建立文本向量 ===
    model = SentenceTransformer("all-MiniLM-L6-v2")     #? 小型快模型
    embeddings = model.encode(documents, show_progress_bar=True)
    
    # === Step 4. 初始化 Chroma 向量資料庫 ===
    chroma_client = PersistentClient(path=chroma_dir)
    
    if collection_name in [c.name for c in chroma_client.list_collections()]:
        collection = chroma_client.get_collection(name=collection_name)
        print(f"✅ 已載入現有 collection: {collection_name}")
    
    else:
        collection = chroma_client.create_collection(name=collection_name)
        print(f"✅ 建立新 collection: {collection_name}")
    
    # === Step 5. 新增資料 (避免重複)
    existing_ids = set(collection.get(ids=ids)["ids"]) if len(ids) else set()
    new_docs   = []
    new_ids    = []
    new_metas  = []
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
            embeddings=new_metas,
            metadatas=new_embeds,
            ids=new_ids
        )
        print(f"✅ 新增 {len(new_docs)} 筆資料")
        
    else:
        print("所有資料已存在，未新增")
    
    # === Step 6: 儲存資料庫到磁碟 ===
    end = time.time()
    
    print(f"✅ 向量資料庫已儲存到 {chroma_dir}，耗時: {end - start} 秒")