"""
DigiIn Developer Platform — Webhook Dispatcher
Delivers asynchronous domain events to registered developer applications with cryptographic HMAC-SHA256 signatures.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time
from typing import Any


class WebhookSubscription:
    def __init__(self, id: str, application_id: str, target_url: str, secret_key: str, events: list[str]):
        self.id = id
        self.application_id = application_id
        self.target_url = target_url
        self.secret_key = secret_key
        self.events = events
        self.active = True

class WebhookDispatcher:
    def __init__(self):
        self._subscriptions: dict[str, WebhookSubscription] = {}
        self._delivery_history: list[dict[str, Any]] = []

    def register_subscription(
        self,
        application_id: str,
        target_url: str,
        events: list[str],
        secret_key: str | None = None
    ) -> WebhookSubscription:
        sub_id = f"sub_{secrets.token_hex(8)}"
        secret = secret_key or secrets.token_hex(20)
        sub = WebhookSubscription(
            id=sub_id,
            application_id=application_id,
            target_url=target_url,
            secret_key=secret,
            events=events
        )
        self._subscriptions[sub_id] = sub
        return sub

    def dispatch_event(
        self,
        event_type: str,
        application_id: str,
        payload: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Dispatches webhook to all subscriptions matching application and event_type.
        Computes X-DigiIn-Signature (HMAC-SHA256) over timestamp and JSON body.
        """
        deliveries = []
        matching = [
            s for s in self._subscriptions.values()
            if s.application_id == application_id and s.active and event_type in s.events
        ]

        now = time.time()
        event_id = f"evt_{secrets.token_hex(12)}"
        body_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")

        for sub in matching:
            ts_str = str(now)
            signed_payload = f"{ts_str}.".encode() + body_bytes
            sig = hmac.new(
                sub.secret_key.encode("utf-8"),
                signed_payload,
                hashlib.sha256
            ).hexdigest()

            delivery_record = {
                "eventId": event_id,
                "subscriptionId": sub.id,
                "targetUrl": sub.target_url,
                "eventType": event_type,
                "timestamp": ts_str,
                "signature": sig,
                "headers": {
                    "X-DigiIn-Event-ID": event_id,
                    "X-DigiIn-Timestamp": ts_str,
                    "X-DigiIn-Signature": sig,
                },
                "payload": payload,
                "status": "DELIVERED_SIMULATED",
            }
            self._delivery_history.append(delivery_record)
            deliveries.append(delivery_record)

        return deliveries
