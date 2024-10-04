import { VictoryBar, VictoryChart, VictoryAxis } from 'victory';

const BarChartComponent = ({ confidenceData }) => {
    const data = confidenceData.map((item, index) => ({
        x: `Interview ${index + 1}`,
        y: item.poor ? 1 : item.good ? 2 : item.excellent ? 3 : 0,
        label: item.poor ? 'Poor' : item.good ? 'Good' : item.excellent ? 'Excellent' : 'Unknown',
    }));

    return (
        <div style={{  width: '30rem', height:'20rem'}}>
            <VictoryChart
                domainPadding={100} 
            >
                <VictoryAxis />
                {/* <VictoryAxis dependentAxis /> */}
                <VictoryBar
                    data={data}
                    barWidth={30} 
                    style={{
                        data: {
                            fill: ({ datum }) => 
                                datum.label === 'Poor' ? '#f3c9c4' :
                                datum.label === 'Good' ? '#e29288' :
                                datum.label === 'Excellent' ? '#f76f60' : 
                                '#000'
                        }
                    }}
                />
            </VictoryChart>
        </div>
    );
};

export default BarChartComponent;