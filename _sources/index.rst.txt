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

* Generate API document with redoc_ or swagger_
* Less boilerplate code, annotations are really easy-to-use
* Validate query, JSON data, response data with pydantic_
* Better HTTP exceptions for API services (default & customized) (JSON instead of HTML)

.. _pydantic: https://github.com/samuelcolvin/pydantic/
.. _openapi: https://github.com/OAI/OpenAPI-Specification
.. _redoc: https://github.com/Redocly/redoc
.. _swagger: https://github.com/swagger-api/swagger-ui

Quick Start
-----------

install with :code:`pip install flaskerk` (Python 3.6+)

Simple demo
++++++++++++++

.. code:: py

    from flask import Flask, request, jsonify
    from flaskerk import Flaskerk
    from pydantic import BaseModel

    class Query(BaseModel):
        text: str

    app = Flask(__name__)
    api = Flaskerk()

    @app.route('/api/classify')
    @api.validate(query=Query)
    def classify():
        print(request.query)
        return jsonify(label=0)

    if __name__ == "__main__":
        api.register(app)
        app.run()


Changes you need to make:

* create model with ``pydantic``
* decorate the route function with :class:`flaskerk.Flaskerk.validate`
* specify which part you need in ``validate``
    - ``query`` (args in url)
    - ``data`` (JSON data)
    - ``resp`` (response)
    - ``x`` (HTTP Exceptions)
* register to Flask application

After that, this library will help you validate the incoming request and provide API document in ``/docs``.


More feature
+++++++++++++++

.. code:: py

    from flask import Flask, request, jsonify
    from pydantic import BaseModel, Schema
    from random import random

    from flaskerk import Flaskerk, HTTPException


    app = Flask(__name__)
    api = Flaskerk()


    class Query(BaseModel):
        text: str


    class Response(BaseModel):
        label: int
        score: float = Schema(
            ...,
            gt=0,
            lt=1,
        )


    class Data(BaseModel):
        uid: str
        limit: int
        vip: bool


    e403 = HTTPException(code=403, msg='lucky for you')
    e233 = HTTPException(code=233, msg='it works')


    @app.route('/api/predict/<string(length=2):source>/<string(length=2):target>', methods=['POST'])
    @api.validate(query=Query, data=Data, resp=Response, x=[e403], tags=['model'])
    def predict(source, target):
        """
        predict demo

        demo for `query`, `data`, `resp`, `x`
        """
        print(f'=> from {source} to {target}')  # path
        print(f'Data: {request.json_data}')  # Data
        print(f'Query: {request.query}')  # Query
        if random() < 0.5:
            e403.abort('bad luck')
        return Response(label=int(10 * random()), score=random())


    @app.route('/api/code', methods=['POST'])
    @api.validate(x=[e233], tags=['test'])
    def withcode():
        """
        demo for JSON with status code
        """
        return jsonify('code'), 203


    @app.route('/api/code', methods=['GET'])
    @api.validate()
    def getcode():
        """
        demo for the same route with different methods
        """
        return jsonify('code'), 200


    @app.route('/api/header', methods=['POST'])
    @api.validate(x=[e233], tags=['test', 'demo'])
    def withheader():
        """
        demo for JSON with status code and header
        """
        return jsonify('header'), 203, {'X': 233}


    if __name__ == '__main__':
        api.register(app)
        app.run()


try it with ``http POST ':5000/api/predict/zh/en?text=hello' uid=0b01001001 limit=5 vip=true``


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   doc
   utils



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
