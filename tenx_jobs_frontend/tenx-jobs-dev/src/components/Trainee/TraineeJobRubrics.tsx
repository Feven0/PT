import {  Divider, Form, Typography } from 'antd'
import TraineeJobCriteria from "./TraineeJobCriteria"
import TraineeJobFormContent from "./TraineeJobFormContent"
import { CriteriaInterface, FormCriteriaInterface } from "../../types/Jobs"

//Style
import '../../styles/slidingCard.css'

interface RubricProps {
    rubric?: CriteriaInterface[] | null
    AdHoc: FormCriteriaInterface[] | null,
}

export default function TraineeJobRubric({ AdHoc = null,  rubric = null }: RubricProps) {
    const rubrics: any[] = [];
    const [form] = Form.useForm();

    if (rubric) {
        for (const criteria in rubric) {
            const points = rubric[criteria].points.slice().sort((a, b) => b.point - a.point)
            rubrics.push({ ...rubric[criteria], points: points });
        }

    }
    const { Text } = Typography;
    return (
        <div>
            <div>
                <Text className="trainee-job-rubric-title">
                    Rubric
                </Text>
            </div>
            {
                rubric ?
                    <>
                        <div>
                            {rubrics.map((item: CriteriaInterface, index) => (
                                <TraineeJobCriteria title={item.title} items={item.total} points={item.points} value={item.value} key={index} />
                            ))}
                        </div>
                    </> :
                    null
            }
            {
                AdHoc && <>
                    <Divider />
                    <Text className="trainee-job-rubric-title">
                        Form
                    </Text>
                    {AdHoc ? <>
                        <Form
                            style={{ marginTop: "15px" }}
                            form={form}
                            name="basic"
                            labelCol={{ span: 23 }}
                            wrapperCol={{ span: 23 }}
                            initialValues={{ remember: true }}
                            autoComplete="off"
                            size={"small"}

                        >
                            {
                                <>
                                    {
                                        AdHoc?.map((item: FormCriteriaInterface, index: number) => {
                                            return <TraineeJobFormContent indexNo={index}  {...item} />
                                        })
                                    }
                                </>
                            }
                        </Form>

                    </> : null}
                </>
            }
        </div>
    );
}
