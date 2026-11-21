from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from backend.core.config import settings, BASE_DIR
from backend.core.logging import logger
from backend.database.models import KnowledgeDocument
from backend.services.rag.ingest import DocumentChunker
from backend.services.rag.embeddings import vector_store

class RAGRetriever:
    """Coordinates document ingestion and context retrieval for RAG."""

    @staticmethod
    def ingest_all_documents(db: Optional[Session] = None) -> int:
        """
        Scans knowledge_base/ directory, chunks documents, indexes them in ChromaDB,
        and records document metadata in the relational database.
        Returns total number of chunks indexed.
        """
        kb_dir = BASE_DIR / "knowledge_base"
        if not kb_dir.exists():
            logger.warning(f"Knowledge base directory does not exist: {kb_dir}")
            return 0

        supported_extensions = [".md", ".txt", ".pdf"]
        doc_files = [p for p in kb_dir.iterdir() if p.suffix.lower() in supported_extensions and p.is_file()]

        total_chunks_indexed = 0

        for file_path in doc_files:
            # Skip documentation readme if present
            if file_path.name.lower() == "readme.md":
                continue

            chunk_records = DocumentChunker.process_file(file_path)
            if not chunk_records:
                continue

            ids = [c["id"] for c in chunk_records]
            documents = [c["text"] for c in chunk_records]
            metadatas = [c["metadata"] for c in chunk_records]

            # Upsert into ChromaDB
            vector_store.add_chunks(ids=ids, documents=documents, metadatas=metadatas)
            total_chunks_indexed += len(chunk_records)

            # Persist record in MySQL/SQLite if DB session is provided
            if db:
                existing_doc = db.query(KnowledgeDocument).filter(
                    KnowledgeDocument.file_path == str(file_path)
                ).first()
                if not existing_doc:
                    new_doc = KnowledgeDocument(
                        doc_title=file_path.stem.replace("_", " ").title(),
                        category=file_path.stem.replace("_", " ").title(),
                        file_path=str(file_path),
                        total_chunks=len(chunk_records)
                    )
                    db.add(new_doc)
                else:
                    existing_doc.total_chunks = len(chunk_records)
                db.commit()

        logger.info(f"Knowledge Base ingestion complete: {total_chunks_indexed} total chunks.")
        return total_chunks_indexed

    @staticmethod
    def retrieve_context(
        query_text: str,
        top_k: int = 3,
        distance_threshold: float = 0.90
    ) -> Tuple[Optional[str], List[Dict[str, str]]]:
        """
        Performs semantic search against ChromaDB.
        Constructs an isolated, prompt-injection-resistant context block.
        Returns: (formatted_context_block, citations_list)
        """
        if not query_text or not query_text.strip():
            return None, []

        results = vector_store.query(query_text=query_text, n_results=top_k)

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        if not documents:
            return None, []

        context_chunks = []
        citations = []
        seen_sources = set()

        for doc_text, meta, dist in zip(documents, metadatas, distances):
            # Only include chunks within acceptable semantic distance
            if dist > distance_threshold:
                continue

            source = meta.get("source", "verified_wellness_resource")
            category = meta.get("category", "General")
            
            context_chunks.append(
                f"[Source: {source} | Category: {category}]\n{doc_text}"
            )

            if source not in seen_sources:
                citations.append({
                    "source": source,
                    "category": category
                })
                seen_sources.add(source)

        if not context_chunks:
            return None, []

        # Wrap in isolated XML-like tags to defend against prompt injection in retrieved content
        formatted_context = (
            "<retrieved_wellness_knowledge>\n"
            + "\n\n---\n\n".join(context_chunks)
            + "\n</retrieved_wellness_knowledge>"
        )

        return formatted_context, citations

rag_retriever = RAGRetriever()
