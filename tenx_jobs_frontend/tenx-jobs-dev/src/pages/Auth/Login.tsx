import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Row, Col, message, notification } from "antd";
import { Form, Input, Button } from "antd";
import { Mail01, PasscodeLock } from '@untitled-ui/icons-react';
import { gql, useLazyQuery, useMutation } from "@apollo/client";
import { useDispatch } from "react-redux";
import { setToken, setUsername, setRole, setEmail, setStrapiId } from "../../redux/slices/userSlices";
import { setWithExpiry } from "../../utils/BrowserFunction";
import AuthBackgroundPattern from "./AuthBackgroundPattern";
import { log } from "../../graphql/mutations/Log";
import { setUserRole, setUserToken } from "../../redux/slices/leapProfileIdSlice";
import '../../styles/auth.css'

const backendUrl = import.meta.env.VITE_API_BACKEND_URL;

export default function Login() {
  const dispatch = useDispatch()
  const [errorMessage, setErrorMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();
  const resetForm = () => {
    form.resetFields();
  };

  const me = gql`
    query {
      me {
        username,
        email,
        role {
          name
        }
      }
    }
  `;

  const [fetchMe] = useLazyQuery(me, {
    fetchPolicy: "network-only",
    onCompleted: data => {
      dispatch(setRole({ role: data.me.role.name }))
      dispatch(setUserRole(data.me.role.name))
      dispatch(setEmail({ email: data.me.email }))
      if (data.me.role.name === "Trainee") {
        navigate("/trainee")
      } else if (data.me.role.name === "Staff") {
        navigate("/team")
      }
    }
  });

  const [createLog] = useMutation(log);

  const openNotification = () => {
    notification.success({
      message: `Hi,`,
      description: `We’ve sent a link for changing password to your email. Please reset your password.`,
      duration: 0,
      placement: 'top'
    });
  };

  const navigate = useNavigate();

  const handleSubmit = async (values: any) => {
    setLoading(true);
    const user_info = {
      identifier: values.email.trim(),
      password: values.password,
    };

    axios
      .post(`${backendUrl}/api/auth/local/`, user_info)
      .then((response) => {
        setLoading(false);
        setErrorMessage("")
        setWithExpiry("token", response.data.jwt, 24 * 60 * 60 * 1000)
        dispatch(setToken({ token: response.data.jwt }))
        dispatch(setUserToken(response.data.jwt))
        dispatch(setUsername({ username: response.data.user.username }))

        dispatch(setStrapiId(response.data.user.id))

        createLog({ variables: { "userId": response.data.user.id, "action": "login" } })

        resetForm()

        if (response.data.user.createdAt === response.data.user.updatedAt) {
          axios
            .post(`${backendUrl}/api/auth/forgot-password`, {
              email: response.data.user.email,
            })
            .then(_response => {
              openNotification()
            })
            .catch(error => {
              if (error.response) {
                message.error(error.response.data.error.message);
              setLoading(false);
              } else {
                message.error('Server error.', 2)
              }

            })
        } else {
          fetchMe()
        }
      })
      .catch((error) => {
        setLoading(false);
        if (error.response) {
          setErrorMessage((_val) => error.response.data.error?.message);
        } else {
          message.error('Server error.', 2)
        }
      });
  };

  return (
    <Row gutter={[16, 16]} className="full-width full-height overflow-y margin-0">
        <AuthBackgroundPattern />
        <Col xs={0} md={1} xxl={2}/>
        <Col xs={24} md={12} xl={12} className="auth-form-wrapper-login">
            <Row gutter={[16, 16]} justify="center" className="auth-form-container-login margin-0" style={{paddingBottom:"2rem"}}>
                <Col xs={24} md={20} lg={18} xl={16} xxl={11}>
                    <div className='auth-title-wrapper'>
                        <h3 className="auth-title-login" style={{whiteSpace: 'pre-wrap' }}>You’re back!</h3>
                        <p className="auth-sub-title-login">We are Thrilled you are here!</p>
                    </div>
                </Col>
                <Col xs={24} md={20} lg={18} xl={16} xxl={11}>
                {
                    errorMessage && <p className="error__message">
                        {errorMessage}
                    </p>
                }
                <Form name="login_form" form={form} onFinish={handleSubmit} className="auth-form-items">
                    <Form.Item name="email"
                        validateStatus={errorMessage ? "error" : ""}
                        rules={[
                            {
                                required: true,
                                message: "Please input your email!",
                            },
                        ]}>
                        <Input placeholder='Email' type='email' suffix={<Mail01 style={{ opacity: "0.5" }} />} />
                    </Form.Item>
                    <Form.Item name="password"
                        validateStatus={errorMessage ? "error" : ""}
                        rules={[
                            {
                                required: true,
                                message: "Please input your Password!",
                            },
                        ]}>
                        <Input.Password placeholder='Password' type='password' suffix={<PasscodeLock style={{ opacity: "0.5" }} />} />
                    </Form.Item>
                    <Form.Item>
                        <Button loading={loading} htmlType='submit' className="auth-button-login">
                            Login
                        </Button>
                    </Form.Item>
                </Form>
            </Col>
          </Row>
    </Col>
</Row>
  );
}
