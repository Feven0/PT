import { useMemo } from 'react';
import { Avatar } from 'antd';
import { DownloadOutlined, ExpandAltOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { IoIosLink } from 'react-icons/io';
import { ensureURLProtocol } from "../utils/isUrl";
import { useAppSelector } from "../redux/hooks/hooks";

const useRenderIcon = () => {
  const {role} = useAppSelector((state) => state.user);
  return useMemo(
    () => (icon: { type: string; source: string; icon: string }, data: string, record: any) => {
      const dataSource = record[icon.source];
      if(data === "" || 
        data === undefined || 
        data === null || 
        data === "NA" || 
        data === "NOT SPECIFIED" || 
        data==="None" || 
        data==="null" || 
        data==="-" ||
        data==="started") {
        return "--";
      }
      switch (icon.type) {
        case 'with_text':
          if (icon.icon === 'first-letter') {
            return <Avatar size="small">{data.charAt(0).toUpperCase()}</Avatar>;
          }
          return data;
        case 'icon_only':
          if (icon.icon === 'download') {
            return (
              <a href={ensureURLProtocol(data)} target="_blank" rel="noopener noreferrer">
                <DownloadOutlined />
              </a>
            );
          } else if (icon.icon === 'expand') {
            let url = '';
            if(role==='Staff'){
              url = `/staff/trainee-reactions/${dataSource}`;
            }else if(role==='Trainee'){
              url = `/trainee/match-detail/${dataSource}`;
            }
            return (
              <Link to={url}>
                <ExpandAltOutlined />
              </Link>
            );
          } else if (icon.icon === 'link') {
            return (
              <a href={ensureURLProtocol(data)} rel="noreferrer" target="_blank">
                <IoIosLink />
              </a>
            );
          }
          return data;
        default:
          return data;
      }
    },
    []
  );
};

export default useRenderIcon;
