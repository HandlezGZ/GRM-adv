import os
import sys

# Ensure backend can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.database import SessionLocal, init_db
from backend.app.repositories.chat_repository import ChatRepository
from backend.app.repositories.tax_document_repository import TaxDocumentRepository
from backend.app.schemas.extraction import TaxExtractionCreate
from backend.app.schemas.tax_document import TaxDocumentCreate
from backend.app.services.extraction import TaxExtractionService
from backend.app.services.ingestion import PDFIngestionService
from backend.app.services.retrieval import TaxRetrievalService

DOCUMENTS_DATA = [
    {
        "filename": "AIIM_ICMS_SP_4123456.txt",
        "document_type": "AIIM",
        "text": """GOVERNO DO ESTADO DE SÃO PAULO
SECRETARIA DA FAZENDA E PLANEJAMENTO - SEFAZ/SP
DELEGACIA REGIONAL TRIBUTÁRIA DA CAPITAL (DRTC-III)
POSTO FISCAL DA SÉ

AUTO DE INFRAÇÃO E IMPOSIÇÃO DE MULTA - AIIM Nº 4.123.456-7
DATA DA LAVRATURA: 15/02/2024
DATA DA INTIMAÇÃO: 20/02/2024
DATA DE VENCIMENTO: 21/03/2024

1. IDENTIFICAÇÃO DO SUJEITO PASSIVO
AUTUADO: METALÚRGICA PAULISTA DE PRECISÃO S.A.
CNPJ: 33.123.456/0001-80
INSCRIÇÃO ESTADUAL: 110.220.330.440
ENDEREÇO: Avenida Industrial, nº 1.500, Mooca, São Paulo/SP - CEP 03100-000

2. DESCRIÇÃO DOS FATOS E RELATÓRIO FISCAL
No curso de procedimento fiscalizatório realizado no estabelecimento acima qualificado, relativo ao exercício de 2023, apurou-se que o contribuinte creditou-se indevidamente de ICMS destacado em notas fiscais de aquisição de bens destinados ao uso e consumo do próprio estabelecimento, bem como apropriou créditos decorrentes de notas fiscais emitidas por fornecedores declarados inidôneos pela administração tributária paulista.

Conforme demonstrativo analítico anexo a este termo, os lançamentos a crédito na Escrituração Fiscal Digital (EFD-ICMS/IPI) nos livros de Registro de Entradas infringiram diretamente a vedação ao creditamento para mercadorias alheias à atividade-fim ou sem comprovação da efetiva entrada física.

3. DISCRIMINAÇÃO DOS DÉBITOS
TRIBUTO: ICMS
PERÍODO DE APURAÇÃO: 01/2023 a 12/2023
VALOR PRINCIPAL: R$ 1.250.000,00
MULTA DE OFÍCIO (50%): R$ 625.000,00
JUROS SELIC: R$ 180.000,00
VALOR TOTAL: R$ 2.055.000,00

4. FUNDAMENTAÇÃO LEGAL E INFRAÇÕES
Incorreu nas disposições expressas dos seguintes diplomas legais:
- Art. 61 e Art. 66 da Lei Estadual nº 6.374/1989;
- Art. 59 e Art. 527, inciso II, alínea 'a' do Regulamento do ICMS do Estado de São Paulo - RICMS/SP (Decreto Estadual nº 45.490/2000);
- Art. 123 e Art. 161 da Lei Federal nº 5.172/1966 (Código Tributário Nacional - CTN).

5. INTIMAÇÃO E PRAZOS
Fica o contribuinte intimado a recolher os débitos com as reduções legais de multa (50% de desconto para pagamento à vista no prazo de 30 dias) ou apresentar Impugnação Administrativa no prazo improrrogável de 30 (trinta) dias, perante o Tribunal de Impostos e Taxas (TIT/SP), sob pena de inscrição do débito na Dívida Ativa do Estado de São Paulo e imediata execução fiscal.
""",
    },
    {
        "filename": "Notificacao_Lancamento_RFB_IRPJ_CSLL.txt",
        "document_type": "NL",
        "text": """MINISTÉRIO DA FAZENDA
SECRETARIA ESPECIAL DA RECEITA FEDERAL DO BRASIL - RFB
SUPERINTENDÊNCIA REGIONAL DA 8ª REGIÃO FISCAL
DELEGACIA DE JULGAMENTO DA RECEITA FEDERAL EM SÃO PAULO

NOTIFICAÇÃO DE LANÇAMENTO
PROCESSO ADMINISTRATIVO FISCAL (PAF) Nº 10880.720455/2024-12
DATA DA LAVRATURA: 01/03/2024
DATA DA INTIMAÇÃO: 05/03/2024
DATA DE VENCIMENTO: 04/04/2024

1. IDENTIFICAÇÃO DO SUJEITO PASSIVO
CONTRIBUINTE: LOGÍSTICA INTEGRADA NACIONAL LTDA
CNPJ: 44.987.654/0001-22
DOMICÍLIO FISCAL: Alameda Santos, nº 900, Cerqueira César, São Paulo/SP

2. RELATÓRIO FISCAL E ENQUADRAMENTO
Em auditoria realizada nas escriturações fiscais digitais (ECF - Escrituração Contábil Fiscal) do ano-calendário 2022, exercício 2023, apurou-se a dedução indevida de despesas operacionais no Livro de Apuração do Lucro Real (Lalur). O sujeito passivo deduziu amortização de ágio gerado em operação de reestruturação societária entre partes relacionadas ("ágio interno"), sem substrato econômico e desprovido de efetiva transferência patrimonial a terceiros independentes.

Adicionalmente, verificou-se a dedução de despesas com consultoria e bônus a administradores sem a respectiva comprovação da efetiva necessidade e prestação dos serviços para as operações da sociedade empresária.

3. EXIGÊNCIA DO CRÉDITO TRIBUTÁRIO
TRIBUTOS EXIGIDOS: IRPJ e CSLL
PERÍODO DE APURAÇÃO: Ano-Calendário 2022
VALOR PRINCIPAL: R$ 850.000,00
MULTA DE OFÍCIO (75%): R$ 637.500,00
JUROS DE MORA: R$ 95.000,00
TOTAL DO CRÉDITO TRIBUTÁRIO: R$ 1.582.500,00

4. DISPOSITIVOS LEGAIS INFRINGIDOS
- Art. 43 e Art. 44 da Lei Federal nº 5.172/1966 (Código Tributário Nacional - CTN);
- Art. 12 da Lei Federal nº 9.430/1996;
- Art. 20 da Lei Federal nº 9.249/1995;
- Art. 249 e Art. 385 do Regulamento do Imposto sobre a Renda - RIR/2018 (Decreto nº 9.580/2018).

5. DISPOSIÇÕES PROCESSUAIS
O contribuinte tem o prazo de 30 (trinta) dias contados da ciência desta intimação para recolher o crédito lançado ou interpor Impugnação perante a Delegacia da Receita Federal de Julgamento (DRJ), nos termos do Decreto nº 70.235/1972.
""",
    },
    {
        "filename": "Solucao_Consulta_COSIT_98102.txt",
        "document_type": "COSIT",
        "text": """MINISTÉRIO DA FAZENDA
SECRETARIA ESPECIAL DA RECEITA FEDERAL DO BRASIL
SUBSECRETARIA DE TRIBUTAÇÃO E ASSESSORAMENTO
COORDENAÇÃO-GERAL DE TRIBUTAÇÃO - COSIT

SOLUÇÃO DE CONSULTA COSIT Nº 98.102
DATA DA LAVRATURA: 10/01/2024
DATA DA INTIMAÇÃO: 15/01/2024

INTERESSADO: AGROINDÚSTRIA DO VALE S.A.
CNPJ: 55.444.333/0001-77

EMENTA:
TRIBUTO: CONTRIBUIÇÃO PARA O PIS/PASEP E COFINS
REGIME NÃO-CUMULATIVO. CONCEITO DE INSUMOS. BENS E SERVIÇOS EXIGIDOS POR IMPOSIÇÃO LEGAL AMBIENTAL. DIREITO A CRÉDITO.

1. RELATÓRIO DA CONSULTA
A consulente, pessoa jurídica dedicada à industrialização e processamento de produtos agrícolas, submete consulta questionando se as despesas incorridas com tratamento de resíduos poluentes e monitoramento ambiental, exigidas expressamente por licença de operação do órgão ambiental estadual (CETESB), podem ser enquadradas como insumos para fins de creditamento da Contribuição para o PIS/PASEP e da COFINS, à luz do precedente vinculante do Superior Tribunal de Justiça no Recurso Especial nº 1.221.170/PR (Tema 779).

2. FUNDAMENTAÇÃO LEGAL E ENTENDIMENTO DO FISCO
O Superior Tribunal de Justiça assentou que o conceito de insumo para fins do art. 3º, inciso II, das Leis nº 10.637/2002 e 10.833/2003 deve ser aferido à luz dos critérios de essencialidade ou relevância.

Conforme a jurisprudência fixada e a regulamentação do Parecer Normativo Cosit nº 5/2018, consideram-se insumos geradores de créditos os bens ou serviços cuja utilização decorra de imposição legal obrigatória para o regular exercício da atividade industrial.

3. CONCLUSÃO
As despesas efetuadas com contratação de serviços de tratamento de efluentes, descarte de resíduos e exames laboratoriais periódicos, quando exigidas expressamente por norma legal ou regulamentar ambiental para a operação da planta fabril, geram direito ao desconto de créditos de PIS/PASEP e COFINS no regime não-cumulativo.
VALOR TOTAL: R$ 0,00
DISPOSITIVOS APLICÁVEIS: Lei nº 10.637/2002, art. 3º; Lei nº 10.833/2003, art. 3º; Parecer Normativo Cosit nº 5/2018.
""",
    },
]


def seed_database():
    print("[Seed] Initializing database schema...")
    init_db()

    db = SessionLocal()
    doc_repo = TaxDocumentRepository(db)
    chat_repo = ChatRepository(db)
    ingestion_service = PDFIngestionService()
    extraction_service = TaxExtractionService()
    retrieval_service = TaxRetrievalService()

    # Create sample docs directory if not exists
    sample_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "sample_docs")
    )
    os.makedirs(sample_dir, exist_ok=True)

    print(f"[Seed] Seeding {len(DOCUMENTS_DATA)} realistic synthetic tax documents...")

    for item in DOCUMENTS_DATA:
        # Write text file to data/sample_docs/
        file_path = os.path.join(sample_dir, item["filename"])
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(item["text"])

        sha256 = ingestion_service.compute_sha256(item["text"])

        # Check if already present
        existing = doc_repo.get_by_hash(sha256)
        if existing:
            print(f"[Seed] Document {item['filename']} already seeded (ID: {existing.id})")
            continue

        pages = ingestion_service.extract_pages_from_text(item["text"])
        chunks_data = ingestion_service.chunk_document(pages, chunk_size=600, chunk_overlap=100)

        # Create TaxDocument
        doc_in = TaxDocumentCreate(
            filename=item["filename"],
            document_type=item["document_type"],
            raw_text=item["text"],
            file_size_bytes=len(item["text"].encode("utf-8")),
            total_pages=len(pages),
            sha256_hash=sha256,
        )
        created_doc = doc_repo.create(doc_in)
        chunks = doc_repo.create_chunks(created_doc.id, chunks_data)

        # Extract structured entities
        ext_res = extraction_service.extract(item["text"])
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
        doc_repo.save_extraction(ext_in)

        # Create initial chat session and sample Q&A
        session = chat_repo.create_session(
            created_doc.id, title=f"Sessão Inicial - {item['filename']}"
        )

        sample_questions = [
            "Qual o valor total cobrado e os tributos envolvidos?",
            "Qual o prazo para defesa ou pagamento com desconto?",
        ]

        for q in sample_questions:
            chat_repo.add_message(session.id, "user", q)
            answer_dict = retrieval_service.answer_query(q, chunks)
            chat_repo.add_message(
                session.id,
                "assistant",
                answer_dict["answer"],
                citations=[c.model_dump() for c in answer_dict["citations"]],
            )

        print(
            f"[Seed] Successfully ingested {item['filename']} (ID: {created_doc.id}) with {len(chunks)} chunks."
        )

    db.close()
    print("[Seed] Seed process completed successfully!")


if __name__ == "__main__":
    seed_database()
