import {
  PolarAngleAxis,
  RadialBar,
  RadialBarChart,
  ResponsiveContainer,
} from "recharts";

export default function RateGaugeChart({ value, max = 4500 }) {
  const safeValue = Math.max(0, Math.min(value, max));
  const percent = Number(((safeValue / max) * 100).toFixed(1));

  return (
    <div className="rate-gauge">
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart
          data={[{ name: "rate", value: safeValue, fill: "#22d3ee" }]}
          startAngle={210}
          endAngle={-30}
          innerRadius="68%"
          outerRadius="92%"
          barSize={18}
        >
          <PolarAngleAxis type="number" domain={[0, max]} tick={false} />
          <RadialBar dataKey="value" cornerRadius={8} background />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="rate-gauge-overlay">
        <p className="rate-gauge-value">{safeValue}</p>
        <p className="rate-gauge-label">events/sec</p>
        <p className="rate-gauge-meta">{percent}% of max capacity</p>
      </div>
    </div>
  );
}
