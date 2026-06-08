import { useRef, useState } from 'react';
import { Row, Col, Avatar, Flex, Card, List, Button, Radio } from 'antd';
import { LikeOutlined, LikeFilled, DislikeFilled, DislikeOutlined, HeartOutlined, StarOutlined } from '@ant-design/icons';
import Slider from 'react-slick';
import SliderJob from "../../Trainee/SliderJob";
import useJobHeaderHandler from "../../../hooks/useJobHeaderHandler";
import useNextPrevJobs from "../../../hooks/useNextPrevJobs";

import { capitalize } from "../../../utils/commonUtils";
import { TJobCardHeader, TJobPage, TReactionAttribute } from '../../../types/Jobs';
import ApplyStatusForm from './ApplyStatusForm';
import StaffDataLoader from "../../commonComponents/StaffDataLoader";

type TResponseType = {
    response: any;
    refetch: () => void;
    apply_status?: string;
}

export default function EngagementDetailData( {response, refetch}: TResponseType) {
    const ref = useRef<HTMLDivElement>(null);
    const [jobCurr, setJobCurr] = useState(0);
    const { PrevArrow, NextArrow } = useNextPrevJobs();
    const [applyStatusFormVisible, setApplyStatusFormVisible] = useState(false);
    const [transitioning, setTransitioning] = useState(false);
    const [isExpandDetails, setIsExpandDetails] = useState(false);
    const jobPages: TJobPage[] = response?.infocards?.job_profile_card?.job_card?.pages
    const jobHeader = response?.infocards?.job_profile_card?.job_card?.header;
    const jobTitle = response?.infocards?.job_profile_card?.job_card?.header.find((header: TJobCardHeader) => header.position === 1)?.value;
    const companyName = response?.infocards?.job_profile_card?.company_name;
    const matched = response?.infocards?.job_profile_card?.match_attributes?.match_score
    const {reaction_attributes, apply_status, user_reaction} = response?.infocards?.reaction_profile_card || {};
    const { renderSecondLine } = useJobHeaderHandler(jobHeader);
    const idList = {
        user_reaction_id: response?.infocards?.reaction_profile_card?.user_reaction_id,
        job_trainee_id: response?.infocards?.reaction_profile_card?.job_id?.job_trainee_id,
        job_id: response?.infocards?.reaction_profile_card?.job_id,
      };
    const prev = () => {
        setTimeout(() => {
          setJobCurr(jobCurr === 0 ? jobPages.length - 1 : jobCurr - 1);
          setTransitioning(false);
        }, 100);
      }
    
      const next = () => {
        setTimeout(() => {
          jobPages.length
          setJobCurr(jobCurr === jobPages.length - 1 ? 0 : jobCurr + 1)
          setTransitioning(false);
        }, 100);
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


  return (
   <Row gutter={[32,32]}>
    <Col xs={24} md={18} >
        <Card 
         title={
            <>
            <Row  style={{padding: "0.8rem 0"}}>
                <Col span={20} className='d-flex-center'>
                        <div className="d-flex-center gap-8">
                        {jobPages?.map((_, i) => (
                            <div
                            key={i}
                            className={`carousel-indicator ${jobCurr === i ? 'carousel-indicator-active' : ''}`}
                            />
                        ))}
                        </div>
                </Col>
                <Col span={4}>
                    <Flex justify='end'>
                        <p>Matched <span style={{color: "#52C41A"}}>{matched}%</span></p>
                    </Flex>
                </Col>
                
            </Row>
            
            </>
         }
        >
            {!response ? <StaffDataLoader/>:
            <>
            <Flex gap={"0.75rem"} vertical>
                <p className="job-title">{jobTitle}</p>
                <Flex gap={"0.5rem"}>
                    <Avatar shape="square" size="small">
                        {companyName?.charAt(0).toUpperCase()}
                    </Avatar>  <span style={{ marginRight: "8px" }}> {capitalize(companyName)} {"|"}</span>
                    <div>{renderSecondLine()}</div>
                </Flex>
            </Flex>
            <Slider {...settings}
                className="job-slider-wrapper">
                {jobPages?.map((job, index) => (
                <div key={index}>
                    <SliderJob
                        ref={ref}
                        key={job.id}
                        job={job}
                        transitioning={transitioning}
                    />
                </div>
                ))}
            </Slider>
            <Flex justify='end'>
                <a href={reaction_attributes?.applyLink} target='_blank' rel='noopener'>
                    Apply Link
                </a>
            </Flex>
            </>
            }
        </Card>
        {
            user_reaction && (
                <Flex style={{position: "absolute", top: "95%",zIndex: "1", left: "43%", transform: "translate (-50%, -50%"}}>
                    <Button className={"job-action-button width-3 height-3 isLikeButtonActive"}
                        disabled={true} 
                        style={{
                            background: user_reaction && user_reaction === 'super_like' ? "#FA8C16" : user_reaction === "like" ? "#EB2F96" : "#D9D9D9",
                            padding: "0.5rem"
                        }}
                        icon={
                            user_reaction && 
                            user_reaction === 'super_like' ? <HeartOutlined className="engagement-user-reaction" /> 
                            : user_reaction === "like" ? <StarOutlined className="engagement-user-reaction"/> : 
                            <p className="engagement-user-reaction" >Skip</p>}
                    />
                </Flex>
            )
        }
    </Col>
    <Col xs={24} md={6} className='flex flex-column' style={{gap: "1rem"}}>
        <Card
            title="Trainee Reactions" 
            className='engagement-cards'
        >
            <List
                dataSource={reaction_attributes?.reaction_attributes}
                renderItem={(item: TReactionAttribute) => (
                    <List.Item>
                        <List.Item.Meta
                            title={capitalize(item?.section?.split("_").join(" "))}
                        />
                        <Flex gap={"1rem"}>
                            {
                                item?.user_reaction === 'like' ? (
                                <LikeFilled
                                    style={{ color: '#6A6A6A', opacity: 0.7 }}
                                />
                                ):(
                                <LikeOutlined
                                    style={{ color: '#6A6A6A', opacity: 0.7 }}
                                />
                                )
                            }
                            {
                                item?.user_reaction === 'dislike' ? (
                                    <DislikeFilled
                                        style={{ color: '#6A6A6A', opacity: 0.7 }}
                                    />
                                ):(
                                    <DislikeOutlined
                                        style={{ color: '#6A6A6A', opacity: 0.7 }}
                                    />
                                )
                            }
                        </Flex>
                    </List.Item>
                )}
            />
        </Card>
        <Card
            title="Apply Status?" 
            className='engagement-cards'
        >
            <Flex vertical gap={"0.5rem"}>
                <Radio checked style={{width: "100%"}} disabled title='Curren status'>
                    {apply_status}
                </Radio>
                <Button style={{background: "#F5222D", color: "#FFF"}} onClick={() => {
                    setApplyStatusFormVisible(true)
                    setIsExpandDetails(true)
                }}
                >Update</Button>
            </Flex>
        </Card> 
    </Col>
    {
        applyStatusFormVisible && <ApplyStatusForm 
            setVisible={setApplyStatusFormVisible} 
            apply_status={apply_status} 
            refetch={refetch}
            idList={idList}
            isExpandDetails={isExpandDetails}
            setIsExpandDetails={setIsExpandDetails}
           
        />
    }
   </Row>
  )
}
