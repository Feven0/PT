import { Card, Typography } from "antd"

const { Text, Title } = Typography;

const PercentageCard = () => {
  return (
    <>
        <Card title='Performance' style={{height: '16rem'}}>
            <div>
                <h1>Good Job!</h1>
                <Text className='interview_percent'>70%</Text>
            </div>
        </Card>
    </>
  )
}

export default PercentageCard