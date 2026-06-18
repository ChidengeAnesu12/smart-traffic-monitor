"""
Video Router
Handles video upload and processing endpoints.
"""

import sys
import uuid
import asyncio
import tempfile
import logging
from pathlib import Path
from typing import Optional

import yaml
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from detection.detector import VehicleDetector
from tracking.tracker import VehicleTracker
from counting.counter import VehicleCounter
from analytics.density import TrafficDensityAnalyzer
from analytics.speed import SpeedEstimator
from analytics.lane_violation import LaneViolationDetector
from analytics.heatmap import TrafficHeatmap
from analytics.analytics_engine import AnalyticsEngine
from database.db_handler import DatabaseHandler

import cv2

router = APIRouter()
logger = logging.getLogger(__name__)

# Job status store {job_id: status_dict}
jobs = {}


def load_config() -> dict:
    with open("configs/config.yaml") as f:
        return yaml.safe_load(f)


def process_video_job(job_id: str, video_path: str, config: dict):
    """Run full pipeline as background job."""
    try:
        jobs[job_id]["status"] = "processing"

        frame_width = config["video"]["frame_width"]
        frame_height = config["video"]["frame_height"]

        detector = VehicleDetector(config)
        tracker = VehicleTracker(config)
        counter = VehicleCounter(config, frame_height)
        density_analyzer = TrafficDensityAnalyzer(config)
        speed_estimator = SpeedEstimator(config, 30.0)
        lane_detector = LaneViolationDetector(config, frame_width)
        heatmap = TrafficHeatmap(frame_width, frame_height)
        analytics = AnalyticsEngine(config)
        db = DatabaseHandler(config)
        db.create_session(analytics.session_id, video_path)

        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        speed_estimator.fps = fps

        output_path = f"data/outputs/{job_id}_output.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(
            output_path, fourcc, fps, (frame_width, frame_height)
        )

        frame_count = 0
        last_frame = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (frame_width, frame_height))
            last_frame = frame.copy()

            detections = detector.detect(frame)
            tracked = tracker.update(detections, frame)
            tracked_speed = speed_estimator.update(tracked)
            tracked_violations = lane_detector.update(tracked_speed, frame_count)
            counts = counter.update(tracked)
            density = density_analyzer.update(tracked)
            heatmap.update(tracked)
            analytics.record_frame(frame_count, tracked_violations, density, counts)

            frame_count += 1
            jobs[job_id]["progress"] = round(frame_count / total_frames * 100)
            jobs[job_id]["current_frame"] = frame_count
            jobs[job_id]["counts"] = counts
            jobs[job_id]["density"] = {
                "level": density["level"],
                "score": density["density_score"],
                "vehicle_count": density["vehicle_count"],
            }

        cap.release()
        writer.release()

        # Save heatmap
        heatmap_path = f"data/outputs/{job_id}_heatmap.jpg"
        if last_frame is not None:
            heatmap.save(heatmap_path, background=last_frame)

        # Save to DB
        summary = analytics.get_summary()
        db.update_session(analytics.session_id, summary)
        db.insert_frame_records(analytics.session_id, analytics.frame_records)
        db.insert_vehicles(analytics.session_id, analytics.vehicle_records)
        db.insert_violations(analytics.session_id, lane_detector.violations)
        db.close()

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["session_id"] = analytics.session_id
        jobs[job_id]["summary"] = summary
        jobs[job_id]["heatmap_path"] = heatmap_path

        logger.info(f"Job {job_id} completed.")

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        logger.error(f"Job {job_id} failed: {e}")


@router.post("/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """Upload a video and start processing."""
    if not file.filename.endswith((".mp4", ".avi", ".mov")):
        raise HTTPException(400, "Invalid file type. Use mp4, avi, or mov.")

    job_id = str(uuid.uuid4())[:8]

    # Save uploaded file
    tmp_path = f"data/raw/upload_{job_id}.mp4"
    Path(tmp_path).parent.mkdir(parents=True, exist_ok=True)

    with open(tmp_path, "wb") as f:
        content = await file.read()
        f.write(content)

    config = load_config()
    config["video"]["source"] = tmp_path

    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "filename": file.filename,
        "counts": {},
        "density": {},
    }

    background_tasks.add_task(
        process_video_job, job_id, tmp_path, config
    )

    logger.info(f"Job {job_id} queued for {file.filename}")
    return {"job_id": job_id, "status": "queued"}


@router.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """Get processing job status and progress."""
    if job_id not in jobs:
        raise HTTPException(404, f"Job {job_id} not found.")
    return jobs[job_id]


@router.get("/jobs")
async def list_jobs():
    """List all processing jobs."""
    return list(jobs.values())