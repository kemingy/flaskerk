# Flaskerk

[![Build Status](https://travis-ci.com/kemingy/flaskerk.svg?branch=master)](https://travis-ci.com/kemingy/flaskerk)
![GitHub](https://img.shields.io/github/license/kemingy/flaskerk)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flaskerk)

Provide OpenAPI document and validation for flask service.

Mainly built for Machine Learning Model services.

## Features

- [x] JSON data(request&response) validation with [pydantic](https://github.com/samuelcolvin/pydantic/)
- [x] Redoc UI
- [x] OpenAPI spec
- [ ] Swagger UI
- [ ] support flask url path validation

## Quick Start

install with `pip install flaskerk` (Python 3.6+)

```py
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
```

try it with `http POST :5000/api/recommend name='hello' uid='uuuuu'`

For more examples, check [examples](/examples).
