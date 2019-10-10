# Flaskerk

[![Build Status](https://travis-ci.com/kemingy/flaskerk.svg?branch=master)](https://travis-ci.com/kemingy/flaskerk)
![GitHub](https://img.shields.io/github/license/kemingy/flaskerk)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flaskerk)

Provide OpenAPI document and validation for flask service.

Mainly built for Machine Learning Model services.

If you're using Falcon, check my another library [Falibrary](https://github.com/kemingy/falibrary).

## Features

- [x] JSON data(request&response) validation with [pydantic](https://github.com/samuelcolvin/pydantic/)
- [x] support HTTP exceptions (default&customized)
- [x] [OpenAPI spec](https://github.com/OAI/OpenAPI-Specification)
- [x] [Redoc UI](https://github.com/Redocly/redoc)
- [x] [Swagger UI](https://github.com/swagger-api/swagger-ui)
- [x] support flask url path validation
- [ ] support header validation
- [ ] support cookie validation

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

* create model with [`pydantic`](https://github.com/samuelcolvin/pydantic/)
* decorate the route function with `Flaskerk.validate()`
* specify which part you need in `validate`
  * `query` (args in url)
  * `data` (JSON data)
  * `resp` (response)
  * `x` (HTTP Exceptions)
* register to Flask application

After that, this library will help you validate the incoming request and provide API document in `/docs`.

For more details, check the [document](https://kemingy.github.io/flaskerk).


### More feature

```py
from flask import Flask, request
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

@app.route('/api/predict/<string(length=2):source>/<string(length=2):target>', methods=['POST'])
@api.validate(query=Query, data=Data, resp=Response, x=[e403])
def predict(source, target):
    print(f'=> from {source} to {target}')  # path
    print(f'Data: {request.json_data}')  # Data
    print(f'Query: {request.query}')  # Query
    if random() < 0.5:
        e403.abort()
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

> 