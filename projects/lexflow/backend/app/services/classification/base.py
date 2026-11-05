from abc import ABC, abstractmethod

from backend.app.api.schemas.classification import ClassificationResult


class BaseClassifier(ABC):
    @abstractmethod
    def classify(self, title: str, description: str) -> ClassificationResult:
        """Classify a request based on title and description."""
        pass
