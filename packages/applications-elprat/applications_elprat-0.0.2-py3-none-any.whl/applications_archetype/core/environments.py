"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón (y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
from enum import Enum


class Environments(Enum):
    """Environments"""

    DEVELOPMENT_ENVIRONMENT = "dev"
    TESTING_ENVIRONMENT = "test"
    INTEGRATION_ENVIRONMENT = "int"
    STAGGING_ENVIRONMENT = "pre"
    PRODUCTION_ENVIRONMENT = "prod"
