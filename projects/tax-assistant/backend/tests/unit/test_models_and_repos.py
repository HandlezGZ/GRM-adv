import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base
from backend.app.repositories.chat_repository import ChatRepository
from backend.app.repositories.tax_document_repository import TaxDocumentRepository
from backend.app.schemas.extraction import TaxExtractionCreate
from backend.app.schemas.tax_document import TaxDocumentCreate


@pytest.fixture
def db_session():
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


def test_tax_document_and_chunks(db_session):
    repo = TaxDocumentRepository(db_session)

    # Create Document
    doc_in = TaxDocumentCreate(
        filename="auto_infracao_icms.pdf",
        document_type="AIIM",
        raw_text="Auto de Infração e Imposição de Multa - ICMS SP",
        file_size_bytes=1024,
        total_pages=2,
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    )
    doc = repo.create(doc_in)
    assert doc.id is not None
    assert doc.status == "PROCESSED"
    assert doc.document_type == "AIIM"

    # Add Chunks
    chunks_data = [
        {"chunk_index": 0, "page_number": 1, "content": "Chunk page 1 content"},
        {"chunk_index": 1, "page_number": 2, "content": "Chunk page 2 content"},
    ]
    chunks = repo.create_chunks(doc.id, chunks_data)
    assert len(chunks) == 2
    assert chunks[0].page_number == 1
    assert chunks[1].chunk_index == 1

    # Fetch document and verify chunks
    fetched = repo.get_by_id(doc.id)
    assert fetched is not None
    assert len(fetched.chunks) == 2

    # Fetch by hash
    by_hash = repo.get_by_hash(doc.sha256_hash)
    assert by_hash is not None
    assert by_hash.id == doc.id


def test_tax_extraction_save_and_update(db_session):
    repo = TaxDocumentRepository(db_session)
    doc_in = TaxDocumentCreate(
        filename="notificacao_irpj.pdf",
        document_type="NL",
        raw_text="Notificação de Lançamento",
        sha256_hash="abc123hash",
    )
    doc = repo.create(doc_in)

    ext_in = TaxExtractionCreate(
        document_id=doc.id,
        contribuinte_nome="Empresa Fictícia Ltda",
        contribuinte_cnpj_cpf="12.345.678/0001-90",
        orgao_fiscal="Receita Federal do Brasil",
        tributos_identificados=["IRPJ", "CSLL"],
        valor_principal=100000.0,
        valor_multa=75000.0,
        valor_juros=15000.0,
        valor_total=190000.0,
        dispositivos_legais=["Art. 43 do CTN", "Lei 9.249/95"],
        confidence_score=0.92,
    )
    extraction = repo.save_extraction(ext_in)
    assert extraction.id is not None
    assert extraction.valor_total == 190000.0
    assert "IRPJ" in extraction.tributos_identificados

    # Update extraction
    ext_in.valor_multa = 80000.0
    ext_in.valor_total = 195000.0
    updated = repo.save_extraction(ext_in)
    assert updated.id == extraction.id
    assert updated.valor_multa == 80000.0

    latest = repo.get_latest_extraction(doc.id)
    assert latest is not None
    assert latest.valor_total == 195000.0


def test_chat_session_and_messages(db_session):
    doc_repo = TaxDocumentRepository(db_session)
    chat_repo = ChatRepository(db_session)

    doc = doc_repo.create(
        TaxDocumentCreate(
            filename="consulta.pdf",
            document_type="COSIT",
            raw_text="Solução de Consulta COSIT",
            sha256_hash="def456hash",
        )
    )

    session = chat_repo.create_session(doc.id, title="Análise COSIT PIS/COFINS")
    assert session.id is not None
    assert session.document_id == doc.id

    # Add messages
    user_msg = chat_repo.add_message(session.id, "user", "Qual o entendimento do Fisco?")
    assert user_msg.id is not None
    assert user_msg.role == "user"

    citations = [
        {"chunk_id": "chunk-1", "page_number": 1, "verbatim_excerpt": "O entendimento consolidado..."}
    ]
    assistant_msg = chat_repo.add_message(
        session.id,
        "assistant",
        "O Fisco esclarece que insumos geram crédito.",
        citations=citations,
    )
    assert assistant_msg.id is not None
    assert len(assistant_msg.citations) == 1
    assert assistant_msg.citations[0]["page_number"] == 1

    history = chat_repo.get_history(session.id)
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[1].role == "assistant"


def test_metrics_calculation(db_session):
    repo = TaxDocumentRepository(db_session)
    doc1 = repo.create(
        TaxDocumentCreate(
            filename="doc1.pdf",
            document_type="AIIM",
            raw_text="AIIM text",
            total_pages=3,
            sha256_hash="hash1",
        )
    )
    repo.save_extraction(
        TaxExtractionCreate(
            document_id=doc1.id,
            tributos_identificados=["ICMS"],
            valor_total=50000.0,
            confidence_score=0.9,
        )
    )

    metrics = repo.get_metrics()
    assert metrics["total_documents"] == 1
    assert metrics["total_tax_amount"] == 50000.0
    assert metrics["total_pages_analyzed"] == 3
    assert metrics["documents_by_type"].get("AIIM") == 1
    assert metrics["taxes_distribution"].get("ICMS") == 1
    assert metrics["average_confidence_score"] == 0.9
