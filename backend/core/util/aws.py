import json

import boto3


def trigger_scale_out_event(scale_to: int = 1):
    eventbridge = boto3.client("events", region_name="ap-northeast-2")
    eventbridge.put_events(
        Entries=[
            {
                "Source": "custom.celery.monitor",
                "DetailType": "celery.task.queue_full",
                "Detail": json.dumps({"scale_to": scale_to}),
                "EventBusName": "default",
            }
        ],
    )
