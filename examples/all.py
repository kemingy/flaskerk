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
