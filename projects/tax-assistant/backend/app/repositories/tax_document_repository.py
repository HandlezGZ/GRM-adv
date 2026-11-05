from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from backend.app.models.document_chunk import DocumentChunk
from backend.app.models.tax_document import TaxDocument
from backend.app.models.tax_extraction import TaxExtraction
from backend.app.schemas.extraction import TaxExtractionCreate
from backend.app.schemas.tax_document import TaxDocumentCreate


class TaxDocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, doc_in: TaxDocumentCreate) -> TaxDocument:
        db_doc = TaxDocument(
            filename=doc_in.filename,
            document_type=doc_in.document_type,
            sha256_hash=doc_in.sha256_hash,
            file_size_bytes=doc_in.file_size_bytes,
            total_pages=doc_in.total_pages,
            raw_text=doc_in.raw_text,
            status="PROCESSED",
        )
        self.db.add(db_doc)
        self.db.commit()
        self.db.refresh(db_doc)
        return db_doc

    def get_by_id(self, doc_id: str) -> TaxDocument | None:
        return (
            self.db.query(TaxDocument)
            .options(joinedload(TaxDocument.chunks))
            .filter(TaxDocument.id == doc_id)
            .first()
        )

    def get_by_hash(self, sha256_hash: str) -> TaxDocument | None:
        return self.db.query(TaxDocument).filter(TaxDocument.sha256_hash == sha256_hash).first()

    def list_all(
        self, skip: int = 0, limit: int = 100, doc_type: str | None = None
    ) -> list[TaxDocument]:
        query = self.db.query(TaxDocument)
        if doc_type:
            query = query.filter(TaxDocument.document_type == doc_type.upper())
        return query.order_by(TaxDocument.created_at.desc()).offset(skip).limit(limit).all()

    def create_chunks(self, document_id: str, chunks_data: list[dict]) -> list[DocumentChunk]:
        created_chunks = []
        for c in chunks_data:
            chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=c["chunk_index"],
                page_number=c["page_number"],
                content=c["content"],
                token_count=c.get("token_count", len(c["content"].split())),
            )
            self.db.add(chunk)
            created_chunks.append(chunk)
        self.db.commit()
        for chunk in created_chunks:
            self.db.refresh(chunk)
        return created_chunks

    def get_chunks_by_document_id(self, document_id: str) -> list[DocumentChunk]:
        return (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
            .all()
        )

    def save_extraction(self, extraction_in: TaxExtractionCreate) -> TaxExtraction:
        # Check if an extraction already exists for this document
        existing = (
            self.db.query(TaxExtraction)
            .filter(TaxExtraction.document_id == extraction_in.document_id)
            .first()
        )
        if existing:
            existing.contribuinte_nome = extraction_in.contribuinte_nome
            existing.contribuinte_cnpj_cpf = extraction_in.contribuinte_cnpj_cpf
            existing.orgao_fiscal = extraction_in.orgao_fiscal
            existing.tributos_identificados = extraction_in.tributos_identificados
            existing.periodo_apuracao = extraction_in.periodo_apuracao
            existing.valor_principal = extraction_in.valor_principal
            existing.valor_multa = extraction_in.valor_multa
            existing.valor_juros = extraction_in.valor_juros
            existing.valor_total = extraction_in.valor_total
            existing.data_lavratura = extraction_in.data_lavratura
            existing.data_intimacao = extraction_in.data_intimacao
            existing.data_vencimento = extraction_in.data_vencimento
            existing.dispositivos_legais = extraction_in.dispositivos_legais
            existing.resumo_executivo = extraction_in.resumo_executivo
            existing.extraction_method = extraction_in.extraction_method
            existing.confidence_score = extraction_in.confidence_score
            self.db.commit()
            self.db.refresh(existing)
            return existing

        db_ext = TaxExtraction(
            document_id=extraction_in.document_id,
            contribuinte_nome=extraction_in.contribuinte_nome,
            contribuinte_cnpj_cpf=extraction_in.contribuinte_cnpj_cpf,
            orgao_fiscal=extraction_in.orgao_fiscal,
            tributos_identificados=extraction_in.tributos_identificados,
            periodo_apuracao=extraction_in.periodo_apuracao,
            valor_principal=extraction_in.valor_principal,
            valor_multa=extraction_in.valor_multa,
            valor_juros=extraction_in.valor_juros,
            valor_total=extraction_in.valor_total,
            data_lavratura=extraction_in.data_lavratura,
            data_intimacao=extraction_in.data_intimacao,
            data_vencimento=extraction_in.data_vencimento,
            dispositivos_legais=extraction_in.dispositivos_legais,
            resumo_executivo=extraction_in.resumo_executivo,
            extraction_method=extraction_in.extraction_method,
            confidence_score=extraction_in.confidence_score,
        )
        self.db.add(db_ext)
        self.db.commit()
        self.db.refresh(db_ext)
        return db_ext

    def get_latest_extraction(self, document_id: str) -> TaxExtraction | None:
        return (
            self.db.query(TaxExtraction)
            .filter(TaxExtraction.document_id == document_id)
            .order_by(TaxExtraction.created_at.desc())
            .first()
        )

    def get_metrics(self) -> dict:
        total_docs = self.db.query(func.count(TaxDocument.id)).scalar() or 0
        total_pages = self.db.query(func.sum(TaxDocument.total_pages)).scalar() or 0
        total_amount = self.db.query(func.sum(TaxExtraction.valor_total)).scalar() or 0.0
        avg_confidence = (
            self.db.query(func.avg(TaxExtraction.confidence_score)).scalar() or 0.0
        )

        # Distribution by type
        types_q = (
            self.db.query(TaxDocument.document_type, func.count(TaxDocument.id))
            .group_by(TaxDocument.document_type)
            .all()
        )
        docs_by_type = {doc_type: count for doc_type, count in types_q}

        # Taxes distribution
        all_extractions = self.db.query(TaxExtraction.tributos_identificados).all()
        taxes_dist: dict[str, int] = {}
        for ext in all_extractions:
            tributos = ext[0]
            if isinstance(tributos, list):
                for t in tributos:
                    taxes_dist[t] = taxes_dist.get(t, 0) + 1

        return {
            "total_documents": total_docs,
            "total_tax_amount": float(total_amount),
            "total_pages_analyzed": int(total_pages),
            "documents_by_type": docs_by_type,
            "taxes_distribution": taxes_dist,
            "average_confidence_score": round(float(avg_confidence), 2),
        }
