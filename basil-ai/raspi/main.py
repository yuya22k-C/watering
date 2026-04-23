"""basil-ai Pi-side entrypoint.

Wires the other modules together:
  - schedules 1-day observations (OBSERVATION_TIMES from .env, 2-4 per day)
  - on each observation: camera.capture -> claude_client.call -> safety.decide
    -> mqtt_handler.publish_pump -> db.insert_{decision,api_log,watering}
  - handles sensor abnormality triggers for ad-hoc observations

This file is a skeleton; see CLAUDE.md and docs/ for the contract each
collaborator is expected to satisfy.
"""

from __future__ import annotations


def load_config() -> dict:
    """Load .env via python-dotenv and return a dict of resolved settings."""
    raise NotImplementedError


def run_observation(config: dict) -> None:
    """Perform one full observation cycle.

    Steps:
      1. capture still image
      2. aggregate recent 24h sensors from DB
      3. load last decision from DB
      4. build prompt and call Claude
      5. pass suggestion through safety.decide()
      6. if watering approved: publish_pump(), record watering_history
      7. always: record decisions + api_logs, publish ai/report
      8. notify via LINE on notable events
    """
    raise NotImplementedError


def on_sensor_event(topic: str, payload: dict) -> None:
    """Handle an incoming MQTT sensor message.

    - Persist into `sensors`
    - If value is anomalous (stale, out-of-range, tank empty, weight spike),
      schedule an ad-hoc observation or emit a LINE alert
    """
    raise NotImplementedError


def main() -> None:
    """Wire everything up and enter the event loop.

    TODO:
    - load_config()
    - db.init_db()
    - MqttHandler(...).connect() / loop_start()
    - register on_sensor_event
    - schedule run_observation at OBSERVATION_TIMES
    - block on a stop event; on SIGTERM, stop loop and close DB cleanly
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
