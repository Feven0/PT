import { Badge, Col, Divider, Dropdown, Menu, Row, Space, Switch, Tooltip, Typography } from 'antd'
import { useEffect, useState } from 'react'
import { BellOutlined, ClearOutlined } from '@ant-design/icons';
import { gql, useMutation, useQuery } from '@apollo/client';
import { useMediaQuery } from "react-responsive";
import moment from 'moment';
import { Link } from 'react-router-dom';
import { GET_TEAM_NOTIFICATION } from "../../graphql/queries/getNotification";
import { useAppSelector } from "../../redux/hooks/hooks";
import { NotificationEntity, NotificationEntityResponseCollection } from "../../types/generated";
import '../../styles/button.css'

const { Title, Text } = Typography

const CREATE_NOTIFICATION_STATUS = gql`
mutation CreateNotificationStatus($alluserID:ID,$NotificationID:ID){
  createNotificationStatus(data:{all_user:$alluserID,notification:$NotificationID,IsRead:true}){
    data{
      id
    }
  }
}`

type NotificationTypes = {
  notifications: NotificationEntityResponseCollection
}

export default function TeamNotification() {
  const [count, setCount] = useState(0)
  const [reload, setReload] = useState(true)
  const [showUnread, setshowUnread] = useState(true)
  const { username, groups, batch } = useAppSelector((state) => state.user)
  const allUserId = useAppSelector((state) => state.user?.allUserId)

  const isMobile = useMediaQuery({ maxWidth: 992 });
  const [createNotificationStat] = useMutation(CREATE_NOTIFICATION_STATUS);

  const { loading: NotificationLoading, error: NotificationError, data: NotificationData, refetch } = useQuery<NotificationTypes>(GET_TEAM_NOTIFICATION, {
    variables: {
      allUser: allUserId,
      groupID: groups,
      batch: batch,
      origin: "leap"
    },
    nextFetchPolicy: 'network-only'
  })

  const onClickSave = (e: any) => {
    createNotificationStat({
      variables: { NotificationID: e, alluserID: allUserId },
    })
    refetch()
    setReload(!reload)
  }

  const onClickCheck = (_e: any) => { }

  useEffect(() => {
    let count = 0;
    if (NotificationData) {
      NotificationData.notifications.data.forEach((notification: NotificationEntity) => {
        if (notification?.attributes?.notification_statuses?.data.length === 0) {
          count = count + 1
        }
      })
      setCount(count)
    }
  }, [NotificationData])


  if (NotificationLoading) {
    return (
      <></>
    );

  }
  if (NotificationError) {
    return (
      null
    );
  }
  const onChangeSWitch = () => {
    setshowUnread(!showUnread)
  }
  const markallasRead = () => {
    NotificationData?.notifications?.data.map((notification: NotificationEntity) => {
      if (notification?.attributes?.notification_statuses?.data.length === 0) {
        createNotificationStat({
          variables: {
            NotificationID: notification.id,
            alluserID: allUserId
          },
        })
      }
    })
    refetch()
    setReload(!reload)
  }

  const notificationMenu = (
    <Menu className="notificationDropdown">
      <Row gutter={[2, 4]}>
        <Col xs={10} lg={8}>
          <Title className="notificationTitle">
            Notifications
          </Title>
        </Col>
        <Col xs={4} lg={4} className="mark-all-as-read">
          <Tooltip title={'Mark all as read'}>
            <ClearOutlined onClick={markallasRead} style={{ fontSize: "20px", marginTop: "8px" }} />
          </Tooltip>
        </Col>
        <Col xs={10} lg={12} className="notificationButtons">
          {
            isMobile ? <>
              <Tooltip title={' Only show unread'}>
                <Switch defaultChecked onChange={onChangeSWitch} onClick={markallasRead} />
              </Tooltip>
            </> : <>
              <Space style={{ paddingTop: "10px" }}>
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
      {NotificationData?.notifications?.data?.map((notification: NotificationEntity) => {
        if (notification?.attributes?.notification_statuses?.data?.length === 0) {
          const detail = notification.attributes.Detail === "" ? {} : typeof (notification?.attributes?.Detail) === "string" ? JSON.parse(notification?.attributes?.Detail) : notification?.attributes?.Detail
          return (
            <Menu.Item onClick={() => onClickSave(notification?.id)} key={notification?.id} className="notificationsList">
              <Link to={detail?.staffLink}>
                <Space direction='vertical' size={1}>

                  <Text className="notification-title">
                    <Badge color={"#FAAD14"} />
                    {` Dear ${username},`}
                    <br></br>
                    {` ${notification?.attributes?.sender?.data?.attributes?.name} ${(detail?.notificationMessageTeam ? detail?.notificationMessageTeam : (detail?.notificationMessage ? detail?.notificationMessage : `added a new comment on ${detail?.where}`))} `}
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
        else if (notification?.attributes?.notification_statuses?.data?.length && notification.attributes.notification_statuses.data.length >= 1 && !showUnread) {
          if (moment(notification?.attributes?.notification_statuses?.data[0]?.attributes?.createdAt).isAfter(moment().subtract(1, 'hours'))) {
            const detail = notification.attributes.Detail === "" ? {} : typeof (notification?.attributes?.Detail) === "string" ? JSON.parse(notification?.attributes?.Detail) : notification?.attributes?.Detail

            return (
              <Menu.Item onClick={() => onClickCheck(notification?.id)} key={notification?.id}>
                <Link to={detail.staffLink}>
                  <Space direction='vertical' size={1}>
                    <Text
                      className="notification-title">
                      {`Dear ${username},`}
                      <br></br>
                      {` ${notification?.attributes?.sender?.data?.attributes?.name} ${(detail.notificationMessageTeam ? detail.notificationMessageTeam : (detail.notificationMessage ? detail.notificationMessage : `added a new comment on ${detail.where}`))} `}
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

  return (
    <Dropdown overlayStyle={{ zIndex: 99999 }} trigger={['click']} overlay={notificationMenu}>
      <Badge size="small" offset={[-7, 4]} count={count < 0 ? 0 : count}>
        <BellOutlined style={{ fontSize: "20px", marginRight: "6px" }} />
      </Badge>
    </Dropdown>
  )
}
