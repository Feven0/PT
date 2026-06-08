import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { RxDotFilled } from 'react-icons/rx'; 

export const useIconRender = () => {
  const renderIcon = (priority: string | null) => {
    switch (priority) {
      case "high":
        return <ArrowUpOutlined style={{ color: "green", marginRight: "0.5rem" }} />;
      case "medium":
        return <RxDotFilled style={{ color: "blue", fontSize: "20px" }} />;
      case "low":
        return <ArrowDownOutlined style={{ color: "#FF4405", marginRight: "0.5rem" }} />;
      default:
        return null;
    }
  };

  return { renderIcon };
};
