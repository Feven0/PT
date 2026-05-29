import { useAppDispatch } from "../redux/hooks/hooks";
import { setSince } from "../redux/slices/jobSinceFilterSlice";

type TableParams = {
  pagination: {
    current: number;
    pageSize: number;
  };
};

const useFilterAndPagination = (
  setTableParams: (params: TableParams) => void,
  sendResult: () => void
) => {
  const dispatch = useAppDispatch();
  const handleFilterChange = ( filterLabel: string) => {
    
    let days: number;

  switch (filterLabel) {
    case 'Today':
      days = 1;
      break;
    case 'Last 7 days':
      days = 7;
      break;
    case 'Last 15 days':
      days = 15;
      break;
    case 'Last 30 days':
      days = 30;
      break;
    case 'Last 90 days':
      days = 90;
      break;
    default:
      days = 7;
  }

  dispatch(setSince({
    days,
    filter: filterLabel,
  }));

  sendResult();

    setTableParams({
      pagination: {
        current: 1,
        pageSize: 10,
      },
    });
  };

  const handleTodayChange = () => {
    handleFilterChange('Today');
    dispatch(setSince({
      days: 1,
      filter: 'Today',
    }));
  }
  const handleLast7Change = () => {
    dispatch(setSince({
      days: 7,
      filter: 'Last 7 days',
    }));
    handleFilterChange('Last 7 days');
  }
  const handleFetchLast15Days = () => {
    dispatch(setSince({
      days: 15,
      filter: 'Last 15 days',
    }));
    handleFilterChange('Last 15 days');
  }
  const handleFetchLastMonth = () =>  {
    dispatch(setSince({
      days: 30,
      filter: 'Last 30 days',
    }));
    handleFilterChange('Last 30 days');
  }
  const handleFetchLast3Months = () => {
    dispatch(setSince({
      days: 90,
      filter: 'Last 90 days',
    }));
    handleFilterChange('Last 90 days');
  }

  return {
    handleTodayChange,
    handleLast7Change,
    handleFetchLast15Days,
    handleFetchLastMonth,
    handleFetchLast3Months,
  };
};

export default useFilterAndPagination;
