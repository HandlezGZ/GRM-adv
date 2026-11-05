export const SAMPLE_DOCUMENTS = [
  {
    id: "doc-aiim-sp-4123456",
    filename: "AIIM_ICMS_SP_4123456.txt",
    document_type: "AIIM",
    total_pages: 3,
    file_size_bytes: 2356,
    sha256_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    status: "PROCESSED",
    created_at: "2024-02-15T10:30:00Z",
    raw_text: `GOVERNO DO ESTADO DE SÃO PAULO
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
Fica o contribuinte intimado a recolher os débitos com as reduções legais de multa (50% de desconto para pagamento à vista no prazo de 30 dias) ou apresentar Impugnação Administrativa no prazo improrrogável de 30 (trinta) dias, perante o Tribunal de Impostos e Taxas (TIT/SP), sob pena de inscrição do débito na Dívida Ativa do Estado de São Paulo e imediata execução fiscal.`,
    extraction: {
      id: "ext-aiim-1",
      document_id: "doc-aiim-sp-4123456",
      contribuinte_nome: "METALÚRGICA PAULISTA DE PRECISÃO S.A.",
      contribuinte_cnpj_cpf: "33.123.456/0001-80",
      orgao_fiscal: "SECRETARIA DA FAZENDA E PLANEJAMENTO - SEFAZ/SP",
      tributos_identificados: ["ICMS"],
      periodo_apuracao: "01/2023 a 12/2023",
      valor_principal: 1250000.0,
      valor_multa: 625000.0,
      valor_juros: 180000.0,
      valor_total: 2055000.0,
      data_lavratura: "15/02/2024",
      data_intimacao: "20/02/2024",
      data_vencimento: "21/03/2024",
      dispositivos_legais: [
        "Art. 61 e Art. 66 da Lei Estadual nº 6.374/1989",
        "Art. 59 e Art. 527, inciso II do RICMS/SP",
        "Art. 123 e Art. 161 do Código Tributário Nacional (CTN)"
      ],
      resumo_executivo: "Autuação fiscal por glosa de créditos indevidos de ICMS em aquisições para uso e consumo e notas fiscais de fornecedores inidôneos.",
      extraction_method: "RULES_DETERMINISTIC",
      confidence_score: 0.96,
      created_at: "2024-02-15T10:35:00Z"
    },
    summary: {
      document_id: "doc-aiim-sp-4123456",
      filename: "AIIM_ICMS_SP_4123456.txt",
      document_type: "AIIM",
      contribuinte_nome: "METALÚRGICA PAULISTA DE PRECISÃO S.A.",
      contribuinte_cnpj_cpf: "33.123.456/0001-80",
      orgao_fiscal: "SECRETARIA DA FAZENDA E PLANEJAMENTO - SEFAZ/SP",
      tributos: ["ICMS"],
      total_autuado: 2055000.0,
      valor_principal: 1250000.0,
      valor_multa: 625000.0,
      valor_juros: 180000.0,
      prazos: {
        data_intimacao: "20/02/2024",
        data_vencimento: "21/03/2024",
        prazo_impugnacao_administrativa: "21/03/2024",
        prazo_pagamento_com_desconto: "21/03/2024"
      },
      tese_acusacao: "Glosa de créditos tributários apropriados indevidamente pelo contribuinte referente a bens alheios à atividade-fim e fornecedores inidôneos.",
      dispositivos_legais: [
        "Art. 61 e Art. 66 da Lei Estadual nº 6.374/1989",
        "Art. 59 e Art. 527, inciso II do RICMS/SP",
        "Art. 123 e Art. 161 do CTN"
      ],
      grau_risco: "ALTO",
      resumo_texto: `### Resumo Executivo Fiscal - AIIM_ICMS_SP_4123456.txt

- **Tipo Documental:** AIIM (Auto de Infração e Imposição de Multa)
- **Órgão Autuante:** SECRETARIA DA FAZENDA E PLANEJAMENTO - SEFAZ/SP
- **Contribuinte Autuado:** METALÚRGICA PAULISTA DE PRECISÃO S.A. (CNPJ: 33.123.456/0001-80)
- **Tributos Exigidos:** ICMS
- **Montante Total:** R$ 2.055.000,00 (Principal: R$ 1.250.000,00 | Multa: R$ 625.000,00 | Juros: R$ 180.000,00)

#### Fato Gerador e Tese de Acusação
Glosa de créditos tributários apropriados indevidamente pelo contribuinte decorrentes de aquisição de bens para uso e consumo e notas fiscais emitidas por estabelecimentos declarados inidôneos.

#### Fundamentação Normativa
Art. 61 e 66 da Lei Paulista 6.374/89 c/c Art. 527 do RICMS/SP e Art. 161 do CTN.

#### Prazos Processuais e Contingência
- **Grau de Risco:** ALTO (exigência superior a R$ 1.000.000,00 com multa de 50%)
- **Data da Intimação:** 20/02/2024
- **Prazo Limite para Impugnação Administrativa (30 dias):** 21/03/2024
- **Vencimento com Desconto de 50% na Multa:** 21/03/2024`
    },
    chunks: [
      {
        id: "chk-1",
        document_id: "doc-aiim-sp-4123456",
        chunk_index: 0,
        page_number: 1,
        content: "AUTO DE INFRAÇÃO E IMPOSIÇÃO DE MULTA - AIIM Nº 4.123.456-7. DATA DA LAVRATURA: 15/02/2024. DATA DA INTIMAÇÃO: 20/02/2024. AUTUADO: METALÚRGICA PAULISTA DE PRECISÃO S.A. CNPJ: 33.123.456/0001-80.",
        token_count: 55,
        created_at: "2024-02-15T10:30:00Z"
      },
      {
        id: "chk-2",
        document_id: "doc-aiim-sp-4123456",
        chunk_index: 1,
        page_number: 2,
        content: "DISCRIMINAÇÃO DOS DÉBITOS: TRIBUTO: ICMS. PERÍODO DE APURAÇÃO: 01/2023 a 12/2023. VALOR PRINCIPAL: R$ 1.250.000,00. MULTA DE OFÍCIO (50%): R$ 625.000,00. JUROS SELIC: R$ 180.000,00. VALOR TOTAL: R$ 2.055.000,00.",
        token_count: 62,
        created_at: "2024-02-15T10:30:00Z"
      },
      {
        id: "chk-3",
        document_id: "doc-aiim-sp-4123456",
        chunk_index: 2,
        page_number: 3,
        content: "INTIMAÇÃO E PRAZOS: Fica o contribuinte intimado a recolher os débitos com as reduções legais de multa ou apresentar Impugnação Administrativa no prazo improrrogável de 30 (trinta) dias perante o Tribunal de Impostos e Taxas (TIT/SP).",
        token_count: 58,
        created_at: "2024-02-15T10:30:00Z"
      }
    ]
  },
  {
    id: "doc-rfb-nl-2024-098",
    filename: "Notificacao_Lancamento_RFB_IRPJ_CSLL.txt",
    document_type: "NL",
    total_pages: 2,
    file_size_bytes: 2153,
    sha256_hash: "7d1b3294cfa5848bb01e06fa492cb2c9f91a9f029019f2a96996ba0c8efae241",
    status: "PROCESSED",
    created_at: "2024-03-01T14:15:00Z",
    raw_text: `MINISTÉRIO DA FAZENDA
SECRETARIA ESPECIAL DA RECEITA FEDERAL DO BRASIL - RFB
DELEGACIA ESPECIAL DE MAIORES CONTRIBUINTES (DEMAC/SP)

NOTIFICAÇÃO DE LANÇAMENTO Nº 08123/2024/DEMAC
DATA DA LAVRATURA: 01/03/2024
DATA DA INTIMAÇÃO: 05/03/2024
DATA DE VENCIMENTO: 04/04/2024

1. DADOS CADASTRAIS DO SUJEITO PASSIVO
CONTRIBUINTE: NOVA ERA LOGÍSTICA & DISTRIBUIÇÃO LTDA
CNPJ: 12.345.678/0001-90
REGIME DE TRIBUTAÇÃO: LUCRO REAL ANUAL

2. MOTIVAÇÃO E RELATÓRIO DO LANÇAMENTO DE OFÍCIO
Através de procedimento de fiscalização e auditoria fiscal contábil nas escriturações ECF e DCTF relativas ao ano-calendário de 2022, constatou-se a dedução indevida de despesas operacionais não necessárias e sem comprovação hábil documental, resultando em subavaliação do Lucro Real e da Base de Cálculo da Contribuição Social sobre o Lucro Líquido.

3. DEMONSTRATIVO DE EXIGÊNCIAS
TRIBUTOS: IRPJ e CSLL
VALOR PRINCIPAL (IRPJ): R$ 420.000,00
VALOR PRINCIPAL (CSLL): R$ 150.000,00
VALOR PRINCIPAL TOTAL: R$ 570.000,00
MULTA DE OFÍCIO (75%): R$ 427.500,00
JUROS DE MORA SELIC: R$ 68.400,00
VALOR CONSOLIDADO: R$ 1.065.900,00

4. DISPOSITIVOS LEGAIS INVOCADOS
- Art. 47 da Lei nº 4.506/1964;
- Art. 311 do Decreto Federal nº 9.580/2018 (Regulamento do Imposto de Renda - RIR/2018);
- Art. 44 da Lei nº 9.430/1996;
- Lei Federal nº 7.689/1988 (CSLL).

5. DISPOSIÇÕES PROCESSUAIS
O contribuinte dispõe do prazo de 30 (trinta) dias a contar da intimação para efetuar o pagamento integral com benefício de redução da penalidade legal ou apresentar impugnação à Delegacia da Receita Federal do Brasil de Julgamento (DRJ).`,
    extraction: {
      id: "ext-nl-2",
      document_id: "doc-rfb-nl-2024-098",
      contribuinte_nome: "NOVA ERA LOGÍSTICA & DISTRIBUIÇÃO LTDA",
      contribuinte_cnpj_cpf: "12.345.678/0001-90",
      orgao_fiscal: "SECRETARIA ESPECIAL DA RECEITA FEDERAL DO BRASIL - RFB",
      tributos_identificados: ["IRPJ", "CSLL"],
      periodo_apuracao: "Exercício 2022",
      valor_principal: 570000.0,
      valor_multa: 427500.0,
      valor_juros: 68400.0,
      valor_total: 1065900.0,
      data_lavratura: "01/03/2024",
      data_intimacao: "05/03/2024",
      data_vencimento: "04/04/2024",
      dispositivos_legais: [
        "Art. 47 da Lei nº 4.506/1964",
        "Art. 311 do Decreto Federal nº 9.580/2018 (RIR/2018)",
        "Art. 44 da Lei nº 9.430/1996",
        "Lei Federal nº 7.689/1988"
      ],
      resumo_executivo: "Lançamento de ofício por dedução indevida de despesas sem comprovação hábil no Lucro Real e base da CSLL.",
      extraction_method: "RULES_DETERMINISTIC",
      confidence_score: 0.94,
      created_at: "2024-03-01T14:20:00Z"
    },
    summary: {
      document_id: "doc-rfb-nl-2024-098",
      filename: "Notificacao_Lancamento_RFB_IRPJ_CSLL.txt",
      document_type: "NL",
      contribuinte_nome: "NOVA ERA LOGÍSTICA & DISTRIBUIÇÃO LTDA",
      contribuinte_cnpj_cpf: "12.345.678/0001-90",
      orgao_fiscal: "SECRETARIA ESPECIAL DA RECEITA FEDERAL DO BRASIL - RFB",
      tributos: ["IRPJ", "CSLL"],
      total_autuado: 1065900.0,
      valor_principal: 570000.0,
      valor_multa: 427500.0,
      valor_juros: 68400.0,
      prazos: {
        data_intimacao: "05/03/2024",
        data_vencimento: "04/04/2024",
        prazo_impugnacao_administrativa: "04/04/2024",
        prazo_pagamento_com_desconto: "04/04/2024"
      },
      tese_acusacao: "Glosa de despesas operacionais indedutíveis para fins de apuração da base de cálculo do IRPJ/CSLL.",
      dispositivos_legais: [
        "Art. 47 da Lei nº 4.506/1964",
        "Art. 311 do RIR/2018",
        "Art. 44 da Lei nº 9.430/1996"
      ],
      grau_risco: "ALTO",
      resumo_texto: `### Resumo Executivo Fiscal - Notificacao_Lancamento_RFB_IRPJ_CSLL.txt

- **Tipo Documental:** Notificação de Lançamento (NL)
- **Órgão Autuante:** RECEITA FEDERAL DO BRASIL - RFB
- **Contribuinte Autuado:** NOVA ERA LOGÍSTICA & DISTRIBUIÇÃO LTDA (CNPJ: 12.345.678/0001-90)
- **Tributos Exigidos:** IRPJ, CSLL
- **Montante Total:** R$ 1.065.900,00 (Principal: R$ 570.000,00 | Multa 75%: R$ 427.500,00 | Juros: R$ 68.400,00)

#### Fato Gerador e Tese de Acusação
Dedução irregular de despesas operacionais sem documentação comprobatória com subavaliação do Lucro Real e da apuração da CSLL.

#### Prazos Processuais e Contingência
- **Grau de Risco:** ALTO
- **Data da Intimação:** 05/03/2024
- **Prazo Limite para Impugnação Administrativa (30 dias):** 04/04/2024`
    },
    chunks: [
      {
        id: "chk-nl-1",
        document_id: "doc-rfb-nl-2024-098",
        chunk_index: 0,
        page_number: 1,
        content: "NOTIFICAÇÃO DE LANÇAMENTO Nº 08123/2024/DEMAC. CONTRIBUINTE: NOVA ERA LOGÍSTICA & DISTRIBUIÇÃO LTDA. CNPJ: 12.345.678/0001-90. DATA DA INTIMAÇÃO: 05/03/2024.",
        token_count: 48,
        created_at: "2024-03-01T14:15:00Z"
      },
      {
        id: "chk-nl-2",
        document_id: "doc-rfb-nl-2024-098",
        chunk_index: 1,
        page_number: 2,
        content: "DEMONSTRATIVO DE EXIGÊNCIAS: TRIBUTOS: IRPJ e CSLL. VALOR PRINCIPAL TOTAL: R$ 570.000,00. MULTA DE OFÍCIO (75%): R$ 427.500,00. JUROS DE MORA SELIC: R$ 68.400,00. VALOR CONSOLIDADO: R$ 1.065.900,00.",
        token_count: 59,
        created_at: "2024-03-01T14:15:00Z"
      }
    ]
  },
  {
    id: "doc-cosit-98102",
    filename: "Solucao_Consulta_COSIT_98102.txt",
    document_type: "COSIT",
    total_pages: 2,
    file_size_bytes: 2107,
    sha256_hash: "2c79f90f23cf9911e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934c",
    status: "PROCESSED",
    created_at: "2024-01-20T09:00:00Z",
    raw_text: `MINISTÉRIO DA FAZENDA
SECRETARIA ESPECIAL DA RECEITA FEDERAL DO BRASIL
COORDENAÇÃO-GERAL DE TRIBUTAÇÃO - COSIT

SOLUÇÃO DE CONSULTA Nº 98.102 - COSIT
ASSUNTO: CONTRIBUIÇÃO PARA O PIS/PASEP E COFINS
EMENTA: NÃO CUMULATIVIDADE. CRÉDITOS. INSUMOS. FRETES NA TRANSFERÊNCIA ENTRE ESTABELECIMENTOS.

1. RELATÓRIO
A pessoa jurídica consulente, atuante na indústria de transformação de plásticos e polímeros, formula consulta quanto à viabilidade de apuração de créditos da não cumulatividade do PIS e da COFINS sobre os dispêndios incorridos na contratação de fretes de produtos acabados entre estabelecimentos da mesma empresa (transferência interestadual da fábrica para os centros de distribuição).

2. FUNDAMENTOS
Conforme jurisprudência vinculante fixada pelo Superior Tribunal de Justiça no Recurso Especial nº 1.221.170/PR sob o rito dos recursos repetitivos (Tema 779), o conceito de insumo para fins de creditamento das contribuições deve ser aferido pelos critérios da essencialidade ou relevância.
O frete de produtos acabados entre estabelecimentos da mesma empresa não integra o processo produtivo, configurando despesa posterior à finalização da fabricação, razão pela qual não se amolda à hipótese de creditamento prevista no Art. 3º, inciso II da Lei nº 10.637/2002 e da Lei nº 10.833/2003.

3. CONCLUSÃO
Inexiste previsão legal para a apropriação de créditos de PIS/Pasep e Cofins sobre despesas de fretes decorrentes da simples transferência de mercadorias ou produtos acabados entre estabelecimentos da mesma pessoa jurídica.`,
    extraction: {
      id: "ext-cosit-3",
      document_id: "doc-cosit-98102",
      contribuinte_nome: "CONSULENTE INDÚSTRIA DE POLÍMEROS S.A.",
      contribuinte_cnpj_cpf: "Não informado na consulta",
      orgao_fiscal: "COORDENAÇÃO-GERAL DE TRIBUTAÇÃO - COSIT / RFB",
      tributos_identificados: ["PIS", "COFINS"],
      periodo_apuracao: "Contínuo",
      valor_principal: 0.0,
      valor_multa: 0.0,
      valor_juros: 0.0,
      valor_total: 0.0,
      data_lavratura: "20/01/2024",
      data_intimacao: "22/01/2024",
      data_vencimento: null,
      dispositivos_legais: [
        "Art. 3º, inciso II da Lei nº 10.637/2002",
        "Art. 3º, inciso II da Lei nº 10.833/2003",
        "REsp 1.221.170/PR (Tema 779 STJ)"
      ],
      resumo_executivo: "Solução de consulta vinculante vedando créditos de PIS/Cofins sobre fretes entre filiais de produtos acabados.",
      extraction_method: "RULES_DETERMINISTIC",
      confidence_score: 0.98,
      created_at: "2024-01-20T09:05:00Z"
    },
    summary: {
      document_id: "doc-cosit-98102",
      filename: "Solucao_Consulta_COSIT_98102.txt",
      document_type: "COSIT",
      contribuinte_nome: "CONSULENTE INDÚSTRIA DE POLÍMEROS S.A.",
      contribuinte_cnpj_cpf: null,
      orgao_fiscal: "COORDENAÇÃO-GERAL DE TRIBUTAÇÃO - COSIT / RFB",
      tributos: ["PIS", "COFINS"],
      total_autuado: 0.0,
      valor_principal: 0.0,
      valor_multa: 0.0,
      valor_juros: 0.0,
      prazos: {
        data_intimacao: "22/01/2024",
        data_vencimento: null,
        prazo_impugnacao_administrativa: null,
        prazo_pagamento_com_desconto: null
      },
      tese_acusacao: "Consulta formal quanto à correta interpretação da legislação tributária federal aplicável aos fatos narrados.",
      dispositivos_legais: [
        "Art. 3º, inciso II da Lei nº 10.637/2002",
        "Art. 3º, inciso II da Lei nº 10.833/2003",
        "REsp 1.221.170/PR (Tema 779 STJ)"
      ],
      grau_risco: "BAIXO",
      resumo_texto: `### Resumo Executivo Fiscal - Solucao_Consulta_COSIT_98102.txt

- **Tipo Documental:** Solução de Consulta COSIT
- **Órgão Autuante:** COORDENAÇÃO-GERAL DE TRIBUTAÇÃO - COSIT / RFB
- **Tributos Exigidos:** PIS, COFINS
- **Montante Total:** R$ 0,00 (Natureza Declaratória Consultiva)

#### Tese e Entendimento Vinculante
Inadmissibilidade de apropriação de créditos da não cumulatividade das contribuições PIS/Cofins sobre fretes na transferência de produtos acabados entre estabelecimentos da mesma empresa.

#### Fundamentação Normativa
Tema 779 STJ (REsp 1.221.170/PR) c/c Lei 10.637/2002 e Lei 10.833/2003.

#### Classificação de Risco
- **Grau de Risco:** BAIXO (Orientação normativa vinculante sem autuação pecuniária imediata)`
    },
    chunks: [
      {
        id: "chk-cosit-1",
        document_id: "doc-cosit-98102",
        chunk_index: 0,
        page_number: 1,
        content: "SOLUÇÃO DE CONSULTA Nº 98.102 - COSIT. ASSUNTO: CONTRIBUIÇÃO PARA O PIS/PASEP E COFINS. EMENTA: NÃO CUMULATIVIDADE. CRÉDITOS. INSUMOS. FRETES NA TRANSFERÊNCIA ENTRE ESTABELECIMENTOS.",
        token_count: 42,
        created_at: "2024-01-20T09:00:00Z"
      },
      {
        id: "chk-cosit-2",
        document_id: "doc-cosit-98102",
        chunk_index: 1,
        page_number: 2,
        content: "O frete de produtos acabados entre estabelecimentos da mesma empresa não integra o processo produtivo, razão pela qual não se amolda à hipótese de creditamento prevista no Art. 3º, inciso II da Lei nº 10.637/2002.",
        token_count: 55,
        created_at: "2024-01-20T09:00:00Z"
      }
    ]
  }
];

export const SAMPLE_TEXT_TEMPLATES = [
  {
    name: "AIIM Estadual - ICMS SP",
    type: "AIIM",
    filename: "AIIM_ICMS_SP_4123456.txt",
    text: SAMPLE_DOCUMENTS[0].raw_text
  },
  {
    name: "Notificação Federal - IRPJ / CSLL (RFB)",
    type: "NL",
    filename: "Notificacao_Lancamento_RFB_IRPJ_CSLL.txt",
    text: SAMPLE_DOCUMENTS[1].raw_text
  },
  {
    name: "Solução de Consulta - COSIT PIS / COFINS",
    type: "COSIT",
    filename: "Solucao_Consulta_COSIT_98102.txt",
    text: SAMPLE_DOCUMENTS[2].raw_text
  }
];
