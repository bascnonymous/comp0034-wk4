import os
from pathlib import Path
import pytest
from sqlalchemy import exists
from paralympics import create_app
from paralympics import db
from paralympics.models import Region


@pytest.fixture(scope="function")
def new_region(app):
    """Create a new region and add to the database.

    Adds a new Region to the database and also returns an instance of that Region object.
    """
    new_region = Region(NOC="NEW", notes="", region="A new region")
    with app.app_context():
        db.session.add(new_region)
        db.session.commit()

        yield new_region

    # Remove the region from the database at the end of the test if it still exists
    with app.app_context():
        region_exists = db.session.query(exists().where(Region.NOC == "NEW")).scalar()
        if region_exists:
            db.session.delete(new_region)
            db.session.commit()


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
