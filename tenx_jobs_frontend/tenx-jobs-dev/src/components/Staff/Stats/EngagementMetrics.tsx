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
import { EngagementStat } from "../../../types/statsTypes";

interface EngagementsProps {
  engagements: EngagementStat[];
}

export default function EngagementMetrics({ engagements }: EngagementsProps) {
  return (
    <div>
         <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={engagements}
            {...{
              overflow: "visible",
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="name"
              interval={0}
              angle={-45}
              fontSize={12}
              tickMargin={5}
            />
            <YAxis
              domain={[0, 100]}
              label={{
                value: "Percentage (%)",
                angle: -90,
                position: "insideLeft",
              }}
            />
            <Tooltip />
            <Legend
              wrapperStyle={{
                position: "relative",
                marginTop: "1px",
              }}
            />
            <Bar dataKey="Challenges Completed(%)" fill="#8884d8" />
            <Bar dataKey="Standup Attendance(%)" fill="#82ca9d" />
          </BarChart>
        </ResponsiveContainer>
    </div>
  )
}
