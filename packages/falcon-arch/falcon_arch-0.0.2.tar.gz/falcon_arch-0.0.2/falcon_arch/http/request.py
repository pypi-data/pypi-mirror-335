from flask import request
from collections import defaultdict
from werkzeug.datastructures import MultiDict

class Request:
    @staticmethod
    def get(key, default=None):
        sources = [
            request.view_args,
            request.args,
            request.json if request.is_json else {},
            request.form,
            request.files
        ]
        data = []
        for source in sources:
            if key in source:
                value = source.getlist(key) if isinstance(source, (MultiDict,)) else source[key]
                data.extend(value if isinstance(value, list) else [value])
        return data[0] if len(data) == 1 else (data if data else default)

    @staticmethod
    def all():
        data = defaultdict(list)
        for source in [request.view_args, request.args, request.form]:
            for key, value in source.items():
                data[key].extend(value if isinstance(value, list) else [value])
        if request.is_json:
            for key, value in request.json.items():
                data[key].append(value)
        for key, file in request.files.items():
            data[key].append(file)
        return {key: values[0] if len(values) == 1 else values for key, values in data.items()}

    @staticmethod
    def headers(key=None):
        return request.headers.get(key) if key else dict(request.headers)

    @staticmethod
    def input(key, default=None):
        return Request.get(key, default)

    @staticmethod
    def only(*keys):
        return {key: Request.get(key) for key in keys if Request.has(key)}

    @staticmethod
    def except_(*keys):
        return {key: value for key, value in Request.all().items() if key not in keys}

    @staticmethod
    def has(key):
        return key in Request.all()

    @staticmethod
    def missing(*keys):
        return [key for key in keys if key not in Request.all()]

    @staticmethod
    def file(key):
        return request.files.get(key)

    @staticmethod
    def files():
        return request.files.to_dict()

    @staticmethod
    def is_json():
        return request.is_json

    @staticmethod
    def method():
        return request.method

    @staticmethod
    def ip():
        return request.remote_addr

    @staticmethod
    def url():
        return request.url

    @staticmethod
    def path():
        return request.path

    @staticmethod
    def full_path():
        return request.full_path
