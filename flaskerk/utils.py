from inspect import getdoc
from flask import abort, make_response, jsonify
from werkzeug.routing import parse_rule, parse_converter_args
from werkzeug.exceptions import default_exceptions

from flaskerk.const import CONVERTER_TYPE_ANY, CONVERTER_TYPE_INT, CONVERTER_TYPE_FLOAT, \
    CONVERTER_TYPE_UUID, CONVERTER_TYPE_PATH, CONVERTER_TYPE_STRING, CONVERTER_TYPE_DEFAULT
from flaskerk.converters import get_converter_type_any, get_converter_type_int, \
    get_converter_type_float, get_converter_type_uuid, get_converter_type_path, \
    get_converter_type_string, get_converter_type_default

CONVERTER_MAPPING = {
    CONVERTER_TYPE_ANY: get_converter_type_any,
    CONVERTER_TYPE_INT: get_converter_type_int,
    CONVERTER_TYPE_FLOAT: get_converter_type_float,
    CONVERTER_TYPE_UUID: get_converter_type_uuid,
    CONVERTER_TYPE_PATH: get_converter_type_path,
    CONVERTER_TYPE_STRING: get_converter_type_string,
    CONVERTER_TYPE_DEFAULT: get_converter_type_default
}


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
    it will be used as description.
    """
    doc = getdoc(func)
    if not doc:
        return None, None
    doc = doc.split('\n\n', 1)
    if len(doc) == 1:
        return None, doc[0]
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
