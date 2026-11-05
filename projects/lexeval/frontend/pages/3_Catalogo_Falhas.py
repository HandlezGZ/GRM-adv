import streamlit as st
from utils import get_datasets, get_failures

st.set_page_config(page_title="Catálogo de Falhas | LexEval", page_icon=None, layout="wide")

st.title(" Catálogo de Falhas e Incidentes de IA")
st.caption(
    "Auditoria detalhada de alucinações fáticas, citações jurídicas espúrias, violações de formato "
    "e quebras de guardrails."
)

datasets = get_datasets()
dataset_filter = None

col1, col2 = st.columns(2)
with col1:
    ds_options = {"all": "Todos os Datasets"}
    for d in datasets:
        ds_options[d["id"]] = d["name"]
    sel_ds = st.selectbox("Filtrar por Dataset", options=list(ds_options.keys()), format_func=lambda x: ds_options[x])
    if sel_ds != "all":
        dataset_filter = sel_ds

with col2:
    reason_options = [
        "Todas as Falhas",
        "HALLUCINATED_CITATION",
        "HALLUCINATED_NUMERICAL_VALUE",
        "FORBIDDEN_TERM_VIOLATION",
        "UNGROUNDED_CLAIM",
        "SCHEMA_ERROR",
        "LOW_FAITHFULNESS",
        "INSUFFICIENT_RELEVANCE",
    ]
    sel_reason = st.selectbox("Filtrar por Categoria de Erro", options=reason_options)
    reason_filter = None if sel_reason == "Todas as Falhas" else sel_reason

failures = get_failures(dataset_id=dataset_filter, reason=reason_filter)

if not failures:
    st.success("Nenhuma falha encontrada para os filtros selecionados.")
else:
    st.info(f"Total de {len(failures)} incidente(s) catalogado(s).")

    for f in failures:
        reason = f.get("failure_reason", "ERRO")
        title = f.get("test_case_title", "Caso sem título")

        with st.container():
            st.markdown(f"###  `{reason}` — {title}")
            st.caption(f"Dataset: **{f.get('dataset_name')}** | Modelo: `{f.get('model_name')}` | Data: {f.get('created_at')[:19]}")

            col_gen, col_exp = st.columns(2)

            with col_gen:
                st.markdown("** Resposta Gerada (Com Defeito):**")
                st.warning(f.get("generated_output", ""))

            with col_exp:
                st.markdown("** Gabarito / Resposta Esperada:**")
                st.success(f.get("expected_output", ""))

            with st.expander(" Ver Documento de Contexto e Diagnóstico Completo"):
                st.markdown("**Documento de Contexto Jurídico:**")
                st.text(f.get("context_snippet", ""))

                st.markdown("**Diagnóstico Técnico:**")
                st.json(f.get("diagnostics", {}))

            st.markdown("---")
