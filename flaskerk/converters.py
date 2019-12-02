# converters
#
# check Werkzeug builtin_converters in
# https://werkzeug.palletsprojects.com/en/0.15.x/routing/#builtin-converters


def convert_any(*args, **kwargs):
    """
    Handle converter type "any"

    :param args:
    :param kwargs:
    :return: return schema dict
    """
    schema = {
        'type': 'array',
        'items': {
            'type': 'string',
            'enum': args,
        }
    }
    return schema


def convert_int(*args, **kwargs):
    """
    Handle converter type "int"

    :param args:
    :param kwargs:
    :return: return schema dict
    """
    schema = {
        'type': 'integer',
        'format': 'int32',
    }
    if 'max' in kwargs:
        schema['maximum'] = kwargs['max']
    if 'min' in kwargs:
        schema['minimum'] = kwargs['min']
    return schema


def convert_float(*args, **kwargs):
    """
    Handle converter type "float"

    :param args:
    :param kwargs:
    :return: return schema dict
    """
    schema = {
        'type': 'number',
        'format': 'float',
    }
    return schema


def convert_uuid(*args, **kwargs):
    """
    Handle converter type "uuid"

    :param args:
    :param kwargs:
    :return: return schema dict
    """
    schema = {
        'type': 'string',
        'format': 'uuid',
    }
    return schema


def convert_path(*args, **kwargs):
    """
    Handle converter type "path"

    :param args:
    :param kwargs:
    :return: return schema dict
    """
    schema = {
        'type': 'string',
        'format': 'path',
    }
    return schema


def convert_string(*args, **kwargs):
    """
    Handle converter type "string"

    :param args:
    :param kwargs:
    :return: return schema dict
    """
    schema = {
        'type': 'string',
    }
    for prop in ['length', 'maxLength', 'minLength']:
        if prop in kwargs:
            schema[prop] = kwargs[prop]
    return schema


def convert_default(*args, **kwargs):
    """
    Handle converter type "default"

    :param args:
    :param kwargs:
    :return: return schema dict
    """
    schema = {'type': 'string'}
    return schema


CONVERTER_ANY = 'any'
CONVERTER_INT = 'int'
CONVERTER_FLOAT = 'float'
CONVERTER_UUID = 'uuid'
CONVERTER_PATH = 'path'
CONVERTER_STRING = 'string'
CONVERTER_DEFAULT = 'default'

CONVERTER_MAPPING = {
    CONVERTER_ANY: convert_any,
    CONVERTER_INT: convert_int,
    CONVERTER_FLOAT: convert_float,
    CONVERTER_UUID: convert_uuid,
    CONVERTER_PATH: convert_path,
    CONVERTER_STRING: convert_string,
    CONVERTER_DEFAULT: convert_default
}
