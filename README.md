# Basic RAG System

A small, from-scratch Retrieval-Augmented Generation (RAG) system over a folder of
Markdown documents. It chunks docs by paragraph, embeds them with OpenAI, stores the
vectors in a persistent [Chroma](https://www.trychroma.com/) collection, and answers
questions grounded in the retrieved chunks.

## How it works

```
docs/*.md  ->  paragraph chunking  ->  OpenAI embeddings  ->  Chroma (on disk)
                                                                    |
question  ->  embed  ->  top-k similarity search  ->  grounded prompt  ->  answer
```

- **Chunking**: paragraph packing — split on blank lines, greedily fill paragraphs
  up to a character cap (`CHUNK_CAP`) so chunks never cut mid-sentence.
- **Embeddings**: OpenAI `text-embedding-3-small`.
- **Vector store**: Chroma `PersistentClient` (`./chroma_db`) — build once, query across runs.
- **Generation**: `gpt-4o-mini`, constrained to answer only from retrieved chunks.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install openai chromadb numpy

cp .env.example .env   # then add your OPENAI_API_KEY
```

## Usage

```bash
python build_index.py   # chunk docs/, embed, and store in ./chroma_db (run once)
python query_index.py   # ask a question against the index
```

Edit the `query` variable in `query_index.py` to change the question.

## Project layout

| File | Purpose |
|------|---------|
| `build_index.py` | Ingest `docs/*.md`, paragraph-chunk, embed, and index into Chroma |
| `query_index.py` | Embed a question, retrieve top-k chunks, answer grounded in them |
| `docs/` | Sample Markdown documents |
| `check.py` | Minimal OpenAI chat + embeddings sanity check |
