.. flaskerk documentation master file, created by
   sphinx-quickstart on Tue Aug 20 15:42:05 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to flaskerk's documentation!
========================================

Provide OpenAPI document and validation for flask service.

Mainly built for Machine Learning Model services.

Features
--------

- [x] JSON data(request&response) validation with pydantic_
- [x] support HTTP exceptions (default&customized)
- [x] OpenAPI_ spec
- [x] Redoc_ UI
- [ ] Swagger_ UI
- [ ] support flask url path validation
- [ ] support header validation
- [ ] support cookie validation

.. _pydantic: https://github.com/samuelcolvin/pydantic/
.. _openapi: https://github.com/OAI/OpenAPI-Specification
.. _redoc: https://github.com/Redocly/redoc
.. _swagger: https://github.com/swagger-api/swagger-ui

Quick Start
-----------

.. code:: py

    from typing import List
    from flask import Flask, request
    from flaskerk import Flaskerk
    from pydantic import BaseModel

    class Query(BaseModel):
        name: str
        uid: str
        limit: int = 5

    class Response(BaseModel):
        users: List[str]

    app = Flask(__name__)
    api = Flaskerk(app)

    @app.route('/api/recommend', methods=['POST'])
    @api.validate(query=Query, resp=Response)
    def recommend():
        # algorithm
        user = request.query
        print(user.name, user.uid)
        return Response(users=['xxx'] * user.limit)

    if __name__ == '__main__':
        app.run()

try it with ``http POST :5000/api/recommend name='hello' uid='uuuuu'``


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   doc



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
