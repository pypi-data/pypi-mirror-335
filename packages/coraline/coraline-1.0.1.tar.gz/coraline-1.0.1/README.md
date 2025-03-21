## Welcome to Coraline

Coraline is a Python library that aims to use Pydantic models to work with AWS DynamoDB tables.

### Install

```shell
$ pip install coraline
```

Coraline needs `boto3` to work. If you don't have it installed, you can install it using:

```shell
$ pip install coraline[boto]
```

---

### Documentation

* TODO

---

### Quick Start:

```python
import uuid
from enum import Enum
from coraline import CoralModel, KeyField, HashType
from pydantic import SecretStr, Field


class UserType(Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class Users(CoralModel):
    user_id: uuid.UUID = KeyField(default=lambda: uuid.uuid4(), hash_key=HashType.HASH, alias="userId")
    user_type: UserType = KeyField(..., hash_type=HashType.RANGE, alias="userType")
    name: str
    age: int = Field(..., gt=0)
    password: SecretStr


Users.get_or_create_table()
new_user = Users(name="John Doe", user_type=UserType.USER, age=30, password="123456")
new_user.save()
```

This class will create a DynamoDB table named `Users`, with `PAY_PER_REQUEST` billing mode and using default AWS
session, with the following fields:

* `userId` as a String. It's the Table's Hash Key.
* `userType` as a String. It's the Table's Range Key.
* `name` as a String
* `email` as a Number
* `password` as a String

### Configuring the table

Use the `CoralConfig` class to configure your table.

```python
import uuid
from enum import Enum
from coraline import CoralModel, KeyField, HashType, CoralConfig, BillingMode, TableClass
from pydantic import SecretStr, Field


class UserType(Enum):
    USER = "USER"
    ADMIN = "ADMIN"


def to_camel(string: str) -> str:
    return ''.join(word.capitalize() for word in string.split('_'))


# CoralModel is a subclass of Pydantic's BaseModel
class Users(CoralModel):
    # CoralConfig is a subclass of Pydantic's ConfigDict
    model_config = CoralConfig(
        table_name="MyUsers",
        billing_mode=BillingMode.PROVISIONED,
        read_capacity_units=5,
        write_capacity_units=5,
        alias_generator=to_camel,
        protect_from_exclusion=True,
        table_class=TableClass.STANDARD_INFREQUENT_ACCESS,
        extra_table_params={
            "Tags": [
                {
                    "Key": "Project",
                    "Value": "MyProject"
                }
            ]
        }
    )

    # KeyField is a sub method of Pydantic's Field
    user_id: uuid.UUID = KeyField(default=lambda: uuid.uuid4(), hash_key=HashType.HASH)
    user_type: UserType = KeyField(..., hash_type=HashType.RANGE)
    name: str
    age: int = Field(..., gt=0)
    password: SecretStr
```

For Table Name, Billing Methods, you can use the `BillingMode` and Capacity Units constants. For any other parameter
accepted by `boto3`'s `create_table` use the `extra_table_params` parameter.

---

### Configuring AWS Credentials

To configure boto3's client credentials, Coraline will:

1. Check for Class specific configuration in `model_config`
2. Check for Coraline Environment Variables (
   ex. `CORALINE_AWS_REGION`, `CORALINE_AWS_ACCESS_KEY_ID`, `CORALINE_AWS_SECRET_ACCESS_KEY`)
3. Check for AWS Environment Variables (ex. `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)

#### Env Example:
```dotenv
# Add to .env file:
AWS_REGION="local"
CORALINE_ENDPOINT_URL="http://localhost:8000"
```

#### Class Example:
```python
from coraline import CoralModel, CoralConfig

class Users(CoralModel):
    model_config = CoralConfig(
        aws_region="local",
        aws_endpoint_url="http://localhost:8000"
    )
```

#### Class Example using Boto3 Config instance:
```python
from botocore.config import Config
from coraline import CoralModel, CoralConfig

config = Config(
    region_name="local",
    endpoint_url="http://localhost:8000"
)

class Users(CoralModel):
    model_config = CoralConfig(
        aws_region="local",
        aws_config=config
    )
```

---

### Basic Operations

#### Get or Create Table
Use to get Table info or create the table if it doesn't exist.

```python
table_description: dict = Users.get_or_create_table()
```

#### Get Table Info
Use to get Table info. You can also add boto's client `describe_XXX` methods here, for any describe operation which does not have signature
or the only argument is the TableName:

* Allowable Descriptions Example: `describe_continuous_backups`, `describe_time_to_live`, `descript_limits`, etc...
* Not Allowable Descriptions Example: `describe_backup`, `describe_global_table`, `describe_export`, etc...

```python
table_info: dict = Users.get_table_info(include=["describe_time_to_live"])
```

#### Check if Record exists
Use to check if a record exists in the table. You need to pass on the parameters all hash and range keys defined in Model:

```python
user_exists: bool = Users.exists(user_id="12345678-1234-1234-1234-123456789012", user_type=UserType.USER)
```

#### Get Record
Use to get a record from the table. You need to pass on the parameters all hash and range keys defined in Model:

```python
user: Users = Users.get(user_id="12345678-1234-1234-1234-123456789012", user_type=UserType.USER)
```

#### Save Record
Use to save a record in the table:

```python
new_user = Users(name="John Doe", user_type=UserType.USER, age=30, password="123456")
new_user.save()
```

### Using boto3's Client

You can use boto3's client to perform any operation you need. Just use the `get_client` method:

```python
new_user = Users(name="John Doe", user_type=UserType.USER, age=30, password="123456")
new_user.save()
new_user.get_client().create_backup(
   TableName=new_user.table_name(),  # or Users.get_table_name()
   BackupName="MyBackup"
)
```

---
### Current Project Status

Current status: In Progress

We strong advise to not use this lib in Production projects at this current stage.
Except bugs and breaking changes between each release.

### Future Implementations
* Add option to "update" tables (`create_or_update_table` method)
* Add native support for Global and Local Secondary Indexes
* Add native support for Query operations
* Add native support for TransactWriteItems and TransactGetItems
* Add native support for BatchWriteItems and BatchGetItems

---

### Not working?

Don't panic. Get a towel and, please, open an
[issue](https://github.com/megalus/coraline/issues).
