import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function RateLimitChart({ data, enabled }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data} margin={{ left: 8, right: 8, top: 8, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,116,139,0.35)" />
        <XAxis dataKey="time" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="actualRate" name="Actual rate" stroke="#22d3ee" strokeWidth={2.4} dot={false} />
        <Line type="monotone" dataKey="rateLimit" name="Rate limit" stroke="#f97316" strokeWidth={2.2} dot={false} />
        {!enabled ? <ReferenceLine y={0} stroke="#475569" label="Rate limiting disabled" /> : null}
      </LineChart>
    </ResponsiveContainer>
  );
}
