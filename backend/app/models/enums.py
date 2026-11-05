from enum import Enum


class RequestStatus(str, Enum):
    NEW = "NEW"
    TRIAGE = "TRIAGE"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING = "WAITING"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"


class RequestCategory(str, Enum):
    ACCESS_AND_SYSTEMS = "ACCESS_AND_SYSTEMS"
    DOCUMENTS_AND_TEMPLATES = "DOCUMENTS_AND_TEMPLATES"
    INTERNAL_REQUEST = "INTERNAL_REQUEST"
    DATA_AND_REPORTS = "DATA_AND_REPORTS"
    AI_AND_AUTOMATION = "AI_AND_AUTOMATION"
    OTHER = "OTHER"


class RequestPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"


class ClassificationSource(str, Enum):
    RULES = "rules"
    LLM = "llm"
    HUMAN = "human"


class EventActor(str, Enum):
    SYSTEM = "system"
    HUMAN = "human"
    DEMO_USER = "demo_user"


class EventType(str, Enum):
    REQUEST_CREATED = "REQUEST_CREATED"
    CLASSIFICATION_APPLIED = "CLASSIFICATION_APPLIED"
    CLASSIFICATION_REVIEWED = "CLASSIFICATION_REVIEWED"
    STATUS_CHANGED = "STATUS_CHANGED"
    CLASSIFICATION_FAILED = "CLASSIFICATION_FAILED"
