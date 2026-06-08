import { useMutation, useQuery } from '@apollo/client';
import { Col, Form, Row, Button, Input, Avatar} from 'antd';
import  { useState } from 'react'

//Components
import ServerError from "../commonComponents/ServerError";
import Comments from "./Comments";

//Graphql queries and mutations
import { CREATE_EXCHANGE, CREATE_MESSAGE, CREATE_NOTIFICATION } from "../../graphql/mutations/CreateJobs";
import { EXCHANGE } from "../../graphql/queries/CreateJobs";

//Types
import { ExchangeEntityResponseCollection, MessageEntity } from "../../types/generated";

//Redux and Custom hooks
import { useAppSelector } from "../../redux/hooks/hooks";

//Utils
import { colors } from "../../utils/colors";
import { extractInitials } from "../../utils/extractInitionalts";

//Styles
import '../../styles/slidingCard.css'
import StaffDataLoader from "../commonComponents/StaffDataLoader";

const { TextArea } = Input;

type propsType = {
  slug: string,
  jobTitle: string,
  job_trainee_id: string | number
}

type exchangeData = {
  exchanges: ExchangeEntityResponseCollection
}

export default function JobDetailFeedbackTrainee({ slug, jobTitle, job_trainee_id }: propsType) {
  const traineeJobID = job_trainee_id
  const {username} = useAppSelector((state) => state.user)
  const topic = slug
  const {allUserId, batch, trainee_id:traineeID} = useAppSelector((state) => state.leapProfileId)
  const [submitting, setSubmitting] = useState(false);
  const [value, setValue] = useState("");

  const [createExchange] = useMutation(CREATE_EXCHANGE);
  const [createMessage] = useMutation(CREATE_MESSAGE);
  const [createNotification] = useMutation(CREATE_NOTIFICATION);

  const { error, loading, data: data, refetch } = useQuery<exchangeData>(EXCHANGE,
    {
      variables: { topic: topic },
      pollInterval: 10000
    })

  if (loading) return <StaffDataLoader />
  if (error) return <ServerError />

  const handleSubmit = () => {
    if (!value.trim()) {
      return;
    }
    setSubmitting(false);
    setValue("");
    refetch()
    if (data?.exchanges.data.length === 0) {
      createExchange({
        variables: { topic: topic, batch: batch },
        onCompleted(data) {
          const exchangeId = data.createExchange.data.id
          const content = { msg: value }
          const detail = {
            topic: topic,
            jobtitle: jobTitle,
            traineeId: traineeID,
            where: `${jobTitle}`,
            traineeLink: `/trainee/job/${traineeJobID}`,
            staffLink: `/staff`
          }
          createMessage({
            variables: { content: content,
               exchangeID: exchangeId,
               sender: allUserId },
            onCompleted(data) {
              const messageID = data.createMessage.data.id
              createNotification({
                variables: { message: messageID,
                   sender: allUserId, 
                   group: 1, 
                   detail: detail, 
                   batch: batch,
                   origin: "leap"
                  },
                   
                onError(error) {
                  console.error(error)
                }
              })
              refetch()
            },
            onError(error) {
              console.error(error)
            }
          })
        }
      })

    }
    else {
      const exchangeId = data?.exchanges.data[0].id
      const content = { msg: value }
      const detail = {
        topic: topic,
        asset: jobTitle,
        traineeId: traineeID,
        where: `${jobTitle}`,
        traineeLink: `/trainee/job/${traineeJobID}`,
        staffLink: `/staff`
      }
      createMessage({
        variables: { content: content, 
          exchangeID: exchangeId, 
          sender: allUserId },
        onCompleted(data) {
          const messageID = data.createMessage.data.id
          createNotification({
            variables: { message: messageID, 
              sender: allUserId, 
              group: 1, 
              detail: detail, 
              batch: batch },
            onError(error) {
              console.error(error)
            }
          })
          refetch()
        },
        onError(error) {
          console.error(error)
        }
      })
    }
  };

  const handleChange = (e: any) => {
    setValue(e.target.value);
  };

  if (data?.exchanges.data.length === 0) {
    return (
      <Row gutter={16}>
        <Col span={24}>
            <Form.Item>
               <TextArea maxLength={600} rows={4} onChange={handleChange} value={value} />
            </Form.Item>
            <Form.Item>
              <Button
                htmlType="submit"
                loading={submitting}
                onClick={handleSubmit}
                className="job-detail-feedback-button">
                  Post
              </Button>
          </Form.Item>
        </Col>
      </Row>
    )
  }
  else {
    return (
      data?.exchanges.data.length && 
      <Row gutter={16}>
        {
          data?.exchanges?.data[0]?.attributes?.messages?.data?.map((message: MessageEntity, index: number) => (
            <Col span={24} key={index}>
              <Comments content={message?.attributes?.content} createdAt={message?.attributes?.createdAt} sender={message?.attributes?.sender_id?.data?.attributes?.name}/>
            </Col>
          ))}

        <Col span={24}>
          <Row gutter={16}>
            <Col span={2}>
            <Avatar size={32} 
                      style={{ fontSize: "16px", 
                              backgroundColor: colors[(username?.length ?? 0) % colors.length], 
                              verticalAlign: 'middle' }}
                            >
                  {extractInitials(username)}
                  </Avatar>
            </Col>
            <Col span={22}>
              <Form.Item>
              <TextArea maxLength={600} rows={4} onChange={handleChange} value={value} />
            </Form.Item>
              <Form.Item className="mt-16">
              <Button
                htmlType="submit"
                loading={submitting}
                onClick={handleSubmit}
                className="job-detail-feedback-button">
                Post
              </Button>
            </Form.Item>
            </Col>
          </Row>
        </Col>
      </Row>
    )
  }
}