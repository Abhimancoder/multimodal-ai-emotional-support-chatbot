# Retrieval-Augmented Generation (RAG) Architecture

## 1. Goal
Provide verified psychoeducation, grounding exercises, and coping mechanisms without hallucination or fabricated citations.

## 2. Ingestion Pipeline
1. **Source Documents:** Placed in `knowledge_base/` as `.md`, `.txt`, or `.pdf`.
2. **Text Cleaning:** Normalize whitespace, strip unprintable characters.
3. **Chunking Strategy:** Recursive character text chunking (chunk size: 500 characters, overlap: 50 characters).
4. **Embedding Generation:** HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (runs locally, 384 dimensions) or Gemini Embeddings.
5. **Vector Indexing:** Persisted in local ChromaDB at `storage/chromadb/`.

## 3. Retrieval & Prompt Construction
1. Query embedding computed.
2. Similarity search retrieves top 3 chunks (minimum cosine similarity threshold: 0.65).
3. Chunks formatted with source tags:
```xml
<retrieved_context>
[Source: grounding_techniques.md, Chunk 1]
...text...
</retrieved_context>
```
4. LLM instructed to synthesize answer using context while acknowledging limitations if info is unavailable.
