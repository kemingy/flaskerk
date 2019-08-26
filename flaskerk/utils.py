from flask import abort, make_response, jsonify
from werkzeug.routing import parse_rule, parse_converter_args
from werkzeug.exceptions import default_exceptions


def abort_json(code: int, msg: str = ''):
    """
    abort as a JSON response

    :param int code: HTTP status code
    :param str msg: description for this abort
    """
    if not msg:
        assert code in default_exceptions
        msg = default_exceptions[code].description
    abort(make_response(jsonify(message=msg), code))


def parse_url(path: str):
    """
    Parsing Flask route url to get the normal url path and parameter type.

    Based on Werkzeug_ builtin converters.

    .. _werkzeug: https://werkzeug.palletsprojects.com/en/0.15.x/routing/#builtin-converters
    """
    subs = []
    parameters = []

    for converter, arguments, variable in parse_rule(path):
        subs.append(variable)
        if converter is None:
            continue
        if arguments:
            args, kwargs = parse_converter_args(arguments)
        else:
            args, kwargs = [], {}
        schema = None
        if converter == 'any':
            schema = {
                'type': 'array',
                'items': {
                    'type': 'string',
                    'enum': args,
                }
            }
        elif converter == 'int':
            schema = {
                'type': 'integer',
                'format': 'int32',
            }
            if 'max' in kwargs:
                schema['maximum'] = kwargs['max']
            if 'min' in kwargs:
                schema['minimum'] = kwargs['min']
        elif converter == 'float':
            schema = {
                'type': 'number',
                'format': 'float',
            }
        elif converter == 'uuid':
            schema = {
                'type': 'string',
                'format': 'uuid',
            }
        elif converter == 'path':
            schema = {
                'type': 'string',
                'format': 'path',
            }
        elif converter == 'string':
            schema = {
                'type': 'string',
            }
            for prop in ['length', 'maxLength', 'minLength']:
                if prop in kwargs:
                    schema[prop] = kwargs[prop]

        parameters.append({
            'name': variable,
            'in': 'path',
            'required': True,
            'schema': schema,
        })

    return ''.join(subs), parameters
