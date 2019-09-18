from flask import Flask, request
from pydantic import BaseModel, Schema
from typing import List
from random import random, randint

from flaskerk import Flaskerk


class Category(BaseModel):
    label: int = Schema(
        ...,
        ge=0,
        lt=10,
        description='label index for categories',
    )
    score: List[float]


class Response(BaseModel):
    res: List[Category] = Schema(..., max_items=128)


class Data(BaseModel):
    text: List[str] = Schema(
        ...,
        max_items=128,
    )


app = Flask(__name__)
api = Flaskerk(app)


def get_label(n):
    return [
        Category(label=randint(0, 9), score=[random() for i in range(10)])
        for _ in range(n)
    ]


@app.route('/api/<string(length=2):lang>', methods=['POST'])
@api.validate(data=Data, resp=Response)
def predict(lang):
    print(f'{lang}')
    return Response(res=get_label(len(request.json_data.text)))


if __name__ == '__main__':
    app.run()
