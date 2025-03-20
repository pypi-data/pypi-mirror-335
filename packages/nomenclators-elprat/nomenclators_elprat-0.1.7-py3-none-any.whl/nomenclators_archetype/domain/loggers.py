"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón(y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
import logging
import sys
import os

LOGGER_LEVEL_ENV_NAME = "LOGGER_LEVEL"
LOGGER_LEVEL_DEFAULT = "INFO"
LOGGER_LEVEL = os.getenv(LOGGER_LEVEL_ENV_NAME, LOGGER_LEVEL_DEFAULT).upper()

DEFAULT_LOGGER_ENV_NAME = "DEFAULT_LOGGER_NAME"
DEFAULT_LOGGER_NAME_DEFAULT = "default_logger"
DEFAULT_LOGGER_NAME = os.getenv(
    DEFAULT_LOGGER_ENV_NAME, DEFAULT_LOGGER_NAME_DEFAULT)

# Default Logger
logging.basicConfig(
    level=getattr(logging, LOGGER_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)
default_logger = logging.getLogger(DEFAULT_LOGGER_NAME)
