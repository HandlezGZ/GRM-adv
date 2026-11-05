from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaxExtractionBase(BaseModel):
    contribuinte_nome: str | None = None
    contribuinte_cnpj_cpf: str | None = None
    orgao_fiscal: str | None = None
    tributos_identificados: list[str] = Field(default_factory=list)
    periodo_apuracao: str | None = None
    valor_principal: float = 0.0
    valor_multa: float = 0.0
    valor_juros: float = 0.0
    valor_total: float = 0.0
    data_lavratura: str | None = None
    data_intimacao: str | None = None
    data_vencimento: str | None = None
    dispositivos_legais: list[str] = Field(default_factory=list)
    resumo_executivo: str | None = None
    extraction_method: str = "RULES_DETERMINISTIC"
    confidence_score: float = 0.0


class TaxExtractionCreate(TaxExtractionBase):
    document_id: str


class TaxExtractionRead(TaxExtractionBase):
    id: str
    document_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExecutiveSummaryResponse(BaseModel):
    document_id: str
    filename: str
    document_type: str
    contribuinte_nome: str | None = None
    contribuinte_cnpj_cpf: str | None = None
    orgao_fiscal: str | None = None
    tributos: list[str] = Field(default_factory=list)
    total_autuado: float = 0.0
    valor_principal: float = 0.0
    valor_multa: float = 0.0
    valor_juros: float = 0.0
    prazos: dict[str, str | None] = Field(default_factory=dict)
    tese_acusacao: str
    dispositivos_legais: list[str] = Field(default_factory=list)
    grau_risco: str  # BAIXO, MEDIO, ALTO
    resumo_texto: str
