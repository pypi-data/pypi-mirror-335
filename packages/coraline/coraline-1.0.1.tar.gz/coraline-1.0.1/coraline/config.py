from __future__ import annotations as _annotations

from botocore.config import Config
from pydantic import ConfigDict

from coraline.types import BillingMode, TableClass


class CoralConfig(ConfigDict):
    table_name: str | None
    billing_mode: BillingMode | None
    aws_region: str | None
    aws_secret_access_key: str | None
    aws_access_key_id: str | None
    aws_session_token: str | None
    aws_config: Config | None
    aws_endpoint_url: str | None
    read_capacity_units: int | None
    write_capacity_units: int | None
    protect_from_exclusion: bool | None
    table_class: TableClass | None
    extra_table_params: dict | None
