from flask import Flask, request, jsonify
from pydantic import BaseModel, Schema
from typing import List

from flaskerk import Flaskerk


class Data(BaseModel):
    """
    This is the description of the data model.
    """
    name: str
    limit: int = Schema(5, gt=1, lt=10, description='xxx')
    size: List[int] = []
    text: str = Schema(..., max_length=100)  # ... means no default value

    class Config:
        schema_extra = {
            'examples': [
                {
                    'name': 'user',
                    'size': [2, 3, 4],
                    'text': 'Hello World',
                }
            ]
        }


class Response(BaseModel):
    """
    basic response model
    """
    prob: List[float]


app = Flask(__name__)
api = Flaskerk(app)


@app.route('/api/predict', methods=['POST'])
@api.validate(data=Data, resp=Response)
def predict():
    data = request.json_data
    print(data.name, data.limit, data.size, data.text)
    return Response(prob=[len(data.text)] * data.limit)


@app.route('/')
def index():
    return jsonify(text='hello world')


if __name__ == '__main__':
    app.run()
