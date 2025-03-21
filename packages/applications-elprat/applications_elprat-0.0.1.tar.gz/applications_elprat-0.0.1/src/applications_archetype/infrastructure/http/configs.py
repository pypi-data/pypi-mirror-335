"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón (y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
from fastapi.middleware.cors import CORSMiddleware


class APIConfig:
    """Configuración de la API."""

    def __init__(self, tags, origins):
        """Inicializa la configuración de la API."""

        self.tags = tags
        self.origins = origins

    def get_tags(self):
        """Devuelve las etiquetas de la configuración."""

        return self.tags

    def get_origins(self):
        """Devuelve los orígenes permitidos de la configuración."""

        return self.origins

    @property
    def corsmiddleware(self):
        """Devuelve el middleware de CORS de la configuración."""

        return CORSMiddleware

    @property
    def methods(self):
        """Devuelve los métodos permitidos de la configuración."""

        return ["*"]

    @property
    def headers(self):
        """Devuelve las cabeceras permitidas de la configuración."""

        return ["*"]

    @property
    def credentials(self):
        """Devuelve las credenciales permitidas de la configuración."""

        return True

    def __str__(self):
        """Representación de la configuración en formato legible."""

        return f"APIConfig(tags={self.tags}, origins={self.origins})"
