import React from 'react';
import { Area } from '@ant-design/plots';

interface Data {
    chartData: any
}

const LineChartAdmin: React.FC<Data> = ({ chartData }) => {
    const config = {
        data: chartData, 
        xField: 'day', 
        yField: 'sessionCount', 
        // point: {
        //     shapeField: 'circle', 
        //     sizeField: 1,
        // },
        style: {
            fill: 'linear-gradient(-90deg, white 0%, #e49226 100%)',
          },
    };

    return (
        <div style={{ width: '24rem', height: '10rem' }}>
            <Area {...config} />
        </div>
    );
};

export default LineChartAdmin;
