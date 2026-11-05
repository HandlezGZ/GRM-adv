import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class TaxExtraction(Base):
    __tablename__ = "tax_extractions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("tax_documents.id"), nullable=False, index=True)
    contribuinte_nome = Column(String(255), nullable=True)
    contribuinte_cnpj_cpf = Column(String(30), nullable=True)
    orgao_fiscal = Column(String(100), nullable=True)
    tributos_identificados = Column(JSON, default=list, nullable=False)
    periodo_apuracao = Column(String(100), nullable=True)
    valor_principal = Column(Float, default=0.0, nullable=False)
    valor_multa = Column(Float, default=0.0, nullable=False)
    valor_juros = Column(Float, default=0.0, nullable=False)
    valor_total = Column(Float, default=0.0, nullable=False)
    data_lavratura = Column(String(50), nullable=True)
    data_intimacao = Column(String(50), nullable=True)
    data_vencimento = Column(String(50), nullable=True)
    dispositivos_legais = Column(JSON, default=list, nullable=False)
    resumo_executivo = Column(Text, nullable=True)
    extraction_method = Column(String(30), default="RULES_DETERMINISTIC", nullable=False)
    confidence_score = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    document = relationship("TaxDocument", back_populates="extractions")
