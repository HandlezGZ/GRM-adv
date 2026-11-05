import pytest
from backend.app.db.base import Base
from backend.app.models.enums import EventType, RequestStatus
from backend.app.repositories.request_repo import RequestRepository
from backend.app.services.workflow import InvalidStatusTransitionError, WorkflowService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def workflow_setup():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    repo = RequestRepository(session)
    workflow = WorkflowService(repo)
    try:
        yield repo, workflow
    finally:
        session.close()


def test_allowed_status_transitions(workflow_setup):
    repo, workflow = workflow_setup
    req = repo.create(title="Workflow Test", description="Testing transitions")
    assert req.status == RequestStatus.NEW.value

    # NEW -> TRIAGE
    req = workflow.transition_status(
        req, RequestStatus.TRIAGE.value, reason="Triagem inicial"
    )
    assert req.status == RequestStatus.TRIAGE.value

    # TRIAGE -> IN_PROGRESS
    req = workflow.transition_status(req, RequestStatus.IN_PROGRESS.value)
    assert req.status == RequestStatus.IN_PROGRESS.value

    # IN_PROGRESS -> RESOLVED
    req = workflow.transition_status(req, RequestStatus.RESOLVED.value)
    assert req.status == RequestStatus.RESOLVED.value
    assert req.resolved_at is not None

    # Check events
    events = repo.get_events(req.id)
    # 1 creation + 3 transitions = 4 events
    assert len(events) == 4
    transition_events = [
        e for e in events if e.event_type == EventType.STATUS_CHANGED.value
    ]
    assert len(transition_events) == 3


def test_invalid_status_transition_raises_error(workflow_setup):
    repo, workflow = workflow_setup
    req = repo.create(
        title="Workflow Invalid", description="Testing invalid transition"
    )
    assert req.status == RequestStatus.NEW.value

    # NEW cannot directly transition to RESOLVED
    with pytest.raises(InvalidStatusTransitionError) as exc_info:
        workflow.transition_status(req, RequestStatus.RESOLVED.value)
    assert "Transição inválida" in str(exc_info.value)

    # Status must remain unchanged
    assert req.status == RequestStatus.NEW.value


def test_resolved_status_is_terminal(workflow_setup):
    repo, workflow = workflow_setup
    req = repo.create(title="Workflow Terminal", description="Testing terminal state")

    req = workflow.transition_status(req, RequestStatus.TRIAGE.value)
    req = workflow.transition_status(req, RequestStatus.IN_PROGRESS.value)
    req = workflow.transition_status(req, RequestStatus.RESOLVED.value)

    # RESOLVED cannot transition to any other status
    with pytest.raises(InvalidStatusTransitionError):
        workflow.transition_status(req, RequestStatus.IN_PROGRESS.value)
