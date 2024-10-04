import React from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    LineChart,
    Line,
} from 'recharts';
import { Card } from 'antd';

const ChartComponent = ({ data, type }) => {
    return (
        <Card style={{ width: '80%' }}>
            <ResponsiveContainer width="100%" height={200}>
                {type === 'confidence' ? (
                    <LineChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="value" stroke="#82ca9d" />
                    </LineChart>
                ) : (
                    <BarChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="index" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        {type === 'timeManagement' && (
                            <>
                                <Bar dataKey="pass" fill="#4caf50" />
                                <Bar dataKey="fail" fill="#f44336" />
                            </>
                        )}
                        {type === 'relevancy' && (
                            <Bar dataKey="overall" fill="#2196f3" />
                        )}
                        {type !== 'timeManagement' && type !== 'relevancy' && (
                            <>
                                <Bar dataKey="Excellent" fill="#f76f60" />
                                <Bar dataKey="Good" fill="#e29288" />
                                <Bar dataKey="Poor" fill="#f3c9c4" />
                            </>
                        )}
                    </BarChart>
                )}
            </ResponsiveContainer>
        </Card>
    );
};

export default ChartComponent;