import React from 'react';
interface Data {
    value: any,
    label: any,   
}

interface DataTime {
    passRate: any, 
    failRate: any
}

interface DataProgress {
    data: any
}

const ProgressBar: React.FC<Data> = ({ value, label }) => {
    const getColor = (val: any) => {
        if (val < 1.5) return '#e66262';
        if (val < 2.5) return '#f3b747'; 
        return '#44e444'; 
    };

    const getPercentage = (val: any) => (val / 3) * 100;

    return (
        <div style={{ marginBottom: '15px' }}>
            <p>{label}</p>
            <div style={{
                width: '100%',
                backgroundColor: '#ddd',
                borderRadius: '20px',
                overflow: 'hidden',
                height: '20px'
            }}>
                <div style={{
                    width: `${getPercentage(value)}%`,
                    backgroundColor: getColor(value),
                    height: '100%',
                    transition: 'width 0.5s ease'
                }}>
                </div>
            </div>
            <p>Rating: {value} / 3</p>
        </div>
    );
};

const DualProgressBar: React.FC<DataTime> = ({ passRate, failRate }) => {
    return (
        <div>
            <p>Time Management</p>
            <div style={{ display: 'flex', width: '100%', height: '20px', marginBottom: '15px', borderRadius: '20px', overflow: 'hidden' }}>
                <div style={{ width: `${passRate}%`, backgroundColor: '#44e444' }}></div>
                <div style={{ width: `${failRate}%`, backgroundColor: '#e66262' }}></div>
            </div>
            <p>Pass Rate: {passRate}% | Fail Rate: {failRate}%</p>
        </div>
    );
};

const ProgressBarChart: React.FC<DataProgress> = ({data}) => {
    return (
        <div style={{width: '20rem'}}>
            <h2>Overall Performance</h2>

            <ProgressBar value={data?.avg_confidence} label="Confidence" />
            <ProgressBar value={data?.avg_clarity} label="Clarity" />
            <ProgressBar value={data?.avg_engagment} label="Engagement" />

            <DualProgressBar
                passRate={data?.avg_time_management?.average_pass_rate}
                failRate={data?.avg_time_management?.average_fail_rate}
            />
        </div>
    );
};

export default ProgressBarChart;
