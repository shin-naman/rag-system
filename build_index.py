from pathlib import Path
import os
import chromadb 
from chromadb.utils import embedding_functions


directory = Path("./docs")

CHUNK_CAP = 800  # max characters per chunk


def pack_paragraphs(text, cap):
    """Split on blank lines, greedily fill paragraphs into chunks up to `cap` chars."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for para in paragraphs:
        # +2 accounts for the "\n\n" separator we'd add between paragraphs
        if current and len(current) + len(para) + 2 > cap:
            chunks.append(current)
            current = para
        else:
            current = f"{current}\n\n{para}" if current else para
    if current:
        chunks.append(current)
    return chunks


documents, ids, metadatas = [], [], []


for file_path in directory.glob("*.md"):
    filename = file_path.name
    text = file_path.read_text()
    for idx, chunk in enumerate(pack_paragraphs(text, CHUNK_CAP)):
        documents.append(chunk)
        ids.append(f"{filename}_{idx}")
        metadatas.append({"source": filename})

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