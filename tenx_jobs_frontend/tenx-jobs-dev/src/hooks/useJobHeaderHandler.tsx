import { useCallback } from 'react';

const useJobHeaderHandler = (jobHeader: any[] | undefined) => {
  const isLink = (value: string): boolean => {
    const urlPattern = /^(http|https):\/\/[^ "]+$/;
    return urlPattern.test(value);
  };

  const findHeaderValueByPosition = useCallback((position: number): string | null => {
    const header = jobHeader?.find(header => header.position === position);
    return header ? header.value : null;
  }, [jobHeader]);

  const findHeaderValuesByPosition = useCallback((position: number): string[] => {
    return jobHeader?.filter(header => header.position === position).map(header => header.value) || [];
  }, [jobHeader]);

  const renderSecondLine = useCallback((): (JSX.Element | string) | null => {
    const header2 = findHeaderValueByPosition(2);
    const headers3 = findHeaderValuesByPosition(3)?.join(', ');

    const renderValue = (value: string): JSX.Element | string => {
      return isLink(value) ? (
        <a href={value} target="_blank" rel="noopener noreferrer">
          {value}
        </a>
      ) : (
        value
      );
    };

    if (header2 && headers3) {
      return (
        <>
          {renderValue(header2)} | {renderValue(headers3)}
        </>
      );
    } else if (header2) {
      return renderValue(header2);
    } else if (headers3) {
      return renderValue(headers3);
    } else {
      return null;
    }
  }, [findHeaderValueByPosition, findHeaderValuesByPosition]);

  return { findHeaderValueByPosition, findHeaderValuesByPosition, renderSecondLine };
};

export default useJobHeaderHandler;
