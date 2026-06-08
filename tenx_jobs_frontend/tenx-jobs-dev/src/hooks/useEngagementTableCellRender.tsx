import { useCallback } from 'react';
import { Tag } from 'antd';
import { IoIosLink } from 'react-icons/io';
import { ReactNode } from 'react';
import { getRandomColor } from "../utils/commonUtils";
import { ensureURLProtocol, isURL } from "../utils/isUrl";

type RenderTableCellType = {
  dtype: string;
  format?: string;
  source?: string;
};

const useEngagementTableCellRender = () => {

  const renderTableCell = useCallback((type: RenderTableCellType, data: any, icon: ReactNode = <IoIosLink />) => {
    if (data === "" || 
      data === undefined || 
      data === null || 
      data === "NA" || 
      data === "NOT SPECIFIED") {
      return "--";
    }

    if (!type) {
      return data;
    }

    switch (type.dtype) {
      case 'tag_list': {
        const tags = data.split(',').map((tag: string) => tag.trim());
        return (
          <>
            {tags.map((tag: string) => {
              const color = getRandomColor();
              return (
                <Tag color={color} key={tag}>
                  {tag.toUpperCase()}
                </Tag>
              );
            })}
          </>
        );
      }
      case 'datetime': {
        const date = new Date(data);
        if (type.format === "YYYY-MM-DD") {
          return date.toISOString().split('T')[0];
        }
        return date.toLocaleDateString('en-US', {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric',
        });
      }
      case 'link':
        if (isURL(data)) {
          return (
            <a href={ensureURLProtocol(data)} rel="noreferrer" target="_blank">
              {icon}
            </a>
          );
        }
        return data;

      case 'string':
        if (data === 'user_profile_id' || data === 'job_profile_id' || data === 'all_user') {
          return null;
        }
        return data;

      case 'HTML':
        return <div dangerouslySetInnerHTML={{ __html: data }} />;
      default:
        return data;
    }
  }, []);

  return {
    renderTableCell
    };
};

export default useEngagementTableCellRender;
