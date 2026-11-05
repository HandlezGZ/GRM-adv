import streamlit as st
from utils import compare_runs, get_eval_runs

st.set_page_config(page_title="Comparador A/B | LexEval", page_icon="🔍", layout="wide")

st.title("🔍 Comparador e Versionador de Prompts (A/B Testing)")
st.caption(
    "Avalie o impacto de alterações em prompts e modelos: identifique regressões silenciosas, "
    "ganhos de acurácia fática e variações de relevância."
)

runs = get_eval_runs()

if len(runs) < 2:
    st.info("É necessário ter pelo menos 2 execuções de avaliação para realizar a comparação A/B.")
else:
    run_options = {
        r["id"]: f"Run {r['id'][:8]} — {r['model_name']} (Pass Rate: {r.get('pass_rate', 0.0) * 100:.1f}%)"
        for r in runs
    }

    col_a, col_b = st.columns(2)
    with col_a:
        run_a_id = st.selectbox("Baseline — Execução A", options=list(run_options.keys()), index=1, format_func=lambda x: run_options[x])
    with col_b:
        run_b_id = st.selectbox("Candidato — Execução B", options=list(run_options.keys()), index=0, format_func=lambda x: run_options[x])

    if st.button("⚖️ Executar Análise Comparativa A/B", type="primary"):
        with st.spinner("Analisando regressões e variações caso a caso..."):
            comp = compare_runs(run_a_id, run_b_id)

            if not comp:
                st.error("Falha ao obter dados comparativos.")
            else:
                st.markdown("---")
                st.subheader("📊 Veredito da Análise")

                verdict = comp.get("verdict")
                if verdict == "POSITIVE_PROGRESSION":
                    st.success("🏆 **PROGRESSÃO POSITIVA:** O candidato B superou o baseline A sem regressões críticas detectadas.")
                elif verdict == "CRITICAL_REGRESSION":
                    st.error("🛑 **REGRESSÃO CRÍTICA DETECTADA:** O candidato B introduziu falhas ou teve desempenho inferior ao baseline.")
                elif verdict == "MODERATE_IMPROVEMENT":
                    st.warning("⚠️ **MELHORIA MODERADA:** Ganhos superaram perdas, mas requer atenção a casos específicos.")
                else:
                    st.info("⚖️ **EQUIVALENTE:** Desempenho neutro ou sem deltas estatisticamente significativos.")

                # KPI Deltas
                k1, k2, k3, k4, k5 = st.columns(5)
                delta_pr = comp.get("pass_rate_delta", 0.0) * 100
                delta_ft = comp.get("faithfulness_delta", 0.0) * 100
                delta_rl = comp.get("relevance_delta", 0.0) * 100

                k1.metric("Delta Pass Rate", f"{delta_pr:+.1f}%", delta=f"{delta_pr:+.1f}%")
                k2.metric("Delta Fidelidade", f"{delta_ft:+.1f}%", delta=f"{delta_ft:+.1f}%")
                k3.metric("Ganhos (A falhou, B passou)", comp.get("gains_count", 0))
                k4.metric("Regressões (A passou, B falhou)", comp.get("regressions_count", 0))
                k5.metric("Empates / Consistentes", comp.get("ties_count", 0))

                st.markdown("---")
                st.subheader("🔬 Análise Caso a Caso")

                filter_status = st.radio(
                    "Filtrar casos por status:",
                    options=["Todos", "Somente Regressões", "Somente Ganhos"],
                    horizontal=True,
                )

                comparisons = comp.get("comparisons", [])
                for item in comparisons:
                    status = item.get("status")
                    if filter_status == "Somente Regressões" and status != "REGRESSION":
                        continue
                    if filter_status == "Somente Ganhos" and status != "GAIN":
                        continue

                    status_icon = "🟢 GAIN" if status == "GAIN" else ("🔴 REGRESSION" if status == "REGRESSION" else "⚪ TIE")
                    with st.expander(f"{status_icon} — {item.get('title')}"):
                        st.write(f"**Diagnóstico:** {item.get('notes')}")
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.write(f"**Run A Fidelidade:** {item.get('run_a_faithfulness', 0.0) * 100:.1f}%")
                        sc2.write(f"**Run B Fidelidade:** {item.get('run_b_faithfulness', 0.0) * 100:.1f}%")
                        sc3.write(f"**Delta:** {item.get('delta_faithfulness', 0.0) * 100:+.1f}%")
