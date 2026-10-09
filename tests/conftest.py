import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    test_app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "UPLOAD_FOLDER": Path(__file__).resolve().parent / "test-uploads"
    })

    with test_app.app_context():
        db.create_all()

    yield test_app

    with test_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
