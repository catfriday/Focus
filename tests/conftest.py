import os
import pytest
from alembic.config import Config
from alembic import command
from backend_engineer_interview.app import create_app
from connexion.apps.abstract import TestClient  # type: ignore


@pytest.fixture
def test_client() -> TestClient:
    if os.path.exists("test.db"):
        os.remove("test.db")
    alembic_cfg = Config("./alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", "sqlite:///test.db")
    command.upgrade(alembic_cfg, "head")
    return create_app("test").test_client()
