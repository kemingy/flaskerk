from functools import wraps
from pydantic import ValidationError, BaseModel
from flask import Blueprint, abort, request, current_app

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
        self.parse_path(app)
        app.openapi = self

    def update_config(self, app):
        configs = app.config.get('OPENAPI', {})
        for key, value in configs.items():
            setattr(self.config, key, value)

    def register(self, app):
        blueprint = Blueprint(
            self.config.endpoint,
            __name__,
            url_prefix=self.config.url_prefix,
            template_folder=self.config.template_folder,
        )

        blueprint.add_url_rule(
            self.config.endpoint,
            view_func)

        app.register_blueprint(blueprint)

    def generate_spec(self):
        """
        generate OpenAPI spec JSON file
        """
        rules = current_app.url_map.iter_rules()

    def validate(self, Model):
        """
        validate JSON data according to Model schema
        """
        def decorate_validate_request(func):
            @wraps
            def validate_request(*args, **kwargs):
                assert isinstance(Model, BaseModel)
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

    def parse_path(self, app):
        pass
