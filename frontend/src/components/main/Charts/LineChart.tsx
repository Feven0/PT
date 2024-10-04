import { Line, Area } from '@ant-design/plots';

const LineChart = ({relevancy}) => {
  // const relevancy = [
  //     {
  //       "index": 1,
  //       "level": "90",
  //       "reason": "The response was highly relevant, addressing both educational qualifications and practical experience in AI, which are crucial for the role."
  //     },
  //     {
  //       "index": 2,
  //       "level": "90",
  //       "reason": "Your background in machine learning and experience with AI projects directly relate to the responsibilities of the Senior AI Engineer position."
  //     },
  //     {
  //       "index": 3,
  //       "level": "80",
  //       "reason": "Most of your response was relevant, but it lacked specific examples of projects and challenges faced."
  //     },
  //     {
  //       "index": 4,
  //       "level": "30",
  //       "reason": "The response only mentioned the use of PyTorch without any specific examples or details about projects, making it largely irrelevant to the question."
  //     },
  //     {
  //       "index": 5,
  //       "level": "30",
  //       "reason": "The response only vaguely addresses teamwork without providing context or specifics about the experience."
  //     },
  //     {
  //       "index": 6,
  //       "level": "30",
  //       "reason": "The answer provided was very vague and did not adequately address the question about teamwork and collaboration."
  //     },
  //     {
  //       "index": 7,
  //       "level": "30",
  //       "reason": "The response only vaguely addresses teamwork without providing substantial context or detail."
  //     },
  //     {
  //       "index": 8,
  //       "level": "30",
  //       "reason": "The response only vaguely addresses teamwork without providing substantial context or detail."
  //     }
  //   ]
    const relevancyData = relevancy.map(item => ({
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





