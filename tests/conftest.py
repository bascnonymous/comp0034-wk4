import os
from pathlib import Path
import pytest
from paralympics import create_app


@pytest.fixture(scope="module")
def app():
    """Fixture that creates a test app.

    The app is created with test config parameters that include a temporary database. The app is created once for
    each test module.

    Returns:
        app A Flask app with a test config
    """
    # Location for the temporary testing database
    db_path = Path(__file__).parent.parent.joinpath("data", "paralympics_testdb.sqlite")
    test_cfg = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + str(db_path),
    }
    app = create_app(test_config=test_cfg)

    yield app

    # clean up / reset resources
    # Delete the test database
    os.unlink(db_path)


@pytest.fixture()
def client(app):
    return app.test_client()
