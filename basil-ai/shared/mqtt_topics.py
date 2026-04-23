"""MQTT topic constants shared between Pi-side modules.

See docs/mqtt-topics.md for payload schemas and direction.
ESP32 side (C++) hard-codes the same strings; do not attempt to share a header.
"""

# --- ESP32 -> Pi ---
SENSOR_ENV = "picopico/basil/sensor/env"
SENSOR_SOIL = "picopico/basil/sensor/soil"
SENSOR_WEIGHT = "picopico/basil/sensor/weight"
SENSOR_TANK = "picopico/basil/sensor/tank"
STATUS = "picopico/basil/status"

SENSOR_WILDCARD = "picopico/basil/sensor/+"

# --- Pi -> ESP32 ---
COMMAND_PUMP = "picopico/basil/command/pump"
COMMAND_LED = "picopico/basil/command/led"

COMMAND_WILDCARD = "picopico/basil/command/+"

# --- Pi internal / logging ---
AI_REPORT = "picopico/basil/ai/report"
