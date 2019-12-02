import pytest

from flaskerk.converters import CONVERTER_ANY, CONVERTER_INT, CONVERTER_FLOAT, \
    CONVERTER_UUID, CONVERTER_PATH, CONVERTER_STRING, CONVERTER_DEFAULT
from flaskerk.utils import parse_url

TEST_PARAM_NAME = 'test_param'
EXPECTED_PATH = '/{%s}' % TEST_PARAM_NAME

PARSE_URL_PARAMETRIZE = [
    (
        f'/<{CONVERTER_ANY}(test1, test2, test3, test4, "test,test"):{TEST_PARAM_NAME}>',
        (EXPECTED_PATH,
         [{'name': 'test_param', 'in': 'path', 'required': True, 'schema': {
             'type': 'array',
             'items': {
                 'type': 'string', 'enum': (('test1', 'test2', 'test3', 'test4', 'test,test'))}
         }}])
    ),
    (
        f'/<{CONVERTER_INT}:{TEST_PARAM_NAME}>',
        (EXPECTED_PATH,
         [{'name': 'test_param', 'in': 'path', 'required': True,
           'schema': {'type': 'integer', 'format': 'int32'}}]
         )
    ),
    (
        f'/<{CONVERTER_INT}(max=2):{TEST_PARAM_NAME}>',
        (EXPECTED_PATH,
         [{'name': 'test_param', 'in': 'path', 'required': True,
           'schema': {'type': 'integer', 'maximum': 2, 'format': 'int32'}}]
         )
    ),
    (
        f'/<{CONVERTER_INT}(min=2):{TEST_PARAM_NAME}>',
        (EXPECTED_PATH,
         [{'name': 'test_param', 'in': 'path', 'required': True,
           'schema': {'type': 'integer', 'minimum': 2, 'format': 'int32'}}]
         )
    ),
    (
        f'/<{CONVERTER_FLOAT}:{TEST_PARAM_NAME}>',
        (EXPECTED_PATH,
         [{'name': 'test_param', 'in': 'path', 'required': True, 'schema': {
             'type': 'number', 'format': 'float'}}])
    ),
    (
        f'/<{CONVERTER_UUID}:{TEST_PARAM_NAME}>',
        (EXPECTED_PATH,
         [{'name': 'test_param', 'in': 'path', 'required': True, 'schema': {
             'type': 'string', 'format': 'uuid'}}])
    ),
    (
        f'/<{CONVERTER_PATH}:{TEST_PARAM_NAME}>',
        (EXPECTED_PATH,
         [{'name': 'test_param', 'in': 'path', 'required': True, 'schema': {
             'type': 'string', 'format': 'path'}}])
    ),
    (
        f'/<{CONVERTER_STRING}:{TEST_PARAM_NAME}>',
        (EXPECTED_PATH,
         [{'name': 'test_param', 'in': 'path', 'required': True, 'schema': {'type': 'string'}}])
    ),
    (
        f'/<{CONVERTER_STRING}(length=2):{TEST_PARAM_NAME}>',
        (EXPECTED_PATH,
         [{'name': 'test_param', 'in': 'path', 'required': True, 'schema': {
             'length': 2, 'type': 'string'}}])
    ),
    (
        f'/<{CONVERTER_DEFAULT}:{TEST_PARAM_NAME}>',
        (EXPECTED_PATH,
         [{'name': 'test_param', 'in': 'path', 'required': True, 'schema': {'type': 'string'}}])
    ),
]


@pytest.mark.parametrize('path, expected_data', PARSE_URL_PARAMETRIZE)
def test_parse_url(path, expected_data):
    result_path, result_params = parse_url(path)
    expected_path, expected_params = expected_data
    assert result_path == expected_path
    assert result_params == expected_params
