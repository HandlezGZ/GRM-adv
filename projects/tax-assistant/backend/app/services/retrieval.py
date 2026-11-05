import math
import re
from typing import Any

from backend.app.models.document_chunk import DocumentChunk
from backend.app.schemas.chat import CitationItem

# Portuguese stopwords
PORTUGUESE_STOPWORDS = {
    "a", "ao", "aos", "aquela", "aquelas", "aquele", "aqueles", "aquilo", "as", "à", "às",
    "até", "com", "como", "da", "das", "de", "dela", "delas", "dele", "deles", "depois",
    "do", "dos", "e", "é", "ela", "elas", "ele", "eles", "em", "entre", "era", "eram",
    "éramos", "essa", "essas", "esse", "esses", "esta", "estamos", "estas", "estava",
    "estavam", "este", "estes", "estive", "estivemos", "estiveram", "estivesse",
    "estivessem", "estou", "eu", "foi", "fomos", "foram", "fosse", "fossem", "há",
    "isso", "isto", "já", "lhe", "lhes", "mais", "mas", "me", "mesmo", "meu", "meus",
    "minha", "minhas", "muito", "na", "nas", "não", "no", "nos", "nós", "nossa",
    "nossas", "nosso", "nossos", "num", "numa", "o", "os", "ou", "para", "pela",
    "pelas", "pelo", "pelos", "por", "qual", "quais", "quando", "que", "quem", "se",
    "seja", "sejam", "sem", "ser", "será", "serão", "seu", "seus", "só", "sua",
    "suas", "também", "te", "tem", "têm", "temos", "tenho", "ter", "teu", "teus",
    "teve", "tinha", "tinham", "tive", "tivemos", "tiveram", "tivesse", "tivessem",
    "tu", "tua", "tuas", "um", "uma", "você", "vocês",
}


class BM25Retriever:
    """In-memory BM25 ranker for text chunks."""

    def __init__(self, chunks: list[DocumentChunk], k1: float = 1.5, b: float = 0.75):
        self.chunks = chunks
        self.k1 = k1
        self.b = b
        self.corpus_size = len(chunks)
        self.doc_tokens: list[list[str]] = [self._tokenize(c.content) for c in chunks]
        self.doc_lens: list[int] = [len(tokens) for tokens in self.doc_tokens]
        self.avg_dl: float = sum(self.doc_lens) / max(1, self.corpus_size)
        self.idf: dict[str, float] = self._calculate_idf()

    def _tokenize(self, text: str) -> list[str]:
        words = re.findall(r"\b[a-zA-Z0-9áéíóúâêîôûãõçÁÉÍÓÚÂÊÎÔÛÃÕÇ]{2,}\b", text.lower())
        return [w for w in words if w not in PORTUGUESE_STOPWORDS]

    def _calculate_idf(self) -> dict[str, float]:
        df: dict[str, int] = {}
        for tokens in self.doc_tokens:
            for term in set(tokens):
                df[term] = df.get(term, 0) + 1

        idf: dict[str, float] = {}
        for term, freq in df.items():
            # Standard Lucene/BM25 IDF
            idf[term] = math.log(1.0 + (self.corpus_size - freq + 0.5) / (freq + 0.5))
        return idf

    def score(self, query: str) -> list[tuple[DocumentChunk, float]]:
        q_tokens = self._tokenize(query)
        if not q_tokens or self.corpus_size == 0:
            return []

        scores: list[tuple[DocumentChunk, float]] = []
        for idx, chunk in enumerate(self.chunks):
            chunk_tokens = self.doc_tokens[idx]
            dl = self.doc_lens[idx]
            score = 0.0

            token_counts: dict[str, int] = {}
            for t in chunk_tokens:
                token_counts[t] = token_counts.get(t, 0) + 1

            for qt in q_tokens:
                if qt in token_counts:
                    tf = token_counts[qt]
                    term_idf = self.idf.get(qt, 0.1)
                    numerator = tf * (self.k1 + 1.0)
                    denominator = tf + self.k1 * (1.0 - self.b + self.b * (dl / max(1.0, self.avg_dl)))
                    score += term_idf * (numerator / denominator)

            scores.append((chunk, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores


class TaxRetrievalService:
    def __init__(self, top_k: int = 3, min_score_threshold: float = 0.4):
        self.top_k = top_k
        self.min_score_threshold = min_score_threshold

    def search_chunks(
        self,
        query: str,
        chunks: list[DocumentChunk],
    ) -> list[tuple[DocumentChunk, float]]:
        """Rank chunks using BM25 and filter by relevance threshold."""
        if not chunks:
            return []

        ranker = BM25Retriever(chunks)
        ranked = ranker.score(query)

        # Filter relevant matches
        relevant = [(chunk, score) for chunk, score in ranked if score >= self.min_score_threshold]
        return relevant[: self.top_k]

    def _extract_verbatim_excerpt(self, chunk_text: str, query: str, max_chars: int = 280) -> str:
        """Locate the most relevant sentence or paragraph within the chunk text."""
        sentences = re.split(r"(?<=[.!?\n])\s+", chunk_text.strip())
        query_words = set(re.findall(r"\b\w{3,}\b", query.lower())) - PORTUGUESE_STOPWORDS

        if not sentences or not query_words:
            return chunk_text[:max_chars].strip() + ("..." if len(chunk_text) > max_chars else "")

        best_sentence = sentences[0]
        max_overlap = -1

        for sent in sentences:
            sent_words = set(re.findall(r"\b\w{3,}\b", sent.lower()))
            overlap = len(query_words.intersection(sent_words))
            if overlap > max_overlap:
                max_overlap = overlap
                best_sentence = sent

        excerpt = best_sentence.strip()
        if len(excerpt) > max_chars:
            excerpt = excerpt[:max_chars].strip() + "..."
        return excerpt

    def answer_query(
        self,
        query: str,
        chunks: list[DocumentChunk],
    ) -> dict[str, Any]:
        """Grounded Q&A over document chunks with mandatory citations and anti-hallucination."""
        relevant_matches = self.search_chunks(query, chunks)

        # Absolute Anti-Hallucination Guardrail
        if not relevant_matches:
            return {
                "answer": "A informação não foi localizada no documento analisado.",
                "citations": [],
                "is_grounded": False,
            }

        # Build citations
        citations: list[CitationItem] = []
        context_snippets = []

        for chunk, score in relevant_matches:
            excerpt = self._extract_verbatim_excerpt(chunk.content, query)
            citation = CitationItem(
                chunk_id=chunk.id,
                page_number=chunk.page_number,
                verbatim_excerpt=excerpt,
                relevance_score=round(score, 3),
            )
            citations.append(citation)
            context_snippets.append(f"[Página {chunk.page_number}]: {excerpt}")

        # Synthesize verified response
        primary_match = citations[0]
        other_pages = sorted(list({c.page_number for c in citations}))
        pages_str = ", ".join(f"pág. {p}" for p in other_pages)

        answer = (
            f"Com base na análise do documento ({pages_str}), verifica-se o seguinte:\n\n"
            f"> \"{primary_match.verbatim_excerpt}\"\n\n"
            f"Este trecho fundamenta diretamente a questão suscitada, "
            f"conforme registrado nos autos do documento na página {primary_match.page_number}."
        )

        return {
            "answer": answer,
            "citations": citations,
            "is_grounded": True,
        }
