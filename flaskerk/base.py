from functools import wraps
from pydantic import ValidationError, BaseModel
from flask import Blueprint, abort, request, jsonify, make_response

from flaskerk.config import default_config
from flaskerk.view import APIview
from flaskerk.utils import abort_json, parse_url
from flaskerk.exception import HTTPException


class Flaskerk:
    """
    :param app: Flask app instance
    :param configs: key-value pairs in :class:`flaskerk.config.Config`

    example:

    .. code-block:: python

       from flask import Flask
       from flaskerk import Flaskerk

       app = Flask(__name__)
       api = Flaskerk(app, version='0.2', title='Machine Translation service')
    """

    def __init__(self, app, **configs):
        self.models = {}
        self.config = default_config
        self.config._spec = None
        for key, value in configs.items():
            setattr(self.config, key, value)

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.update_config()
        self.register()
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
                if self.config._spec is None:
                    self.generate_spec()
                return jsonify(self.config._spec)
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
            path, parameters = parse_url(str(rule))
            routes[path] = {}
            for method in rule.methods:
                if method in ['HEAD', 'OPTIONS']:
                    continue

                spec = {
                    'summary': func.__name__.capitalize(),
                    'operationID': func.__name__ + '__' + method.lower(),
                }

                if hasattr(func, 'data'):
                    spec['requestBody'] = {
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': f'#/components/schemas/{func.data}'
                                }
                            }
                        }
                    }

                if hasattr(func, 'query'):
                    parameters.append({
                        'name': func.query,
                        'in': 'query',
                        'required': True,
                        'schema': {
                            '$ref': f'#/components/schemas/{func.query}',
                        }
                    })
                spec['parameters'] = parameters

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

                routes[path][method.lower()] = spec

        definitions = {}
        for _, schema in self.models.items():
            if 'definitions' in schema:
                for key, value in schema['definitions'].items():
                    definitions[key] = value
                del schema['definitions']

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
            },
            'definitions': definitions
        }
        self.config._spec = data

    def validate(self, query=None, data=None, resp=None, x=[]):
        """
        validate JSON data according to Model schema

        :param query: ``pydantic.BaseModel`` schema for request. The parsed
                      data will store in :class:`flask.request.query`.
        :param resp: ``pydantic.BaseModel`` schema for response
        :param data: ``pydantic.BaseModel`` schema for JSON data
        :param x: List of :class:`flaskerk.exception.HTTPException`

        .. code-block:: python

           from pydantic import BaseModel
           from flask import request, jsonify

           class Query(BaseModel):
               text: str
               limit: int

           @app.route('/api/predict', methods=['POST'])
           @api.validate(data=Query)
           def predict():
               data = request.json_data
               print(data.text, data.limit)
               return jsonify(is_spam=True)

        For more examples, check examples_.

        .. _examples: https://github.com/kemingy/flaskerk/tree/master/examples
        """
        def decorate_validate_request(func):
            @wraps(func)
            def validate_request(*args, **kwargs):
                if query and not issubclass(query, BaseModel):
                    abort_json(500, 'Unsupported request query type.')
                if data and not issubclass(data, BaseModel):
                    abort_json(500, 'Unsupported request data type.')

                try:
                    # validate query
                    arg = request.args
                    if not arg:
                        arg = {}
                    json_query = query(**arg) if query else None

                    # validate data
                    json_obj = request.get_json()
                    if json_obj is None:
                        json_obj = {}
                    json_data = data(**json_obj) if data else None
                except ValidationError as err:
                    abort(make_response(jsonify(message=str(err)), 422))
                except Exception:
                    raise

                request.query = json_query
                request.json_data = json_data
                response = func(*args, **kwargs)
                if resp and not isinstance(response, resp):
                    abort_json(500, 'Wrong response type produced by server.')

                return jsonify(**response.dict()) if resp else response

            # register schemas to this function
            for schema, name in zip(
                (query, data, resp), ('query', 'data', 'resp')
            ):
                if schema:
                    self.models[schema.__name__] = schema.schema()
                    setattr(validate_request, name, schema.__name__)

            # store exception for doc
            code_msg = {}
            for e in x:
                assert isinstance(e, HTTPException)
                code_msg[e.code] = e.msg

            if code_msg:
                validate_request.x = code_msg

            return validate_request
        return decorate_validate_request
