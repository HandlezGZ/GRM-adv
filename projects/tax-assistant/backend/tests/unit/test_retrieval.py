from backend.app.models.document_chunk import DocumentChunk
from backend.app.services.retrieval import BM25Retriever, TaxRetrievalService


def test_bm25_ranking():
    chunks = [
        DocumentChunk(
            id="c1",
            document_id="doc1",
            chunk_index=0,
            page_number=1,
            content="O contribuinte foi autuado por falta de recolhimento de ICMS no exercício de 2023.",
        ),
        DocumentChunk(
            id="c2",
            document_id="doc1",
            chunk_index=1,
            page_number=2,
            content="A multa de ofício aplicada foi de 50% nos termos do artigo 527 do regulamento.",
        ),
        DocumentChunk(
            id="c3",
            document_id="doc1",
            chunk_index=2,
            page_number=3,
            content="O prazo para apresentação de impugnação administrativa é de 30 dias contados da intimação.",
        ),
    ]

    retriever = BM25Retriever(chunks)
    scores = retriever.score("qual o prazo para impugnação administrativa?")
    assert len(scores) == 3
    # Top chunk should be c3 (page 3)
    best_chunk, best_score = scores[0]
    assert best_chunk.id == "c3"
    assert best_chunk.page_number == 3
    assert best_score > 0


def test_retrieval_grounded_answer_and_citations():
    svc = TaxRetrievalService()
    chunks = [
        DocumentChunk(
            id="c1",
            document_id="doc1",
            chunk_index=0,
            page_number=1,
            content="A autuação decorre da glosa de créditos indevidos de ICMS sobre bens de uso e consumo.",
        ),
        DocumentChunk(
            id="c2",
            document_id="doc1",
            chunk_index=1,
            page_number=2,
            content="O valor total exigido é de R$ 1.500.000,00 acrescido de juros Selic.",
        ),
    ]

    result = svc.answer_query("qual o motivo da glosa de créditos?", chunks)
    assert result["is_grounded"] is True
    assert len(result["citations"]) > 0
    assert result["citations"][0].page_number == 1
    assert "créditos indevidos de ICMS" in result["citations"][0].verbatim_excerpt
    assert "pág. 1" in result["answer"]


def test_anti_hallucination_guardrail():
    svc = TaxRetrievalService()
    chunks = [
        DocumentChunk(
            id="c1",
            document_id="doc1",
            chunk_index=0,
            page_number=1,
            content="Auto de infração referente a ICMS e mercadorias.",
        )
    ]

    # Query completely unrelated to the tax document
    result = svc.answer_query("Qual a previsão do tempo para amanhã em Paris?", chunks)
    assert result["is_grounded"] is False
    assert result["answer"] == "A informação não foi localizada no documento analisado."
    assert len(result["citations"]) == 0


def test_empty_chunks():
    svc = TaxRetrievalService()
    result = svc.answer_query("Qualquer pergunta?", [])
    assert result["is_grounded"] is False
    assert result["answer"] == "A informação não foi localizada no documento analisado."
    assert len(result["citations"]) == 0
