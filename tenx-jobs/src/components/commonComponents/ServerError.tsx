import { Button, Result, Space } from 'antd'
export default function ServerError() {
  return (
    <Result
      status="500"
      title="500"
      subTitle="Sorry, something went wrong."
      extra={
        <Space>
          <Button type="primary" onClick={() => { window.location.reload() }}>Reload page</Button>
        </Space>
      }
    />
  )
}
