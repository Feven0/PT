import { useState, useEffect } from 'react';
import { Drawer, Button, Form, Input, Tag, Divider, notification, Switch, Typography, Spin, message, Flex } from "antd"
import { PlusCircle, Maximize01, Minimize01 } from '@untitled-ui/icons-react';
import { setTableExtension, setEmails, } from '../../redux/slices/tableExtension';
import { CKEditor } from '@ckeditor/ckeditor5-react';
import ClassicEditor from '@ckeditor/ckeditor5-build-classic';
import { getRandomColor } from '../../utils/GenerateColors';
import { isEmailValid } from '../../utils/isEmailValid';
import { emailsType, reportType } from '../../types/TableTypes';
import { useAppDispatch, useAppSelector } from "../../redux/hooks/hooks";
import ShowReport from "./ShowReport";
import useAxiosRequest from "../../hooks/useAxiosRequest";


type EmailProps = {
  visible: boolean;
  onSelectChange?: (selectedKeys: React.Key[]) => void;
  onClose: () => void;
}

const { Paragraph, Text } = Typography;

export default function Email({ visible, onSelectChange, onClose }: EmailProps) {
  const dispatch = useAppDispatch();
  const { selectedRows, emails, failedReport } = useAppSelector((state) => state.tableExtension);
  const [ccInputVisible, setCcInputVisible] = useState(false);
  const [senderEmail, setSenderEmail] = useState(false);
  const { email: sender } = useAppSelector((state) => state.user);

  const [recipientInput, setRecipientInput] = useState(false);
  const [inputError, setInputError] = useState("");
  const [drawerHeight, setDrawerHeight] = useState<string>('20%');
  const [isResizing, setIsResizing] = useState(false);
  const [width, setWidth] = useState(720);
  const [recipient, setRecipient] = useState<string[]>([]);
  const [ccRecipient, setCcRecipient] = useState<string[]>([]);
  const [newCcEmail, setCcEmail] = useState("");
  const [newRecipient, setNewRecipient] = useState("");
  const [editorData, setEditorData] = useState("");
  const [loading, setLoading] = useState(false);
  const [viewReport, setViewReport] = useState(false);
  const [form] = Form.useForm();

  const { makeRequest } = useAxiosRequest();

  const getEmailColor = (email: string) => {
    return getRandomColor(email);
  };

  useEffect(() => {
    if (emails) {
      form.setFieldsValue({ bcc: emails?.map((bccEmail: emailsType) => bccEmail.email) })
    }
  }, [emails, form])

  const onMouseDown = () => setIsResizing(true);

  const onCloseReport = () => {
    dispatch(setTableExtension({
      failedReport: [],
      successReport: [],
      printData: { to: "", cc: "", sender: '', subject: '', body: '', sentCount: 0, failedCount: 0 }
    }
    ));
    setViewReport(false);
  };

  const onMouseUp = () => setIsResizing(false);
  const setSenderEmailValue = () => setSenderEmail(!senderEmail);

  const handleMaximize = () => {
    const newWidth = width === 2000 ? 720 : 2000;
    const newHeight = newWidth === 2000 ? '10%' : '20%';
    setWidth(newWidth);
    setDrawerHeight(newHeight);
  };

  const handleBccTagClose = (closedTag: string) => {
    const updatedEmails = emails.filter((tag: emailsType) => tag.email !== closedTag);
    dispatch(setEmails(updatedEmails));
    onSelectChange && onSelectChange(selectedRows?.filter((row: any) => updatedEmails.map((item: emailsType) => item.email).includes((row as any).email)).map((row: any) => (row as any).key) || []);
    form.setFieldsValue({ bcc: updatedEmails?.map((bccEmail: emailsType) => bccEmail.email) })
  }

  const handleToTagClose = (closedTag: string) => {
    const updatedEmails = recipient.filter((tag) => tag !== closedTag);
    setRecipient(updatedEmails);
    form.setFieldsValue({ to: updatedEmails });
  };

  const handleCcTagClose = (closedTag: string) => {
    const updatedEmails = ccRecipient.filter((tag) => tag !== closedTag);
    setCcRecipient(updatedEmails);
    form.setFieldsValue({ cc: updatedEmails });
  };

  const handleRecipient = () => {
    if (newRecipient.trim() !== "") {
      if (isEmailValid(newRecipient)) {
        if (!recipient.includes(newRecipient.trim())) {
          setRecipient([...recipient, newRecipient.trim()]);
          setNewRecipient("");
          setRecipientInput(false);
          form.setFieldsValue({ to: [...recipient, newRecipient.trim()] });
          setRecipient([...recipient, newRecipient.trim()]);
        } else {
          setInputError('Email already exists');
        }
      }
      else {
        setInputError('Invalid email address');
      }
    } else {
      setInputError('Email address cannot be empty');
    }
  };

  const handleAddTag = () => {
    if (newCcEmail.trim() !== "") {
      if (isEmailValid(newCcEmail)) {
        if (!ccRecipient.includes(newCcEmail.trim())) {
          setCcRecipient([...ccRecipient, newCcEmail.trim()]);
          form.setFieldsValue({ bcc: [...ccRecipient, newCcEmail.trim()] });
          setCcEmail("");
          setCcInputVisible(false);
          setInputError("");
        } else {
          setInputError('Email already exists');
        }
      } else {
        setInputError('Invalid email address');
      }
    } else {
      setInputError('Email address cannot be empty');
    }
  };

  useEffect(() => {
    const onMouseMoveHandler = (e: MouseEvent) => {
      if (isResizing) {
        const offsetRight =
          document.body.offsetWidth - (e.clientX - document.body.offsetLeft);
        const minWidth = 720;
        if (offsetRight > minWidth) {
          setWidth(offsetRight);
        }
      }
    };

    document.addEventListener("mousemove", onMouseMoveHandler);
    document.addEventListener("mouseup", onMouseUp);

    return () => {
      document.removeEventListener("mousemove", onMouseMoveHandler);
      document.removeEventListener("mouseup", onMouseUp);
    };
  }, [isResizing]);

  const clearForm = () => {
    dispatch(setTableExtension({ emails: [] }));
    setRecipient([]);
    form.resetFields();
    setEditorData("");
    setRecipient([]);
    setCcRecipient([]);
    onSelectChange && onSelectChange([]);
    onClose();
  }

  const notificationDescription = () => {
    return (
      <Flex justify='flex-end'>
        <Button onClick={() => {
          setViewReport(true)
          notification.destroy()
        }}>
          See Report
        </Button>
      </Flex>
    )
  }

  const resendEmails = async () => {
    const failedEmails = failedReport.map((item: reportType) => item.email);
    form.setFieldsValue({ bcc: failedEmails });
    onFinish();
    setViewReport(false);
    message.info('Resending emails...');
  }

  const onFinish = async () => {
    let totalEmails = emails.length;
    let sentCount = 0;
    let notSentCount = 0;
  
    try {
      const values = await form.validateFields();
      const { to, bcc, cc, subject, body } = values;
  
      if (bcc && bcc.length > 0) {
        setLoading(true);
  
        const chunkSize = 100;
        const chunkedBcc = [];
        for (let i = 0; i < bcc.length; i += chunkSize) {
          chunkedBcc.push(bcc.slice(i, i + chunkSize));
        }
  
        for (const chunk of chunkedBcc) {
          const sendBCCMails = chunk.map(async (bccEmail: string) => {
            const user = emails?.find((item: emailsType) => item.email === bccEmail);
            const fullName = user?.name;
            const firstName = fullName;
            let bodyForEach = body;
            const regex = new RegExp('{{name}}', 'g');
            bodyForEach = bodyForEach.replace(regex, firstName);
  
            const composedEmail = {
              to: to,
              subject: subject,
              from: senderEmail ? sender : "trainee@10academy.org",
              cc: cc,
              bcc: bccEmail,
              replyTo: senderEmail ? sender : "trainee@10academy.org",
              html: bodyForEach,
            };
  
            try {
              await makeRequest({
                url: '/api/email/',
                method: 'POST',
                data: composedEmail,
              });
              sentCount++;
            } catch (error) {
              notSentCount++;
            }
          });
  
          await Promise.all(sendBCCMails);
        }
  
        setLoading(false);
        dispatch(setTableExtension({ 
          printData: { 
            to: to, 
            cc: cc, 
            sender: senderEmail ? sender : "trainee@10academy.org", 
            subject: subject, 
            body: body, 
            sentCount: sentCount, 
            failedCount: notSentCount 
          } 
        }));
  
        sentCount > 0 &&
          notification.success({
            message: 'Emails Sent Successfully',
            description: (
              <Flex vertical>
                <Paragraph>{`${sentCount} out of ${sentCount + notSentCount} emails were sent successfully`}</Paragraph>
                {notificationDescription()}
              </Flex>
            ),
            duration: null,
          });
  
        notSentCount > 0 &&
          notification.warning({
            message: 'Your Emails Failed to Send',
            description: (
              <Flex vertical>
                <Paragraph>{`${notSentCount} out of ${sentCount + notSentCount} emails failed to send successfully`}</Paragraph>
                {notificationDescription()}
              </Flex>
            ),
            duration: null,
          });
  
        if (sentCount === totalEmails) {
          totalEmails = 0;
          sentCount = 0;
          notSentCount = 0;
          clearForm();
        }
        onClose();
      } else {
        setLoading(true);
        const composedEmail = {
          to: to,
          subject: subject,
          from: senderEmail ? sender : "trainee@10academy.org",
          cc: cc,
          replyTo: senderEmail ? sender : "trainee@10academy.org",
          html: body,
        };
  
        try {
          await makeRequest({
            url: '/api/email/',
            method: 'POST',
            data: composedEmail,
          });
          setLoading(false);
          clearForm();
          notification.success({
            message: 'Emails Sent Successfully',
            duration: null,
          });
        } catch (error) {
          setLoading(false);
          message.error('Error making the request');
        }
      }
    } catch (errorInfo) {
      setLoading(false);
      message.error('Form validation failed');
    }
  };

  return (
    <>
      <Drawer
        title={
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span>New Email</span>
            <span className="d-flex" style={{ gap: "0.5rem", alignItems: 'center' }}>
              <Switch
                checkedChildren={sender.split('@')[0].charAt(0).toUpperCase() + sender.split('@')[0].slice(1)}
                unCheckedChildren={"trainee@10academy.org".split('@')[0].charAt(0).toUpperCase() + "trainee@10academy.org".split('@')[0].slice(1)}
                value={senderEmail}
                onChange={setSenderEmailValue}
              />
              <Button
                type='text'
                style={{ border: 'none' }}
                icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
                onClick={handleMaximize}
              >
              </Button>
            </span>
          </div>
        }
        style={{ top: drawerHeight, overflowY: 'scroll', height: "90%" }}
        placement="right"
        closable={true}
        onClose={onClose}
        open={visible}
        width={width}
        className='email-drawer'
      >
        <div
          style={{
            position: "absolute",
            width: "5px",
            padding: "4px 0 0",
            top: 0,
            left: 0,
            bottom: 0,
            zIndex: 100,
            cursor: "ew-resize",
            backgroundColor: "#ddd"
          }}
          onMouseDown={onMouseDown}
        />
        <Form className="email-form" form={form} onFinish={onFinish} style={{ overflow: "scroll", marginBottom: "5rem" }} >
          <Spin spinning={loading} tip="Sending...">
            <Form.Item
              label="To: "
              name="to"
              style={{ padding: "0 0 0.5rem 0", maxHeight: '100px', overflowY: 'auto' }}
              rules={[{ required: true, message: 'Please enter the recipient' }]}
            >
              {recipient.map((email) => (
                <Tag
                  key={email}
                  closable
                  onClose={() => handleToTagClose(email)}
                  style={{ backgroundColor: getEmailColor(email).backgroundColor, color: getEmailColor(email).textColor, fontSize: "1rem", margin: "0.2rem", padding: "0.2rem" }}
                >
                  {email}
                </Tag>
              ))}
              {recipientInput ? (
                <>
                  <Input
                    style={{
                      width: "100%",
                      padding: "0.2rem",
                      fontSize: "1rem",
                      border: "0",
                      boxShadow: "none",
                      borderRadius: "0",
                      borderBottom: "1px solid #ddd",
                    }}
                    placeholder='Enter Recipient'
                    value={newRecipient}
                    onChange={(e) => {
                      setNewRecipient(e.target.value);
                      setInputError("");
                    }}
                    onPressEnter={handleRecipient}
                    onBlur={() => {
                      if (newRecipient.trim() !== "" && !isEmailValid(newRecipient)) {
                        setInputError('Invalid email address');
                      }
                      setRecipientInput(false);
                    }}
                    type='email'
                  />
                  <div style={{ color: 'red' }}>{inputError}</div>
                </>
              ) : (
                <Tag
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: "0.5rem",
                    width: "20%",
                    cursor: "pointer",
                    padding: "0.2rem",
                    borderStyle: 'dashed'
                  }}
                  icon={<PlusCircle />}
                  onClick={() => setRecipientInput(true)}
                >
                  Add Recipient
                </Tag>
              )}
            </Form.Item>
            <Divider style={{ margin: "0.8rem" }} />
            <Form.Item
              label="CC: "
              name="cc"
              style={{ padding: "0 0 0.5rem 0", maxHeight: '100px', overflowY: 'auto' }}
            >
              {ccRecipient.map((email) => (
                <Tag
                  key={email}
                  closable
                  onClose={() => handleCcTagClose(email)}
                  style={{ backgroundColor: getEmailColor(email).backgroundColor, color: getEmailColor(email).textColor, fontSize: "1rem", margin: "0.2rem", padding: "0.2rem" }}
                >
                  {email}
                </Tag>
              ))}
              {ccInputVisible ? (
                <>
                  <Input
                    style={{
                      width: "100%",
                      padding: "0.2rem",
                      fontSize: "1rem",
                      border: "0",
                      boxShadow: "none",
                      borderRadius: "0",
                      borderBottom: "1px solid #ddd",
                    }}
                    placeholder='Enter Recipient'
                    value={newCcEmail}
                    onChange={(e) => {
                      setCcEmail(e.target.value);
                      setInputError("");
                    }}
                    onPressEnter={handleAddTag}
                    onBlur={() => {
                      if (newCcEmail.trim() !== "" && !isEmailValid(newCcEmail)) {
                        setInputError('Invalid email address');
                      }
                      setCcInputVisible(false);
                    }}
                    type='email'
                  />
                  <div style={{ color: 'red' }}>{inputError}</div>
                </>
              ) : (
                <Tag
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: "0.5rem",
                    width: "20%",
                    padding: "0.2rem",
                    cursor: "pointer",
                    borderStyle: 'dashed'
                  }}
                  icon={<PlusCircle />}
                  onClick={() => setCcInputVisible(true)}
                >
                  Add Recipient
                </Tag>
              )}
            </Form.Item>
            {emails.length > 0 && (
              <>
                <Divider style={{ margin: "0.8rem" }} />
                <Form.Item
                  label="Bcc: "
                  name="bcc"
                  style={{ padding: "0 0 0.5rem 0", maxHeight: '100px', overflowY: 'auto' }}
                >
                  {emails?.map((bccEmail: emailsType) => (
                    <Tag
                      key={bccEmail.email}
                      closable
                      // onChange={emails.map((bccEmail: emailsType) => bccEmail.email)}
                      onClose={() => handleBccTagClose(bccEmail.email)}
                      style={{ backgroundColor: getEmailColor(bccEmail.email).backgroundColor, color: getEmailColor(bccEmail.email).textColor, fontSize: "1rem", margin: "0.2rem", padding: "0.2rem" }}
                    >
                      {bccEmail.email}
                    </Tag>
                  ))}
                </Form.Item>
                <Text className="d-flex flex-end">{`${emails.length} ${emails.length === 1 ? "email" : "emails"} ${emails.length === 1 ? "is" : "are"} selected`}</Text>
              </>
            )}
            <Divider style={{ margin: "0.8rem" }} />
            <Form.Item
              label="Subject: "
              name="subject"
              rules={[{ required: true, message: 'Please enter the subject' }]}>
              <Input
                style={{
                  border: "0",
                  boxShadow: "none",
                  borderRadius: "0",
                  borderBottom: "1px solid #ddd",
                }}
              />
            </Form.Item>
            <Divider style={{ margin: "0.8rem" }} />
            <Form.Item
              label="Sender"
              style={{ padding: "0 0 0.5rem 0", maxHeight: '100px', overflowY: 'auto' }}
            >
              <Input
                style={{
                  width: "fit-content",
                  padding: "0.2rem",
                  fontSize: "1rem",
                  border: "none",
                  boxShadow: "none",
                }}
                value={`${senderEmail ? sender : "trainee@10academy.org"}`}
                disabled
              />
            </Form.Item>
            <Divider style={{ margin: "0.8rem" }} />
            <Form.Item
              label=""
              name="body"
              rules={[{ required: true, message: 'Please enter the body' }]}
              className="ck-body"
            >
              <CKEditor
                editor={ClassicEditor as any}
                config={{
                  toolbar: {
                    items: [
                      'heading', '|',
                      'bold', 'italic', 'link', '|',
                      'outdent', 'indent', '|',
                      'bulletedList', 'numberedList', '|',
                      'insertTable', 'tableColumn', 'tableRow', 'mergeTableCells', '|',
                      'blockQuote', '|',
                      'mediaEmbed', '|',
                      'undo', 'redo'
                    ],
                    shouldNotGroupWhenFull: true
                  }
                }}

                data={editorData}
                onChange={(_event, editor: any) => {
                  const data = editor.getData();
                  setEditorData(data);
                  form.setFieldsValue({ body: data });
                }}
              />
            </Form.Item>
            <Divider style={{ margin: "0.8rem" }} />
            <Form.Item>
              <Button
                loading={loading}
                style={{
                  float: "right",
                  paddingRight: "1rem"
                }}
                htmlType="submit">
                Send
              </Button>
            </Form.Item>
          </Spin>
        </Form>

      </Drawer>
      {
        viewReport && <ShowReport viewReport={viewReport} onCloseReport={onCloseReport} resendEmails={resendEmails} />
      }
    </>
  )
}