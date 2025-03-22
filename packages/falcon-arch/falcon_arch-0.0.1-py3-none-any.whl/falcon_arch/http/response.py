from flask import jsonify, make_response, redirect, send_file, render_template

class Response:
    """Encapsula a resposta do Flask para um formato mais estruturado."""

    @staticmethod
    def render(view, **context):
        """Renderiza um template com contexto fornecido."""
        return render_template(view, **context)

    @staticmethod
    def json(data, status=200, headers=None):
        """Retorna uma resposta JSON."""
        response = make_response(jsonify(data), status)
        if headers:
            for key, value in headers.items():
                response.headers[key] = value
        return response

    @staticmethod
    def success(data, message="Success", status=200):
        """Retorna um JSON de sucesso padrão."""
        return Response.json({"message": message, "data": data}, status)

    @staticmethod
    def error(message="Error", status=400, data=None):
        """Retorna um JSON de erro padrão."""
        return Response.json({"message": message, "error": True, "data": data}, status)

    @staticmethod
    def text(content, status=200, headers=None):
        """Retorna uma resposta de texto puro."""
        response = make_response(content, status)
        response.mimetype = "text/plain"
        if headers:
            for key, value in headers.items():
                response.headers[key] = value
        return response

    @staticmethod
    def html(content, status=200, headers=None):
        """Retorna uma resposta HTML."""
        response = make_response(content, status)
        response.mimetype = "text/html"
        if headers:
            for key, value in headers.items():
                response.headers[key] = value
        return response

    @staticmethod
    def redirect(url, status=302):
        """Faz um redirecionamento para outra URL."""
        return redirect(url, status)

    @staticmethod
    def download(filepath, filename=None, as_attachment=True):
        """Faz o download de um arquivo."""
        return send_file(filepath, as_attachment=as_attachment, download_name=filename)

    @staticmethod
    def make(response, status=200, headers=None, mimetype="application/json"):
        """Cria uma resposta personalizada."""
        resp = make_response(response, status)
        resp.mimetype = mimetype
        if headers:
            for key, value in headers.items():
                resp.headers[key] = value
        return resp
