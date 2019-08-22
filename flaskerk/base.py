from functools import wraps
from pydantic import ValidationError, BaseModel
from flask import Blueprint, abort, request, jsonify, make_response

from flaskerk.config import default_config
from flaskerk.view import APIview
from flaskerk.exception import HTTPException


class Flaskerk:
    """
    :param app: Flask app instance
    :param configs: key-value pairs in :class:`flaskerk.config.Config`

    """
    def __init__(self, app, **configs):
        self.models = {}
        self.config = default_config
        for key, value in configs.items():
            setattr(self.config, key, value)

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.update_config()
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

                spec = {
                    'summary': func.__name__.capitalize(),
                    'operationID': func.__name__ + '__' + method.lower(),
                }

                if hasattr(func, 'query'):
                    spec['requestBody'] = {
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': f'#/components/schemas/{func.query}'
                                }
                            }
                        }
                    }

                if hasattr(func, 'resp'):
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

                if hasattr(func, 'expt'):
                    for code, msg in func.expt.items():
                        spec['responses'][str(code)] = {
                            'description': msg,
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

    def validate(self, query=None, resp=None, expt=[]):
        """
        validate JSON data according to Model schema

        :param query: ``pydantic.BaseModel`` schema for request
        :param resp: ``pydantic.BaseModel`` schema for response
        :param expt: List of :class:`flaskerk.exception.HTTPException`
        """
        def decorate_validate_request(func):
            @wraps(func)
            def validate_request(*args, **kwargs):
                if query and not issubclass(query, BaseModel):
                    abort(make_response(
                        jsonify(message='Unsupported request data type.'),
                        500,
                    ))

                try:
                    json_obj = request.get_json()
                    if json_obj is None:
                        json_obj = {}
                    model = query(**json_obj) if query else {}
                except ValidationError as err:
                    abort(make_response(jsonify(message=str(err)), 422))
                except Exception:
                    raise

                request.query = model
                response = func(*args, **kwargs)
                if resp and not isinstance(response, resp):
                    abort(make_response(
                        jsonify(message='Wrong response type produced by server.'),
                        500,
                    ))

                return jsonify(**response.dict()) if resp else response

            if query:
                self.models[query.__name__] = query.schema()
                validate_request.query = query.__name__
            if resp:
                self.models[resp.__name__] = resp.schema()
                validate_request.resp = resp.__name__

            code_msg = {}
            for e in expt:
                assert isinstance(e, HTTPException)
                code_msg[e.code] = e.msg

            if code_msg:
                validate_request.expt = code_msg

            return validate_request
        return decorate_validate_request

    def parse_path(self):
        pass
