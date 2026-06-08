import { Card, Avatar } from 'antd';
import Slider from 'react-slick';
import { useState } from "react";
import { LeftOutlined, RightOutlined } from '@ant-design/icons';

import SliderJob from "../SliderJob";
import { T_ExpandHeader, TProcessedJobCard } from "../../../types/expandReactionTypes";
import EmptyJobHandler from "../../commonComponents/EmptyJobHandler";

type JobTabProps = {
  processedJobCard: TProcessedJobCard;
}

export default function JobDetails ({processedJobCard}: JobTabProps) {
  const [jobCurr, setJobCurr] = useState(0);
  const [transitioning, setTransitioning] = useState(false);
  const isExpandReaction = true;
  const jobPages = processedJobCard.cards?.job_card?.pages;
  const jobHeader = processedJobCard.cards?.job_card?.header;
  const jobTitle = processedJobCard.cards?.job_card?.header.find((header: T_ExpandHeader) => header.position === 1)?.value || "";

  const prev = () => {
    setTimeout(() => {
      setJobCurr(jobCurr === 0 ? jobPages.length - 1 : jobCurr - 1);
      setTransitioning(false);
    }, 500);
  }

  const next = () => {
    setTimeout(() => {
      setJobCurr(jobCurr === jobPages.length - 1 ? 0 : jobCurr + 1)
      setTransitioning(false);
    }, 500);
  }

  const PrevArrow = (props: any) => {
    const { className, style, onClick } = props;
    return (
      <LeftOutlined
        className={className}
        style={{ ...style, display: 'block', color: '#000000A6', fontSize: '20px', opacity: 0.5 }}
        onClick={onClick}
      />
    );
  };
  
  const NextArrow = (props: any) => {
    const { className, style, onClick } = props;
    return (
      <RightOutlined
        className={className}
        style={{
          ...style,
          display: 'block',
          color: '#000000A6',
          opacity: 0.5,
          fontSize: '20px',
          padding: "8px",
        }}
        onClick={onClick}
      />
    );
  };
  
  const settings = {
    dots: true,
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
    appendDots: (dots: any) => (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          padding: '10px',
        }}
      >
        <ul style={{ margin: 0 }}> {dots} </ul>
      </div>
    ),
    customPaging: (i: any) => (
      <div
        style={{
          width: '30px',
          height: '5px',
          background: i === jobCurr ? 'black' : 'lightgray',
          margin: '0 2px',
        }}
      />
    ),
  };
  
  const findHeaderValueByPosition = (position: number) => {
    const header = jobHeader?.find((header: T_ExpandHeader) => header.position === position);
    return header ? header.value : null;
  };
  
  const findHeaderValuesByPosition = (position: number) => {
    return jobHeader?.filter((header: T_ExpandHeader) => header.position === position)
      .map((header:T_ExpandHeader) => header.value);
  };
  
  const capitalize = (str: string) => {
    return str?.charAt(0).toUpperCase() + str?.slice(1).toLowerCase();
  }
  
  const renderSecondLine = () => {
    const header2 = findHeaderValueByPosition(2);
    const headers3 = findHeaderValuesByPosition(3)?.join(', ');
  
    if (header2 && headers3) {
      return `${header2} | ${headers3}`;
    } else if (header2) {
      return header2;
    } else if (headers3) {
      return headers3;
    } else {
      return null;
    }
  };

  return (
    <>
      {processedJobCard ? (
        <Card className={`job-card ${isExpandReaction ? "job-card-expanded-reaction":""}`} title={<div className="flex-end gap-8"></div>}>
          <div className="pl-16 pr-16">
            <div className="flex-column">
              {jobTitle && <span className="job-title">{jobTitle}</span>}
            </div>
            <div className="flex gap-8 mt-8">
              <Avatar shape="square" size="small">
                {processedJobCard.cards?.company_name?.charAt(0).toUpperCase()}
              </Avatar>
              <span style={{ marginRight: "8px" }}>
                {capitalize(processedJobCard.cards?.company_name)} {"|"}
              </span>
              <div>{renderSecondLine()}</div>
            </div>
          </div>
          <Slider {...settings} className="job-slider-wrapper">
            {jobPages?.map((job, index) => (
              <div key={index}>
                <SliderJob
                  job={job}
                  transitioning={transitioning}
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
        </Card>
      ) :<EmptyJobHandler title="No Job details" description="You have no job details"/>
      }
    </>
  );
}

