import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db.session import Base
from backend.app.repositories.eval_repository import EvalRepository
from scripts.seed_golden_dataset import seed_database


@pytest.fixture
def seed_db():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_seed_golden_dataset(seed_db):
    result = seed_database(seed_db)
    assert result["dataset_id"] is not None
    assert result["total_test_cases"] == 10
    assert result["prompts_seeded"] == 2

    repo = EvalRepository(seed_db)
    dataset = repo.get_dataset(result["dataset_id"])
    assert dataset is not None
    assert dataset.category == "TRIBUTARIO"

    cases = repo.list_test_cases(dataset.id)
    assert len(cases) == 10
    first = cases[0]
    assert len(first.required_keywords) > 0
    assert len(first.forbidden_terms) > 0

    prompts = repo.list_prompt_versions()
    assert len(prompts) == 2
