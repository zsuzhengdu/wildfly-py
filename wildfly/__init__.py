import logging
from .client import Client  # flake8: noqa

# setup log stream handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)7s | %(name)s | line:%(lineno)4s | %(message)s')
ch.setFormatter(formatter)

# setup package logger
logger = logging.getLogger(__name__)
#logger.setLevel(logging.INFO)
logger.addHandler(ch)

