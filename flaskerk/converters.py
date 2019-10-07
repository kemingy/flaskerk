def get_converter_type_any(*args, **kwargs):
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


def get_converter_type_int(*args, **kwargs):
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


def get_converter_type_float(*args, **kwargs):
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


def get_converter_type_uuid(*args, **kwargs):
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


def get_converter_type_path(*args, **kwargs):
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


def get_converter_type_string(*args, **kwargs):
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


def get_converter_type_default(*args, **kwargs):
    """
    Handle converter type "default"

    :param args:
    :param kwargs:
    :return: return schema dict
    """
    schema = {'type': 'string'}
    return schema
