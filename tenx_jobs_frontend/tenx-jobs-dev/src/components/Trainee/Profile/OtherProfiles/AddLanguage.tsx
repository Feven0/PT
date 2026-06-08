import { Button, Col, Form, Input, message, Popconfirm, Row } from "antd";
import { useEffect } from "react";
import { useMutation } from "@apollo/client";
import { useAppDispatch, useAppSelector } from "../../../../redux/hooks/hooks";
import { resetLanguages, setLanguages, setLanguageUUID } from "../../../../redux/slices/otherProfilesSlice";
import { CREATE_NOTIFICATION } from "../../../../graphql/mutations/createNotification";
import useFetchUserProfile from "../../../../hooks/useFetchUserProfile";
import useAxiosRequest from "../../../../hooks/useAxiosRequest";
import { getRunStage } from "../../../../utils/getRunStage";

const run_stage = getRunStage();

type LanguageProps = {
  setIsLanguageModalVisible: (value: boolean) => void;
}

export default function AddLanguage({setIsLanguageModalVisible}: LanguageProps) {
  const {languages, languageUUID} = useAppSelector(state => state.otherProfiles);
  const {allUserId, user_profile_id, user_role, trainee_id, batch} = useAppSelector(state => state.leapProfileId)
  const {languageButtonEditing} = useAppSelector(state => state.otherProfileSubmitButtons)

  const  { fetchUserProfile } = useFetchUserProfile();
  const { makeRequest, loading } = useAxiosRequest();

  const [form] = Form.useForm();
  const dispatch = useAppDispatch();
  const [createNotification] = useMutation(CREATE_NOTIFICATION);

  useEffect(() => {
    form.setFieldsValue({
      fluency: languages.fluency,
      language: languages.language
    })
  }
  , [languages]
  )

  const onFinish = () => {
    let data = {}
    if(languages.id === languageUUID) {
    data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      user_profile_id: user_profile_id,
      user_profile: [
        {
          code: "languages",
          uuid: languageUUID,
          data: {
            fluency: languages.fluency,
            language: languages.language
          }
        }
      ],
      status: "approved",  
    }
    }else {
      data = {
        user_role: user_role,
        run_stage: run_stage,
        all_user_id: allUserId,
        user_profile_id: user_profile_id,
        user_profile: [
          {
            code: "languages",
            data: {
              fluency: languages.fluency,
              language: languages.language
            }
          }
        ],
        status: "approved",  
      }
    }
    const details = {
      traineeId: trainee_id,
      notificationMessageTeam: `Added a new languages! `,
      notificationMessageTrainee: `Added a new languages!`,
      where: "Languages",
      traineeLink: `/trainee/trainee-profile`,
      staffLink: `/staff/trainee_details/${allUserId}/${trainee_id}/${user_profile_id}`,
    }
    form.validateFields().then((values) => {
      {values}
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
  
          if (languages.id === languageUUID) {
            message.success("Language updated successfully");
          } else {
            message.success("Language added successfully");
          }
          message.success("Language added successfully");
          dispatch(resetLanguages());
          setIsLanguageModalVisible(false);
          dispatch(setLanguageUUID(""));
          fetchUserProfile();
          form.resetFields();
        } 
        },
        onError: () => {},
      });
    }).catch(() => {});
  }

  return (
   <Row gutter={16}>
      <Col span={24}>
        <Form name="language_form" form={form} layout="vertical">
        <Form.Item className="update-submit-button">
            <Popconfirm okText="Yes" cancelText="No"
                  title="Are you sure you want to upload this language?"
                  onConfirm={() => onFinish()}
                  onCancel={() => {message.info("Profile creation cancelled")}}>
                    <Button className="dark-orange-bg white-color" loading = {loading} >
                        {languageButtonEditing ? "Update" : "Add Language"}
                  </Button>
            </Popconfirm>
          </Form.Item>
          <Form.Item
            label="Fluency"
            name="fluency"
            rules={[{ required: true, message: 'Please input fluency!' }]}
          >
            <Input onChange={(e)=> dispatch(setLanguages({
              ...languages, fluency: e.target.value}))}
              placeholder="eg. Native Speaker, Professional ..."/>
          </Form.Item>
          <Form.Item
            label="language"
            name="language"
            rules={[{ required: true, message: 'Please input language!' }]}
          >
            <Input onChange={(e)=> dispatch(setLanguages({
              ...languages, language: e.target.value
            }))} placeholder="eg. English, Amharic ..."/>
          </Form.Item>
        </Form>
      </Col>
   </Row>
  )
}
