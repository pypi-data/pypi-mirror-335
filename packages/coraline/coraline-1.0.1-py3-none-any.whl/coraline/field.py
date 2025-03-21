from pydantic import Field

from coraline.exceptions import ConfigError
from coraline.types import HashType


def KeyField(*args, **kwargs):  # C901
    hash_type: HashType = kwargs.pop("hash_type")
    if not hash_type:
        raise ConfigError("hash_type is required for KeyField")
    if "json_schema_extra" not in kwargs:
        kwargs["json_schema_extra"] = {
            "dynamodb_key": True,
            "dynamodb_hash_type": hash_type,
        }
    else:
        kwargs["json_schema_extra"].update(
            {"dynamodb_key": True, "dynamodb_hash_type": hash_type}
        )
    return Field(*args, **kwargs)


def TTLField(*args, **kwargs):  # C901
    if "json_schema_extra" not in kwargs:
        kwargs["json_schema_extra"] = {
            "dynamodb_ttl": True,
        }
    else:
        kwargs["json_schema_extra"].update({"dynamodb_ttl": True})
    return Field(*args, **kwargs)
