"""Boto3 DynamoDB resource — cached across Lambda invocations."""

from __future__ import annotations

import os

import boto3
from botocore.config import Config

_resource = None


def get_dynamodb_resource():
    """Return a cached boto3 DynamoDB resource."""
    global _resource
    if _resource is None:
        endpoint = os.getenv("DYNAMODB_ENDPOINT")  # for local/moto testing
        config = Config(retries={"max_attempts": 3, "mode": "adaptive"})
        kwargs: dict = {"config": config}
        if endpoint:
            kwargs["endpoint_url"] = endpoint
        _resource = boto3.resource("dynamodb", **kwargs)
    return _resource


def get_table(table_name: str):
    """Return a DynamoDB Table object."""
    return get_dynamodb_resource().Table(table_name)
