from backend.app.services.extraction import TaxExtractionService


def test_brl_currency_parsing():
    svc = TaxExtractionService()
    assert svc._parse_brl_currency("R$ 1.250.450,50") == 1250450.50
    assert svc._parse_brl_currency("R$ 500,00") == 500.0
    assert svc._parse_brl_currency("10.000,00") == 10000.0
    assert svc._parse_brl_currency("250.75") == 250.75
    assert svc._parse_brl_currency("") == 0.0


def test_deterministic_aiim_extraction():
    svc = TaxExtractionService()
    sample_aiim_text = """
    GOVERNO DO ESTADO DE SÃO PAULO
    SECRETARIA DA FAZENDA E PLANEJAMENTO - SEFAZ/SP
    DELEGACIA REGIONAL TRIBUTÁRIA DE SÃO PAULO

    AUTO DE INFRAÇÃO E IMPOSIÇÃO DE MULTA - AIIM Nº 4.123.456-7

    1. IDENTIFICAÇÃO DO SUJEITO PASSIVO
    AUTUADO: ALPHA COMÉRCIO E LOGÍSTICA LTDA
    CNPJ: 12.345.678/0001-90
    INSCRIÇÃO ESTADUAL: 111.222.333.444

    2. DISCRIMINAÇÃO DOS DÉBITOS
    TRIBUTO: ICMS
    PERÍODO DE APURAÇÃO: 01/2023 a 12/2023
    VALOR PRINCIPAL: R$ 1.000.000,00
    MULTA DE OFÍCIO: R$ 500.000,00
    JUROS SELIC: R$ 120.000,00
    VALOR TOTAL: R$ 1.620.000,00

    3. DISPOSITIVOS LEGAIS INFRINGIDOS
    Incorreu nas disposições do Art. 61 do RICMS/SP e Art. 527 da Lei Estadual nº 6.374/1989.

    4. DATAS E PRAZOS
    DATA DA LAVRATURA: 15/03/2024
    DATA DA INTIMAÇÃO: 20/03/2024
    DATA DE VENCIMENTO: 19/04/2024
    """

    res = svc.extract(sample_aiim_text)
    assert res.contribuinte_cnpj_cpf == "12.345.678/0001-90"
    assert "ALPHA COMÉRCIO" in res.contribuinte_nome
    assert "SEFAZ/SP" in res.orgao_fiscal
    assert "ICMS" in res.tributos_identificados
    assert res.valor_principal == 1000000.0
    assert res.valor_multa == 500000.0
    assert res.valor_juros == 120000.0
    assert res.valor_total == 1620000.0
    assert res.data_lavratura == "15/03/2024"
    assert res.data_intimacao == "20/03/2024"
    assert res.data_vencimento == "19/04/2024"
    assert any("Art. 61" in art for art in res.dispositivos_legais)
    assert res.confidence_score >= 0.8
    assert res.resumo_executivo is not None


def test_deterministic_notificacao_irpj():
    svc = TaxExtractionService()
    sample_nl_text = """
    MINISTÉRIO DA FAZENDA
    SECRETARIA ESPECIAL DA RECEITA FEDERAL DO BRASIL
    DELEGACIA DE JULGAMENTO

    NOTIFICAÇÃO DE LANÇAMENTO
    PROCESSO ADMINISTRATIVO FISCAL Nº 10880.720123/2024-55

    CONTRIBUINTE: BETA INDÚSTRIA QUÍMICA S.A.
    CNPJ: 98.765.432/0001-10
    EXERCÍCIO: 2023

    TRIBUTO EXIGIDO: IRPJ e CSLL
    VALOR PRINCIPAL: R$ 400.000,00
    MULTA DE OFÍCIO: R$ 300.000,00
    JUROS DE MORA: R$ 40.000,00
    TOTAL DO CRÉDITO: R$ 740.000,00

    INFRAÇÃO LEGAL: Art. 43 do CTN e Art. 12 da Lei nº 9.430/1996.
    NOTIFICADO EM: 10/01/2024
    PAGAMENTO ATÉ: 09/02/2024
    """

    res = svc.extract(sample_nl_text)
    assert res.contribuinte_cnpj_cpf == "98.765.432/0001-10"
    assert "BETA" in res.contribuinte_nome
    assert "Receita Federal" in res.orgao_fiscal
    assert "IRPJ" in res.tributos_identificados
    assert "CSLL" in res.tributos_identificados
    assert res.valor_principal == 400000.0
    assert res.valor_multa == 300000.0
    assert res.valor_juros == 40000.0
    assert res.valor_total == 740000.0
    assert res.data_intimacao == "10/01/2024"
    assert res.data_vencimento == "09/02/2024"
    assert any("Art. 43" in art for art in res.dispositivos_legais)
    assert res.confidence_score >= 0.8


def test_fallback_when_no_llm_key():
    svc = TaxExtractionService(api_key=None)
    # Test prefer_llm=True gracefully falls back to deterministic
    res = svc.extract("AUTO DE INFRAÇÃO ICMS VALOR TOTAL: R$ 50.000,00 CNPJ: 11.222.333/0001-44", prefer_llm=True)
    assert res.extraction_method == "RULES_DETERMINISTIC"
    assert res.valor_total == 50000.0
    assert res.contribuinte_cnpj_cpf == "11.222.333/0001-44"
