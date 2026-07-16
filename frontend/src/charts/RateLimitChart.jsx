import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceDot,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import LiveChartFrame from "./LiveChartFrame";
import { chartAnimation, getLastPoint, getSampleDomain, makeTimeFormatter } from "./chartUtils";

export default function RateLimitChart({ data, enabled }) {
  const last = getLastPoint(data);
  const timeFormatter = makeTimeFormatter(data);

  return (
    <LiveChartFrame points={data?.length ?? 0}>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data} margin={{ left: 8, right: 8, top: 8, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,116,139,0.35)" />
          <XAxis
            dataKey="sampleIndex"
            type="number"
            domain={getSampleDomain(data)}
            tickFormatter={timeFormatter}
            tick={{ fill: "#94a3b8", fontSize: 11 }}
          />
          <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
          <Tooltip labelFormatter={(value) => `Sample ${value} - ${timeFormatter(value)}`} />
          <Legend />
          <Line type="monotone" dataKey="incomingRate" name="Incoming rate" stroke="#38bdf8" strokeWidth={2.2} dot={false} connectNulls {...chartAnimation} />
          <Line type="monotone" dataKey="actualRate" name="Processed rate" stroke="#22c55e" strokeWidth={2.4} dot={false} connectNulls {...chartAnimation} />
          <Line type="monotone" dataKey="appliedRateLimit" name="Applied limit" stroke="#f97316" strokeWidth={2.2} dot={false} connectNulls {...chartAnimation} />
          <Line type="monotone" dataKey="rateLimit" name="Operator limit" stroke="#a78bfa" strokeWidth={1.8} strokeDasharray="5 5" dot={false} connectNulls {...chartAnimation} />
          {!enabled ? <ReferenceLine y={0} stroke="#475569" label="Rate limiting disabled" /> : null}
          {last ? <ReferenceDot x={last.sampleIndex} y={last.actualRate} r={4} fill="#22c55e" stroke="#0f172a" /> : null}
        </LineChart>
      </ResponsiveContainer>
    </LiveChartFrame>
  );
}
