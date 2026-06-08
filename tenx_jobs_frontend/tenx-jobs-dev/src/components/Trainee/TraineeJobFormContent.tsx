import { QuestionCircleOutlined } from "@ant-design/icons";
import { Space, Tooltip, Typography } from "antd"
import '../../styles/trainee-job.css'

const { Text } = Typography
type componentProps = {
    name: string,
    description?: string | null,
    options?: {
        name: string,
        value: string,
    }[],
    label: string,
    component: string,
    value?: number | string | null | boolean,
    indexNo: number
}

export default function TraineeJobFormContent({ description, label, component, value }: componentProps) {
    const CommonComponent = () => {
        if (description) {
            return <div><Space>
                <span className="job__label">
                    {label}{" "}
                    <Tooltip placement="top" title={description}>
                        <QuestionCircleOutlined />
                    </Tooltip>
                </span>
            </Space>
            </div>
        }
        else {
            return <span className="job__label">
                {label}
            </span>
        }
    }
    const SingleElement = () => {
        if ('input' === component || 'number' === component) {
            return <>
                {<CommonComponent />}
                <div className="job__value">
                    {value ? value : null}
                </div>
            </>
        }
        else if ('text' === component) {
            return <>
                {<CommonComponent />}
                <p className="job__value">
                    {value ? value : null}
                </p>
            </>
        }
        else if ('checkboxGroup' === component || 'multiselect' === component || 'multiSelect' === component) {
            let listValue = []
            try {
                listValue = value ? (typeof (value) === 'string' ? JSON.parse(value) : []) : []
            } catch (e) {
                console.error(e)
            }
            return (
                <>
                    <CommonComponent />
                    <>
                        {
                            listValue.length > 0 &&
                            <Text>
                                {listValue.join(', ')}
                            </Text>
                        }
                    </>
                </>
            )
        }

        else if ('select' === component || 'Select' === component || component === 'radio') {
            return <>
                {<CommonComponent />}
                {
                    value ?
                        <div className="job__value">
                            {value}
                        </div> : null}
            </>
        }

        else {
            return null
        }
    }
    return (
        <SingleElement />
    )
}
