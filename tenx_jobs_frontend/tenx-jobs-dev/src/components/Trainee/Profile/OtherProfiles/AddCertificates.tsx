import moment from "moment";
import { Button, Col, DatePicker, Form, Input, message, Popconfirm, Row } from "antd";
import { useEffect } from "react";
import { useMutation } from "@apollo/client";
import { useAppDispatch, useAppSelector } from "../../../../redux/hooks/hooks";
import {resetTraineeCertificates, setCertificateUUID, setTraineeCertificates } from "../../../../redux/slices/otherProfilesSlice";
import { formatDateToYYYYMMDD } from "../../../../utils/commonUtils";
import { CREATE_NOTIFICATION } from "../../../../graphql/mutations/createNotification";
import useFetchUserProfile from "../../../../hooks/useFetchUserProfile";
import useAxiosRequest from "../../../../hooks/useAxiosRequest";
import { getRunStage } from "../../../../utils/getRunStage";

const run_stage = getRunStage();

type CertificateProps = {
  setIsCertificateModalVisible: (value: boolean) => void;
}

export default function AddCertificates({setIsCertificateModalVisible}: CertificateProps) {
  const {certificates, certificateUUID} = useAppSelector(state => state.otherProfiles);
  const {allUserId, user_profile_id, user_role, trainee_id, batch} = useAppSelector(state => state.leapProfileId)
  const {certificateButtonEditing} = useAppSelector(state => state.otherProfileSubmitButtons)
  const  { fetchUserProfile } = useFetchUserProfile();
  
  const [form] = Form.useForm();
  const dispatch = useAppDispatch();
  const [createNotification] = useMutation(CREATE_NOTIFICATION);

  useEffect(() => {
    if (certificates.date) {
      form.setFieldsValue({
        issuer: certificates.issuer,
        title: certificates.name,
        date: moment(certificates.date) 
      });
    } else {
      form.setFieldsValue({
        issuer: certificates.issuer,
        title: certificates.name,
        date: moment()
      });
    }
  }, [certificates, form]);

  const { makeRequest, loading } = useAxiosRequest();

  const onFinish = () => {
    let data = {}
    if(certificates.id === certificateUUID) {
     data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      user_profile_id: user_profile_id,
      user_profile: [
        {
          code: "certificates",
          uuid: certificateUUID,
          data: {
            issuer: certificates.issuer,
            name: certificates.name,
            date: formatDateToYYYYMMDD(certificates.date),
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
          code: "certificates",
          data: {
            issuer: certificates.issuer,
            name: certificates.name,
            date: formatDateToYYYYMMDD(certificates.date),
          }
        }
      ],
      status: "approved",  
    }
  }
    
    const details = {
      traineeId: trainee_id,
      notificationMessageTeam: `Added a new certificates! `,
      notificationMessageTrainee: `Added a new certificates!`,
      where: "Certificates",
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
                  batch,
                },
                onCompleted(data) {
                  if (data?.createNotification?.data.id) {
                    message.success("Notification created successfully");
                  } else {
                    console.error("Notification creation failed");
                  }
                },
              });
              message.success("Certificate added successfully");
              dispatch(resetTraineeCertificates());
              setIsCertificateModalVisible(false);
              dispatch(setCertificateUUID(""));
              fetchUserProfile();
              form.resetFields();
            } 
          },
          onError: () => { }
        });
      })
      .catch(() => {});
  }

  return (
   <Row gutter={16}>
      <Col span={24}>
        <Form name="certificate_form" form={form} layout="vertical">
          <Form.Item
            label="Issuer"
            name="issuer"
            rules={[{ required: true, message: 'Please input issuer!' }]}>
            <Input onChange={(e)=> dispatch(setTraineeCertificates({
              ...certificates, issuer: e.target.value}))}
              placeholder="Please input issuer!"/>
          </Form.Item>
          <Form.Item
              label="Title"
              name="title"
              rules={[{ required: true, message: 'Please input certificate title!' }]}>
              <Input onChange={(e)=> dispatch(setTraineeCertificates({
                ...certificates, name: e.target.value
              }))} placeholder="Please input certificate title"/>
            </Form.Item>
          <Form.Item 
                name="date" 
                label="Date"
                rules={[{ required: true, message: 'Please select issue date'}]}>
              <DatePicker 
              style={{ width: '100%' }} 
              onChange={(date, dateString) => {
                if (date && date.isValid() && typeof dateString === 'string') { 
                  dispatch(setTraineeCertificates({
                    ...certificates, 
                    date: dateString 
                  }));
                } else if (Array.isArray(dateString)) {
                  message.error("Unexpected date format. Please select a single date.");
                } else {
                  message.error("Invalid date selected");
                }
              }}
          />
          </Form.Item>
            <Form.Item className="update-submit-button">
            <Popconfirm okText="Yes" cancelText="No"
                  title="Are you sure you want to upload this certificate?"
                  onConfirm={() => onFinish()}
                  onCancel={() => {message.info("Profile creation cancelled")}}>
                    <Button className="dark-orange-bg white-color" loading = {loading} >
                        {certificateButtonEditing ? "Update" : "Add Certificate"}
                  </Button>
            </Popconfirm>
          </Form.Item>
        </Form>
      </Col>
   </Row>
  )
}
