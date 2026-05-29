import {  Space, Typography } from "antd";

//Style
import '../../styles/point.css'

interface InputProps {
    title: string,
    description?: string | null,
    items: number,
    points: {
        title: string,
        description: string,
        point: number
    }[],
    value?: number
}
const { Text } = Typography;

export default function TraineeJobCriteria({ title, items, points, value = -1 }: InputProps) {

    return (
        <div>
            <div className="flex-between m-4">
                <Space size="small">
                    <Text style={{ width: "100px" }} ellipsis={{ tooltip: true }}>{title}</Text>
                </Space>
                <Text className="trainee-job-criteria">
                    {
                        value === 0 ?
                            <span style={{ color: "#BFBFBF"}}>
                                {value}
                            </span> :
                            (
                                value < 0 ?
                                    null :
                                    <span>
                                        {value}
                                    </span>
                            )
                    }
                    <span>&nbsp;&nbsp; / {items}</span>
                </Text>
            </div>
            <div>
                <div className="flex-between m-4">
                    {
                        points.map((item, index) => (
                            <div
                                style={{
                                    backgroundColor: item.point === value ? "#595959" : "#F0F0F0",
                                    height: 20,
                                    width: "100%",
                                    margin: '2px',
                                }}
                                className="tooltip pointer"
                                key={index}>
                                <span className="tooltiptext">{item.point} pts •</span>
                            </div>
                        ))
                    }
                </div>
            </div>
        </div>
    );
}
