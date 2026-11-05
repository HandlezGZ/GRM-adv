import re
import unicodedata

from backend.app.api.schemas.classification import ClassificationResult
from backend.app.models.enums import (
    ClassificationSource,
    RequestCategory,
    RequestPriority,
)
from backend.app.services.classification.base import BaseClassifier


def normalize_text(text: str) -> str:
    """Normalize text: lowercase, remove accents and strip excess spaces."""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(c for c in normalized if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", ascii_text.lower()).strip()


class RulesClassifier(BaseClassifier):
    """Deterministic, rules-based classifier for internal requests.

    Does not require external APIs. Provides transparent scoring and reasons.
    """

    CATEGORY_MAPPING: dict[RequestCategory, dict] = {
        RequestCategory.ACCESS_AND_SYSTEMS: {
            "team": "TI / Suporte",
            "keywords": [
                "acesso", "login", "senha", "password", "reset", "vpn",
                "software", "sistema", "ferramenta", "token", "certificado",
                "permissao", "computador", "notebook", "email", "outlook",
                "bloqueio", "desbloqueio", "suporte",
            ],
            "reason": (
                "Demanda relacionada a contas, permissões, acessos "
                "ou suporte técnico."
            ),
        },
        RequestCategory.DOCUMENTS_AND_TEMPLATES: {
            "team": "Operações",
            "keywords": [
                "modelo", "minuta", "procuracao", "template", "contrato padrao",
                "documento interno", "clausula", "formulario", "substabelecimento",
                "padronizacao", "cabecalho",
            ],
            "reason": (
                "Demanda relacionada a minutas, modelos institucionais "
                "e documentos padrão."
            ),
        },
        RequestCategory.DATA_AND_REPORTS: {
            "team": "Dados / Inovação",
            "keywords": [
                "relatorio", "dados", "extracao", "planilha", "metrica",
                "bi", "dashboard", "volumetria", "exportacao", "sql",
                "estatistica", "grafico", "painel", "indicador",
            ],
            "reason": (
                "Demanda analítica, envolvendo dados, relatórios ou "
                "consolidação de planilhas."
            ),
        },
        RequestCategory.AI_AND_AUTOMATION: {
            "team": "Inovação",
            "keywords": [
                "automacao", "ia", "inteligencia artificial", "llm", "bot",
                "chat", "fluxo automatico", "robo", "script", "inovacao",
                "prompt", "agente", "ocr",
            ],
            "reason": (
                "Demanda de novos fluxos automatizados, inteligência artificial "
                "ou inovação."
            ),
        },
        RequestCategory.INTERNAL_REQUEST: {
            "team": "Operações",
            "keywords": [
                "sala de reuniao", "compra", "material", "equipamento",
                "cracha", "estacionamento", "manutencao predial", "escritorio",
                "viagem", "reembolso", "nota fiscal", "despesa", "correios",
                "copiadora", "impressora",
            ],
            "reason": (
                "Demanda operacional ou administrativa de infraestrutura "
                "e suprimentos."
            ),
        },
    }

    URGENT_KEYWORDS = [
        "urgente", "emergencia", "imediato", "prazo fatal", "hoje",
        "critico", "parado", "fora do ar", "bloqueado",
    ]

    HIGH_KEYWORDS = [
        "alta prioridade", "importante", "prioritario", "breve", "amanha",
    ]

    LOW_KEYWORDS = [
        "sugestao", "quando possivel", "sem pressa", "baixa", "duvida geral",
    ]

    def classify(self, title: str, description: str) -> ClassificationResult:
        full_text = f"{title} {description}"
        norm_text = normalize_text(full_text)

        category_scores: dict[RequestCategory, int] = {}
        for category, config in self.CATEGORY_MAPPING.items():
            score = 0
            for kw in config["keywords"]:
                # Word boundary search
                pattern = r"\b" + re.escape(kw) + r"\b"
                matches = len(re.findall(pattern, norm_text))
                score += matches
            category_scores[category] = score

        # Find best category
        best_category = RequestCategory.OTHER
        best_score = 0
        for category, score in category_scores.items():
            if score > best_score:
                best_score = score
                best_category = category

        # Determine priority
        priority = RequestPriority.NORMAL
        if any(
            re.search(r"\b" + re.escape(w) + r"\b", norm_text)
            for w in self.URGENT_KEYWORDS
        ):
            priority = RequestPriority.URGENT
        elif any(
            re.search(r"\b" + re.escape(w) + r"\b", norm_text)
            for w in self.HIGH_KEYWORDS
        ):
            priority = RequestPriority.HIGH
        elif any(
            re.search(r"\b" + re.escape(w) + r"\b", norm_text)
            for w in self.LOW_KEYWORDS
        ):
            priority = RequestPriority.LOW

        if best_score == 0:
            return ClassificationResult(
                category=RequestCategory.OTHER,
                team="Triagem",
                priority=priority,
                confidence=0.50,
                reason=(
                    "Nenhuma regra determinística encontrou correspondência clara. "
                    "Encaminhado para triagem."
                ),
                source=ClassificationSource.RULES,
            )

        # Confidence heuristic based on match count
        confidence = min(0.65 + (best_score * 0.10), 0.95)
        config = self.CATEGORY_MAPPING[best_category]

        reason_text = config["reason"]
        if priority == RequestPriority.URGENT:
            reason_text += (
                " Identificados termos críticos; prioridade urgente requer "
                "confirmação humana."
            )

        return ClassificationResult(
            category=best_category,
            team=config["team"],
            priority=priority,
            confidence=round(confidence, 2),
            reason=reason_text,
            source=ClassificationSource.RULES,
        )
