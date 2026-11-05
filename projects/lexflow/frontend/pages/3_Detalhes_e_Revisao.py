import streamlit as st
from utils import (
    classify_request,
    get_request,
    get_request_events,
    list_requests,
    review_request,
    update_status,
)

st.set_page_config(
    page_title="Detalhes e Revisão | LexFlow",
    page_icon=None,
    layout="wide",
)

st.title(" Detalhes e Revisão Humana")
st.caption("Acompanhe o workflow, inspecione eventos e assuma o controle humano da triagem.")

# Fetch recent requests for easy selection
recent_requests = list_requests(limit=30)
options_map = {f"{r['title'][:40]}... ({r['id'][:8]})": r["id"] for r in recent_requests}

selected_label = st.selectbox(
    "Selecione uma solicitação recente ou cole o UUID:",
    options=list(options_map.keys()),
    index=0 if options_map else None,
)

manual_id = st.text_input("Ou busque diretamente pelo ID (UUID):", placeholder="Ex.: 3fa85f64-5717-4562-b3fc-2c963f66afa6")
target_id = manual_id.strip() if manual_id.strip() else (options_map.get(selected_label) if selected_label else None)

if not target_id:
    st.info("Nenhuma solicitação selecionada.")
    st.stop()

req = get_request(target_id)
if not req:
    st.error(f"Solicitação `{target_id}` não foi localizada no backend.")
    st.stop()

# Layout: 2 Columns (Details & Controls on left, Audit History on right)
col_main, col_audit = st.columns([3, 2])

with col_main:
    st.subheader(f" {req['title']}")
    st.write(f"**Descrição:** {req['description']}")

    # Info chips
    i1, i2, i3, i4 = st.columns(4)
    i1.metric("Status Atual", req["status"])
    i2.metric("Prioridade", req["priority"])
    i3.metric("Categoria", req["category"] or "Não definida")
    i4.metric("Equipe", req["team"] or "Não definida")

    c_source = req.get("classification_source")
    conf_val = req.get("classification_confidence")
    conf_display = f"{conf_val:.2f}" if conf_val is not None else "N/A"

    badge = " Automática (Regras/IA)" if c_source != "human" else " Revisada por Humano"
    st.info(
        f"**Origem:** {badge} | **Confiança:** {conf_display}\n\n"
        f"**Justificativa:** {req.get('classification_reason') or 'Sem justificativa registrada.'}"
    )

    st.divider()

    # Classification Action
    if st.button(" Executar Classificação Automática (Regras/IA)", use_container_width=True):
        with st.spinner("Classificando solicitação..."):
            ok, res = classify_request(target_id)
            if ok:
                st.success("Classificação executada com sucesso!")
                st.rerun()
            else:
                st.error(f"Falha ao classificar: {res}")

    st.divider()

    # Workflow Status Transitions
    st.write("####  Atualizar Status do Workflow")
    current_status = req["status"]

    transitions_map = {
        "NEW": ["TRIAGE", "CANCELLED"],
        "TRIAGE": ["IN_PROGRESS", "WAITING", "CANCELLED"],
        "IN_PROGRESS": ["WAITING", "RESOLVED", "CANCELLED"],
        "WAITING": ["IN_PROGRESS", "CANCELLED"],
        "RESOLVED": [],
        "CANCELLED": [],
    }
    allowed_next = transitions_map.get(current_status, [])

    if not allowed_next:
        st.write(f"O status `{current_status}` é um estado terminal no MVP. Nenhuma transição permitida.")
    else:
        st_col1, st_col2 = st.columns([2, 3])
        with st_col1:
            next_st = st.selectbox("Próximo Status", options=allowed_next)
        with st_col2:
            st_reason = st.text_input("Motivo da alteração", placeholder="Ex.: Encaminhado para o time responsável")

        if st.button("Confirmar Mudança de Status"):
            ok, res = update_status(target_id, next_st, st_reason)
            if ok:
                st.success(f"Status alterado para `{next_st}`!")
                st.rerun()
            else:
                st.error(f"Erro ao alterar status: {res}")

    st.divider()

    # Human-in-the-Loop Review Panel
    st.write("####  Painel de Revisão Humana (Human-in-the-Loop)")
    st.caption("O analista pode corrigir a sugestão da IA. A validação humana se torna definitiva e auditável.")

    CATEGORIES_REV = [
        "ACCESS_AND_SYSTEMS",
        "DOCUMENTS_AND_TEMPLATES",
        "DATA_AND_REPORTS",
        "AI_AND_AUTOMATION",
        "INTERNAL_REQUEST",
        "OTHER",
    ]
    PRIORITIES_REV = ["NORMAL", "LOW", "HIGH", "URGENT"]

    with st.form("form_revisao_humana"):
        r_c1, r_c2 = st.columns(2)
        with r_c1:
            rev_cat = st.selectbox(
                "Categoria Confirmada",
                options=CATEGORIES_REV,
                index=CATEGORIES_REV.index(req["category"]) if req.get("category") in CATEGORIES_REV else 0,
            )
            rev_prio = st.selectbox(
                "Prioridade Confirmada",
                options=PRIORITIES_REV,
                index=PRIORITIES_REV.index(req["priority"]) if req.get("priority") in PRIORITIES_REV else 0,
            )
        with r_c2:
            rev_team = st.text_input(
                "Equipe Responsável",
                value=req.get("team") or "TI / Suporte",
            )
            rev_reviewer = st.text_input(
                "Nome do Analista Revisor",
                value="Analista de Triagem",
            )

        rev_reason = st.text_area(
            "Justificativa da Revisão Humana *",
            placeholder="Explique o motivo do ajuste ou confirme a adequação da categoria...",
            height=90,
        )

        submitted_rev = st.form_submit_button("Confirmar Revisão Humana", type="primary")

        if submitted_rev:
            if not rev_reason or len(rev_reason.strip()) < 5:
                st.error("A justificativa humana é obrigatória (mínimo 5 caracteres).")
            else:
                rev_payload = {
                    "category": rev_cat,
                    "team": rev_team.strip(),
                    "priority": rev_prio,
                    "review_reason": rev_reason.strip(),
                    "reviewer_name": rev_reviewer.strip(),
                }
                ok, res = review_request(target_id, rev_payload)
                if ok:
                    st.success("Revisão humana registrada com sucesso!")
                    st.rerun()
                else:
                    st.error(f"Erro ao salvar revisão: {res}")

with col_audit:
    st.subheader(" Trilha de Auditoria (Eventos)")
    events = get_request_events(target_id)
    if not events:
        st.info("Nenhum evento registrado até o momento.")
    else:
        for ev in reversed(events):
            actor_label = "Humano" if ev["actor"] == "human" else ("Sistema" if ev["actor"] == "system" else ev["actor"])
            with st.container(border=True):
                st.markdown(f"**[{actor_label}] {ev['event_type']}** | `{ev['actor']}`")
                st.write(ev["summary"])
                st.caption(f"Horário UTC: {ev['created_at'][:19].replace('T', ' ')}")
                if ev.get("metadata_json"):
                    st.caption(f"Metadados: `{ev['metadata_json']}`")
