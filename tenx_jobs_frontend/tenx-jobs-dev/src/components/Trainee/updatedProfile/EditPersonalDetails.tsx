import { Button, Card, Col, Flex, Form, Input, message, Popconfirm, Row, Select, Typography } from "antd"
import { PlusOutlined, DeleteOutlined } from "@ant-design/icons"
import { useEffect} from "react"
import { useMutation } from "@apollo/client";
import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { resetPersonalInformation, setPersonalInformation } from "../../../redux/slices/personalInformationSlice";
import { CREATE_NOTIFICATION } from "../../../graphql/mutations/createNotification";
import useUpdateMedia from "../../../hooks/useupdateMedia";
import { addMediaSession, removeMediaSession, resetMediaForm } from "../../../redux/slices/setMediaSlice";
import { addContactsSession, removeContactsSession, resetContactsForm } from "../../../redux/slices/setContactsSlice";
import useContactsForm from "../../../hooks/useContactsForm";
import useFetchUserProfile from "../../../hooks/useFetchUserProfile";
import useAxiosRequest from "../../../hooks/useAxiosRequest";
import '../../../styles/slidingCard.css'
import { getRunStage } from "../../../utils/getRunStage";

type personalInfoProps = {
  closeDrawer: () => void;
}

const { Paragraph } = Typography

const run_stage = getRunStage();

export default function EditPersonalDetails({ closeDrawer }: personalInfoProps) {
  const [form] = Form.useForm()
  const { info } = useAppSelector((state) => state.personalInformation)
  const { media } = useAppSelector((state) => state.setMediaForm)
  const { phone } = useAppSelector((state) => state.contactsForm)
  const { allUserId, user_profile_id, user_role, trainee_id, batch } = useAppSelector(state => state.leapProfileId)

  const [createNotification] = useMutation(CREATE_NOTIFICATION);
  const { handleSelectChange, handleMaxSectionChange, capitalizedOptions } = useUpdateMedia();
  const { handleContactSelectChange, handleContactMaxSectionChange, capitalizeContactsOptions } = useContactsForm()
  const  { fetchUserProfile } = useFetchUserProfile();

  const dispatch = useAppDispatch()
  const { makeRequest, loading } = useAxiosRequest();

  useEffect(() => {
    form.setFieldsValue({
      "full-name": info.full_name,
      "email": info.email,
      "role": info.role,
      "name-title": info.name_title,
      "country": info.location.country,
      "address": info.location.address,
      "city": info.location.city,
      "postal-code": info.location.postal_code,
      "region": info.location.region,
      phone: phone,
      media: media,
    });
  }, [info]);

  const onFinish = () => {
    const data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      user_profile_id: user_profile_id,
      user_profile: [
        {
          code: "basics",
          uuid: info.id,
          data: {
            full_name: info.full_name,
            email: info.email,
            role: info.role,
            name_title: info.name_title,
            phone: phone,
            location: info.location,
            media: media,
            personal_statement: info.personal_statement,
          },
        },
      ],
      status: "approved",
    }
    const details = {
      traineeId: trainee_id,
      notificationMessageTeam: `Updated basics! `,
      notificationMessageTrainee: `Updated basics!`,
      where: "Profile",
      traineeLink: `/trainee/trainee-profile`,
      staffLink: `/staff/trainee_details/${allUserId}/${trainee_id}/${user_profile_id}`,
    }

    form.validateFields()
    .then(() => {
      makeRequest({
        url: '/sjob/put-user-profile',
        method: 'POST',
        data,
        onSuccess: (response) => {
          if (response.status === 200) {
            createNotification({
              variables: {
                sender: allUserId,
                group: 1,
                detail: details,
                origin: "leap",
                batch: batch,
              },
              onCompleted(data) {
                if (data?.createNotification?.data.id) {
                  message.success("Notification created successfully");
                } else {
                  console.error("Notification creation failed");
                }
              },
            });
            message.success("Profile updated successfully");
            dispatch(resetPersonalInformation());
            dispatch(resetContactsForm());
            dispatch(resetMediaForm());
            closeDrawer();
            form.resetFields();
            fetchUserProfile();
          } 
        },
        onError: () => {}
      });
    })
    .catch(() => {});
  }

  return (
    <Row gutter={16}>
      <Col span={24}>
        <Form layout="vertical" form={form}>
          <Form.Item className="personal-info-submit">
            <Popconfirm okText="Yes" cancelText="No"
              title="Are you sure you want to update this train information?"
              onConfirm={() => onFinish()}
              onCancel={() => { message.info("Profile creation cancelled") }}>
              <Button className="dark-orange-bg white-color" loading={loading} >
                Update
              </Button>
            </Popconfirm>
          </Form.Item>
          <Form.Item label="Full Name" name="full-name"
            rules={[{ required: true, message: 'Please input your full name!' }]}
          >
            <Input
              placeholder="Please input your full name"
              onChange={(e) =>
                dispatch(
                  setPersonalInformation({
                    info: {
                      ...info,
                      full_name: e.target.value,
                    },
                  })
                )
              }
            />
          </Form.Item>
          <Form.Item label="Email" name="email"
            rules={[{ required: true, type: 'email', message: 'Please input your  email!' }]}
          >
            <Input placeholder="eg. someone@gmail.com"
              onChange={(e) =>
                dispatch(
                  setPersonalInformation({
                    info: {
                      ...info,
                      email: e.target.value,
                    },
                  })
                )
              }
            />
          </Form.Item>
          <Form.Item label="Role" name="role">
            <Input placeholder="eg. Developer"
              onChange={(e) =>
                dispatch(
                  setPersonalInformation({
                    info: {
                      ...info,
                      role: e.target.value,
                    },
                  })
                )
              }
            />
          </Form.Item>
          <Form.Item label="Name Title" name="name-title">
            <Input placeholder="eg. Mr"
              onChange={(e) =>
                dispatch(
                  setPersonalInformation({
                    info: {
                      ...info,
                      name_title: e.target.value,
                    },
                  })
                )
              }
            />
          </Form.Item>
          <Paragraph>Contacts</Paragraph>
          <Form.List
            name="contacts"
            initialValue={phone}
            rules={[]}
          >
            {(phone, { add, remove }) => (
              <div style={{ display: 'flex', rowGap: 8, flexDirection: 'column' }}>
                {phone.map((field) => {
                  return (
                    <Card
                      size="small"
                      title={<div className="d-flex-between">
                        <span>
                          {`Contact-${field.name + 1}`}
                        </span>
                        {phone.length > 0 && (
                          <Flex justify='flex-end'>
                            <Button
                              style={{ background: "#FF4405", color: "#FFF" }}
                              icon={<DeleteOutlined />}
                              onClick={() => {
                                dispatch(removeContactsSession(field.name));
                                remove(field.name)
                              }}
                            />
                          </Flex>
                        )}
                      </div>
                      }
                      key={field.key}
                    >
                      <Row gutter={[16, 16]}>
                        <Col span={12}>
                          <Form.Item
                            label="Name"
                            name={[field.name, 'name']}
                            rules={[{ required: false, message: 'Please select Media name!' }]}
                            tooltip="Contacts"
                          >
                            <Select
                              options={capitalizeContactsOptions}
                              placeholder="Select name"
                              onChange={(value) => handleContactSelectChange(value, field.name)}
                              value={field.name.toString()}
                            />
                          </Form.Item>
                        </Col>
                        <Col span={12}>
                          <Form.Item
                            label="Value"
                            name={[field.name, 'value']}
                            rules={[{ required: false, message: 'Please input contact!' }]}
                            tooltip="Contacts url"
                          >
                            <Input
                              placeholder='Contact'
                              style={{ width: "100%" }}
                              value={field.name}
                              onChange={(e) => handleContactMaxSectionChange(e.target.value, field.name)}
                            />
                          </Form.Item>

                        </Col>

                      </Row>
                    </Card>
                  )
                })}
                {phone.length < 5 && (
                  <Button type="dashed"
                    className="mb-16"
                    onClick={() => {
                      dispatch(addContactsSession());
                      add();
                    }}
                    block
                    icon={<PlusOutlined />}
                  >
                    Add Item
                  </Button>
                )}
              </div>
            )}
          </Form.List>
          <Form.Item label="Country" name="country">
            <Input placeholder="eg. Ethiopia"
              onChange={(e) =>
                dispatch(
                  setPersonalInformation({
                    info: {
                      ...info,
                      location: {
                        ...info.location,
                        country: e.target.value,
                      },
                    },
                  })
                )
              }
            />
          </Form.Item>
          <Form.Item label="Address" name="address"
            rules={[{ required: false, message: 'Please input your address!' }]}
          >
            <Input placeholder="eg. Addis Ababa"
              onChange={(e) =>
                dispatch(
                  setPersonalInformation({
                    info: {
                      ...info,
                      location: {
                        ...info.location,
                        address: e.target.value,
                      },
                    },
                  })
                )
              }
            />
          </Form.Item>
          <Form.Item label="City" name="city"
            rules={[{ required: false, message: 'Please input your city!' }]}>
            <Input placeholder="eg. Addis Ababa"
              onChange={(e) =>
                dispatch(
                  setPersonalInformation({
                    info: {
                      ...info,
                      location: {
                        ...info.location,
                        city: e.target.value,
                      },
                    },
                  })
                )
              }
            />
          </Form.Item>
          <Form.Item label="Postal Code" name="postal-code"
            rules={[{ required: false, message: 'Please input your state!' }]}>
            <Input placeholder="Please Input your postal code"
              onChange={(e) =>
                dispatch(
                  setPersonalInformation({
                    info: {
                      ...info,
                      location: {
                        ...info.location,
                        postal_code: e.target.value,
                      },
                    },
                  })
                )
              }
            />
          </Form.Item>
          <Form.Item label="Region" name="region">
            <Input placeholder="eg. Africa"
              onChange={(e) =>
                dispatch(
                  setPersonalInformation({
                    info: {
                      ...info,
                      location: {
                        ...info.location,
                        region: e.target.value,
                      },
                    },
                  })
                )
              }
            />
          </Form.Item>
          <Paragraph>Medias</Paragraph>
          <Form.List
            name="medias"
            initialValue={media}
            rules={[]} >
            {(media, { add, remove }) => (
              <div style={{ display: 'flex', rowGap: 16, flexDirection: 'column' }}>
                {media.map((field) => {
                  return (
                    <Card
                      size="small"
                      title={<div className="d-flex-between">
                        <span>
                          {`Media-${field.name + 1}`}
                        </span>
                        {media.length > 0 && (
                          <Flex justify='flex-end'>
                            <Button
                              style={{ background: "#FF4405", color: "#FFF" }}
                              icon={<DeleteOutlined />}
                              onClick={() => {
                                dispatch(removeMediaSession(field.name));
                                remove(field.name)
                              }}
                            />
                          </Flex>
                        )}
                      </div>
                      }
                      key={field.key}
                    >
                      <Row gutter={[16, 16]}>
                        <Col span={12}>
                          <Form.Item
                            label="Name"
                            name={[field.name, 'name']}
                            rules={[{ required: false, message: 'Please select Media name!' }]}
                            tooltip="Media"
                          >
                            <Select
                              options={capitalizedOptions}
                              placeholder="Select name"
                              onChange={(value) => handleSelectChange(value, field.name)}
                              value={field.name.toString()}
                            />
                          </Form.Item>
                        </Col>
                        <Col span={12}>
                          <Form.Item
                            label="Link"
                            name={[field.name, 'link']}
                            rules={[{ required: false, message: 'Please input level!', type: "url" }]}
                            tooltip="Media url"
                          >
                            <Input
                              placeholder='Link'
                              style={{ width: "100%" }}
                              value={field.name}
                              onChange={(e) => handleMaxSectionChange(e.target.value, field.name)}
                            />
                          </Form.Item>

                        </Col>
                      </Row>
                    </Card>
                  )
                })}
                {media.length < 10 && (
                  <Button type="dashed"
                    className="mb-16"
                    onClick={() => {
                      dispatch(addMediaSession());
                      add();
                    }}
                    block
                    icon={<PlusOutlined />}
                  >
                    Add Item
                  </Button>
                )}
              </div>
            )}
          </Form.List>
        </Form>
      </Col>
    </Row>
  )
}

