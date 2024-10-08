import { Line } from '@ant-design/plots';

interface Relevance {
  relevancy: any
}
const LineChart: React.FC<Relevance> = ({relevancy}) => {
    const relevancyData = relevancy.map((item:any) => ({
      question: item.index, 
      answer_relevance: parseInt(item.level, 10)
    }));

    const config = {
      data: relevancyData, 
      xField: 'question', 
      yField: 'answer_relevance',
      point: {
          shapeField: 'square',
          sizeField: 4,
      },
      interaction: {
          tooltip: {
              marker: false,
          },
      },
      style: {
          lineWidth: 8, 
      }
    };
  
  
  return(
    <div style={{ width: '44rem', height: '15rem' }}>
      <Line {...config} />
    </div>
  )
};

export default LineChart





