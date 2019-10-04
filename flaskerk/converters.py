def get_converter_type_any(*args, **kwargs):
    schema = {
        'type': 'array',
        'items': {
            'type': 'string',
            'enum': args,
        }
    }
    return schema


def get_converter_type_int(*args, **kwargs):
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
    schema = {
        'type': 'number',
        'format': 'float',
    }
    return schema


def get_converter_type_uuid(*args, **kwargs):
    schema = {
        'type': 'string',
        'format': 'uuid',
    }
    return schema


def get_converter_type_path(*args, **kwargs):
    schema = {
        'type': 'string',
        'format': 'path',
    }
    return schema


def get_converter_type_string(*args, **kwargs):
    schema = {
        'type': 'string',
    }
    for prop in ['length', 'maxLength', 'minLength']:
        if prop in kwargs:
            schema[prop] = kwargs[prop]
    return schema


def get_converter_type_default(*args, **kwargs):
    schema = {'type': 'string'}
    return schema
