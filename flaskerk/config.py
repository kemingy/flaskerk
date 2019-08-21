from enum import Enum


class UI(Enum):
    """
    :param: 'redoc' or 'swagger'
    """
    redoc = 'redoc'
    swagger = 'swagger'


class Config:
    """
    Flaskerk configuration
    """
    name = 'docs'
    #: url path for docs
    endpoint = '/docs/'
    url_prefix = None
    template_folder = 'templates'
    #: openapi spec file name
    filename = 'openapi.json'

    #: openapi spec version
    openapi_veresion = '3.0.2'
    #: document title
    title = 'Service Documents'
    #: service version
    version = '0.1'
    #: :class:`.UI`
    ui = UI('redoc')


default_config = Config()
