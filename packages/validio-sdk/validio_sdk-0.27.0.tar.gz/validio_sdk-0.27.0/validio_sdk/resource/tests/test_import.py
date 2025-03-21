import asyncio

from validio_sdk.code._import import _import
from validio_sdk.resource._resource import DiffContext
from validio_sdk.resource.channels import WebhookChannel
from validio_sdk.resource.credentials import DemoCredential
from validio_sdk.resource.notification_rules import (
    Conditions,
    NotificationRule,
    SegmentCondition,
    SegmentNotificationRuleCondition,
    SourceNotificationRuleCondition,
    TagNotificationRuleCondition,
)
from validio_sdk.resource.sources import DemoSource
from validio_sdk.resource.tags import Tag


# We mostly test import of all resource types in the IaC e2e tests but this is
# here to speed up implementations of changes to import such as new resource
# types and makes TDD faster and easier.
# This test is not meant to be exhaustive.
def test_import_resources() -> None:
    t0 = Tag(key="t0", value="v0")
    t1 = Tag(key="t1", value="v1")
    t2 = Tag(key="t2", value="v2")

    c = DemoCredential(name="my-credential")

    s1 = DemoSource(name="my-source", credential=c, tags=[t0, t1])
    s2 = DemoSource(name="my-source-2", credential=c, tags=[t2])

    ch = WebhookChannel(
        name="my-channel",
        application_link_url="https://link.url",
        webhook_url="https://webhook.url",
        auth_header=None,
    )

    nr = NotificationRule(
        name="my-nr",
        channel=ch,
        conditions=Conditions(
            segment_conditions=[
                SegmentNotificationRuleCondition(
                    segments=[SegmentCondition(field="foo", value="bar")],
                ),
                SegmentNotificationRuleCondition(
                    segments=[SegmentCondition(field="bar", value="baz")],
                ),
            ],
            source_condition=SourceNotificationRuleCondition(sources=[s1, s2]),
            tag_conditions=[
                TagNotificationRuleCondition(
                    tags=[t1, t2],
                ),
            ],
        ),
    )

    ctx = DiffContext(
        credentials={c.name: c},
        sources={s1.name: s1},
        channels={ch.name: ch},
        notification_rules={nr.name: nr},
    )

    tags_ctx = DiffContext(
        tags={
            t0.name: t0,
            t1.name: t1,
            t2.name: t2,
        },
    )

    expected = """
from validio_sdk import *
from validio_sdk.resource.thresholds import *
from validio_sdk.resource.channels import *
from validio_sdk.resource.credentials import *
from validio_sdk.resource.filters import *
from validio_sdk.resource.notification_rules import *
from validio_sdk.resource.segmentations import *
from validio_sdk.resource.sources import *
from validio_sdk.resource.tags import *
from validio_sdk.resource.validators import *
from validio_sdk.resource.windows import *


source_1 = 'my-source-2'  # FIXME: manually change to actual resource reference


tag_0 = Tag(
    key='t0',
    value='v0',
)
tag_1 = Tag(
    key='t1',
    value='v1',
)
tag_2 = Tag(
    key='t2',
    value='v2',
)
credential_0 = DemoCredential(
    name='my-credential',
    ignore_changes=True,
    display_name='my-credential',
)
channel_0 = WebhookChannel(
    name='my-channel',
    ignore_changes=True,
    application_link_url='https://link.url',
    auth_header='UNSET', # FIXME: Add secret value
    display_name='my-channel',
    webhook_url='UNSET', # FIXME: Add secret value
)
source_0 = DemoSource(
    name='my-source',
    credential=credential_0,
    description=None,
    display_name='my-source',
    tags=[tag_0, tag_1],
)
notificationrule_0 = NotificationRule(
    name='my-nr',
    channel=channel_0,
    conditions=Conditions(
        owner_condition=None,
        segment_conditions=[
            SegmentNotificationRuleCondition(
                segments=[SegmentCondition(field='bar', value='baz')],
            ),
            SegmentNotificationRuleCondition(
                segments=[SegmentCondition(field='foo', value='bar')],
            ),
        ],
        severity_condition=None,
        source_condition=SourceNotificationRuleCondition(
            sources=[source_0, source_1],
        ),
        tag_conditions=[
            TagNotificationRuleCondition(
                tags=[tag_1, tag_2],
            ),
        ],
        type_condition=None,
    ),
    display_name='my-nr',
)
"""
    doc = asyncio.run(_import(ctx, tags_ctx))

    assert doc.strip() == expected.strip()
