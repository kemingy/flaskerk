from flask import render_template, jsonify, abort
from flask.views import MethodView


class APIview(MethodView):
    def __init__(self, *args, **kwargs):
        view_args = kwargs.pop('view_args', {})
        self.config = view_args.get('config')
        super().__init__(*args, **kwargs)

    def get(self):
        assert self.config.ui in self.config._support_ui
        ui_file = f'{self.config.ui}.html'
        return render_template(ui_file, spec_url=self.config.filename)


class JSONview(MethodView):
    def __init__(self, *args, **kwargs):
        view_args = kwargs.pop('view_args', {})
        self.config = view_args.get('config')
        super().__init__(*args, **kwargs)

    def get(self, filename):
        if filename == self.config.filename:
            return jsonify(self.config.data)
        abort(404)
