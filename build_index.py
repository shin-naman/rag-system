from pathlib import Path
import os
import chromadb
from chromadb.utils import embedding_functions

from chunk import chunk_markdown


directory = Path("./docs")

CHUNK_CAP = 800       # max characters per chunk
CHUNK_OVERLAP = 100   # chars shared between windows when hard-slicing an over-cap paragraph


documents, ids, metadatas = [], [], []


for file_path in directory.glob("*.md"):
    filename = file_path.name
    text = file_path.read_text()
    for idx, (chunk, path) in enumerate(chunk_markdown(text, CHUNK_CAP, CHUNK_OVERLAP)):
        documents.append(chunk)
        ids.append(f"{filename}_{idx}")
        metadatas.append({"source": filename, "headings": path})

embedding_func = embedding_functions.OpenAIEmbeddingFunction(model_name="text-embedding-3-small", api_key=os.environ["OPENAI_API_KEY"])
chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_client.delete_collection("nimbus_docs")

collection = chroma_client.get_or_create_collection(
    name="nimbus_docs",
    embedding_function=embedding_func
)

collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)

print(len(collection.get(include=["metadatas"])["metadatas"]), "documents added to the collection.")
