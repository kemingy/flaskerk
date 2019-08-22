from flask import Flask, request, abort, jsonify, make_response
from pydantic import BaseModel, Schema
from random import random

from flaskerk import Flaskerk, HTTPException
# from werkzeug.exceptions import HTTPException


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


# define customized error
e555 = HTTPException(code=555, msg='random error')


@app.route('/ping')
@api.validate(expt=[e555])
def index():
    if random() < 0.5:
        abort(make_response(jsonify('lucky for you'), 555))
    return jsonify('pong')


@app.route('/api/inference', methods=['POST'])
@api.validate(Query, Response, [HTTPException(code=429)])
def inference():
    if random() < 0.5:
        abort(make_response(jsonify('too much request, wait a second'), 429))
    query = request.query
    return Response(label=(len(query.text) % 10), score=random())


if __name__ == '__main__':
    app.run()
