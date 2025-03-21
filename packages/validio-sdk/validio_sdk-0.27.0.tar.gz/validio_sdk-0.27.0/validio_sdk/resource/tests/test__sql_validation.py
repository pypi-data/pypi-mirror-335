import asyncio
from typing import Any, cast
from unittest import mock
from unittest.mock import AsyncMock, Mock

from validio_sdk.resource import (
    credentials,
    filters,
    segmentations,
    sources,
    validators,
    windows,
)
from validio_sdk.resource._diff import DiffContext
from validio_sdk.resource._server_resources import _maybe_validate_queries


@mock.patch("validio_sdk._api.api.validate_sql_validator_query")
def test__should_invoke_sql_validation_request(
    mocked_fn: AsyncMock,
) -> None:
    c1 = credentials.PostgreSqlCredential("c1", "host", 1234, "user", "password", "db")
    c1._id.value = "c1"
    s1 = sources.PostgreSqlSource("s1", c1, "db", "table", 41, None, "schema")
    s1._id.value = "s1"
    w1 = windows.GlobalWindow("w1", s1)
    w1._id.value = "w1"
    seg1 = segmentations.Segmentation("seg1", s1, [])
    seg1._id.value = "seg1"
    query = "SELECT * FROM my_table"
    v1 = validators.SqlValidator("v1", cast(Any, w1), seg1, query)
    ctx = DiffContext(
        credentials={"c1": c1},
        channels={},
        sources={"s1": s1},
        windows={"w1": w1},
        filters={},
        segmentations={"seg1": seg1},
        validators={"v1": v1},
        notification_rules={},
    )
    session_mock = Mock()
    asyncio.run(_maybe_validate_queries([v1], ctx, session_mock, True))
    mocked_fn.assert_called_with(session_mock, query, "v1", "s1", "seg1", "w1")


@mock.patch("validio_sdk._api.api.validate_sql_validator_query")
def test__should_skip_invoking_sql_validation_request_for_azure(
    mocked_fn: AsyncMock,
) -> None:
    c2 = credentials.AzureSynapseEntraIdCredential(
        "c2",
        "host",
        1234,
        credentials.AzureSynapseBackendType.SERVERLESS_SQL_POOL,
        "client_id",
        "client_secret",
    )
    c2._id.value = "c2"
    s2 = sources.AzureSynapseSource("s2", c2, "db", "table", 42, None, "schema")
    s2._id.value = "s2"
    w2 = windows.GlobalWindow("w2", s2)
    w2._id.value = "w2"
    seg2 = segmentations.Segmentation("seg2", s2, [])
    seg2._id.value = "seg2"
    v2 = validators.SqlValidator("v2", cast(Any, w2), seg2, "SELECT * FROM my_table")
    ctx = DiffContext(
        credentials={"c2": c2},
        channels={},
        sources={"s2": s2},
        windows={"w2": w2},
        filters={},
        segmentations={"seg2": seg2},
        validators={"v2": v2},
        notification_rules={},
    )
    session_mock = Mock()
    asyncio.run(_maybe_validate_queries([v2], ctx, session_mock, True))
    mocked_fn.assert_not_called()


@mock.patch("validio_sdk._api.api.validate_sql_filter_query")
def test__should_invoke_filter_sql_validation_request(
    mocked_fn: AsyncMock,
) -> None:
    c3 = credentials.PostgreSqlCredential("c3", "host", 1234, "user", "password", "db")
    c3._id.value = "c3"
    s3 = sources.PostgreSqlSource("s3", c3, "db", "table", 41, None, "schema")
    s3._id.value = "s3"
    query = "id = '123'"
    f1 = filters.SqlFilter(query, "f1", s3)
    ctx = DiffContext(
        credentials={"c3": c3},
        channels={},
        sources={"s3": s3},
        windows={},
        filters={"f1": f1},
        segmentations={},
        validators={},
        notification_rules={},
    )
    session_mock = Mock()
    asyncio.run(_maybe_validate_queries([f1], ctx, session_mock, True))
    mocked_fn.assert_called_with(session_mock, query, "f1", "s3")


@mock.patch("validio_sdk._api.api.validate_sql_filter_query")
def test__should_skip_invoking_filter_sql_validation_request_for_azure(
    mocked_fn: AsyncMock,
) -> None:
    c4 = credentials.AzureSynapseEntraIdCredential(
        "c4",
        "host",
        1234,
        credentials.AzureSynapseBackendType.SERVERLESS_SQL_POOL,
        "client_id",
        "client_secret",
    )
    c4._id.value = "c4"
    s4 = sources.AzureSynapseSource("s4", c4, "db", "table", 42, None, "schema")
    s4._id.value = "s4"
    f2 = filters.SqlFilter("SELECT * FROM my_table", "f2", s4)
    ctx = DiffContext(
        credentials={"c4": c4},
        channels={},
        sources={"s4": s4},
        windows={},
        filters={"f2": f2},
        segmentations={},
        validators={},
        notification_rules={},
    )
    session_mock = Mock()
    asyncio.run(_maybe_validate_queries([f2], ctx, session_mock, True))
    mocked_fn.assert_not_called()
