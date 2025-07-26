
from chromadb import PersistentClient
from dotenv import load_dotenv
import os
import openai

# 讀取 .env 檔案
load_dotenv()

class Config:
    
    def __init__(self):
        
        self.linebot_access_token  = None
        self.linebot_access_secret = None
        
        self.openai_api_key = None
        
        self.db_client = None
        self.collections = None
        self.chroma_dir = "chroma_db"
        self.collection_name = "sat_courses_openai"
        
        self.read_env_var()
        self.set_openai_api_key()
        self.init_chroma()
    
    def read_env_var(self):
        self.linebot_access_token  = os.getenv('CHANNEL_ACCESS_TOKEN')
        self.linebot_access_secret = os.getenv('CHANNEL_SECRET')
        self.openai_api_key = os.getenv("OPAI_API_KEY")
    
    def set_openai_api_key(self):
        openai.api_key = self.openai_api_key
    
    def init_chroma(self):
        self.db_client = PersistentClient(path=self.chroma_dir)
        if self.collection_name not in [c.name for c in self.db_client.list_collections()]:
            print(f"❌ 找不到 collection: {self.collection_name}")
        
        else:
            self.collections = self.db_client.get_collection(name=self.collection_name)
    
    def _fetch_embedding(self, text):
        response = openai.embeddings.create(
            model="text-embedding-3-small",  # 或 "text-embedding-ada-002"
            input=text
        )
        return response.data[0].embedding

    def recommendation(self, question):
        embedding = self._fetch_embedding(question)
        result = self.collections.query(
            query_embeddings=[embedding],
            n_results=3
        )
        
        result_dict = {}
        for idx, (doc, meta, dist) in enumerate(zip(result["documents"][0],
                                                    result["metadatas"][0],
                                                    result["distances"][0])):
            result_dict[idx] = {
                'cource': f"{meta['title']}",
                'teacher': f"{meta['teacher']}",
                'category': f"{meta['category']}",
                'link': f"{meta['link']}",
                'rate': f"{meta['rating']}",
                'duration': f"{meta['duration']}",
                'price': f"{meta['price']}",
                'image': f"{meta['image']}",
                'relative': f"{dist:.1f}"
            }
            
        return result_dict

config = Config()