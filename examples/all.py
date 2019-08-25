from flask import Flask, request
from pydantic import BaseModel, Schema
from random import random

from flaskerk import Flaskerk, HTTPException, abort_json


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


class Data(BaseModel):
    uid: str
    limit: int
    vip: bool


@app.route('/api/predict/<string(length=2):source>/<string(length=2):target>', methods=['POST'])
@api.validate(query=Query, data=Data, resp=Response, x=[HTTPException(403)])
def predict(source, target):
    print(f'=> from {source} to {target}')  # path
    print(f'Data: {request.json_data}')  # Data
    print(f'Query: {request.query}')  # Query
    if random() < 0.5:
        abort_json(403)
    return Response(label=int(10 * random()), score=random())


if __name__ == '__main__':
    app.run()
