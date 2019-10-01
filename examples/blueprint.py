from flask import Blueprint, request, Flask, jsonify
from flaskerk import Flaskerk
from pydantic import BaseModel


class Query(BaseModel):
    name: str
    uid: str
    limit: int = 5


bp = Blueprint('bp', __name__)
api = Flaskerk(ui='swagger')


@bp.route('/api/recommend', methods=['POST'])
@api.validate(query=Query)
def recommend():
    query = request.query
    print(query.name, query.uid)
    return jsonify(users=['xxx'] * query.limit)


if __name__ == '__main__':
    app = Flask(__name__)
    app.register_blueprint(bp)
    api.register(app)

    app.run()
