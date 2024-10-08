import { Sankey } from '@ant-design/plots';

interface Communication {
  communication: any
}
const SankeyChart : React.FC<Communication> = ({communication}) => {
  const config = {
    data: {
      value: {
        links: communication,
      },
    },
    scale: {
      color: {
        range: [
          '#76b7b2',
          '#59a14f',
          '#edc949',
          '#f76f60',
          '#e29288',
          '#f3c9c4'
        ],
      },
    },

    interaction: {
        tooltip: {
      
        },
    },
  };
  return(
    <div style={{ width: '28rem', height:'20rem' }}>
        <Sankey {...config} />
    </div>
  ) 
};

export default SankeyChart

