import re
import logging
from flask import Blueprint
from .request import Request
from .response import Response

class FlaskMVCBlueprint(Blueprint):
    def __init__(self, path: str, prefix: str = "", **kwargs):
        """Construtor para o Blueprint, com prefixo de rota opcional"""
        if not path:
            raise ValueError("Blueprint 'path' cannot be empty.")

        self.route_prefix = prefix.strip("/") if prefix else ""
        self.route_path = path.lower().strip("/") if path else ""
        
        super().__init__(self.route_path, __name__, **kwargs)
        logging.info(f"Blueprint '{path}' registrado com prefixo '{self.route_prefix}'")

    def get(self, route, controller_action):
        return self.__add_route(route, controller_action, methods=["GET"])

    def post(self, route, controller_action):
        return self.__add_route(route, controller_action, methods=["POST"])

    def put(self, route, controller_action):
        return self.__add_route(route, controller_action, methods=["PUT"])

    def delete(self, route, controller_action):
        return self.__add_route(route, controller_action, methods=["DELETE"])

    def patch(self, route, controller_action):
        return self.__add_route(route, controller_action, methods=["PATCH"])

    def options(self, route, controller_action):
        return self.__add_route(route, controller_action, methods=["OPTIONS"])

    def head(self, route, controller_action):
        return self.__add_route(route, controller_action, methods=["HEAD"])

    def trace(self, route, controller_action):
        return self.__add_route(route, controller_action, methods=["TRACE"])

    def __add_route(self, route: str, controller_action: str, methods: list):
        """Adiciona rotas ao blueprint"""
        full_route = f"/{self.route_prefix}/{route}".strip("/")
        logging.info(f"📍 Registrando rota: {methods} {full_route} -> {controller_action}")
        
        def handler(**kwargs):
            controller_name, action_name = controller_action.split("@")
            controller = self._load_controller(controller_name)

            if not controller:
                return Response.error(f"Controller {controller_name} não encontrado", 500)

            try:
                action = getattr(controller, action_name, None)
                if not action:
                    return Response.error(f"Método {action_name} não encontrado", 500)

                request = Request()
                response = Response()
                return action(request, response)

            except Exception as e:
                logging.error(f"Erro ao executar {controller_name}@{action_name}: {e}")
                return Response.error(f"Erro ao executar o método {action_name}", 500)

        self.add_url_rule(f"/{full_route}", endpoint=controller_action, view_func=handler, methods=methods)
        return handler

    def _load_controller(self, controller_name: str):
        """Carrega dinamicamente o controlador"""
        controller_file = f"{self.___camel_to_snake(controller_name)}_controller"
        try:
            module = __import__(f"app.controllers.{self.route_path}.{controller_file}", fromlist=[controller_name])
            controller_class = getattr(module, controller_name)
            return controller_class()
        except (ModuleNotFoundError, AttributeError) as e:
            logging.error(f"Erro ao carregar controller {controller_name}: {e}")
            return None

    def ___camel_to_snake(self, name):
        without_prefix = re.sub(r'(?i)_(controller|Controller)$', '', name)
        without_prefix = re.sub(r'(?i)controller$', '', without_prefix)

        return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', without_prefix).lower()
