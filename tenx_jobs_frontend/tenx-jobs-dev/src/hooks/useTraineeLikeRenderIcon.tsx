import { Avatar } from 'antd';
import { DownloadOutlined, ExpandAltOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { IoIosLink } from 'react-icons/io';

interface IconType {
  type: string;
  source: string;
  icon: string;
}


const useTraineeLikeRenderIcon = (allUserId: string | number | null | undefined, user_profile_id: string, handleClick: (data: string, record: any) => void) => {

  const renderIcon = (icon: IconType, data: string, record: any) => {
    const dataSource = record[icon.source];

    switch (icon.type) {
      case 'with_text':
        if (icon.icon === 'first-letter') {
          return <Avatar size="small">{data.charAt(0).toUpperCase()}</Avatar>;
        }
        return data;

      case 'icon_only':
        switch (icon.icon) {
          case 'download':
            return <DownloadOutlined />;
          case 'expand':
            {
            const url = `/trainee/trainee_engagements/${allUserId}/${user_profile_id}/${dataSource}`;
            return (
              <Link to={url}>
                <ExpandAltOutlined />
              </Link>
            );
          }
          case 'link':
            return (
              <div
                onClick={() => handleClick(data, record)}
                style={{ display: 'inline-block', cursor: 'pointer' }}
              >
                <IoIosLink className="dark-orange-color" />
              </div>
            );
          default:
            return data;
        }
      default:
        return data;
    }
  };

  return {
    renderIcon,
  };
};

export default useTraineeLikeRenderIcon;
