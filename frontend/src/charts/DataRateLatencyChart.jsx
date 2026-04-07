import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function DataRateLatencyChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data} margin={{ left: 8, right: 8, top: 8, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,116,139,0.35)" />
        <XAxis dataKey="time" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <YAxis yAxisId="left" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <YAxis yAxisId="right" orientation="right" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <Tooltip />
        <Legend />
        <Line yAxisId="left" type="monotone" dataKey="dataRate" name="Data Rate (eps)" stroke="#22d3ee" strokeWidth={2.6} dot={false} />
        <Line yAxisId="right" type="monotone" dataKey="latency" name="Latency (ms)" stroke="#f59e0b" strokeWidth={2.4} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
