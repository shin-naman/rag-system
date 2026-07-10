from chromadb import PersistentClient
from chromadb.utils import embedding_functions
import os 
from openai import OpenAI

query = "What is Nimbus Coffee Roasters?"
chroma_client = PersistentClient(path="./chroma_db")
embedding_func = embedding_functions.OpenAIEmbeddingFunction(model_name="text-embedding-3-small", api_key=os.environ["OPENAI_API_KEY"])

collection = chroma_client.get_collection("nimbus_docs", embedding_function=embedding_func)

results = collection.query(
    query_texts=[query],
    n_results=3
)

results = results['documents'][0]

chat = OpenAI().chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Answer using only the text below. If it's not there, say you don't know."},
        {
            "role": "user",
            "content": str(results[0]) + str(results[1]) + str(results[2]) + query
        },
    ],
)

print(chat.choices[0].message.content)