import React, { forwardRef, ReactNode } from 'react';
import { Col, Divider, Row, Tag, Tooltip } from 'antd';
import { ClockCircleOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';

// Components
import EmptyJobHandler from "../commonComponents/EmptyJobHandler";
import TagComponent from "../commonComponents/Tag";

// Types
import { PageHeader } from "../../types/Jobs";
import { T_PageTags, T_PageTagsValue, TJopCardExpPages } from "../../types/expandReactionTypes";

// Styles
import '../../styles/slidingCard.css';

type SliderProps = {
  job: TJopCardExpPages;
  transitioning: boolean;
  skipCard?: boolean;
  ref: React.RefObject<HTMLDivElement>;
};

const SliderJob = forwardRef<HTMLDivElement, SliderProps>(({ job, transitioning, skipCard }, ref) => {
  const formatHeaderString = (headers: PageHeader[]) => {
    if (headers.length === 0) {
      return '';
    }
    const isDate = (str: string) => {
      return /\b(?:\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{2}\/\d{2}\/\d{4})\b/.test(str);
    };

    const elements: ReactNode[] = [];
    headers.forEach((header, index: number) => {
      if (header.description.toLowerCase().includes('date') || isDate(header.value)) {
        elements.push(
          <span key={index} className="job-end-date">
            <ClockCircleOutlined /> End date: {header.value}
          </span>
        );
      } else {
        elements.push(<span key={index}>{header.value}</span>);
      }
      if (index < headers.length - 1) {
        elements.push(<span key={`separator-${index}`}>{index === 0 ? ' | ' : ', '}</span>);
      }
    });
    return elements;
  };

  // Remove new lines and add double spaces to allow line breaks in markdown
  const preprocessMarkdown = (markdown: string): string => {
    let processedMarkdown = markdown.replace(/\n/g, '  \n');
    processedMarkdown = processedMarkdown.replace(
      /\[([^\]]*)\]/g,
      (_match, p1) => {
        return p1.split(', ').map((item: string) => `<span class="highlight">${item.replace(/'/g, '')}</span>`).join(', ');
      }
    );
    return processedMarkdown;
  };

  const processedValue = preprocessMarkdown(job.page_body.value);

  if (!job) return <EmptyJobHandler title="No Job Found" description="No job found for the selected job." />;

  return (
    <div ref={ref} className={`page-container ${transitioning ? 'turn' : ''} ${skipCard ? 'skipCard-item' : ''}`}>
      <Row gutter={16} className="mb-16 page-content">
        <Col xs={24} lg={job.page_tags.length > 0 ? 15 : 24}>
          <span className="job-body-titles">{formatHeaderString(job.page_header)}</span>
          <div className={`mt-16 ${transitioning ? 'fade-out' : 'fade-in'}`}>
            <span className="job-body-titles mt-16">{job.page_body.title} </span>
            {
              job.page_body.type === 'summary' || job.page_body.type === 'competency' ? 
                <ReactMarkdown
                  className="pre-line"
                  children={processedValue}
                  rehypePlugins={[rehypeRaw]}
                  remarkPlugins={[remarkGfm]} 
                /> :
                <Tag>{job.page_body.value}</Tag>
            }
          </div>
        </Col>
        <Col xs={0} lg={job.page_tags.length > 0 ? 1 : 0}>
          <Divider type="vertical" style={{ height: "100%" }} />
        </Col>
        {job.page_tags && job.page_tags.length > 0 && (
          <Col xs={job.page_tags.length > 0 ? 24 : 0} lg={job.page_tags.length > 0 ? 8 : 0}>
            {job.page_tags.map((tagGroup: T_PageTags, index: number) => (
              <div key={index} className={`mt-16 ${transitioning ? 'fade-out' : 'fade-in'}`}>
                {tagGroup.value.length > 0 && 
                  <span className="pre-line job-body-titles mt-16">{tagGroup.title}</span>}
                <div className="mt-8 gap-8">
                  {tagGroup.value.map((tag: T_PageTagsValue, tagIndex: number) => {
                    const phrases = tag.name.split(',').map(phrase => phrase.trim());
                    return phrases.map((phrase, phraseIndex) => (
                      <Tooltip title={tag.score} key={`${tagIndex}-${phraseIndex}`}>
                        <TagComponent ref={ref} type={tag.type ?? 'neutral10'} text={phrase} />
                      </Tooltip>
                    ));
                  })}
                </div>
              </div>
            ))}
          </Col>
        )}
      </Row>
    </div>
  );
});

SliderJob.displayName = 'SliderJob';

export default SliderJob;
