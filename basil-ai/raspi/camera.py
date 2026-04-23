"""USB webcam capture for basil-ai.

Targets Logicool C270 / C920 via OpenCV. ESP32-CAM is explicitly out of scope
(see CLAUDE.md §4.3).
"""

from __future__ import annotations

from pathlib import Path


def capture_still(
    device: str,
    output_dir: str | Path,
    *,
    width: int = 1280,
    height: int = 720,
    warmup_frames: int = 5,
) -> Path:
    """Grab one still frame from the USB camera and save it as JPEG.

    Returns the path to the saved JPEG.

    TODO: open cv2.VideoCapture(device), set WIDTH/HEIGHT, grab `warmup_frames`
    frames to let exposure stabilize, save the last one as
    {output_dir}/YYYY-MM-DDTHHMMSSZ.jpg, and return the path.
    """
    raise NotImplementedError


def encode_base64(image_path: str | Path) -> str:
    """Read a JPEG and return its base64 string (for Claude API image blocks)."""
    raise NotImplementedError
