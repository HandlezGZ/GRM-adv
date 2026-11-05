from backend.app.models.tax_document import TaxDocument
from backend.app.models.tax_extraction import TaxExtraction
from backend.app.services.summary import TaxSummaryService


def test_calculate_deadlines():
    svc = TaxSummaryService()
    ext = TaxExtraction(
        data_intimacao="10/04/2024",
        data_vencimento="10/05/2024",
    )
    deadlines = svc.calculate_deadlines(ext)
    assert deadlines["data_intimacao"] == "10/04/2024"
    assert deadlines["prazo_impugnacao_administrativa"] == "10/05/2024"


def test_assess_risk_high():
    svc = TaxSummaryService()
    ext = TaxExtraction(
        valor_principal=800000.0,
        valor_multa=800000.0,
        valor_total=1600000.0,
    )
    assert svc.assess_risk(ext) == "ALTO"


def test_assess_risk_medium_and_low():
    svc = TaxSummaryService()
    ext_med = TaxExtraction(
        valor_principal=100000.0,
        valor_multa=50000.0,
        valor_total=150000.0,
    )
    assert svc.assess_risk(ext_med) == "MEDIO"

    ext_low = TaxExtraction(
        valor_principal=20000.0,
        valor_multa=4000.0,
        valor_total=24000.0,
    )
    assert svc.assess_risk(ext_low) == "BAIXO"


def test_identify_allegation_thesis():
    svc = TaxSummaryService()
    assert "Glosa de créditos" in svc.identify_allegation_thesis("Apurou-se crédito indevido de ICMS", "AIIM")
    assert "despesas operacionais indedutíveis" in svc.identify_allegation_thesis("glosa de despesa indedutível no Lalur", "NL")
    assert "Consulta formal" in svc.identify_allegation_thesis("Ementa da consulta COSIT", "COSIT")


def test_generate_summary_integration():
    svc = TaxSummaryService()
    doc = TaxDocument(
        id="doc-test-123",
        filename="aiim_icms.pdf",
        document_type="AIIM",
        raw_text="Auto de Infração por crédito indevido de ICMS.",
    )
    ext = TaxExtraction(
        document_id=doc.id,
        contribuinte_nome="Empresa ABC",
        contribuinte_cnpj_cpf="11.222.333/0001-44",
        orgao_fiscal="SEFAZ/SP",
        tributos_identificados=["ICMS"],
        valor_principal=1500000.0,
        valor_multa=750000.0,
        valor_juros=150000.0,
        valor_total=2400000.0,
        data_intimacao="01/03/2024",
        dispositivos_legais=["Art. 61 do RICMS/SP"],
    )

    summary = svc.generate_summary(doc, ext)
    assert summary.document_id == "doc-test-123"
    assert summary.grau_risco == "ALTO"
    assert "Glosa de créditos" in summary.tese_acusacao
    assert "Resumo Executivo Fiscal" in summary.resumo_texto
    assert "R$ 2.400.000,00" in summary.resumo_texto
    assert summary.prazos["prazo_impugnacao_administrativa"] == "31/03/2024"
