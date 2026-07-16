import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceDot,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import LiveChartFrame from "./LiveChartFrame";
import { chartAnimation, getLastPoint, getSampleDomain, makeTimeFormatter } from "./chartUtils";

export default function StreamBacklogChart({ data }) {
  const last = getLastPoint(data);
  const timeFormatter = makeTimeFormatter(data);

  return (
    <LiveChartFrame points={data?.length ?? 0} tone="amber">
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data} margin={{ left: 8, right: 8, top: 8, bottom: 8 }}>
          <defs>
            <linearGradient id="streamBacklogFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f97316" stopOpacity={0.34} />
              <stop offset="95%" stopColor="#f97316" stopOpacity={0.02} />
            </linearGradient>
          </defs>
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
          <Area type="monotone" dataKey="streamBacklog" name="Stream backlog" stroke="#f97316" fill="url(#streamBacklogFill)" strokeWidth={2.4} dot={false} connectNulls {...chartAnimation} />
          {last ? <ReferenceDot x={last.sampleIndex} y={last.streamBacklog} r={4} fill="#f97316" stroke="#0f172a" /> : null}
        </AreaChart>
      </ResponsiveContainer>
    </LiveChartFrame>
  );
}
