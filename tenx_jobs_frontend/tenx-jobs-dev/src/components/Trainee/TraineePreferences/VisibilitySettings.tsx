import { Switch } from 'antd';
import { InfoCircleOutlined } from '@ant-design/icons';
import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { updateVisibility } from "../../../redux/slices/Preferences/systemSlice";
import { switchConfig } from "../../../utils/commonUtils";
import { setPreferenceControlTag } from "../../../redux/slices/Preferences/preferenceControlSlice";

export default function VisibilitySettings() {
  const dispatch = useAppDispatch();
  const {visibility} = useAppSelector((state) => state.visibility);

  const handleSwitchChange = (name: string, checked: boolean) => {
    dispatch(updateVisibility({ name, value: checked }));
    dispatch(setPreferenceControlTag(true));
  };


  return (
    <div>
      <div style={{padding:"0 1rem", marginTop:"1rem"}}>
         <span className="preference__header__title">View Preferences</span>
        </div>
        <div className="flex-center gap-8 description-text">
          <InfoCircleOutlined />
          <span>
            This only affect the mobile app view!
          </span>
        </div>
        {Object?.entries(switchConfig).map(([name, label]) => {
          const item = visibility?.find((item) => item.name === name);
          return (
            <div key={name} className="d-flex-between p-16">
              <span>{label}</span>
              <Switch
                defaultChecked={item ? item.default : false}
                onChange={(checked) => handleSwitchChange(name, checked)}
              />
            </div>
          );
        })}
    </div>
  );
}
