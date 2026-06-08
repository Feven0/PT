import { useState } from 'react';
import { Row, Col, Card, Table, Form, Button, Input, message, Popconfirm, Tooltip } from "antd";
import { IoSendSharp } from "react-icons/io5";
import { LikeFilled, LikeOutlined, DislikeFilled, DislikeOutlined, QuestionCircleOutlined, DownOutlined } from '@ant-design/icons';
import type { CollapseProps } from 'antd';
import { Collapse } from 'antd';

// Components
import TraineeMatchDetails from "../../components/Trainee/TraineeMatchDetails";
import NoFile from "../../components/commonComponents/NoFile";
import EmptyJobHandler from "../../components/commonComponents/EmptyJobHandler";

// Redux and custom hooks
import { useAppDispatch, useAppSelector } from "../../redux/hooks/hooks";
import { ActionState } from "../../components/Trainee/AllJobs";
import { resetCheckedValue, setFeedbackText } from "../../redux/slices/experienceSlice";

//Styles
import { T_MatchDetails, TMatchAttributesExp } from "../../types/expandReactionTypes";
import useAxiosRequest from "../../hooks/useAxiosRequest";
import { getRunStage } from "../../utils/getRunStage";
import '../../styles/slidingCard.css'

const { TextArea } = Input;

const run_stage = getRunStage();

export default function MatchDetail() {
  const { cards } = useAppSelector((state) => state.jobCard);
  const [bubblingOption, setBubblingOption] = useState<string | null>(null);
  const { feedbackText } = useAppSelector((state) => state.experience);
  const { allUserId, user_job_match_id, user_role } = useAppSelector((state) => state.leapProfileId);
  const [showInput, setShowInput] = useState(false);
  const { makeRequest, loading } = useAxiosRequest(); 
  const [form] = Form.useForm();

  const dispatch = useAppDispatch();

  const transformedMatchDetail: TMatchAttributesExp = {
    ...cards[0]?.match_attributes,
    match_detail: cards[0]?.match_attributes?.match_detail.map((detail: T_MatchDetails, index: number) => ({
      ...detail,
      key: index.toString(),
    }))
  };

  const sectionMap = transformedMatchDetail?.match_detail.reduce((acc: Record<string, string>, detail: T_MatchDetails) => {
    acc[detail.job_competency_name] = detail.job_competency_name;
    return acc;
  }, {});

  const checkboxOptions = sectionMap ? Object.keys(sectionMap) : [];

  const [actions, setActions] = useState<ActionState[]>(checkboxOptions.map(option => ({ option, action: null })));

  const columns = [
    {
      title: 'Job Required Competency',
      dataIndex: 'job_competency_name',
      key: 'job_competency_name',
    },
    {
      title: 'Best Matched User Competency',
      dataIndex: 'best_matched_user_competency',
      key: 'best_matched_user_competency',
    },
    {
      title: 'Match Score',
      dataIndex: 'match_score',
      key: 'match_score',
    },
    {
      title: 'Confidence',
      dataIndex: 'confidence',
      key: 'confidence',
    },
  ];

  const transformReactions = () => {
    const sectionMap = transformedMatchDetail?.match_detail.reduce((acc: Record<string, string>, detail: T_MatchDetails) => {
      acc[detail.job_competency_name] = detail.job_competency_name.toLowerCase().replace(/\s+/g, '_');
      return acc;
    }, {});

    return {
      reaction_attributes: {
        comment: feedbackText ? feedbackText : "",
        attributes: actions.map(({ option, action }) => ({
          section: sectionMap ? sectionMap[option] : undefined,
          user_reaction: action
        }))
      }
    };
  };

  //Set user reactions
  const handleAction = (option: string, action: 'like' | 'dislike' | null) => {
    if (action === 'like') {
      setBubblingOption(option);
    } else if (action === 'dislike') {
      setBubblingOption(null);
    }
    setTimeout(() => setBubblingOption(null), 300);
    setActions(prevActions => {
      const existingAction = prevActions.find(item => item.option === option);
      if (existingAction) {
        const newAction = existingAction.action === action ? null : action;
        return prevActions.map(item =>
          item.option === option ? { ...item, action: newAction } : item
        );
      } else {
        return [...prevActions, { option, action }];
      }
    });
  };

  const column = [
    {
      title: 'Option',
      dataIndex: 'option',
      key: 'option',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: { option: string }) => {
        const action = actions.find(item => item.option === record.option)?.action;
        return (
          <div className="flex gap-16">
            {action === 'like' ? (
              <LikeFilled
                onClick={() => handleAction(record.option, 'like')}
                className={bubblingOption === record.option ? 'bubble' : ''}
                style={{ color: '#6A6A6A', opacity: 0.7 }}
              />
            ) : (
              <LikeOutlined
                onClick={() => handleAction(record.option, 'like')}
                className={bubblingOption === record.option ? 'bubble' : ''}
                style={{ color: 'inherit', opacity: 0.5 }}
              />
            )}
            {action === 'dislike' ? (
              <DislikeFilled
                onClick={() => handleAction(record.option, 'dislike')}
                style={{ color: '#6A6A6A', opacity: 0.7 }}
              />
            ) : (
              <DislikeOutlined
                onClick={() => handleAction(record.option, 'dislike')}
                style={{ color: 'inherit', opacity: 0.5 }}
              />
            )}
          </div>
        );
      },
    },
  ];

  const handleShowInput = () => {
    setShowInput(true);
    dispatch(setFeedbackText(feedbackText));
    form.setFieldValue('feedback', feedbackText);
  };

  const handleSubmit = () => {
    dispatch(setFeedbackText(feedbackText));
    setShowInput(false);
    form.resetFields();

  }

  const handleFeedbackSubmit = () => {
    const reactionData = {
      user_role: user_role,
      all_user_id: allUserId,
      user_job_match_id: user_job_match_id,
      feedback: transformReactions(),
      run_stage: run_stage,
    }
    makeRequest({
      url: '/sjob/post-match-feedback',
      method: 'POST',
      data: reactionData,
      onSuccess: (response) => {
        if (response.status === 200) {
          message.success('Feedback submitted successfully');
          setActions(checkboxOptions.map(option => ({ option, action: null })));
          dispatch(setFeedbackText(''));
          dispatch(resetCheckedValue());
        }
      },
      onError: () => {},
    });
  }

  if (!transformedMatchDetail) {
    <NoFile />
  }

  const data = checkboxOptions.map(option => ({ key: option, option }));
  const hasNonNullAction = actions.some(action => action.action)
  const fullText = "Rate to Agree or Disagree!” Tooltip should be “Please provide your feedback on our matching algorithm. Thumb up for the match score you agree, thumb down otherwise. If you have other feedback, please use the other field to write your opinion or thoughts";
  const shortText = "Do you agree with the competency match analysis?";

  const items: CollapseProps['items'] = [
    {
      key: '1',
      label: <Row gutter={8}>
      <Col span={24} className="flex gap-8">
        <Tooltip title={fullText}>
          <div className="flex-center gap-8">
            <QuestionCircleOutlined />
            <span>{shortText}</span>
          </div>
        </Tooltip>
      </Col>
    </Row>,
      children:  <Card
      className="reaction-feedback-card"
      actions={[
        showInput ? (
          <div className="card-action">
            <Form form={form} onFinish={handleSubmit}>
              <Form.Item name="feedback" className="feedback-input">
                <TextArea
                  rows={2}
                  placeholder="Your feedback here"
                  onChange={(e) => dispatch(setFeedbackText(e.target.value))}
                  style={{ width: "100%" }}
                  maxLength={200}
                />
              </Form.Item>
              <Form.Item className="feedback-submit-button">
                <Button
                  type="text"
                  onClick={handleSubmit}
                  className="dark-orange-bg white-color"
                  icon={<IoSendSharp />}
                />
              </Form.Item>
            </Form>
          </div>
        ) : (
          <Button type="text" key="other" onClick={handleShowInput}>
            Other
          </Button>
        ),
      ]}
    >
      <Table columns={column} dataSource={data} pagination={false} />
      {feedbackText.trim() !== "" && (
        <div className="feedback-text">
          <span className="feedback-text-title">Comment:</span> {feedbackText}
        </div>
      )}
      {(hasNonNullAction || feedbackText?.trim()) && (
        <div className="flex-end mt-32">
          <Popconfirm
            title="Are you sure you want to submit this feedback?"
            onConfirm={handleFeedbackSubmit}
            onCancel={() => {
              message.info("Feedback creation cancelled");
            }}
            okText="Yes"
            cancelText="No"
          >
            <Button loading={loading} className="dark-orange-bg white-color">
              Submit
            </Button>
          </Popconfirm>
        </div>
      )}
    </Card>,
    },
  ];

  return (
    transformedMatchDetail ? (
      <Row
        gutter={16}
        className="match-detail-row-container"
        style={{ marginTop: "3rem" }}
        justify="center"
      >
        <Col xs={24} lg={20} xxl={16} className="match-details-header">
          <div className="d-flex-between">
            <div />
            <span className="match-detail-apply-link">
              <a
                href={transformedMatchDetail?.applyLink}
                target="_blank"
                rel="noopener noreferrer"
              >
                Apply
              </a>
            </span>
          </div>
        </Col>
        <Col xs={24} lg={20} xxl={16} className="mobile-match-details-container">
          <Row gutter={16} justify="center">
            <TraineeMatchDetails
              transformedMatchDetail={transformedMatchDetail}
              columns={columns}
            />
            <Col xs={24} lg={10} className="mt-16" style={{ marginBottom: "3rem" }}>
              <Collapse 
                  items={items}
                  className="reaction__feedback__collapse"
                  expandIconPosition="end"
                  expandIcon={({ isActive }) => <DownOutlined  style={{ transform: isActive ? 'rotate(180deg)' : 'rotate(0deg)' }} />}
                  />
            </Col>
          </Row>
        </Col>
      </Row>
    ) : (
      <Row gutter={16} justify="center">
        <Col xs={24} lg={20} xxl={16} className="mt-16">
          <EmptyJobHandler
            title="No Match details"
            description="You have no match detail for this job!" />
        </Col>
      </Row>
    ))
}
