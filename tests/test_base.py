from flask import Flask
from flaskerk import Flaskerk


def test_import_init():
    app = Flask(__name__)
    api = Flaskerk(app)
    assert api.app == app
