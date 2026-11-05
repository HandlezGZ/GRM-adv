import json
from pathlib import Path

import httpx
from backend.app.api.schemas.classification import ClassificationResult
from backend.app.core.config import settings
from backend.app.models.enums import ClassificationSource
from backend.app.services.classification.base import BaseClassifier
from pydantic import ValidationError


class LLMClassificationError(Exception):
    """Raised when LLM classification fails, times out or returns invalid output."""
    pass


class LLMClassifier(BaseClassifier):
    """LLM-based classifier with prompt versioning and schema validation."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        prompt_file = (
            Path(__file__).resolve().parent.parent.parent
            / "prompts"
            / "request_classifier_v1.txt"
        )
        if prompt_file.exists():
            return prompt_file.read_text(encoding="utf-8")
        return (
            "Classifique a solicitação nos campos category, team, priority, "
            "confidence e reason no formato JSON:\n{title}\n{description}"
        )

    def classify(self, title: str, description: str) -> ClassificationResult:
        if not self.api_key:
            raise LLMClassificationError("API key do provedor LLM não configurada.")

        prompt = self.prompt_template.format(title=title, description=description)

        try:
            # Standard OpenAI-compatible Chat Completion API
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Você é um classificador estruturado JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.1,
            }

            with httpx.Client(timeout=5.0) as client:
                response = client.post(url, headers=headers, json=payload)
                if response.status_code != 200:
                    resp_sample = response.text[:200]
                    raise LLMClassificationError(
                        f"Provedor retornou HTTP {response.status_code}: {resp_sample}"
                    )

                data = response.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)

                # Validate schema
                parsed["source"] = ClassificationSource.LLM.value
                result = ClassificationResult(**parsed)
                return result

        except (httpx.TimeoutException, httpx.NetworkError) as e:
            raise LLMClassificationError(
                f"Erro de conexão/timeout com o provedor: {e}"
            ) from e
        except (json.JSONDecodeError, KeyError, ValidationError) as e:
            raise LLMClassificationError(
                f"Saída do modelo inválida ou fora do schema: {e}"
            ) from e
        except Exception as e:
            raise LLMClassificationError(
                f"Falha inesperada no processador LLM: {e}"
            ) from e
