/**
 * DensityBadge Component
 * Colored badge showing traffic density level.
 */

interface DensityBadgeProps {
  level: string;
  score?: number;
}

const levelColors: Record<string, string> = {
  LOW:       "bg-green-100 text-green-700 border-green-400",
  MODERATE:  "bg-yellow-100 text-yellow-700 border-yellow-400",
  HIGH:      "bg-orange-100 text-orange-700 border-orange-400",
  CONGESTED: "bg-red-100 text-red-700 border-red-400",
};

export default function DensityBadge({ level, score }: DensityBadgeProps) {
  const classes = levelColors[level] || levelColors.LOW;
  return (
    <span className={`inline-flex items-center gap-2 border rounded-full px-4 py-1 text-sm font-bold ${classes}`}>
      <span className="w-2 h-2 rounded-full bg-current animate-pulse" />
      {level}
      {score !== undefined && (
        <span className="text-xs opacity-70">({(score * 100).toFixed(0)}%)</span>
      )}
    </span>
  );
}