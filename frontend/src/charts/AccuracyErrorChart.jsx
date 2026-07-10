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

export default function AccuracyErrorChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data} margin={{ left: 8, right: 8, top: 8, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,116,139,0.35)" />
        <XAxis dataKey="time" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <YAxis domain={[0, 1]} tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="accuracy" name="Accuracy" stroke="#34d399" strokeWidth={2.3} dot={false} />
        <Line type="monotone" dataKey="error" name="Error" stroke="#f87171" strokeWidth={2.3} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
