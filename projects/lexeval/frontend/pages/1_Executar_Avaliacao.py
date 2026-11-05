import streamlit as st
from utils import get_datasets, get_eval_run_detail, get_prompts, trigger_evaluation

st.set_page_config(page_title="Executar Avaliação | LexEval", page_icon="🚀", layout="wide")

st.title("🚀 Disparo de Avaliação em Lote (Batch Eval Run)")
st.caption(
    "Execute baterias de testes automatizados com validação determinística, "
    "fidelidade factual e juiz IA."
)

datasets = get_datasets()
prompts = get_prompts()

if not datasets:
    st.warning("Nenhum Golden Dataset encontrado. Execute o script de seed ou cadastre novos casos.")
else:
    with st.form("eval_run_form"):
        st.subheader("1. Configurações do Benchmark")
        col_ds, col_pm, col_ev = st.columns(3)

        with col_ds:
            ds_options = {d["id"]: f"{d['name']} ({d.get('test_cases_count', 0)} casos)" for d in datasets}
            selected_ds_id = st.selectbox("Selecione o Golden Dataset", options=list(ds_options.keys()), format_func=lambda x: ds_options[x])

        with col_pm:
            prompt_options = {"none": "Modelo Base Padrão (Sem Prompt Versionado)"}
            for p in prompts:
                prompt_options[p["id"]] = f"{p['name']} (v{p['version']})"
            selected_prompt_id = st.selectbox("Versão do Prompt", options=list(prompt_options.keys()), format_func=lambda x: prompt_options[x])

        with col_ev:
            eval_type = st.selectbox(
                "Motor de Avaliação",
                options=["hybrid", "deterministic", "llm"],
                format_func=lambda x: {
                    "hybrid": "Híbrido (Regras + Fático + Juiz IA)",
                    "deterministic": "Determinístico Puro (Regras Léxicas e Citações)",
                    "llm": "LLM-as-a-Judge (Semântico)",
                }[x],
            )

        col_model, col_thresh = st.columns([2, 1])
        with col_model:
            model_name = st.text_input("Identificador do Modelo", value="rule-evaluator-v1")
        with col_thresh:
            threshold = st.slider("Limiar de Aprovação (Threshold)", min_value=0.50, max_value=0.95, value=0.70, step=0.05)

        submitted = st.form_submit_button("⚡ Iniciar Bateria de Avaliação", type="primary")

    if submitted:
        with st.spinner("Executando avaliação caso a caso contra o contexto fático..."):
            payload = {
                "dataset_id": selected_ds_id,
                "prompt_version_id": selected_prompt_id if selected_prompt_id != "none" else None,
                "model_name": model_name,
                "evaluator_type": eval_type,
                "threshold": threshold,
            }
            res = trigger_evaluation(payload)

            if res:
                st.success(f"Avaliação concluída com sucesso! Run ID: `{res['id']}`")

                # Metrics summary
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Taxa de Aprovação", f"{res['pass_rate'] * 100:.1f}%")
                m2.metric("Fidelidade Média", f"{res['avg_faithfulness'] * 100:.1f}%")
                m3.metric("Relevância Média", f"{res['avg_relevance'] * 100:.1f}%")
                m4.metric("Duração", f"{res['duration_ms']:.0f} ms")

                st.markdown("---")
                st.subheader("📑 Resultados Detalhados por Caso de Teste")

                # Fetch full results with diagnostics
                run_detail = get_eval_run_detail(res["id"])
                results = run_detail.get("results", []) if run_detail else res.get("results", [])

                for r in results:
                    passed = r.get("passed", False)
                    badge = "✅ APROVADO" if passed else f"❌ REPROVADO ({r.get('failure_reason', 'FALHA')})"
                    title = r.get("test_case_title") or f"Caso {r.get('test_case_id')[:8]}"

                    with st.expander(f"{badge} — {title}"):
                        c_score1, c_score2, c_score3 = st.columns(3)
                        c_score1.write(f"**Fidelidade:** {r.get('faithfulness_score', 0.0) * 100:.1f}%")
                        c_score2.write(f"**Relevância:** {r.get('relevance_score', 0.0) * 100:.1f}%")
                        c_score3.write(f"**Schema:** {r.get('schema_score', 0.0) * 100:.1f}%")

                        st.markdown("**Resposta Produzida pela IA:**")
                        st.code(r.get("generated_output", ""), language="markdown")

                        diag = r.get("diagnostics", {})
                        if diag:
                            st.markdown("**Diagnóstico do Avaliador:**")
                            st.json(diag)
            else:
                st.error("Erro ao executar avaliação. Verifique os logs da API.")
