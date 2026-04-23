"""MQTT handler for the Pi side.

Connects to the local Mosquitto broker, subscribes to sensor topics,
and publishes pump/LED commands. See docs/mqtt-topics.md for payload schemas.
"""

from __future__ import annotations

from typing import Any, Callable


SensorCallback = Callable[[str, dict[str, Any]], None]
"""Signature: (topic, payload_dict) -> None."""


class MqttHandler:
    """Thin wrapper over paho-mqtt.

    Usage (intended):
        handler = MqttHandler(host, port, username, password, client_id)
        handler.on_sensor = lambda topic, payload: ...
        handler.connect()
        handler.loop_start()
        ...
        handler.publish_pump(ml=25, max_seconds=12, source="claude_guarded",
                             request_id="req-...")
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str | None,
        password: str | None,
        client_id: str,
    ) -> None:
        """Build the client, set credentials and LWT. Do not connect yet.

        TODO: register Last Will on picopico/basil/ai/report with
        {"status":"offline","ts":...}.
        """
        raise NotImplementedError

    def connect(self) -> None:
        """Connect to the broker. Idempotent."""
        raise NotImplementedError

    def loop_start(self) -> None:
        """Start the paho-mqtt network loop thread."""
        raise NotImplementedError

    def loop_stop(self) -> None:
        """Stop the network loop and disconnect cleanly."""
        raise NotImplementedError

    # --- subscribe ---

    def on_sensor(self, callback: SensorCallback) -> None:
        """Register a callback for every picopico/basil/sensor/+ message.

        TODO: also route picopico/basil/status here so the caller sees ESP32
        heartbeats.
        """
        raise NotImplementedError

    # --- publish ---

    def publish_pump(
        self,
        ml: int,
        max_seconds: int,
        source: str,
        request_id: str,
    ) -> None:
        """Send a pump command. Caller is expected to have passed safety already."""
        raise NotImplementedError

    def publish_led(self, on: bool, brightness: int = 100) -> None:
        """Send an LED command. Retained so ESP32 gets it on reconnect."""
        raise NotImplementedError

    def publish_ai_report(self, payload: dict[str, Any]) -> None:
        """Publish Claude decision record to picopico/basil/ai/report."""
        raise NotImplementedError
