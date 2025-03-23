from typing import Union
import os

from blue_options.env import load_config, load_env, get_env

load_env(__name__)
load_config(__name__)

HOME = get_env("HOME")

ABCLI_AWS_REGION = get_env("ABCLI_AWS_REGION")

ABCLI_AWS_S3_BUCKET_NAME = get_env(
    "ABCLI_AWS_S3_BUCKET_NAME",
    "kamangir",
)

ABCLI_AWS_S3_PREFIX = get_env(
    "ABCLI_AWS_S3_PREFIX",
    "bolt",
)

ABCLI_AWS_S3_PUBLIC_BUCKET_NAME = get_env("ABCLI_AWS_S3_PUBLIC_BUCKET_NAME")


abcli_object_path = get_env("abcli_object_path")

ABCLI_PATH_STORAGE = get_env(
    "ABCLI_PATH_STORAGE",
    os.path.join(HOME, "storage"),
)

abcli_object_name = get_env("abcli_object_name")

ABCLI_S3_OBJECT_PREFIX = get_env(
    "ABCLI_S3_OBJECT_PREFIX",
    f"s3://{ABCLI_AWS_S3_BUCKET_NAME}/{ABCLI_AWS_S3_PREFIX}",
)


ABCLI_OBJECT_ROOT = get_env(
    "ABCLI_OBJECT_ROOT",
    os.path.join(ABCLI_PATH_STORAGE, "abcli"),
)

abcli_path_git = get_env(
    "abcli_path_git",
    os.path.join(HOME, "git"),
)

ABCLI_PATH_STATIC = get_env("ABCLI_PATH_STATIC")

ABCLI_PUBLIC_PREFIX = get_env("ABCLI_PUBLIC_PREFIX")

VANWATCH_TEST_OBJECT = get_env("VANWATCH_TEST_OBJECT")

# https://www.randomtextgenerator.com/
DUMMY_TEXT = "This is some dummy text. This is some dummy text. This is some dummy text. This is some dummy text. This is some dummy text. This is some dummy text. This is some dummy text. This is some dummy text. This is some dummy text. This is some dummy text."

ABCLI_AWS_RDS_DB = get_env("ABCLI_AWS_RDS_DB")
ABCLI_AWS_RDS_PORT = get_env("ABCLI_AWS_RDS_PORT")
ABCLI_AWS_RDS_USER = get_env("ABCLI_AWS_RDS_USER")

ABCLI_AWS_RDS_HOST = get_env("ABCLI_AWS_RDS_HOST")
ABCLI_AWS_RDS_PASSWORD = get_env("ABCLI_AWS_RDS_PASSWORD")

DATABRICKS_WORKSPACE = get_env("DATABRICKS_WORKSPACE")

DATABRICKS_HOST = get_env("DATABRICKS_HOST")
DATABRICKS_TOKEN = get_env("DATABRICKS_TOKEN")

ABCLI_MLFLOW_EXPERIMENT_PREFIX = get_env("ABCLI_MLFLOW_EXPERIMENT_PREFIX")
