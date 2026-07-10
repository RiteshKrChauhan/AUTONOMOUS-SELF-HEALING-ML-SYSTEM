import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function DriftScoreLineChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <AreaChart data={data} margin={{ left: 8, right: 8, top: 8, bottom: 8 }}>
        <defs>
          <linearGradient id="driftFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#fb7185" stopOpacity={0.5} />
            <stop offset="100%" stopColor="#fb7185" stopOpacity={0.05} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,116,139,0.35)" />
        <XAxis dataKey="time" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <YAxis domain={[0, 1]} tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <Tooltip />
        <ReferenceLine y={0.6} stroke="#f43f5e" strokeDasharray="5 5" />
        <Area type="monotone" dataKey="driftScore" stroke="#fb7185" fill="url(#driftFill)" strokeWidth={2.4} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
