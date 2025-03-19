import logging
import sys

logger = logging.getLogger()

default_handler = logging.StreamHandler(stream=sys.stderr)
default_handler.setLevel(logging.ERROR)
default_handler.setFormatter(logging.Formatter())

logger.addHandler(default_handler)
