import pinecone
import asyncio
import os
from openai import OpenAI
from VAgent.config import CONFIG

class VectorDBInterface:
    def __init__(self, config=CONFIG):
        # Initialize Pinecone
        self.config = CONFIG
        pinecone.init(api_key=config.DB_API_Key, environment=config.DB_Environment)
        self.task_index = pinecone.Index(config.DB_Index)
        self.client = OpenAI(
            api_key = self.config.request.ada_embedding.api_key,
            base_url= self.config.request.ada_embedding.base_url,
        )
        self.embedding_model = self.config.request.ada_embedding.embedding_model
        self.get_info()
    
    def get_info(self):
        # 定义函数：统计数据库信息
        try:
            info = self.task_index.describe_index_stats()
            self.vector_count = info["total_vector_count"]
            dimension = info['dimension']
            print(info)
            print("DB dims: ", dimension)
            print("DB vectors: ", self.vector_count)
        except:
            print("Warning: Failed to obtain database information")

    async def generate_embedding(self, text:str):
        try:
            response = self.client.embeddings.create(
                input = [text],
                model=self.embedding_model
            )
            embedding = response.data[0].embedding
            return embedding
        except Exception as e:
            print(f"Error in embedding generation: {e}")

    async def delete_sentence(self, sentence:str):
        # 定义函数：删除句子及其语义向量
        try:
            self.task_index.delete(sentence)
            print("Successful deletion of sentence vector: ", sentence)
        except:
            print("Warning: Fail to delete the sentence vector ", sentence)

    async def insert_sentence(self, vec_sentence:str, sentence:str, namespace=""):
        embedding = await self.generate_embedding(vec_sentence)
        if embedding:
            try:
                self.task_index.upsert(
                    [(str(self.vector_count),
                    embedding,
                    {"text":sentence, "type":namespace})],
                    # namespace=namespace,
                )
                print(f"Successfully insert into the data base, type: {namespace}")
                self.vector_count += 1
            except Exception as e:
                print(e)
                print("Warning: ")
        else:
            print("Warning: Failed to generate embedding for ", sentence)

    async def search_similar_sentences(self, query_sentence:str, namespace="", top_k=1):
        embedding = await self.generate_embedding(query_sentence)
        if embedding:
            try:
                res = self.task_index.query(
                    embedding,
                    top_k=top_k,
                    include_metadata=True,
                    include_values=False,
                    filter={
                        "type": {"$eq": namespace},
                    },
                )
                return res
            except Exception as e:
                print(e)
                print("Warning: failed to find similar sentences")
        else:
            print("Warning: Fail to generate embedding")

async def main():
    import os
    CONFIG.reload(os.path.join(os.path.dirname(__file__), "../assets/private.yml"))
    VDB = VectorDBInterface()
    await VDB.insert_sentence("I want to search the saftey level of Tesla model X", "I want to search the saftey level of Tesla model X", "test1123")
    res = await VDB.search_similar_sentences("Tesla model Y is said to be very expensive, I would like a report on it's price in 5 years", "test1123")
    print(res)

# vectordb = VectorDBInterface(CONFIG)

if __name__ == "__main__":
    asyncio.run(main())