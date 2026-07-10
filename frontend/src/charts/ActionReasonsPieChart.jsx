import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const COLORS = ["#22d3ee", "#f59e0b", "#fb7185"];

export default function ActionReasonsPieChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="reason"
          cx="50%"
          cy="50%"
          innerRadius={55}
          outerRadius={95}
          label
        >
          {data.map((entry, idx) => (
            <Cell key={entry.reason} fill={COLORS[idx % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
}
