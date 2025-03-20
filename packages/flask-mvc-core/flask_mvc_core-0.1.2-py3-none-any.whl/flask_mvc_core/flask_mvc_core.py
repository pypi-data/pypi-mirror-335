import logging
from flask import Flask

class FlaskMVC(Flask):
    """Wrapper personalizado para Flask com estrutura MVC"""

    def __init__(self, import_name="Flask MVC", template_folder="app/views", static_folder="public", **kwargs):
        super().__init__(import_name, template_folder=template_folder, static_folder=static_folder, **kwargs)

    def register(self, blueprint):
        """Método para registrar blueprints de forma centralizada"""
        logging.info(f"Registrando blueprint: {blueprint.name} com prefixo '{blueprint.route_prefix}'")
        self.register_blueprint(blueprint)
