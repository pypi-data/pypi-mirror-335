import os
import importlib.util
import logging
from flask import Flask
from waitress import serve
from .exceptions.http_exception_helper import HTTPExceptionHelper
from .helps._error import render
from .http.request import Request
from .http.response import Response

class FalconArch(Flask):
    """Custom wrapper for Flask with MVC structure"""
    def __init__(self, import_name="FalconArch", template_folder="app/views", static_folder="public", routes_folder="routes", api_prefix="/api", error_handler=None, **kwargs):
        super().__init__(import_name, template_folder=template_folder, static_folder=static_folder, **kwargs)
        self.__api_prefix = f"/{api_prefix.strip('/')}/"
        self.__error_handler_function = error_handler or self.__handle_errors
        self.__routes_folder = routes_folder
        self.__load_routes()
        self.__register_error_handlers()

    def __register_error_handlers(self):
        """Registers error handlers for common HTTP codes."""
        self.register_error_handler(Exception, self.__error_handler_function)

    def __handle_errors(self, error: Exception):
        """Captures errors and returns custom responses."""
        logging.error(f"❌ The route {Request.path()} does not exist")
        http_error = HTTPExceptionHelper.handle(getattr(error, "code", 500))

        if self.__api_prefix in Request.path():
            return Response.error(message=http_error.description, status=http_error.code)

        if os.path.exists(f"{self.template_folder}/exceptions/{http_error.code}.html"):
            return Response.render(
                view=f"exceptions/{http_error.code}.html",
                code=http_error.code,
                title=http_error.title,
                description=http_error.description
            )
        
        logging.warning(f"📢 To create a custom error page, create the file '{self.template_folder}/exceptions/{http_error.code}.html'")
        return Response.html(
            content=render(
                code=http_error.code,
                title=http_error.title,
                description=http_error.description
            ),
            status=http_error.code
        )

    def __load_routes(self):
        """Automatically loads all blueprints from the 'routes' folder, including subfolders."""
        from .router import Router

        loaded_routes = 0  # Route counter

        for root, _, files in os.walk(self.__routes_folder):
            for filename in files:
                if filename.endswith(".py") and filename != "__init__.py":
                    relative_path = os.path.join(root, filename)
                    module_name = relative_path.replace("/", ".").replace("\\", ".")[:-3]

                    try:
                        spec = importlib.util.spec_from_file_location(module_name, relative_path)
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)

                            for attr_name, attr_value in vars(module).items():
                                if isinstance(attr_value, Router):
                                    self.__register(attr_value)
                                    loaded_routes += 1  # Increment route counter
                                    logging.info(f"✅ Route '{attr_name}' loaded from {module_name}")
                        else:
                            logging.warning(f"⚠️ Invalid module: {module_name}")

                    except Exception as e:
                        logging.error(f"❌ Error importing routes from /{module_name.replace('.', '/')}.py")

        if loaded_routes == 0:
            logging.error(f"❌ No routes imported from '/{self.__routes_folder.strip('/')}'")

    def __register(self, blueprint):
        """Method to centrally register blueprints"""
        logging.info(f"✅ Registering Blueprint: {blueprint.name} with prefix '{blueprint.url_prefix or '/'}'")
        self.register_blueprint(blueprint)
    
    def run(self, host="0.0.0.0", port=80, threads=4, _quiet=False):
        try:
            serve(self, host=host, port=port, threads=threads, _quiet=_quiet)
        except PermissionError:
            logging.error(f"❌ Permission denied! Run with {"Administrator" if os.name == "nt" else "sudo"} or choose a port above 1024.")
        except Exception as e:
            logging.exception("❌ Unexpected error starting the server:")
