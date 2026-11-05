import time

from backend.app.api.schemas.classification import (
    ClassificationResponse,
)
from backend.app.core.config import settings
from backend.app.models.enums import (
    ClassificationSource,
    EventActor,
    EventType,
    RequestStatus,
)
from backend.app.models.request import Request
from backend.app.repositories.request_repo import RequestRepository
from backend.app.services.classification.rules import RulesClassifier


class ClassificationManager:
    def __init__(self, repo: RequestRepository):
        self.repo = repo
        self.rules_classifier = RulesClassifier()

    def classify_request(self, request: Request) -> ClassificationResponse:
        start_time = time.perf_counter()

        # In Phase 5, rules mode is default and robust
        # In Phase 7, LLM will be plugged in here with graceful fallback
        result = self.rules_classifier.classify(
            title=request.title, description=request.description
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        # Record attempt
        self.repo.record_classification_attempt(
            request_id=request.id,
            provider="rules",
            source=ClassificationSource.RULES.value,
            success=True,
            model_name="rule-engine-v1",
            duration_ms=round(elapsed_ms, 2),
        )

        # Apply to request
        request.category = result.category.value
        request.team = result.team
        request.priority = result.priority.value
        request.classification_source = result.source.value
        request.classification_confidence = result.confidence
        request.classification_reason = result.reason

        # If NEW, advance to TRIAGE
        if request.status == RequestStatus.NEW.value:
            request.status = RequestStatus.TRIAGE.value

        summary_text = (
            f"Classificado como {result.category.value} ({result.team}) "
            f"com confiança {result.confidence}"
        )
        self.repo.add_event(
            request_id=request.id,
            event_type=EventType.CLASSIFICATION_APPLIED.value,
            actor=EventActor.SYSTEM.value,
            summary=summary_text,
            metadata={
                "category": result.category.value,
                "team": result.team,
                "confidence": result.confidence,
                "source": result.source.value,
            },
        )
        self.repo.update(request)

        warning = None
        if result.confidence < settings.LLM_CONFIDENCE_THRESHOLD:
            warning = "Baixa confiança na classificação; recomenda-se revisão humana."

        return ClassificationResponse(
            request_id=request.id,
            result=result,
            fallback_used=False,
            warning=warning,
        )
