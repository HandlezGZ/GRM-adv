from backend.app.models.enums import (
    ClassificationSource,
    RequestCategory,
    RequestPriority,
)
from backend.app.services.classification.rules import RulesClassifier, normalize_text


def test_normalize_text():
    raw = "  Olá, Atenção aos Prazos de TI!!   "
    normalized = normalize_text(raw)
    assert normalized == "ola, atencao aos prazos de ti!!"


def test_classify_access_and_systems():
    classifier = RulesClassifier()
    result = classifier.classify(
        title="Solicitação de Acesso VPN",
        description="Preciso de login e senha para acessar o sistema corporativo.",
    )
    assert result.category == RequestCategory.ACCESS_AND_SYSTEMS
    assert result.team == "TI / Suporte"
    assert result.source == ClassificationSource.RULES
    assert result.confidence >= 0.70


def test_classify_documents_and_templates():
    classifier = RulesClassifier()
    result = classifier.classify(
        title="Modelo de Procuração",
        description="Necessitamos atualizar a minuta padrão e template de poderes.",
    )
    assert result.category == RequestCategory.DOCUMENTS_AND_TEMPLATES
    assert result.team == "Operações"


def test_classify_data_and_reports():
    classifier = RulesClassifier()
    result = classifier.classify(
        title="Extração de dados mensais",
        description="Preciso de um relatório com métricas em planilha Excel.",
    )
    assert result.category == RequestCategory.DATA_AND_REPORTS
    assert result.team == "Dados / Inovação"


def test_classify_ai_and_automation():
    classifier = RulesClassifier()
    result = classifier.classify(
        title="Projeto de IA para triagem",
        description="Queremos construir um bot de automação para tarefas repetitivas.",
    )
    assert result.category == RequestCategory.AI_AND_AUTOMATION
    assert result.team == "Inovação"


def test_classify_urgent_priority():
    classifier = RulesClassifier()
    result = classifier.classify(
        title="Sistema fora do ar crítico",
        description="O sistema está parado, urgência imediata com prazo fatal.",
    )
    assert result.priority == RequestPriority.URGENT


def test_classify_unmatched_falls_back_to_other():
    classifier = RulesClassifier()
    result = classifier.classify(
        title="Conversa informal",
        description="Gostaria de saber como estão as coisas por aí nesta tarde.",
    )
    assert result.category == RequestCategory.OTHER
    assert result.team == "Triagem"
    assert result.confidence == 0.50
