from flask import abort, make_response, jsonify
from werkzeug.routing import parse_rule, parse_converter_args


def abort_json(code: int, msg: str):
    """
    abort as a JSON response

    :param int code: HTTP status code
    :param str msg: description for this abort
    """
    abort(make_response(jsonify(message=msg), code))


def parse_url(path: str):
    """
    parse Flask route url to get the normal url path and parameter type
    """
    subs = []
    parameters = []

    for converter, arguments, variable in parse_rule(path):
        if converter is None:
            subs.append(variable)
        else:
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
                    'type': 'int',
                }

            parameters.append({
                'name': variable,
                'in': 'path',
                'required': True,
                'schema': schema,
            })

    return ''.join(subs), parameters
