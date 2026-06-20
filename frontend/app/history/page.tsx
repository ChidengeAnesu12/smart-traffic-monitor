/**
 * Session History Page
 * Shows all past processing sessions.
 */

"use client";

import { useState, useEffect } from "react";
import { getAllSessions, Session } from "@/lib/api";
import StatCard from "@/components/StatCard";

export default function HistoryPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAllSessions()
      .then(setSessions)
      .finally(() => setLoading(false));
  }, []);

  const completed = sessions.filter((s) => s.status === "completed").length;

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Session History</h2>
        <p className="text-gray-500 mt-1">All past traffic monitoring sessions.</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Total Sessions" value={sessions.length} color="blue" />
        <StatCard label="Completed" value={completed} color="green" />
        <StatCard
          label="Total Vehicles"
          value={sessions.reduce((a, s) => a + (s.total_counted || 0), 0)}
          color="yellow"
        />
        <StatCard
          label="Total Violations"
          value={sessions.reduce((a, s) => a + (s.total_violations || 0), 0)}
          color="red"
        />
      </div>

      {loading && (
        <div className="text-center text-gray-500 py-12">Loading sessions...</div>
      )}

      {/* Sessions Table */}
      {!loading && (
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
          <h3 className="text-gray-900 font-semibold mb-4">All Sessions</h3>
          {sessions.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              No sessions found. Run the pipeline first.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-gray-500 border-b border-gray-200">
                    <th className="text-left py-2 px-3">Session ID</th>
                    <th className="text-left py-2 px-3">Video</th>
                    <th className="text-left py-2 px-3">Status</th>
                    <th className="text-left py-2 px-3">Frames</th>
                    <th className="text-left py-2 px-3">Counted</th>
                    <th className="text-left py-2 px-3">Avg Density</th>
                    <th className="text-left py-2 px-3">Started</th>
                  </tr>
                </thead>
                <tbody>
                  {sessions.map((s) => (
                    <tr key={s.session_id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-2 px-3 text-blue-600 font-mono text-xs">{s.session_id}</td>
                      <td className="py-2 px-3 text-gray-700 max-w-xs truncate">
                        {s.video_source.split("/").pop()}
                      </td>
                      <td className="py-2 px-3">
                        <span className={`text-xs font-bold px-2 py-1 rounded-full ${
                          s.status === "completed"
                            ? "bg-green-100 text-green-700"
                            : "bg-yellow-100 text-yellow-700"
                        }`}>
                          {s.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-gray-700">{s.total_frames}</td>
                      <td className="py-2 px-3 text-gray-700">{s.total_counted}</td>
                      <td className="py-2 px-3 text-gray-700">
                        {s.avg_density ? `${(s.avg_density * 100).toFixed(1)}%` : "N/A"}
                      </td>
                      <td className="py-2 px-3 text-gray-500 text-xs">
                        {new Date(s.started_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}