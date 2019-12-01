from functools import wraps
from pydantic import ValidationError, BaseModel
from flask import Blueprint, abort, request, jsonify, make_response, Flask

from flaskerk.config import Config
from flaskerk.view import APIview
from flaskerk.utils import abort_json, parse_url, get_summary_desc
from flaskerk.exception import HTTPException


class Flaskerk:
    """
    :param app: Flask app instance, you can register it later
    :param configs: key-value pairs in :class:`flaskerk.config.Config`

    example:

    .. code-block:: python

       from flask import Flask
       from flaskerk import Flaskerk

       app = Flask(__name__)
       api = Flaskerk(app, version='0.2', title='Machine Translation service')
    """

    def __init__(self, app=None, **configs):
        self.models = {}
        self.config = Config()
        self.config._spec = None
        for key, value in configs.items():
            setattr(self.config, key, value)

        if app:
            self._init_app(app)

    def _init_app(self, app):
        assert isinstance(app, Flask)
        self.app = app
        self.update_config(**self.app.config.get('OPENAPI', {}))
        self._register_route()
        app.openapi = self

    def register(self, app):
        """
        :param app: `flask.Flask`

        Register to Flask application.

        This function will update some config, and add some routes to Flask
        application. If you have already pass the Flask application when
        Flaskerk is initialized, then it will register automatically.
        """
        self._init_app(app)

    def update_config(self, **kwargs):
        """
        Manually update config.

        This function will be triggered when you register this library to Flask
        instance, and configs in Flask.config['OPENAPI'] will be used to update.
        """
        for key, value in kwargs.items():
            setattr(self.config, key, value)

    def _register_route(self):
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
                return jsonify(self.spec)
            abort(404)

        self.app.register_blueprint(blueprint)

    def bypass(self, func):
        if self.config.mode == 'greedy':
            return False
        elif self.config.mode == 'strict':
            if getattr(func, '_decorator', None) == self:
                return False
            return True
        else:
            decorator = getattr(func, '_decorator', None)
            if decorator and decorator != self:
                return True
            return False

    @property
    def spec(self):
        """
        Get OpenAPI spec for this Flask app.
        """
        if self.config._spec is None:
            self._generate_spec()
        return self.config._spec

    def _generate_spec(self):
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

            # bypass the function decorated by others
            if self.bypass(func):
                continue

            # multiple methods (with different func) may bond to the same path
            if path not in routes:
                routes[path] = {}

            for method in rule.methods:
                if method in ['HEAD', 'OPTIONS']:
                    continue

                summary, desc = get_summary_desc(func)
                spec = {
                    'summary': summary or func.__name__.capitalize(),
                    'description': desc or '',
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

                params = parameters[:]
                if hasattr(func, 'query'):
                    params.append({
                        'name': func.query,
                        'in': 'query',
                        'required': True,
                        'schema': {
                            '$ref': f'#/components/schemas/{func.query}',
                        }
                    })
                spec['parameters'] = params

                spec['responses'] = {}
                has_2xx = False
                if hasattr(func, 'x'):
                    for code, msg in func.x.items():
                        if code.startswith('2'):
                            has_2xx = True
                        spec['responses'][code] = {
                            'description': msg,
                        }

                if hasattr(func, 'resp'):
                    spec['responses']['200'] = {
                        'description': 'Successful Response',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': f'#/components/schemas/{func.resp}'
                                }
                            }
                        },
                    }
                elif not has_2xx:
                    spec['responses']['200'] = {'description': 'Successful Response'}

                if any([hasattr(func, schema)
                        for schema in ('query', 'data', 'resp')]):
                    spec['responses']['422'] = {
                        'description': 'Validation Error',
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
        :param query: ``pydantic.BaseModel`` schema for request. The parsed
                      data will store in :class:`flask.request.query`.
        :param resp: ``pydantic.BaseModel`` schema for response
        :param data: ``pydantic.BaseModel`` schema for JSON data
        :param x: List of :class:`flaskerk.exception.HTTPException`

        validate JSON data according to Model schema

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
                others = ()
                if isinstance(response, tuple) and len(response) > 1:
                    response, others = response[0], response[1:]
                if resp and not isinstance(response, resp):
                    abort_json(500, 'Wrong response type produced by server.')

                if resp:
                    return make_response(jsonify(**response.dict()), *others)
                return make_response(response, *others)

            # register schemas to this function
            for schema, name in zip(
                (query, data, resp), ('query', 'data', 'resp')
            ):
                if schema:
                    assert issubclass(schema, BaseModel)
                    self.models[schema.__name__] = schema.schema()
                    setattr(validate_request, name, schema.__name__)

            # store exception for doc
            code_msg = {}
            for e in x:
                assert isinstance(e, HTTPException)
                code_msg[str(e.code)] = e.msg

            if code_msg:
                validate_request.x = code_msg

            # register this decorator
            validate_request._decorator = self

            return validate_request
        return decorate_validate_request
