import pytest
from backend.app.db.base import Base
from backend.app.models.enums import (
    EventActor,
    EventType,
    RequestPriority,
    RequestStatus,
)
from backend.app.repositories.request_repo import RequestRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def test_create_request_with_audit_event(in_memory_db):
    repo = RequestRepository(in_memory_db)
    req = repo.create(
        title="Solicitação de Teste Unitário",
        description="Descrição detalhada para teste de persistência e auditoria.",
        priority=RequestPriority.HIGH.value,
        department="Inovação",
        requester_name="Usuário Teste",
        actor=EventActor.DEMO_USER.value,
    )

    assert req.id is not None
    assert req.title == "Solicitação de Teste Unitário"
    assert req.status == RequestStatus.NEW.value
    assert req.priority == RequestPriority.HIGH.value

    # Verify event was created
    events = repo.get_events(req.id)
    assert len(events) == 1
    assert events[0].event_type == EventType.REQUEST_CREATED.value
    assert events[0].actor == EventActor.DEMO_USER.value


def test_list_and_filter_requests(in_memory_db):
    repo = RequestRepository(in_memory_db)
    r1 = repo.create(title="Acesso VPN", description="Necessito acesso VPN urgente")
    repo.create(title="Modelo Contrato", description="Novo modelo de prestação")

    r1.status = RequestStatus.TRIAGE.value
    repo.update(r1)

    all_reqs = repo.list_requests()
    assert len(all_reqs) == 2

    triage_reqs = repo.list_requests(status=RequestStatus.TRIAGE.value)
    assert len(triage_reqs) == 1
    assert triage_reqs[0].title == "Acesso VPN"

    search_reqs = repo.list_requests(search="Contrato")
    assert len(search_reqs) == 1
    assert search_reqs[0].title == "Modelo Contrato"


def test_record_classification_attempt_and_failures(in_memory_db):
    repo = RequestRepository(in_memory_db)
    req = repo.create(
        title="Teste Falha",
        description="Descrição para simulação de falha",
    )

    attempt_ok = repo.record_classification_attempt(
        request_id=req.id,
        provider="rules",
        source="rules",
        success=True,
    )
    assert attempt_ok.success is True

    attempt_fail = repo.record_classification_attempt(
        request_id=req.id,
        provider="llm",
        source="llm",
        success=False,
        error_type="TimeoutError",
    )
    assert attempt_fail.success is False

    failures = repo.list_failures()
    assert len(failures) == 1
    assert failures[0].error_type == "TimeoutError"
