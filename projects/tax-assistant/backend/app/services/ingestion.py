import hashlib
import io
import re

from pypdf import PdfReader


class PDFExtractionError(Exception):
    """Raised when PDF extraction fails."""

    pass


class PDFIngestionService:
    @staticmethod
    def compute_sha256(data: bytes | str) -> str:
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def detect_document_type(text: str, filename: str = "") -> str:
        combined = f"{filename.upper()} {text.upper()}"
        if "AUTO DE INFRAÇÃO" in combined or "AIIM" in combined:
            return "AIIM"
        if "NOTIFICAÇÃO DE LANÇAMENTO" in combined or "NOTIFICACAO DE LANCAMENTO" in combined:
            return "NL"
        if "SOLUÇÃO DE CONSULTA" in combined or "COSIT" in combined or "PARECER" in combined:
            return "COSIT"
        if "DOCUMENTO DE ARRECADAÇÃO" in combined or "DARF" in combined:
            return "DARF"
        if (
            "CERTIDÃO NEGATIVA" in combined
            or "CERTIDAO NEGATIVA" in combined
            or "CPEN" in combined
            or "CND" in combined
        ):
            return "CND"
        return "OUTRO"

    def extract_pages_from_pdf(self, file_bytes: bytes) -> list[dict]:
        """Extract text page by page from raw PDF bytes."""
        if not file_bytes:
            raise PDFExtractionError("PDF file is empty.")

        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            if len(reader.pages) == 0:
                raise PDFExtractionError("PDF contains no pages.")

            pages: list[dict] = []
            for idx, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() or ""
                # Normalize spaces and newlines
                normalized = self._normalize_text(page_text)
                pages.append({"page_number": idx, "text": normalized})

            return pages
        except Exception as e:
            if isinstance(e, PDFExtractionError):
                raise
            raise PDFExtractionError(f"Failed to parse PDF document: {str(e)}") from e

    def extract_pages_from_text(self, raw_text: str, page_char_limit: int = 2500) -> list[dict]:
        """Extract pages from plain text, respecting form feeds if present."""
        if not raw_text.strip():
            return [{"page_number": 1, "text": ""}]

        if "\f" in raw_text:
            raw_pages = raw_text.split("\f")
            pages = []
            for idx, p in enumerate(raw_pages, start=1):
                norm = self._normalize_text(p)
                if norm or len(raw_pages) == 1:
                    pages.append({"page_number": idx, "text": norm})
            return pages if pages else [{"page_number": 1, "text": ""}]

        # Partition by length if continuous text without form-feeds
        paragraphs = raw_text.split("\n\n")
        pages = []
        current_page_text = []
        current_len = 0
        current_page = 1

        for p in paragraphs:
            p_clean = self._normalize_text(p)
            if not p_clean:
                continue
            if current_len + len(p_clean) > page_char_limit and current_page_text:
                pages.append({"page_number": current_page, "text": "\n\n".join(current_page_text)})
                current_page += 1
                current_page_text = [p_clean]
                current_len = len(p_clean)
            else:
                current_page_text.append(p_clean)
                current_len += len(p_clean)

        if current_page_text:
            pages.append({"page_number": current_page, "text": "\n\n".join(current_page_text)})

        return pages if pages else [{"page_number": 1, "text": self._normalize_text(raw_text)}]

    def chunk_document(
        self,
        pages: list[dict],
        chunk_size: int = 800,
        chunk_overlap: int = 150,
    ) -> list[dict]:
        """Chunk document text by page while preserving context and overlap."""
        chunks: list[dict] = []
        chunk_index = 0

        for page in pages:
            page_num = page["page_number"]
            text = page["text"].strip()
            if not text:
                continue

            # Split into words to calculate character bounds and overlaps cleanly
            words = text.split()
            if not words:
                continue

            # Approximate tokens ~ words
            start_word = 0
            step = max(1, (chunk_size - chunk_overlap) // 5)  # approx 5 chars per word
            max_words = max(5, chunk_size // 5)

            while start_word < len(words):
                end_word = min(len(words), start_word + max_words)
                chunk_words = words[start_word:end_word]
                chunk_content = " ".join(chunk_words)

                chunks.append(
                    {
                        "chunk_index": chunk_index,
                        "page_number": page_num,
                        "content": chunk_content,
                        "token_count": len(chunk_words),
                    }
                )
                chunk_index += 1

                if end_word >= len(words):
                    break
                start_word += step

        return chunks

    def _normalize_text(self, text: str) -> str:
        """Clean up multiple whitespaces while preserving structural line breaks."""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Replace 3 or more newlines with double newline
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Collapse multiple horizontal spaces
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()
