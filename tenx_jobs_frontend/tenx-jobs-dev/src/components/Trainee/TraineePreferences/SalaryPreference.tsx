import { Divider, Slider, Switch } from 'antd';
import { useDispatch } from 'react-redux';
import { useAppSelector } from "../../../redux/hooks/hooks";
import { setMaximumSalary, setMinimumSalary, setNoMaxLimit } from "../../../redux/slices/Preferences/salarySlices";
import { setPreferenceControlTag } from "../../../redux/slices/Preferences/preferenceControlSlice";

export default function SalaryPreference() {
  const dispatch = useDispatch();
  const { salary_range, noMaxLimit} = useAppSelector((state) => state.salaryPreference);
  const { minimum_salary: minSalary, maximum_salary: maxSalary } = salary_range;

  const handleSliderChange = (value: number | number[]) => {
    if (noMaxLimit) {
      dispatch(setMinimumSalary(value as number));
      dispatch(setMaximumSalary(undefined)); 
      dispatch(setPreferenceControlTag(true));
    } else {
      const [min, max] = value as number[];
      dispatch(setMinimumSalary(min));
      dispatch(setMaximumSalary(max));
      dispatch(setPreferenceControlTag(true));
    }
  };

  const handleSwitchChange = (checked: boolean) => {
    dispatch(setNoMaxLimit(checked));
    if (checked) {
      dispatch(setMinimumSalary(minSalary));
      dispatch(setMaximumSalary(undefined));
      dispatch(setPreferenceControlTag(true));
    } else {
      dispatch(setMaximumSalary(maxSalary ?? 100000));
      dispatch(setPreferenceControlTag(true));
    }
  };

  return (
    <>
      <Divider/>
      <div className="d-flex-between roles-header mb-16">
        <span className="preference__header__title">Salary Range (Yearly)</span>
        <div className="flex-center gap-8">
          ${minSalary?.toLocaleString()} 
          {!noMaxLimit && maxSalary !== undefined ? ` - $${maxSalary.toLocaleString()}` : ''}
        </div>
      </div>
      <div className="company-size-tags-div">
        {noMaxLimit ? (
          <Slider
            value={minSalary}
            onChange={(value) => handleSliderChange(value as number)}
            min={0}
            max={100000}
            included={false}
            step={1000}
            marks={{ [minSalary]: minSalary.toLocaleString() }}
          />
        ) : (
          <Slider
            range
            value={[minSalary, maxSalary || minSalary]}
            onChange={(value) => handleSliderChange(value as number[])}
            min={0}
            max={100000}
            step={1000}
          />
        )}
        <div className="flex-end">
          <div className="flex-center gap-8">
            <span>I don't want max limit</span>
            <Switch
              checked={noMaxLimit}
              onChange={handleSwitchChange}
            />
          </div>
        </div>
      </div>
    </>
  );
}
