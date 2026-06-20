/**
 * StatCard Component
 * Displays a single metric with label and value.
 */

interface StatCardProps {
  label: string;
  value: string | number;
  sub?: string;
  color?: "green" | "yellow" | "red" | "blue" | "gray";
}

const colorMap = {
  green:  "border-green-300 bg-green-50",
  yellow: "border-yellow-300 bg-yellow-50",
  red:    "border-red-300 bg-red-50",
  blue:   "border-blue-300 bg-blue-50",
  gray:   "border-gray-300 bg-gray-50",
};

const textMap = {
  green:  "text-green-700",
  yellow: "text-yellow-700",
  red:    "text-red-700",
  blue:   "text-blue-700",
  gray:   "text-gray-700",
};

export default function StatCard({
  label,
  value,
  sub,
  color = "blue",
}: StatCardProps) {
  return (
    <div className={`rounded-xl border p-4 ${colorMap[color]}`}>
      <p className="text-gray-500 text-xs uppercase tracking-wider mb-1 font-medium">
        {label}
      </p>
      <p className={`text-2xl font-bold ${textMap[color]}`}>{value}</p>
      {sub && <p className="text-gray-500 text-xs mt-1">{sub}</p>}
    </div>
  );
}