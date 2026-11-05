"""Seed script generating realistic fictitious demo requests for LexFlow.

Zero real client data, zero real credentials.
"""

from backend.app.db.session import SessionLocal, init_db
from backend.app.models.enums import (
    ClassificationSource,
    EventActor,
    EventType,
    RequestCategory,
    RequestPriority,
    RequestStatus,
)
from backend.app.repositories.request_repo import RequestRepository


def seed():
    init_db()
    db = SessionLocal()
    repo = RequestRepository(db)

    # Check if already seeded
    existing = repo.list_requests(limit=1)
    if existing:
        print("Database already has records. Skipping seed.")
        db.close()
        return

    demo_items = [
        {
            "title": "Acesso a ferramenta de pesquisa jurisprudencial",
            "description": "Necessito de login na plataforma de pesquisa jurídica para elaboração de subsídios técnicos na área tributária.",
            "category": RequestCategory.ACCESS_AND_SYSTEMS.value,
            "team": "TI / Suporte",
            "priority": RequestPriority.NORMAL.value,
            "status": RequestStatus.IN_PROGRESS.value,
            "department": "Tributário",
            "requester_name": "Mariana Silva",
            "confidence": 0.95,
            "reason": "Solicitação explícita de credenciais/acesso a software jurídico.",
        },
        {
            "title": "Atualização de modelo de procuração padrão",
            "description": "Precisamos atualizar a minuta padrão de procuração com os novos poderes bancários conforme orientação do comitê.",
            "category": RequestCategory.DOCUMENTS_AND_TEMPLATES.value,
            "team": "Operações",
            "priority": RequestPriority.HIGH.value,
            "status": RequestStatus.TRIAGE.value,
            "department": "Contencioso Cível",
            "requester_name": "Carlos Eduardo",
            "confidence": 0.88,
            "reason": "Trata-se de alteração em minuta e modelo institucional.",
        },
        {
            "title": "Extração de relatório de produtividade mensal",
            "description": "Solicito a extração dos dados consolidados de tempo e volume de casos do último trimestre em formato de planilha.",
            "category": RequestCategory.DATA_AND_REPORTS.value,
            "team": "Dados / Inovação",
            "priority": RequestPriority.NORMAL.value,
            "status": RequestStatus.RESOLVED.value,
            "department": "Controladoria",
            "requester_name": "Fernanda Souza",
            "confidence": 0.92,
            "reason": "Pedido de consolidação e exportação de dados analíticos.",
        },
        {
            "title": "Sugestão de automação para triagem de e-mails",
            "description": "Gostaria de avaliar a viabilidade de aplicar IA generativa para auxiliar na classificação preliminar de notificações recebidas.",
            "category": RequestCategory.AI_AND_AUTOMATION.value,
            "team": "Inovação",
            "priority": RequestPriority.LOW.value,
            "status": RequestStatus.NEW.value,
            "department": "Inovação e Projetos",
            "requester_name": "Roberto Dias",
            "confidence": 0.85,
            "reason": "Demanda voltada a projetos de IA e transformação digital.",
        },
        {
            "title": "Solicitação de material para sala de reuniões",
            "description": "Necessitamos de cabos adaptadores e apontador laser para a apresentação aos sócios amanhã cedo.",
            "category": RequestCategory.INTERNAL_REQUEST.value,
            "team": "Operações",
            "priority": RequestPriority.URGENT.value,
            "status": RequestStatus.WAITING.value,
            "department": "Administrativo",
            "requester_name": "Juliana Castro",
            "confidence": 0.79,
            "reason": "Solicitação administrativa e de infraestrutura física.",
        },
        {
            "title": "Dúvida geral sobre fluxo de reembolso",
            "description": "Qual o prazo padrão para aprovação de despesas de viagem após envio dos comprovantes fiscais?",
            "category": RequestCategory.OTHER.value,
            "team": "Triagem",
            "priority": RequestPriority.NORMAL.value,
            "status": RequestStatus.NEW.value,
            "department": "Financeiro",
            "requester_name": "Lucas Ramos",
            "confidence": 0.65,
            "reason": "Não se encaixa nas categorias técnicas; encaminhado para triagem geral.",
        },
    ]

    for item in demo_items:
        req = repo.create(
            title=item["title"],
            description=item["description"],
            category=item["category"],
            priority=item["priority"],
            department=item["department"],
            requester_name=item["requester_name"],
            actor=EventActor.DEMO_USER.value,
        )
        req.team = item["team"]
        req.status = item["status"]
        req.classification_source = ClassificationSource.RULES.value
        req.classification_confidence = item["confidence"]
        req.classification_reason = item["reason"]

        repo.add_event(
            request_id=req.id,
            event_type=EventType.CLASSIFICATION_APPLIED.value,
            actor=EventActor.SYSTEM.value,
            summary=f"Classificado automaticamente como {req.category} (Equipe: {req.team})",
            metadata={"confidence": req.classification_confidence, "source": req.classification_source},
        )
        repo.update(req)

    print(f"Successfully seeded {len(demo_items)} fictitious demonstration requests.")
    db.close()


if __name__ == "__main__":
    seed()
