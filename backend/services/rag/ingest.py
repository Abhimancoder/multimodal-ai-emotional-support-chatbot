import re
from pathlib import Path
from typing import List, Dict, Any
from backend.core.logging import logger

class DocumentChunker:
    """Extracts, cleans, and chunks text from knowledge base documents."""

    @staticmethod
    def clean_text(text: str) -> str:
        """Normalizes whitespace and removes unprintable characters."""
        # Replace non-breaking spaces and tabs
        text = text.replace("\xa0", " ").replace("\t", " ")
        # Collapse multiple empty lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @classmethod
    def chunk_text(
        cls,
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> List[str]:
        """
        Splits text into chunks of specified size with overlap.
        Preserves paragraph and sentence boundaries wherever possible.
        """
        text = cls.clean_text(text)
        if not text:
            return []

        chunks = []
        paragraphs = text.split("\n\n")
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) + 2 <= chunk_size:
                current_chunk = f"{current_chunk}\n\n{para}".strip()
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                # If paragraph itself is longer than chunk_size, split by sentences/size
                if len(para) > chunk_size:
                    start = 0
                    while start < len(para):
                        end = min(start + chunk_size, len(para))
                        chunks.append(para[start:end].strip())
                        start += (chunk_size - chunk_overlap)
                    current_chunk = ""
                else:
                    current_chunk = para

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    @classmethod
    def process_file(cls, file_path: Path) -> List[Dict[str, Any]]:
        """
        Reads a document file (.md, .txt) and returns a list of chunk dictionaries
        with source metadata.
        """
        if not file_path.exists():
            logger.error(f"Knowledge document not found: {file_path}")
            return []

        try:
            if file_path.suffix.lower() == ".pdf":
                try:
                    import pypdf
                    reader = pypdf.PdfReader(str(file_path))
                    content = "\n\n".join(page.extract_text() or "" for page in reader.pages)
                except Exception as pdf_err:
                    logger.error(f"Failed to parse PDF {file_path}: {pdf_err}")
                    return []
            else:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

            chunks = cls.chunk_text(content)
            doc_name = file_path.name
            category = file_path.stem.replace("_", " ").title()

            chunk_records = []
            for idx, chunk in enumerate(chunks):
                chunk_records.append({
                    "id": f"{doc_name}_chunk_{idx}",
                    "text": chunk,
                    "metadata": {
                        "source": doc_name,
                        "category": category,
                        "chunk_index": idx,
                        "total_chunks": len(chunks)
                    }
                })

            logger.info(f"Processed {doc_name}: {len(chunks)} chunks created.")
            return chunk_records

        except Exception as exc:
            logger.error(f"Failed to process knowledge document {file_path}: {exc}")
            return []
