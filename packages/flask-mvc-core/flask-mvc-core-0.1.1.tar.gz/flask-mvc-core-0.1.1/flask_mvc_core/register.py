import importlib
import sys
import logging
from os import listdir

_registered_routes = []

def register(func):
    """Decorador para registrar rotas automaticamente."""
    _registered_routes.append(func)
    return func

class Register:
    @staticmethod
    def routes(app):
        """Carrega automaticamente todas as rotas registradas no diretório 'routes'."""
        route_dir = "routes"
        if route_dir not in sys.path:
            sys.path.append(route_dir)

        for filename in listdir(route_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = f"routes.{filename[:-3]}"
                try:
                    importlib.import_module(module_name)
                    logging.info(f"✅ Módulo carregado: {module_name}")
                except Exception as e:
                    logging.error(f"❌ Erro ao carregar {module_name}: {e}")

        for func in _registered_routes:
            try:
                logging.info(f"🔗 Registrando rotas: {func.__name__.upper()}")
                func(app)
            except Exception as e:
                logging.error(f"⚠️ Erro ao registrar {func.__name__}: {e}")
