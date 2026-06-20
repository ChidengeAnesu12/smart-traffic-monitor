/**
 * Live CCTV Stream Page
 * Connects to a live RTSP/video stream via WebSocket for
 * real-time vehicle detection and analytics.
 */

"use client";

import { useState } from "react";
import { useLiveStream } from "@/hooks/useLiveStream";
import StatCard from "@/components/StatCard";
import DensityBadge from "@/components/DensityBadge";
import { Radio, Square, Play } from "lucide-react";

export default function LiveStreamPage() {
  const [streamUrl, setStreamUrl] = useState("");
  const { connect, disconnect, connected, frameData, error } = useLiveStream();

  const handleConnect = () => {
    // Falls back to the default configured video source if left blank
    connect(streamUrl.trim() || "");
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Live CCTV Monitoring</h2>
        <p className="text-gray-500 mt-1">
          Connect to an RTSP camera feed or a video stream for real-time analysis.
        </p>
      </div>

      {/* Connection Card */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Stream Source</h3>

        <div className="flex gap-3">
          <input
            type="text"
            value={streamUrl}
            onChange={(e) => setStreamUrl(e.target.value)}
            placeholder="rtsp://username:password@camera-ip:554/stream  (leave blank to use demo video)"
            disabled={connected}
            className="flex-1 border border-gray-300 rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gov-green disabled:bg-gray-100"
          />

          {!connected ? (
            <button
              onClick={handleConnect}
              className="flex items-center gap-2 bg-gov-green hover:bg-gov-green-dark text-white font-semibold px-6 py-2 rounded-xl transition-colors"
            >
              <Play size={18} />
              Connect
            </button>
          ) : (
            <button
              onClick={disconnect}
              className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white font-semibold px-6 py-2 rounded-xl transition-colors"
            >
              <Square size={18} />
              Disconnect
            </button>
          )}
        </div>

        <div className="flex items-center gap-2 text-sm">
          <span
            className={`w-2 h-2 rounded-full ${
              connected ? "bg-green-500 animate-pulse" : "bg-gray-400"
            }`}
          />
          <span className="text-gray-500">
            {connected ? "Stream connected — processing live" : "Not connected"}
          </span>
        </div>

        {error && <p className="text-red-600 text-sm">{error}</p>}
      </div>

      {/* Live Feed */}
      {connected && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Video Feed */}
          <div className="lg:col-span-2 bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
            <div className="flex items-center gap-2 mb-3">
              <Radio size={18} className="text-red-600 animate-pulse" />
              <span className="text-sm font-semibold text-gray-900">LIVE FEED</span>
            </div>
            {frameData ? (
              <img
                src={`data:image/jpeg;base64,${frameData.frame}`}
                alt="Live stream"
                className="w-full rounded-xl border border-gray-200"
              />
            ) : (
              <div className="w-full aspect-video bg-gray-100 rounded-xl flex items-center justify-center text-gray-400">
                Waiting for first frame...
              </div>
            )}
          </div>

          {/* Live Stats Sidebar */}
          <div className="space-y-4">
            <StatCard
              label="Vehicles in Frame"
              value={frameData?.vehicle_count ?? 0}
              color="green"
            />
            <StatCard
              label="Total Counted"
              value={frameData?.total_counted ?? 0}
              color="blue"
            />
            <div className="grid grid-cols-2 gap-4">
              <StatCard
                label="Up"
                value={frameData?.counts_up ?? 0}
                color="gray"
              />
              <StatCard
                label="Down"
                value={frameData?.counts_down ?? 0}
                color="gray"
              />
            </div>

            {frameData && (
              <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
                <p className="text-gray-500 text-sm mb-2">Traffic Density</p>
                <DensityBadge
                  level={frameData.density_level}
                  score={frameData.density_score}
                />
              </div>
            )}

            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
              <p className="text-gray-500 text-sm">Current Frame</p>
              <p className="text-2xl font-bold text-gray-900">
                {frameData?.frame_number ?? 0}
              </p>
            </div>
          </div>
        </div>
      )}

     
    </div>
  );
}