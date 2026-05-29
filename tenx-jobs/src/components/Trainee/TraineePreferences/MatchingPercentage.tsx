import {Divider, Slider } from 'antd';
import { useDispatch } from 'react-redux';
import {InfoCircleOutlined } from '@ant-design/icons';
import { useAppSelector } from "../../../redux/hooks/hooks";
import { setSliderValue } from "../../../redux/slices/Preferences/matchingPercentageSlice";
import { setPreferenceControlTag } from "../../../redux/slices/Preferences/preferenceControlSlice";

export default function MatchingPercentage() {
  const dispatch = useDispatch();
  const {match} = useAppSelector((state) => state.matchingPercentage);

  const onChange = (newValue: number) => {
    const adjustedValue = newValue < 50 ? 50 : newValue;
    dispatch(setSliderValue({
      ...match,
      ujc_score_threshold: adjustedValue
    }));
    dispatch(setPreferenceControlTag(true));
  };

  const onPreferenceChange = (newValue: number) => {
    const adjustedValue = newValue < 50 ? 50 : newValue;
    dispatch(setSliderValue({
      ...match,
      preference_score_threshold: adjustedValue
    }));
    dispatch(setPreferenceControlTag(true));
  };

  return (
    <>
      <div className="d-flex-between roles-header">
         <span className="preference__header__title">Matching Percentage</span>
        <div className="flex-center gap-8">
          {match?.ujc_score_threshold}%
        </div>
      </div>
      <div className="description-text">
        <InfoCircleOutlined />
        <span style={{ marginLeft: "8px" }}>
          This will affect the job you are going to see.
        </span>
      </div>
      <div className="company-size-tags-div">
        <Slider
          step={5}
          min={0}
          max={100}
          value={match?.ujc_score_threshold}
          onChange={onChange}
        />
      </div>
    <Divider/>
    <div className="mt-16">
        <div className="d-flex-between roles-header">
         <span className="preference__header__title">Preference Score Threshold</span>
        <div className="flex-center gap-8">
          {match.preference_score_threshold}%
        </div>
      </div>
      <div className="description-text">
        <InfoCircleOutlined />
        <span style={{ marginLeft: "8px" }}>
          Determines how much your preferences influence the jobs you’re likely to get.
        </span>
      </div>
    </div>
    <div className="company-size-tags-div mt-16">
        <Slider
          step={5}
          min={0}
          max={100}
          value={match?.preference_score_threshold}
          onChange={onPreferenceChange}
        />
      </div>
    </>
  );
}
