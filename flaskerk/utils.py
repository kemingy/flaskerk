from inspect import getdoc
from flask import abort, make_response, jsonify
from werkzeug.routing import parse_rule, parse_converter_args
from werkzeug.exceptions import default_exceptions

from flaskerk.converters import CONVERTER_MAPPING


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


def get_summary_desc(func):
    """
    get summary, description from `func.__doc__`

    Summary and description are split by '\n\n'. If only one is provided,
    it will be used as summary.
    """
    doc = getdoc(func)
    if not doc:
        return None, None
    doc = doc.split('\n\n', 1)
    if len(doc) == 1:
        return doc[0], None
    return doc


def get_converter(converter: str, *args, **kwargs):
    """
    Get conveter method from converter map

    :param converter: str: converter type
    :param args:
    :param kwargs:
    :return: return schema dict
    """
    return CONVERTER_MAPPING[converter](*args, **kwargs)


def parse_url(path: str):
    """
    Parsing Flask route url to get the normal url path and parameter type.

    Based on Werkzeug_ builtin converters.

    .. _werkzeug: https://werkzeug.palletsprojects.com/en/0.15.x/routing/#builtin-converters
    """
    subs = []
    parameters = []

    for converter, arguments, variable in parse_rule(path):
        if converter is None:
            subs.append(variable)
            continue
        subs.append(f'{{{variable}}}')

        args, kwargs = [], {}

        if arguments:
            args, kwargs = parse_converter_args(arguments)

        schema = get_converter(converter, *args, **kwargs)

        parameters.append({
            'name': variable,
            'in': 'path',
            'required': True,
            'schema': schema,
        })

    return ''.join(subs), parameters
