class Config:
    def __init__(self):
        """
        Flaskerk configuration
        """
        self.name = 'docs'
        #: url path for docs
        self.endpoint = '/docs/'
        self.url_prefix = None
        self.template_folder = 'templates'
        #: openapi spec file name
        self.filename = 'openapi.json'

        #: openapi spec version
        self.openapi_veresion = '3.0.2'
        #: document title
        self.title = 'Service Documents'
        #: service version
        self.version = '0.1'
        #: 'redoc' or 'swagger'
        self.ui = 'redoc'

        #: private
        self._support_ui = {'redoc', 'swagger'}
