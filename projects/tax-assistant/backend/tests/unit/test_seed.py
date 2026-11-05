from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base
from backend.app.repositories.tax_document_repository import TaxDocumentRepository
from backend.app.schemas.tax_document import TaxDocumentCreate
from backend.app.services.ingestion import PDFIngestionService
from scripts.seed_tax_data import DOCUMENTS_DATA


def test_seed_documents_data_integrity():
    assert len(DOCUMENTS_DATA) == 3
    filenames = [d["filename"] for d in DOCUMENTS_DATA]
    assert "AIIM_ICMS_SP_4123456.txt" in filenames
    assert "Notificacao_Lancamento_RFB_IRPJ_CSLL.txt" in filenames
    assert "Solucao_Consulta_COSIT_98102.txt" in filenames


def test_seed_flow_in_memory():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSession()

    repo = TaxDocumentRepository(db)
    ingestion = PDFIngestionService()

    for item in DOCUMENTS_DATA:
        pages = ingestion.extract_pages_from_text(item["text"])
        doc = repo.create(
            TaxDocumentCreate(
                filename=item["filename"],
                document_type=item["document_type"],
                raw_text=item["text"],
                file_size_bytes=len(item["text"]),
                total_pages=len(pages),
                sha256_hash=ingestion.compute_sha256(item["text"]),
            )
        )
        assert doc.id is not None

    all_docs = repo.list_all()
    assert len(all_docs) == 3
    db.close()
