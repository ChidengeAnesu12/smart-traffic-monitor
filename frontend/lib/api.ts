/**
 * API Client
 * Centralized HTTP client for FastAPI backend communication.
 */

import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

// ─── Types ────────────────────────────────────────────────────

export interface Job {
  job_id: string;
  status: "queued" | "processing" | "completed" | "failed";
  progress: number;
  filename: string;
  current_frame?: number;
  counts?: {
    total: number;
    up: number;
    down: number;
  };
  density?: {
    level: string;
    score: number;
    vehicle_count: number;
  };
  session_id?: string;
  summary?: Summary;
  error?: string;
}

export interface Summary {
  session_id: string;
  total_frames: number;
  total_vehicles_counted: number;
  unique_vehicles_tracked: number;
  avg_density: number;
  peak_density: number;
  avg_vehicles_per_frame: number;
  peak_vehicles_per_frame: number;
  total_violations: number;
  vehicle_type_distribution: Record<string, number>;
  density_level_distribution: Record<string, number>;
}

export interface Session {
  id: number;
  session_id: string;
  video_source: string;
  status: string;
  total_frames: number;
  total_counted: number;
  avg_density: number;
  peak_density: number;
  total_violations: number;
  started_at: string;
  ended_at: string;
}

export interface FrameRecord {
  frame_number: number;
  vehicle_count: number;
  density_score: number;
  density_level: string;
}

export interface Vehicle {
  track_id: number;
  label: string;
  avg_speed_kmh: number | null;
  max_speed_kmh: number | null;
  zone: string;
  violation: string | null;
}

// ─── API Functions ────────────────────────────────────────────

export const uploadVideo = async (file: File): Promise<{ job_id: string }> => {
  const formData = new FormData();
  formData.append("file", file);
  const res = await api.post("/api/video/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
};

export const getJobStatus = async (jobId: string): Promise<Job> => {
  const res = await api.get(`/api/video/job/${jobId}`);
  return res.data;
};

export const getAllSessions = async (): Promise<Session[]> => {
  const res = await api.get("/api/sessions/");
  return res.data;
};

export const getSessionSummary = async (sessionId: string): Promise<Session> => {
  const res = await api.get(`/api/sessions/${sessionId}`);
  return res.data;
};

export const getFrameRecords = async (sessionId: string): Promise<FrameRecord[]> => {
  const res = await api.get(`/api/analytics/frames/${sessionId}`);
  return res.data;
};

export const getVehicles = async (sessionId: string): Promise<Vehicle[]> => {
  const res = await api.get(`/api/analytics/vehicles/${sessionId}`);
  return res.data;
};

export const getHeatmapUrl = (jobId: string): string =>
  `${API_BASE}/api/analytics/heatmap/${jobId}`;