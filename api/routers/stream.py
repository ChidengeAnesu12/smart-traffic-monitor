"""
Stream Router
WebSocket endpoint for live CCTV/RTSP stream processing.
"""

import sys
import cv2
import base64
import logging
import yaml
from pathlib import Path

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from detection.detector import VehicleDetector
from tracking.tracker import VehicleTracker
from counting.counter import VehicleCounter
from analytics.density import TrafficDensityAnalyzer
from analytics.speed import SpeedEstimator
from detection.utils import (
    draw_tracks, draw_stats, draw_counting_line,
    draw_density, draw_speed, resize_frame
)

router = APIRouter()
logger = logging.getLogger(__name__)


def load_config() -> dict:
    with open("configs/config.yaml") as f:
        return yaml.safe_load(f)


def frame_to_base64(frame) -> str:
    """Convert OpenCV frame to base64 string for WebSocket."""
    import numpy as np
    _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
    return base64.b64encode(buffer).decode("utf-8")


@router.websocket("/live")
async def live_stream(websocket: WebSocket):
    """
    WebSocket endpoint for live video processing.
    Client sends stream URL, server returns processed frames.
    """
    await websocket.accept()
    logger.info("WebSocket connection established.")

    config = load_config()
    frame_width = config["video"]["frame_width"]
    frame_height = config["video"]["frame_height"]

    detector = VehicleDetector(config)
    tracker = VehicleTracker(config)
    counter = VehicleCounter(config, frame_height)
    density_analyzer = TrafficDensityAnalyzer(config)
    speed_estimator = SpeedEstimator(config, 30.0)

    try:
        # Wait for stream URL from client
        data = await websocket.receive_json()
        stream_url = data.get("url", config["video"]["source"])

        logger.info(f"Opening stream: {stream_url}")
        cap = cv2.VideoCapture(stream_url)

        if not cap.isOpened():
            await websocket.send_json({"error": f"Cannot open stream: {stream_url}"})
            return

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        speed_estimator.fps = fps
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = resize_frame(frame, frame_width, frame_height)

            detections = detector.detect(frame)
            tracked = tracker.update(detections, frame)
            tracked_speed = speed_estimator.update(tracked)
            counts = counter.update(tracked)
            density = density_analyzer.update(tracked)

            annotated = draw_tracks(frame, tracked_speed)
            annotated = draw_speed(annotated, tracked_speed)
            annotated = draw_counting_line(
                annotated, counter.line_y, counts["total"]
            )
            annotated = draw_density(annotated, density)
            annotated = draw_stats(annotated, {
                "Vehicles": density["vehicle_count"],
                "Level": density["level"],
                "Counted": counts["total"],
            })

            # Send frame + analytics to client
            await websocket.send_json({
                "frame": frame_to_base64(annotated),
                "frame_number": frame_count,
                "vehicle_count": density["vehicle_count"],
                "density_level": density["level"],
                "density_score": density["density_score"],
                "total_counted": counts["total"],
                "counts_up": counts["up"],
                "counts_down": counts["down"],
            })

            frame_count += 1

        cap.release()
        await websocket.send_json({"status": "stream_ended"})

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected.")
    except Exception as e:
        logger.error(f"Stream error: {e}")
        await websocket.send_json({"error": str(e)})