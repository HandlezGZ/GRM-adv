import io

import pytest
from pypdf import PdfWriter

from backend.app.services.ingestion import PDFExtractionError, PDFIngestionService


def create_sample_pdf(num_pages: int = 1) -> bytes:
    writer = PdfWriter()
    for _ in range(num_pages):
        writer.add_blank_page(width=595, height=842)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()



def test_sha256_computation():
    svc = PDFIngestionService()
    hash1 = svc.compute_sha256(b"Auto de Infracao")
    hash2 = svc.compute_sha256("Auto de Infracao")
    assert hash1 == hash2
    assert len(hash1) == 64


def test_document_type_detection():
    svc = PDFIngestionService()
    assert (
        svc.detect_document_type("Auto de Infração e Imposição de Multa - AIIM", "doc.pdf")
        == "AIIM"
    )
    assert svc.detect_document_type("Notificação de Lançamento IRPJ", "") == "NL"
    assert (
        svc.detect_document_type("Solução de Consulta COSIT nº 123", "parecer.pdf")
        == "COSIT"
    )
    assert svc.detect_document_type("DARF - Código de Receita 0561", "") == "DARF"
    assert (
        svc.detect_document_type("Certidão Negativa de Débitos Tributários CND", "")
        == "CND"
    )
    assert (
        svc.detect_document_type("Contrato de Prestação de Serviços", "contrato.pdf")
        == "OUTRO"
    )


def test_extract_pages_from_text():
    svc = PDFIngestionService()
    # Test with form feeds
    raw = "Página 1: Introdução do auto fiscal.\fPágina 2: Quadro de demonstrativo de débitos."
    pages = svc.extract_pages_from_text(raw)
    assert len(pages) == 2
    assert pages[0]["page_number"] == 1
    assert "Página 1" in pages[0]["text"]
    assert pages[1]["page_number"] == 2
    assert "Página 2" in pages[1]["text"]


def test_extract_pages_from_text_partitioning():
    svc = PDFIngestionService()
    long_text = "\n\n".join([f"Parágrafo fiscal número {i} com detalhes sobre a autuação." for i in range(50)])
    pages = svc.extract_pages_from_text(long_text, page_char_limit=400)
    assert len(pages) > 1
    assert pages[0]["page_number"] == 1
    assert pages[1]["page_number"] == 2


def test_chunk_document_overlap_and_indexing():
    svc = PDFIngestionService()
    pages = [
        {"page_number": 1, "text": "Este é o primeiro texto da página 1 contendo fatos da infração tributária apurada pelo auditor fiscal."},
        {"page_number": 2, "text": "Na segunda página temos os valores devidos e os artigos da lei infringidos pelo sujeito passivo."},
    ]
    chunks = svc.chunk_document(pages, chunk_size=50, chunk_overlap=10)
    assert len(chunks) >= 2
    assert chunks[0]["page_number"] == 1
    assert chunks[0]["chunk_index"] == 0
    assert chunks[-1]["page_number"] == 2
    assert chunks[-1]["chunk_index"] == len(chunks) - 1
    assert "content" in chunks[0]
    assert chunks[0]["token_count"] > 0


def test_extract_pages_from_pdf_corrupted():
    svc = PDFIngestionService()
    with pytest.raises(PDFExtractionError):
        svc.extract_pages_from_pdf(b"corrupted invalid pdf data")

    with pytest.raises(PDFExtractionError):
        svc.extract_pages_from_pdf(b"")


def test_extract_pages_from_valid_pdf_structure():
    svc = PDFIngestionService()
    pdf_bytes = create_sample_pdf(num_pages=2)
    pages = svc.extract_pages_from_pdf(pdf_bytes)
    assert len(pages) == 2
    assert pages[0]["page_number"] == 1
    assert pages[1]["page_number"] == 2

