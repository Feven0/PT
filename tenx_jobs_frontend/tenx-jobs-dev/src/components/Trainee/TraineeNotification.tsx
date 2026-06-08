import { Badge, Col, Divider, Dropdown, Menu, Row, Space, Switch, Tooltip, Typography } from 'antd'
import { useEffect, useState } from 'react'
import { BellOutlined, ClearOutlined } from '@ant-design/icons';
import { useMutation, useQuery } from '@apollo/client';
import { useMediaQuery } from "react-responsive";
import moment from 'moment';
import { Link } from 'react-router-dom';
import type { MenuProps } from 'antd';

//Redux ands custom hooks
import { useAppSelector } from "../../redux/hooks/hooks";
import { NotificationEntity, NotificationEntityResponseCollection } from "../../types/generated";
import { CREATE_NOTIFICATION_STATUS } from "../../graphql/mutations/createNotification";
import { NOTIFICATION } from "../../graphql/queries/getNotification";

//Styles
import '../../styles/button.css'

const { Title, Text } = Typography


type Notification = {
  notifications: NotificationEntityResponseCollection
}

export default function TraineeNotification() {
  const [count, setCount] = useState(0)
  const [reload, setReload] = useState(true)
  const [showUnread, setShowUnread] = useState(true)
  const { username, allUserId, groups } = useAppSelector((state) => state.user)

  const isMobile = useMediaQuery({ maxWidth: 992 });

  const [createNotificationStat] = useMutation(CREATE_NOTIFICATION_STATUS);
  const { loading, error, data, refetch } = useQuery<Notification>(NOTIFICATION, {
    variables: {
      allUser: allUserId,
      groupID: groups,
      origin: "leap"
    },
    nextFetchPolicy: 'network-only',
    pollInterval: 300000
  })

  const onClickSave = (e: any) => {
    createNotificationStat({
      variables:
      {
        NotificationID: e,
        allUserID: allUserId
      },
    })
    refetch()
    setReload(!reload)
  }

  const onClickCheck = (_e: any) => { }

  useEffect(() => {
    let count = 0;
    if (data) {
      data.notifications.data.forEach((notification: NotificationEntity) => {
        if (notification?.attributes?.notification_statuses?.data?.length === 0) {
          count = count + 1
        }
      })
      setCount(count)
    }
  }, [data])


  if (loading) return <></>
  if (error) return <></>

  const onChangeSWitch = () => {
    setShowUnread(!showUnread)
  }

  const markAllAsRead = () => {
    data?.notifications?.data.map((notification: NotificationEntity) => {
      if (notification?.attributes?.notification_statuses?.data?.length === 0) {
        createNotificationStat({
          variables: {
            NotificationID: notification.id,
            allUserID: allUserId
          }
        })
      }
    })
    refetch()
    setReload(!reload)
  }

  const notificationMenu = (
    <Menu className="notificationDropdown" >
      <Row gutter={[2, 4]}>
        <Col xs={10} lg={8}>
          <Title className="notificationTitle">
            Notifications
          </Title>
        </Col>
        <Col xs={4} lg={4} className="mark-all-as-read">
          <Tooltip title={'Mark all as read'}>
            <ClearOutlined onClick={markAllAsRead} style={{ fontSize: "20px" }} />
          </Tooltip>
        </Col>
        <Col xs={10} lg={12} className="notificationButtons">
          {
            isMobile ? <>
              <Tooltip title={' Only show unread'}>
                <Switch defaultChecked onChange={onChangeSWitch} onClick={markAllAsRead} />
              </Tooltip>
            </> : <>
              <Space>
                <Text className="unreadText">
                  Only show unread
                </Text>
              </Space>
              <Switch defaultChecked onChange={onChangeSWitch} />
            </>
          }
        </Col>
      </Row>
      <Divider style={{ margin: "10px 0" }} />
      {data?.notifications?.data.map((notification: NotificationEntity) => {
        if (notification?.attributes?.notification_statuses?.data?.length === 0) {
          const detail = notification?.attributes?.Detail === "" ? {} : typeof (notification?.attributes?.Detail) === "string" ? JSON.parse(notification?.attributes?.Detail) : notification?.attributes?.Detail
          return (
            <Menu.Item onClick={() => onClickSave(notification.id)} key={notification.id}>
              <Link to={detail.traineeLink}>
                <Space direction='vertical' size={1}>

                  <Text className="notification-title">
                    <Badge color={"#FAAD14"} />{` Dear ${username},`}
                    <br></br>
                    {` ${notification?.attributes?.sender?.data?.attributes?.name} ${(detail.notificationMessageTrainee ?
                      detail.notificationMessageTrainee :
                      (detail.notificationMessage ?
                        detail.notificationMessage :
                        `added a new comment on ${notification?.attributes?.Detail.where}`))} `}

                  </Text>
                  <Text className="notification-sub-title">
                    {`Posted `}
                    <Tooltip title={moment().format("YYYY-MM-DD HH:mm:ss")}>
                      <span>{moment(notification?.attributes?.createdAt).fromNow()}</span>
                    </Tooltip>
                    {` by ${notification?.attributes?.sender?.data?.attributes?.email}`}

                  </Text>
                </Space>
              </Link>
            </Menu.Item>
          );
        }
        else if (notification?.attributes?.notification_statuses?.data && notification?.attributes?.notification_statuses?.data?.length >= 1 && !showUnread) {
          if (moment(notification?.attributes?.notification_statuses?.data[0]?.attributes?.createdAt).isAfter(moment().subtract(1, 'hours'))) {
            const detail = notification?.attributes?.Detail === "" ? {} : typeof (notification?.attributes?.Detail) === "string" ? JSON.parse(notification?.attributes?.Detail) : notification?.attributes?.Detail

            return (
              <Menu.Item onClick={() => onClickCheck(notification.id)} key={notification.id}>
                <Link to={detail.traineeLink}>
                  <Space direction='vertical' size={1}>

                    <Text className="notification-title">
                      {`Dear ${username},`}
                      <br></br>
                      {` ${notification?.attributes?.sender?.data?.attributes?.name} ${(detail.notificationMessageTrainee ?
                        detail.notificationMessageTrainee :
                        (detail.notificationMessage ?
                          detail.notificationMessage :
                          `added a new comment on ${detail.where}`))} `}
                    </Text>
                    <Text className="notification-sub-title">
                      {`Posted `}
                      <Tooltip title={moment().format("YYYY-MM-DD HH:mm:ss")}>
                        <span>{moment(notification?.attributes?.createdAt).fromNow()}</span>
                      </Tooltip>
                      {` by ${notification?.attributes?.sender?.data?.attributes?.email}`}

                    </Text>
                  </Space>
                </Link>
              </Menu.Item>
            )
          }
        }

      })}
    </Menu>
  );

  const items: MenuProps['items'] = [
    {
      key: '1',
      label: notificationMenu
    },
  ];

  return (
    <Dropdown overlayStyle={{ zIndex: 99999 }} trigger={['click']} menu={{ items }}>
      <Badge size="small" offset={[-7, 4]} count={count < 0 ? 0 : count}>
        <BellOutlined style={{ fontSize: "20px", marginRight: "6px" }} />
      </Badge>
    </Dropdown>
  )
}
