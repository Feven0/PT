import { Spin } from 'antd'

export default function LoadingState() {
  return (
    <div style={{
      textAlign: 'center',
      paddingTop: '200px',
      left: '50%',
      top: '50%'

    }}>
      <Spin size="large" />
    </div>
  )
}
