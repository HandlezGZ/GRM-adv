import logging

from sqlalchemy.orm import Session

from backend.app.db.session import Base, SessionLocal, engine
from backend.app.repositories.eval_repository import EvalRepository
from backend.app.schemas.eval_schemas import (
    EvalDatasetCreate,
    EvalTestCaseCreate,
    PromptVersionCreate,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")

GOLDEN_DATASET_NAME = "Golden Dataset - Direito Tributário Corporativo"
GOLDEN_DATASET_DESC = (
    "Casos de teste sintéticos e controlados cobrindo PIS/COFINS, ICMS-ST, retenções federais, "
    "IPI, ITCMD, Simples Nacional e jurisprudência dos Tribunais Superiores."
)

GOLDEN_TEST_CASES = [
    {
        "title": "Aproveitamento de Créditos de PIS/COFINS sobre Insumos",
        "input_query": "Uma indústria química pode apurar créditos de PIS e COFINS sobre despesas com tratamento de efluentes exigidos por órgão ambiental?",
        "context_document": (
            "Nos termos do julgamento do Recurso Especial 1.221.170/PR (Tema 779/STJ), o conceito de insumo "
            "para fins de creditamento de PIS/COFINS na sistemática não cumulativa (Leis 10.637/2002 e 10.833/2003) "
            "deve ser aferido pelos critérios da essencialidade ou relevância. Despesas incorridas por imposição legal, "
            "como o tratamento de efluentes imposto por normas ambientais para viabilizar a atividade produtiva, "
            "são consideradas insumos essenciais, gerando direito a crédito."
        ),
        "expected_output": (
            "Sim. Conforme entendimento firmado pelo STJ no Tema 779 (REsp 1.221.170/PR), despesas decorrentes "
            "de imposição legal (como tratamento obrigatório de efluentes) são consideradas insumos por relevância "
            "ou essencialidade, autorizando o creditamento de PIS e COFINS no regime não cumulativo."
        ),
        "required_keywords": ["Tema 779", "STJ", "essencialidade", "crédito", "PIS", "COFINS", "10.833"],
        "forbidden_terms": ["vedado o crédito", "impossível creditar", "não cumulativo sem insumos"],
    },
    {
        "title": "Prazo de Recolhimento e Retenção de Contribuições Federais (CSRF)",
        "input_query": "Qual é a data limite para recolhimento da CSRF (PIS/COFINS/CSLL 4,65%) retida na prestação de serviços?",
        "context_document": (
            "Conforme a Lei nº 10.833/2003, art. 30 e art. 35 (com redação pela Lei nº 13.137/2015), os valores "
            "retidos na quinzena deverão ser recolhidos de forma unificada até o último dia útil do segundo decêndio "
            "do mês subsequente àquele em que tiver ocorrido o pagamento à pessoa jurídica fornecedora dos serviços (dia 20)."
        ),
        "expected_output": (
            "O recolhimento da CSRF (4,65%) deve ocorrer até o último dia útil do segundo decêndio do mês subsequente "
            "ao do pagamento dos serviços prestados (em regra, dia 20), nos termos do art. 35 da Lei 10.833/2003, "
            "alterado pela Lei 13.137/2015."
        ),
        "required_keywords": ["último dia útil", "segundo decêndio", "mês subsequente", "dia 20", "Lei 10.833/2003"],
        "forbidden_terms": ["dia 10", "dia 15", "mesmo dia", "prazo decadencial"],
    },
    {
        "title": "Cálculo do ICMS em Substituição Tributária (ICMS-ST) e MVA",
        "input_query": "Como deve ser calculada a base de cálculo do ICMS-ST quando há aplicação de Margem de Valor Agregado (MVA)?",
        "context_document": (
            "Na sistemática do ICMS Substituição Tributária progressiva (art. 8º da Lei Complementar nº 87/1996), "
            "a base de cálculo do imposto devido por substituição tributária é obtida somando-se ao valor da operação "
            "própria (preço do produto + frete + seguro + IPI + outros encargos) o percentual correspondente à MVA "
            "(Margem de Valor Agregado). Sobre essa base aplica-se a alíquota interna, deduzindo-se o ICMS da operação própria."
        ),
        "expected_output": (
            "A base de cálculo do ICMS-ST é apurada somando ao valor total da operação própria (produto, IPI, frete e encargos) "
            "a MVA estabelecida em convênio ou protocolo. Aplica-se a alíquota interna sobre esse montante e subtrai-se o ICMS "
            "próprio destacado pelo substituto."
        ),
        "required_keywords": ["base de cálculo", "MVA", "alíquota interna", "deduzindo", "operação própria", "LC 87/1996"],
        "forbidden_terms": ["sem dedução", "apenas sobre o frete", "isenção total"],
    },
    {
        "title": "Tributação sobre Licenciamento e Cessão de Softwares (ISS vs. ICMS)",
        "input_query": "Incide ICMS ou ISS sobre o licenciamento de software por download ou SaaS?",
        "context_document": (
            "O Supremo Tribunal Federal, no julgamento conjunto das ADIs 5659 e 5958, pacificou que o licenciamento "
            "ou a cessão de direito de uso de programas de computador (software padronizado ou por encomenda), inclusive "
            "em nuvem (SaaS) ou via download, está sujeito exclusivamente ao ISSQN (de competência municipal), "
            "sendo inconstitucional a incidência de ICMS."
        ),
        "expected_output": (
            "Incide exclusivamente o ISS (imposto municipal). O STF decidiu nas ADIs 5659 e 5958 que o licenciamento "
            "ou cessão de software, inclusive por download ou SaaS, configura prestação de serviço sujeita ao ISS, "
            "afastando terminantemente a cobrança de ICMS."
        ),
        "required_keywords": ["ISS", "STF", "ADIs 5659", "inconstitucional", "afastando", "ICMS"],
        "forbidden_terms": ["incide apenas ICMS", "bitributação autorizada", "isenção tributária municipal"],
    },
    {
        "title": "Não Incidência de ITCMD sobre Planos de Previdência VGBL e PGBL",
        "input_query": "O Estado pode cobrar ITCMD sobre valores transferidos aos beneficiários de VGBL em caso de falecimento do titular?",
        "context_document": (
            "Segundo pacífica orientação do Superior Tribunal de Justiça (STJ), os planos de previdência privada na modalidade "
            "VGBL (Vida Gerador de Benefício Livre) possuem natureza securitária de seguro de pessoas, não integrando a herança "
            "nem o monte partilhável por força do art. 794 do Código Civil. Logo, não incide o ITCMD sobre a transmissão "
            "aos beneficiários decorrente de morte do titular."
        ),
        "expected_output": (
            "Não. Conforme pacificado pelo STJ, o VGBL ostenta natureza securitária (art. 794 do Código Civil) e não "
            "integra a herança ou monte partilhável, razão pela qual é indevida a cobrança de ITCMD pelos Estados sobre "
            "o repasse aos beneficiários."
        ),
        "required_keywords": ["não incide", "ITCMD", "VGBL", "STJ", "natureza securitária", "art. 794"],
        "forbidden_terms": ["é devida a cobrança", "incide integralmente", "tributação estadual válida"],
    },
    {
        "title": "Creditamento de IPI na Aquisição de Matérias-Primas Isentas ou com Alíquota Zero",
        "input_query": "O contribuinte tem direito a creditar IPI na entrada de matérias-primas isentas ou sujeitas à alíquota zero?",
        "context_document": (
            "O Plenário do STF, ao julgar o Tema 322 da Repercussão Geral (RE 562.980), fixou a tese de que inexiste "
            "direito a crédito presumido de IPI relativamente à aquisição de insumos ou matérias-primas isentas, sujeitas "
            "à alíquota zero ou não tributadas, ressalvada expressa previsão legal em sentido contrário, pois não houve ônus "
            "tributário a ser compensado no princípio da não cumulatividade."
        ),
        "expected_output": (
            "Não há direito a crédito de IPI na aquisição de insumos isentos ou com alíquota zero. O STF pacificou no Tema 322 "
            "(RE 562.980) que a não cumulatividade não gera crédito presumido quando a etapa anterior foi desonerada, "
            "salvo expressa determinação legal."
        ),
        "required_keywords": ["inexiste direito", "Tema 322", "STF", "RE 562.980", "não cumulatividade", "alíquota zero"],
        "forbidden_terms": ["direito irrestrito", "crédito garantido", "compensação automática"],
    },
    {
        "title": "Exclusão do Simples Nacional em Razão de Débitos Tributários Pendentes",
        "input_query": "A existência de débitos tributários sem exigibilidade suspensa autoriza a exclusão da pessoa jurídica do Simples Nacional?",
        "context_document": (
            "De acordo com o art. 17, inciso V, da Lei Complementar nº 123/2006, não poderão recolher os impostos e "
            "contribuições na forma do Simples Nacional as pessoas jurídicas que possuam débito com o Instituto Nacional "
            "do Seguro Social (INSS), ou com as Fazendas Públicas Federal, Estadual ou Municipal, cuja exigibilidade não "
            "esteja suspensa. A Fazenda deve previamente intimar a empresa concedendo prazo de 30 dias para regularização."
        ),
        "expected_output": (
            "Sim. Nos termos do art. 17, inciso V, da LC 123/2006, débitos tributários com exigibilidade não suspensa constituem "
            "óbice à permanência no Simples Nacional. A pessoa jurídica deve ser notificada com prazo de 30 dias para regularizar "
            "antes da concretização da exclusão."
        ),
        "required_keywords": ["LC 123/2006", "art. 17", "exigibilidade suspensa", "regularização", "30 dias"],
        "forbidden_terms": ["impossível excluir", "imunidade total", "débito prescinde de regularização"],
    },
    {
        "title": "Denúncia Espontânea e Afastamento de Multa de Mora e Ofício (CTN art. 138)",
        "input_query": "O recolhimento integral do tributo em atraso com juros, antes de qualquer procedimento fiscal, exclui a multa moratória?",
        "context_document": (
            "Nos termos do art. 138 do Código Tributário Nacional (CTN) e da Súmula 360 do STJ, a denúncia espontânea "
            "acompanhada do pagamento do tributo devido e dos juros de mora, efetuada antes do início de qualquer medida "
            "de fiscalização, exclui a responsabilidade por infrações, afastando tanto a multa punitiva quanto a multa de mora. "
            "Todavia, no caso de tributo sujeito a lançamento por homologação previamente declarado pelo contribuinte (DCTF), "
            "não se aplica o benefício (Súmula 360/STJ)."
        ),
        "expected_output": (
            "Em regra, sim. Conforme o art. 138 do CTN, a denúncia espontânea com recolhimento total e juros antes de procedimento "
            "fiscal afasta a multa moratória e punitiva. Contudo, se o débito já havia sido previamente declarado (ex.: via DCTF), "
            "a Súmula 360 do STJ afasta o benefício da denúncia espontânea."
        ),
        "required_keywords": ["art. 138", "CTN", "denúncia espontânea", "multa", "Súmula 360", "STJ"],
        "forbidden_terms": ["multa sempre exigida", "sem juros", "anistia ampla sem condições"],
    },
    {
        "title": "Tributação de Juros de Mora de Depósito Judicial pelo IRPJ e CSLL",
        "input_query": "Incide IRPJ e CSLL sobre a taxa Selic recebida em decorrência de repetição de indébito tributário ou levantamento de depósito?",
        "context_document": (
            "O Supremo Tribunal Federal, no julgamento do Tema 1.062 da Repercussão Geral (RE 1.063.187), fixou a tese "
            "de que 'É inconstitucional a incidência do IRPJ e da CSLL sobre os valores atinentes à taxa Selic recebidos em "
            "razão de repetição de indébito tributário'. Tal entendimento fundamenta-se na natureza estritamente indenizatória "
            "dos juros de mora, que visam a recomposição de danos emergentes, não constituindo acréscimo patrimonial."
        ),
        "expected_output": (
            "Não incide. O STF, no Tema 1.062 (RE 1.063.187), declarou inconstitucional a tributação pelo IRPJ e CSLL sobre a "
            "taxa Selic na repetição de indébito tributário, reconhecendo a natureza indenizatória dos juros de mora por danos "
            "emergentes, afastando acréscimo patrimonial."
        ),
        "required_keywords": ["Tema 1.062", "STF", "RE 1.063.187", "inconstitucional", "IRPJ", "CSLL", "indenizatória"],
        "forbidden_terms": ["incide regularmente", "tributação legítima", "lucro operacional tributável"],
    },
    {
        "title": "Prazo Prescricional para Execução Fiscal de Crédito Tributário",
        "input_query": "Qual é o prazo para a Fazenda Pública ajuizar a execução fiscal e quando ocorre sua interrupção?",
        "context_document": (
            "Nos termos do art. 174 do Código Tributário Nacional (CTN), a ação para a cobrança do crédito tributário prescreve "
            "em 5 (cinco) anos, contados da data da sua constituição definitiva. A prescrição interrompe-se pelo despacho do "
            "juiz que ordenar a citação em execução fiscal (redação da LC 118/2005), retroagindo à data da propositura da ação "
            "(Súmula 106 do STJ)."
        ),
        "expected_output": (
            "O prazo prescricional é de 5 anos contados da constituição definitiva do crédito (art. 174 do CTN). A interrupção "
            "ocorre pelo despacho judicial ordenatório da citação (LC 118/2005), com efeitos retroativos à propositura da ação "
            "quando observada a Súmula 106 do STJ."
        ),
        "required_keywords": ["5 anos", "art. 174", "CTN", "constituição definitiva", "despacho", "citação"],
        "forbidden_terms": ["10 anos", "20 anos", "imprescritível", "interrupção automática sem juiz"],
    },
]

PROMPT_VERSIONS = [
    {
        "name": "prompt_tributario_v1",
        "version": "1.0.0",
        "system_prompt": (
            "Você é um consultor tributário experiente. Responda à dúvida do usuário de forma concisa "
            "e direta, utilizando exclusivamente as informações fornecidas no documento de contexto."
        ),
        "template_text": (
            "Contexto:\n{context}\n\n"
            "Pergunta:\n{query}\n\n"
            "Instruções:\nForneça uma resposta jurídica objetiva baseada no contexto acima."
        ),
        "temperature": 0.1,
    },
    {
        "name": "prompt_tributario_v2",
        "version": "2.0.0",
        "system_prompt": (
            "Você é um auditor sênior e especialista em contencioso tributário. Responda à dúvida com rigor técnico "
            "absoluto. Cite textualmente os artigos de lei, precedentes (Temas/Súmulas) e tribunais presentes no contexto. "
            "Não extrapole o contexto nem infira regras não documentadas."
        ),
        "template_text": (
            "Documento de Referência Jurídica:\n{context}\n\n"
            "Consulta Formulada:\n{query}\n\n"
            "Diretrizes Obrigatórias:\n"
            "1. Fundamente com as normas e julgados citados no contexto.\n"
            "2. Seja explícito quanto à autorização ou vedação do procedimento.\n"
            "3. Se faltar contexto, aponte a limitação sem alucinar normas inexistentes."
        ),
        "temperature": 0.0,
    },
]


def seed_database(db: Session) -> dict:
    Base.metadata.create_all(bind=engine)
    repo = EvalRepository(db)

    # 1. Dataset
    dataset = repo.get_dataset_by_name(GOLDEN_DATASET_NAME)
    if not dataset:
        dataset = repo.create_dataset(
            EvalDatasetCreate(
                name=GOLDEN_DATASET_NAME,
                description=GOLDEN_DATASET_DESC,
                category="TRIBUTARIO",
            )
        )
        logger.info(f"Created Golden Dataset: {dataset.name} (id={dataset.id})")
    else:
        logger.info(f"Dataset already exists: {dataset.name}")

    # 2. Test cases
    existing_cases = repo.list_test_cases(dataset.id)
    existing_titles = {c.title for c in existing_cases}
    created_cases_count = 0

    for tc_data in GOLDEN_TEST_CASES:
        if tc_data["title"] not in existing_titles:
            repo.create_test_case(
                dataset.id,
                EvalTestCaseCreate(
                    title=tc_data["title"],
                    input_query=tc_data["input_query"],
                    context_document=tc_data["context_document"],
                    expected_output=tc_data["expected_output"],
                    required_keywords=tc_data["required_keywords"],
                    forbidden_terms=tc_data["forbidden_terms"],
                ),
            )
            created_cases_count += 1

    logger.info(f"Seeded {created_cases_count} test cases into {dataset.name}")

    # 3. Prompt versions
    created_prompts_count = 0
    for pv_data in PROMPT_VERSIONS:
        existing_pv = repo.get_prompt_by_name_and_version(pv_data["name"], pv_data["version"])
        if not existing_pv:
            repo.create_prompt_version(
                PromptVersionCreate(
                    name=pv_data["name"],
                    version=pv_data["version"],
                    system_prompt=pv_data["system_prompt"],
                    template_text=pv_data["template_text"],
                    temperature=pv_data["temperature"],
                )
            )
            created_prompts_count += 1

    logger.info(f"Seeded {created_prompts_count} prompt versions")

    return {
        "dataset_id": dataset.id,
        "dataset_name": dataset.name,
        "total_test_cases": len(repo.list_test_cases(dataset.id)),
        "prompts_seeded": created_prompts_count,
    }


def main():
    db = SessionLocal()
    try:
        result = seed_database(db)
        print(f"Seed completed successfully: {result}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
