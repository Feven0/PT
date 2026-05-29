import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';

export const useRenderTag = () => {
  const renderTagIcon = (priority: string | null) => {
    switch (priority) {
      case "include":
        return <ArrowUpOutlined style={{ color: "green", marginRight: "0.5rem" }} />;
      case "exclude":
        return <ArrowDownOutlined style={{ color: "#FF4405", marginRight: "0.5rem" }} />;
      default:
        return null;
    }
  };

  return { renderTagIcon };
};
