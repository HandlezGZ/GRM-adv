import streamlit as st
from utils import create_test_case, get_dataset_cases, get_datasets

st.set_page_config(page_title="Golden Datasets | LexEval", page_icon="📚", layout="wide")

st.title("📚 Gerenciador de Golden Datasets & Casos de Teste")
st.caption(
    "Gerenciamento e curadoria de gabaritos jurídicos sintéticos, documentos de contexto "
    "e critérios estritos de aceitação."
)

datasets = get_datasets()

if not datasets:
    st.warning("Nenhum dataset cadastrado. Execute o script de seed.")
else:
    ds_map = {d["id"]: f"{d['name']} [{d.get('category', 'GERAL')}] ({d.get('test_cases_count', 0)} casos)" for d in datasets}
    selected_ds = st.selectbox("Selecione o Dataset", options=list(ds_map.keys()), format_func=lambda x: ds_map[x])

    tab_cases, tab_add = st.tabs(["📋 Casos de Teste Cadastrados", "➕ Adicionar Novo Caso"])

    with tab_cases:
        cases = get_dataset_cases(selected_ds)
        st.write(f"Total de casos no dataset: **{len(cases)}**")

        for idx, c in enumerate(cases):
            with st.expander(f"Caso #{idx+1}: {c.get('title')}"):
                st.markdown("**Pergunta / Consulta:**")
                st.info(c.get("input_query"))

                st.markdown("**Documento de Contexto Fático:**")
                st.text(c.get("context_document"))

                st.markdown("**Resposta Esperada (Ground Truth):**")
                st.success(c.get("expected_output"))

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Palavras-chave Obrigatórias:**")
                    kws = c.get("required_keywords", [])
                    st.write(", ".join([f"`{k}`" for k in kws]) if kws else "Nenhuma restrição específica.")
                with c2:
                    st.markdown("**Termos Proibidos (Guardrails):**")
                    fts = c.get("forbidden_terms", [])
                    st.write(", ".join([f"`{f}`" for f in fts]) if fts else "Nenhum termo vedado.")

    with tab_add:
        st.subheader("Cadastrar Novo Caso de Teste")
        with st.form("new_case_form"):
            title = st.text_input("Título do Caso", placeholder="Ex: Isenção de IPI em insumos")
            query = st.text_area("Pergunta do Usuário", placeholder="Qual a regra aplicável...")
            context = st.text_area("Documento de Contexto", placeholder="Texto da lei, acórdão ou contrato...")
            expected = st.text_area("Resposta Esperada (Ground Truth)", placeholder="A resposta jurídica correta...")

            col_kw, col_fb = st.columns(2)
            with col_kw:
                kws_raw = st.text_input("Palavras-chave Obrigatórias (separadas por vírgula)", placeholder="art. 174, CTN, 5 anos")
            with col_fb:
                fbs_raw = st.text_input("Termos Proibidos (separados por vírgula)", placeholder="10 anos, imprescritível")

            submitted = st.form_submit_button("Salvar Caso de Teste", type="primary")

        if submitted:
            if not title or not query or not context or not expected:
                st.error("Todos os campos principais são obrigatórios.")
            else:
                kws = [k.strip() for k in kws_raw.split(",") if k.strip()]
                fbs = [f.strip() for f in fbs_raw.split(",") if f.strip()]
                payload = {
                    "title": title,
                    "input_query": query,
                    "context_document": context,
                    "expected_output": expected,
                    "required_keywords": kws,
                    "forbidden_terms": fbs,
                }
                res = create_test_case(selected_ds, payload)
                if res:
                    st.success("Caso de teste cadastrado com sucesso! Atualize a página para visualizar.")
                else:
                    st.error("Erro ao salvar caso de teste.")
