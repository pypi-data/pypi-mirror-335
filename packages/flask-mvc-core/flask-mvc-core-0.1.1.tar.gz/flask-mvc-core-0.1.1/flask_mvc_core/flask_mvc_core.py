import logging
from importlib import import_module
from flask import Flask
from .request import Request
from .response import Response

class FlaskMVC(Flask):
    """Wrapper personalizado para Flask com estrutura MVC"""

    def __init__(self, import_name="Flask MVC", template_folder="app/views", static_folder="public", **kwargs):
        super().__init__(import_name, template_folder=template_folder, static_folder=static_folder, **kwargs)
        self.route_prefix = ""
        self.route_path = ""

    def prefix(self, prefix="", path=""):
        """Define o prefixo e caminho das rotas"""
        self.route_prefix = prefix.strip("/")
        self.route_path = path.strip("/")

    def get(self, route, controller_action):
        return self._add_route(route, controller_action, methods=["GET"])

    def post(self, route, controller_action):
        return self._add_route(route, controller_action, methods=["POST"])

    def put(self, route, controller_action):
        return self._add_route(route, controller_action, methods=["PUT"])

    def delete(self, route, controller_action):
        return self._add_route(route, controller_action, methods=["DELETE"])

    def patch(self, route, controller_action):
        return self._add_route(route, controller_action, methods=["PATCH"])

    def options(self, route, controller_action):
        return self._add_route(route, controller_action, methods=["OPTIONS"])

    def head(self, route, controller_action):
        return self._add_route(route, controller_action, methods=["HEAD"])

    def trace(self, route, controller_action):
        return self._add_route(route, controller_action, methods=["TRACE"])

    def _add_route(self, route, controller_action, methods):
        """Registra a rota e mapeia para o controller correspondente"""
        route = f"{self.route_prefix if self.route_prefix else ''}{route}"
        logging.info(f"📍 Registrando rota: {methods} {route} -> {controller_action}")

        def handler(**kwargs):
            controller_name, action_name = controller_action.split("@")
            controller = self._load_controller(controller_name)

            if not controller:
                logging.error(f"❌ Controller não encontrado: {controller_name}")
                return Response.error(message=f"Controller {controller_name} não encontrado", status=500)

            request = Request()
            response = Response()

            try:
                action = getattr(controller, action_name, None)
                if not action:
                    logging.error(f"⚠️ Método {action_name} não encontrada no controller {controller_name}")
                    return Response.error(message=f"Método {action_name} não encontrada no Controller {controller_name}.", status=500)

                logging.info(f"✅ Executando método: {controller_name}@{action_name}")
                return action(request, response)
            except AttributeError:
                logging.error(f"⚠️ Erro de atributo ao buscar {action_name} em {controller_name}")
                return Response.error(message=f"Método {action_name} não encontrada no Controller {controller_name}.", status=500)
            except Exception as e:
                logging.error(f"🔥 Erro ao executar {controller_name}@{action_name}: {e}")
                return Response.error(message=f"Erro ao executar a método {action_name}.", status=500)

        self.route(route, methods=methods, endpoint=controller_action)(handler)
        return handler

    def _load_controller(self, controller_name):
        """Carrega dinamicamente um controller do diretório correto"""
        controller_name = controller_name.replace("Controller", "")
        module_path = f"app.controllers{f'.{self.route_path.lower()}' if self.route_path else ''}.{controller_name.lower()}_controller"
        class_name = f"{controller_name}Controller"

        try:
            module = import_module(module_path, package=None)
            controller_class = getattr(module, class_name, None)

            return controller_class() if controller_class else None
        except ModuleNotFoundError:
            logging.error(f"❌ Módulo não encontrado: {module_path}")
            return None
        except AttributeError:
            logging.error(f"⚠️ Atributo inválido ao carregar {class_name} de {module_path}")
            return None
