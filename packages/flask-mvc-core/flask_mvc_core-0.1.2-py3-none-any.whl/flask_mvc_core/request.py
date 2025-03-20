from flask import request
from collections import defaultdict
from werkzeug.datastructures import MultiDict

class Request:
    def __init__(self):
        self._request = request

    def get(self, key, default=None):
        sources = [
            self._request.view_args,
            self._request.args,
            self._request.json if self._request.is_json else {},
            self._request.form,
            self._request.files
        ]
        data = []
        for source in sources:
            if key in source:
                value = source.getlist(key) if isinstance(source, (MultiDict,)) else source[key]
                data.extend(value if isinstance(value, list) else [value])
        return data[0] if len(data) == 1 else (data if data else default)

    def all(self):
        data = defaultdict(list)
        for source in [self._request.view_args, self._request.args, self._request.form]:
            for key, value in source.items():
                data[key].extend(value if isinstance(value, list) else [value])
        if self._request.is_json:
            for key, value in self._request.json.items():
                data[key].append(value)
        for key, file in self._request.files.items():
            data[key].append(file)
        return {key: values[0] if len(values) == 1 else values for key, values in data.items()}

    def headers(self, key=None):
        return self._request.headers.get(key) if key else dict(self._request.headers)

    def input(self, key, default=None):
        return self.get(key, default)

    def only(self, *keys):
        return {key: self.get(key) for key in keys if self.has(key)}

    def except_(self, *keys):
        return {key: value for key, value in self.all().items() if key not in keys}

    def has(self, key):
        return key in self.all()

    def missing(self, *keys):
        return [key for key in keys if key not in self.all()]

    def file(self, key):
        return self._request.files.get(key)

    def files(self):
        return self._request.files.to_dict()

    def is_json(self):
        return self._request.is_json

    def method(self):
        return self._request.method

    def ip(self):
        return self._request.remote_addr

    def url(self):
        return self._request.url

    def path(self):
        return self._request.path

    def full_path(self):
        return self._request.full_path
