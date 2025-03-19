from typing import TypedDict, Literal
from botocore.client import BaseClient
from pandas import DataFrame


class UploadParams(TypedDict):
    s3_client: BaseClient  # Ref: https://stackoverflow.com/a/68006865
    identity_id: str
    file_name: str
    mode: Literal["public", "protected", "private"]
    bucket_name: str
    data: DataFrame | dict


class UploadFileParams(TypedDict):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_session_token: str
    identity_id: str

    data: DataFrame
    file_name: str
    config: dict
    mode: Literal["public", "protected", "private"]
    bucket_name: str

    upload_data_to_gooder: bool
