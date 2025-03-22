import os
import uuid
import re
import logging
from flask import Blueprint
from .exceptions.http_exception import HTTPException
from .http.request import Request
from .http.response import Response

class Router(Blueprint):
    """
    Flask Blueprint extension that adds custom handling for prefixes,
    route paths, and dynamic loading of controllers.
    """
    def __init__(self, path: str = "/", prefix: str = "/", **kwargs):
        """
        Router constructor.
        
        :param path: Base path for the routes. Example: "/" or "/my-route".
                     This path is used to locate the controller directory.
        :param prefix: Optional prefix for routes. Example: "/api".
                       This prefix will be used to construct route URLs.
        :param kwargs: Additional parameters for the Blueprint (e.g., static_folder, template_folder, etc.).
        """
        # Generate a unique name to avoid conflicts between blueprints
        blueprint_name = f"{self.__class__.__name__}_{uuid.uuid4().hex[:8]}"
        
        # Validate and normalize prefix and path values
        self._prefix = self.__validate_prefix(prefix)
        self._path = self.__validate_path(path)

        # Initialize the Blueprint without defining url_prefix, as the prefix will be included in routes
        super().__init__(blueprint_name, __name__, url_prefix=self._prefix, **kwargs)

    def get(self, route: str, controller_action: str):
        return self.__add_route(route, controller_action, methods=["GET"])

    def post(self, route: str, controller_action: str):
        return self.__add_route(route, controller_action, methods=["POST"])

    def put(self, route: str, controller_action: str):
        return self.__add_route(route, controller_action, methods=["PUT"])

    def delete(self, route: str, controller_action: str):
        return self.__add_route(route, controller_action, methods=["DELETE"])

    def patch(self, route: str, controller_action: str):
        return self.__add_route(route, controller_action, methods=["PATCH"])

    def options(self, route: str, controller_action: str):
        return self.__add_route(route, controller_action, methods=["OPTIONS"])

    def head(self, route: str, controller_action: str):
        return self.__add_route(route, controller_action, methods=["HEAD"])

    def trace(self, route: str, controller_action: str):
        return self.__add_route(route, controller_action, methods=["TRACE"])

    def __add_route(self, route: str, controller_action: str, methods: list):
        """
        Adds a route to the blueprint, associating it with a specific controller and action.
        
        :param route: Route to be registered (e.g., "list" or "detail/<id>").
        :param controller_action: String in the format "ControllerName@action" indicating which
                                  controller and method will be called.
        :param methods: List of allowed HTTP methods.
        :return: The handler function that processes the request.
        """
        def handler(**kwargs):
            try:
                controller_name, action_name = controller_action.split("@")
            except ValueError:
                return Response.error("Invalid format for controller_action. Use 'Controller@action'", 500)
            
            try:
                controller = self._load_controller(controller_name)
            except HTTPException as e:
                code = e.response
                message = e.description
                return Response.render(f"exceptions/{code}.html", code=code, message=message)

            if not controller:
                return Response.error(f"🚨 Controller {controller_name} not found", 500)

            try:
                action = getattr(controller, action_name, None)
                if not action:
                    return Response.error(f"⚠️ Method {action_name} not found in controller {controller_name}", 500)

                request = Request()
                response = Response()
                return action(request, response)
            except Exception as e:
                logging.error(f"❌ Error executing {controller_name}@{action_name}: {e}")
                return Response.error(f"❌ Error executing method {action_name}", 500)

        logging.info(f"✅ Registering '{controller_action}' on route '{route}'")
        self.add_url_rule(route, endpoint=controller_action, view_func=handler, methods=methods)
        return handler

    def _load_controller(self, controller_name: str):
        """
        Dynamically loads the controller from the given name.
        
        :param controller_name: Controller name (in CamelCase).
        :return: Controller instance or an error response if not found.
        """
        controller_file = f"{self.__camel_to_snake(controller_name)}_controller"
        try:
            module_path = "app.http.controllers"
            if self._path.strip("/"):
                module_path += f".{self._path.strip('/').replace('/', '.')}"
            module_path += f".{controller_file}"

            module = __import__(module_path, fromlist=[controller_name])
            controller_class = getattr(module, controller_name)
            logging.info(f"✅ Controller '{controller_name}' successfully loaded.")
            return controller_class()
        except (ModuleNotFoundError, AttributeError):
            logging.error(f"❌ Issues loading '{controller_name}' from '{module_path.replace('.', '/')}.py'")
            raise HTTPException(code=404, title="Not Found", description="The requested resource was not found on the server.")

    def __camel_to_snake(self, name: str) -> str:
        """
        Converts a CamelCase name to snake_case.
        
        :param name: Name in CamelCase.
        :return: Converted name in snake_case.
        """
        without_prefix = re.sub(r'(?i)_(controller|Controller)$', '', name)
        without_prefix = re.sub(r'(?i)controller$', '', without_prefix)
        return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', without_prefix).lower()

    def __validate_path(self, path: str) -> str:
        """
        Validates and normalizes the Blueprint path.
        
        :param path: Provided path.
        :return: Normalized path.
        :raises ValueError: If validation fails.
        """
        if not path:
            self.__raise_validation_error("The 'path' of the Blueprint cannot be empty.")
        if not isinstance(path, str):
            self.__raise_validation_error("The 'path' of the Blueprint must be a string.")
        if not path.startswith("/"):
            self.__raise_validation_error("The 'path' of the Blueprint must start with '/'")
        
        normalized_path = path.strip("/").lower()
        controllers_dir = os.path.join("app", "http", "controllers")
        expected_dir = os.path.join(controllers_dir, normalized_path)
        
        if not os.path.exists(expected_dir):
            self.__raise_validation_error(f"The folder 'app/http/controllers/{normalized_path}' does not exist")
        
        return f"/{normalized_path}" if normalized_path else "/"

    def __validate_prefix(self, prefix: str) -> str:
        if not isinstance(prefix, str):
            self.__raise_validation_error("The 'prefix' of the Blueprint must be a string.")
        if prefix and not prefix.startswith("/"):
            self.__raise_validation_error("The 'prefix' of the Blueprint must start with '/'")
        return prefix if prefix else "/"

    def __raise_validation_error(self, message: str):
        logging.error(f"❌ {message}")
        raise ValueError(message)
