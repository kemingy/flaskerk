from flask import Flask, request, abort, jsonify
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


@app.route('/ping')
@api.validate(expt=[HTTPException(code=444, msg='random error')])
def index():
    if random() < 0.5:
        abort(555)
    return jsonify('pong')


@app.route('/api/inference', methods=['POST'])
@api.validate(Query, Response, [HTTPException(code=429, msg='too many requests')])
def inference():
    if random() < 0.5:
        abort(429)
    query = request.query
    return Response(label=(len(query.text) % 10), score=random())


if __name__ == '__main__':
    app.run()
