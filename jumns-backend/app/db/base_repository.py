"""Shared DynamoDB CRUD patterns used by all repositories."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from botocore.exceptions import BotoCoreError, ClientError

from app.exceptions import ResourceNotFoundError


def new_id() -> str:
    """Generate a UUID v4 string."""
    return str(uuid.uuid4())


def utc_now_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


class BaseRepository:
    """Thin wrapper around a DynamoDB table with common operations."""

    def __init__(self, table):
        self._table = table

    # -- write ---------------------------------------------------------------

    def put_item(self, item: dict[str, Any]) -> dict[str, Any]:
        try:
            self._table.put_item(Item=item)
            return item
        except (ClientError, BotoCoreError) as exc:
            raise RuntimeError(f"DynamoDB put_item failed: {exc}") from exc

    # -- read ----------------------------------------------------------------

    def get_item(self, key: dict[str, Any]) -> dict[str, Any]:
        try:
            resp = self._table.get_item(Key=key)
        except (ClientError, BotoCoreError) as exc:
            raise RuntimeError(f"DynamoDB get_item failed: {exc}") from exc
        item = resp.get("Item")
        if not item:
            raise ResourceNotFoundError()
        return item

    def query_by_user(
        self,
        user_id: str,
        *,
        scan_forward: bool = True,
        limit: int | None = None,
        filter_expression=None,
        index_name: str | None = None,
    ) -> list[dict[str, Any]]:
        """Query items by userId partition key."""
        from boto3.dynamodb.conditions import Key

        kwargs: dict[str, Any] = {
            "KeyConditionExpression": Key("userId").eq(user_id),
            "ScanIndexForward": scan_forward,
        }
        if limit:
            kwargs["Limit"] = limit
        if filter_expression:
            kwargs["FilterExpression"] = filter_expression
        if index_name:
            kwargs["IndexName"] = index_name
        try:
            resp = self._table.query(**kwargs)
            return resp.get("Items", [])
        except (ClientError, BotoCoreError) as exc:
            raise RuntimeError(f"DynamoDB query failed: {exc}") from exc

    # -- update --------------------------------------------------------------

    def update_item(
        self,
        key: dict[str, Any],
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        """Update specific attributes on an item. Returns the updated item."""
        if not updates:
            return self.get_item(key)

        expr_parts = []
        names: dict[str, str] = {}
        values: dict[str, Any] = {}
        for i, (attr, val) in enumerate(updates.items()):
            placeholder = f"#a{i}"
            value_key = f":v{i}"
            expr_parts.append(f"{placeholder} = {value_key}")
            names[placeholder] = attr
            values[value_key] = val

        try:
            resp = self._table.update_item(
                Key=key,
                UpdateExpression="SET " + ", ".join(expr_parts),
                ExpressionAttributeNames=names,
                ExpressionAttributeValues=values,
                ReturnValues="ALL_NEW",
            )
            return resp.get("Attributes", {})
        except (ClientError, BotoCoreError) as exc:
            raise RuntimeError(f"DynamoDB update_item failed: {exc}") from exc

    # -- delete --------------------------------------------------------------

    def delete_item(self, key: dict[str, Any]) -> None:
        try:
            self._table.delete_item(Key=key)
        except (ClientError, BotoCoreError) as exc:
            raise RuntimeError(f"DynamoDB delete_item failed: {exc}") from exc

    def batch_delete(self, keys: list[dict[str, Any]]) -> None:
        """Delete multiple items using batch_writer (handles pagination)."""
        try:
            with self._table.batch_writer() as batch:
                for key in keys:
                    batch.delete_item(Key=key)
        except (ClientError, BotoCoreError) as exc:
            raise RuntimeError(f"DynamoDB batch_delete failed: {exc}") from exc
