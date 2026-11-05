import streamlit as st
from utils import classify_request, create_request

st.set_page_config(page_title="Nova Solicitação | LexFlow", page_icon=None, layout="wide")

st.title(" Nova Solicitação Interna")
st.caption("Cadastre uma necessidade operacional para triagem automatizada.")

CATEGORIES = [
    ("", "Não informar (deixar para classificação)"),
    ("ACCESS_AND_SYSTEMS", "Acessos e Sistemas (TI)"),
    ("DOCUMENTS_AND_TEMPLATES", "Modelos e Minutas (Operações)"),
    ("DATA_AND_REPORTS", "Dados e Relatórios (Inovação)"),
    ("AI_AND_AUTOMATION", "IA e Automações (Inovação)"),
    ("INTERNAL_REQUEST", "Solicitação Interna / Suprimentos (Operações)"),
    ("OTHER", "Outros (Triagem Geral)"),
]

PRIORITIES = ["NORMAL", "LOW", "HIGH", "URGENT"]

with st.form("form_nova_solicitacao", clear_on_submit=False):
    title = st.text_input(
        "Título da Solicitação *",
        placeholder="Ex.: Acesso a ferramenta de pesquisa jurisprudencial",
        help="Obrigatório, entre 5 e 120 caracteres.",
    )

    description = st.text_area(
        "Descrição Detalhada *",
        placeholder="Descreva a necessidade com contexto e ferramentas requeridas...",
        height=140,
        help="Obrigatório, entre 10 e 5.000 caracteres.",
    )

    c1, c2 = st.columns(2)
    with c1:
        category_choice = st.selectbox(
            "Categoria Sugerida (Opcional)",
            options=[c[0] for c in CATEGORIES],
            format_func=lambda x: dict(CATEGORIES).get(x, x),
        )
        department = st.text_input("Departamento Solicitante", placeholder="Ex.: Tributário")

    with c2:
        priority_choice = st.selectbox("Prioridade Preliminar", options=PRIORITIES, index=0)
        requester_name = st.text_input("Nome do Solicitante (Demo)", placeholder="Ex.: Lucas Mendes")

    auto_classify = st.checkbox("Classificar com IA imediatamente após o cadastro", value=True)

    submitted = st.form_submit_button("Criar Solicitação", type="primary")

    if submitted:
        if not title or len(title.strip()) < 5:
            st.error("O título deve ter no mínimo 5 caracteres.")
        elif not description or len(description.strip()) < 10:
            st.error("A descrição deve ter no mínimo 10 caracteres.")
        else:
            payload = {
                "title": title.strip(),
                "description": description.strip(),
                "category": category_choice if category_choice else None,
                "priority": priority_choice,
                "department": department.strip() if department else None,
                "requester_name": requester_name.strip() if requester_name else None,
            }

            success, res = create_request(payload)
            if success:
                req_id = res["id"]
                st.success(f" Solicitação cadastrada com sucesso! Protocolo: `{req_id}`")

                if auto_classify:
                    with st.spinner("Executando motor de classificação..."):
                        c_success, c_res = classify_request(req_id)
                        if c_success:
                            c_data = c_res.get("result", {})
                            st.info(
                                f" **Classificação Automática Realizada:**\n"
                                f"- **Categoria:** `{c_data.get('category')}`\n"
                                f"- **Equipe:** `{c_data.get('team')}`\n"
                                f"- **Confiança:** {c_data.get('confidence')}\n"
                                f"- **Justificativa:** {c_data.get('reason')}"
                            )
                            if c_res.get("warning"):
                                st.warning(f" {c_res['warning']}")
                        else:
                            st.warning(f"A solicitação foi criada, mas a classificação automática falhou: {c_res}")
            else:
                st.error(f"Erro ao cadastrar solicitação: {res}")
