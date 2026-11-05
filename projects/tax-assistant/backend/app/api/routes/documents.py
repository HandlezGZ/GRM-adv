from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.repositories.tax_document_repository import TaxDocumentRepository
from backend.app.schemas.extraction import (
    ExecutiveSummaryResponse,
    TaxExtractionCreate,
    TaxExtractionRead,
)
from backend.app.schemas.tax_document import (
    TaxDocumentCreate,
    TaxDocumentRead,
    TaxDocumentSummaryItem,
)
from backend.app.services.extraction import TaxExtractionService
from backend.app.services.ingestion import PDFExtractionError, PDFIngestionService
from backend.app.services.summary import TaxSummaryService

router = APIRouter(prefix="/documents", tags=["Documents"])
ingestion_service = PDFIngestionService()
extraction_service = TaxExtractionService()
summary_service = TaxSummaryService()


@router.post("/upload", response_model=TaxDocumentRead)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    repo = TaxDocumentRepository(db)
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")

    filename = file.filename or "uploaded_document.pdf"
    is_pdf = filename.lower().endswith(".pdf") or file.content_type == "application/pdf"

    try:
        if is_pdf:
            pages = ingestion_service.extract_pages_from_pdf(contents)
            raw_text = "\n\n".join(p["text"] for p in pages)
        else:
            raw_text = contents.decode("utf-8", errors="replace")
            pages = ingestion_service.extract_pages_from_text(raw_text)

        sha256 = ingestion_service.compute_sha256(contents)
        doc_type = ingestion_service.detect_document_type(raw_text, filename)

        # Check existing by hash
        existing = repo.get_by_hash(sha256)
        if existing:
            return existing

        doc_in = TaxDocumentCreate(
            filename=filename,
            document_type=doc_type,
            raw_text=raw_text,
            file_size_bytes=len(contents),
            total_pages=len(pages),
            sha256_hash=sha256,
        )
        created_doc = repo.create(doc_in)

        # Chunk and persist
        chunks_data = ingestion_service.chunk_document(pages)
        repo.create_chunks(created_doc.id, chunks_data)

        # Auto-extract structured data
        ext_res = extraction_service.extract(raw_text)
        ext_in = TaxExtractionCreate(
            document_id=created_doc.id,
            contribuinte_nome=ext_res.contribuinte_nome,
            contribuinte_cnpj_cpf=ext_res.contribuinte_cnpj_cpf,
            orgao_fiscal=ext_res.orgao_fiscal,
            tributos_identificados=ext_res.tributos_identificados,
            periodo_apuracao=ext_res.periodo_apuracao,
            valor_principal=ext_res.valor_principal,
            valor_multa=ext_res.valor_multa,
            valor_juros=ext_res.valor_juros,
            valor_total=ext_res.valor_total,
            data_lavratura=ext_res.data_lavratura,
            data_intimacao=ext_res.data_intimacao,
            data_vencimento=ext_res.data_vencimento,
            dispositivos_legais=ext_res.dispositivos_legais,
            resumo_executivo=ext_res.resumo_executivo,
            extraction_method=ext_res.extraction_method,
            confidence_score=ext_res.confidence_score,
        )
        repo.save_extraction(ext_in)

        return repo.get_by_id(created_doc.id)

    except PDFExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento do documento: {str(e)}")


class TextDocumentPayload:
    pass


from pydantic import BaseModel  # noqa: E402


class TextDocumentRequest(BaseModel):
    filename: str
    text: str
    document_type: str | None = None


@router.post("/text", response_model=TaxDocumentRead)
def intake_text_document(
    payload: TextDocumentRequest,
    db: Session = Depends(get_db),
):
    repo = TaxDocumentRepository(db)
    raw_text = payload.text.strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="Texto do documento vazio.")

    sha256 = ingestion_service.compute_sha256(raw_text)
    existing = repo.get_by_hash(sha256)
    if existing:
        return existing

    doc_type = payload.document_type or ingestion_service.detect_document_type(
        raw_text, payload.filename
    )
    pages = ingestion_service.extract_pages_from_text(raw_text)

    doc_in = TaxDocumentCreate(
        filename=payload.filename,
        document_type=doc_type,
        raw_text=raw_text,
        file_size_bytes=len(raw_text.encode("utf-8")),
        total_pages=len(pages),
        sha256_hash=sha256,
    )
    created_doc = repo.create(doc_in)
    chunks_data = ingestion_service.chunk_document(pages)
    repo.create_chunks(created_doc.id, chunks_data)

    ext_res = extraction_service.extract(raw_text)
    ext_in = TaxExtractionCreate(
        document_id=created_doc.id,
        contribuinte_nome=ext_res.contribuinte_nome,
        contribuinte_cnpj_cpf=ext_res.contribuinte_cnpj_cpf,
        orgao_fiscal=ext_res.orgao_fiscal,
        tributos_identificados=ext_res.tributos_identificados,
        periodo_apuracao=ext_res.periodo_apuracao,
        valor_principal=ext_res.valor_principal,
        valor_multa=ext_res.valor_multa,
        valor_juros=ext_res.valor_juros,
        valor_total=ext_res.valor_total,
        data_lavratura=ext_res.data_lavratura,
        data_intimacao=ext_res.data_intimacao,
        data_vencimento=ext_res.data_vencimento,
        dispositivos_legais=ext_res.dispositivos_legais,
        resumo_executivo=ext_res.resumo_executivo,
        extraction_method=ext_res.extraction_method,
        confidence_score=ext_res.confidence_score,
    )
    repo.save_extraction(ext_in)

    return repo.get_by_id(created_doc.id)


@router.get("", response_model=list[TaxDocumentSummaryItem])
def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    doc_type: str | None = Query(None),
    db: Session = Depends(get_db),
):
    repo = TaxDocumentRepository(db)
    return repo.list_all(skip=skip, limit=limit, doc_type=doc_type)


@router.get("/{document_id}", response_model=TaxDocumentRead)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
):
    repo = TaxDocumentRepository(db)
    doc = repo.get_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento fiscal não encontrado.")
    return doc


@router.post("/{document_id}/extract", response_model=TaxExtractionRead)
def extract_document(
    document_id: str,
    force_recompute: bool = Query(False),
    db: Session = Depends(get_db),
):
    repo = TaxDocumentRepository(db)
    doc = repo.get_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento fiscal não encontrado.")

    if not force_recompute:
        latest = repo.get_latest_extraction(document_id)
        if latest:
            return latest

    ext_res = extraction_service.extract(doc.raw_text)
    ext_in = TaxExtractionCreate(
        document_id=doc.id,
        contribuinte_nome=ext_res.contribuinte_nome,
        contribuinte_cnpj_cpf=ext_res.contribuinte_cnpj_cpf,
        orgao_fiscal=ext_res.orgao_fiscal,
        tributos_identificados=ext_res.tributos_identificados,
        periodo_apuracao=ext_res.periodo_apuracao,
        valor_principal=ext_res.valor_principal,
        valor_multa=ext_res.valor_multa,
        valor_juros=ext_res.valor_juros,
        valor_total=ext_res.valor_total,
        data_lavratura=ext_res.data_lavratura,
        data_intimacao=ext_res.data_intimacao,
        data_vencimento=ext_res.data_vencimento,
        dispositivos_legais=ext_res.dispositivos_legais,
        resumo_executivo=ext_res.resumo_executivo,
        extraction_method=ext_res.extraction_method,
        confidence_score=ext_res.confidence_score,
    )
    saved = repo.save_extraction(ext_in)
    return saved


@router.get("/{document_id}/summary", response_model=ExecutiveSummaryResponse)
def get_document_summary(
    document_id: str,
    db: Session = Depends(get_db),
):
    repo = TaxDocumentRepository(db)
    doc = repo.get_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento fiscal não encontrado.")

    extraction = repo.get_latest_extraction(document_id)
    if not extraction:
        # Generate extraction on the fly
        ext_res = extraction_service.extract(doc.raw_text)
        ext_in = TaxExtractionCreate(
            document_id=doc.id,
            contribuinte_nome=ext_res.contribuinte_nome,
            contribuinte_cnpj_cpf=ext_res.contribuinte_cnpj_cpf,
            orgao_fiscal=ext_res.orgao_fiscal,
            tributos_identificados=ext_res.tributos_identificados,
            periodo_apuracao=ext_res.periodo_apuracao,
            valor_principal=ext_res.valor_principal,
            valor_multa=ext_res.valor_multa,
            valor_juros=ext_res.valor_juros,
            valor_total=ext_res.valor_total,
            data_lavratura=ext_res.data_lavratura,
            data_intimacao=ext_res.data_intimacao,
            data_vencimento=ext_res.data_vencimento,
            dispositivos_legais=ext_res.dispositivos_legais,
            resumo_executivo=ext_res.resumo_executivo,
            extraction_method=ext_res.extraction_method,
            confidence_score=ext_res.confidence_score,
        )
        extraction = repo.save_extraction(ext_in)

    return summary_service.generate_summary(doc, extraction)
