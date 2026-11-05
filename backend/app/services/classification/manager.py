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
from backend.app.services.classification.llm import (
    LLMClassificationError,
    LLMClassifier,
)
from backend.app.services.classification.rules import RulesClassifier


class ClassificationManager:
    def __init__(self, repo: RequestRepository):
        self.repo = repo
        self.rules_classifier = RulesClassifier()
        self.llm_classifier = LLMClassifier()

    def classify_request(self, request: Request) -> ClassificationResponse:
        start_time = time.perf_counter()
        fallback_used = False
        warning = None
        result = None

        mode = settings.CLASSIFICATION_MODE

        # Try LLM if configured for llm or hybrid mode
        if mode in ("llm", "hybrid"):
            try:
                result = self.llm_classifier.classify(
                    title=request.title, description=request.description
                )
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                self.repo.record_classification_attempt(
                    request_id=request.id,
                    provider="openai",
                    source=ClassificationSource.LLM.value,
                    success=True,
                    model_name=settings.OPENAI_MODEL,
                    prompt_version="v1",
                    duration_ms=round(elapsed_ms, 2),
                )
            except LLMClassificationError as err:
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                error_msg = str(err)
                fallback_used = True
                warning = (
                    f"Falha no classificador LLM: {error_msg}. "
                    "Fallback determinístico executado."
                )

                # Record failure
                self.repo.record_classification_attempt(
                    request_id=request.id,
                    provider="openai",
                    source=ClassificationSource.LLM.value,
                    success=False,
                    model_name=settings.OPENAI_MODEL,
                    prompt_version="v1",
                    error_type=err.__class__.__name__,
                    duration_ms=round(elapsed_ms, 2),
                )
                self.repo.add_event(
                    request_id=request.id,
                    event_type=EventType.CLASSIFICATION_FAILED.value,
                    actor=EventActor.SYSTEM.value,
                    summary=f"Falha na IA ({err.__class__.__name__}): {error_msg}",
                    metadata={"error": error_msg, "mode": mode},
                )

        # If result is not obtained (rules mode or LLM failed with fallback)
        if result is None:
            rules_start = time.perf_counter()
            result = self.rules_classifier.classify(
                title=request.title, description=request.description
            )
            rules_elapsed_ms = (time.perf_counter() - rules_start) * 1000.0
            self.repo.record_classification_attempt(
                request_id=request.id,
                provider="rules",
                source=ClassificationSource.RULES.value,
                success=True,
                model_name="rule-engine-v1",
                duration_ms=round(rules_elapsed_ms, 2),
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
            f"Classificado via {result.source.value} como {result.category.value} "
            f"({result.team}) com confiança {result.confidence}"
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
                "fallback_used": fallback_used,
            },
        )
        self.repo.update(request)

        if not warning and result.confidence < settings.LLM_CONFIDENCE_THRESHOLD:
            warning = "Baixa confiança na classificação; recomenda-se revisão humana."

        return ClassificationResponse(
            request_id=request.id,
            result=result,
            fallback_used=fallback_used,
            warning=warning,
        )
