class Config:
    name = 'docs'
    endpoint = '/docs/'
    url_prefix = None
    template_folder = 'templates'
    filename = 'openapi.json'

    openapi_veresion = '3.0.2'
    title = 'Service Documents'
    version = '0.1'


default_config = Config()
