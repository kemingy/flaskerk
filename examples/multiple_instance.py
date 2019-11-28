from flask import Flask, request, jsonify
from flaskerk import Flaskerk
from pydantic import BaseModel


class Query(BaseModel):
    text: str


app = Flask(__name__)
api = Flaskerk()
another = Flaskerk(ui='swagger', mode='strict')


@app.route('/api/classify')
@api.validate(query=Query)
def classify():
    print(request.query)
    return jsonify(label=0)


@app.route('/ping')
def ping():
    return jsonify(msg='pong')


@app.route('/api/recommend')
@another.validate()
def recommend():
    return jsonify(result=[])


if __name__ == "__main__":
    # api.register(app)
    another.register(app)
    app.run()
