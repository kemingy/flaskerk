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
