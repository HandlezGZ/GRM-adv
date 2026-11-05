import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship

from backend.app.db.session import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EvalDataset(Base):
    __tablename__ = "eval_datasets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, default="TRIBUTARIO")
    created_at = Column(DateTime, default=utc_now, nullable=False)

    test_cases = relationship("EvalTestCase", back_populates="dataset", cascade="all, delete-orphan")
    eval_runs = relationship("EvalRun", back_populates="dataset", cascade="all, delete-orphan")


class EvalTestCase(Base):
    __tablename__ = "eval_test_cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dataset_id = Column(String(36), ForeignKey("eval_datasets.id"), nullable=False)
    title = Column(String(150), nullable=False)
    input_query = Column(Text, nullable=False)
    context_document = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    required_keywords = Column(JSON, default=list, nullable=False)
    forbidden_terms = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    dataset = relationship("EvalDataset", back_populates="test_cases")
    eval_results = relationship("EvalResult", back_populates="test_case", cascade="all, delete-orphan")


class PromptVersion(Base):
    __tablename__ = "prompt_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False)
    system_prompt = Column(Text, nullable=False)
    template_text = Column(Text, nullable=False)
    temperature = Column(Float, default=0.1, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    eval_runs = relationship("EvalRun", back_populates="prompt_version")


class EvalRun(Base):
    __tablename__ = "eval_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dataset_id = Column(String(36), ForeignKey("eval_datasets.id"), nullable=False)
    prompt_version_id = Column(String(36), ForeignKey("prompt_versions.id"), nullable=True)
    model_name = Column(String(100), nullable=False, default="rule-evaluator-v1")
    status = Column(String(30), default="COMPLETED", nullable=False)
    total_cases = Column(Integer, default=0, nullable=False)
    passed_cases = Column(Integer, default=0, nullable=False)
    pass_rate = Column(Float, default=0.0, nullable=False)
    avg_faithfulness = Column(Float, default=0.0, nullable=False)
    avg_relevance = Column(Float, default=0.0, nullable=False)
    avg_schema = Column(Float, default=0.0, nullable=False)
    duration_ms = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    dataset = relationship("EvalDataset", back_populates="eval_runs")
    prompt_version = relationship("PromptVersion", back_populates="eval_runs")
    results = relationship("EvalResult", back_populates="eval_run", cascade="all, delete-orphan")


class EvalResult(Base):
    __tablename__ = "eval_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("eval_runs.id"), nullable=False)
    test_case_id = Column(String(36), ForeignKey("eval_test_cases.id"), nullable=False)
    generated_output = Column(Text, nullable=False)
    faithfulness_score = Column(Float, default=0.0, nullable=False)
    relevance_score = Column(Float, default=0.0, nullable=False)
    schema_score = Column(Float, default=0.0, nullable=False)
    passed = Column(Boolean, default=False, nullable=False)
    failure_reason = Column(String(100), nullable=True)
    diagnostics = Column(JSON, default=dict, nullable=False)
    duration_ms = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    eval_run = relationship("EvalRun", back_populates="results")
    test_case = relationship("EvalTestCase", back_populates="eval_results")
