import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ApplicationStat } from "../../../types/statsTypes";

type JobApplicationStatsProps= {
  applications: ApplicationStat[];
}

export default function JobApplicationStats({
  applications}: JobApplicationStatsProps) {
  return (
    <div className="]">
    <ResponsiveContainer width="100%" height={500}>
      <BarChart
        data={applications}
        layout="vertical"
        {...{
          overflow: "visible",
        }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" />
        <YAxis
          dataKey="name"
          type="category"
          width={60}
          fontSize={10}
          interval={0}
        />
        <Tooltip />
        <Legend />
        <Bar dataKey="Interested" fill="#8884d8" />
        <Bar dataKey="Applied" fill="#82ca9d" />
        <Bar dataKey="Rejections" fill="#ef4444" />
        <Bar dataKey="Interviews" fill="#ff8042" />
        <Bar dataKey="Offers" fill="#0088fe" />
      </BarChart>
    </ResponsiveContainer>
  </div>
  )
}
