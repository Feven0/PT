import { Button, Result } from 'antd';
import { useNavigate } from 'react-router-dom';

export default function PageNotfound() {
    const Navigate = useNavigate()
  return (
    <Result
      status="404"
      title="404"
      subTitle="Sorry, the page you visited does not exist."
      extra={<Button onClick={() => Navigate("/")} style={{background: "#FF4405", color:"#FFF"}}>Back Home</Button>}
    />
  )
}
