import { Card, Typography } from "antd"

const { Text, Title } = Typography;

const PercentageCard = () => {
  return (
    <>
        <Card className='card_box' title='Performance'>
            <Card type="inner">
                <Title>Good Job!</Title>
                <Text className='interview_percent'>70%</Text>
            </Card>
        </Card>
    </>
  )
}

export default PercentageCard