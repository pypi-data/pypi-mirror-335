from asbool import asbool
from loguru import logger
from stela import env

from coraline.config import CoralConfig
from coraline.field import KeyField, TTLField
from coraline.model import CoralModel
from coraline.types import BillingMode, HashType, TableClass

__version__ = "1.0.1"

__all__ = [
    "CoralModel",
    "KeyField",
    "BillingMode",
    "HashType",
    "CoralConfig",
    "TTLField",
    "TableClass",
]

if asbool(env.get_or_default("CORALINE_SHOW_LOGS", True)):
    logger.enable("coraline")
else:
    logger.disable("coraline")
