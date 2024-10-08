import { Line } from '@ant-design/plots';

interface Relevance {
  relevancy: any
}

const LineChartOverall : React.FC<Relevance> = ({relevancy}) => {

    const relevancyData = relevancy.map((item:any) => ({
      interview: item.interview, 
      performance: parseInt(item.performance, 10)
    }));

    const config = {
      data: relevancyData, 
      xField: 'interview', 
      yField: 'performance',
      point: {
          shapeField: 'circle',
          sizeField: 1,
      },
      interaction: {
          tooltip: {
              marker: false,
          },
      },
      style: {
          lineWidth: 1, 
      }
    };
  
  
  return(
    <div style={{ marginTop: '3rem', width: '25rem', height: '20rem' }}>
      <Line {...config} />
    </div>
  )
};

export default LineChartOverall





