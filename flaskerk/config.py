class Config:
    """
    :ivar endpoint: url path for docs
    :ivar filename: openapi spec file name
    :ivar openapi_version: openapi spec version
    :ivar title: document title
    :ivar version: service version
    :ivar ui: ui theme, choose 'redoc' or 'swagger'
    :ivar mode: mode for route. **normal** includes undecorated routes and
        routes decorated by this instance. **strict** only includes routes
        decorated by this instance. **greedy** includes all the routes.

    Flaskerk configuration.
    """

    def __init__(self):
        self.name = 'docs'
        self.endpoint = '/docs/'
        self.url_prefix = None
        self.template_folder = 'templates'
        self.filename = 'openapi.json'
        self.mode = 'normal'

        self.openapi_veresion = '3.0.2'
        self.title = 'Service Documents'
        self.version = 'latest'
        self.ui = 'redoc'

        self._support_ui = {'redoc', 'swagger'}
        self._support_mode = {'normal', 'greedy', 'strict'}
