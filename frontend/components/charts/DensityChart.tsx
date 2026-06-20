/**
 * DensityChart Component
 * Line chart showing vehicle count over time.
 */

"use client";

import {
  LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { FrameRecord } from "@/lib/api";

interface Props {
  data: FrameRecord[];
}

export default function DensityChart({ data }: Props) {
  if (!data.length) return (
    <div className="flex items-center justify-center h-48 text-gray-500">
      No data available
    </div>
  );

  // Sample every 5th frame for performance
  const sampled = data.filter((_, i) => i % 5 === 0);

  return (
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={sampled}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis
          dataKey="frame_number"
          stroke="#9CA3AF"
          tick={{ fontSize: 11 }}
          label={{ value: "Frame", position: "insideBottom", offset: -2, fill: "#9CA3AF" }}
        />
        <YAxis stroke="#9CA3AF" tick={{ fontSize: 11 }} />
        <Tooltip
          contentStyle={{ backgroundColor: "#1F2937", border: "1px solid #374151" }}
          labelStyle={{ color: "#F9FAFB" }}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="vehicle_count"
          stroke="#10B981"
          dot={false}
          strokeWidth={2}
          name="Vehicles"
        />
        <Line
          type="monotone"
          dataKey="density_score"
          stroke="#3B82F6"
          dot={false}
          strokeWidth={2}
          name="Density Score"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}