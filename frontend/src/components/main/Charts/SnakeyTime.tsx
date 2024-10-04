import { Sankey } from '@ant-design/plots';

const SankeyTime = ({time}) => {
// Time Managment
  const config = {
    data: {
      value: {
        links: time,
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
            // render: (e, {items }) => {

            //     const sourceItem = items.find(item => item.name === 'source');
            //     const targetItem = items.find(item => item.name === 'target');

            //     const source = sourceItem ? sourceItem.value : 'Unknown Source';
            //     const target = targetItem ? targetItem.value : 'Unknown Target';

            //     const link = config.data.value.links.find(
            //         (link) => link.source === source && link.target === target
            //     );
            //     const value = link ? link.value : 'N/A';
            //     console.log("much", value, source, target)
            //     return (
            //         <div>
            //             <strong>{source} → {target}</strong>
            //             <div>Value: {value}</div>
            //         </div>
            //     );
            // },
        },
    },
  };
  return(
    <div style={{ width: '28rem', height:'20rem' }}>
        <Sankey {...config} />
    </div>
  ) 
};

export default SankeyTime

