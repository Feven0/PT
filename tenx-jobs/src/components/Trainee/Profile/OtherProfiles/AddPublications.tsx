import { Button, Col, DatePicker, Form, Input, message, Popconfirm, Row } from "antd";
import { useEffect } from "react";
import { useMutation } from "@apollo/client";
import moment from "moment";
import { useAppDispatch, useAppSelector } from "../../../../redux/hooks/hooks";
import {setPublicationUUID, setTraineePublications } from "../../../../redux/slices/otherProfilesSlice";
import { formatDateToYYYYMMDD } from "../../../../utils/commonUtils";
import { CREATE_NOTIFICATION } from "../../../../graphql/mutations/createNotification";
import useFetchUserProfile from "../../../../hooks/useFetchUserProfile";
import useAxiosRequest from "../../../../hooks/useAxiosRequest";
import { getRunStage } from "../../../../utils/getRunStage";

const run_stage = getRunStage()
const {TextArea} = Input;

type PublicationsProps = {
  setIsPublicationDrawerVisible: (value: boolean) => void;
}
export default function AddPublications({setIsPublicationDrawerVisible}: PublicationsProps) {
  const {publications, publicationUUID} = useAppSelector(state => state.otherProfiles);
  const {allUserId, user_profile_id, user_role, trainee_id, batch} = useAppSelector(state => state.leapProfileId)
  const {publicationButtonEditing} = useAppSelector(state => state.otherProfileSubmitButtons)
  const  { fetchUserProfile } = useFetchUserProfile();
  const { makeRequest, loading } = useAxiosRequest();

  const [form] = Form.useForm();
  const dispatch = useAppDispatch();
  const [createNotification] = useMutation(CREATE_NOTIFICATION);

  useEffect(() => {
    form.setFieldsValue({
      name: publications?.name || "",
      date: publications?.release_date && moment(publications.release_date).isValid() 
      ? moment(publications.release_date) 
      : moment(), 
      description: publications?.summary || "",
      url: publications?.url || "",
      publisher: publications?.publisher || "",
    })
  }, [publications])

  const onFinish = () => {
    let data = {}
    if(publications.id === publicationUUID) {
     data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      user_profile_id: user_profile_id,
      user_profile: [
        {
          code: "publications",
          uuid: publicationUUID,
          data: {
            name: publications.name,
            release_date: formatDateToYYYYMMDD(publications.release_date),
            publisher: publications.publisher,
            url: publications.url,
            summary: publications.summary,
          }
        }
      ],
      status: "approved",  
    }
    }else{
      data = {
        user_role: user_role,
        run_stage: run_stage,
        all_user_id: allUserId,
        user_profile_id: user_profile_id,
        user_profile: [
          {
            code: "publications",
            data: {
              name: publications.name,
              release_date: formatDateToYYYYMMDD(publications.release_date),
              publisher: publications.publisher,
              url: publications.url,
              summary: publications.summary,
            }
          }
        ],
        status: "approved",  
      }
    }

    const details = {
      traineeId: trainee_id,
      notificationMessageTeam: `Added a new publication! `,
      notificationMessageTrainee: `Added a new publication!`,
      where: "Publications",
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

              if (publications.id === publicationUUID) {
                message.success("Publication updated successfully");
              } else {
                message.success("Publication added successfully");
              }
              message.success("Publication added successfully");
              setIsPublicationDrawerVisible(false);
              dispatch(setPublicationUUID(""));
              fetchUserProfile();
              form.resetFields();
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
        <Form name="achievements_form" form={form} layout="vertical">
          <Form.Item
            label="Name"
            name="name"
            rules={[{ required: true, message: 'Please input publication name!' }]}>
            <Input onChange={(e)=> dispatch(setTraineePublications({
              ...publications, 
              name: e.target.value
            }))}
              placeholder="Please input publication title!"/>
          </Form.Item>
          <Form.Item
            label="Publisher"
            name="publisher"
            rules={[{ required: true, message: 'Please input publisher!' }]}>
            <Input onChange={(e)=> dispatch(setTraineePublications({
              ...publications, 
              publisher: e.target.value
            }))}
              placeholder="Please input publisher!"/>
          </Form.Item>
          <Form.Item 
                name="date" 
                label="Release Date"
                rules={[{ required: true, message: 'Please select release date'}]}>
              <DatePicker 
                style={{ width: '100%' }} 
                onChange={(_date, dateString) => {
                  if (typeof dateString === 'string') {
                    dispatch(setTraineePublications({
                      ...publications, 
                      release_date: dateString
                    }));
                  }
                }}
              />
          </Form.Item>
          <Form.Item
            label="URL"
            name="url"
            rules={[{ required: false, message: 'Please input publication link!' }]}>
            <Input onChange={(e)=> dispatch(setTraineePublications({
              ...publications, 
              url: e.target.value
            }))}
              placeholder="Please input publication link!"/>
          </Form.Item>
            <Form.Item 
                  label="Description" 
                  tooltip="Publication description" 
                  colon={false}
                  name="description"
                  className="applicationForm"
                  rules={[{ required: true, message: "Please input a description"}]}>
                <TextArea placeholder="Please input description" rows={4}
                      value={publications?.summary ? publications.summary : ""}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                      dispatch(setTraineePublications({ 
                      ...publications, 
                      summary: e.target.value 
                      }))} />
          </Form.Item>
            <Form.Item className="update-submit-button">
            <Popconfirm okText="Yes" cancelText="No"
                  title="Are you sure you want to upload this publication?"
                  onConfirm={() => onFinish()}
                  onCancel={() => {message.info("Publication creation cancelled")}}>
                    <Button className="dark-orange-bg white-color" loading = {loading} >
                        {publicationButtonEditing ? "Update" : "Add Publication"}
                  </Button>
            </Popconfirm>
          </Form.Item>
        </Form>
      </Col>
   </Row>
  )
}
