# Flaskerk

[![Build Status](https://travis-ci.com/kemingy/flaskerk.svg?branch=master)](https://travis-ci.com/kemingy/flaskerk)
![GitHub](https://img.shields.io/github/license/kemingy/flaskerk)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flaskerk)

Provide OpenAPI document and validation for flask service.

Mainly built for Machine Learning Model services.

If you're using Falcon, check my another library [Falibrary](https://github.com/kemingy/falibrary).

## Features

* Generate API document with [Redoc UI](https://github.com/Redocly/redoc) or [Swagger UI](https://github.com/swagger-api/swagger-ui) :yum:
* Less boilerplate code, annotations are really easy-to-use :sparkles:
* Validate query, JSON data, response data with [pydantic](https://github.com/samuelcolvin/pydantic/) :wink:
* Better HTTP exceptions for API services (default & customized) (JSON instead of HTML) :grimacing:

## Quick Start

install with `pip install flaskerk` (Python 3.6+)

### Simple demo

```py
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
```

Changes you need to make:

* create model with [pydantic](https://github.com/samuelcolvin/pydantic/)
* decorate the route function with `Flaskerk.validate()`
* specify which part you need in `validate`
  * `query` (args in url)
    * [builtin converters](https://werkzeug.palletsprojects.com/en/0.15.x/routing/#builtin-converters) (string, path, any, int, float, uuid)
  * `data` (JSON data from request)
  * `resp` (response) this will be transformed to JSON data after validation
  * `x` (HTTP Exceptions list)
  * `tags` (tags for this API route)
* register to Flask application

After that, this library will help you validate the incoming request and provide API document in `/docs`.

| Parameters in `Flaskerk.validate` | Corresponding parameters in `Flask` |
| ------------- | ------------- |
| `query` | `request.query` |
| `data` | `request.json_data` |
| `resp` | \ |
| `x` | \ |

For more details, check the [document](https://kemingy.github.io/flaskerk).


### More feature

```py
from flask import Flask, request
from pydantic import BaseModel, Schema
from random import random
from flaskerk import Flaskerk, HTTPException

app = Flask(__name__)
api = Flaskerk(
    title='Demo Service',
    version='1.0',
    ui='swagger',
)

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

e233 = HTTPException(code=233, msg='lucky for you')

@app.route('/api/predict/<string(length=2):source>/<string(length=2):target>', methods=['POST'])
@api.validate(query=Query, data=Data, resp=Response, x=[e233], tags=['model'])
def predict(source, target):
    """
    predict demo

    demo for `query`, `data`, `resp`, `x`
    """
    print(f'=> from {source} to {target}')  # path
    print(f'Data: {request.json_data}')  # Data
    print(f'Query: {request.query}')  # Query
    if random() < 0.5:
        e233.abort('bad luck')
    return Response(label=int(10 * random()), score=random())

if __name__ == '__main__':
    api.register(app)
    app.run()
```

try it with `http POST ':5000/api/predict/zh/en?text=hello' uid=0b01001001 limit=5 vip=true`

Open the docs in http://127.0.0.1:5000/docs .

For more examples, check [examples](/examples).

## FAQ

> Can I just do the validation without generating API document?

Sure. If you don't register it to Flask application, there won't be document routes.
