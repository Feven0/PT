import { useMemo } from 'react';
import { Tag } from 'antd';
import { IoIosLink } from 'react-icons/io';

import { getRandomColor } from "../utils/commonUtils";
import { isURL } from "../utils/extractInitionalts";
import { ensureURLProtocol } from "../utils/isUrl";

const useRenderTableCell = () => {
  return useMemo(
    () => (type: { dtype: string; format: string; source: string }, data: any, icon: React.ReactNode = <IoIosLink />) => {
      if (data === "" || 
          data === undefined || 
          data === null || 
          data === "NA" || 
          data === "NOT SPECIFIED" || 
          data==="None" || 
          data==="null" || 
          data==="started") {
        return "--";
      }
      if (!type) {
        return data;
      }

      if (data === "completed") {
        return <Tag color="green">COMPLETED</Tag>;
      }

      if (data === "scheduled") {
        return <Tag color="pink">SCHEDULED</Tag>;
      }
      if(data === "update_started") {
        return <Tag color="blue">IN PROGRESS</Tag>;
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
          if (type.format === 'YYYY-MM-DD') {
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
                {icon ? icon : <IoIosLink />}
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
    },
    []
  );
};

export default useRenderTableCell;
