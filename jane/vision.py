from __future__ import annotations

from datetime import datetime
from pathlib import Path

import cv2


def capture_frame(output_dir: str = "captures") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(0)
    ok, frame = cap.read()
    cap.release()

    if not ok:
        raise RuntimeError("Unable to capture webcam frame.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(output_dir) / f"frame_{timestamp}.jpg"
    cv2.imwrite(str(path), frame)
    return str(path)
