from datetime import datetime, timedelta

from backend.app.models.tax_document import TaxDocument
from backend.app.models.tax_extraction import TaxExtraction
from backend.app.schemas.extraction import ExecutiveSummaryResponse


class TaxSummaryService:
    @staticmethod
    def _parse_date(date_str: str | None) -> datetime | None:
        if not date_str:
            return None
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None

    @staticmethod
    def _format_date(dt: datetime | None) -> str | None:
        if not dt:
            return None
        return dt.strftime("%d/%m/%Y")

    def calculate_deadlines(self, extraction: TaxExtraction) -> dict[str, str | None]:
        intimacao_dt = self._parse_date(extraction.data_intimacao)
        vencimento_dt = self._parse_date(extraction.data_vencimento)

        # Default Brazilian administrative defense deadline: 30 days from intimação
        if intimacao_dt:
            impugnacao_dt = intimacao_dt + timedelta(days=30)
            prazo_desconto_dt = intimacao_dt + timedelta(days=30)
        elif vencimento_dt:
            impugnacao_dt = vencimento_dt
            prazo_desconto_dt = vencimento_dt
        else:
            impugnacao_dt = None
            prazo_desconto_dt = None

        return {
            "data_intimacao": extraction.data_intimacao,
            "data_vencimento": extraction.data_vencimento or self._format_date(vencimento_dt),
            "prazo_impugnacao_administrativa": self._format_date(impugnacao_dt),
            "prazo_pagamento_com_desconto": self._format_date(prazo_desconto_dt),
        }

    def assess_risk(self, extraction: TaxExtraction) -> str:
        total = extraction.valor_total
        multa = extraction.valor_multa
        principal = extraction.valor_principal

        # Ratio of fine to principal
        multa_ratio = (multa / principal) if principal > 0 else 0.0

        if total >= 1_000_000.0 or multa_ratio >= 1.0:
            return "ALTO"
        if total >= 100_000.0 or multa_ratio >= 0.5:
            return "MEDIO"
        return "BAIXO"

    def identify_allegation_thesis(self, text: str, doc_type: str) -> str:
        text_upper = text.upper()
        if "CRÉDITO INDEVIDO" in text_upper or "CREDITO INDEVIDO" in text_upper:
            return "Glosa de créditos tributários apropriados indevidamente pelo contribuinte."
        if "OMISSÃO DE RECEITA" in text_upper or "OMISSAO DE RECEITA" in text_upper:
            return "Omissão de receitas tributáveis constatada através de cruzamento eletrônico fiscal."
        if "FALTA DE RECOLHIMENTO" in text_upper or "NÃO RECOLHIMENTO" in text_upper:
            return "Falta de recolhimento integral do tributo apurado no período de competência."
        if "DESPESA INDEDUTÍVEL" in text_upper or "DESPESAS INDEDUTIVEIS" in text_upper:
            return "Glosa de despesas operacionais indedutíveis para fins de apuração da base de cálculo do IRPJ/CSLL."
        if "OBRIGAÇÃO ACESSÓRIA" in text_upper or "OBRIGACAO ACESSORIA" in text_upper:
            return "Descumprimento de obrigação tributária acessória ou inexatidão de declarações fiscais."
        if doc_type == "COSIT":
            return "Consulta formal quanto à correta interpretação da legislação tributária federal aplicável aos fatos narrados."

        return "Exigência de crédito tributário e aplicação de penalidades fiscais decorrentes de procedimento de fiscalização."

    def generate_summary(
        self,
        document: TaxDocument,
        extraction: TaxExtraction,
    ) -> ExecutiveSummaryResponse:
        deadlines = self.calculate_deadlines(extraction)
        risk = self.assess_risk(extraction)
        thesis = self.identify_allegation_thesis(document.raw_text, document.document_type)

        total_fmt = f"R$ {extraction.valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        principal_fmt = f"R$ {extraction.valor_principal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        multa_fmt = f"R$ {extraction.valor_multa:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        juros_fmt = f"R$ {extraction.valor_juros:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        trib_str = ", ".join(extraction.tributos_identificados) if extraction.tributos_identificados else "Não especificado"
        arts_str = ", ".join(extraction.dispositivos_legais[:5]) if extraction.dispositivos_legais else "Nenhum dispositivo mapeado"

        resumo_md = (
            f"### Resumo Executivo Fiscal - {document.filename}\n\n"
            f"- **Tipo Documental:** {document.document_type}\n"
            f"- **Órgão Autuante:** {extraction.orgao_fiscal or 'Não identificado'}\n"
            f"- **Contribuinte Autuado:** {extraction.contribuinte_nome or 'Não identificado'} "
            f"(CNPJ/CPF: {extraction.contribuinte_cnpj_cpf or 'Não identificado'})\n"
            f"- **Tributos Exigidos:** {trib_str}\n"
            f"- **Montante Total:** {total_fmt} (Principal: {principal_fmt} | Multa: {multa_fmt} | Juros: {juros_fmt})\n\n"
            f"#### Fato Gerador e Tese de Acusação\n{thesis}\n\n"
            f"#### Fundamentação Normativa\n{arts_str}\n\n"
            f"#### Prazos Processuais e Contingência\n"
            f"- **Grau de Risco:** `{risk}`\n"
            f"- **Intimação:** {deadlines.get('data_intimacao') or 'Pendente'}\n"
            f"- **Prazo Limite para Impugnação Administrativa (30 dias):** {deadlines.get('prazo_impugnacao_administrativa') or 'A apurar'}\n"
            f"- **Vencimento com Desconto:** {deadlines.get('prazo_pagamento_com_desconto') or 'A apurar'}\n"
        )

        return ExecutiveSummaryResponse(
            document_id=document.id,
            filename=document.filename,
            document_type=document.document_type,
            contribuinte_nome=extraction.contribuinte_nome,
            contribuinte_cnpj_cpf=extraction.contribuinte_cnpj_cpf,
            orgao_fiscal=extraction.orgao_fiscal,
            tributos=extraction.tributos_identificados or [],
            total_autuado=extraction.valor_total,
            valor_principal=extraction.valor_principal,
            valor_multa=extraction.valor_multa,
            valor_juros=extraction.valor_juros,
            prazos=deadlines,
            tese_acusacao=thesis,
            dispositivos_legais=extraction.dispositivos_legais or [],
            grau_risco=risk,
            resumo_texto=resumo_md,
        )
