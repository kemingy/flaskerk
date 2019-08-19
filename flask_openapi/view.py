from flask import render_template, jsonify, abort
from flask.views import MethodView


class APIview(MethodView):
    def __init__(self, *args, **kwargs):
        view_args = kwargs.pop('view_args', {})
        self.config = view_args.get('config')
        super().__init__(*args, **kwargs)

    def get(self):
        return render_template('redoc.html', spec_url=self.config.filename)


class JSONview(MethodView):
    def __init__(self, *args, **kwargs):
        view_args = kwargs.pop('view_args', {})
        self.config = view_args.get('config')
        super().__init__(*args, **kwargs)

    def get(self, filename):
        if filename == self.config.filename:
            return jsonify(self.config.data)
        abort(404)
