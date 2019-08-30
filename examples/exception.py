from flask import Flask, request, jsonify
from pydantic import BaseModel, Schema
from random import random

from flaskerk import Flaskerk, HTTPException


app = Flask(__name__)
api = Flaskerk(app)


class Query(BaseModel):
    text: str


class Response(BaseModel):
    label: int
    score: float = Schema(
        ...,
        gt=0,
        lt=1,
    )


# define customized exception
e555 = HTTPException(code=555, msg='random error')


@app.route('/ping')
@api.validate(x=[e555])
def index():
    if random() < 0.5:
        e555.abort()
    return jsonify('pong')


# default exception
e429 = HTTPException(code=429)


@app.route('/api/inference', methods=['POST'])
@api.validate(query=Query, resp=Response, x=[e429])
def inference():
    if random() < 0.5:
        e429.abort()
    query = request.query
    return Response(label=(len(query.text) % 10), score=random())


if __name__ == '__main__':
    app.run()
