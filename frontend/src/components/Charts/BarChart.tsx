import { VictoryBar, VictoryChart, VictoryAxis, VictoryTooltip } from 'victory';
import { useState } from 'react';
interface Data {
    metricData: any
}

const BarChart: React.FC<Data> = ({ metricData }) => {
    const [tooltipData, setTooltipData] = useState(null);

    const data = metricData?.map((item: any) => ({
        x: item.time,
        y: item.value,
        label: item.level,
    }));

    return (
        <div style={{ width: '28rem', height: '20rem', position: 'relative' }}>
            <VictoryChart domainPadding={100}>
                <VictoryAxis
                    style={{
                        tickLabels: {
                            angle: 90, 
                            textAnchor: 'start',
                            verticalAnchor: 'middle', 
                            cursor: 'pointer', 
                        }
                    }}
                    events={[
                        {
                            target: 'tickLabels',
                            eventHandlers: {
                                onMouseOver: (evt, { index }) => {
                                    console.log(evt)
                                    if (data && index !== undefined) {
                                        setTooltipData(data[index].x);
                                    }
                                },
                                onMouseOut: () => {
                                    setTooltipData(null); 
                                }
                            }
                        }
                    ]}
                />
                <VictoryBar
                    data={data}
                    barWidth={30}
                    labels={({ datum }) => `Value: ${datum.y}\nLabel: ${datum.label}`}
                    labelComponent={
                        <VictoryTooltip
                            flyoutStyle={{ fill: "white", stroke: "#ccc" }}
                            style={{ fontSize: 12 }}
                            pointerLength={10}
                        />
                    }
                    style={{
                        data: {
                            fill: ({ datum }) => 
                                datum.label === 'poor' ? '#f3c9c4' :
                                datum.label === 'good' ? '#e29288' :
                                datum.label === 'excellent' ? '#f76f60' : 
                                '#000'
                        }
                    }}
                />
            </VictoryChart>
            {tooltipData && (
                <div style={{
                    position: 'absolute',
                    background: 'rgba(255, 255, 255, 0.9)',
                    padding: '5px',
                    border: '1px solid #ccc',
                    borderRadius: '5px',
                    pointerEvents: 'none',
                    left: '50%',  
                    top: '10%',   
                    transform: 'translate(-50%, -50%)'
                }}>
                    {`Time: ${tooltipData}`}
                </div>
            )}
        </div>
    );
};

export default BarChart;