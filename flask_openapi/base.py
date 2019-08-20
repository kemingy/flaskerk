import os
import json
from functools import wraps
from pydantic import ValidationError, BaseModel
from flask import Blueprint, abort, request, current_app, jsonify

from flask_openapi.config import default_config
from flask_openapi.view import APIview, JSONview


class FlaskOpenAPI:
    def __init__(self, app, config=None):
        self.models = set()
        self.config = config or default_config

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.update_config()
        self.register()
        self.parse_path()
        app.openapi = self

    def update_config(self):
        configs = self.app.config.get('OPENAPI', {})
        for key, value in configs.items():
            setattr(self.config, key, value)

    def register(self):
        blueprint = Blueprint(
            self.config.name,
            __name__,
            url_prefix=self.config.url_prefix,
            template_folder=self.config.template_folder,
        )

        self.generate_spec()
        # docs
        blueprint.add_url_rule(
            self.config.endpoint,
            self.config.name,
            view_func=APIview().as_view(
                self.config.name,
                view_args=dict(config=self.config),
            )
        )
        # docs/openapi.json
        blueprint.add_url_rule(
            self.config.endpoint + '<filename>',
            view_func=JSONview().as_view(
                self.config.name + '_json',
                view_args=dict(config=self.config),
            )
        )

        self.app.register_blueprint(blueprint)

    def generate_spec(self):
        """
        generate OpenAPI spec JSON file
        """
        routes = {}
        for rule in self.app.url_map.iter_rules():
            routes[str(rule)] = {}
            func = self.app.view_functions[rule.endpoint]
            methods = rule.methods
        data = {
            'openapi': self.config.openapi_veresion,
            'info': {
                'title': self.config.title,
                'version': self.config.version,
            },
            'paths': {
                '/': {
                    'get': {
                        'responses': {
                            '200': {}
                        }
                    }
                }
            },
            'components': {
                'schemas': {
                    model.__name__: model.schema() for model in self.models
                }
            }
        }
        self.config.data = data

    def validate(self, query, resp):
        """
        validate JSON data according to Model schema
        """
        def decorate_validate_request(func):
            @wraps(func)
            def validate_request(*args, **kwargs):
                if not issubclass(query, BaseModel):
                    abort(422, 'Unsupported request data type.')

                try:
                    json_obj = request.get_json()
                    if json_obj is None:
                        json_obj = {}
                    model = query(**json_obj)
                except ValidationError as err:
                    abort(422, err)
                except Exception:
                    raise

                request.query = model
                response = func(*args, **kwargs)
                if not isinstance(response, resp):
                    abort(500, 'Wrong response type produced by server.')

                return jsonify(**response.dict())

            self.models.add(query)
            self.models.add(resp)
            validate_request.query = query.schema()
            validate_request.resp = resp.schema()
            return validate_request
        return decorate_validate_request

    def parse_path(self):
        pass
