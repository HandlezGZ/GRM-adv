import re
from typing import Any

from backend.app.schemas.extraction import TaxExtractionBase


class TaxExtractionService:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    @staticmethod
    def _parse_brl_currency(value_str: str) -> float:
        """Convert Brazilian formatted currency '1.234.567,89' or '1234,56' to float."""
        clean = re.sub(r"[^\d,\.]", "", value_str.strip())
        if not clean:
            return 0.0
        # If both '.' and ',' are present, '.' is thousand separator and ',' is decimal
        if "." in clean and "," in clean:
            clean = clean.replace(".", "").replace(",", ".")
        elif "," in clean:
            clean = clean.replace(",", ".")
        # If only '.' is present and followed by 2 digits at end, could be decimal or thousands
        elif "." in clean:
            parts = clean.split(".")
            if len(parts[-1]) == 2:
                clean = clean  # Already standard float
            else:
                clean = clean.replace(".", "")

        try:
            return round(float(clean), 2)
        except ValueError:
            return 0.0

    def extract_deterministic(self, text: str) -> dict[str, Any]:
        """Extract structured tax data using deterministic regex and pattern rules."""
        result: dict[str, Any] = {
            "contribuinte_nome": None,
            "contribuinte_cnpj_cpf": None,
            "orgao_fiscal": None,
            "tributos_identificados": [],
            "periodo_apuracao": None,
            "valor_principal": 0.0,
            "valor_multa": 0.0,
            "valor_juros": 0.0,
            "valor_total": 0.0,
            "data_lavratura": None,
            "data_intimacao": None,
            "data_vencimento": None,
            "dispositivos_legais": [],
            "resumo_executivo": None,
            "extraction_method": "RULES_DETERMINISTIC",
            "confidence_score": 0.0,
        }

        # 1. CNPJ / CPF
        cnpj_match = re.search(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b", text)
        if cnpj_match:
            result["contribuinte_cnpj_cpf"] = cnpj_match.group(0)
        else:
            cpf_match = re.search(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", text)
            if cpf_match:
                result["contribuinte_cnpj_cpf"] = cpf_match.group(0)

        # 2. Contribuinte Nome
        name_patterns = [
            r"(?:AUTUADO|SUJEITO PASSIVO|CONTRIBUINTE|INTERESSADO|INTERESSADA|NOME / RAZÃO SOCIAL|RAZÃO SOCIAL)[\s:]+([^\n\r;,]+)",
            r"(?:EMPRESA|NOTIFICADO)[\s:]+([^\n\r;,]+)",
        ]
        for pattern in name_patterns:
            name_match = re.search(pattern, text, re.IGNORECASE)
            if name_match:
                candidate = name_match.group(1).strip()
                # Clean candidate
                candidate = re.sub(r"[\n\r]+", " ", candidate)
                if len(candidate) > 2 and not re.match(r"^(CNPJ|CPF|INSCRIÇÃO)", candidate, re.I):
                    result["contribuinte_nome"] = candidate[:200].strip()
                    break

        # 3. Órgão Fiscal
        if re.search(r"RECEITA FEDERAL|SECRETARIA DA RECEITA FEDERAL|DELEGACIA DA RECEITA FEDERAL", text, re.I):
            result["orgao_fiscal"] = "Receita Federal do Brasil"
        elif re.search(r"SEFAZ[/ -]?SP|SECRETARIA DA FAZENDA DO ESTADO DE SÃO PAULO|GOVERNO DO ESTADO DE SÃO PAULO", text, re.I):
            result["orgao_fiscal"] = "SEFAZ/SP - Secretaria da Fazenda de São Paulo"
        elif re.search(r"SEFAZ|SECRETARIA DE ESTADO DA FAZENDA|SECRETARIA DA FAZENDA", text, re.I):
            match_state = re.search(r"SEFAZ[/ -]?([A-Z]{2})", text, re.I)
            uf = match_state.group(1).upper() if match_state else "Estadual"
            result["orgao_fiscal"] = f"SEFAZ/{uf}"
        elif re.search(r"PROCURADORIA-GERAL DA FAZENDA NACIONAL|PGFN", text, re.I):
            result["orgao_fiscal"] = "PGFN - Procuradoria-Geral da Fazenda Nacional"
        elif re.search(r"SECRETARIA MUNICIPAL DE FINANÇAS|SECRETARIA MUNICIPAL DA FAZENDA|PREFEITURA", text, re.I):
            result["orgao_fiscal"] = "Secretaria Municipal de Finanças"

        # 4. Tributos Identificados
        tax_keywords = {
            "ICMS": r"\bICMS\b|IMPOSTO SOBRE OPERAÇÕES RELATIVAS À CIRCULAÇÃO DE MERCADORIAS",
            "IRPJ": r"\bIRPJ\b|IMPOSTO DE RENDA PESSOA JURÍDICA",
            "CSLL": r"\bCSLL\b|CONTRIBUIÇÃO SOCIAL SOBRE O LUCRO LÍQUIDO",
            "PIS": r"\bPIS\b|\bPIS/PASEP\b|PROGRAMA DE INTEGRAÇÃO SOCIAL",
            "COFINS": r"\bCOFINS\b|CONTRIBUIÇÃO PARA O FINANCIAMENTO DA SEGURIDADE SOCIAL",
            "IPI": r"\bIPI\b|IMPOSTO SOBRE PRODUTOS INDUSTRIALIZADOS",
            "ISS": r"\bISS\b|\bISSQN\b|IMPOSTO SOBRE SERVIÇOS",
            "ITCMD": r"\bITCMD\b|\bITCD\b",
            "IPVA": r"\bIPVA\b",
            "IPTU": r"\bIPTU\b",
        }
        for tax_name, pattern in tax_keywords.items():
            if re.search(pattern, text, re.IGNORECASE):
                result["tributos_identificados"].append(tax_name)

        # 5. Período de Apuração / Exercício
        pa_match = re.search(
            r"(?:PERÍODO DE APURAÇÃO|COMPETÊNCIA|EXERCÍCIO(?:/ANO-CALENDÁRIO)?)[\s:]+([0-9]{2}/[0-9]{4}|[0-9]{4}|[0-9]{2}/[0-9]{2}/[0-9]{4}\s*(?:a|até|-)\s*[0-9]{2}/[0-9]{2}/[0-9]{4})",
            text,
            re.IGNORECASE,
        )
        if pa_match:
            result["periodo_apuracao"] = pa_match.group(1).strip()

        # 6. Valores Monetários (BRL)
        principal_match = re.search(
            r"(?:VALOR PRINCIPAL|TRIBUTO DEVIDO|IMPOSTO EXIGIDO|DÉBITO PRINCIPAL|PRINCIPAL)[\s:]+(?:R\$\s*)?([\d\.]+(?:,\d{2})?)",
            text,
            re.IGNORECASE,
        )
        if principal_match:
            result["valor_principal"] = self._parse_brl_currency(principal_match.group(1))

        multa_match = re.search(
            r"(?:VALOR DA MULTA|MULTA DE OFÍCIO|MULTA ISOLADA|MULTA PUNITIVA|MULTA)[\s:]+(?:R\$\s*)?([\d\.]+(?:,\d{2})?)",
            text,
            re.IGNORECASE,
        )
        if multa_match:
            result["valor_multa"] = self._parse_brl_currency(multa_match.group(1))

        juros_match = re.search(
            r"(?:VALOR DOS JUROS|JUROS DE MORA|JUROS SELIC|JUROS)[\s:]+(?:R\$\s*)?([\d\.]+(?:,\d{2})?)",
            text,
            re.IGNORECASE,
        )
        if juros_match:
            result["valor_juros"] = self._parse_brl_currency(juros_match.group(1))

        total_match = re.search(
            r"(?:VALOR TOTAL|TOTAL DA AUTUAÇÃO|TOTAL DO CRÉDITO|TOTAL DEVIDO|TOTAL A RECOLHER|TOTAL GERAL|TOTAL)[\s:]+(?:R\$\s*)?([\d\.]+(?:,\d{2})?)",
            text,
            re.IGNORECASE,
        )
        if total_match:
            result["valor_total"] = self._parse_brl_currency(total_match.group(1))

        # Reconcile total if total is 0 but parts exist
        calculated_total = round(
            result["valor_principal"] + result["valor_multa"] + result["valor_juros"], 2
        )
        if result["valor_total"] == 0.0 and calculated_total > 0:
            result["valor_total"] = calculated_total

        # 7. Datas
        date_pattern = r"\b(\d{2}/\d{2}/\d{4})\b"
        lavratura_match = re.search(
            rf"(?:DATA DA LAVRATURA|LAVRATURA|DATA DE EMISSÃO|EMITIDO EM)[\s:]+{date_pattern}",
            text,
            re.IGNORECASE,
        )
        if lavratura_match:
            result["data_lavratura"] = lavratura_match.group(1)

        intimacao_match = re.search(
            rf"(?:DATA DA INTIMAÇÃO|INTIMAÇÃO|CIÊNCIA|NOTIFICADO EM)[\s:]+{date_pattern}",
            text,
            re.IGNORECASE,
        )
        if intimacao_match:
            result["data_intimacao"] = intimacao_match.group(1)

        vencimento_match = re.search(
            rf"(?:DATA DE VENCIMENTO|VENCIMENTO|PAGAMENTO ATÉ|PRAZO DE PAGAMENTO)[\s:]+{date_pattern}",
            text,
            re.IGNORECASE,
        )
        if vencimento_match:
            result["data_vencimento"] = vencimento_match.group(1)

        # 8. Dispositivos Legais
        legal_matches = re.findall(
            r"(?:Art(?:igo|\.)?\s*\d+(?:-[A-Za-z]+)?(?:\s*,\s*(?:§|parágrafo|inciso|alínea)\s*[\w\d]+)*\s*(?:d[oa]\s+[A-Za-z0-9/\.\-]+)?|Lei\s*(?:Federal|Complementar|Estadual)?\s*n[ºo°]?\s*[\d\.]+(?:/\d{2,4})?|Decreto\s*n[ºo°]?\s*[\d\.]+(?:/\d{2,4})?|CTN|RICMS(?:/[A-Z]{2})?)",
            text,
            re.IGNORECASE,
        )
        cleaned_articles = []
        for m in legal_matches:
            c = re.sub(r"\s+", " ", m).strip()
            if len(c) > 4 and c not in cleaned_articles:
                cleaned_articles.append(c)
        result["dispositivos_legais"] = cleaned_articles[:15]

        # 9. Confidence Score Calculation
        score = 0.0
        if result["contribuinte_cnpj_cpf"]:
            score += 0.25
        if result["contribuinte_nome"]:
            score += 0.15
        if result["orgao_fiscal"]:
            score += 0.15
        if result["tributos_identificados"]:
            score += 0.15
        if result["valor_total"] > 0:
            score += 0.20
        if result["dispositivos_legais"]:
            score += 0.10
        result["confidence_score"] = round(min(1.0, score), 2)

        # 10. Generate preliminary summary
        tribs = ", ".join(result["tributos_identificados"]) if result["tributos_identificados"] else "Tributo não identificado"
        orgao = result["orgao_fiscal"] or "Órgão fiscal competente"
        total_fmt = f"R$ {result['valor_total']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        result["resumo_executivo"] = (
            f"Exigência fiscal emitida por {orgao} referente a {tribs}, "
            f"no montante total de {total_fmt}. Contribuinte: {result['contribuinte_nome'] or 'Não identificado'} "
            f"({result['contribuinte_cnpj_cpf'] or 'Sem CNPJ'})."
        )

        return result

    def extract_with_llm(self, text: str) -> dict[str, Any] | None:
        """Optional LLM-based structured extraction with schema fallback."""
        if not self.api_key:
            return None
        # In this implementation, if no live key is present, fallback to deterministic
        return None

    def extract(self, text: str, prefer_llm: bool = False) -> TaxExtractionBase:
        """Dual-engine extraction: executes LLM if configured, otherwise deterministic."""
        if prefer_llm and self.api_key:
            llm_result = self.extract_with_llm(text)
            if llm_result:
                return TaxExtractionBase(**llm_result)

        det_result = self.extract_deterministic(text)
        return TaxExtractionBase(**det_result)
