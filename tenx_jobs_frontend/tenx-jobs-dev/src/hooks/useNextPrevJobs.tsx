import { CSSProperties } from 'react';
import { LeftOutlined, RightOutlined } from '@ant-design/icons';

interface ArrowProps {
  className?: string;
  style?: CSSProperties;
  onClick?: () => void;
}

const useNextPrevJobs = () => {
  const PrevArrow = ({ className, style, onClick }: ArrowProps) => (
    <LeftOutlined
      className={className}
      style={{ 
        ...style, 
        display: 'block', 
        color: '#000000A6', 
        fontSize: '20px', 
        opacity: 0.5 
      }}
      onClick={onClick}
    />
  );

  const NextArrow = ({ className, style, onClick }: ArrowProps) => (
    <RightOutlined
      className={className}
      style={{ 
        ...style, 
        display: 'block', 
        color: '#000000A6', 
        opacity: 0.5, 
        fontSize: '20px', 
        padding: '8px' 
      }}
      onClick={onClick}
    />
  );

  return { PrevArrow, NextArrow };
};

export default useNextPrevJobs;
