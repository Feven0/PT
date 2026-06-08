import { useMediaQuery } from "react-responsive";
import { Row, Col, Card, Button, Avatar, Divider, Table, Tooltip, Dropdown, Radio, Input, Form, message, Switch, Popconfirm, Select, Tabs, Collapse } from "antd";
import { StarOutlined, StarFilled, HeartFilled, HeartOutlined, QuestionCircleOutlined, LikeOutlined, DislikeOutlined, DislikeFilled, LikeFilled } from '@ant-design/icons';
import { useState, useEffect, useRef } from "react";
import { IoSendSharp } from "react-icons/io5";
import type { MenuProps } from 'antd';
import { useNavigate } from "react-router-dom";
import Slider from 'react-slick';
import type { TabsProps } from 'antd';
import type { CollapseProps } from 'antd';

// Components
import SliderJob from "./SliderJob";
import JobLoading from "../commonComponents/JobLoading";
import ServerError from "../commonComponents/ServerError";
import TraineeStats from "./Stats";
import useActionHandler from "../../hooks/useActionHandlers";
import useJobHeaderHandler from "../../hooks/useJobHeaderHandler";
import useNextPrevJobs from "../../hooks/useNextPrevJobs";
import AddNewJob from "./AddNewJob";
import NoJobsAvailable from "../commonComponents/NoJobsAvailable";
import StaffDataLoader from "../commonComponents/StaffDataLoader";

// Redux and custom hooks
import { useAppDispatch, useAppSelector } from "../../redux/hooks/hooks";
import { setUserProfileId } from "../../redux/slices/userSlices";
import { resetCheckedValue, setCheckedValue, setFeedbackText } from "../../redux/slices/experienceSlice";
import { setCards, setRedisListId } from "../../redux/slices/jobCardSlice";
import { setUserState } from "../../redux/slices/userStatsSlice";
import { setUserJobMatchId } from "../../redux/slices/leapProfileIdSlice";
import { setReportJobTab } from "../../redux/slices/tabsSlice";
import useAxiosRequest from "../../hooks/useAxiosRequest";

// Static Assets
import { firedAction } from "../../assets";
// Utility function
import { capitalize, checkboxOptions, reportDuplicate, reportStatus, sectionMap } from "../../utils/commonUtils";
import { getRunStage } from "../../utils/getRunStage";

//Styles
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";
import '../../App.css'
import '../../styles/slidingCard.css'

const { TextArea } = Input;

export type ActionState = {
  option: string;
  action: string | null;
}

const run_stage = getRunStage();

export default function AllJobs() {
  const [jobCurr, setJobCurr] = useState(0);
  const [transitioning, setTransitioning] = useState(false);
  const [skipCard, setSkipCard] = useState(false);
  const [response, setResponse] = useState<any>(null);

  const [isJobLiked, setIsJobLiked] = useState(false);
  const [isJobSuperLiked, setIsJobSuperLiked] = useState(false);
  const [skipButtonClicked, setSkipButtonClicked] = useState(false);
  const [showInput, setShowInput] = useState(false);
  const [count, setCount] = useState(5);
  const [isButtonHovered, setIsButtonHovered] = useState(false);
  const [otherReason, setOtherReason] = useState(""); 
  const [jobStatus, setJobStatus] = useState(reportStatus[0].value);
  const [duplicateReason, setDuplicateReason] = useState(reportDuplicate[0].value)

  const ref = useRef<HTMLDivElement>(null);
  
  const { cards: jobProfile, redis_list_id } = useAppSelector((state) => state.jobCard);
  const { user_profile_id, allUserId, user_role } = useAppSelector((state) => state.leapProfileId);
  const { feedbackText, checkedValue } = useAppSelector((state) => state.experience);
  const { move_to, move_from } = useAppSelector((state) => state.updateFilter);
  const { stats } = useAppSelector((state) => state.userStats);
  const {reportJobTab} = useAppSelector((state)=>state.tabs)
  const {days} = useAppSelector((state) => state.updateSince);

  const isMobile = useMediaQuery({ maxWidth: 767 });
  const [form] = Form.useForm();
  const { bubblingOption, isSkipping, actions, handleAction, handleSubmitFeedback, setActions, setIsSkipping } = useActionHandler(form);
  const { PrevArrow, NextArrow } = useNextPrevJobs();
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const isCardView = true;

  const jobPages = jobProfile[0]?.job_card?.pages;
  const jobHeader = jobProfile[0]?.job_card?.header;
  const jobTitle = jobProfile[0]?.job_card?.header.find(header => header.position === 1)?.value;
  const { renderSecondLine } = useJobHeaderHandler(jobHeader);
  const { makeRequest, loading:duplicateLoading, error } = useAxiosRequest()
  const { makeRequest:newRequest, loading, error: fetchErr } = useAxiosRequest()
  const { makeRequest:skipRequest, loading:skipLoading, error: skipErr } = useAxiosRequest()

  const prev = () => {
    setTimeout(() => {
      setJobCurr(jobCurr === 0 ? jobPages.length - 1 : jobCurr - 1);
      setTransitioning(false);
    }, 100);
  }

  const next = () => {
    setTimeout(() => {
      setJobCurr(jobCurr === jobPages.length - 1 ? 0 : jobCurr + 1)
      setTransitioning(false);
    }, 100);
  }

  const sendResult = () => {
    if (allUserId) {  
      makeRequest({
        url: '/sjob/get-user-profile-id',
        method: 'POST',
        data: {
          all_user_id: allUserId,
          profile_type: 'other',
          filter: {},
          run_stage: run_stage,
        },
        onSuccess: (response) => {
          if(response.status === 200) {
            setResponse(response.data);
          }
        },
        onError: () => {},
      });
    }
  };

  useEffect(() => {
    if (!user_profile_id) {
      sendResult();
    }
  }, [user_profile_id])

  useEffect(() => {
    if (response) {
      dispatch(setUserProfileId(response?.user_profile_id));
    }
  }, [response]);

  useEffect(() => {
    if (jobProfile.length > 0) {
      dispatch(setUserJobMatchId(jobProfile[0].match_attributes.user_job_match_id ?? '0'));
    }
  }, []);


  const transformReactions = (attrib: string,  isSkipping: boolean, reason?: string) => {
    return {
      comment: feedbackText || "",  
      user_reaction: reason 
        ? reason  
        : isSkipping 
          ? "I don't want to rate"
          : attrib,
  
      attributes: isSkipping 
        ? [] 
        : actions.map(({ option, action }) => ({
          section: sectionMap[option],
          user_reaction: action
        })),
      
      additional_data: {}
    };
  };
  
  const columns = [
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
                onClick={!isSkipping ? () => handleAction(record.option, 'like') : undefined}
                className={bubblingOption === record.option ? 'bubble' : ''}
                style={{ color: '#6A6A6A', opacity: 0.7 }}
              />
            ) : (
              <LikeOutlined
                onClick={!isSkipping ? () => handleAction(record.option, 'like') : undefined}
                className={bubblingOption === record.option ? 'bubble' : ''}
                style={{ color: 'inherit', opacity: 0.5 }}
              />
            )}
            {action === 'dislike' ? (
              <DislikeFilled
                onClick={!isSkipping ? () => handleAction(record.option, 'dislike') : undefined}
                style={{ color: '#6A6A6A', opacity: 0.7 }}
              />
            ) : (
              <DislikeOutlined
                onClick={!isSkipping ? () => handleAction(record.option, 'dislike') : undefined}
                style={{ color: 'inherit', opacity: 0.5 }}
              />
            )}
          </div>
        );
      },
    },
  ];

  const fetchCardData = () => {
    const data = {
      all_user_id: allUserId,
      user_role: user_role,
      user_profile_id: user_profile_id,
      session_id: '',
      topic_type: 'job',
      resend: false,
      since: days,
      filter: {
        move_to: move_to,
        move_from: move_from,
      },
      run_stage: run_stage,
    };
    newRequest({
      url: '/sjob/get-job-cards',
      method: 'POST',
      data,
      onSuccess: (response) => {
        if (response?.data?.cards) {
          dispatch(setCards(response.data.cards));
          dispatch(setUserState(response.data.stats));
          dispatch(setRedisListId(response.data.redis_id_list[0]));
          setTimeout(() => {
          }, 5000);
        }
      },
      onError: () => {},
    });
  };
  const data = checkboxOptions.map(option => ({ key: option, option }));
  const handleRadioClick = (key: string) => dispatch(setCheckedValue(key));

  // Handle skip job action
  const handleSkipAction = (reason?: string) => {
    const reactionProfile = isSkipping 
    ? transformReactions("", true, reason)
    : transformReactions(checkedValue, false, reason)
    const postData = {
      all_user_id: allUserId,
      jop_profile_id: jobProfile[0].job_profile_id,
      redis_id: redis_list_id,
      user_profile_id: user_profile_id,
      reaction_profile: reactionProfile,
      job_profile: {},
      run_stage: run_stage
    };
    setSkipButtonClicked(true)
    skipRequest({
      url: '/sjob/post-user-reaction',
      method: 'POST',
      data: postData,
      onSuccess: (response) => {
        if (response.status === 200) {
          setSkipCard(true);
          setJobCurr(0);
          setActions(checkboxOptions.map(option => ({ option, action: null })));
          fetchCardData();
          setIsSkipping(false);
          setTimeout(() => {
            setSkipCard(false);
          }, 1000);
          dispatch(resetCheckedValue());
          dispatch(setFeedbackText(''));
        }
      },
      onError: () => {
        setIsSkipping(false);
      },
    });
    
  }

  // Post user like reaction
  const handleHeartClick = () => {
    const postData = {
      all_user_id: allUserId,
      jop_profile_id: jobProfile[0].job_profile_id,
      user_profile_id: user_profile_id,
      redis_id: redis_list_id,
      reaction_profile: transformReactions("like", false),
      job_profile: {},
      run_stage: run_stage
    };
    makeRequest({
      url: '/sjob/post-user-reaction',
      method: 'POST',
      data: postData,
      onSuccess: (response) => {
        if (response.status === 200) {
          setActions(checkboxOptions.map(option => ({ option, action: null })));
          fetchCardData();
          setIsJobLiked(true);
          setJobCurr(0);
          setTimeout(() => {
            setIsJobLiked(false);
          }, 5000);
          dispatch(setFeedbackText(''));
        } 
      },
      onError: () => {},
    });
  };

  // Post user super-like reaction
  const handleSuperLikeClick = () => {
    const postData = {
      all_user_id: allUserId,
      jop_profile_id: jobProfile[0].job_profile_id,
      user_profile_id: user_profile_id,
      redis_id: redis_list_id,
      reaction_profile: transformReactions("super_like", false),
      job_profile: {},
      run_stage: run_stage
    };
    makeRequest({
      url: '/sjob/post-user-reaction',
      method: 'POST',
      data: postData,
      onSuccess: (response) => {
        if (response.status === 200) {
          setActions(checkboxOptions.map(option => ({ option, action: null })));
          fetchCardData();
          setIsJobSuperLiked(true);
          setJobCurr(0);
          setTimeout(() => {
            setIsJobSuperLiked(false);
          }, 5000);
          dispatch(setFeedbackText(''));
        } 
      },
      onError: () => {},
    });
  };

  const isButtonActive = actions.some(action => action.action !== null);

  // Format skip job menu items
  const items: MenuProps['items'] = [
    {
      key: 'not_interested',
      label: (
        <Radio
          checked={checkedValue === 'not_interested'}
          onChange={() => handleRadioClick('not_interested')}>
          Not Interested
        </Radio>
      ),
    },
    {
      key: 'not_this_but_fits',
      label: (
        <Radio
          checked={checkedValue === 'not_this_but_fits'}
          onChange={() => handleRadioClick('not_this_but_fits')}>
          Not This But Fits
        </Radio>
      ),
    },
    {
      key: 'not_this_and_all_like_this',
      label: (
        <Radio
          checked={checkedValue === 'not_this_and_all_like_this'}
          onChange={() => handleRadioClick('not_this_and_all_like_this')}>
          Not This and All Like This
        </Radio>
      ),
    },
  ];

  const handleShowInput = () => {
    setShowInput(true);
    dispatch(setFeedbackText(feedbackText));
    form.setFieldValue('feedback', feedbackText);
  };

  const handleSubmit = () => {
    if (feedbackText.trim() !== '') {
      handleSubmitFeedback(feedbackText.trim());
    }
    dispatch(setFeedbackText(feedbackText));
    setShowInput(false);
    form.resetFields();
  }

  const handleMatchDetail = () => {
    navigate(`/trainee/match-detail/${jobProfile[0].job_profile_id}`);
  }

  const settings = {
    dots: false,
    infinite: true,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    initialSlide: jobCurr,
    nextArrow: <NextArrow onClick={next} className="next-job-arrow" />,
    prevArrow: <PrevArrow onClick={prev} />,
    afterChange: (current: number) => {
      setJobCurr(current);
    },
  };

  const handleMouseEnter = () => {
    if (!isButtonActive) {
      setIsButtonHovered(true);
    }
  };

  const onCardMouseEnter = () => setIsButtonHovered(false);
  const onSwitchChange = (checked: boolean) => setIsSkipping(checked);
  const handleReportingJobChange = (value: string) => setJobStatus(value);
  const handleDuplicateChange = (value: string) => setDuplicateReason(value)

  const onFinish =  () => {
    const reason = jobStatus === 'other' ? otherReason : jobStatus;
    const data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      job_profile_id: [jobProfile[0].job_profile_id],
      reason: reason,
    }
     makeRequest({
      url: '/sjob/post-report-invalid-job',
      method: 'POST',
      data,
      onSuccess: (response) => {
        if (response.status === 200) {
          handleSkipAction(reason);
        } 
      },
      onError: () => { },
    });
  }

  const onDuplicateSubmit =  () => {  
    const data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      job_profile_id: jobProfile[0].job_profile_id,
      reason: duplicateReason,
    }
    makeRequest({
      url: '/sjob/post-report-duplicate-job',
      method: 'POST',
      data,
      onSuccess: (response) => {
        if (response.status === 200) {
          handleSkipAction(duplicateReason);
        } 
      },
      onError: () => {},
    }); 
  }

  const onChange = (key: string) =>dispatch(setReportJobTab(key))

  const tabItems: TabsProps['items'] = [ 
    {
      key: '1',
      label: 'Invalid',
      children:  <Row gutter={16}>
      <Col span={24}>
        <Form form={form} 
          layout="vertical" 
          initialValues={{
            job_status: reportStatus[0].value, 
          }}
          className="mt-16">
          <Form.Item
                className="mt-16"
                name="job_status"
                label="Reason for Reporting"
                rules={[{ required: true, message: 'Please select match status' }]}
              >
                <Select
                      placeholder="Select reason" 
                      defaultActiveFirstOption={true}
                      onChange={handleReportingJobChange}>
                    {reportStatus.map((status) => (
                        <Select.Option key={status.value} value={status.value}>
                            {status.display}
                        </Select.Option>
                    ))}
                </Select>
              </Form.Item>
              {jobStatus === 'other' && (
                <Form.Item
                  name="other_reason"
                  label="Please specify"
                  rules={[{ required: true, message: 'Please provide details for the "Other" reason' }]}
                >
                  <Input
                    placeholder="Enter your reason"
                    value={otherReason}
                    onChange={(e) => setOtherReason(e.target.value)}
                  />
                </Form.Item>
              )}
              <Form.Item
                className="flex-center gap-16"
              >
                <Popconfirm
                  title="Are you sure you want to report this job?"
                  onConfirm={onFinish}
                  onCancel={() => {
                    message.info("Reporting cancelled");
                  }}
                  okText="Yes"
                  cancelText="No"
                  className="flex-center gap-16"
                >
                  <Button
                    className="dark-orange-bg white-color"
                    disabled={loading || skipLoading}
                    loading={duplicateLoading}
                  >
                    Report
                  </Button>
                </Popconfirm>
              </Form.Item>
        </Form>
      </Col>
  </Row>
    },
    {
      key: '2',
      label: 'Duplicate',
      children: <Row gutter={16}>
      <Col span={24}>
        <Form form={form} 
          layout="vertical" 
          initialValues={{
            duplicate: reportDuplicate[0].value, 
          }}
          className="mt-16">
          <Form.Item
                className="mt-16"
                name="duplicate"
                label="When Did You Find This Job?"
                rules={[{ required: true, message: 'Please select match status' }]}
              >
                <Select
                      placeholder="Select reason" 
                      defaultActiveFirstOption={true}
                      onChange={handleDuplicateChange}>
                    {reportDuplicate.map((status) => (
                        <Select.Option key={status.value} value={status.value}>
                            {status.display}
                        </Select.Option>
                    ))}
                </Select>
              </Form.Item>
              <Form.Item
                className="flex-center gap-16"
              >
                <Popconfirm
                  title="Are you sure you want to report this job?"
                  onConfirm={onDuplicateSubmit}
                  onCancel={() => {
                    message.info("Reporting cancelled");
                  }}
                  okText="Yes"
                  cancelText="No"
                  className="flex-center gap-16"
                >
                  <Button
                    className="dark-orange-bg white-color"
                    disabled={loading || skipLoading}
                    loading={(duplicateLoading)}>
                    Report
                  </Button>
                </Popconfirm>
              </Form.Item>
        </Form>
      </Col>
  </Row>
    },
  ];

  const collapseItems: CollapseProps['items'] = [
    {
      key: '1',
      label: 'Report Job',
      children: <Tabs defaultActiveKey={reportJobTab} className="report__job-tab" items={tabItems} onChange={onChange} />,
    },
  ];

  if (error || fetchErr || skipErr) return <ServerError />
  if (jobProfile.length === 0 && count > 0) {
    return <JobLoading count={count} setCount={setCount} />
  }

  return (
    <Row gutter={16}>
      <Col span={24} className="all-jobs-container-column">
        <TraineeStats stats={stats} source="jobs" />
        <Row gutter={[16, 32]}>
          {
            (jobProfile.length === 0 && count === 0) ? 
            <Col xs={24} lg={16}>
            <NoJobsAvailable title="No Jobs Available"
            description="There are no jobs available at the moment. Please check back later." /> 
            </Col> :
          <Col xs={24} lg={16} className="start-page-job-card-container">
            {!(duplicateLoading || loading || skipLoading)  ? (
              <Card className={`job-card ${isJobLiked ? "job-liked" : ""} ${isJobSuperLiked ? "job-super-liked" : ""} ${isCardView ? "card-view" : ""}`}
                title={
                  <div className="flex-end gap-8">
                  </div>
                }>
                <div className="pl-16 pr-16">
                  <div className="flex-column">
                      <span className="job-title">{jobTitle}</span>
                  </div>
                  <div className="flex gap-8 mt-8">
                    <Avatar shape="square" size="small">
                      {jobProfile[0]?.company_name?.charAt(0).toUpperCase()}
                    </Avatar>  <span style={{ marginRight: "8px" }}> {capitalize(jobProfile[0]?.company_name)} {"|"}</span>
                    <div>{renderSecondLine()}</div>
                  </div>
                </div>
                <Divider />
                <Slider {...settings}
                  className="job-slider-wrapper">
                  {jobPages?.map((job, index) => (
                    <div key={index}>
                      <SliderJob
                        ref={ref}
                        key={job.id}
                        job={job}
                        transitioning={transitioning}
                        skipCard={skipCard}
                      />
                    </div>
                  ))}
                </Slider>
                <div className="carousel-indicators">
                  <div className="d-flex-center gap-8">
                    {jobPages?.map((_, i) => (
                      <div
                        key={i}
                        className={`carousel-indicator ${jobCurr === i ? 'carousel-indicator-active' : ''}`}
                      />
                    ))}
                  </div>
                </div>
                {
                  skipCard && <div className="skipped-card-container">
                    <Button className="job-action-button skipped-button width-4 height-4">
                      Skipped
                    </Button>
                    <span className="d-flex-center skipped-text">Skipped</span>
                  </div>
                }
                {
                  isJobLiked && <div className="skipped-card-container">
                    <Button
                      className="job-action-button liked-button width-4 height-4"
                      icon={<StarFilled style={{ fontSize: "1.5rem" }} />}
                    />
                    <span className="d-flex-center liked-text">Liked</span>
                  </div>
                }

                {
                  isJobSuperLiked && <div className="skipped-card-container">
                    <div className="flex">
                      <Button
                        className="job-action-button supper-liked-button width-4 height-4">
                        <HeartFilled style={{ fontSize: "2rem" }} />
                      </Button>
                      <Button
                        className="job-action-button supper-liked-fired-button width-4 height-4">
                        <img src={firedAction} alt="supperLike" width={28} />
                      </Button>
                    </div>
                    <span className="d-flex-center supper-matched-text">Super Liked</span>
                  </div>
                }
                <div className={`d-flex-center gap-16 job-action-button-wrapper ${isMobile ? "mobile-action-buttons" : ""}`}>
                  <Dropdown
                    menu={{ items }}
                    placement="bottomRight"
                    arrow
                    disabled={(!isButtonActive && !isSkipping)}
                  >
                    <Tooltip title={(!isButtonActive && !isSkipping) ? "You have to give at least one feedback to continue" : ""}>
                      <div
                        className="d-flex align-items-center"
                        onMouseEnter={handleMouseEnter}
                        style={{ cursor: 'pointer' }}
                      >
                        <Button
                          onClick={()=>handleSkipAction()}
                          className={`job-action-button skip-action-button width-3 height-3 ${skipButtonClicked ? "skippedButtonClicked" : ""}`}
                          disabled={!isButtonActive && !isSkipping}
                        >
                          Skip
                        </Button>
                      </div>
                    </Tooltip>
                  </Dropdown>
                  <Tooltip title={!isButtonActive ? "Like, You have to give at least one feedback to continue" : "Like, You're interested but haven't made a final decision yet. "}>
                    <div onMouseEnter={handleMouseEnter}>
                      <Button
                        className={`job-action-button width-3 height-3 ${!isButtonActive ? "isNotActive" : "isSupperLikeButtonActive"} ${isJobLiked ? "isLiked" : ""}`}
                        style={{
                          border: "1px solid #D9D9D9",
                          color: "#F759AB"
                        }}
                        onClick={handleHeartClick}
                        disabled={!isButtonActive}
                        icon={isJobLiked ?
                          <StarFilled style={{ fontSize: "1.5rem" }} /> :
                          <StarOutlined style={{ fontSize: "1.5rem" }} />}
                      />
                    </div>
                  </Tooltip>
                  <Tooltip title={!isButtonActive ? "Supper Like, You have to give at least one feedback to continue" : "Supper Like, You're very interested and definitely want to apply for the job. If the match score is 60% or higher, application materials will be generated automatically."}>
                    <div onMouseEnter={handleMouseEnter}>
                      <Button className={`job-action-button width-3 height-3 ${!isButtonActive ? "isNotActive" : "isLikeButtonActive"} ${isJobSuperLiked ? "isLiked" : ""}`}
                        disabled={!isButtonActive}
                        onClick={handleSuperLikeClick}>
                        {isButtonActive ? (
                          <HeartOutlined className="font-28" />
                        ) : isJobSuperLiked ? (
                          <HeartOutlined className="font-28" />
                        ) : (
                          <HeartOutlined className="font-28" />
                        )}
                      </Button>
                    </div>
                  </Tooltip>
                </div>

                <div className="detail-button-container flex-end">
                  {
                    jobProfile[0]?.match_attributes?.applyLink && <span><a href={jobProfile[0]?.match_attributes?.applyLink} target="_blank" rel="noreferrer">View Details</a></span>
                  }
                </div>
                {Number(jobProfile[0]?.match_attributes?.overall_match_score) > 0 &&
                  <div className="job-card-match-attribute flex gap-8">
                    <Tooltip title="Shows the percentage match between your profile (skills and attributes) and the job description. Click to view a detailed summary of the match score.">
                      <div className="match-text flex-center gap-8" onClick={handleMatchDetail}>
                        <div className="flex gap-8 match-text-title"><QuestionCircleOutlined />Match Score</div>
                        <span className="match-text-percentage">{jobProfile[0]?.match_attributes?.overall_match_score}%</span>
                      </div>
                    </Tooltip>
                  </div>
                }
              </Card>
            )
              : (
              <Card className="job-card"
                style={{ height: "45vh" }}
                title={
                  <div className="flex-end gap-8">
                  </div>
                }>
                <StaffDataLoader />
              </Card>
              )
            }
          </Col>
        }
          <Col xs={24} lg={8}>
            <Row gutter={16}>
              {
                (jobProfile.length === 0 && count === 0) ? null :
                <Col span={24}>
                  <Card onMouseEnter={onCardMouseEnter}
                    className={`reaction-feedback-card ${(isButtonHovered && !isSkipping) ? "isButtonHovered" : ""}`}
                    title={
                      <Row gutter={8}>
                        <Tooltip title="Please provide your feedback about the job you are seeing. If you like it, what are the elements you like most. If you don’t like it, what does not fit your competency or that you do not like. If you super-like it or have other strong opinions, please use the other field to tell us about it. NOTE THAT your feedback will influence the jobs you see in the future">
                          <Col xs={24} sm={18} style={{
                            overflow: "hidden",
                            flexWrap: "wrap",
                          }}>
                            <div className="flex gap-8" style={{ whiteSpace: "normal", wordWrap: "break-word" }}><QuestionCircleOutlined />
                              What do you like about this job?</div>
                          </Col>
                        </Tooltip>
                        <Col xs={24} sm={6} className="flex-end">
                          <Tooltip title="Toggle this switch on if you do not wish to provide feedback">
                            <Switch checked={isSkipping} onChange={onSwitchChange} />
                          </Tooltip>
                        </Col>
                      </Row>
                    }
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
                                htmlType="submit"
                                icon={<IoSendSharp />}
                              />
                            </Form.Item>
                          </Form>
                        </div>
                      ) : (
                        <div className="d-flex-between">
                          <Button type="text" key="other" onClick={handleShowInput}>
                            Other Feedback
                          </Button>
                        </div>
                      )
                    ]}
                    
                  >
                    <Table columns={columns} dataSource={data} pagination={false} />

                    {
                      (feedbackText?.trim() !== "") && <div className="feedback-text"><span className="feedback-text-title">Comment:</span> {feedbackText}</div>
                    }
                  </Card>
              </Col>
              }
              <Col span={24} className="mt-16" style={{ marginTop: "1rem" }}>
                <AddNewJob />
              </Col>
              {jobProfile.length > 0 &&
                <Col span={24} className="mt-16 report__jobs">
                  <Collapse items={collapseItems} />
              </Col>
              }
            </Row>
          </Col>
        </Row>
      </Col>
    </Row>
  )
}
