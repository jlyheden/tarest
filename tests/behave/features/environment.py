import os
import tempfile
from behave import fixture, use_fixture
from tarest import app, init_db


@fixture
def tarest_client(context, *args, **kwargs):
    context.db, path = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////{}".format(path)
    app.testing = True
    context.client = app.test_client()
    with app.app_context():
        init_db()
    yield context.client
    os.close(context.db)
    os.unlink(path)


def before_scenario(context, feature):
    use_fixture(tarest_client, context)
