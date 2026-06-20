/**
 * VehicleTypeChart Component
 * Bar chart showing vehicle type distribution.
 */

"use client";

import {
  BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

interface Props {
  data: Record<string, number>;
}

export default function VehicleTypeChart({ data }: Props) {
  const chartData = Object.entries(data).map(([type, count]) => ({
    type, count,
  }));

  if (!chartData.length) return (
    <div className="flex items-center justify-center h-48 text-gray-500">
      No data available
    </div>
  );

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis dataKey="type" stroke="#9CA3AF" tick={{ fontSize: 12 }} />
        <YAxis stroke="#9CA3AF" tick={{ fontSize: 12 }} />
        <Tooltip
          contentStyle={{ backgroundColor: "#1F2937", border: "1px solid #374151" }}
          labelStyle={{ color: "#F9FAFB" }}
        />
        <Bar dataKey="count" fill="#10B981" radius={[4, 4, 0, 0]} name="Count" />
      </BarChart>
    </ResponsiveContainer>
  );
}