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
