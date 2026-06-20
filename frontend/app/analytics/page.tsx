/**
 * Analytics Page
 * Shows charts and metrics from a selected session.
 */

"use client";

import { useState, useEffect } from "react";
import {
  getAllSessions, getFrameRecords, getVehicles,
  Session, FrameRecord, Vehicle,
} from "@/lib/api";
import StatCard from "@/components/StatCard";
import DensityChart from "@/components/charts/DensityChart";
import VehicleTypeChart from "@/components/charts/VehicleTypeChart";

export default function AnalyticsPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [session, setSession] = useState<Session | null>(null);
  const [frames, setFrames] = useState<FrameRecord[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getAllSessions().then((data) => {
      setSessions(data);
      if (data.length > 0) setSelected(data[0].session_id);
    });
  }, []);

  useEffect(() => {
    if (!selected) return;
    setLoading(true);

    const sess = sessions.find((s) => s.session_id === selected) || null;
    setSession(sess);

    Promise.all([
      getFrameRecords(selected),
      getVehicles(selected),
    ]).then(([f, v]) => {
      setFrames(f);
      setVehicles(v);
      setLoading(false);
    });
  }, [selected]);

  const typeDistribution = vehicles.reduce((acc, v) => {
    acc[v.label] = (acc[v.label] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Traffic Analytics</h2>
        <p className="text-gray-500 mt-1">
          Deep dive into session data and traffic patterns.
        </p>
      </div>

      {/* Session Selector */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
        <label className="text-gray-500 text-sm block mb-2 font-medium">Select Session</label>
        <select
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
          className="bg-white border border-gray-300 text-gray-900 rounded-xl px-4 py-2 w-full max-w-md focus:outline-none focus:ring-2 focus:ring-gov-green"
        >
          {sessions.map((s) => (
            <option key={s.session_id} value={s.session_id}>
              {s.session_id} — {s.video_source.split("/").pop()}
            </option>
          ))}
        </select>
      </div>

      {loading && (
        <div className="text-center text-gray-500 py-12">Loading analytics...</div>
      )}

      {session && !loading && (
        <>
          {/* Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="Total Frames" value={session.total_frames} color="gray" />
            <StatCard label="Vehicles Counted" value={session.total_counted} color="green" />
            <StatCard label="Avg Density" value={`${(session.avg_density * 100).toFixed(1)}%`} color="blue" />
            <StatCard label="Violations" value={session.total_violations} color="red" />
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
              <h3 className="text-gray-900 font-semibold mb-4">Vehicle Count Over Time</h3>
              <DensityChart data={frames} />
            </div>
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
              <h3 className="text-gray-900 font-semibold mb-4">Vehicle Type Distribution</h3>
              <VehicleTypeChart data={typeDistribution} />
            </div>
          </div>

          {/* Vehicle Table */}
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-gray-900 font-semibold mb-4">Vehicle Records</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-gray-500 border-b border-gray-200">
                    <th className="text-left py-2 px-3">ID</th>
                    <th className="text-left py-2 px-3">Type</th>
                    <th className="text-left py-2 px-3">Avg Speed</th>
                    <th className="text-left py-2 px-3">Max Speed</th>
                    <th className="text-left py-2 px-3">Zone</th>
                    <th className="text-left py-2 px-3">Violation</th>
                  </tr>
                </thead>
                <tbody>
                  {vehicles.map((v) => (
                    <tr key={v.track_id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-2 px-3 text-blue-600 font-mono">#{v.track_id}</td>
                      <td className="py-2 px-3 text-gray-900 capitalize">{v.label}</td>
                      <td className="py-2 px-3 text-gray-600">
                        {v.avg_speed_kmh ? `${v.avg_speed_kmh} km/h` : "N/A"}
                      </td>
                      <td className="py-2 px-3 text-gray-600">
                        {v.max_speed_kmh ? `${v.max_speed_kmh} km/h` : "N/A"}
                      </td>
                      <td className="py-2 px-3 text-gray-600">{v.zone}</td>
                      <td className="py-2 px-3">
                        {v.violation ? (
                          <span className="text-red-600 text-xs font-medium">{v.violation}</span>
                        ) : (
                          <span className="text-green-600 text-xs">None</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}