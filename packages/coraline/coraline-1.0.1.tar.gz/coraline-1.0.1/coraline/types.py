from enum import Enum


class TableAttr(str, Enum):
    @classmethod
    def get_default(cls):
        # Return first value from __members__
        return list(cls.__members__.values())[0].value


class BillingMode(TableAttr):
    PAY_PER_REQUEST = "PAY_PER_REQUEST"
    PROVISIONED = "PROVISIONED"


class TableClass(TableAttr):
    STANDARD = "STANDARD"
    STANDARD_INFREQUENT_ACCESS = "STANDARD_INFREQUENT_ACCESS"


class HashType(str, Enum):
    HASH = "HASH"
    RANGE = "RANGE"
