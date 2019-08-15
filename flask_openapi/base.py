from functools import wraps
from pydantic import ValidationError
from flask import Blueprint, abort, request

from flask_openapi.config import default_config


class FlaskOpenAPI:
    def __init__(self, app, config=None):
        self.models = set()
        self.config = config or default_config

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.update_config(app)
        self.register(app)

    def update_config(self, app):
        pass

    def register(self, app):
        blueprint = Blueprint()

    def validate(self, Model):
        def decorate_validate_request(func):
            @wraps
            def validate_request(*args, **kwargs):
                self.models.add(Model)
                try:
                    json_obj = request.get_json()
                    model = Model(**json_obj)
                except ValidationError as err:
                    abort(400, err)
                except Exception:
                    raise
                request.model = model
                return func(*args, **kwargs)
            return validate_request
        return decorate_validate_request
