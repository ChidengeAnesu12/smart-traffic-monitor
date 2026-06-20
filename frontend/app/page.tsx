/**
 * Home Page — Live Processing
 * Upload video and monitor processing in real time.
 */

"use client";

import { useState, useRef, useEffect } from "react";
import { uploadVideo, getJobStatus, getHeatmapUrl, Job } from "@/lib/api";
import StatCard from "@/components/StatCard";
import DensityBadge from "@/components/DensityBadge";

export default function HomePage() {
  const [file, setFile] = useState<File | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<NodeJS.Timeout | null>(null);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setJob(null);

    try {
      const { job_id } = await uploadVideo(file);
      setJob({ job_id, status: "queued", progress: 0, filename: file.name });
      startPolling(job_id);
    } catch (e: any) {
      setError(e.message || "Upload failed.");
    } finally {
      setLoading(false);
    }
  };

  const startPolling = (jobId: string) => {
    pollRef.current = setInterval(async () => {
      try {
        const status = await getJobStatus(jobId);
        setJob(status);
        if (status.status === "completed" || status.status === "failed") {
          clearInterval(pollRef.current!);
        }
      } catch (e) {
        clearInterval(pollRef.current!);
      }
    }, 2000);
  };

  useEffect(() => {
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, []);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Live Traffic Processing</h2>
        <p className="text-gray-500 mt-1">
          Upload a traffic video to run the full AI detection pipeline.
        </p>
      </div>

      {/* Upload Card */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Upload Video</h3>

        <div
          className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-gov-green transition-colors"
          onClick={() => document.getElementById("fileInput")?.click()}
        >
          <input
            id="fileInput"
            type="file"
            accept=".mp4,.avi,.mov"
            className="hidden"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          {file ? (
            <div>
              <p className="text-gov-green font-medium">{file.name}</p>
              <p className="text-gray-500 text-sm mt-1">
                {(file.size / 1024 / 1024).toFixed(1)} MB
              </p>
            </div>
          ) : (
            <div>
              <p className="text-gray-500">Click to upload or drag and drop</p>
              <p className="text-gray-400 text-sm mt-1">MP4, AVI, MOV supported</p>
            </div>
          )}
        </div>

        <button
          onClick={handleUpload}
          disabled={!file || loading}
          className="w-full bg-gov-green hover:bg-gov-green-dark disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-colors"
        >
          {loading ? "Uploading..." : "Run Pipeline"}
        </button>

        {error && (
          <p className="text-red-600 text-sm">{error}</p>
        )}
      </div>

      {/* Job Progress */}
      {job && (
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              Processing: {job.filename}
            </h3>
            <span className={`text-xs font-bold px-3 py-1 rounded-full ${
              job.status === "completed" ? "bg-green-100 text-green-700" :
              job.status === "failed"    ? "bg-red-100 text-red-700" :
              "bg-yellow-100 text-yellow-700"
            }`}>
              {job.status.toUpperCase()}
            </span>
          </div>

          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-gray-500">
              <span>Progress</span>
              <span>{job.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-gov-green h-3 rounded-full transition-all duration-500"
                style={{ width: `${job.progress}%` }}
              />
            </div>
          </div>

          {/* Live Stats */}
          {job.density && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard
                label="Vehicles in Frame"
                value={job.density.vehicle_count}
                color="green"
              />
              <StatCard
                label="Total Counted"
                value={job.counts?.total ?? 0}
                color="blue"
              />
              <StatCard
                label="Density Score"
                value={`${(job.density.score * 100).toFixed(0)}%`}
                color="yellow"
              />
              <StatCard
                label="Current Frame"
                value={job.current_frame ?? 0}
                color="gray"
              />
            </div>
          )}

          {job.density && (
            <div className="flex items-center gap-3">
              <span className="text-gray-500 text-sm">Traffic Level:</span>
              <DensityBadge
                level={job.density.level}
                score={job.density.score}
              />
            </div>
          )}

          {/* Completed Summary */}
          {job.status === "completed" && job.summary && (
            <div className="border-t border-gray-200 pt-6 space-y-4">
              <h4 className="text-gray-900 font-semibold">Final Summary</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard
                  label="Total Frames"
                  value={job.summary.total_frames}
                  color="gray"
                />
                <StatCard
                  label="Vehicles Counted"
                  value={job.summary.total_vehicles_counted}
                  color="green"
                />
                <StatCard
                  label="Unique IDs"
                  value={job.summary.unique_vehicles_tracked}
                  color="blue"
                />
                <StatCard
                  label="Violations"
                  value={job.summary.total_violations}
                  color="red"
                />
              </div>

              {/* Heatmap */}
              <div>
                <h4 className="text-gray-900 font-semibold mb-3">Traffic Heatmap</h4>
                <img
                  src={getHeatmapUrl(job.job_id)}
                  alt="Traffic Heatmap"
                  className="rounded-xl w-full object-cover border border-gray-200"
                  onError={(e) => (e.currentTarget.style.display = "none")}
                />
              </div>
            </div>
          )}

          {job.status === "failed" && (
            <p className="text-red-600">Error: {job.error}</p>
          )}
        </div>
      )}
    </div>
  );
}