import { Sankey } from '@ant-design/plots';
interface Time {
  time: any
}

const SankeyTime : React.FC<Time> = ({time}) => {
  const transformDataToLinks = (data: any) => {
    return data?.flatMap((item: any, index: any) => [
        { source: `Interview ${index + 1}`, target: 'fail', value: item.time_management.fail },
        { source: `Interview ${index + 1}`, target: 'pass', value: item.time_management.pass }
    ]);
  };

  const transformedLinks = transformDataToLinks(time);

  const config = {
    data: {
      value: {
        links: transformedLinks,
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

