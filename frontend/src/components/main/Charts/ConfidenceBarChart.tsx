import React from 'react';
import { Bar } from '@ant-design/charts';

const ConfidenceBarChart = () => {
    const rawData = [
        { "level": "poor" },
        { "level": "poor" },
        { "level": "good" }
    ];

    // Aggregate data
    const aggregatedData = rawData.reduce((acc, curr) => {
        acc[curr.level] = (acc[curr.level] || 0) + 1;
        return acc;
    }, {});

    const chartData = Object.keys(aggregatedData).map(key => ({
        level: key,
        count: aggregatedData[key]
    }));

    // Chart configuration
    const config = {
        data: chartData,
        xField: 'level',
        yField: 'count',
        label: {
            // Optional: display value labels on bars
            position: 'middle', // 'top', 'bottom', 'middle'
            style: {
                fill: '#fff', // Text color
                opacity: 0.6, // Text opacity
            },
        },
        meta: {
            level: { alias: 'Confidence Level' },
            count: { alias: 'Count' },
        },
        interactions: [{ type: 'element-active' }],
    };

    return <Bar {...config} />;
};

export default ConfidenceBarChart;