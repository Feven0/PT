import { Row, Col, Avatar } from "antd";
import moment from 'moment';
import { useEffect, useState } from "react";

// Utils
import { colors } from "../../utils/colors";
import { extractInitials } from "../../utils/extractInitionalts";

type CommentProps = {
  content: {
    msg: string;
  };
  createdAt: string;
  sender?: string;
};

export default function Comments({ content, createdAt, sender }: CommentProps) {
  const [currentTimestamp, setCurrentTimestamp] = useState<string>('');

  useEffect(() => {
    const updateTimestamp = () => {
      const duration = moment.duration(moment().diff(moment(createdAt)));
      const seconds = duration.asSeconds();
      const minutes = duration.asMinutes();
      const hours = duration.asHours();
      const days = duration.asDays();
      const months = duration.asMonths();
      const years = duration.asYears();

      if (seconds < 60) {
        setCurrentTimestamp('posted just now');
      } else if (minutes < 60) {
        setCurrentTimestamp(`${Math.floor(minutes)} ${Math.floor(minutes) === 1 ? 'minute' : 'minutes'} ago`);
      } else if (hours < 24) {
        setCurrentTimestamp(`${Math.floor(hours)} ${Math.floor(hours) === 1 ? 'hr' : 'hrs'} ago`);
      } else if (days < 30) {
        setCurrentTimestamp(`${Math.floor(days)} ${Math.floor(days) === 1 ? 'day' : 'days'} ago`);
      } else if (months < 12) {
        setCurrentTimestamp(`${Math.floor(months)} ${Math.floor(months) === 1 ? 'month' : 'months'} ago`);
      } else {
        setCurrentTimestamp(`${Math.floor(years)} ${Math.floor(years) === 1 ? 'year' : 'years'} ago`);
      }
    };

    updateTimestamp();
    const interval = setInterval(updateTimestamp, 30000);
    return () => clearInterval(interval);
  }, [createdAt]);

  return (
    <Row gutter={16}>
     <Col span={24}>
        <Row gutter={16}>
          <Col span={2}>
              <Avatar size={32} 
                      style={{ fontSize: "16px", 
                              backgroundColor: colors[(sender?.length ?? 0) % colors.length], 
                              verticalAlign: 'middle' }}
                            >
                  {extractInitials(sender ?? "Unknown")}
                  </Avatar>
          </Col>
          <Col span={22}>
            <div className="flex gap-8 mb-16" style={{flexDirection:"column"}}>
              <div className="flex-center gap-8">
                <span style={{ fontWeight: 'bold' }}>{sender}</span>
                <span style={{ color: 'gray', fontSize: '12px', marginTop:"0.25rem" }}>{currentTimestamp}</span>
              </div>
              <p>{content.msg}</p>
            </div>
          </Col>
        </Row>
      </Col>
  </Row>
  );
}
