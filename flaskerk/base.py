from functools import wraps
from pydantic import ValidationError, BaseModel
from flask import Blueprint, abort, request, jsonify

from flaskerk.config import default_config
from flaskerk.view import APIview
from flaskerk.exception import HTTPValidationError


class Flaskerk:
    """
    :param app: Flask app instance


    """
    def __init__(self, app, config=None):
        self.models = {}
        self.config = config or default_config

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.update_config()
        self.models[HTTPValidationError.__name__] = HTTPValidationError.schema()
        self.register()
        self.parse_path()
        app.openapi = self

    def update_config(self):
        """
        update config from Flask app config with key 'OPENAPI'
        """
        configs = self.app.config.get('OPENAPI', {})
        for key, value in configs.items():
            setattr(self.config, key, value)

    def register(self):
        """
        register doc blueprint to Flask app
        """
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
        @blueprint.route(f'{self.config.endpoint}<filename>')
        def jsonfile(filename):
            if filename == self.config.filename:
                self.generate_spec()
                return jsonify(self.config.data)
            abort(404)

        self.app.register_blueprint(blueprint)

    def generate_spec(self):
        """
        generate OpenAPI spec JSON file
        """
        routes = {}
        for rule in self.app.url_map.iter_rules():
            if str(rule).startswith(self.config.endpoint) or \
                    str(rule).startswith('/static'):
                continue

            func = self.app.view_functions[rule.endpoint]
            routes[str(rule)] = {}
            for method in rule.methods:
                if method in ['HEAD', 'OPTIONS']:
                    continue

                has_schema = hasattr(func, 'query') or hasattr(func, 'resp')
                spec = {
                    'summary': func.__name__.capitalize(),
                    'operationID': func.__name__ + '__' + method.lower(),
                }
                if has_schema:
                    spec['requestBody'] = {
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': f'#/components/schemas/{func.query}'
                                }
                            }
                        }
                    }
                    spec['responses'] = {
                        '200': {
                            'description': 'Successful Response',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        '$ref': f'#/components/schemas/{func.resp}'
                                    }
                                }
                            }
                        },
                        '422': {
                            'description': 'Validation Error',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        '$ref': '#/components/schemas/HTTPValidationError',
                                    }
                                }
                            }
                        },
                    }
                else:
                    spec['responses'] = {
                        '200': {
                            'description': 'Successful Response',
                            'content': {
                                'application/json': {
                                    'schema': {}
                                }
                            }
                        }
                    }

                routes[str(rule)][method.lower()] = spec

        data = {
            'openapi': self.config.openapi_veresion,
            'info': {
                'title': self.config.title,
                'version': self.config.version,
            },
            'paths': {
                **routes
            },
            'components': {
                'schemas': {
                    name: schema for name, schema in self.models.items()
                },
            }
        }
        self.config.data = data

    def validate(self, query, resp):
        """
        validate JSON data according to Model schema

        :param query: ``pydantic.BaseModel`` schema for request
        :param resp: ``pydantic.BaseModel`` schema for response
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

            self.models[query.__name__] = query.schema()
            self.models[resp.__name__] = resp.schema()
            validate_request.query = query.__name__
            validate_request.resp = resp.__name__
            return validate_request
        return decorate_validate_request

    def parse_path(self):
        pass
